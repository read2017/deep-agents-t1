---
name: research-fact-pack
description: 当任务需要提取 Deep Agents、subagents、skills、LangGraph runtime 等官方事实、概念定义、对比点时使用。输出应简洁、事实优先、避免教学铺陈。
---

# Research Fact Pack

## 适用场景

适用于这些类型的子任务：

- 提取关键事实
- 比较两个概念
- 输出定义和边界
- 为主 agent 提供简短研究结果

## 输出原则

- 先给事实，再给一句解释
- 尽量压缩输出长度
- 默认使用 3 条 bullet
- 不做长篇教学，不写学习计划

## 执行规则

- 优先使用本地工具获取事实
- 如果任务是比较两个概念，先分别定义，再给边界
- 如果主问题是教学型任务，只返回研究摘要给上游 agent
