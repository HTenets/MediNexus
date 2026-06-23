# MediNexus 部署指南 — Vercel（前端）+ Render（后端）

> 零成本部署方案，所有服务均使用免费套餐。

## 架构概览

```
用户 → Vercel (CDN) → Render (API + WebSocket) → Render PostgreSQL + Redis
          ↑                          ↑
     next.config.js 代理      render.yaml 编排
     /api/* → Render         Dockerfile.render
     wss:// → Render
```

## 前置条件

1. [GitHub](https://github.com) 账号 — 代码托管
2. [Vercel](https://vercel.com) 账号 — 前端部署（用 GitHub 登录）
3. [Render](https://render.com) 账号 — 后端部署（用 GitHub 登录）

---

## 第1步：推送到 GitHub

```bash
# 在项目根目录
git init  # 如果尚未初始化
git add .
git commit -m "feat: 初始化 MediNexus 项目，含 Vercel + Render 部署配置"

# 在 GitHub 创建仓库后（不要加 README/.gitignore）
git remote add origin https://github.com/<你的用户名>/medinexus.git
git branch -M main
git push -u origin main
```

---

## 第2步：在 Render 部署后端

### 2.1 创建 PostgreSQL 数据库

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 **New +** → **PostgreSQL**
3. 配置：
   - **Name**: `medinexus-db`
   - **Database**: `medinexus`
   - **User**: `medinexus`
   - **Plan**: **Free**
4. 点击 **Create Database**（等待创建完成，约 2-3 分钟）
5. 创建后，**复制 Internal Connection String** — 下一步要用

### 2.2 创建 Redis 实例

1. 点击 **New +** → **Redis**
2. 配置：
   - **Name**: `medinexus-redis`
   - **Plan**: **Free**
3. 点击 **Create Redis**
4. 创建后，**复制 Internal Connection String**

### 2.3 创建 Web Service（后端 API）

**方法 A：使用 render.yaml（一键部署）**

1. 在 Render Dashboard 点击 **New +** → **Blueprint**
2. 连接你的 GitHub 仓库
3. Render 会自动读取 `render.yaml` 并创建所有服务
4. 点击 **Apply**

**方法 B：手动创建**

1. 点击 **New +** → **Web Service**
2. 连接你的 GitHub 仓库
3. 配置：
   - **Name**: `medinexus-api`
   - **Runtime**: **Docker**
   - **Dockerfile Path**: `infrastructure/docker/Dockerfile.render`
   - **Plan**: **Free**
4. 设置环境变量（**必须**）：

| 变量 | 值 |
|------|-----|
| `MEDINEXUS_DATABASE_URL` | 粘贴 PostgreSQL Internal Connection String |
| `MEDINEXUS_REDIS_URL` | 粘贴 Redis Internal Connection String |
| `MEDINEXUS_JWT_SECRET` | 点击 **Generate** |
| `MEDINEXUS_DEMO_MODE` | `true`（首次启动建议开启） |
| `PYTHONPATH` | `/app/backend` |

5. 点击 **Create Web Service**

> ⏱ 首次构建约需 3-5 分钟。完成后会显示 `https://medinexus-api.onrender.com`

### 2.4 验证后端

```bash
# 测试健康检查
curl https://medinexus-api.onrender.com/health
# 应返回: {"status":"ok","mode":"demo","version":"0.1.0"}

# 测试 API
curl -X POST https://medinexus-api.onrender.com/api/v1/consult \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"头痛两天"}'
# 应返回 session_id
```

---

## 第3步：在 Vercel 部署前端

### 3.1 部署

1. 登录 [Vercel Dashboard](https://vercel.com)
2. 点击 **Add New...** → **Project**
3. 导入你的 GitHub 仓库
4. 配置：
   - **Framework Preset**: **Next.js**
   - **Root Directory**: `frontend`（**重要！**）
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. 环境变量（无需手动设置，`vercel.json` 已配置代理）
6. 点击 **Deploy**

### 3.2 配置自定义域名（可选）

1. 在 Vercel 项目 → **Settings** → **Domains**
2. 添加你的域名（如 `medinexus.example.com`）
3. 按照 Vercel 提示配置 DNS

### 3.3 验证前端

访问 `https://medinexus.vercel.app`（或 Vercel 分配的域名）
- 首页应正常显示
- 点击「AI 问诊」进入对话页
- 输入症状，确认 WebSocket 连接正常

---

## 第4步：启动生产模式（可选）

### 4.1 关闭 Demo 模式

1. 在 Render Dashboard → `medinexus-api` → **Environment**
2. 将 `MEDINEXUS_DEMO_MODE` 改为 `false`
3. 点击 **Deploy** 重新部署

### 4.2 首次数据库迁移

```bash
# 在 Render 的 Shell 中执行（或者本地连远程 DB）
alembic upgrade head
```

---

## 常见问题

### Q: Render 免费套餐的限制？

| 资源 | 限制 |
|------|------|
| Web Service | 每月 750 小时（≈ 全天运行） |
| PostgreSQL | 1GB 存储，自动休眠 |
| Redis | 25MB 内存 |
| 休眠策略 | Web Service 15 分钟无请求自动休眠 |
| 唤醒延迟 | 首次请求需等待 10-30 秒 |

> 💡 **避免休眠**：可以设置 [UptimeRobot](https://uptimerobot.com) 每 14 分钟 ping 一次 `/health`

### Q: Vercel 免费套餐的限制？

| 资源 | 限制 |
|------|------|
| 带宽 | 100 GB/月 |
| 构建时间 | 6000 分钟/月 |
| Serverless 函数 | 无（本项目纯静态 + 代理） |

### Q: WebSocket 连接失败？

检查 `frontend/src/lib/websocket.ts` 中的 `getWsBase()`：
- 生产环境默认连接 `wss://medinexus-api.onrender.com`
- 确保 Render 服务已运行
- 首次请求可能需要等待 10-30 秒（免费套餐冷启动）

### Q: 如何更新代码？

```bash
# 本地修改后
git add .
git commit -m "feat: xxx"
git push

# Vercel 和 Render 会自动重新部署
# Render 需要在 Dashboard 手动触发 Deploy
```

### Q: 如何查看日志？

- **Vercel**: Dashboard → Project → **Deployments** → 点选 → **Function Logs**
- **Render**: Dashboard → `medinexus-api` → **Logs**

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `frontend/vercel.json` | Vercel 部署配置 + API 代理 |
| `frontend/.env.production` | 生产环境变量 |
| `frontend/next.config.js` | Next.js 配置（含环境感知代理） |
| `render.yaml` | Render Blueprint（一键部署配置） |
| `infrastructure/docker/Dockerfile.render` | Render 专用 Dockerfile |
| `backend/requirements.txt` | Python 依赖清单 |
| `backend/app/config.py` | 配置类（支持环境变量注入） |
| `backend/app/core/database.py` | 数据库（支持 Demo 模式） |
| `docs/deploy-vercel-render.md` | **本文档** |
