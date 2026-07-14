#!/bin/bash

set -e

echo "=========================================="
echo "  MediNexus 服务器环境初始化脚本"
echo "=========================================="

if [ "$(id -u)" != "0" ]; then
    echo "错误：必须以root用户运行此脚本"
    exit 1
fi

echo ""
echo "1. 更新系统软件包..."
apt update -y && apt upgrade -y

echo ""
echo "2. 安装必要依赖..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    git \
    wget \
    unzip \
    vim

echo ""
echo "3. 安装 Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io

echo ""
echo "4. 安装 Docker Compose..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo ""
echo "5. 启动 Docker 服务..."
systemctl start docker
systemctl enable docker

echo ""
echo "6. 创建项目目录..."
mkdir -p /opt/program/medinexus_deploy
mkdir -p /opt/program/medinexus_deploy/logs
mkdir -p /opt/program/medinexus_deploy/data/postgres
mkdir -p /opt/program/medinexus_deploy/data/redis
mkdir -p /opt/program/medinexus_deploy/data/qdrant

echo ""
echo "7. 配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable

echo ""
echo "8. 创建普通用户..."
if ! id -u medinexus &>/dev/null; then
    useradd -m -s /bin/bash medinexus
    usermod -aG docker medinexus
    echo "medinexus用户已创建"
fi

echo ""
echo "=========================================="
echo "  服务器环境初始化完成！"
echo "=========================================="
echo ""
echo "接下来请执行："
echo "1. 克隆代码仓库到 /opt/program/medinexus_deploy/MediNexus"
echo "   git clone <your-repository-url> /opt/program/medinexus_deploy/MediNexus"
echo "2. 运行 deploy.sh 脚本进行部署"
echo ""