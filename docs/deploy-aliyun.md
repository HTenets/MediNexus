# MediNexus 阿里云服务器部署文档

## 1. 服务器信息

| 项目 | 值 |
|------|-----|
| 阿里云实例ID | afb6b276a0774ff0a74dc56d84c9d1ae |
| 公网IP | 47.80.10.180 |
| 私有IP | 172.19.17.175 |
| 操作系统 | Ubuntu Server 22.04 LTS (推荐) |

## 2. 环境要求

### 2.1 硬件要求

| 资源 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核 |
| 内存 | 8GB | 16GB |
| 磁盘 | 40GB SSD | 80GB SSD |

### 2.2 软件要求

| 软件 | 版本 | 用途 |
|------|------|------|
| Docker | 24.0+ | 容器化部署 |
| Docker Compose | 2.0+ | 容器编排 |
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| PostgreSQL | 17+ (带pgvector) | 数据库 |
| Redis | 7+ | 缓存 |
| Qdrant | 最新版 | 向量数据库 |

## 3. 部署前准备

### 3.1 安全组配置

在阿里云控制台配置安全组规则：

| 端口 | 协议 | 来源 | 用途 |
|------|------|------|------|
| 22 | TCP | 0.0.0.0/0 | SSH连接 |
| 80 | TCP | 0.0.0.0/0 | HTTP访问 |
| 443 | TCP | 0.0.0.0/0 | HTTPS访问（可选，需配置域名和证书） |
| 5432 | TCP | 172.19.17.175/32 | PostgreSQL(内部) |
| 6379 | TCP | 172.19.17.175/32 | Redis(内部) |
| 6333 | TCP | 172.19.17.175/32 | Qdrant(内部) |

### 3.2 SSH密钥配置

将本地SSH公钥上传到服务器：

```bash
ssh-copy-id root@47.80.10.180
```

或者手动添加：

```bash
# 在服务器上执行
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCt/3/bc5VLV8N4rfikGmJyraswPww9wQYWYGsWzuTirimjt63KM1qzo88rZqbn6vzz5gy1FZgQGMYElZLL4a+eWsj/fYwKp6dHqeK5xmfr22C7ik6/JuMH7c4cG1GP7Me4+UwkF3Iaw/wY4kmDv7ov6ocaoS/ODspOIdkgc3qZAzU8PfRkuZOaFmrVgbCsdC4mU5lBN9QJopCm4s45S4DHs8GxY9BqtgSW9XaGsF+oPTHumpRn/A5qUvJVuUuVxBYfUnjgdj/JgJSNcBxLKn5Wv1F+R20Mw8fukfdELdjoeic7ZQQLQ4XXIqshx2kFWq+1nhAQEN/zoVdMFmpwIdt0ztelAN6DEcU1ZDGJxVcu33prM+4C71WiGM4eqy/8c1cIRQmPAtnJ0z6BRsLzsw4jzwenIzWqoeBSXwkbi9dM3azm6CPJwQyn6MqcXYdSEyP/2yRZmPzMza602EkLGgKCKroRd6rzvOga3rCxhFe0vwkgDKXy2OyhNiM7ZnU0OB8= huitao425@gmail.com" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 4. 服务器环境初始化

### 4.1 登录服务器

```bash
ssh root@47.80.10.180
```

### 4.2 执行初始化脚本

```bash
# 上传初始化脚本
scp scripts/deploy/init_server.sh root@47.80.10.180:/opt/

# 登录服务器执行
ssh root@47.80.10.180
chmod +x /opt/init_server.sh
/opt/init_server.sh
```

### 4.3 手动安装步骤（如果脚本执行失败）

```bash
# 更新系统
apt update -y && apt upgrade -y

# 安装依赖
apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common git wget unzip

# 安装Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 创建项目目录
mkdir -p /opt/program/medinexus_deploy/{logs,data/postgres,data/redis,data/qdrant}

# 配置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable
```

## 5. 部署项目

### 5.1 方式一：服务器直接克隆项目部署（推荐）

此方式适用于直接在服务器上克隆仓库进行部署。

#### 步骤1：克隆项目

```bash
# 在服务器上执行
cd /opt/program/medinexus_deploy
git clone https://github.com/HTenets/MediNexus.git MediNexus
cd MediNexus
```

#### 步骤2：配置环境变量

```bash
cp scripts/deploy/.env.production /opt/program/medinexus_deploy/MediNexus/.env
cp scripts/deploy/docker-compose.prod.yml /opt/program/medinexus_deploy/MediNexus/docker-compose.yml
cp scripts/deploy/nginx.conf infrastructure/nginx/nginx.conf
```

**编辑环境变量文件**：

```bash
vim /opt/program/medinexus_deploy/MediNexus/.env
```

修改以下关键配置：

```env
# 数据库密码（必须修改）
POSTGRES_PASSWORD=your_secure_postgres_password_here

# JWT密钥（必须修改）
MEDINEXUS_JWT_SECRET=your_very_secure_jwt_secret_here_must_be_long_and_random

# 允许的来源
MEDINEXUS_ALLOWED_ORIGINS=http://47.80.10.180

# 前端API地址
NEXT_PUBLIC_API_URL=http://47.80.10.180
```

**生成随机密码的方法**：

如果你不知道如何设置密码，可以使用以下命令自动生成随机密码：

```bash
# 生成数据库密码（16位随机字符串）
POSTGRES_PASSWORD=$(openssl rand -hex 16)
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"

# 生成JWT密钥（32位随机字符串）
JWT_SECRET=$(openssl rand -hex 32)
echo "MEDINEXUS_JWT_SECRET=$JWT_SECRET"
```

**一键生成并写入.env文件**（推荐）：

```bash
# 在服务器上执行，自动生成所有密码并写入.env文件
POSTGRES_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)

cat > /opt/program/medinexus_deploy/MediNexus/.env <<EOF
POSTGRES_DB=medinexus
POSTGRES_USER=medinexus
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MEDINEXUS_DATABASE_URL=postgresql+asyncpg://medinexus:$POSTGRES_PASSWORD@postgres:5432/medinexus
MEDINEXUS_REDIS_URL=redis://redis:6379/0
MEDINEXUS_QDRANT_URL=http://qdrant:6333
MEDINEXUS_JWT_SECRET=$JWT_SECRET
MEDINEXUS_DEMO_MODE=true
MEDINEXUS_ALLOWED_ORIGINS=http://47.80.10.180
MEDINEXUS_LLM_PROVIDER=ollama
MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434
NEXT_PUBLIC_API_URL=http://47.80.10.180
EOF

echo "✅ .env 文件已生成！"
```

> **注意**：
> - `POSTGRES_PASSWORD` 和 `MEDINEXUS_DATABASE_URL` 中的密码必须一致
> - JWT密钥建议至少32个字符，越长越安全
> - 请妥善保存这些密码，丢失后无法恢复

#### 步骤3：创建数据目录

```bash
mkdir -p /opt/program/medinexus_deploy/{logs,data/postgres,data/redis,data/qdrant}
chown -R $(whoami):$(whoami) /opt/program/medinexus_deploy
```

#### 步骤4：构建并启动服务

> **低配服务器（2核2G）注意**：不要用 `build --no-cache`（每层重编、反复触发内存峰值），且**必须串行构建**，否则 frontend 的 Next.js 构建会与其他镜像同时抢内存导致 OOM 卡死。完整命令与前置步骤见 [10.4 节](#104-2核2g-低配服务器构建与运行专项优化)。

```bash
cd /opt/program/medinexus_deploy/MediNexus
# 串行构建（推荐），不追加 --no-cache
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build --no-parallel
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d 
```

### 5.2 方式二：使用一键部署脚本

```bash
# 在本地项目目录执行
cd e:\Program\MediNexus

# 上传代码并部署
bash scripts/deploy/deploy.sh -f
```

**脚本参数说明**：

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息 |
| `-u, --upload` | 仅更新代码（git pull） |
| `-b, --build` | 仅构建镜像 |
| `-s, --start` | 仅启动服务 |
| `-d, --down` | 停止服务 |
| `-r, --restart` | 重启服务 |
| `-l, --logs` | 查看服务日志 |
| `-f, --full` | 完整部署流程 |
| `-c, --clean` | 清理旧容器和镜像 |

### 5.3 子路径部署说明（/programs/medinexus）

当前部署已支持将应用挂载到**子路径**访问：

- 访问地址：`http://htenets.top/programs/medinexus`（域名）或 `http://47.80.10.180/programs/medinexus`（IP）
- **子路径专用**：根路径（`htenets.top/`）不再提供服务，返回 404
- 前端使用 Next.js `basePath`，API（`/api/v1`）和 WebSocket（`/ws`）同样挂在子路径下，由 Nginx 剥离前缀后转发到后端

**关键配置说明**：

| 配置项 | 位置 | 说明 |
|--------|------|------|
| `NEXT_PUBLIC_BASE_PATH` | `scripts/deploy/.env.production` | 子路径前缀，默认 `/programs/medinexus`，修改后需重新构建 frontend 镜像 |
| Nginx 路由 | `infrastructure/nginx/nginx.conf`（HTTP）或 `scripts/deploy/nginx.conf`（HTTPS） | 子路径下的页面/API/WS 转发规则 |
| `MEDINEXUS_ALLOWED_ORIGINS` | `.env` | 已加入 `http(s)://htenets.top` |

**修改子路径名称**：如想改用其它路径（例如 `/programs/mx`），需要同时修改：

1. `scripts/deploy/.env.production` 中的 `NEXT_PUBLIC_BASE_PATH`
2. `infrastructure/nginx/nginx.conf`（或 `scripts/deploy/nginx.conf`）中所有 `/programs/medinexus` 的 location

**重新部署生效**：

```bash
# 在服务器上重新构建前端镜像和 nginx 镜像并重启
bash scripts/deploy/deploy.sh -b -r
# 或手动：
docker-compose build frontend nginx
docker-compose up -d
```

> **注意**：`NEXT_PUBLIC_BASE_PATH` 是构建时注入的，只改 `.env` 不重新构建 frontend 镜像不会生效。

## 6. SSL证书配置（可选）

> **注意**：当前部署默认使用HTTP协议。如需启用HTTPS，需要先注册域名并配置DNS解析。Let's Encrypt不支持为裸IP地址颁发证书。

### 6.1 使用Let's Encrypt（推荐）

1. **注册域名**：在域名注册商处注册域名（如 `medinexus.example.com`）
2. **配置DNS**：将域名A记录指向服务器公网IP `47.80.10.180`
3. **获取证书**：

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书（替换为你的域名）
certbot certonly --nginx -d medinexus.example.com

# 证书文件位置
# 完整链: /etc/letsencrypt/live/medinexus.example.com/fullchain.pem
# 私钥: /etc/letsencrypt/live/medinexus.example.com/privkey.pem

# 创建证书目录并复制证书
mkdir -p /opt/program/medinexus_deploy/certs
cp /etc/letsencrypt/live/medinexus.example.com/fullchain.pem /opt/program/medinexus_deploy/certs/
cp /etc/letsencrypt/live/medinexus.example.com/privkey.pem /opt/program/medinexus_deploy/certs/
```

4. **更新Nginx配置**：使用支持HTTPS的配置文件（参考 `scripts/deploy/nginx-ssl.conf`）

### 6.2 使用自签名证书（仅测试环境）

```bash
mkdir -p /opt/program/medinexus_deploy/certs
openssl req -x509 -newkey rsa:4096 -keyout /opt/program/medinexus_deploy/certs/privkey.pem \
    -out /opt/program/medinexus_deploy/certs/fullchain.pem -days 365 -nodes \
    -subj "/CN=47.80.10.180"
```

> **警告**：自签名证书在浏览器中会显示安全警告，不适合生产环境使用。

## 7. 服务管理

### 7.1 查看服务状态

```bash
# 在服务器上执行
cd /opt/program/medinexus_deploy/MediNexus
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml ps
```

### 7.2 查看日志

```bash
# 查看所有服务日志
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f

# 查看特定服务日志
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f backend
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f frontend
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f nginx
```

### 7.3 启动/停止/重启服务

```bash
# 启动服务
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d

# 停止服务
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml down

# 重启服务
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml restart

# 重启特定服务
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml restart backend
```

### 7.4 更新代码

```bash
# 在本地执行
bash scripts/deploy/deploy.sh -u -b -r
```

## 8. 健康检查

### 8.1 服务健康检查

```bash
# 检查后端服务
curl http://localhost:80/health

# 预期响应
{"status": "ok"}

# 检查API
curl http://localhost:80/api/v1/health

# 检查前端
curl http://localhost:80/
```

### 8.2 数据库连接检查

```bash
# 检查PostgreSQL
docker exec -it medinexus-postgres-1 pg_isready -U medinexus

# 检查Redis
docker exec -it medinexus-redis-1 redis-cli ping

# 检查Qdrant
curl http://localhost:6333/collections
```

## 9. 数据备份

### 9.1 备份PostgreSQL

```bash
docker exec medinexus-postgres-1 pg_dump -U medinexus medinexus > /opt/program/medinexus_deploy/backup/postgres_backup.sql
```

### 9.2 备份Redis

```bash
docker exec medinexus-redis-1 redis-cli SAVE
docker cp medinexus-redis-1:/data/dump.rdb /opt/program/medinexus_deploy/backup/
```

### 9.3 备份Qdrant

```bash
tar -czf /opt/program/medinexus_deploy/backup/qdrant_backup.tar.gz /opt/program/medinexus_deploy/data/qdrant
```

### 9.4 自动化备份脚本

```bash
#!/bin/bash
BACKUP_DIR="/opt/program/medinexus_deploy/backup"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec medinexus-postgres-1 pg_dump -U medinexus medinexus > $BACKUP_DIR/postgres_$DATE.sql
docker exec medinexus-redis-1 redis-cli SAVE
docker cp medinexus-redis-1:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb
tar -czf $BACKUP_DIR/qdrant_$DATE.tar.gz /opt/program/medinexus_deploy/data/qdrant

find $BACKUP_DIR -type f -mtime +7 -delete
```

## 10. 性能优化

### 10.1 Docker资源限制

在 `docker-compose.yml` 中为每个服务配置。本项目默认按 **2核2G 低配服务器** 调优（已写入 `docker-compose.yml`）：

```yaml
# 单个服务示例：硬上限 512M，允许额外 256M swap 兜底
mem_limit: 512m
memswap_limit: 768m
```

> `memswap_limit` 必须为 `mem_limit` 之上（含 swap 的总上限），否则容器无法使用 swap。
> 若服务器已配置 swap（强烈建议，见 10.4），容器在瞬时内存尖峰时不会被 OOM kill。

**各服务默认资源限制（适配 2核2G）**：

| 服务 | mem_limit（硬上限） | memswap_limit（含swap上限） |
|------|---------|---------|
| postgres | 512M | 768M |
| redis | 128M | 256M |
| qdrant | 512M | 768M |
| backend | 512M | 768M |
| worker | 384M | 512M |
| frontend | 512M | 1024M |
| nginx | 128M | 256M |

> **注意**：以上为 2核2G 默认配置。若服务器内存 ≥8GB，可自行上调（如 qdrant 调到 4G、backend 调到 2G）。调整时务必保证各服务 `mem_limit` 之和不超过「物理内存 + swap」，否则运行时会 OOM。

### 10.2 Nginx优化

```nginx
# 增加worker进程数
worker_processes auto;

# 增加连接数
events {
    worker_connections 4096;
    multi_accept on;
}

# 启用Gzip压缩
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript;

# 客户端超时设置
client_max_body_size 100m;
proxy_read_timeout 120s;
```

### 10.3 PostgreSQL优化

在 `docker-compose.yml` 中添加环境变量：

```yaml
POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
```

### 10.4 2核2G 低配服务器构建与运行专项优化

在 2核2G 实例上，`docker-compose build`（尤其 frontend 的 Next.js 构建）极易因内存不足被 OOM kill，表现为**构建卡死或进程消失**。请按以下顺序操作，全部在服务器上执行。

#### 1) 先配置 swap 给内存兜底（最关键）

2G 实例默认通常无 swap，OOM 时直接杀进程。建一个 2G swap：

```bash
# 在服务器上执行
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h   # 确认 Swap 行已显示 2.0Gi
```

#### 2) 降低前端构建内存上限（已写入 Dockerfile，无需手动改）

`infrastructure/docker/Dockerfile.frontend` 已将 `NODE_OPTIONS` 限制为：

```dockerfile
ENV NODE_OPTIONS=--max-old-space-size=1024 --max-semi-space-size=32
```

> 原值 2048 在 2G 机器上等于让 Node 独占全部内存，必然 OOM。若已配置 swap，此值可上调到 1280~1536；未配置 swap 时保持 1024。

#### 3) 串行构建，禁止并行全量构建

`docker-compose build` 默认**并行**构建 backend/worker/frontend/nginx，内存峰值叠加必爆。改为串行：

```bash
cd /opt/program/medinexus_deploy/MediNexus

# 方式A：compose 串行构建（推荐）
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build --no-parallel

# 方式B：手动逐个构建（最稳妥，任何时刻只有一个构建在跑）
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build backend
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build worker
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build frontend
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build nginx
```

#### 4) 不要用 `--no-cache`

`--no-cache` 强制每层重编，既慢又反复触发内存峰值。依赖没变时直接 build 复用缓存即可：

```bash
# 推荐（不用 --no-cache）
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build --no-parallel

# 仅当依赖（pyproject.toml / package.json）确实变化时才加 --no-cache，且仍需串行
```

#### 5) 构建前先停掉残留容器、清理中间层

若之前 `up` 过，残留容器会占用内存。构建前释放：

```bash
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml down
docker system prune -f   # 清掉无用中间层与悬空镜像，释放磁盘/内存压力
```

#### 6) （可选）关闭 BuildKit 进一步降内存

新版 BuildKit 构建器内存占用更高，2G 机器可改用旧 builder：

```bash
DOCKER_BUILDKIT=0 docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml build --no-parallel
```

#### 7) 启动服务

构建成功后启动。运行时各服务已通过 `docker-compose.yml` 的 `mem_limit` 限制内存（见 10.1），不会被单个容器拖垮整机：

```bash
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml up -d
```

> **结论**：2G 为最低可行配置，仅适合 demo。生产/稳定使用请按第 2.1 节升级到 4核8G 及以上。

## 11. 故障排查

### 11.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 服务无法启动 | 端口被占用 | 检查端口占用：`netstat -tlnp` |
| 数据库连接失败 | 密码错误 | 检查 `.env` 文件中的数据库密码 |
| 前端无法访问API | CORS配置错误 | 检查 `MEDINEXUS_ALLOWED_ORIGINS` |
| 内存不足 / 构建卡死 | 2G低配服务器 OOM（并行构建、无swap、--no-cache） | 见 [10.4 节](#104-2核2g-低配服务器构建与运行专项优化)：配 swap、串行构建、去 --no-cache；并确认 `Dockerfile.frontend` 的 `NODE_OPTIONS=--max-old-space-size=1024` |
| 镜像构建失败 | 网络问题 | 配置Docker镜像加速器 |

### 11.2 查看详细日志

```bash
# 查看所有服务日志
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs

# 查看最近100行日志
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs --tail=100

# 实时查看日志
docker-compose -f /opt/program/medinexus_deploy/MediNexus/docker-compose.yml logs -f
```

### 11.3 Docker镜像加速器

```bash
cat > /etc/docker/daemon.json <<EOF
{
    "registry-mirrors": ["https://docker.m.daocloud.io", "https://hub-mirror.c.163.com"]
}
EOF

systemctl daemon-reload
systemctl restart docker
```

## 12. 目录结构

```
/opt/program/medinexus_deploy/
├── MediNexus/                 # 项目代码
│   ├── backend/               # 后端代码
│   ├── frontend/              # 前端代码
│   ├── infrastructure/        # 基础设施配置
│   ├── scripts/               # 脚本文件
│   └── ...
├── data/                      # 数据目录
│   ├── postgres/              # PostgreSQL数据
│   ├── redis/                 # Redis数据
│   └── qdrant/                # Qdrant数据
├── logs/                      # 日志目录
│   └── nginx/                 # Nginx日志
├── certs/                     # SSL证书
├── backup/                    # 备份文件
├── docker-compose.yml         # Docker Compose配置
└── .env                       # 环境变量
```

## 13. 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://htenets.top/programs/medinexus 或 http://47.80.10.180/programs/medinexus |
| API文档 | http://htenets.top/programs/medinexus/api/v1/docs |
| 健康检查 | http://htenets.top/programs/medinexus/health |
| PostgreSQL | localhost:5432 (内部) |
| Redis | localhost:6379 (内部) |
| Qdrant | localhost:6333 (内部) |

> 应用部署在子路径 `/programs/medinexus` 下，根路径（`htenets.top/`）返回 404。

## 14. 安全建议

1. **修改默认密码**：修改 `.env` 文件中的所有密码
2. **启用HTTPS**：配置SSL证书
3. **限制访问**：配置安全组只允许必要的端口
4. **定期备份**：配置自动备份脚本
5. **更新系统**：定期执行 `apt update && apt upgrade`
6. **监控日志**：定期检查服务日志
7. **禁用root远程登录**：创建普通用户进行日常操作