#!/bin/bash
set -e

# 打印欢迎信息
echo "========================================"
echo "Subscription Converter Docker 版本"
echo "========================================"
echo "启动中..."
echo ""

# 检查配置目录
CONFIG_DIR="/app/config"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "创建配置目录: $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR"
fi

# 设置默认端口
PORT=${PORT:-8000}
echo "使用端口: $PORT"

# 启动服务器
echo "启动Web服务器..."
exec python /app/web-ui/docker_server.py --port "$PORT"