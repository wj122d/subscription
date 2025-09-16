require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const compression = require('compression');
const path = require('path');

const app = express();
const port = process.env.PORT || 3001;

// 日志中间件
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));

// 压缩中间件
app.use(compression());

// 安全中间件
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:"],
    },
  },
  xssFilter: true,
  noSniff: true,
  referrerPolicy: { policy: 'same-origin' }
}));

app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 速率限制
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 默认15分钟
  max: parseInt(process.env.RATE_LIMIT_MAX) || 100, // 默认每个IP限制100个请求
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: '请求过于频繁，请稍后再试' }
});
app.use('/api', limiter); // 只对API路由应用限制

// 请求体解析
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// 静态文件服务
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../web-ui/build')));
}

// API路由
app.get('/api', (req, res) => {
  res.json({ 
    message: 'Hello from Express!',
    timestamp: new Date().toISOString()
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});