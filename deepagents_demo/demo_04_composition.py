import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从 .env 加载模型配置。
load_dotenv()


def search_study_notes(topic: str) -> str:
    """主 agent 工具：返回适合教学组织的简短知识点。"""
    knowledge_base = {
        "deep agents": (
            "Deep Agents is an agent harness for complex tasks. It adds planning, "
            "tool use, delegation, and context management on top of LangChain and LangGraph."
        ),
        "tool": (
            "A tool is a callable capability. Use tools for concrete actions or data access, "
            "such as search, file reads, edits, or calculations."
        ),
        "subagent": (
            "A subagent is a delegated executor. Use it when a subtask needs its own context, "
            "instructions, or toolset."
        ),
        "skill": (
            "A skill is a reusable instruction package. Use it when a class of tasks needs "
            "a repeatable workflow, output format, or domain-specific guidance."
        ),
    }

    topic_lower = topic.lower()
    matches = [
        text
        for key, text in knowledge_base.items()
        if topic_lower in key or key in topic_lower
    ]
    if matches:
        return "\n\n".join(matches)

    return "\n".join(f"{key}: {value}" for key, value in knowledge_base.items())


def lookup_official_facts(topic: str) -> str:
    """researcher 工具：返回更偏“官方表述风格”的事实摘要。"""
    facts = {
        "deep agents": (
            "- Deep Agents is a standalone library.\n"
            "- It is built on LangGraph runtime and LangChain integrations.\n"
            "- It is designed for complex, multi-step tasks with planning and delegation."
        ),
        "subagents": (
            "- Subagents are used for context isolation.\n"
            "- Custom subagents can have their own tools and model overrides.\n"
            "- Custom subagents do not inherit main-agent skills by default."
        ),
        "skills": (
            "- Skills are directory-based capabilities centered on SKILL.md.\n"
            "- The agent first matches by description, then reads the full skill file.\n"
            "- General-purpose subagents inherit main-agent skills, custom subagents do not."
        ),
        "tool skill subagent": (
            "- Tools provide concrete capabilities.\n"
            "- Skills provide reusable task-handling guidance.\n"
            "- Subagents provide delegated execution with context isolation."
        ),
    }

    topic_lower = topic.lower()
    for key, value in facts.items():
        if topic_lower in key or key in topic_lower:
            return value
    return facts["tool skill subagent"]


def compare_agent_components(left: str, right: str) -> str:
    """researcher 工具：比较两个组件的职责边界。"""
    pair = {left.lower(), right.lower()}
    if pair == {"tool", "skill"}:
        return (
            "tool: concrete callable capability for acting or fetching data\n"
            "skill: reusable instruction package for handling a class of tasks"
        )
    if pair == {"skill", "subagent"}:
        return (
            "skill: tells the agent how to approach a task\n"
            "subagent: is the delegated executor that performs a subtask"
        )
    if pair == {"tool", "subagent"}:
        return (
            "tool: a single capability call\n"
            "subagent: a separate worker with its own context, instructions, and tools"
        )
    return "Compare the purpose, execution role, and context boundary of the two components."


def build_agent():
    # 使用 OpenAI-compatible 配置，兼容官方接口或代理接口。
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL")
    if not api_key or not base_url or not model_name:
        raise SystemExit(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or OPENAI_MODEL. "
            "Copy .env.example to .env and set them first."
        )

    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        max_retries=3,
        timeout=60,
    )

    # 主 agent 的 skills：负责“教学怎么讲”。
    main_skills_dir = Path(__file__).resolve().parent.parent / "deepagents_skills"
    # researcher 的 skills：负责“事实怎么提炼”。
    research_skills_dir = (
        Path(__file__).resolve().parent.parent / "deepagents_subagent_skills"
    )

    # 自定义 subagent 不会继承主 agent 的 skills。
    # 所以如果你希望 researcher 也有自己的方法论，要显式给它传 skills。
    research_subagent = {
        "name": "researcher",
        "description": (
            "Researches Deep Agents facts, boundaries, and concept comparisons. "
            "Use it for factual retrieval and concise comparisons."
        ),
        "system_prompt": (
            "You are a focused research subagent. Return concise factual summaries "
            "for the parent agent. Do not produce long teaching content."
        ),
        "tools": [lookup_official_facts, compare_agent_components],
        "skills": [str(research_skills_dir)],
    }

    system_prompt = """
You are a concise AI engineering mentor.
Teach the user in Chinese.
Use the researcher subagent when the task needs factual retrieval or concept comparison.
Use your own tools when light teaching support is enough.
If a matching main-agent skill exists, follow it.
""".strip()

    return create_deep_agent(
        model=model,
        tools=[search_study_notes],
        skills=[str(main_skills_dir)],
        subagents=[research_subagent],
        system_prompt=system_prompt,
    )


def main():
    agent = build_agent()
    # 这段提示词同时触发三类东西：
    # 1. “教学型组织” -> 主 agent 的 skill
    # 2. “事实和边界比较” -> researcher subagent
    # 3. “轻量概念补充” -> 主 agent 的本地 tool
    user_prompt = """
请用中文帮我搞清楚 Deep Agents 里 tool、skill、subagent 这三者怎么分工。
要求：
1. 先给我 3 条关键事实
2. 再解释它们各自应该放什么职责
3. 最后给我一个设计建议：做学习助手时，什么应该做成 tool，什么应该做成 skill，什么应该做成 subagent
""".strip()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
