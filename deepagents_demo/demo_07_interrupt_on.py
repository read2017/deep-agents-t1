import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


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
def send_study_report(to: str, summary: str) -> str:
    """Send a study report to a recipient."""
    return f"Study report sent to {to}: {summary}"


def build_agent():
    """构建一个带 interrupt_on 的 Deep Agent。"""
    model = build_model()

    # checkpointer 是 interrupt_on 的前提。
    # 因为 agent 暂停后，需要靠它把状态记住，后续才能恢复执行。
    checkpointer = MemorySaver()

    agent = create_deep_agent(
        model=model,
        tools=[send_study_report],
        interrupt_on={
            # 对这个工具启用人工审批。
            # 允许三种决策：
            # - approve：原参数直接执行
            # - edit：改参数后执行
            # - reject：跳过执行
            "send_study_report": {
                "allowed_decisions": ["approve", "edit", "reject"]
            }
        },
        checkpointer=checkpointer,
        system_prompt=(
            "You are a concise AI learning assistant. "
            "Teach the user in Chinese. "
            "When a tool requires approval, pause and wait for review."
        ),
    )
    return agent


def main():
    agent = build_agent()

    # 注意：恢复执行时必须复用同一个 thread_id。
    thread_id = "interrupt-on-demo-thread"
    config = {"configurable": {"thread_id": thread_id}}

    user_prompt = """
    请把今天的学习总结发送给 all-students@example.com。
    内容是：Deep Agents 的核心包括 planning、tools、subagents 和 memory。
    """.strip()

    # 第一次调用：
    # agent 计划调用 send_study_report，但因为命中了 interrupt_on，
    # 所以这里会暂停，而不是立刻执行。
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]},
        config=config,
        version="v2",
    )

    print("=== 第一次调用结果 ===")
    interrupts = getattr(result, "interrupts", None)
    if not interrupts:
        print("没有触发 interrupt，这不符合本 demo 预期。")
        print(result["messages"][-1].content)
        return

    interrupt_value = interrupts[0].value
    action_requests = interrupt_value["action_requests"]
    review_configs = interrupt_value["review_configs"]
    config_map = {cfg["action_name"]: cfg for cfg in review_configs}

    for action in action_requests:
        review_config = config_map[action["name"]]
        print(f"待审批工具: {action['name']}")
        print(f"原始参数: {action['args']}")
        print(f"允许的决策: {review_config['allowed_decisions']}")

    # 这里模拟“人工编辑参数后批准”：
    # 把收件人从 all-students@example.com 改成 mentor@example.com。
    first_action = action_requests[0]
    decisions = [
        {
            "type": "edit",
            "edited_action": {
                "name": first_action["name"],
                "args": {
                    "to": "mentor@example.com",
                    "summary": first_action["args"]["summary"],
                },
            },
        }
    ]

    # 第二次调用：
    # 用 Command(resume=...) 恢复执行，并带上人工决策。
    resumed = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )

    print("\n=== 恢复执行后的最终结果 ===")
    print(resumed.value["messages"][-1].content)


if __name__ == "__main__":
    main()
