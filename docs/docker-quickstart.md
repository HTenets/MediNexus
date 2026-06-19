# Docker 零基础快速入门 — 在 MediNexus 中使用

> 如果你从未用过 Docker，本教程带你从零开始。
> 只需要跟着做，不需要理解全部原理。

---

## 一、什么是 Docker？

把 Docker 想象成一个**「一键启动虚拟电脑」**的工具。

传统方式：你需要手动安装 PostgreSQL、Redis、Qdrant 三个数据库。
Docker 方式：一个命令自动下载、启动所有服务。

```
传统: 下载PostgreSQL安装包 → 安装 → 配置 → 启动
Docker: docker compose up   ← 一条命令
```

**不需要理解的概念:** 镜像(image)、容器(container)、卷(volume)——先跳过，用起来再说。

---

## 二、安装 Docker Desktop

### 2.1 下载
1. 打开 https://www.docker.com/products/docker-desktop/
2. 点击 **Download for Windows**
3. 等待下载完成（约 500MB）

### 2.2 安装
1. 双击安装包 `Docker Desktop Installer.exe`
2. ✅ 勾选 **"Use WSL 2 instead of Hyper-V"** （如果你装了 WSL）
3. 一直点 **Next** → **Finish**
4. 安装完成后**重启电脑**

### 2.3 验证安装
重启后打开终端 (PowerShell)，输入:
```powershell
docker --version
# 应该输出: Docker version 27.x.x
```

---

## 三、启动 MediNexus 的数据库

### 3.1 打开终端
在 MediNexus 项目根目录打开终端（PowerShell）:
```powershell
cd E:\Program\MediNexus
```

### 3.2 启动数据库
```powershell
docker compose up postgres redis qdrant
```

第一次运行会**下载镜像**（约 1-2GB，取决于网络），后续启动秒开。

你会看到类似这样的输出:
```
[+] Running 3/3
 ✔ Container medinexus-postgres-1  Started
 ✔ Container medinexus-redis-1     Started
 ✔ Container medinexus-qdrant-1    Started
```

### 3.3 验证数据库
打开**新终端**，运行:
```powershell
docker ps
# 应该看到 3 个 Running 状态的容器:
# medinexus-postgres-1 (端口 5432)
# medinexus-redis-1    (端口 6379)
# medinexus-qdrant-1   (端口 6333)
```

---

## 四、常见问题

### Q: 端口被占用 (端口 5432 已被使用)
如果本地已安装 PostgreSQL，端口冲突:
```powershell
# 查看哪个程序占用了端口
netstat -ano | findstr :5432

# 然后停止本地 PostgreSQL 服务，或修改 docker-compose.yml 的外部端口
```

### Q: Docker Desktop 打不开
确保:
1. **WSL 2** 已启用（设置 → 应用 → 可选功能 → 更多 Windows 功能 → 勾选"适用于 Linux 的 Windows 子系统"）
2. **BIOS 虚拟化** 已开启（重启按 F2/Del 进 BIOS → 找 Intel VT-x / AMD-V → 启用）
3. **重启电脑** 后再试

### Q: 下载镜像太慢
配置国内镜像加速（Docker Desktop → Settings → Docker Engine → 添加）:
```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```
点 **Apply & Restart**。

### Q: 磁盘空间不足
```powershell
# 查看 Docker 占了多少空间
docker system df

# 清理未使用的镜像和容器（不影响数据）
docker system prune -a
```

---

## 五、日常使用命令速查

| 用途 | 命令 |
|------|------|
| 启动数据库 | `docker compose up postgres redis qdrant` |
| 启动全部（含后端） | `docker compose up --build` |
| 后台运行 | `docker compose up -d` |
| 查看运行中的容器 | `docker ps` |
| 查看日志 | `docker compose logs -f postgres` |
| 停止所有 | `docker compose down` |
| 停止并删除数据 | `docker compose down -v` |
| 查看资源占用 | `docker stats` |

---

## 六、完整启动流程 (每日开发)

### 步骤 1: 启动数据库
打开终端 1:
```powershell
cd E:\Program\MediNexus
docker compose up postgres redis qdrant
```
保持此终端开着（不要关）。

### 步骤 2: 启动后端
打开终端 2:
```powershell
conda activate medinexus
cd E:\Program\MediNexus\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
访问 http://localhost:8000/health 确认 ✅

### 步骤 3: 启动前端
打开终端 3:
```powershell
cd E:\Program\MediNexus\frontend
npm run dev
```
浏览器打开 http://localhost:3000 ✅

### 停止
按 `Ctrl+C` 依次停止前端、后端、数据库终端即可。
