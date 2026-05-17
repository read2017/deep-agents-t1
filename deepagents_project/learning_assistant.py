import asyncio
import json
import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from loguru import logger


# 加载 OpenAI-compatible 配置。
load_dotenv()


# 配置 loguru，终端和文件各保留一份日志。
LOGS_DIR = Path(__file__).resolve().parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
EVENT_TRACE_PATH = LOGS_DIR / "latest_event_trace.jsonl"
SUMMARY_PATH = LOGS_DIR / "latest_run_summary.json"

logger.remove()
logger.add(
    lambda message: print(message, end=""),
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    LOGS_DIR / "learning_assistant.log",
    level="DEBUG",
    rotation="1 MB",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


def search_reference(topic: str) -> str:
    """查询学习主题相关的本地参考资料摘要。"""
    logger.info("Tool `search_reference` called with topic={}", topic)
    knowledge_base = {
        "deep agents": (
            "Deep Agents is a higher-level agent harness for complex tasks. "
            "It combines planning, tools, delegation, and context management."
        ),
        "subagents": (
            "Subagents are mainly used for context isolation and delegated execution."
        ),
        "skills": (
            "Skills are reusable instruction packages that are matched and loaded on demand."
        ),
        "langgraph": (
            "LangGraph provides the runtime layer behind complex agent execution flows."
        ),
    }
    topic_lower = topic.lower()
    matches = [
        f"{key}: {value}"
        for key, value in knowledge_base.items()
        if topic_lower in key or key in topic_lower
    ]
    if matches:
        logger.info("Tool `search_reference` returned {} matched snippet(s)", len(matches))
        return "\n".join(matches)
    logger.info("Tool `search_reference` fell back to full knowledge base")
    return "\n".join(f"{key}: {value}" for key, value in knowledge_base.items())


def generate_questions(topic: str, count: int = 3) -> str:
    """生成学习主题的小测题。"""
    logger.info("Tool `generate_questions` called with topic={}, count={}", topic, count)
    bank = {
        "deep agents": [
            "为什么说 Deep Agents 不是模型，而是 agent harness？",
            "subagent 的第一价值为什么是上下文隔离？",
            "skill 和 tool 的职责边界分别是什么？",
        ],
        "subagents": [
            "什么时候应该用 subagent，而不是主 agent 直接做？",
            "subagent 和普通 tool 最大的区别是什么？",
            "为什么 subagent 能帮助控制上下文膨胀？",
        ],
    }
    topic_lower = topic.lower()
    for key, questions in bank.items():
        if topic_lower in key or key in topic_lower:
            logger.info("Tool `generate_questions` matched topic bucket={}", key)
            return "\n".join(
                f"{index}. {question}"
                for index, question in enumerate(questions[:count], start=1)
            )
    fallback = bank["deep agents"][:count]
    logger.info("Tool `generate_questions` used fallback question set")
    return "\n".join(
        f"{index}. {question}" for index, question in enumerate(fallback, start=1)
    )


def save_note(topic: str, summary: str) -> str:
    """把本轮学习要点追加到本地学习记录文件。"""
    logger.info("Tool `save_note` called with topic={}", topic)
    notes_dir = Path(__file__).resolve().parent / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_path = notes_dir / "learning_journal.md"

    entry = (
        f"## {topic}\n\n"
        f"{summary.strip()}\n\n"
    )

    if notes_path.exists():
        existing = notes_path.read_text(encoding="utf-8")
    else:
        existing = "# Learning Journal\n\n"

    notes_path.write_text(existing + entry, encoding="utf-8")
    logger.info("Tool `save_note` wrote note to {}", notes_path)
    return f"Saved learning note to {notes_path}"


def build_model() -> ChatOpenAI:
    """统一创建模型客户端。"""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL")
    if not api_key or not base_url or not model_name:
        raise SystemExit(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or OPENAI_MODEL. "
            "Copy .env.example to .env and set them first."
        )

    logger.info("Building ChatOpenAI client with model={}, base_url={}", model_name, base_url)
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        max_retries=3,
        timeout=120,
        max_tokens=700,
    )


def build_agent():
    """创建最小学习助手。"""
    logger.info("Building learning assistant agent")
    project_root = Path(__file__).resolve().parent
    main_skills_dir = project_root / "skills"
    subagent_skills_dir = project_root / "subagent_skills"

    model = build_model()

    assessor = {
        "name": "assessor",
        "description": (
            "Handles stage checks, mastery checks, and weak-point analysis for learned topics."
        ),
        "system_prompt": (
            "You are an assessment subagent. Return concise mastery judgments, "
            "weak points, and one next-step suggestion."
        ),
        "tools": [generate_questions],
        "skills": [str(subagent_skills_dir)],
    }

    lesson_pack_builder = {
        "name": "lesson_pack_builder",
        "description": (
            "Builds a compact lesson pack for a topic, including explanation points, "
            "a small exercise, and a suggested learning order."
        ),
        "system_prompt": (
            "You are a lesson-pack subagent. Return compact structured learning packs "
            "for the parent agent."
        ),
        "tools": [search_reference, generate_questions],
    }

    system_prompt = """
You are a practical AI learning assistant.
Teach the user in Chinese.
Use your main skills for explanation and mastery-check structure.
Use tools for concrete actions.
Delegate complete subproblems to subagents when it helps.
When you finish, provide:
1. a short explanation
2. a mini practice section
3. a mastery check section
4. a note summary suitable for saving
Keep the output compact.
""".strip()

    return create_deep_agent(
        model=model,
        tools=[search_reference, generate_questions, save_note],
        skills=[str(main_skills_dir)],
        subagents=[assessor, lesson_pack_builder],
        system_prompt=system_prompt,
    )


def _stringify_message_content(content) -> str:
    """把消息内容压缩成适合日志的字符串。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def _truncate(text: str, limit: int = 200) -> str:
    """截断过长日志文本。"""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...(truncated)"


def _record_event(trace_file, event: dict) -> None:
    """把原始事件落成 jsonl，便于事后分析。"""
    trace_file.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


async def _run_agent_with_debug_async(agent, user_prompt: str) -> tuple[str, dict]:
    """通过 astream_events 运行 agent，并输出更完整的调试信息。"""
    logger.info("Invoking agent with async event streaming")

    summary = {
        "tool_calls": [],
        "tool_results": [],
        "subagent_dispatches": [],
        "event_count": 0,
    }
    final_result = None
    model_round = 0
    seen_tool_starts: set[str] = set()
    seen_tool_ends: set[str] = set()
    seen_subagent_dispatches: set[str] = set()

    with EVENT_TRACE_PATH.open("w", encoding="utf-8") as trace_file:
        async for event in agent.astream_events(
            {"messages": [{"role": "user", "content": user_prompt}]},
            version="v2",
        ):
            summary["event_count"] += 1
            _record_event(trace_file, event)

            event_name = event.get("event", "")
            event_data = event.get("data", {}) or {}
            event_metadata = event.get("metadata", {}) or {}
            event_name_hint = event.get("name", "") or event_metadata.get("langgraph_node", "")
            runnable_name = event.get("name", "")

            # 只保留关键的模型轮次日志。
            if event_name == "on_chat_model_start":
                model_round += 1
                logger.info("Model round {} started", model_round)

            if event_name == "on_chat_model_end":
                logger.info("Model round {} finished", model_round)

            # 识别 tool 开始事件。
            if event_name == "on_tool_start":
                payload = {
                    "event": event_name,
                    "name": event_name_hint,
                    "input": event_data.get("input"),
                }
                summary["tool_calls"].append(payload)
                key = f"{payload['name']}::{json.dumps(payload['input'], ensure_ascii=False, default=str)}"
                if key not in seen_tool_starts:
                    seen_tool_starts.add(key)
                    logger.info("Tool started: {} | input={}", payload["name"], payload["input"])

                # 只有 task 工具且明确带 subagent_type 时，才打印为真正的 subagent 调度。
                tool_input = payload["input"]
                if payload["name"] == "task" and isinstance(tool_input, dict):
                    subagent_type = tool_input.get("subagent_type")
                    description = tool_input.get("description", "")
                    dispatch_key = f"{subagent_type}::{description}"
                    if isinstance(subagent_type, str) and dispatch_key not in seen_subagent_dispatches:
                        seen_subagent_dispatches.add(dispatch_key)
                        summary["subagent_dispatches"].append(
                            {
                                "subagent_type": subagent_type,
                                "description": description,
                            }
                        )
                        logger.info(
                            "Subagent dispatched: {} | task={}",
                            subagent_type,
                            _truncate(str(description), 120),
                        )

            # 识别 tool 结束事件。
            if event_name == "on_tool_end":
                output = event_data.get("output")
                payload = {
                    "event": event_name,
                    "name": event_name_hint,
                    "output": _truncate(str(output)),
                }
                summary["tool_results"].append(payload)
                key = f"{payload['name']}::{payload['output']}"
                if key not in seen_tool_ends:
                    seen_tool_ends.add(key)
                    logger.info("Tool finished: {} | output={}", payload["name"], payload["output"])

            # 某些事件会直接带最终输出。
            if "output" in event_data:
                final_result = event_data["output"]

    logger.info("Async event streaming completed with {} events", summary["event_count"])

    final_message = ""
    if isinstance(final_result, dict) and "messages" in final_result:
        messages = final_result["messages"]
        if messages:
            final_message = _stringify_message_content(getattr(messages[-1], "content", ""))

    # 如果事件流里没有直接拿到最终 output，就退回普通 invoke。
    if not final_message:
        logger.info("No final message extracted from event stream, falling back to invoke()")
        invoke_result = agent.invoke(
            {"messages": [{"role": "user", "content": user_prompt}]}
        )
        final_message = _stringify_message_content(invoke_result["messages"][-1].content)

    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    logger.info("Wrote run summary to {}", SUMMARY_PATH)
    logger.info("Wrote raw event trace to {}", EVENT_TRACE_PATH)
    return final_message, summary


def run_agent_with_debug(agent, user_prompt: str) -> tuple[str, dict]:
    """同步包装器：在脚本里直接运行异步事件流调试。"""
    return asyncio.run(_run_agent_with_debug_async(agent, user_prompt))


def main():
    logger.info("Starting learning assistant demo")
    agent = build_agent()

    # 用固定的最小请求演示学习助手的完整闭环。
    user_prompt = """
请帮我学习 Deep Agents。
要求：
1. 用中文做一个简短讲解
2. 给我一个最小练习
3. 给我 2 道掌握度检查题
4. 最后生成一段可以保存到学习笔记里的总结
""".strip()

    final_message, summary = run_agent_with_debug(agent, user_prompt)
    logger.info(
        "Run summary: tool_calls={} tool_results={} subagent_dispatches={} total_events={}",
        len(summary["tool_calls"]),
        len(summary["tool_results"]),
        len(summary["subagent_dispatches"]),
        summary["event_count"],
    )
    logger.info("Printing final agent response")
    print(final_message)

    # 尝试从最终输出里抽出一个较短摘要，保存到本地学习日志。
    # 这里故意保持简单，重点是展示 tool 在学习闭环里的位置。
    note_summary = final_message[:500]
    save_result = save_note("Deep Agents", note_summary)
    logger.info("Printing save-note result")
    print("\n---\n")
    print(save_result)


if __name__ == "__main__":
    main()
