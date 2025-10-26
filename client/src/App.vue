<template>
  <div id="app">
    <!-- Форма авторизации -->
    <LoginForm v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    
    <!-- Основное приложение -->
    <el-container v-else>
      <el-header>
        <div class="header-left">
          <Logo />
          <span class="app-title">Ресторан</span>
        </div>
        <el-menu mode="horizontal" :default-active="activeTab" @select="handleMenuSelect" class="main-menu">
          <el-menu-item index="checks">
            <el-icon><Document /></el-icon>
            <span>Чеки</span>
          </el-menu-item>
          <el-menu-item index="egais">
            <el-icon><Box /></el-icon>
            <span>ЕГАИС</span>
          </el-menu-item>
          <el-menu-item index="products">
            <el-icon><ShoppingBag /></el-icon>
            <span>Товары</span>
          </el-menu-item>
          <el-menu-item index="kkt">
            <el-icon><Monitor /></el-icon>
            <span>ККТ</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><User /></el-icon>
            <span>Пользователи</span>
          </el-menu-item>
          <el-menu-item index="logs">
            <el-icon><Document /></el-icon>
            <span>Логи</span>
          </el-menu-item>
          <el-menu-item index="stats">
            <el-icon><DataAnalysis /></el-icon>
            <span>Статистика</span>
          </el-menu-item>
        </el-menu>
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-button size="small" @click="handleLogout" type="danger" plain>Выход</el-button>
        </div>
      </el-header>
      
      <el-main>
        <CheckForm v-if="activeTab === 'checks'" @check-created="handleCheckCreated" />
        <EgaisForm v-if="activeTab === 'egais'" @egais-sent="handleEgaisSent" />
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
import Logo from './components/Logo.vue'
import { ElMessage } from 'element-plus'
import { Document, Box, ShoppingBag, Monitor, User, DataAnalysis } from '@element-plus/icons-vue'

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
    LoginForm,
    Logo,
    Document,
    Box,
    ShoppingBag,
    Monitor,
    User,
    DataAnalysis
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
  padding: 0 15px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: 10px;
}

.username {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.main-menu {
  flex: 1;
  min-width: 0;
  max-width: calc(100vw - 400px);
  overflow-x: auto;
}

.main-menu .el-menu-item {
  padding: 0 12px;
  font-size: 14px;
}

.main-menu .el-icon {
  margin-right: 4px;
}

.el-main {
  padding: 20px;
}

/* Скрываем scrollbar для menu */
.main-menu::-webkit-scrollbar {
  height: 0;
}

.main-menu {
  scrollbar-width: none;
}
</style>
