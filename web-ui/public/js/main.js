// 主应用程序文件
// 导入组件
import { AppNavbar } from './components/AppNavbar.js';
import { AppSidebar } from './components/AppSidebar.js';
import { HomePage } from './components/HomePage.js';
import { ConverterPage } from './components/ConverterPage.js';
import { TimedLinkPage } from './components/TimedLinkPage.js';
import { ServerPage } from './components/ServerPage.js';
import { SettingsPage } from './components/SettingsPage.js';

// 创建路由
const routes = {
  '/': HomePage,
  '/converter': ConverterPage,
  '/timed-link': TimedLinkPage,
  '/server': ServerPage,
  '/settings': SettingsPage
};

// 创建Vue应用
const app = Vue.createApp({
  data() {
    return {
      currentRoute: window.location.hash.slice(1) || '/',
      sidebarCollapsed: window.innerWidth < 768,
      pageTitle: '订阅转换工具'
    };
  },
  computed: {
    currentView() {
      return routes[this.currentRoute] || HomePage;
    }
  },
  methods: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
    updatePageTitle() {
      switch (this.currentRoute) {
        case '/':
          this.pageTitle = '首页';
          break;
        case '/converter':
          this.pageTitle = '订阅转换';
          break;
        case '/timed-link':
          this.pageTitle = '时效链接';
          break;
        case '/server':
          this.pageTitle = '订阅服务器';
          break;
        case '/settings':
          this.pageTitle = '设置';
          break;
        default:
          this.pageTitle = '订阅转换工具';
      }
    }
  },
  watch: {
    currentRoute() {
      this.updatePageTitle();
    }
  },
  mounted() {
    window.addEventListener('hashchange', () => {
      this.currentRoute = window.location.hash.slice(1) || '/';
    });
    
    window.addEventListener('resize', () => {
      if (window.innerWidth < 768) {
        this.sidebarCollapsed = true;
      }
    });
    
    this.updatePageTitle();
  },
  template: `
    <div class="app-container">
      <AppSidebar :collapsed="sidebarCollapsed" />
      <div class="main-content" :class="{ 'main-content-expanded': sidebarCollapsed }">
        <AppNavbar :title="pageTitle" :sidebarCollapsed="sidebarCollapsed" @toggle-sidebar="toggleSidebar" />
        <div class="container-fluid py-4">
          <component :is="currentView"></component>
        </div>
      </div>
    </div>
  `
});

// 注册组件
app.component('AppNavbar', AppNavbar);
app.component('AppSidebar', AppSidebar);

// 挂载应用
app.mount('#app');