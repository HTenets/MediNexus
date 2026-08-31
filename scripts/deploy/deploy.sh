#!/bin/bash

set -e

PROJECT_DIR="/opt/program/medinexus_deploy"
DEPLOY_DIR="/opt/program/medinexus_deploy/MediNexus"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  MediNexus 部署脚本"
echo "=========================================="

usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -u, --upload        上传代码到服务器 (git pull)"
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
    echo "1. 更新服务器代码..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && git pull origin main"

    echo ""
    echo "✅ 代码更新完成！"
}

build_images() {
    echo ""
    echo "构建 Docker 镜像..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose --env-file $DEPLOY_DIR/scripts/deploy/.env.production -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml build --no-parallel"
    echo ""
    echo "✅ 镜像构建完成！"
}

start_services() {
    echo ""
    echo "启动服务..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose --env-file $DEPLOY_DIR/scripts/deploy/.env.production -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml up -d"
    echo ""
    echo "✅ 服务启动完成！"
    echo ""
    echo "等待服务初始化..."
    sleep 10

    echo ""
    echo "校验 nginx 配置..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml exec -T nginx nginx -t" || {
        echo "❌ nginx 配置校验失败，请检查日志"
        return 1
    }

    echo ""
    echo "执行部署后冒烟测试..."
    ssh root@47.80.10.180 "curl -sf http://localhost:80/programs/medinexus/health > /dev/null && echo '✅ health OK' || echo '⚠ health 检查失败（可能仍在启动）'"
    ssh root@47.80.10.180 "curl -sf http://localhost:80/programs/medinexus/login > /dev/null && echo '✅ login 页面 OK' || echo '⚠ login 页面检查失败'"
}

stop_services() {
    echo ""
    echo "停止服务..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml down"
    echo ""
    echo "✅ 服务已停止！"
}

restart_services() {
    echo ""
    echo "重启服务..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml restart"
    echo ""
    echo "✅ 服务重启完成！"
}

view_logs() {
    echo ""
    echo "查看服务日志..."
    ssh root@47.80.10.180 "cd $DEPLOY_DIR && docker compose -f $DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml logs -f"
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