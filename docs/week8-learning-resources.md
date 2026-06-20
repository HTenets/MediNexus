---
name: week8-learning-resources
description: W8 技术栈学习文档——Docker 部署、BYO Key、项目文档体系、v0.1.0 发布
metadata:
  type: reference
---

# MediNexus W8 技术栈学习指南

> 本文档列出了第 8 周部署 + 文档 + v0.1.0 发布中用到的所有技术，适合新手按顺序学习。

---

## 一、Docker 多阶段构建

### 1. 什么是多阶段构建

传统 Dockerfile 只有一个 `FROM`，导致镜像包含构建工具和源码，体积很大。
多阶段构建使用多个 `FROM`，**先在一个镜像中编译，再在另一个干净的镜像中只复制产物**，大幅减小镜像体积。

```dockerfile
# 阶段 1: build — 安装依赖和编译
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm ci
COPY . .
RUN npm run build

# 阶段 2: run — 只有产物
FROM node:20-alpine AS run
WORKDIR /app
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
CMD ["npx", "next", "start"]
```

### 2. Frontend Dockerfile

| 项目 | 内容 |
|------|------|
| **文件位置** | `frontend/Dockerfile` |
| **基础镜像** | `node:20-alpine` |
| **构建阶段** | `npm ci` → `npm run build` |
| **运行阶段** | 只复制 `.next/`、`node_modules/`、`package.json`、`next.config.js` |
| **启动** | `next start -p 3000` |

### 3. Backend Dockerfile

| 项目 | 内容 |
|------|------|
| **文件位置** | `infrastructure/docker/Dockerfile.backend` |
| **基础镜像** | `python:3.12-slim` |
| **安装** | `pip install -e ".[dev]"` |
| **启动** | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |

---

## 二、Docker Compose 生产配置

### 4. 服务清单

| 服务 | 镜像 | 端口 | 健康检查 |
|------|------|------|---------|
| postgres | pgvector/pgvector:pg17 | 5432 | pg_isready |
| redis | redis:7-alpine | 6379 | redis-cli ping |
| qdrant | qdrant/qdrant:latest | 6333 | — |
| backend | 自构建 | 8000 | — |
| frontend | 自构建 | 3000 | — |

### 5. 启动命令

```bash
# 一键启动全部
docker compose up --build

# 仅启动数据库（本地开发时）
docker compose up postgres redis qdrant

# 后台运行
docker compose up -d

# 停止
docker compose down
```

---

## 三、BYO Key 配置

### 6. 为什么需要 BYO Key

MediNexus **不内置任何 API Key**，遵循以下原则：
- 项目本身是开源免费的
- 用户自行选择 LLM Provider
- 无 Key 时自动降级到规则引擎模式

### 7. 三种 Provider 配置

```env
# Ollama（推荐，免费）
MEDINEXUS_LLM_PROVIDER=ollama
MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434

# Anthropic Claude
MEDINEXUS_LLM_PROVIDER=anthropic
MEDINEXUS_ANTHROPIC_KEY=sk-ant-xxxx

# OpenAI
MEDINEXUS_LLM_PROVIDER=openai
MEDINEXUS_OPENAI_KEY=sk-xxxx
```

### 8. 降级链

```
Ollama 可用 → 使用 Ollama
Ollama 不可用 + 有 OpenAI Key → 使用 OpenAI
Ollama 不可用 + 有 Anthropic Key → 使用 Anthropic
全部不可用 → 规则引擎降级模式 (标注 [模式: 规则引擎])
```

详细配置见 `docs/byok-guide.md`。

---

## 四、Makefile 命令

```bash
# 开发
make dev-backend      # uvicorn backend
make dev-frontend     # next dev

# Docker
make docker-up        # docker compose up --build
make docker-down      # docker compose down
make docker-db-only   # 仅数据库

# 数据库
make db-migrate msg="描述"
make db-upgrade
make init-db

# 测试
make test             # 全部测试
make test-unit        # 单元测试
make test-integration # 集成测试

# 依赖
make install          # pip + npm
```

---

## 五、项目文档体系

### 9. 文档清单

| 文档 | 用途 | 阅读时机 |
|------|------|---------|
| `README.md` | 项目概览、快速开始 | 第一次接触项目 |
| `docs/architecture.md` | 系统架构和 Agent 流程 | 理解整体设计 |
| `docs/api-reference.md` | REST + WebSocket API 详情 | 对接 API |
| `docs/agent-design.md` | Agent 间通信协议 | 扩展 Agent |
| `docs/byok-guide.md` | LLM 配置指南 | 配置 LLM |
| `docs/docker-quickstart.md` | Docker 零基础教程 | 第一次用 Docker |
| `docs/frontend-design-reference.md` | 前端设计规范 | 修改前端 |
| `docs/weekN-learning-resources.md` | 每周技术栈详解 | 学习特定技术 |

### 10. AI 代码结构文档

位于 `.claude/codebase/`，供 AI 阅读：

| 文件 | 内容 |
|------|------|
| `MODULE_MAP.md` | 模块清单、职责、状态 |
| `BUILD_STATUS.md` | 构建进度、测试覆盖率 |
| `CONVENTIONS.md` | 编码规范 |
| `API_SURFACE.md` | API 端点定义 |
| `DATA_FLOW.md` | 数据流图 |
| `DEPENDENCY_GRAPH.md` | 模块依赖关系 |

---

## 六、关键命令速查

```bash
# 本地开发
conda activate medinexus
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && npm run dev

# Docker 生产
docker compose up --build

# 运行测试（快速：跳过慢测试）
cd backend && python -m pytest tests/ -m "not slow" -v

# 运行测试（全量）
cd backend && python -m pytest tests/ -v

# 前端构建验证
cd frontend && npm run build

# 查看 Git 标签
git tag -l
```
