#!/bin/bash

set -e

echo "=========================================="
echo "  MediNexus 登录503错误一键修复脚本"
echo "=========================================="

PROJECT_DIR="/opt/medinexus"
DEPLOY_DIR="/opt/medinexus/deploy"

echo ""
echo "1. 更新配置文件..."

# 更新 Docker Compose 配置
cp "$DEPLOY_DIR/scripts/deploy/docker-compose.prod.yml" "$PROJECT_DIR/docker-compose.yml"

# 更新 .env 文件
POSTGRES_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)

cat > "$PROJECT_DIR/.env" <<EOF
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

echo "✅ .env 文件已更新"

# 更新 Nginx 配置
cp "$DEPLOY_DIR/scripts/deploy/nginx.conf" "$DEPLOY_DIR/infrastructure/nginx/nginx.conf"
echo "✅ Nginx 配置已更新"

echo ""
echo "2. 停止旧服务..."
cd "$DEPLOY_DIR"
docker-compose -f "$PROJECT_DIR/docker-compose.yml" down 2>/dev/null || echo "服务未运行"

echo ""
echo "3. 构建并启动服务..."
docker-compose -f "$PROJECT_DIR/docker-compose.yml" up -d --build

echo ""
echo "4. 等待服务启动..."
sleep 30

echo ""
echo "5. 检查服务状态..."
docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps

echo ""
echo "6. 测试健康检查..."
HEALTH_CHECK=$(curl -s http://localhost:80/health || echo '{"status": "unavailable"}')
echo "健康检查结果: $HEALTH_CHECK"

echo ""
echo "7. 测试登录接口..."
LOGIN_RESULT=$(curl -s -X POST http://localhost:80/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "123456", "role": "patient"}')

if echo "$LOGIN_RESULT" | grep -q "access_token"; then
    echo "✅ 登录接口测试成功!"
    echo "登录结果: $LOGIN_RESULT"
else
    echo "❌ 登录接口测试失败!"
    echo "错误信息: $LOGIN_RESULT"
    echo ""
    echo "查看后端日志:"
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" logs backend | tail -30
fi

echo ""
echo "=========================================="
echo "  修复完成!"
echo "=========================================="
echo ""
echo "访问地址: http://47.80.10.180"
echo "API地址:  http://47.80.10.180/api/v1"
echo "健康检查: http://47.80.10.180/health"
echo ""
echo "登录账号: demo@example.com"
echo "登录密码: 任意密码"
echo "角色: patient 或 doctor"