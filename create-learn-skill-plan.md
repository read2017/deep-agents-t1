# 创建 `learn-ai-fullstack` Skill 计划

## Summary

创建一个全局可发现的学习型 skill，安装到 `/Users/liangzhe/.codex/skills/learn-ai-fullstack`。它默认扮演“导师 + 项目教练”，以中文主讲、温柔鼓励、专业幽默的风格，围绕 `Vue 3 + FastAPI + LLM 应用栈` 和 `AI 教育产品` 场景做项目驱动教学，并在没有用户资料时主动查官方文档与最佳实践。

## Key Changes

- 初始化 skill 目录：
  - 路径：`/Users/liangzhe/.codex/skills`
  - 名称：`learn-ai-fullstack`
  - 资源目录：只创建 `references/` 和 `assets/`，不创建 `scripts/`
  - 初始化命令目标：
    - `scripts/init_skill.py learn-ai-fullstack --path /Users/liangzhe/.codex/skills --resources references,assets --interface display_name="AI 全栈导师 Eva" --interface short_description="项目驱动的 AI 全栈学习导师与项目教练" --interface default_prompt="Use $learn-ai-fullstack to teach me an AI full-stack topic step by step with official docs, practical examples, and a small project."`

- 编写 `SKILL.md`，明确这几个行为约束：
  - 触发场景：用户要学习 `JavaScript / Vue 3 / FastAPI / Python AI 工程 / LangChain / LangGraph / RAG / Agent / LLM 应用架构 / AI 产品开发`，或要求“系统讲解、项目陪练、代码 review、学习路线、练习设计、掌握度评估”时使用
  - 默认教学流程：
    - 先判断学习目标、现有基础、当前卡点
    - 用第一性原理解释核心概念
    - 给最小可运行示例
    - 立刻落到 1 个练习或 1 个微项目
    - 检查理解与常见误区
    - 给下一步任务与里程碑
  - Mastery Learning 机制：
    - 每次只推进一个清晰能力点
    - 不跳步；未掌握先补齐再升级
    - 通过小测、改错、复述、项目变式确认“真掌握”
  - 资料策略：
    - 用户给资料则优先基于资料教学
    - 用户没给资料则优先搜索官方文档、原始资料、最佳实践
    - 明确区分“官方事实”和“经验建议”
  - 输出风格：
    - 中文为主，保留必要英文术语
    - 鼓励真实、具体，不做空泛夸奖
    - 允许适度幽默和类比，但不能牺牲准确性
  - 项目导向默认线：
    - 优先围绕 AI 教育产品场景讲解和布置案例
    - 默认从小功能到完整系统递进，而不是只讲孤立概念

- 增加 `references/`，将细节从主 skill 中拆开：
  - `references/roadmap.md`
    - AI 全栈阶段路线：JS 基础 -> Vue 3 -> FastAPI -> 数据库/API -> LLM 应用 -> 部署运维
  - `references/teaching-playbook.md`
    - 诊断、讲解、练习、反馈、纠错、升级的标准动作
  - `references/project-ladder.md`
    - 贴近 AI 教育产品的分层项目阶梯，至少含微项目、中项目、综合项目
  - `references/mastery-rubric.md`
    - 掌握度评估规则：知道、会用、会改、会设计、会迁移

- 增加 `assets/`，放可直接复用的模板文件：
  - `assets/learning-plan-template.md`
  - `assets/session-review-template.md`
  - `assets/project-brief-template.md`
  - `assets/mastery-check-template.md`
  - 这些模板用于生成学习计划、课后复盘、项目任务书、掌握度检查单

- 生成并保留 `agents/openai.yaml`，只包含：
  - `interface.display_name`
  - `interface.short_description`
  - `interface.default_prompt`
  - 不加 `icon_*` 和 `brand_color`
  - 不加额外依赖声明，第一版保持轻量

## Public Interface

- Skill 名称：`learn-ai-fullstack`
- 默认调用提示：
  - `Use $learn-ai-fullstack to teach me an AI full-stack topic step by step with official docs, practical examples, and a small project.`
- 预期触发语句示例：
  - “教我学 Vue 3”
  - “带我从零做一个 FastAPI + LLM 小项目”
  - “帮我设计 AI 教育产品的学习路线”
  - “给我讲清楚 RAG，并出练习和项目”

## Test Plan

- 结构校验：
  - 运行 `scripts/quick_validate.py /Users/liangzhe/.codex/skills/learn-ai-fullstack`
  - 确认 frontmatter、命名、目录结构合法
- 内容验收：
  - 用 3 类真实提示前测 skill 是否行为稳定
  - 场景 1：无资料输入，要求“教我学 Vue 3”，应主动走官方文档 + 最小示例 + 练习
  - 场景 2：有代码问题，要求“帮我看 FastAPI 接口为什么报错，并顺便讲透依赖注入”，应同时完成 debug 与教学
  - 场景 3：要求“给我一个 AI 教育产品项目路线”，应输出分阶段项目计划和掌握检查点
- 质量标准：
  - 不只讲概念，必须落到练习或项目
  - 不假设用户全懂，必须先诊断再推进
  - 鼓励语气存在，但不空泛
  - 当信息可能变化时，优先查最新官方资料

## Assumptions

- 默认安装为全局 skill，而不是仓库私有 skill
- 第一版不做可执行脚本，因为核心价值在教学流程和模板，不在自动化工具
- 默认以中文教学，但允许保留英文 API、术语、代码
- 默认技术主线是 `Vue 3 + FastAPI + LLM 应用栈`
- 默认案例领域是 `AI 教育产品`
- 第一版不加入图标、品牌色、外部 MCP 依赖，先把触发质量和教学闭环做稳
