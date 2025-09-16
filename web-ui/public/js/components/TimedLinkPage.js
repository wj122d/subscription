// 时效链接组件
export const TimedLinkPage = {
  template: `
    <div>
      <h1 class="mb-4">时效链接生成</h1>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">输入SS链接</h5>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">链接来源</label>
            <div class="btn-group w-100 mb-3" role="group">
              <input type="radio" class="btn-check" name="link-source" id="link-source-single" v-model="linkSource" value="single" autocomplete="off" checked>
              <label class="btn btn-outline-primary" for="link-source-single">单个链接</label>
              
              <input type="radio" class="btn-check" name="link-source" id="link-source-file" v-model="linkSource" value="file" autocomplete="off">
              <label class="btn btn-outline-primary" for="link-source-file">本地文件</label>
              
              <input type="radio" class="btn-check" name="link-source" id="link-source-text" v-model="linkSource" value="text" autocomplete="off">
              <label class="btn btn-outline-primary" for="link-source-text">文本输入</label>
            </div>
          </div>
          
          <div class="form-group" v-if="linkSource === 'single'">
            <label class="form-label" for="ss-link">SS链接</label>
            <input type="text" class="form-control" id="ss-link" v-model="ssLink" placeholder="ss://...">
          </div>
          
          <div class="form-group" v-if="linkSource === 'file'">
            <label class="form-label" for="ss-file">本地文件</label>
            <input type="file" class="form-control" id="ss-file" @change="handleFileUpload">
          </div>
          
          <div class="form-group" v-if="linkSource === 'text'">
            <label class="form-label" for="ss-text">SS链接列表</label>
            <textarea class="form-control" id="ss-text" v-model="ssText" rows="5" placeholder="输入SS链接，每行一个"></textarea>
          </div>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">时效设置</h5>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label" for="expire-hours">过期时间（小时）</label>
            <input type="number" class="form-control" id="expire-hours" v-model="expireHours" min="1" placeholder="24">
          </div>
          
          <div class="form-group">
            <label class="form-label" for="output-file">输出文件名</label>
            <input type="text" class="form-control" id="output-file" v-model="outputFile" placeholder="timed_links.txt">
          </div>
        </div>
      </div>
      
      <div class="d-grid">
        <button class="btn btn-success btn-lg" @click="generateTimedLinks" :disabled="isGenerating">
          <span v-if="isGenerating">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            生成中...
          </span>
          <span v-else>
            <i class="bi bi-clock-history me-2"></i>生成时效链接
          </span>
        </button>
      </div>
      
      <div class="alert alert-success mt-4" v-if="generateSuccess">
        <h5><i class="bi bi-check-circle-fill me-2"></i>生成成功！</h5>
        <p>已生成 {{ generatedLinks.length }} 个带时效的链接，过期时间：{{ expireHours }} 小时</p>
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
          <button class="btn btn-sm btn-outline-success" @click="downloadLinks">
            <i class="bi bi-download me-2"></i>下载链接
          </button>
          <button class="btn btn-sm btn-outline-primary" @click="copyLinks">
            <i class="bi bi-clipboard me-2"></i>复制链接
          </button>
        </div>
      </div>
      
      <div class="alert alert-danger mt-4" v-if="generateError">
        <h5><i class="bi bi-exclamation-triangle-fill me-2"></i>生成失败</h5>
        <p>{{ errorMessage }}</p>
      </div>
      
      <div class="card mt-4" v-if="generateSuccess && generatedLinks.length > 0">
        <div class="card-header">
          <h5 class="mb-0">生成的链接</h5>
        </div>
        <div class="card-body">
          <div class="code-block">
            <div v-for="(link, index) in generatedLinks" :key="index" class="mb-2">
              {{ link.substring(0, 50) }}...
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      linkSource: 'single',
      ssLink: '',
      ssText: '',
      ssFile: null,
      expireHours: 24,
      outputFile: 'timed_links.txt',
      isGenerating: false,
      generateSuccess: false,
      generateError: false,
      errorMessage: '',
      generatedLinks: []
    };
  },
  methods: {
    handleFileUpload(event) {
      this.ssFile = event.target.files[0];
    },
    generateTimedLinks() {
      this.isGenerating = true;
      this.generateSuccess = false;
      this.generateError = false;
      
      // 模拟API调用
      setTimeout(() => {
        try {
          // 这里应该是实际的API调用
          // 模拟成功
          this.isGenerating = false;
          this.generateSuccess = true;
          this.generatedLinks = [
            'ss://time:YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkw',
            'ss://time:YmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejEyMzQ1Njc4OTA='
          ];
        } catch (error) {
          this.isGenerating = false;
          this.generateError = true;
          this.errorMessage = error.message || '生成过程中发生错误';
        }
      }, 1500);
    },
    downloadLinks() {
      const blob = new Blob([this.generatedLinks.join('\n')], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = this.outputFile;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    copyLinks() {
      navigator.clipboard.writeText(this.generatedLinks.join('\n'))
        .then(() => {
          alert('链接已复制到剪贴板');
        })
        .catch(err => {
          alert('复制失败: ' + err);
        });
    }
  }
};