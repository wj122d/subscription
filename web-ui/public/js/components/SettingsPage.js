// 设置组件
export const SettingsPage = {
  template: `
    <div>
      <h1 class="mb-4">设置</h1>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">基本设置</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="default-output-format">默认输出格式</label>
                <select class="form-select" id="default-output-format" v-model="settings.defaultOutputFormat">
                  <option value="clash">Clash</option>
                  <option value="v2ray">V2Ray</option>
                </select>
              </div>
              
              <div class="form-group">
                <label class="form-label" for="default-template">默认配置模板</label>
                <select class="form-select" id="default-template" v-model="settings.defaultTemplate">
                  <option value="minimal">简洁 (Minimal)</option>
                  <option value="standard">标准 (Standard)</option>
                  <option value="advanced">高级 (Advanced)</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label" for="default-expire-hours">默认过期时间（小时）</label>
                <input type="number" class="form-control" id="default-expire-hours" v-model="settings.defaultExpireHours" min="1">
              </div>
              
              <div class="form-group">
                <label class="form-label" for="default-server-port">默认服务器端口</label>
                <input type="number" class="form-control" id="default-server-port" v-model="settings.defaultServerPort" min="1024" max="65535">
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">高级设置</h5>
        </div>
        <div class="card-body">
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="filter-info-nodes" v-model="settings.filterInfoNodes">
            <label class="form-check-label" for="filter-info-nodes">
              默认过滤信息节点（流量、到期时间等）
            </label>
          </div>
          
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="compatible-mode" v-model="settings.compatibleMode">
            <label class="form-check-label" for="compatible-mode">
              默认启用兼容模式（转换不支持的协议为兼容格式）
            </label>
          </div>
          
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="dark-mode" v-model="settings.darkMode" @change="toggleDarkMode">
            <label class="form-check-label" for="dark-mode">
              深色模式
            </label>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="secret-key">加密密钥（用于时效链接）</label>
            <div class="input-group">
              <input :type="showSecretKey ? 'text' : 'password'" class="form-control" id="secret-key" v-model="settings.secretKey">
              <button class="btn btn-outline-secondary" type="button" @click="showSecretKey = !showSecretKey">
                <i class="bi" :class="showSecretKey ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
            </div>
            <small class="form-text text-muted">用于生成和验证时效链接的签名，请妥善保管</small>
          </div>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">自定义模板</h5>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label" for="custom-template-name">模板名称</label>
            <input type="text" class="form-control" id="custom-template-name" v-model="newTemplate.name" placeholder="我的模板">
          </div>
          
          <div class="form-group">
            <label class="form-label" for="custom-template-content">模板内容</label>
            <textarea class="form-control code-editor" id="custom-template-content" v-model="newTemplate.content" rows="10" placeholder="# 在此输入YAML格式的模板内容"></textarea>
          </div>
          
          <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-3">
            <button class="btn btn-primary" @click="addTemplate">
              <i class="bi bi-plus-circle me-2"></i>添加模板
            </button>
          </div>
          
          <hr>
          
          <h6 class="mb-3">已保存的模板</h6>
          <div class="list-group">
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" v-for="(template, index) in settings.customTemplates" :key="index">
              <div>
                <h6 class="mb-1">{{ template.name }}</h6>
                <small>{{ template.content.substring(0, 50) }}...</small>
              </div>
              <div>
                <button class="btn btn-sm btn-outline-primary me-2" @click="editTemplate(index)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteTemplate(index)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="d-grid gap-2 d-md-flex justify-content-md-end">
        <button class="btn btn-secondary" @click="resetSettings">
          <i class="bi bi-arrow-counterclockwise me-2"></i>恢复默认设置
        </button>
        <button class="btn btn-primary" @click="saveSettings">
          <i class="bi bi-save me-2"></i>保存设置
        </button>
      </div>
      
      <div class="alert alert-success mt-4" v-if="saveSuccess">
        <i class="bi bi-check-circle-fill me-2"></i>设置已保存
      </div>
    </div>
  `,
  data() {
    return {
      settings: {
        defaultOutputFormat: 'clash',
        defaultTemplate: 'standard',
        defaultExpireHours: 24,
        defaultServerPort: 8080,
        filterInfoNodes: true,
        compatibleMode: true,
        darkMode: false,
        secretKey: 'subscription_converter_secret',
        customTemplates: [
          {
            name: '示例模板',
            content: 'port: 7890\nmode: Rule\nproxies:\n  # 这里会自动填充代理节点\nproxy-groups:\n  - name: 自动选择\n    type: url-test\n    proxies: []\n    url: http://www.gstatic.com/generate_204\n    interval: 300'
          }
        ]
      },
      newTemplate: {
        name: '',
        content: ''
      },
      showSecretKey: false,
      saveSuccess: false
    };
  },
  methods: {
    toggleDarkMode() {
      document.body.classList.toggle('dark-mode', this.settings.darkMode);
    },
    addTemplate() {
      if (!this.newTemplate.name || !this.newTemplate.content) {
        alert('请填写模板名称和内容');
        return;
      }
      
      this.settings.customTemplates.push({
        name: this.newTemplate.name,
        content: this.newTemplate.content
      });
      
      // 清空表单
      this.newTemplate.name = '';
      this.newTemplate.content = '';
    },
    editTemplate(index) {
      const template = this.settings.customTemplates[index];
      this.newTemplate.name = template.name;
      this.newTemplate.content = template.content;
      
      // 删除原模板
      this.settings.customTemplates.splice(index, 1);
      
      // 滚动到表单
      document.getElementById('custom-template-name').scrollIntoView({ behavior: 'smooth' });
    },
    deleteTemplate(index) {
      if (confirm('确定要删除此模板吗？')) {
        this.settings.customTemplates.splice(index, 1);
      }
    },
    saveSettings() {
      // 这里应该是实际的保存逻辑，例如保存到localStorage或发送到服务器
      localStorage.setItem('subscription-converter-settings', JSON.stringify(this.settings));
      
      this.saveSuccess = true;
      setTimeout(() => {
        this.saveSuccess = false;
      }, 3000);
    },
    resetSettings() {
      if (confirm('确定要恢复默认设置吗？所有自定义设置将被清除。')) {
        this.settings = {
          defaultOutputFormat: 'clash',
          defaultTemplate: 'standard',
          defaultExpireHours: 24,
          defaultServerPort: 8080,
          filterInfoNodes: true,
          compatibleMode: true,
          darkMode: false,
          secretKey: 'subscription_converter_secret',
          customTemplates: []
        };
        
        // 更新深色模式
        document.body.classList.toggle('dark-mode', this.settings.darkMode);
      }
    }
  },
  mounted() {
    // 从localStorage加载设置
    const savedSettings = localStorage.getItem('subscription-converter-settings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        this.settings = { ...this.settings, ...parsedSettings };
        
        // 应用深色模式
        document.body.classList.toggle('dark-mode', this.settings.darkMode);
      } catch (e) {
        console.error('加载设置失败:', e);
      }
    }
  }
};