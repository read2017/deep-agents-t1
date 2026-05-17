import os

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore


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


def build_agent_and_store():
    """构建一个带长期记忆的 Deep Agent。"""
    model = build_model()

    # 这里用 InMemoryStore 做演示：
    # 它能在同一次脚本运行里跨多个 thread 共享记忆，
    # 足够让你理解“跨 thread 记忆”的机制。
    store = InMemoryStore()

    # 先手动种一份初始记忆文件。
    # 你可以把它理解成 agent 的“长期偏好/长期说明”。
    store.put(
        ("my-agent",),
        "/memories/preferences.md",
        create_file_data(
            """## Preferences
- Start with a short answer
- Use Chinese
"""
        ),
    )

    # memory 参数告诉 Deep Agent：
    # 这份文件属于长期记忆，后续可以被读取，也可以被 agent 更新。
    agent = create_deep_agent(
        model=model,
        memory=["/memories/preferences.md"],
        backend=lambda rt: CompositeBackend(
            default=StateBackend(rt),
            routes={
                # 固定用 ("my-agent",) 作为命名空间，
                # 表示这个 agent 在不同 thread 间共享同一份记忆。
                "/memories/": StoreBackend(
                    rt,
                    namespace=lambda rt: ("my-agent",),
                ),
            },
        ),
        store=store,
        system_prompt=(
            "You are a concise AI engineering mentor. "
            "Teach the user in Chinese and respect remembered preferences."
        ),
    )
    return agent, store


def print_memory_snapshot(store: InMemoryStore) -> None:
    """打印当前记忆文件内容，帮助观察 agent 是否真的改写了 memory。"""
    memory_file = store.get(("my-agent",), "/memories/preferences.md")
    print("=== 当前 memory 文件 ===")
    if memory_file is None:
        print("(memory file missing)")
        return
    print(memory_file.value["text"])


def main():
    agent, store = build_agent_and_store()

    print("=== 初始 memory ===")
    print_memory_snapshot(store)

    # Thread 1:
    # 用户告诉 agent 一个新的长期偏好。
    # 重点：这里不是同一个 thread 里立刻测试，而是让 agent 先“学到”这件事。
    thread_1_config = {"configurable": {"thread_id": "memory-demo-thread-1"}}
    agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我以后希望你多举 Python 例子，请记住这个偏好。",
                }
            ]
        },
        config=thread_1_config,
    )

    print("\n=== Thread 1 之后的 memory ===")
    print_memory_snapshot(store)

    # Thread 2:
    # 这里故意换一个新的 thread_id。
    # 如果 agent 还能体现出刚才学到的偏好，说明长期记忆确实跨 thread 生效了。
    thread_2_config = {"configurable": {"thread_id": "memory-demo-thread-2"}}
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请解释一下 Deep Agents 里的 subagent 是什么。",
                }
            ]
        },
        config=thread_2_config,
    )

    print("\n=== Thread 2 的回答 ===")
    print(result["messages"][-1].content)

    print("\n=== 最终 memory ===")
    print_memory_snapshot(store)


if __name__ == "__main__":
    main()
