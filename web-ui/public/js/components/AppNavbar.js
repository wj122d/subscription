// 导航栏组件
export const AppNavbar = {
  props: ['title', 'sidebarCollapsed'],
  template: `
    <div class="top-navbar">
      <button class="navbar-toggle" @click="$emit('toggle-sidebar')">
        <i class="bi" :class="sidebarCollapsed ? 'bi-list' : 'bi-x'"></i>
      </button>
      <div class="navbar-title">{{ title }}</div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="toggleDarkMode">
          <i class="bi" :class="isDarkMode ? 'bi-sun' : 'bi-moon'"></i>
        </button>
      </div>
    </div>
  `,
  data() {
    return {
      isDarkMode: false
    };
  },
  methods: {
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      document.body.classList.toggle('dark-mode', this.isDarkMode);
    }
  }
};