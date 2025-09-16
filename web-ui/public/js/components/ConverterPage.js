// 订阅转换组件
export const ConverterPage = {
  template: `
    <div>
      <h1 class="mb-4">订阅转换</h1>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">输入订阅信息</h5>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">订阅来源</label>
            <div class="btn-group w-100 mb-3" role="group">
              <input type="radio" class="btn-check" name="source" id="source-url" v-model="source" value="url" autocomplete="off" checked>
              <label class="btn btn-outline-primary" for="source-url">订阅链接</label>
              
              <input type="radio" class="btn-check" name="source" id="source-file" v-model="source" value="file" autocomplete="off">
              <label class="btn btn-outline-primary" for="source-file">本地文件</label>
              
              <input type="radio" class="btn-check" name="source" id="source-text" v-model="source" value="text" autocomplete="off">
              <label class="btn btn-outline-primary" for="source-text">文本输入</label>
            </div>
          </div>
          
          <div class="form-group" v-if="source === 'url'">
            <label class="form-label" for="subscription-url">订阅链接</label>
            <input type="text" class="form-control" id="subscription-url" v-model="subscriptionUrl" placeholder="https://example.com/subscribe">
          </div>
          
          <div class="form-group" v-if="source === 'file'">
            <label class="form-label" for="subscription-file">本地文件</label>
            <input type="file" class="form-control" id="subscription-file" @change="handleFileUpload">
          </div>
          
          <div class="form-group" v-if="source === 'text'">
            <label class="form-label" for="subscription-text">节点内容</label>
            <textarea class="form-control" id="subscription-text" v-model="subscriptionText" rows="5" placeholder="输入节点内容，每行一个节点链接"></textarea>
          </div>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">转换选项</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="output-format">输出格式</label>
                <select class="form-select" id="output-format" v-model="outputFormat">
                  <option value="clash">Clash</option>
                  <option value="v2ray">V2Ray</option>
                </select>
              </div>
              
              <div class="form-group">
                <label class="form-label" for="template">配置模板</label>
                <select class="form-select" id="template" v-model="template">
                  <option value="minimal">简洁 (Minimal)</option>
                  <option value="standard">标准 (Standard)</option>
                  <option value="advanced">高级 (Advanced)</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="output-filename">输出文件名</label>
                <input type="text" class="form-control" id="output-filename" v-model="outputFilename" placeholder="config.yaml">
              </div>
              
              <div class="form-group">
                <label class="form-label" for="node-limit">节点数量限制</label>
                <input type="number" class="form-control" id="node-limit" v-model="nodeLimit" min="0" placeholder="不限制">
              </div>
            </div>
          </div>
          
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="filter-info-nodes" v-model="filterInfoNodes">
            <label class="form-check-label" for="filter-info-nodes">
              过滤信息节点（流量、到期时间等）
            </label>
          </div>
          
          <div class="form-check">
            <input class="form-check-input" type="checkbox" id="compatible-mode" v-model="compatibleMode">
            <label class="form-check-label" for="compatible-mode">
              兼容模式（转换不支持的协议为兼容格式）
            </label>
          </div>
        </div>
      </div>
      
      <div class="d-grid">
        <button class="btn btn-primary btn-lg" @click="convertSubscription" :disabled="isConverting">
          <span v-if="isConverting">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            转换中...
          </span>
          <span v-else>
            <i class="bi bi-arrow-repeat me-2"></i>开始转换
          </span>
        </button>
      </div>
      
      <div class="alert alert-success mt-4" v-if="conversionSuccess">
        <h5><i class="bi bi-check-circle-fill me-2"></i>转换成功！</h5>
        <p>配置文件已生成：{{ outputFilename }}</p>
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
          <button class="btn btn-sm btn-outline-success" @click="downloadConfig">
            <i class="bi bi-download me-2"></i>下载配置
          </button>
          <button class="btn btn-sm btn-outline-primary" @click="previewConfig">
            <i class="bi bi-eye me-2"></i>预览配置
          </button>
        </div>
      </div>
      
      <div class="alert alert-danger mt-4" v-if="conversionError">
        <h5><i class="bi bi-exclamation-triangle-fill me-2"></i>转换失败</h5>
        <p>{{ errorMessage }}</p>
      </div>
    </div>
  `,
  data() {
    return {
      source: 'url',
      subscriptionUrl: '',
      subscriptionText: '',
      subscriptionFile: null,
      outputFormat: 'clash',
      template: 'standard',
      outputFilename: 'config.yaml',
      nodeLimit: '',
      filterInfoNodes: true,
      compatibleMode: true,
      isConverting: false,
      conversionSuccess: false,
      conversionError: false,
      errorMessage: '',
      configContent: ''
    };
  },
  methods: {
    handleFileUpload(event) {
      this.subscriptionFile = event.target.files[0];
    },
    convertSubscription() {
      this.isConverting = true;
      this.conversionSuccess = false;
      this.conversionError = false;
      
      // 模拟API调用
      setTimeout(() => {
        try {
          // 这里应该是实际的API调用
          // 模拟成功
          this.isConverting = false;
          this.conversionSuccess = true;
          this.configContent = '# 这是生成的配置文件内容\nproxies:\n  - name: 示例节点\n    type: ss\n    server: example.com\n    port: 443\n    cipher: aes-256-gcm\n    password: password';
        } catch (error) {
          this.isConverting = false;
          this.conversionError = true;
          this.errorMessage = error.message || '转换过程中发生错误';
        }
      }, 1500);
    },
    downloadConfig() {
      const blob = new Blob([this.configContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = this.outputFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    previewConfig() {
      alert('预览功能尚未实现');
      // 这里应该打开一个模态框显示配置内容
    }
  }
};