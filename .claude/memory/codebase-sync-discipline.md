---
name: codebase-sync-discipline
description: 开发即文档——每阶段完成后同步更新 codebase 文档和 memory 的经验
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# 开发即文档 (Document Alongside Coding)

## 原则

每完成一个开发阶段(W1-W8)，在提交代码前必须同步更新以下文档:

### 必须更新的文件

| 文件 | 更新内容 |
|------|---------|
| `.claude/codebase/MODULE_MAP.md` | 新增模块的职责/接口/依赖/状态标记 |
| `.claude/codebase/BUILD_STATUS.md` | 进度条推进、组件状态更新(✅/🏗/📋)、测试覆盖率 |
| `.claude/codebase/CONVENTIONS.md` | 新增代码约定或模式 |
| `.claude/codebase/DATA_FLOW.md` | 新增数据路径或修改现有流程 |
| `.claude/codebase/API_SURFACE.md` | 新增/变更的 API 端点 |
| `docs/week<N>-learning-resources.md` | 本阶段技术栈学习指南 |
| `memory/next-steps.md` | 完成项标记、优先级更新 |

### 推荐触发时机

> 代码写完 80% → 开始写文档 → 写完最后 20% 代码 → 完善文档

不要在全部代码完成后再补文档。正确的节奏是: **关键接口写完就记，架构决策定了就写，测试通过后更新覆盖率。**

## 为什么

- AI 下次进入项目时不需要重新 grep 整个代码库来理解新模块
- `MODULE_MAP.md` 的 "状态标记"(✅/🏗/📋) 让 AI 一眼知道什么可用、什么只是骨架
- 不及时更新 → `BUILD_STATUS.md` 显示"待实现"但代码已经写了 → AI 产生困惑

**How to apply:**
- 每次 `git diff --stat` 确认变化范围后，对照上述清单逐项更新
- 先更新文档再 `git commit`，不要留到"下次再说"
