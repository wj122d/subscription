# 构建阶段 1: 前端构建
FROM node:18-alpine AS frontend-builder
WORKDIR /app

# 安装依赖
COPY web-ui/package*.json ./
RUN npm ci --only=production

# 复制源代码并构建
COPY web-ui/ ./
RUN npm run build

# 构建阶段 2: 后端依赖
FROM node:18-alpine AS backend-builder
WORKDIR /app

# 安装生产依赖
COPY package*.json ./
RUN npm ci --only=production && \
    # 删除不必要的文件以减小体积
    npm cache clean --force

# 构建阶段 3: 最终镜像
FROM node:18-alpine AS production
WORKDIR /app

# 安装运行时必要的工具
RUN apk --no-cache add curl

# 设置非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S -u 1001 -G nodejs nodejs
USER nodejs

# 复制构建产物和依赖
COPY --from=frontend-builder --chown=nodejs:nodejs /app/build ./web-ui/build
COPY --from=backend-builder --chown=nodejs:nodejs /app/node_modules ./node_modules

# 复制应用代码
COPY --chown=nodejs:nodejs package.json ./
COPY --chown=nodejs:nodejs server ./server

# 环境变量配置
ENV PORT=3001 \
    NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=256"

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["node", "--max-old-space-size=256", "server/index.js"]