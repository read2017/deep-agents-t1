import os

from deepagents.backends import FilesystemBackend
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

    # 这一版 demo 显式使用 FilesystemBackend，
    # 让 /notes/today.md 真正落到当前项目目录中，而不是只存在内存态 state 里。
    #
    # root_dir 指向当前工作目录：
    # /Users/liangzhe/workspace/codex/deep-agents-t1
    #
    # virtual_mode=True 的含义是：
    # agent 看到的是“虚拟绝对路径”，例如 /notes/today.md，
    # 但它最终会被映射到 root_dir 下的真实文件：
    # /Users/liangzhe/workspace/codex/deep-agents-t1/notes/today.md
    #
    # 这样做有两个好处：
    # 1. 用户提示词里仍然可以写简洁的 /notes/... 路径
    # 2. 我们又能在本地磁盘里真实看到生成的文件
    backend = FilesystemBackend(
        root_dir=os.getcwd(),
        virtual_mode=True,
    )

    # permissions 只负责“准不准访问某路径”，
    # 它不决定文件最终存在哪里。
    # 真正决定存储位置的是 backend。
    #
    # 下面这组规则表示：
    # - 允许读写 /notes/**
    # - 明确拒绝写 /private/**
    #
    # 所以：
    # /notes/today.md 可以写
    # /private/secret.txt 会被拦住
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
        backend=backend,
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

    # 额外打印真实落盘路径，方便你把“逻辑路径”和“真实文件路径”对上。
    print("\n=== 真实文件路径 ===")
    print(
        os.path.join(
            os.getcwd(),
            "notes",
            "today.md",
        )
    )


if __name__ == "__main__":
    main()
