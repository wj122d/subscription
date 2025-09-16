// 侧边栏组件
export const AppSidebar = {
  props: ['collapsed'],
  template: `
    <div class="sidebar" :class="{ 'sidebar-collapsed': collapsed }">
      <div class="sidebar-header">
        <a href="#/" class="sidebar-logo">
          <i class="bi bi-arrow-repeat me-2"></i>
          <span v-show="!collapsed">订阅转换器</span>
        </a>
      </div>
      <ul class="sidebar-menu">
        <li class="sidebar-menu-item" :class="{ active: currentRoute === '/' }" @click="navigate('/')">
          <i class="bi bi-house"></i>
          <span class="sidebar-menu-text" v-show="!collapsed">首页</span>
        </li>
        <li class="sidebar-menu-item" :class="{ active: currentRoute === '/converter' }" @click="navigate('/converter')">
          <i class="bi bi-arrow-repeat"></i>
          <span class="sidebar-menu-text" v-show="!collapsed">订阅转换</span>
        </li>
        <li class="sidebar-menu-item" :class="{ active: currentRoute === '/timed-link' }" @click="navigate('/timed-link')">
          <i class="bi bi-clock-history"></i>
          <span class="sidebar-menu-text" v-show="!collapsed">时效链接</span>
        </li>
        <li class="sidebar-menu-item" :class="{ active: currentRoute === '/server' }" @click="navigate('/server')">
          <i class="bi bi-server"></i>
          <span class="sidebar-menu-text" v-show="!collapsed">订阅服务器</span>
        </li>
        <li class="sidebar-menu-item" :class="{ active: currentRoute === '/settings' }" @click="navigate('/settings')">
          <i class="bi bi-gear"></i>
          <span class="sidebar-menu-text" v-show="!collapsed">设置</span>
        </li>
      </ul>
    </div>
  `,
  data() {
    return {
      currentRoute: window.location.hash.slice(1) || '/'
    };
  },
  methods: {
    navigate(route) {
      window.location.hash = route;
      this.currentRoute = route;
    }
  },
  mounted() {
    window.addEventListener('hashchange', () => {
      this.currentRoute = window.location.hash.slice(1) || '/';
    });
  }
};