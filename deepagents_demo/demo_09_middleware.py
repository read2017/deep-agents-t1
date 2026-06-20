import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import ToolCallLimitMiddleware, wrap_tool_call
from langchain.tools import tool
from langchain_core.messages import ToolMessage
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


@tool
def search_reference(topic: str) -> str:
    """Search a tiny built-in knowledge base."""
    knowledge = {
        "deep agents": (
            "Deep Agents 是一个更高层的 agent harness，"
            "核心关注 planning、tools、delegation、memory 和 execution control。"
        ),
        "middleware": (
            "Middleware 是插在 agent 执行链路中的控制层，"
            "可以在模型调用前后、工具调用前后插手，而不是直接承担业务动作。"
        ),
    }
    return knowledge.get(
        topic.strip().lower(),
        f"没有找到 {topic} 的内置资料。",
    )


@tool
def save_note(topic: str, content: str) -> str:
    """Pretend to save a study note."""
    return f"已保存笔记：{topic} -> {content}"


@wrap_tool_call
def block_save_note(request, handler):
    """拦截 save_note，让你看到 middleware 可以统一接管工具调用。"""
    if request.tool_call["name"] == "save_note":
        return ToolMessage(
            content=(
                "save_note 被 middleware 主动拦截了。"
                "这说明 middleware 可以在工具执行前统一介入，"
                "而不需要修改 save_note 这个工具本身。"
            ),
            tool_call_id=request.tool_call["id"],
        )
    return handler(request)


def build_agent():
    """构建一个演示 middleware 的 Deep Agent。"""
    model = build_model()

    # 这里同时演示两种 middleware：
    # 1. block_save_note：定向拦截某个工具
    # 2. ToolCallLimitMiddleware：限制本轮最多允许 2 次工具调用
    return create_deep_agent(
        model=model,
        tools=[search_reference, save_note],
        middleware=[
            block_save_note,
            ToolCallLimitMiddleware(run_limit=2, exit_behavior="continue"),
        ],
        system_prompt=(
            "You are a concise AI learning assistant. "
            "Teach the user in Chinese. "
            "When a tool is blocked by middleware, explain that it was blocked "
            "by middleware rather than by the tool itself."
        ),
    )


def main():
    agent = build_agent()

    user_prompt = """
    请你完成三件事：
    1. 查一下 Deep Agents
    2. 查一下 middleware
    3. 把今天的学习总结保存成笔记

    最后告诉我：
    - 哪些动作真的执行了
    - 哪些动作是被 middleware 拦住的
    - middleware 在这个例子里到底起了什么作用
    """.strip()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
