---
name: week1-learning-resources
description: W1 技术栈学习文档——包含每项技术的项目作用、使用方式、官方文档地址
metadata:
  type: reference
---

# MediNexus W1 技术栈学习指南

> 本文档列出了第 1 周项目基础设施中用到的所有技术，适合新手按顺序学习。

---

## 一、后端核心

### 1. Python 3.12+

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 整个后端的基础语言，所有后端代码用 Python 编写 |
| **如何使用** | `backend/` 目录下所有 `.py` 文件；异步编程用 `async/await` |
| **新手学习重点** | 类型注解（type hints）、`async/await`、`dataclass`、包管理（`pyproject.toml`） |
| **官方文档** | https://docs.python.org/3.12/ |

### 2. FastAPI

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | Web 框架，提供 REST API 和 WebSocket 接口 |
| **如何使用** | `backend/app/main.py` 创建 `FastAPI()` 实例；`backend/app/api/` 下定义路由；依赖注入通过 `Depends()` |
| **关键代码** | `app = FastAPI(title="MediNexus")` → `app.include_router(api_router)` |
| **新手学习重点** | 路径装饰器（`@app.get()`）、路径参数、查询参数、请求体（Pydantic）、依赖注入 |
| **官方文档** | https://fastapi.tiangolo.com/ |

### 3. Uvicorn

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | ASGI 服务器，让 FastAPI 应用跑起来 |
| **如何使用** | 命令行启动：`uvicorn app.main:app --reload --port 8000` |
| **官方文档** | https://www.uvicorn.org/ |

### 4. Pydantic v2

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 数据验证 + 配置管理 |
| **如何使用** | `backend/app/schemas/` 下定义请求/响应模型；`backend/app/config.py` 用 `BaseSettings` 管理环境变量 |
| **关键代码** | `class ConsultationRequest(BaseModel):` + `class Settings(BaseSettings):` |
| **新手学习重点** | `BaseModel`、字段类型验证、`model_config`、`Field()`、配置继承 |
| **官方文档** | https://docs.pydantic.dev/latest/ |

### 5. SQLAlchemy 2.0 (Async)

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | ORM，把 Python 类和数据库表对应起来 |
| **如何使用** | `backend/app/models/` 下定义 `Base` + 模型类；`backend/app/core/database.py` 创建 engine 和 session |
| **关键代码** | `class Patient(Base): __tablename__ = "patients"` + `async with AsyncSession() as session:` |
| **新手学习重点** | `DeclarativeBase`、`Column` 类型定义、关系（`ForeignKey`/`relationship`）、异步 session 使用 |
| **官方文档** | https://docs.sqlalchemy.org/en/20/ |

### 6. Alembic

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 数据库版本迁移——模型变了，自动生成 SQL 更新数据库 |
| **如何使用** | `alembic revision --autogenerate -m "描述"` 生成迁移 → `alembic upgrade head` 执行 |
| **关键配置** | `backend/alembic/env.py`：关联 `Base.metadata` 和数据库 URL |
| **新手学习重点** | `alembic init`、`--autogenerate`、`upgrade/downgrade`、迁移文件结构 |
| **官方文档** | https://alembic.sqlalchemy.org/en/latest/ |

### 7. PostgreSQL + pgvector

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 主数据库，存储患者、病历、处方等结构化数据；pgvector 提供向量搜索能力（用于 RAG） |
| **如何使用** | Docker Compose 中 `image: pgvector/pgvector:pg17` 启动；SQLAlchemy 通过 asyncpg 驱动连接 |
| **新手学习重点** | PostgreSQL 基础（创建数据库/表/SQL）、`pgvector` 的向量列概念 |
| **官方文档** | https://www.postgresql.org/docs/ https://github.com/pgvector/pgvector |

### 8. Redis

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 缓存 + 工作记忆（Working Memory）+ 会话管理 + Agent 通信 |
| **如何使用** | `backend/app/core/redis.py`：`redis_client = aioredis.from_url(settings.redis_url)` |
| **新手学习重点** | 基础数据结构（String/Hash/List）、过期时间（TTL）、`asyncio` 客户端 |
| **官方文档** | https://redis.io/docs/latest/ |

---

## 二、容器化与部署

### 9. Docker & Docker Compose

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 一键启动所有服务（PostgreSQL + Redis + Qdrant + Backend），消除环境差异 |
| **如何使用** | `docker-compose.yml` 定义 4 个服务；`infrastructure/docker/Dockerfile.backend` 定义后端镜像 |
| **关键命令** | `docker-compose up --build` 即可启动完整环境 |
| **新手学习重点** | `Dockerfile` 指令（FROM/COPY/RUN/CMD）、`docker-compose.yml` 的 services/volumes/depends_on、healthcheck |
| **官方文档** | https://docs.docker.com/compose/ |

---

## 三、前端

### 10. Next.js 14

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | React 框架，提供前端页面和路由 |
| **如何使用** | `frontend/src/app/` 下用 App Router 定义页面；`next.config.js` 配置 API 代理 |
| **新手学习重点** | App Router（文件即路由）、`layout.tsx`、`page.tsx`、服务端/客户端组件 |
| **官方文档** | https://nextjs.org/docs |

### 11. React 18

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | UI 组件库，构建用户界面 |
| **如何使用** | `frontend/src/components/` 下划分了 chat/medical-record/ui 三个组件目录 |
| **新手学习重点** | 函数组件、Hooks（`useState`/`useEffect`）、Props 传递、组件组合 |
| **官方文档** | https://react.dev/ |

### 12. Tailwind CSS

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | CSS 框架，用 utility class 快速写样式 |
| **如何使用** | `tailwind.config.js` 已配置；直接在 JSX 中写 `className="flex items-center p-4"` |
| **新手学习重点** | Flexbox/Grid、间距（p/m）、颜色、响应式前缀（`sm:`/`md:`） |
| **官方文档** | https://tailwindcss.com/docs |

---

## 四、安全与认证（骨架）

### 13. python-jose + passlib

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | JWT 令牌生成/验证 + 密码哈希 |
| **如何使用** | `backend/app/core/auth.py`：`jwt.decode()` 验证 Token |
| **官方文档** | https://python-jose.readthedocs.io/ https://passlib.readthedocs.io/ |

---

## 五、项目级工具

### 14. pyproject.toml

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | Python 项目元数据 + 依赖声明 |
| **如何使用** | 定义了项目名 `medinexus`、Python 版本要求、所有 pip 依赖 |
| **官方文档** | https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ |

### 15. Makefile

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 常用命令一键执行 |
| **如何使用** | `make dev-backend` / `make db-upgrade` |
| **新手学习重点** | `.PHONY`、目标/依赖、Shell 命令组合 |
| **官方文档** | https://www.gnu.org/software/make/manual/ |

---

## 六、新手学习路线图（建议顺序）

如果你刚接触这些技术，建议按这个顺序学：

```
Week 1: Python 基础 → Git → 命令行
Week 2: FastAPI（看官方 Tutorial）→ Uvicorn → REST API 概念
Week 3: Pydantic → SQLAlchemy → PostgreSQL → Alembic
Week 4: Docker → Docker Compose
Week 5: React → Next.js → Tailwind CSS
Week 6: Redis → 缓存概念
Week 7: 回顾 + 动手改本项目代码
```

每个技术花 **1-2 天** 看官方文档的 "Getting Started" 章节就够了，不需要全部看完——用到什么学什么。

---

## 七、快速参考：本项目启动命令

```bash
# 后端开发
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 数据库迁移
cd backend && alembic upgrade head

# 前端开发
cd frontend && npm run dev

# 完整环境（Docker）
docker-compose up --build
```
