# DeepAgents Learning Assistant

这是一个最小可运行的 Deep Agents 微项目，用来把你已经学会的三层设计真正落地：

- `tools`：查资料、出题、记笔记
- `skills`：教学流程、掌握度检查
- `subagents`：测评助手、教学包生成助手

## 运行

```bash
cd /Users/liangzhe/workspace/codex/deep-agents-t1
UV_CACHE_DIR=.uv-cache uv run python deepagents_project/learning_assistant.py
```

## 你要重点看什么

1. 主 agent 负责统筹和最终输出
2. `search_reference` / `generate_questions` / `save_note` 是基础能力
3. `teaching-flow` / `mastery-check` 约束输出组织方式
4. `assessor` / `lesson_pack_builder` 是完整子任务执行角色
5. 本轮结束后，脚本会把摘要写入 `deepagents_project/notes/learning_journal.md`

## 这个版本为什么故意保持简单

这个版本的重点不是做一个“强功能产品”，而是让你看清：

- 哪些职责应该在主 agent
- 哪些应该做成 tool
- 哪些应该沉淀为 skill
- 哪些值得拆成 subagent
