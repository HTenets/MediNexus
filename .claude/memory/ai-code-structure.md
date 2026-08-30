---
name: ai-code-structure
description: 项目 AI 可读代码结构文档系统
metadata: 
  node_type: memory
  type: reference
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# AI 代码结构文档系统

项目根目录 `.claude/codebase/` 维护了一套 AI 可读的代码结构文档:

| 文件 | 内容 |
|------|------|
| `MODULE_MAP.md` | 完整模块清单, 含职责/接口/依赖/状态标记 |
| `API_SURFACE.md` | 所有 API 端点记录 (请求/响应/错误) |
| `DATA_FLOW.md` | 数据流图 (REST/WebSocket/Agent Pipeline) |
| `DEPENDENCY_GRAPH.md` | 模块依赖图和影响范围分析 |
| `BUILD_STATUS.md` | 构建状态 (完成度/已知问题/开发阶段) |
| `CONVENTIONS.md` | 代码约定 (命名/结构/协议/错误处理) |
| `README.md` | 索引和快速查询指南 |

## 用法

- AI 在开始任务前应查阅 `MODULE_MAP.md` 了解相关模块
- 修改 API 时参阅 `API_SURFACE.md`
- 修改编排逻辑时参阅 `DATA_FLOW.md` + `DEPENDENCY_GRAPH.md`
- 了解开发优先级时参阅 `BUILD_STATUS.md`
- 写新文件时参阅 `CONVENTIONS.md`

**Why:** AI 长程开发需要结构化的上下文感知。没有这些文档, AI 每次需要重新探索整个代码库, 效率低且容易遗漏边界情况。

**How to apply:** 当修改代码结构(新增模块/修改接口/改变数据流)时, 同步更新对应的文档。
