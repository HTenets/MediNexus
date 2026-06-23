# MediNexus 部署指南 — Vercel（前端）+ Render（后端）

> 零成本部署方案，所有服务均使用免费套餐。
> 仓库地址: `https://github.com/HTenets/MediNexus`

## 架构概览

```
用户 → Vercel (CDN) → Render (API + WebSocket) → Render PostgreSQL + Redis
          ↑                          ↑
     next.config.js 代理      render.yaml 编排
     /api/* → Render         Dockerfile.render
     wss:// → Render
```

## 前置条件

1. [GitHub](https://github.com) 账号 — 代码已推送至 `HTenets/MediNexus`
2. [Vercel](https://vercel.com) 账号 — 用 GitHub 登录
3. [Render](https://render.com) 账号 — 用 GitHub 登录

---

## 快速部署清单（约 10 分钟）

| # | 操作 | 平台 | 耗时 |
|---|------|------|------|
| 1 | 创建 PostgreSQL 数据库 | Render | 2-3 min |
| 2 | 创建 Redis 实例 | Render | 1-2 min |
| 3 | 创建 Web Service（后端 API） | Render | 3-5 min |
| 4 | 导入并部署前端 | Vercel | 1-2 min |
| 5 | 验证完整链路 | — | 1 min |

---

## 第1步：Render — 创建 PostgreSQL 数据库

> 部署地址: https://dashboard.render.com

1. 点击 **New +** → **PostgreSQL**
2. 填写以下配置：

| 字段 | 值 |
|------|-----|
| Name | `medinexus-db` |
| Database | `medinexus` |
| User | `medinexus` |
| Plan | **Free** |

3. 点击 **Create Database**
4. 等待创建完成（约 2-3 分钟）
5. **复制 Internal Connection String**，格式类似：
   ```
   postgresql://medinexus:xxx@dpg-xxx.render.com/medinexus
   ```

---

## 第2步：Render — 创建 Redis 实例

1. 点击 **New +** → **Redis**
2. 填写：

| 字段 | 值 |
|------|-----|
| Name | `medinexus-redis` |
| Plan | **Free** |

3. 点击 **Create Redis**
4. **复制 Internal Connection String**，格式类似：
   ```
   rediss://red-xxx.render.com:6379
   ```

---

## 第3步：Render — 创建 Web Service（后端 API）

### 方式一：Blueprint 一键部署（推荐）

1. 点击 **New +** → **Blueprint**
2. 连接 GitHub 仓库 `HTenets/MediNexus`
3. Render 自动读取 `render.yaml`，显示将创建的服务列表：
   - `medinexus-api` (Web Service)
   - `medinexus-db` (PostgreSQL)
   - `medinexus-redis` (Redis)
4. 点击 **Apply**
5. 等待部署完成（约 3-5 分钟）

### 方式二：手动创建（如果 Blueprint 失败）

1. 点击 **New +** → **Web Service**
2. 连接 GitHub 仓库 `HTenets/MediNexus`
3. 填写配置：

| 字段 | 值 |
|------|-----|
| Name | `medinexus-api` |
| Runtime | **Docker** |
| Dockerfile Path | `infrastructure/docker/Dockerfile.render` |
| Plan | **Free** |

4. 展开 **Advanced** → **Environment Variables**，添加：

| 变量 | 值 | 操作 |
|------|-----|------|
| `MEDINEXUS_DATABASE_URL` | 粘贴第1步复制的 PG 连接串 | 手动粘贴 |
| `MEDINEXUS_REDIS_URL` | 粘贴第2步复制的 Redis 连接串 | 手动粘贴 |
| `MEDINEXUS_JWT_SECRET` | — | 点击 **Generate** |
| `MEDINEXUS_DEMO_MODE` | `true` | 手动输入 |
| `PYTHONPATH` | `/app/backend` | 手动输入 |

5. 点击 **Create Web Service**

### 验证后端

构建完成后，访问：
```
https://medinexus-api.onrender.com/health
```

预期返回：
```json
{"status":"ok","mode":"demo","version":"0.1.0"}
```

> ⚠️ 免费套餐首次冷启动约 10-30 秒，之后响应正常。

---

## 第4步：Vercel — 部署前端

> 部署地址: https://vercel.com

1. 点击 **Add New...** → **Project**
2. 导入 GitHub 仓库 `HTenets/MediNexus`
3. 配置项目：

| 字段 | 值 | 说明 |
|------|-----|------|
| Framework Preset | **Next.js** | 自动识别 |
| Root Directory | **`frontend`** | ⚠️ 必须选择此项！ |
| Build Command | `npm run build` | 默认值 |
| Output Directory | `.next` | 默认值 |

4. 环境变量：**无需手动添加**（`vercel.json` 已配置 API 代理）
5. 点击 **Deploy**
6. 等待部署完成（约 1-2 分钟）

### 验证前端

访问 Vercel 分配的域名（格式 `medinexus-xxx.vercel.app`）：
- ✅ 首页正常显示
- ✅ 点击「AI 问诊」进入对话页面
- ✅ 输入症状，确认能收到 AI 回复

---

## 第5步：常见问题排查

### Q: WebSocket 连接失败？

检查 `frontend/src/lib/websocket.ts` 中的 `getWsBase()`：
- 生产环境默认连接 `wss://medinexus-api.onrender.com`
- 确保 Render Web Service 处于 **Live** 状态
- 首次请求需等待 10-30 秒（免费套餐冷启动）

### Q: Render 服务一直 Deploying？

- 检查 Docker build 日志：Dashboard → `medinexus-api` → **Events** → 点选最近的 Deploy
- 常见原因：`PYTHONPATH` 环境变量未设置
- 解决：在 **Environment** 中添加 `PYTHONPATH=/app/backend`，手动触发 **Deploy**

### Q: 如何更新代码？

```bash
git add .
git commit -m "feat: xxx"
git push
# Vercel 自动重新部署
# Render: Dashboard → medinexus-api → Manual Deploy → Deploy latest commit
```

### Q: Render 免费套餐的限制？

| 资源 | 限制 |
|------|------|
| Web Service | 每月 750 小时（全天运行够用） |
| PostgreSQL | 1GB 存储 |
| Redis | 25MB 内存 |
| 休眠策略 | 15 分钟无请求自动休眠 |
| 唤醒延迟 | 首次请求 10-30 秒 |

> 💡 可用 [UptimeRobot](https://uptimerobot.com) 每 14 分钟 ping `/health` 避免休眠

### Q: Vercel 免费套餐的限制？

| 资源 | 限制 |
|------|------|
| 带宽 | 100 GB/月 |
| 构建时间 | 6000 分钟/月 |

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `frontend/vercel.json` | Vercel 部署配置 + API 代理规则 |
| `frontend/.env.production` | 生产环境变量 |
| `frontend/next.config.js` | Next.js 配置（开发/生产环境感知代理） |
| `render.yaml` | Render Blueprint（一键部署模板） |
| `infrastructure/docker/Dockerfile.render` | Render 专用 Dockerfile |
| `backend/requirements.txt` | Python 依赖清单 |
| `backend/app/config.py` | 配置类（`demo_mode` 等环境变量注入） |
| `backend/app/core/database.py` | 数据库引擎（无 DB 时优雅降级） |
| `backend/app/main.py` | 入口（Demo/Production 模式切换 + CORS） |
| `backend/app/api/health.py` | 健康检查（返回 mode/version） |
| `frontend/src/lib/websocket.ts` | WebSocket 客户端（生产环境连接 Render） |
| `docs/deploy-vercel-render.md` | **本文档** |
