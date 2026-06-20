import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
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
def send_study_report(to: str, subject: str, summary: str) -> str:
    """Send a study report to a recipient."""
    # 这里故意把工具做得非常“傻”：
    # 它不会自己判断收件人是否安全，也不会自己修改主题或内容。
    # 这样更容易看清楚：真正负责“改写策略”的不是 tool，而是 middleware。
    return (
        "学习报告已发送：\n"
        f"收件人：{to}\n"
        f"主题：{subject}\n"
        f"摘要：{summary}"
    )


@wrap_tool_call
def rewrite_study_report(request, handler):
    """在工具执行前改写 send_study_report 的参数。"""
    # request.tool_call 就是“模型刚刚规划出来的这次工具调用”。
    # 里面通常有三个关键字段：
    # - name: 这次要调用哪个工具
    # - args: 调工具时要传什么参数
    # - id: 这次工具调用的唯一标识
    #
    # middleware 的一个重要能力就是：
    # 在真实工具执行前，先读到这份“调用计划”，然后决定要不要修改它。
    if request.tool_call["name"] != "send_study_report":
        # 如果不是我们关心的工具，就不要乱动，直接放行。
        return handler(request)

    original_args = request.tool_call["args"]

    # 这里开始演示“改写”而不是“拦截”：
    # 1. 原本模型想发给 all-students@example.com
    # 2. middleware 判断这个目标过大，不适合直接发送
    # 3. 于是把收件人改写成 mentor@example.com
    #
    # 注意：
    # 这不是拒绝执行。
    # 这也不是让模型自己重试。
    # 而是 middleware 直接把参数改好，然后继续往下执行真实工具。
    rewritten_to = original_args["to"]
    if rewritten_to == "all-students@example.com":
        rewritten_to = "mentor@example.com"

    # middleware 也可以顺手做一些“标准化”工作。
    # 比如统一主题格式、给摘要加标记，帮助后面的系统识别这条消息
    # 已经过中间层处理。
    rewritten_subject = f"[Middleware Reviewed] {original_args['subject']}"
    rewritten_summary = (
        f"{original_args['summary']}\n\n"
        "备注：本邮件的收件人与格式已由 middleware 自动校正。"
    )

    # 关键点：
    # 不要原地修改 request.tool_call。
    # 推荐做法是构造一个“新的 tool_call”，再用 request.override(...) 生成新请求。
    #
    # 这样做的意义是：
    # - 保持中间件逻辑更清晰
    # - 避免直接改原对象带来的副作用
    # - 更符合当前 API 的推荐用法
    rewritten_tool_call = {
        **request.tool_call,
        "args": {
            **original_args,
            "to": rewritten_to,
            "subject": rewritten_subject,
            "summary": rewritten_summary,
        },
    }

    rewritten_request = request.override(tool_call=rewritten_tool_call)

    # handler(...) 的含义是：
    # “把这次处理后的请求，继续交给后面的执行链路”。
    #
    # 如果这里传入原 request，就是“看过但不改”。
    # 如果这里传入 rewritten_request，就是“改完之后再放行”。
    #
    # 所以 middleware 的“改写”本质就是：
    # 先改请求，再把改过的请求继续传下去。
    return handler(rewritten_request)


def build_agent():
    """构建一个专门演示 middleware 改写功能的 Deep Agent。"""
    model = build_model()

    return create_deep_agent(
        model=model,
        tools=[send_study_report],
        middleware=[rewrite_study_report],
        system_prompt=(
            "You are a concise AI learning assistant. "
            "Teach the user in Chinese. "
            "When the user asks to send a study report, use the tool directly."
        ),
    )


def main():
    agent = build_agent()

    user_prompt = """
    请把今天的 Deep Agents 学习总结发给 all-students@example.com。
    主题写成：Deep Agents 学习日报
    摘要写成：今天学习了 middleware 的作用，它可以统一控制工具执行过程。

    最后请明确告诉我：
    1. 模型原本想发给谁
    2. 实际工具最终发给了谁
    3. 为什么这说明 middleware 做的是“改写”而不是“拦截”
    """.strip()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
