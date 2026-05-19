import os

from deepagents import FilesystemPermission, create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从 .env 读取模型配置。
load_dotenv()


def build_model() -> ChatOpenAI:
    """创建模型客户端。"""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL")
    if not api_key or not base_url or not model_name:
        raise SystemExit(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or OPENAI_MODEL. "
            "Copy .env.example to .env and set them first."
        )

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
    """构建一个带文件权限限制的 Deep Agent。"""
    model = build_model()

    # 这里只开放 /notes/** 的读写权限，
    # 同时显式拒绝 agent 写 /private/**。
    permissions = [
        FilesystemPermission(
            operations=["read", "write"],
            paths=["/notes/**"],
            mode="allow",
        ),
        FilesystemPermission(
            operations=["write"],
            paths=["/private/**"],
            mode="deny",
        ),
    ]

    return create_deep_agent(
        model=model,
        permissions=permissions,
        system_prompt=(
            "You are a concise AI engineering mentor. "
            "Teach the user in Chinese. "
            "When filesystem access is restricted, explain the restriction clearly."
        ),
    )


def main():
    agent = build_agent()

    # 这个请求故意包含一个允许动作和一个拒绝动作，
    # 方便观察 permissions 的实际效果。
    user_prompt = """
    请完成两件事：
    1. 在 /notes/today.md 写入一行：Deep Agents permissions demo
    2. 在 /private/secret.txt 写入一行：should be denied
    最后告诉我哪一步成功，哪一步被权限拦住。
    """.strip()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
