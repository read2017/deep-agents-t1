import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从 .env 加载运行所需配置。
load_dotenv()


def search_doc_excerpt(topic: str) -> str:
    """研究型工具：返回某个主题的简短资料摘录。"""
    docs = {
        "overview": (
            "Deep Agents adds planning, filesystem tools, subagents, memory, "
            "permissions, and other orchestration features for complex tasks."
        ),
        "subagents": (
            "Subagents help prevent context bloat. The main agent delegates detailed "
            "work and keeps only concise results."
        ),
        "skills": (
            "Skills are directories that contain instructions and workflows, often "
            "anchored by a SKILL.md file."
        ),
        "permissions": (
            "Sensitive actions can be routed through approval flows so the user can "
            "review them before the agent proceeds."
        ),
    }

    topic_lower = topic.lower()
    excerpts = [
        f"{key}: {value}"
        for key, value in docs.items()
        if topic_lower in key or key in topic_lower
    ]
    if excerpts:
        return "\n".join(excerpts)
    return "\n".join(f"{key}: {value}" for key, value in docs.items())


def generate_quiz(topic: str, count: int = 3) -> str:
    """教学型工具：为指定主题生成几道掌握度检查题。"""
    bank = {
        "deep agents": [
            "为什么说 Deep Agents 首先是 orchestration harness，而不是新模型？",
            "普通 agent 在复杂任务里最常见的两个问题是什么？",
            "为什么 Deep Agents 会引入 filesystem tools？",
        ],
        "subagents": [
            "subagent 的第一价值为什么是上下文隔离？",
            "什么时候不应该使用 subagent？",
            "subagent 的 description 为什么重要？",
        ],
    }

    topic_lower = topic.lower()
    for key, questions in bank.items():
        if topic_lower in key or key in topic_lower:
            return "\n".join(
                f"{index}. {question}"
                for index, question in enumerate(questions[:count], start=1)
            )

    fallback = bank["deep agents"][:count]
    return "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(fallback, start=1)
    )


def estimate_study_time(task: str) -> str:
    """辅助工具：根据任务描述粗略估算学习时长。"""
    task_lower = task.lower()
    if "demo" in task_lower or "run" in task_lower:
        return "20-30 minutes"
    if "subagent" in task_lower:
        return "30-45 minutes"
    if "skill" in task_lower or "permission" in task_lower:
        return "45-60 minutes"
    return "30 minutes"


def build_agent():
    # 统一使用 OpenAI-compatible 配置，便于切换官方接口或代理接口。
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL")
    if not api_key or not base_url or not model_name:
        raise SystemExit(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or OPENAI_MODEL. "
            "Copy .env.example to .env and set them first."
        )

    # 主模型负责总体协调，subagent 负责分工执行。
    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        max_retries=3,
        timeout=60,
    )

    # researcher 只负责查资料，重点在“事实提取”和“简洁返回”。
    research_subagent = {
        "name": "researcher",
        "description": "Researches Deep Agents concepts and returns concise factual findings.",
        "system_prompt": (
            "You are a focused research subagent. Use the available tool to collect "
            "relevant facts, then return exactly 3 concise bullets."
        ),
        "tools": [search_doc_excerpt],
    }

    # coach 只负责练习设计和学习节奏建议。
    coach_subagent = {
        "name": "coach",
        "description": "Designs practice exercises, quizzes, and small study plans for AI engineers.",
        "system_prompt": (
            "You are a teaching subagent. Use the quiz and time tools to produce "
            "practice tasks that are concrete and beginner-friendly. Keep the output short."
        ),
        "tools": [generate_quiz, estimate_study_time],
    }

    system_prompt = """
You are the lead mentor for a Deep Agents lesson.
Teach in Chinese.
Delegate factual retrieval to the researcher subagent.
Delegate exercises and study pacing to the coach subagent.
Synthesize the final answer into:
- a short explanation
- a 3-day study plan
- 3 mastery-check questions
Keep the total output compact.
""".strip()

    # 这里不再给主 agent 直接挂普通 tools，而是把能力拆到两个 subagent。
    # 这样主 agent 可以只做协调，避免把所有细节都塞进自己的上下文里。
    return create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        subagents=[research_subagent, coach_subagent],
    )


def main():
    agent = build_agent()
    # 这个示例的目标是观察：主 agent 如何把“查资料”和“出练习”拆给不同 subagent。
    user_prompt = """
我想在 3 天内快速入门 Deep Agents。
请给我：
1. 一段非常短的概念解释
2. 一个 3 天学习计划
3. 3 道检验我是否真的理解的题目
""".strip()

    # 调用方式和基础示例相同，但内部可能触发 subagent delegation。
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
