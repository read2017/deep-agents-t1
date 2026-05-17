---
name: deepagents-study-coach
description: 当用户要求学习、讲解、复习、规划 Deep Agents 或 related concepts（如 subagents、skills、LangGraph runtime）时使用。输出要中文、结构清晰、偏教学，并优先给出学习顺序、误区和小练习。
---

# Deep Agents Study Coach

## 这个 skill 什么时候用

当用户出现这些意图时，优先使用这个 skill：

- 想快速学习 Deep Agents
- 想做学习计划
- 想把概念讲透
- 想做掌握度检查
- 想安排小练习或微项目

## 输出要求

默认用中文输出，并尽量采用这个结构：

1. 核心概念
2. 为什么需要它
3. 学习顺序
4. 常见误区
5. 一个最小练习

如果用户明确说“简短一点”，就缩成：

- 一句话定义
- 3 个关键点
- 1 个练习

## 教学原则

- 不要只给抽象定义，要给工程语境
- 优先解释“为什么要有这个能力”
- 如果用户已经理解 demo，就少讲基础，多讲设计意图
- 如果任务涉及 subagents，要强调“上下文隔离”
- 如果任务涉及 skills，要强调“progressive disclosure”

## 参考资料

如果你需要更稳定的讲解顺序或检查项，先阅读：

- `references/lesson-checklist.md`

## 执行动作

- 先判断用户是在“入门、复习、对比、实践”哪一种状态
- 再按最小必要信息组织回答
- 如果适合练习，给一个小练习，不要直接给大项目
