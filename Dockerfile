FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装依赖
RUN pip install --no-cache-dir PyYAML requests

# 复制项目文件
COPY subscription_converter.py /app/
COPY timed_link_utils.py /app/
COPY convert.sh /app/
COPY README.md /app/
COPY web-ui/ /app/web-ui/
COPY start_web_ui.py /app/

# 复制入口脚本
COPY docker-entrypoint.sh /app/

# 设置权限
RUN chmod +x /app/convert.sh
RUN chmod +x /app/subscription_converter.py
RUN chmod +x /app/web-ui/docker_server.py
RUN chmod +x /app/docker-entrypoint.sh

# 创建配置目录
RUN mkdir -p /app/config

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PORT=8000

# 设置入口点
ENTRYPOINT ["/app/docker-entrypoint.sh"]