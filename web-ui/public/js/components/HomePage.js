// 首页组件
export const HomePage = {
  template: `
    <div>
      <h1 class="mb-4">订阅转换工具</h1>
      <div class="row">
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-arrow-repeat display-4 text-primary mb-3"></i>
              <h5 class="card-title">订阅转换</h5>
              <p class="card-text">将各种代理协议的订阅链接转换为不同客户端可用的配置文件</p>
              <a href="#/converter" class="btn btn-primary">开始转换</a>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-clock-history display-4 text-success mb-3"></i>
              <h5 class="card-title">时效链接</h5>
              <p class="card-text">生成带有过期时间的SS链接，过期后节点将无法访问</p>
              <a href="#/timed-link" class="btn btn-success">生成链接</a>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-server display-4 text-info mb-3"></i>
              <h5 class="card-title">订阅服务器</h5>
              <p class="card-text">启动本地订阅服务器，提供带时效的订阅链接</p>
              <a href="#/server" class="btn btn-info text-white">启动服务器</a>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-gear display-4 text-secondary mb-3"></i>
              <h5 class="card-title">设置</h5>
              <p class="card-text">配置转换选项、模板和其他高级设置</p>
              <a href="#/settings" class="btn btn-secondary">查看设置</a>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card mt-4">
        <div class="card-header">
          <h5 class="mb-0">功能介绍</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>多协议支持</h6>
              <p>支持VMess、VLESS、Shadowsocks、Trojan、Hysteria2等多种代理协议</p>
              
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>多种输入方式</h6>
              <p>支持直接输入订阅链接、从本地文件读取节点信息</p>
              
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>多种输出格式</h6>
              <p>支持Clash YAML配置、V2Ray JSON配置等多种输出格式</p>
            </div>
            <div class="col-md-6">
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>兼容性处理</h6>
              <p>自动转换不支持的协议，确保生成的配置可用于所有客户端</p>
              
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>时效链接</h6>
              <p>生成带有过期时间的链接，过期后节点将无法访问</p>
              
              <h6><i class="bi bi-check-circle-fill text-success me-2"></i>订阅服务器</h6>
              <p>启动本地订阅服务器，提供带时效的订阅链接</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
};