# MediNexus 部署指南

> 多个免费部署方案可选，全部无需绑定信用卡。
> 仓库地址: `https://github.com/HTenets/MediNexus`

## 架构概览

```
用户 → Vercel (CDN) → 后端 API (可选多个平台) → 数据库 (可选多个平台)
          ↑
     next.config.js 代理 /api/* → 后端
     WebSocket 直连 wss://后端
```

## 部署方案选择

| 方案 | 前端 | 后端 | 数据库 | 绑卡 | 适合 |
|------|------|------|--------|------|------|
| 🥇 **方案A** | Vercel | **Zeabur** | Zeabur PG + Redis | ❌ 不需要 | **推荐，国产团队，最省心** |
| 🥈 方案B | Vercel | **Koyeb** | Koyeb + 外部 | ❌ 不需要 | 国际方案，流程成熟 |
| 🥉 方案C | Vercel | **Render** | Render PG + Redis | ✅ 需要 | 原方案，保留参考 |
| 🆓 方案D | Vercel | **Zeabur 纯Demo** | 无（内存模式） | ❌ 不需要 | 快速体验，重启丢失 |
| ☁️ 方案E | **自部署** | **阿里云ECS** | 自建 PG + Redis + Qdrant | ✅ 需要 | 完全掌控，性能最佳 |

---

## 🥇 方案A（推荐）：Vercel + Zeabur

> [Zeabur](https://zeabur.com) 是中国团队开发的部署平台，支持微信/支付宝，免费套餐无需绑卡。

### 前置条件

1. [GitHub](https://github.com) 账号
2. [Vercel](https://vercel.com) 账号 — 用 GitHub 登录
3. [Zeabur](https://zeabur.com) 账号 — 用 GitHub 登录，**无需绑卡**

---

### A1. Zeabur 创建后端服务

1. 登录 [Zeabur Dashboard](https://dashboard.zeabur.com)
2. 点击 **创建项目** → 输入名称 `medinexus`
3. 点击 **创建服务** → **从 GitHub 导入**
4. 选择仓库 `HTenets/MediNexus`
5. Zeabur 自动识别项目类型，配置如下：

| 字段 | 值 |
|------|-----|
| 语言/框架 | **Dockerfile** |
| Dockerfile 路径 | `infrastructure/docker/Dockerfile.render` |
| 端口 | `8000` |

6. 展开 **高级设置** → **环境变量**，添加：

| 变量 | 值 |
|------|-----|
| `MEDINEXUS_DEMO_MODE` | `true` |
| `MEDINEXUS_JWT_SECRET` | 随便填一个复杂字符串 |
| `PYTHONPATH` | `/app/backend` |

7. 点击 **部署**

> ⏱ 首次构建约 3-5 分钟。完成后会显示 `https://medinexus.zeabur.app` 之类的域名

### A2. Zeabur 添加数据库（可选）

在 Zeabur 项目内：

1. 点击 **新建服务** → **数据库** → **PostgreSQL**
2. 选择 **Free** 套餐
3. 创建后，复制连接串（Internal Connection String）
4. 回到 medinexus 服务 → **环境变量** → 添加 `MEDINEXUS_DATABASE_URL` = 粘贴连接串
5. 重新部署

Redis 同理：新建服务 → **数据库** → **Redis**

### A3. 配置自定义域名

Zeabur 免费版提供 `xxx.zeabur.app` 子域名，也可以绑定自己的域名：
- 服务 → **网络** → **域名** → 添加你的域名

---

## 🥈 方案B：Vercel + Koyeb

> [Koyeb](https://www.koyeb.com) 国际平台，免费套餐无需绑卡，支持 Docker 部署。

### 步骤

1. 登录 [Koyeb](https://app.koyeb.com)（GitHub 登录）
2. 点击 **Create App**
3. 选择 **Docker** → 输入以下配置：

| 字段 | 值 |
|------|-----|
| Dockerfile Path | `infrastructure/docker/Dockerfile.render` |
| Port | `8000` |

4. 添加环境变量：

| 变量 | 值 |
|------|-----|
| `MEDINEXUS_DEMO_MODE` | `true` |
| `MEDINEXUS_JWT_SECRET` | 随机字符串 |
| `PYTHONPATH` | `/app/backend` |

5. 点击 **Deploy**

> 免费额度：1 个 Web Service，1GB RAM，每月 5.5 美元等值额度，够用。

---

## 🆓 方案D：纯 Demo 模式（最快体验）

不需要任何数据库，所有数据存内存，重启丢失。适合快速演示。

### 步骤

1. **Zeabur** 创建服务，选择 Dockerfile，添加环境变量 `MEDINEXUS_DEMO_MODE=true`
2. **Vercel** 部署前端，Root Directory 选 `frontend`
3. 修改 `frontend/next.config.js` 中的代理地址为 Zeabur 分配的域名

```js
// next.config.js — 修改 destination 为你的 Zeabur 域名
destination: process.env.NODE_ENV === "production"
  ? "https://medinexus.zeabur.app/api/v1/:path*"
  : "http://localhost:8000/api/v1/:path*",
```

---

## 前端部署（所有方案通用）

> 部署地址: https://vercel.com

1. 点击 **Add New...** → **Project**
2. 导入 GitHub 仓库 `HTenets/MediNexus`
3. 配置：

| 字段 | 值 | 说明 |
|------|-----|------|
| Framework Preset | **Next.js** | 自动识别 |
| Root Directory | **`frontend`** | ⚠️ 必须选此项！ |
| Build Command | `npm run build` | 默认 |
| Output Directory | `.next` | 默认 |

4. 点击 **Deploy**

---

## 验证部署

访问 Vercel 分配的域名：
- ✅ 首页正常显示
- ✅ 点击「AI 问诊」进入对话
- ✅ 访问 `https://你的后端域名/health` 返回 `{"status":"ok","mode":"demo","version":"0.1.0"}`

---

## 常见问题

### Q: WebSocket 连接不上？

检查 `frontend/src/lib/websocket.ts` 中的 `getWsBase()`：
- 生产环境默认连接 `wss://medinexus-api.onrender.com`
- 如果你用的是 Zeabur 或 Koyeb，**需要修改这里的地址**为你的后端域名

修改 `frontend/src/lib/websocket.ts` 第 20 行附近：
```typescript
// 改成你的后端域名
return "wss://medinexus.zeabur.app";  // Zeabur 示例
```

### Q: Zeabur 免费额度够用吗？

| 资源 | 免费额度 |
|------|---------|
| Web Service | 1 个免费服务 |
| 构建时间 | 每月 1000 分钟 |
| PostgreSQL | 1 个免费实例（256MB） |
| Redis | 1 个免费实例 |
| 域名 | `*.zeabur.app` 免费子域名 |
| 绑卡 | ❌ 不需要（免费套餐） |

> 流量不大的个人项目完全够用。如果不够，升级 Dev 套餐 $5/月。

### Q: Zeabur 中国访问速度快吗？

Zeabur 默认部署在美西节点，但中国用户访问速度优于 Render。付费版可选择**北京/上海节点**。

### Q: 如何更新代码？

```bash
git add .
git commit -m "feat: xxx"
git push
# Vercel 自动重新部署
# Zeabur: Dashboard → 服务 → Manual Deploy → Redeploy
```

### Q: 如何查看日志？

- **Vercel**: Dashboard → Deployments → 点选 → Function Logs
- **Zeabur**: Dashboard → 服务 → **日志** 标签

---

## 原方案参考：Render（需绑卡）

> 如果以上方案都不满足，Render 仍然可用，但需要绑定信用卡（即使选 Free 套餐）。
> 操作步骤保留在下方供参考。

### Render 创建 PostgreSQL

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 **New +** → **PostgreSQL**
3. Name: `medinexus-db` / Database: `medinexus` / User: `medinexus` / Plan: **Free**
4. 创建后复制 Internal Connection String

### Render 创建 Redis

点击 **New +** → **Redis** → Name: `medinexus-redis` / Plan: **Free**

### Render 创建 Web Service

点击 **New +** → **Web Service** → 连接 GitHub 仓库 → 配置：

| 字段 | 值 |
|------|-----|
| Name | `medinexus-api` |
| Runtime | **Docker** |
| Dockerfile Path | `infrastructure/docker/Dockerfile.render` |
| Plan | **Free** |

环境变量：

| 变量 | 值 |
|------|-----|
| `MEDINEXUS_DATABASE_URL` | PG 连接串 |
| `MEDINEXUS_REDIS_URL` | Redis 连接串 |
| `MEDINEXUS_JWT_SECRET` | Generate |
| `MEDINEXUS_DEMO_MODE` | `true` |
| `PYTHONPATH` | `/app/backend` |

---

## ☁️ 方案E：阿里云轻量服务器自部署

> 适合希望完全掌控服务器、追求最佳性能的用户。需绑定支付宝/信用卡。

### 前置条件

1. [阿里云](https://www.aliyun.com) 账号
2. 轻量应用服务器实例（推荐配置见下方）
3. 域名（可选，用于自定义访问地址）

### E1. 服务器配置选择

| 配置 | CPU | 内存 | 带宽 | 价格/月 | 适合 |
|------|-----|------|------|---------|------|
| ⚠️ 最小 | 2核 | 4GB | 3Mbps | ~50元 | Demo 测试，勉强运行 |
| ✅ 推荐 | 2核 | 8GB | 5Mbps | ~80元 | 生产环境，流畅运行 |
| 🚀 最佳 | 4核 | 8GB | 10Mbps | ~150元 | 高并发场景 |

> **内存要求说明**：Qdrant（向量数据库）+ PostgreSQL（pgvector）+ Redis + 后端 + 前端 + Nginx，5个容器同时运行，4GB 会非常紧张，建议至少 8GB。

### E2. 应用镜像选择

| 选项 | 说明 | 推荐度 |
|------|------|--------|
| **Docker 镜像** | 预装 Docker 和 Docker Compose，开箱即用 | ⭐⭐⭐⭐⭐ |
| **OpenCloudOS** | 基础 Linux 系统，需手动安装 Docker | ⭐⭐⭐ |

**强烈推荐选择 Docker 镜像**，因为项目本身就是容器化架构，使用官方 Docker 镜像可以节省大量配置时间。

### E3. 创建轻量应用服务器

1. 登录 [阿里云控制台](https://ecs.console.aliyun.com)
2. 点击 **轻量应用服务器** → **创建实例**
3. 配置：

| 配置项 | 值 |
|--------|-----|
| 地域 | 选择靠近你的用户的地域（如华东1、华北2） |
| 可用区 | 默认即可 |
| 镜像 | **应用镜像** → **Docker**（版本选最新） |
| 套餐 | 2核8GB/5Mbps（推荐） |
| 系统盘 | 默认 40GB SSD |
| 购买时长 | 按需选择 |
| 实例名称 | `medinexus-server` |

4. 点击 **立即购买** → 完成支付

### E4. 安全组配置

在实例详情页 → **安全** → **防火墙**，添加以下规则：

| 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|
| TCP | 80 | 0.0.0.0/0 | HTTP 访问 |
| TCP | 443 | 0.0.0.0/0 | HTTPS 访问（后续配置） |
| TCP | 22 | 0.0.0.0/0 | SSH 登录 |
| TCP | 5432 | 127.0.0.1/32 | PostgreSQL（仅本地访问） |
| TCP | 6379 | 127.0.0.1/32 | Redis（仅本地访问） |
| TCP | 6333 | 127.0.0.1/32 | Qdrant（仅本地访问） |

> 数据库端口不要对外暴露，通过 Docker 网络内部访问即可。

### E5. 登录服务器

```bash
ssh root@你的服务器公网IP
```

密码在实例详情页 → **重置密码** 获取。

### E6. 安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 git
apt install -y git

# 确认 Docker 和 Docker Compose 已安装
docker --version
docker compose version
```

> 如果 Docker 未安装：`curl -fsSL https://get.docker.com | sh`

### E7. 克隆代码

```bash
cd /opt/program/medinexus_deploy
git clone https://github.com/HTenets/MediNexus.git MediNexus
cd MediNexus
```

### E8. 配置环境变量

```bash
cp .env.docker /opt/program/medinexus_deploy/MediNexus/.env
vi /opt/program/medinexus_deploy/MediNexus/.env
```

修改以下配置：

```bash
POSTGRES_PASSWORD=your-strong-db-password-here
MEDINEXUS_JWT_SECRET=your-very-long-and-secure-jwt-secret-here
MEDINEXUS_DEMO_MODE=false
MEDINEXUS_ALLOWED_ORIGINS=http://你的服务器IP:80,http://你的域名.com
NEXT_PUBLIC_API_URL=http://你的服务器IP:80
```

> 生成安全密钥：`openssl rand -hex 32`

### E9. 启动服务

```bash
# 后台启动所有服务
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d
```

> ⏱ 首次构建约 5-10 分钟，取决于服务器带宽和配置。

查看服务状态：

```bash
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml ps
```

### E10. 验证部署

访问 `http://你的服务器公网IP`：
- ✅ 首页正常显示
- ✅ 点击「AI 问诊」进入对话
- ✅ 访问 `http://你的服务器公网IP/health` 返回 `{"status":"ok"}`

查看日志：

```bash
# 查看所有服务日志
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs

# 查看特定服务日志（如 backend）
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs backend -f
```

### E11. 配置 HTTPS（可选但推荐）

安装 Certbot 和 Nginx 插件：

```bash
apt install -y certbot python3-certbot-nginx
```

配置 Nginx 支持 HTTPS：

```bash
# 停止服务
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml down

# 修改 infrastructure/nginx/nginx.conf，添加 HTTPS 配置
vi infrastructure/nginx/nginx.conf
```

获取 SSL 证书：

```bash
certbot certonly --standalone -d your-domain.com
```

更新 Nginx 配置，将证书路径填入配置文件，然后重启服务：

```bash
docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d
```

### E12. 数据持久化

Docker Compose 已配置数据卷：
- `pgdata`：PostgreSQL 数据
- `qdrant_data`：Qdrant 向量数据

数据卷默认存储在 `/var/lib/docker/volumes/`，会在服务器重启后保留。

### E13. 自动更新

推荐配置 Watchtower 自动更新 Docker 镜像：

```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --schedule "0 0 4 * * *" \
  --cleanup
```

### E14. 监控和维护

| 操作 | 命令 |
|------|------|
| 查看容器状态 | `docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml ps` |
| 查看日志 | `docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f` |
| 重启服务 | `docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml restart` |
| 更新代码 | `cd /opt/program/medinexus_deploy/MediNexus && git pull && docker compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d --build` |
| 清理未使用资源 | `docker system prune -a` |

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `docker-compose.yml` | Docker Compose 编排（包含全部服务） |
| `.env.docker` | 生产环境环境变量模板 |
| `infrastructure/nginx/nginx.conf` | Nginx 反向代理配置 |
| `infrastructure/nginx/Dockerfile` | Nginx 镜像构建文件 |
| `infrastructure/docker/Dockerfile.backend` | 后端 API 镜像 |
| `infrastructure/docker/Dockerfile.frontend` | 前端 Next.js 镜像 |
| `infrastructure/docker/Dockerfile.render` | 后端 Docker 镜像（Zeabur/Render/Koyeb 通用） |
| `frontend/vercel.json` | Vercel 部署配置 + API 代理规则 |
| `frontend/next.config.js` | Next.js 配置（支持环境变量 API 地址） |
| `render.yaml` | Render Blueprint（已废弃，仅保留参考） |
| `backend/requirements.txt` | Python 依赖清单 |
| `backend/app/config.py` | 配置类（支持 `allowed_origins` 环境变量） |
| `backend/app/core/database.py` | 数据库引擎（无 DB 时优雅降级） |
| `backend/app/main.py` | 入口（支持环境变量 CORS 白名单） |
| `backend/app/api/health.py` | 健康检查（返回 mode/version） |
| `frontend/src/lib/websocket.ts` | WebSocket 客户端（需按实际后端地址修改） |
| `docs/deploy-vercel-render.md` | **本文档** |