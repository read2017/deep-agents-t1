import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从 .env 加载 API Key、Base URL、模型名等环境变量。
load_dotenv()


def search_study_notes(topic: str) -> str:
    """本地假数据工具：模拟查询 Deep Agents 相关知识点。"""
    knowledge_base = {
        "deep agents": (
            "Deep Agents is a higher-level agent harness built on top of LangChain "
            "and LangGraph. It is designed for multi-step tasks that benefit from "
            "planning, filesystem tools, and delegation."
        ),
        "langgraph": (
            "LangGraph provides the runtime layer for agent workflows, including "
            "durable execution and streaming."
        ),
        "subagents": (
            "Subagents are mainly useful for context isolation. The main agent can "
            "delegate detailed work and only keep the final result in its own context."
        ),
        "skills": (
            "Skills are file-based capability packages. They let an agent discover "
            "instructions and workflows from a structured directory."
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

    supported_topics = ", ".join(sorted(knowledge_base))
    return f"No direct note for '{topic}'. Try one of: {supported_topics}."


def build_agent():
    # 显式读取 OpenAI-compatible 接口所需的 3 个关键配置。
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL")
    if not api_key or not base_url or not model_name:
        raise SystemExit(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or OPENAI_MODEL. "
            "Copy .env.example to .env and set them first."
        )

    # 不再使用 model="openai:..." 这种隐式路由，而是显式指定
    # base_url + api_key + model，方便接官方 OpenAI 或兼容代理。
    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        max_retries=3,
        timeout=60,
    )

    system_prompt = """
You are a concise AI engineering mentor.
Teach the user in Chinese.
Use the study notes tool when the question is about Deep Agents, LangGraph, subagents, or skills.
Prefer short explanations with concrete engineering intuition.
""".strip()

    # create_deep_agent 是 Deep Agents 的主入口。
    # 这里给它挂上一个工具和一个系统提示词，形成最小可运行示例。
    return create_deep_agent(
        model=model,
        tools=[search_study_notes],
        system_prompt=system_prompt,
    )


def main():
    agent = build_agent()
    # 用户消息仍然通过 messages 结构传入，这点和 LangChain/LangGraph 生态保持一致。
    user_prompt = """
请用中文快速解释：
1. Deep Agents 和普通 agent 的区别
2. subagent 最核心的价值是什么
3. 我学习时应该先抓哪 3 个概念
""".strip()

    # invoke 会触发一次完整的 agent 执行流程。
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    # 通常最后一条消息就是 agent 给用户的最终回答。
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
