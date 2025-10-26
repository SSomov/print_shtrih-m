<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>Авторизация</h2>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="120px">
        <el-form-item label="Имя пользователя" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="Введите имя пользователя"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item label="Пароль" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="Введите пароль"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading"
            style="width: 100%"
          >
            Войти
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="false"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script>
import { authApi } from '../api'
import { ElMessage } from 'element-plus'

export default {
  name: 'LoginForm',
  emits: ['login-success'],
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: 'Введите имя пользователя', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Введите пароль', trigger: 'blur' }
        ]
      },
      loading: false,
      errorMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        await this.$refs.loginFormRef.validate()
        
        this.loading = true
        this.errorMessage = ''
        
        const response = await authApi.login(
          this.loginForm.username,
          this.loginForm.password
        )
        
        if (response.data.status === 'success') {
          // Сохраняем токен
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('username', response.data.username)
          
          ElMessage.success('Успешный вход')
          this.$emit('login-success')
        } else {
          this.errorMessage = response.data.message || 'Ошибка авторизации'
        }
      } catch (error) {
        console.error('Login error:', error)
        this.errorMessage = error.response?.data?.message || 'Ошибка подключения к серверу'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.login-card h2 {
  margin: 0;
  text-align: center;
  color: #409EFF;
}
</style>
