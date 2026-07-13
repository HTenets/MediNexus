#!/bin/bash

set -e

PROJECT_DIR="/opt/medinexus"
DEPLOY_DIR="/opt/medinexus/deploy"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  MediNexus 部署脚本"
echo "=========================================="

usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -u, --upload        上传代码到服务器"
    echo "  -b, --build         构建 Docker 镜像"
    echo "  -s, --start         启动服务"
    echo "  -d, --down          停止服务"
    echo "  -r, --restart       重启服务"
    echo "  -l, --logs          查看服务日志"
    echo "  -f, --full          执行完整部署流程"
    echo "  -c, --clean         清理旧容器和镜像"
    echo ""
    exit 0
}

upload_code() {
    echo ""
    echo "1. 打包项目代码..."
    cd "$SCRIPT_DIR/../.."
    rm -f medinexus-deploy.tar.gz
    tar --exclude='node_modules' --exclude='.git' --exclude='*.pyc' \
        --exclude='__pycache__' --exclude='*.log' --exclude='.env' \
        -czf medinexus-deploy.tar.gz .

    echo ""
    echo "2. 上传代码到服务器..."
    scp medinexus-deploy.tar.gz root@47.80.10.180:/opt/medinexus/

    echo ""
    echo "3. 解压代码..."
    ssh root@47.80.10.180 "cd /opt/medinexus && rm -rf deploy && mkdir -p deploy && tar -xzf medinexus-deploy.tar.gz -C deploy --strip-components=1"

    echo ""
    echo "4. 复制部署配置文件..."
    ssh root@47.80.10.180 "cp /opt/medinexus/deploy/scripts/deploy/docker-compose.prod.yml /opt/medinexus/docker-compose.yml"
    ssh root@47.80.10.180 "cp /opt/medinexus/deploy/scripts/deploy/.env.production /opt/medinexus/.env"
    ssh root@47.80.10.180 "cp /opt/medinexus/deploy/scripts/deploy/nginx.conf /opt/medinexus/deploy/infrastructure/nginx/nginx.conf"

    echo ""
    echo "✅ 代码上传完成！"
}

build_images() {
    echo ""
    echo "构建 Docker 镜像..."
    ssh root@47.80.10.180 "cd /opt/medinexus/deploy && docker-compose -f /opt/medinexus/docker-compose.yml build --no-cache"
    echo ""
    echo "✅ 镜像构建完成！"
}

start_services() {
    echo ""
    echo "启动服务..."
    ssh root@47.80.10.180 "cd /opt/medinexus/deploy && docker-compose -f /opt/medinexus/docker-compose.yml up -d"
    echo ""
    echo "✅ 服务启动完成！"
    echo ""
    echo "等待服务初始化..."
    sleep 10
    ssh root@47.80.10.180 "curl -s http://localhost:80/health || echo '服务正在启动中，请稍后检查'"
}

stop_services() {
    echo ""
    echo "停止服务..."
    ssh root@47.80.10.180 "cd /opt/medinexus/deploy && docker-compose -f /opt/medinexus/docker-compose.yml down"
    echo ""
    echo "✅ 服务已停止！"
}

restart_services() {
    echo ""
    echo "重启服务..."
    ssh root@47.80.10.180 "cd /opt/medinexus/deploy && docker-compose -f /opt/medinexus/docker-compose.yml restart"
    echo ""
    echo "✅ 服务重启完成！"
}

view_logs() {
    echo ""
    echo "查看服务日志..."
    ssh root@47.80.10.180 "cd /opt/medinexus/deploy && docker-compose -f /opt/medinexus/docker-compose.yml logs -f"
}

cleanup() {
    echo ""
    echo "清理旧容器和镜像..."
    ssh root@47.80.10.180 "docker system prune -af"
    echo ""
    echo "✅ 清理完成！"
}

full_deploy() {
    upload_code
    build_images
    start_services
    echo ""
    echo "=========================================="
    echo "  部署完成！"
    echo "=========================================="
    echo ""
    echo "访问地址: http://47.80.10.180"
    echo "API地址:  http://47.80.10.180/api/v1"
    echo "健康检查: http://47.80.10.180/health"
}

if [ $# -eq 0 ]; then
    usage
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -u|--upload)
            upload_code
            ;;
        -b|--build)
            build_images
            ;;
        -s|--start)
            start_services
            ;;
        -d|--down)
            stop_services
            ;;
        -r|--restart)
            restart_services
            ;;
        -l|--logs)
            view_logs
            ;;
        -f|--full)
            full_deploy
            ;;
        -c|--clean)
            cleanup
            ;;
        *)
            echo "错误: 未知选项 $1"
            usage
            ;;
    esac
    shift
done