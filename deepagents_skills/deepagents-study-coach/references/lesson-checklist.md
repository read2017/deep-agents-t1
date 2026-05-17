# Deep Agents Lesson Checklist

讲解 Deep Agents 时，优先覆盖以下检查点：

1. 它不是模型，而是 agent harness
2. 它和普通 agent 的差别在于 planning、filesystem、subagents、memory 等内建能力
3. subagent 的第一价值是上下文隔离
4. skill 的第一价值是把专门知识和工作流文件化，并按需加载
5. 什么时候不该用 Deep Agents

如果用户要实践，优先安排这种练习顺序：

1. 单 agent + tool
2. 主 agent + subagents
3. skills
4. memory / permissions / HITL
