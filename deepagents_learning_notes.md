# Deep Agents 学习笔记

## 当前阶段

- 学习主题：LangChain Deep Agents 入门
- 当前进度：已完成 `demo_01`、`demo_02`、`demo_03`、`demo_04`、`demo_05`、`demo_06`、`demo_07`、`demo_08`
- 已开始接触：
  - 微项目设计
  - 运行日志阅读
  - long-term memory
  - permissions
  - human-in-the-loop
- 当前阶段判断：
  - 已经理解主线概念
  - 已经能区分 `tool / skill / subagent`
  - 已开始具备阅读 agent 运行轨迹的能力

## 已学内容总览

### 1. Deep Agents 是什么

- `Deep Agents` 不是模型，而是建立在 `LangChain + LangGraph` 之上的 agent harness
- 它适合处理复杂任务，不只是做单轮问答
- 它强调的是：
  - planning
  - tools
  - delegation
  - context management
  - progressive disclosure

### 2. 和普通 agent 的区别

- 普通 agent 更适合较短、较直接的工具调用任务
- Deep Agents 更适合多步骤、长流程、需要分工和上下文管理的任务
- Deep Agents 的重点不是“更像聊天”，而是“更像持续执行任务”

### 3. subagent 的核心价值

- `subagent` 的第一价值是上下文隔离
- 主 agent 不需要持有所有中间细节，只需要拿回子任务结果
- 使用 subagent 的核心目的不是“多智能体更高级”，而是“把复杂任务拆给更合适的执行角色”

### 4. skill 的核心价值

- `skill` 更像流程说明包/方法论包
- 它告诉 agent：遇到某类任务时，应该按什么思路处理
- `skill` 不是执行者，真正执行任务的仍然是 agent 自己
- `skill` 的设计价值包括：
  - 按需加载
  - 节省 token 和上下文
  - 把特定任务套路文件化

### 5. progressive disclosure 是什么

- agent 不会一开始把所有 skill 内容全读进上下文
- 它会先看 skill 的描述是否匹配当前任务
- 只有匹配时，才进一步读取 `SKILL.md`
- 如果 `SKILL.md` 还引用其他参考文件，agent 才可能继续读取那些文件

## Demo 学习记录

### demo_01_basic.py

- 目标：理解 `create_deep_agent(...)` 的最小使用方式
- 关键点：
  - 主 agent 挂普通 tool
  - 没有 subagent
  - `agent.invoke(...)` 是主执行入口
- 当前理解：
  - 这是“主 agent + tool”的最小闭环

### demo_02_subagents.py

- 目标：理解 subagent 如何参与分工
- 关键点：
  - 主 agent 负责协调
  - `researcher` 负责概念/事实
  - `coach` 负责学习计划/题目
- 当前理解：
  - 是否调用 subagent 由主 agent 决策
  - subagent 是否调用自己的 tools，由 subagent 决策

### demo_03_skills.py

- 目标：理解 skill 如何匹配与加载
- 关键点：
  - `skills=[...]` 传的是技能目录
  - agent 先按描述匹配，再按需读取 `SKILL.md`
- 当前理解：
  - `skill` 是指导流程，不是执行角色

### demo_04_composition.py

- 目标：理解 `tool + skill + subagent` 如何组合
- 关键点：
  - tool 负责能力调用
  - skill 负责处理套路
  - subagent 负责完整子任务执行
- 当前理解：
  - 不同层不是“谁更高级”，而是职责不同

### demo_05_memory.py

- 目标：理解 long-term memory 和 thread history 的区别
- 关键点：
  - 对话历史只属于当前 thread
  - memory 文件 + backend/store 可以跨 thread 生效
- 当前理解：
  - 记忆能力不是普通聊天上下文，而是持久化能力

### demo_06_permissions.py

- 目标：理解文件系统权限限制
- 关键点：
  - 有文件工具不代表对所有路径都有权限
  - `permissions` 按操作类型和路径模式做 allow / deny
- 当前理解：
  - `permissions` 是静态边界，不是 prompt 建议

### demo_07_interrupt_on.py

- 目标：理解工具调用前的暂停审批
- 关键点：
  - `interrupt_on` 会先暂停，再等待人工决策
  - 支持 `approve / edit / reject`
  - 恢复执行依赖 `checkpointer + 同一个 thread_id`
- 当前理解：
  - 这是一种配置式 human-in-the-loop

### demo_08_interrupt_primitive.py

- 目标：理解 tool 执行到一半时如何主动暂停
- 关键点：
  - `interrupt()` 发生在 tool 内部
  - 人类回填的不一定是审批动作，也可以是中间参数值
- 当前理解：
  - `interrupt()` 比 `interrupt_on` 粒度更细

## 关键理解纠正

### 纠正 1：Deep Agents 不是“更聪明的聊天”

- 之前容易误以为：它只是回答更复杂
- 正确认识：
  - 它的重点是执行复杂任务
  - 关注点应该放在工具、规划、上下文和验证，而不只是提示词

### 纠正 2：subagent 的重点不是“多几个 agent”

- 容易出现的误解：
  - 以为 subagent 只是为了做 multi-agent 架构
- 正确认识：
  - 它最重要的作用是上下文隔离和职责拆分

### 纠正 3：skill 不是执行者

- 曾经的模糊点：
  - 把 `skill` 想成固定工作流本身在执行任务
- 正确认识：
  - `skill` 是指导 agent 如何处理某类任务的说明包
  - 真正执行任务的还是主 agent

### 纠正 4：没有命中 skill，不代表 agent 不工作

- 曾经的错误回答：
  - “不用 agent，自己完成任务”
- 正确认识：
  - 如果没有 skill 命中，Deep Agent 仍然会继续工作
  - 它会依据：
    - `system prompt`
    - `tools`
    - `subagents`
  - 走普通执行路径

### 纠正 5：不能用“是否调用 tool”来判断“是否调用了 subagent”

- 容易出现的误解：
  - 看到 tool 被调，就以为一定触发了 subagent
- 正确认识：
  - 主 agent 自己也可以直接调用 tool
  - subagent 也可以调用 tool
  - subagent 甚至可能一个 tool 都不调
  - 所以判断 subagent，要看是否真的出现 `task(subagent_type=...)`

### 纠正 6：human-in-the-loop 不只等于 interrupt_on

- 容易出现的误解：
  - 把 HITL 直接等同于 `interrupt_on`
- 正确认识：
  - `human-in-the-loop` 是更上层的设计概念
  - `interrupt_on` 是工具调用前审批的一种实现
  - `interrupt()` 是工具执行中途暂停的更底层实现

## 错题本

### 错题 1

- 题目：`skills` 和 `subagents` 最本质的区别是什么？
- 当时回答：`skills` 是一个固定的工作流程，没有自主决策
- 问题所在：
  - 只答到了“流程”，没答到“角色边界”
  - 没区分“指导任务处理”和“真正执行子任务”
- 正确答案：
  - `skill` 更像流程说明包/方法论包
  - `subagent` 更像执行者，负责被委托的子任务

### 错题 2

- 题目：如果一个任务完全不匹配任何 skill，Deep Agent 会怎样工作？
- 当时回答：不用 agent，自己完成任务
- 问题所在：
  - 误以为 skill 是 agent 工作的前提
- 正确答案：
  - Deep Agent 仍会继续工作
  - 只是不会加载任何 skill
  - 会回到 `system prompt + tools + subagents` 的普通路径

### 错题 3

- 题目：给学习助手设计 2 个 subagents
- 当时回答：
  - 阶段性小节测验
  - 某章节教学包生成
- 问题所在：
  - 这里写成了“任务名”，而不是“执行角色”
  - `subagent` 应该表示一个可被反复委托的工作角色，而不是某一次具体产出
- 正确理解：
  - `subagent` 更适合定义成：
    - `assessor` / 测评助手
    - `lesson_pack_builder` / 教学包生成助手
    - `researcher` / 资料研究助手
    - `coach` / 学习辅导助手
  - 然后再由这些角色去完成：
    - 阶段性小节测验
    - 某章节教学包生成
    - 薄弱点分析
    - 对比整理

## 新一轮设计练习记录

### 用户给出的初版分层

- tools：
  - 记笔记
  - 出题目
  - 查资料
- skills：
  - 教学流程
  - 掌握度检查流程
- subagents：
  - 阶段性小节测验
  - 某章节教学包生成

### 当前点评

- `tools` 方向是对的
- `skills` 方向也是对的
- `subagents` 需要从“任务名”改成“角色名”

### 更合理的一版

- tools：
  - `save_note`
  - `generate_questions`
  - `search_reference`
- skills：
  - `teaching-flow`
  - `mastery-check`
- subagents：
  - `assessor`
    - 负责阶段测验、掌握度检查、薄弱点反馈
  - `lesson_pack_builder`
    - 负责章节学习包、练习组织、复习建议整合

### 用户给出的第二版最小架构

- 主 agent：
  - 统筹全局帮助用户学习
  - 执行任务
  - 调用 skill、tool、subagent
  - 返回结果
- tools：
  - 查资料
  - 出题目
  - 记笔记
- skills：
  - 教学流程
  - 掌握度检查流程
- subagents：
  - 测评助手
  - 教学包生成助手
- 调用链理解：
  - 主 agent 先查资料
  - 再调用教学流程 skill
  - 再调用教学包生成助手生成章节教学包
  - 用户完成单元学习后再记笔记、出题或调用测评助手

### 这一版的进步

- 已经能清楚区分：
  - 主 agent 负责统筹
  - tool 负责动作
  - skill 负责流程
  - subagent 负责完整子任务
- `subagent` 这次已经改成了“角色名”，这是明显进步

### 这一版还需要纠正的点

- 问题 1：把主 agent 写成“执行任务”有点宽泛
  - 更准确的说法应是：
    - 主 agent 负责理解用户目标
    - 决定当前该用哪个 skill
    - 判断是否需要 tool 或 subagent
    - 汇总结果并继续推进下一步

- 问题 2：调用链里不应该默认“每次都先查资料”
  - 更合理的理解是：
    - 主 agent 先判断当前任务类型
    - 如果缺资料，再调用 `search_reference`
    - 如果只是复盘或测验，不一定需要查资料

- 问题 3：`记笔记` 更适合放在收尾或状态更新阶段
  - 它通常不是核心教学流程的最前置动作
  - 更像学习闭环中的记录动作

### 当前更成熟的一版调用链

1. 用户发出学习请求
2. 主 agent 判断这是“讲解 / 练习 / 测评 / 复盘”中的哪一类
3. 主 agent 决定是否匹配 `teaching-flow` 或 `mastery-check`
4. 如果缺外部事实或参考资料，再调用 `search_reference`
5. 如果任务是完整章节学习包，委托 `lesson_pack_builder`
6. 如果任务是阶段测评或薄弱点诊断，委托 `assessor`
7. 主 agent 汇总结果
8. 如有必要，调用 `save_note` 记录学习要点、错题和本轮结论

## 执行路径判断练习

### 当前路径分类

- `A`：主 agent 直接回答
- `B`：主 agent + tools
- `C`：主 agent + subagent
- `D`：主 agent + tools + subagent

### 新一轮用户自拟场景

- 场景 1：阶段性章节知识检测
  - 用户判断：`D`
- 场景 2：根据当前学习进度生成学习计划
  - 用户判断：`B`

### 本轮 review

- 场景 1：`阶段性章节知识检测`
  - `D` 可以成立，但不是唯一答案
  - 如果检测范围较小，只是：
    - 出几道题
    - 做一个简单掌握度判断
    - 记录结果
    - 那么 `B` 就够了
  - 只有当任务变成：
    - 读取较多学习记录
    - 汇总多轮错题
    - 分析薄弱点
    - 生成阶段报告
    - 才更像 `D`

- 场景 2：`根据当前学习进度生成学习计划`
  - `B` 是合理答案
  - 如果只是读取当前进度、结合模板生成计划，主 agent + tools 往往就够了
  - 只有当输入规模变大，例如：
    - 大量学习记录
    - 多学科并行
    - 多阶段目标拆分
    - 才可能升级到 `D`

### 本轮纠正出来的判断标准

- 不要只看任务名称，要看任务规模
- “知识检测”不一定天然需要 subagent
- “学习计划”也不一定只是普通文本生成，要看背后输入有多重
- 真正决定执行路径的，不是名词，而是：
  - 上下文大小
  - 是否需要独立子任务
  - 是否值得上下文隔离

## 微项目学习记录

### 项目：learning_assistant

- 对应文件：
  - [learning_assistant.py](/Users/liangzhe/workspace/codex/deep-agents-t1/deepagents_project/learning_assistant.py)
- 目标：
  - 用一个最小真实项目把 `tool + skill + subagent` 落地
- 当前结构：
  - tools：
    - `search_reference`
    - `generate_questions`
    - `save_note`
  - skills：
    - `teaching-flow`
    - `mastery-check`
  - subagents：
    - `assessor`
    - `lesson_pack_builder`

### 当前最关键的项目理解

- 主 agent 负责统筹和结果整合
- tools 负责基础动作
- skills 负责稳定工作流
- subagents 负责完整子任务
- 不是每次运行都会触发 subagent

## 日志与调试能力学习记录

### 为什么需要运行日志

- 只看最终回答，看不出 agent 中间做了什么
- 学习 Deep Agents 时，关键不只是“结果对不对”，而是：
  - 模型推理了几轮
  - 调了哪些 tools
  - 有没有触发 subagent
  - 最终结果是主 agent 自己整合，还是委托后汇总

### 当前日志系统

- 已把微项目日志切到 `loguru`
- 已接入 `astream_events()` 做事件流观察
- 当前会输出：
  - agent 启动
  - 模型第几轮开始/结束
  - tool 开始/结束
  - 是否真正 dispatch 了 subagent
  - 最终运行摘要

### 日志阅读的关键规则

- `Model round N started/finished`
  - 表示第 N 轮模型推理
- `Tool started/finished`
  - 表示真实工具调用
- `Subagent dispatched: xxx`
  - 只有看到这一类高置信度日志，才能判断真的触发了 subagent
- `save_note`
  - 这是脚本层收尾动作，不是 agent graph 内部的核心决策链

### 当前一次真实运行的结论

- 运行形态：
  - 两轮模型推理
  - 两个 tool 调用
  - 没有触发 subagent
- 可复述成：
  - 主 agent 第 1 轮思考
  - 调 `search_reference` 和 `generate_questions`
  - 主 agent 第 2 轮整合输出
  - 脚本最后调用 `save_note`

## 新增运行与工程问题记录

### 问题 4：`stream_events(version='v2') is not supported`

- 原因：
  - 当前 `CompiledStateGraph` 不支持同步版 `stream_events(version='v2')`
- 纠正：
  - 改用 `astream_events()` 并通过 `asyncio.run(...)` 包装

### 问题 5：日志误判 subagent

- 原因：
  - 之前使用了宽松的启发式检测，把太多 graph 事件都标成“possible subagent/task”
- 纠正：
  - 只在检测到 `task` tool 且参数里存在 `subagent_type` 时，才打印真正的 subagent dispatch 日志

### 问题 6：memory demo 读取字段写错

- 现象：
  - `KeyError: 'text'`
- 原因：
  - `create_file_data()` 生成的数据字段是 `content`，不是 `text`
- 纠正：
  - 读取 memory 快照时改为优先取 `content`

### 问题 7：memory demo backend 写法过时

- 现象：
  - `StateBackend(rt)` / `StoreBackend(rt, ...)` / backend factory 触发弃用警告
- 原因：
  - 当前安装版 deepagents 推荐直接传 backend 实例
- 纠正：
  - 改成：
    - `StateBackend()`
    - `StoreBackend(store=store, namespace=...)`
    - `backend=CompositeBackend(...)`

## 运行与工程问题记录

### 问题 1：`ModuleNotFoundError: No module named 'deepagents'`

- 原因：
  - 当时使用了系统 Python，而不是项目 `.venv`
- 纠正：
  - 用 `uv run python ...` 或激活 `.venv` 后再运行

### 问题 2：401 invalid api key

- 原因：
  - 使用了代理服务的 key，但代码仍按默认 OpenAI 路径理解
- 纠正：
  - 显式配置：
    - `OPENAI_API_KEY`
    - `OPENAI_BASE_URL`
    - `OPENAI_MODEL`

### 问题 3：500 service unavailable

- 原因：
  - 更像代理服务短时不稳定，而不是代码确定性错误
- 当前理解：
  - 单 agent 请求比多轮 orchestration 更稳定
  - subagent / tools 较多时，更容易放大代理服务波动

## 现在已经能说清的 3 句话

1. `subagent` 的第一价值是上下文隔离，而不是“多智能体更高级”。
2. `skill` 是流程说明包，`subagent` 是执行者。
3. 没有命中 skill 时，Deep Agent 仍然会基于 `system prompt + tools + subagents` 继续工作。

## 下一步学习方向

- 下一轮重点：学 `skills + subagents + tools` 如何组合使用
- 要重点理解真实项目里：
  - 哪些规则应该放进 skill
  - 哪些职责应该拆成 subagent
  - 哪些能力应该做成 tool
- 已新增待学习示例：
  - [demo_04_composition.py](/Users/liangzhe/workspace/codex/deep-agents-t1/deepagents_demo/demo_04_composition.py)

## 新阶段学习方向

- 当前进入的新主题：`long-term memory`
- 核心问题：
  - 什么是跨 thread 记忆
  - 它和普通对话历史有什么区别
  - memory 文件、backend、store 各自扮演什么角色
- 对应示例：
  - [demo_05_memory.py](/Users/liangzhe/workspace/codex/deep-agents-t1/deepagents_demo/demo_05_memory.py)

## Memory 学习结论

### 本轮真正学会了什么

- `short-term memory` 和 `long-term memory` 的区别
- `memory` / `backend` / `store` / `agent` 各自负责什么
- `/memories/preferences.md` 在当前 demo 里是逻辑路径，不是本地磁盘真实文件
- 为什么长期记忆和普通临时文件要分开存

### 当前可复述的标准说法

- `memory`
  - 声明哪些文件属于长期记忆
- `backend`
  - 决定这些逻辑文件路径走哪条存储路由
- `store`
  - 底层真正保存长期数据的地方
- `agent`
  - 负责判断用户输入里哪些信息值得写入长期记忆

### 本轮关键理解

- 用户输入不会一开始就自动按 backend 分类存储
- 正确顺序是：
  - 先进入 `messages`
  - agent 判断是否值得长期记忆
  - 如果写到 `/memories/...`
  - backend 再把它路由到 `StoreBackend`

### 本轮结果验证

- Thread 1 确实更新了 memory 文件
- Thread 2 在不同 `thread_id` 下仍能继续使用这份记忆
- 所以这次验证通过的是：
  - 跨 thread 的 long-term memory
  - 不是单纯的会话上下文延续

## Permissions / HITL 学习结论

### `permissions`

- 作用：
  - 对文件系统访问做静态边界限制
- 判断维度：
  - 操作类型：`read` / `write`
  - 路径模式：如 `/notes/**`
- 本轮结论：
  - `permissions` 不是提示词建议，而是真正的执行约束

### `interrupt_on`

- 作用：
  - 在工具调用前暂停，等待人工审批
- 典型决策：
  - `approve`
  - `edit`
  - `reject`
- 本轮结论：
  - 它适合“可以做，但做之前必须看一眼”的动作

### `interrupt()`

- 作用：
  - 在 tool 或 graph 执行到中间步骤时主动暂停
- 特点：
  - 不一定返回审批动作
  - 也可以要求人类直接回填一个中间参数值
- 本轮结论：
  - 它比 `interrupt_on` 粒度更细，更适合执行中确认

### `human-in-the-loop`

- 作用：
  - 是“人参与关键执行闭环”的总概念
- 和具体机制的关系：
  - `interrupt_on` 是一种实现
  - `interrupt()` 也是一种实现

### 本轮关键边界总结

- `permissions`
  - 能不能做
- `interrupt_on`
  - 做之前先审批
- `interrupt()`
  - 做到一半再确认
- `human-in-the-loop`
  - 人参与关键节点决策的整体机制

### 本轮真实运行结论

- `demo_06_permissions.py`
  - `/notes/today.md` 写入成功
  - `/private/secret.txt` 写入失败
  - 说明 permissions 已真实生效

- `demo_07_interrupt_on.py`
  - agent 先返回待审批工具及原始参数
  - 恢复执行时用编辑后的参数继续
  - 说明 `interrupt_on` 的 pause / edit / resume 跑通

- `demo_08_interrupt_primitive.py`
  - tool 先执行前半段
  - 中途 `interrupt()` 把建议主题和草稿正文交给人
  - 恢复后继续后半段执行
  - 说明执行中暂停链路跑通

## 今天的阶段结论

- 已掌握：
  - Deep Agents 不是模型，而是 agent harness
  - `tool / skill / subagent` 的职责边界
  - 什么时候更可能走 `A/B/C/D` 这些执行路径
  - 如何从简化日志中读出：
    - 第几轮模型推理
    - 哪些 tools 被调用
    - 有没有真正 dispatch subagent
  - `memory / backend / store / agent` 在长期记忆里的分工
  - `permissions / interrupt_on / interrupt() / human-in-the-loop` 的边界
- 下一次继续时，优先学习：
  - 更完整的生产级 agent 安全与控制面
  - 真实项目里怎么组合长期记忆、权限和人工审批

## 后续维护规则

以后每学完一轮，持续补充以下内容：

- 新学会的概念
- 新跑通的 demo / 小项目
- 当轮错题
- 容易混淆的边界
- 实战中的报错与修复经验
