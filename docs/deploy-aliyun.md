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
mkdir -p /opt/medinexus/{logs,data/postgres,data/redis,data/qdrant}

# 配置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable
```

## 5. 部署项目

### 5.1 方式一：使用部署脚本（推荐）

```bash
# 在本地项目目录执行
cd e:\Program\MediNexus

# 上传代码并部署
bash scripts/deploy/deploy.sh -f
```

### 5.2 方式二：手动部署

#### 步骤1：打包并上传代码

```bash
# 在本地执行
cd e:\Program\MediNexus
tar --exclude='node_modules' --exclude='.git' --exclude='*.pyc' \
    --exclude='__pycache__' --exclude='*.log' --exclude='.env' \
    -czf medinexus-deploy.tar.gz .

scp medinexus-deploy.tar.gz root@47.80.10.180:/opt/medinexus/
```

#### 步骤2：解压代码

```bash
# 在服务器上执行
ssh root@47.80.10.180
cd /opt/medinexus
rm -rf deploy && mkdir -p deploy
tar -xzf medinexus-deploy.tar.gz -C deploy --strip-components=1
```

#### 步骤3：配置环境变量

```bash
cp /opt/medinexus/deploy/scripts/deploy/.env.production /opt/medinexus/.env
cp /opt/medinexus/deploy/scripts/deploy/docker-compose.prod.yml /opt/medinexus/docker-compose.yml
```

**编辑环境变量文件**：

```bash
vim /opt/medinexus/.env
```

修改以下关键配置：

```env
# 数据库密码（必须修改）
POSTGRES_PASSWORD=your_secure_postgres_password_here

# JWT密钥（必须修改）
MEDINEXUS_JWT_SECRET=your_very_secure_jwt_secret_here_must_be_long_and_random

# 允许的来源
MEDINEXUS_ALLOWED_ORIGINS=http://47.80.10.180,https://47.80.10.180

# 前端API地址
NEXT_PUBLIC_API_URL=http://47.80.10.180
```

#### 步骤4：构建并启动服务

```bash
cd /opt/medinexus/deploy
docker-compose -f /opt/medinexus/docker-compose.yml build --no-cache
docker-compose -f /opt/medinexus/docker-compose.yml up -d
```

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
mkdir -p /opt/medinexus/certs
cp /etc/letsencrypt/live/medinexus.example.com/fullchain.pem /opt/medinexus/certs/
cp /etc/letsencrypt/live/medinexus.example.com/privkey.pem /opt/medinexus/certs/
```

4. **更新Nginx配置**：使用支持HTTPS的配置文件（参考 `scripts/deploy/nginx-ssl.conf`）

### 6.2 使用自签名证书（仅测试环境）

```bash
mkdir -p /opt/medinexus/certs
openssl req -x509 -newkey rsa:4096 -keyout /opt/medinexus/certs/privkey.pem \
    -out /opt/medinexus/certs/fullchain.pem -days 365 -nodes \
    -subj "/CN=47.80.10.180"
```

> **警告**：自签名证书在浏览器中会显示安全警告，不适合生产环境使用。

## 7. 服务管理

### 7.1 查看服务状态

```bash
# 在服务器上执行
cd /opt/medinexus/deploy
docker-compose -f /opt/medinexus/docker-compose.yml ps
```

### 7.2 查看日志

```bash
# 查看所有服务日志
docker-compose -f /opt/medinexus/docker-compose.yml logs -f

# 查看特定服务日志
docker-compose -f /opt/medinexus/docker-compose.yml logs -f backend
docker-compose -f /opt/medinexus/docker-compose.yml logs -f frontend
docker-compose -f /opt/medinexus/docker-compose.yml logs -f nginx
```

### 7.3 启动/停止/重启服务

```bash
# 启动服务
docker-compose -f /opt/medinexus/docker-compose.yml up -d

# 停止服务
docker-compose -f /opt/medinexus/docker-compose.yml down

# 重启服务
docker-compose -f /opt/medinexus/docker-compose.yml restart

# 重启特定服务
docker-compose -f /opt/medinexus/docker-compose.yml restart backend
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
docker exec medinexus-postgres-1 pg_dump -U medinexus medinexus > /opt/medinexus/backup/postgres_backup.sql
```

### 9.2 备份Redis

```bash
docker exec medinexus-redis-1 redis-cli SAVE
docker cp medinexus-redis-1:/data/dump.rdb /opt/medinexus/backup/
```

### 9.3 备份Qdrant

```bash
tar -czf /opt/medinexus/backup/qdrant_backup.tar.gz /opt/medinexus/data/qdrant
```

### 9.4 自动化备份脚本

```bash
#!/bin/bash
BACKUP_DIR="/opt/medinexus/backup"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec medinexus-postgres-1 pg_dump -U medinexus medinexus > $BACKUP_DIR/postgres_$DATE.sql
docker exec medinexus-redis-1 redis-cli SAVE
docker cp medinexus-redis-1:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb
tar -czf $BACKUP_DIR/qdrant_$DATE.tar.gz /opt/medinexus/data/qdrant

find $BACKUP_DIR -type f -mtime +7 -delete
```

## 10. 性能优化

### 10.1 Docker资源限制

在 `docker-compose.yml` 中配置：

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

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

## 11. 故障排查

### 11.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 服务无法启动 | 端口被占用 | 检查端口占用：`netstat -tlnp` |
| 数据库连接失败 | 密码错误 | 检查 `.env` 文件中的数据库密码 |
| 前端无法访问API | CORS配置错误 | 检查 `MEDINEXUS_ALLOWED_ORIGINS` |
| 内存不足 | 容器内存限制过低 | 增加内存限制或升级服务器配置 |
| 镜像构建失败 | 网络问题 | 配置Docker镜像加速器 |

### 11.2 查看详细日志

```bash
# 查看所有服务日志
docker-compose -f /opt/medinexus/docker-compose.yml logs

# 查看最近100行日志
docker-compose -f /opt/medinexus/docker-compose.yml logs --tail=100

# 实时查看日志
docker-compose -f /opt/medinexus/docker-compose.yml logs -f
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
/opt/medinexus/
├── deploy/                    # 项目代码
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
| 前端页面 | http://47.80.10.180 |
| API文档 | http://47.80.10.180/api/v1/docs |
| 健康检查 | http://47.80.10.180/health |
| PostgreSQL | localhost:5432 (内部) |
| Redis | localhost:6379 (内部) |
| Qdrant | localhost:6333 (内部) |

## 14. 安全建议

1. **修改默认密码**：修改 `.env` 文件中的所有密码
2. **启用HTTPS**：配置SSL证书
3. **限制访问**：配置安全组只允许必要的端口
4. **定期备份**：配置自动备份脚本
5. **更新系统**：定期执行 `apt update && apt upgrade`
6. **监控日志**：定期检查服务日志
7. **禁用root远程登录**：创建普通用户进行日常操作