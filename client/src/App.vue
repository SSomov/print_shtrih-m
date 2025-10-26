<template>
  <div id="app">
    <!-- Форма авторизации -->
    <LoginForm v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    
    <!-- Основное приложение -->
    <el-container v-else>
      <el-header>
        <div class="header-left">
          <h1>Print Shtrih Client</h1>
        </div>
        <el-menu mode="horizontal" :default-active="activeTab" @select="handleMenuSelect">
          <el-menu-item index="checks">Чеки</el-menu-item>
          <el-menu-item index="egais">ЕГАИС</el-menu-item>
          <el-menu-item index="egais-xml">ЕГАИС XML</el-menu-item>
          <el-menu-item index="products">Товары</el-menu-item>
          <el-menu-item index="kkt">ККТ</el-menu-item>
          <el-menu-item index="users">Пользователи</el-menu-item>
          <el-menu-item index="logs">Логи</el-menu-item>
          <el-menu-item index="stats">Статистика</el-menu-item>
        </el-menu>
        <div class="header-right">
          <span style="margin-right: 10px;">{{ username }}</span>
          <el-button size="small" @click="handleLogout">Выход</el-button>
        </div>
      </el-header>
      
      <el-main>
        <CheckForm v-if="activeTab === 'checks'" @check-created="handleCheckCreated" />
        <EgaisForm v-if="activeTab === 'egais'" @egais-sent="handleEgaisSent" />
        <EgaisXmlUploadForm v-if="activeTab === 'egais-xml'" />
        <ProductsView v-if="activeTab === 'products'" />
        <KktInfo v-if="activeTab === 'kkt'" />
        <UsersView v-if="activeTab === 'users'" />
        <LogsView v-if="activeTab === 'logs'" />
        <StatsView v-if="activeTab === 'stats'" />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import CheckForm from './components/CheckForm.vue'
import EgaisForm from './components/EgaisForm.vue'
import EgaisXmlUploadForm from './components/EgaisXmlUploadForm.vue'
import ProductsView from './components/ProductsView.vue'
import KktInfo from './components/KktInfo.vue'
import UsersView from './components/UsersView.vue'
import LogsView from './components/LogsView.vue'
import StatsView from './components/StatsView.vue'
import LoginForm from './components/LoginForm.vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'App',
  components: {
    CheckForm,
    EgaisForm,
    EgaisXmlUploadForm,
    ProductsView,
    KktInfo,
    UsersView,
    LogsView,
    StatsView,
    LoginForm
  },
  data() {
    return {
      activeTab: 'checks',
      isAuthenticated: false,
      username: ''
    }
  },
  mounted() {
    // Проверяем, есть ли сохраненный токен
    const token = localStorage.getItem('token')
    const savedUsername = localStorage.getItem('username')
    
    if (token && savedUsername) {
      this.isAuthenticated = true
      this.username = savedUsername
    }
  },
  methods: {
    handleMenuSelect(key) {
      this.activeTab = key
    },
    handleCheckCreated(result) {
      this.$message.success('Чек создан: ' + result.message)
    },
    handleEgaisSent(result) {
      this.$message.success('ЕГАИС: ' + result.message)
    },
    handleLoginSuccess() {
      this.isAuthenticated = true
      this.username = localStorage.getItem('username')
      ElMessage.success('Добро пожаловать!')
    },
    handleLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.isAuthenticated = false
      this.username = ''
      this.activeTab = 'checks'
      ElMessage.success('Вы вышли из системы')
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-header h1 {
  margin: 0;
  margin-right: 20px;
}

.el-main {
  padding: 20px;
}
</style>
