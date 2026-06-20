# Deep Agents Fast Track

This workspace is a compact learning path for LangChain Deep Agents.

## What to learn first

Deep Agents is not a new model. It is a higher-level harness built on LangChain and LangGraph for tasks that need planning, file tools, delegation, and tighter control over long workflows.

You only need three ideas to get started:

1. `create_deep_agent(...)` is the main entry point.
2. Deep Agents can plan and use built-in file tools automatically.
3. Subagents are mainly for context isolation, not for "more agents for the sake of it".

## Files

- `deepagents_fasttrack.md`: Chinese study note for quick understanding
- `deepagents_demo/demo_01_basic.py`: smallest runnable example
- `deepagents_demo/demo_02_subagents.py`: example that shows why subagents exist
- `deepagents_demo/demo_03_skills.py`: example that shows how skills are matched and loaded
- `deepagents_demo/demo_04_composition.py`: example that combines tools, skills, and a custom subagent
- `deepagents_demo/demo_05_memory.py`: example that shows long-term memory across threads
- `deepagents_demo/demo_06_permissions.py`: example that shows path-based filesystem permissions with real filesystem writes
- `deepagents_demo/demo_07_interrupt_on.py`: example that shows pause-and-resume approval for tool calls
- `deepagents_demo/demo_08_interrupt_primitive.py`: example that shows pausing in the middle of a tool with interrupt()
- `deepagents_demo/demo_09_middleware.py`: example that shows middleware intercepting tool execution
- `deepagents_demo/demo_10_middleware_rewrite.py`: example that shows middleware rewriting tool arguments before execution
- `deepagents_project/learning_assistant.py`: minimal project that combines the three layers into a learning assistant
- `deepagents_demo_flow.md`: visual explanation for demo execution flow

## Setup

```bash
cp .env.example .env
uv sync
```

Then fill `.env` with your real credentials.

For official OpenAI:

```bash
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.4
```

For an OpenAI-compatible proxy or gateway:

```bash
OPENAI_API_KEY=your-proxy-key
OPENAI_BASE_URL=https://your-provider-endpoint/v1
OPENAI_MODEL=the-provider-model-id
```

Replace `OPENAI_BASE_URL` and `OPENAI_MODEL` with the exact values required by your provider.

This project already declares `langchain`, `deepagents`, and `langchain-openai` in `pyproject.toml`, which matches the current official quickstart direction for an OpenAI-backed setup.

## Run

```bash
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_01_basic.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_02_subagents.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_03_skills.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_04_composition.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_05_memory.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_06_permissions.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_07_interrupt_on.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_08_interrupt_primitive.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_09_middleware.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_demo/demo_10_middleware_rewrite.py
UV_CACHE_DIR=.uv-cache uv run python deepagents_project/learning_assistant.py
```

## What to observe

- In `demo_01_basic.py`, focus on the shape of `create_deep_agent(...)` and `agent.invoke(...)`.
- In `demo_02_subagents.py`, focus on task delegation boundaries.
- In `demo_03_skills.py`, focus on skill matching and progressive disclosure.
- In `demo_04_composition.py`, focus on which responsibilities belong to tools, skills, and subagents.
- In `demo_05_memory.py`, focus on the difference between thread history and long-term memory.
- In `demo_06_permissions.py`, focus on how `permissions` and `FilesystemBackend` each play a different role: one controls access, the other controls real storage.
- In `demo_07_interrupt_on.py`, focus on the difference between direct denial and pause-for-approval.
- In `demo_08_interrupt_primitive.py`, focus on how a tool can pause halfway through execution.
- In `demo_09_middleware.py`, focus on how middleware can intercept tool execution without rewriting the tool itself.
- In `demo_10_middleware_rewrite.py`, focus on how middleware can rewrite tool arguments and still let the real tool run.
- When the task is simple, Deep Agents may not need to delegate much. That is normal.
- All demos create `ChatOpenAI(...)` explicitly, so they can target official OpenAI or any OpenAI-compatible endpoint.

## Suggested next step

After these two demos, replace the fake local tools with one real external tool:

- web search
- a local codebase search tool
- a database lookup tool

That is where the value of Deep Agents becomes much more obvious.
