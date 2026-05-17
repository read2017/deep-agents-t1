# Deep Agents 速学笔记

## 1. 它到底是什么

`Deep Agents` 不是一个模型，而是 LangChain 官方提供的复杂任务 agent 脚手架。

你可以把它理解成：

- `LangChain` 负责工具、模型、消息这些基础积木
- `LangGraph` 负责 agent runtime、流式执行、持久化这些执行层能力
- `Deep Agents` 负责把复杂任务常见需要的能力打包好

官方文档里反复出现的核心能力有：

- planning
- filesystem tools
- subagents
- memory
- permissions
- human-in-the-loop
- sandbox execution

## 2. 它解决什么问题

普通 agent 很容易遇到两个问题：

1. 任务一复杂，上下文会被中间结果撑爆
2. 一个 agent 既想管全局，又想做细节，提示词会越来越乱

Deep Agents 的思路是：

- 用 `write_todos` 先拆任务
- 用文件工具把大块中间结果放到文件系统，而不是一直塞在对话上下文里
- 用 `subagents` 把脏活、重活隔离出去，主 agent 只拿最终结果

## 3. 你应该怎么理解 subagent

很多人第一次看到会以为“这是 multi-agent 框架”。这不算错，但更关键的理解是：

`subagent` 的第一价值是上下文隔离，不是 agent 数量变多。

什么时候适合用：

- 多步骤任务
- 工具返回很长的结果
- 需要不同角色或不同工具集
- 主 agent 只想做协调，不想吃掉全部细节

什么时候不适合：

- 简单单步任务
- 必须保留完整中间思路的任务
- agent 数量增加的复杂度大于收益

## 4. 最小心智模型

先只记住这 4 个元素：

```python
agent = create_deep_agent(
    model="openai:gpt-4.1-mini",
    tools=[...],
    system_prompt="...",
    subagents=[...],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "..."}]
})
```

你学习初期不需要先啃完所有能力。先掌握：

- 主 agent 怎么创建
- tool 怎么挂
- subagent 怎么配

## 5. 学习顺序建议

### 第一步

跑通最小 demo，只看 `create_deep_agent`、`tools`、`invoke`

### 第二步

看 subagent 版 demo，重点看：

- `name`
- `description`
- `system_prompt`
- `tools`

这里最重要的是 `description`，因为主 agent 会靠它判断“什么时候该委托给谁”。

### 第三步

再去看官方文档里的这些点：

- customization
- skills
- memory
- permissions
- human-in-the-loop

## 6. 常见误区

### 误区 1

“有 agent 就该上 Deep Agents”

不对。简单任务直接普通 agent 更轻。

### 误区 2

“subagent 越多越强”

不对。subagent 太多会增加协调成本。

### 误区 3

“它默认就能执行 shell”

不对。`execute` 要配 sandbox backend 才能用。

## 7. 你下一步最值得做的练习

做一个“AI 学习助教” demo：

- 主 agent：负责规划学习路线
- researcher subagent：负责查资料
- coach subagent：负责出练习和验收题

你会在这个练习里自然碰到 Deep Agents 最重要的三个点：

- planning
- delegation
- context management
