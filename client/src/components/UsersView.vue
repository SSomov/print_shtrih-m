<template>
  <div>
    <el-card>
      <template #header>
        <div class="clearfix">
          <span>Управление пользователями</span>
          <el-button 
            style="float: right; padding: 3px 0" 
            type="primary" 
            @click="showAddDialog"
          >
            <el-icon><Plus /></el-icon> Добавить пользователя
          </el-button>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="Имя пользователя" width="200" />
        <el-table-column label="Статус" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.is_active" type="success">Активен</el-tag>
            <el-tag v-else type="info">Деактивирован</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Дата создания" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Действия" width="150">
          <template #default="scope">
            <el-button @click="editUser(scope.row)" type="text" size="small">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button 
              @click="deleteUser(scope.row)" 
              type="text" 
              size="small"
              :disabled="!scope.row.is_active"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Диалог создания/редактирования пользователя -->
    <el-dialog
      :title="editMode ? 'Редактировать пользователя' : 'Добавить пользователя'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="150px">
        <el-form-item label="Имя пользователя" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        
        <el-form-item 
          :label="editMode ? 'Новый пароль' : 'Пароль'" 
          prop="password"
          :required="!editMode"
        >
          <el-input 
            v-model="userForm.password" 
            type="password" 
            show-password
            :placeholder="editMode ? 'Оставьте пустым, чтобы не менять' : ''"
          />
        </el-form-item>
        
        <el-form-item label="Статус">
          <el-switch 
            v-model="userForm.is_active" 
            active-text="Активен"
            inactive-text="Деактивирован"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Отмена</el-button>
          <el-button type="primary" @click="saveUser">Сохранить</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { usersApi } from '../api'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'UsersView',
  components: {
    Plus,
    Edit,
    Delete
  },
  data() {
    // Валидация пароля при создании
    const validatePassword = (rule, value, callback) => {
      if (!this.editMode && !value) {
        callback(new Error('Пароль обязателен при создании'))
      } else {
        callback()
      }
    }

    return {
      users: [],
      loading: false,
      dialogVisible: false,
      editMode: false,
      userForm: {
        username: '',
        password: '',
        is_active: true
      },
      rules: {
        username: [
          { required: true, message: 'Введите имя пользователя', trigger: 'blur' }
        ],
        password: [
          { validator: validatePassword, trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    console.log('UsersView mounted')
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        console.log('Загрузка пользователей...')
        const response = await usersApi.getUsers()
        console.log('Ответ API:', response)
        this.users = response.data.data
        console.log('Пользователи загружены:', this.users)
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
        ElMessage.error('Ошибка загрузки пользователей: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
      }
    },
    
    showAddDialog() {
      this.editMode = false
      this.userForm = {
        username: '',
        password: '',
        is_active: true
      }
      this.dialogVisible = true
    },
    
    editUser(user) {
      this.editMode = true
      this.userForm = {
        id: user.id,
        username: user.username,
        password: '',
        is_active: user.is_active
      }
      this.dialogVisible = true
    },
    
    async saveUser() {
      try {
        await this.$refs.userFormRef.validate()
        
        const userData = {
          username: this.userForm.username,
          is_active: this.userForm.is_active
        }
        
        // Добавляем пароль только если он указан
        if (this.userForm.password) {
          userData.password = this.userForm.password
        }
        
        if (this.editMode) {
          await usersApi.updateUser(this.userForm.id, userData)
          ElMessage.success('Пользователь обновлен')
        } else {
          await usersApi.createUser(userData)
          ElMessage.success('Пользователь создан')
        }
        
        this.dialogVisible = false
        await this.loadUsers()
      } catch (error) {
        if (error.errors) {
          // Ошибки валидации формы
          return
        }
        ElMessage.error('Ошибка сохранения: ' + error.message)
      }
    },
    
    async deleteUser(user) {
      try {
        await ElMessageBox.confirm(
          `Вы уверены, что хотите деактивировать пользователя "${user.username}"?`,
          'Подтверждение',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Отмена',
            type: 'warning'
          }
        )
        
        await usersApi.deleteUser(user.id)
        ElMessage.success('Пользователь деактивирован')
        await this.loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('Ошибка удаления: ' + error.message)
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
