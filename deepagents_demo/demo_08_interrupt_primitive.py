import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt


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
def draft_learning_email(topic: str, level: str) -> str:
    """Draft a learning email, but ask for human confirmation on the subject line midway."""
    # 前半段先自动完成：生成邮件主题和正文草稿。
    suggested_subject = f"[{level}] {topic} 学习提醒"
    draft_body = (
        f"今天的主题是 {topic}。\n"
        f"请按 {level} 难度准备学习材料，并在今晚前完成复习。"
    )

    # 在工具执行到中间时暂停，向人确认或修改主题。
    reviewed_subject = interrupt(
        {
            "kind": "subject_review",
            "suggested_subject": suggested_subject,
            "draft_body": draft_body,
            "instruction": "请确认邮件主题，或者直接提供修改后的主题。",
        }
    )

    # 恢复后继续后半段：把确认后的主题拼回最终邮件草稿。
    return (
        "邮件草稿已生成：\n"
        f"主题：{reviewed_subject}\n"
        f"正文：\n{draft_body}"
    )


def build_agent():
    """构建一个使用 interrupt() 原语的 Deep Agent。"""
    model = build_model()
    checkpointer = MemorySaver()

    return create_deep_agent(
        model=model,
        tools=[draft_learning_email],
        checkpointer=checkpointer,
        system_prompt=(
            "You are a concise AI learning assistant. "
            "Teach the user in Chinese. "
            "Use the email-drafting tool when the user asks for a learning reminder email."
        ),
    )


def main():
    agent = build_agent()
    thread_id = "interrupt-primitive-demo-thread"
    config = {"configurable": {"thread_id": thread_id}}

    user_prompt = """
    请帮我起草一封学习提醒邮件。
    主题是 Deep Agents，难度等级是 Intermediate。
    """.strip()

    # 第一次调用：工具执行到中间时主动 interrupt。
    first = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]},
        config=config,
        version="v2",
    )

    print("=== 工具中途暂停 ===")
    interrupts = getattr(first, "interrupts", None)
    if not interrupts:
        print("没有触发 interrupt，这不符合本 demo 预期。")
        print(first["messages"][-1].content)
        return

    payload = interrupts[0].value
    print("暂停时给人的信息：")
    print(payload)

    # 这里模拟人工直接给出修改后的主题。
    resumed = agent.invoke(
        Command(resume="【请今晚完成】Deep Agents 学习提醒"),
        config=config,
        version="v2",
    )

    print("\n=== 恢复执行后的最终结果 ===")
    print(resumed.value["messages"][-1].content)


if __name__ == "__main__":
    main()
