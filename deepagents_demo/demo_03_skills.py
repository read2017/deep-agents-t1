import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从 .env 加载模型配置。
load_dotenv()


def search_study_notes(topic: str) -> str:
    """本地教学工具：返回 Deep Agents 相关的简短知识点。"""
    knowledge_base = {
        "deep agents": (
            "Deep Agents is an agent harness built on top of LangChain and LangGraph. "
            "It is useful for complex tasks that need planning, file tools, and delegation."
        ),
        "subagents": (
            "Subagents are mainly for context isolation. They let the main agent delegate "
            "detailed work without carrying all intermediate context."
        ),
        "skills": (
            "Skills are reusable capability folders. The agent first matches by description, "
            "then reads the full SKILL.md only when needed."
        ),
        "progressive disclosure": (
            "Progressive disclosure means the agent only loads detailed skill instructions "
            "when a task matches that skill."
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


def build_agent():
    # 继续沿用 OpenAI-compatible 配置，便于接官方或代理接口。
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

    # skills 参数传的是“技能目录根路径”，不是单个 SKILL.md 文件。
    # Deep Agents 会先读取每个 skill 的 frontmatter，任务匹配时再展开读取内容。
    skills_dir = Path(__file__).resolve().parent.parent / "deepagents_skills"

    system_prompt = """
You are a concise AI engineering mentor.
Teach the user in Chinese.
Use tools when factual support helps.
If a matching skill exists, follow the skill instructions.
""".strip()

    return create_deep_agent(
        model=model,
        tools=[search_study_notes],
        skills=[str(skills_dir)],
        system_prompt=system_prompt,
    )


def main():
    agent = build_agent()
    # 这段提示词故意包含“学习计划、误区、练习”这些信号，
    # 让模型更容易匹配到 deepagents-study-coach 这个 skill。
    user_prompt = """
请用中文给我一份 Deep Agents 的 2 天速学安排。
要求：
1. 先用一句话定义它
2. 告诉我学习顺序
3. 提醒我最容易犯的 2 个误区
4. 给我 1 个最小练习
""".strip()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
