#!/bin/bash

echo "开始部署教学评估系统..."

# 检查 Docker 是否安装
if ! command -v docker >/dev/null 2>&1; then
  echo "错误: Docker 未安装，请先安装 Docker"
  exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose >/dev/null 2>&1; then
  echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
  exit 1
fi

# 创建必要的目录
mkdir -p logs static

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "错误: .env 文件不存在，请创建 .env 文件以配置环境变量"
    exit 1
else
    echo "使用现有的 .env 配置文件"
fi

echo "构建并启动服务..."
docker-compose down -v
docker-compose up --build -d

echo "等待数据库服务启动..."
# 等待 db 容器健康
until docker-compose exec -T db mysqladmin ping -h "localhost" -u"${MYSQL_USER:-root}" -p"${MYSQL_PASSWORD:-root}" >/dev/null 2>&1; do
  echo "数据库尚未就绪，等待 2 秒..."
  sleep 2
done

echo "数据库已就绪，执行 Alembic 迁移..."
docker-compose exec backend alembic upgrade head

echo "部署完成！"
echo "访问 http://localhost:8000 查看应用"
echo ""
echo "提示："
echo "- 本地无需 SSL，可直接通过 http 访问"
