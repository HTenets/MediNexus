# MediNexus AI 代码结构索引

> 此目录包含 AI 可读的代码结构文档。
> AI 在开始任务前应查阅相关文档以理解代码上下文。

## 文档列表

| 文件 | 用途 | 推荐阅读时机 |
|------|------|-------------|
| [MODULE_MAP.md](MODULE_MAP.md) | 完整模块清单: 职责/接口/依赖/状态 | ✅ 每次任务前查阅 |
| [API_SURFACE.md](API_SURFACE.md) | API 端点: 路由/请求/响应/错误 | 修改 API 时 |
| [DATA_FLOW.md](DATA_FLOW.md) | 数据流: REST/WebSocket/Agent Pipeline | 修改编排逻辑时 |
| [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) | 依赖图: 导入关系/影响范围 | 重构/修改核心模块时 |
| [BUILD_STATUS.md](BUILD_STATUS.md) | 构建状态: 完成度/已知问题/Todo | 了解当前开发阶段 |
| [CONVENTIONS.md](CONVENTIONS.md) | 代码约定: 命名/结构/协议/错误处理 | 写新文件时 |

## 快速查询

- **新增一个 Agent** → 看 [CONVENTIONS.md](CONVENTIONS.md#agent-实现模板) + [MODULE_MAP.md](MODULE_MAP.md#11-agent-系统-backendagents)
- **新增 API 端点** → 看 [API_SURFACE.md](API_SURFACE.md) + [CONVENTIONS.md](CONVENTIONS.md#api-路由)
- **修改 Agent Pipeline** → 看 [DATA_FLOW.md](DATA_FLOW.md#3-agent-pipeline-内部数据流) + [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md#3-影响范围分析)
- **了解当前开发优先级** → 看 [BUILD_STATUS.md](BUILD_STATUS.md)
