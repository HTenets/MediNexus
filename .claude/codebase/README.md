# MediNexus AI 代码结构索引

> 此目录包含 AI 可读的代码结构文档。
> 版本: v0.1.0 (2026-06-19) — 8 周开发全部完成。
> AI 在开始任务前应查阅相关文档以理解代码上下文。

## 文档列表

| 文件 | 用途 | 推荐阅读时机 |
|------|------|-------------|
| [MODULE_MAP.md](MODULE_MAP.md) | 完整模块清单: 职责/接口/依赖/状态 | ✅ 每次任务前查阅 |
| [BUILD_STATUS.md](BUILD_STATUS.md) | 构建状态: 完成度/已知问题/测试覆盖率 | 了解当前开发阶段 |
| [CONVENTIONS.md](CONVENTIONS.md) | 代码约定: 命名/结构/协议/错误处理 | 写新文件时 |
| [API_SURFACE.md](API_SURFACE.md) | API 端点: REST/Mock/WebSocket/数据模型 | 修改 API 时 |
| [DATA_FLOW.md](DATA_FLOW.md) | 数据流: REST/WebSocket/Agent Pipeline/记忆/Guardrail | 修改编排逻辑时 |
| [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) | 依赖图: 导入关系/影响范围 | 重构/修改核心模块时 |

## 快速查询

| 场景 | 阅读 |
|------|------|
| 新增一个 Agent | `CONVENTIONS.md` (模板) + `MODULE_MAP.md` (现有 Agent) |
| 新增 API 端点 | `API_SURFACE.md` (现有路由) + `CONVENTIONS.md` (路由风格) |
| 修改 Agent Pipeline | `DATA_FLOW.md` (数据流) + `DEPENDENCY_GRAPH.md` (影响分析) |
| 了解开发优先级 | `BUILD_STATUS.md` (已完成 vs 待办) |
| 做架构决策 | `architecture-decisions.md` (ADR-001~014) + `design-decisions.md` (7 项产品决策) |
