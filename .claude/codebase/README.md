# MediNexus 代码结构索引（AI 可读）

> AI 在开始任务前应查阅相关文档以理解代码上下文。
> 版本: 对齐 **v0.1.1**（2026-08-30 去伪存真）。能力真伪以根 `README.md`「实现状态」表为准。

## 文档列表

| 文件 | 用途 | 推荐阅读时机 |
|------|------|-------------|
| [MODULE_MAP.md](MODULE_MAP.md) | 完整模块清单: 职责/接口/状态 | ✅ 每次任务前查阅 |
| [BUILD_STATUS.md](BUILD_STATUS.md) | 构建状态: 完成度/测试 | 了解当前开发阶段 |
| [CONVENTIONS.md](CONVENTIONS.md) | 代码约定: 命名/结构/协议/错误处理 | 写新文件时 |
| [API_SURFACE.md](API_SURFACE.md) | API 端点: REST/WebSocket/数据模型 | 修改 API 时 |
| [DATA_FLOW.md](DATA_FLOW.md) | 数据流: 问诊流水线/记忆/RAG/护栏 | 修改编排逻辑时 |
| [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) | 依赖图: 导入关系/影响范围 | 重构/修改核心模块时 |
| [architecture-decisions.md](architecture-decisions.md) | 架构决策 ADR-001~014 | 做架构决策时 |
| [design-decisions.md](design-decisions.md) | 产品设计决策 D1~D7 | 做产品决策时 |

## 快速查询

| 场景 | 阅读 |
|------|------|
| 新增一个 Agent | `CONVENTIONS.md` + `MODULE_MAP.md`（agents/） |
| 新增 API 端点 | `API_SURFACE.md` + `CONVENTIONS.md` |
| 修改问诊流水线 | `DATA_FLOW.md` + `DEPENDENCY_GRAPH.md` |
| 了解当前能力真伪 | 根 `README.md`「实现状态」表 |
