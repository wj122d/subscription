// 订阅服务器组件
export const ServerPage = {
  template: `
    <div>
      <h1 class="mb-4">订阅服务器</h1>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">服务器配置</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="subscription-source">订阅来源</label>
                <input type="text" class="form-control" id="subscription-source" v-model="subscriptionSource" placeholder="https://example.com/subscribe">
              </div>
              
              <div class="form-group">
                <label class="form-label" for="server-port">服务器端口</label>
                <input type="number" class="form-control" id="server-port" v-model="serverPort" min="1024" max="65535" placeholder="8080">
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="default-expire">默认过期时间（小时）</label>
                <input type="number" class="form-control" id="default-expire" v-model="defaultExpire" min="1" placeholder="24">
              </div>
              
              <div class="form-check mt-4">
                <input class="form-check-input" type="checkbox" id="filter-info-nodes" v-model="filterInfoNodes">
                <label class="form-check-label" for="filter-info-nodes">
                  过滤信息节点（流量、到期时间等）
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="d-grid gap-2">
        <button class="btn btn-info btn-lg text-white" @click="startServer" v-if="!serverRunning">
          <i class="bi bi-play-fill me-2"></i>启动服务器
        </button>
        <button class="btn btn-danger btn-lg" @click="stopServer" v-else>
          <i class="bi bi-stop-fill me-2"></i>停止服务器
        </button>
      </div>
      
      <div class="alert alert-info mt-4" v-if="serverRunning">
        <h5><i class="bi bi-info-circle-fill me-2"></i>服务器运行中</h5>
        <p>订阅服务器已在端口 {{ serverPort }} 上启动</p>
        <div class="code-block">
          <div class="mb-2">
            <strong>本地订阅链接：</strong>
            <code>http://localhost:{{ serverPort }}/sub?expire={{ defaultExpire }}</code>
          </div>
          <div>
            <strong>局域网订阅链接：</strong>
            <code>http://{{ localIp }}:{{ serverPort }}/sub?expire={{ defaultExpire }}</code>
          </div>
        </div>
        <p class="mt-3 mb-0">
          <i class="bi bi-lightbulb-fill me-2 text-warning"></i>
          提示：可以通过修改链接中的 expire 参数调整过期时间
        </p>
      </div>
      
      <div class="card mt-4" v-if="serverRunning">
        <div class="card-header">
          <h5 class="mb-0">服务器日志</h5>
        </div>
        <div class="card-body">
          <div class="code-block" style="max-height: 300px; overflow-y: auto;">
            <div v-for="(log, index) in serverLogs" :key="index" class="mb-1">
              <span class="text-muted">{{ log.time }}</span> - 
              <span :class="{'text-success': log.type === 'info', 'text-danger': log.type === 'error', 'text-warning': log.type === 'warning'}">
                {{ log.message }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      subscriptionSource: '',
      serverPort: 8080,
      defaultExpire: 24,
      filterInfoNodes: true,
      serverRunning: false,
      localIp: '192.168.1.100', // 模拟本地IP
      serverLogs: []
    };
  },
  methods: {
    startServer() {
      // 模拟启动服务器
      this.serverRunning = true;
      this.addLog('info', '服务器启动中...');
      setTimeout(() => {
        this.addLog('info', `服务器已在端口 ${this.serverPort} 上启动`);
        this.addLog('info', `加载订阅源: ${this.subscriptionSource}`);
        this.addLog('info', '解析节点信息...');
        this.addLog('info', '找到 8 个节点');
        this.addLog('info', '服务器准备就绪，等待连接...');
      }, 1000);
    },
    stopServer() {
      // 模拟停止服务器
      this.addLog('warning', '正在停止服务器...');
      setTimeout(() => {
        this.serverRunning = false;
        this.serverLogs = [];
      }, 1000);
    },
    addLog(type, message) {
      const now = new Date();
      const timeString = now.toLocaleTimeString();
      this.serverLogs.push({
        time: timeString,
        type: type,
        message: message
      });
      
      // 保持日志不超过100条
      if (this.serverLogs.length > 100) {
        this.serverLogs.shift();
      }
    }
  }
};