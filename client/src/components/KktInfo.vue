<template>
  <div class="kkt-info">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Информация о ККТ</span>
          <el-button @click="loadKktInfo" :loading="loading">Обновить</el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="error" class="error">
        <el-alert :title="error" type="error" show-icon />
      </div>
      
      <div v-else-if="kktInfo" class="kkt-details">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="never" class="info-card">
              <template #header>
                <h3>Статус ККТ</h3>
              </template>
              <div class="info-item">
                <span class="label">Номер документа:</span>
                <span class="value">{{ kktInfo.ECRStatus?.DocumentNumber || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Код результата:</span>
                <span class="value">{{ kktInfo.ECRStatus?.ResultCode || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Описание:</span>
                <span class="value">{{ kktInfo.ECRStatus?.ResultCodeDescription || '-' }}</span>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="never" class="info-card">
              <template #header>
                <h3>Статус ФН</h3>
              </template>
              <div class="info-item">
                <span class="label">Серийный номер:</span>
                <span class="value fiscal-number">{{ kktInfo.FNStatus?.SerialNumber || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Номер ФД:</span>
                <span class="value">{{ kktInfo.FNStatus?.DocumentNumber || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Состояние ФН:</span>
                <span class="value">{{ kktInfo.FNStatus?.FNLifeState || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Состояние смены:</span>
                <span class="value">{{ kktInfo.FNStatus?.FNSessionState || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Дата:</span>
                <span class="value">{{ formatDate(kktInfo.FNStatus?.Date) }}</span>
              </div>
              <div class="info-item">
                <span class="label">Время:</span>
                <span class="value">{{ kktInfo.FNStatus?.Time || '-' }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="never" class="info-card">
              <template #header>
                <h3>Срок действия ФН</h3>
              </template>
              <div class="info-item">
                <span class="label">Дата истечения:</span>
                <span class="value expiration-date" :class="getExpirationClass(kktInfo.FNExpiration?.Date)">
                  {{ formatDate(kktInfo.FNExpiration?.Date) }}
                </span>
              </div>
              <div class="info-item">
                <span class="label">Код результата:</span>
                <span class="value">{{ kktInfo.FNExpiration?.ResultCode || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Описание:</span>
                <span class="value">{{ kktInfo.FNExpiration?.ResultCodeDescription || '-' }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <el-card shadow="never" class="info-card">
              <template #header>
                <h3>Фискализация ФН</h3>
              </template>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">ИНН:</span>
                    <span class="value">{{ kktInfo.FNFiscalization?.INN || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Рег. номер ККТ:</span>
                    <span class="value fiscal-number">{{ kktInfo.FNFiscalization?.KKTRegistrationNumber || '-' }}</span>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">Номер ФД:</span>
                    <span class="value">{{ kktInfo.FNFiscalization?.DocumentNumber || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Фискальный признак:</span>
                    <span class="value fiscal-sign">{{ kktInfo.FNFiscalization?.FiscalSign || '-' }}</span>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">Код налогообложения:</span>
                    <span class="value">{{ kktInfo.FNFiscalization?.TaxType || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Режим работы:</span>
                    <span class="value">{{ kktInfo.FNFiscalization?.WorkMode || '-' }}</span>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- Параметры текущей смены -->
        <el-row :gutter="20" v-if="sessionParams">
          <el-col :span="24">
            <el-card shadow="never" class="info-card">
              <template #header>
                <h3>Параметры текущей смены</h3>
              </template>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">Состояние смены:</span>
                    <el-tag :type="getSessionStateType(sessionParams.fn_session_state)">
                      {{ getSessionStateText(sessionParams.fn_session_state) }}
                    </el-tag>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">Номер смены:</span>
                    <span class="value">{{ sessionParams.session_number || '-' }}</span>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <span class="label">Номер чека:</span>
                    <span class="value">{{ sessionParams.receipt_number || '-' }}</span>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { logsApi } from '../api'

export default {
  name: 'KktInfo',
  data() {
    return {
      loading: false,
      error: null,
      kktInfo: null,
      sessionParams: null
    }
  },
  mounted() {
    this.loadKktInfo()
  },
  methods: {
    async loadKktInfo() {
      this.loading = true
      this.error = null
      try {
        // Загружаем основную информацию о ККТ
        const result = await logsApi.getKktInfo()
        if (result.data.status === 'success') {
          this.kktInfo = result.data.kkt_info
        } else {
          this.error = result.data.error || 'Ошибка получения данных ККТ'
        }
        
        // Загружаем параметры текущей смены
        try {
          const sessionResult = await logsApi.getFnSessionParams()
          if (sessionResult.data.status === 'success') {
            this.sessionParams = sessionResult.data.session_params
          }
        } catch (sessionError) {
          console.warn('Не удалось загрузить параметры смены:', sessionError.message)
        }
        
      } catch (error) {
        this.error = 'Ошибка: ' + error.message
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('ru-RU')
    },
    
    getExpirationClass(expirationDate) {
      if (!expirationDate) return ''
      
      const expiration = new Date(expirationDate)
      const now = new Date()
      const daysUntilExpiration = Math.ceil((expiration - now) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiration < 0) {
        return 'expired' // Просрочен
      } else if (daysUntilExpiration <= 30) {
        return 'warning' // Предупреждение (меньше 30 дней)
      } else if (daysUntilExpiration <= 90) {
        return 'caution' // Осторожность (меньше 90 дней)
      }
      return 'normal' // Нормальный срок
    },
    
    getSessionStateText(state) {
      if (state === null || state === undefined) return 'Неизвестно'
      
      switch (state) {
        case 0: return 'Смена закрыта'
        case 1: return 'Смена открыта'
        case 2: return 'Смена истекла'
        default: return `Состояние ${state}`
      }
    },
    
    getSessionStateType(state) {
      if (state === null || state === undefined) return 'info'
      
      switch (state) {
        case 0: return 'info'      // Смена закрыта
        case 1: return 'success'   // Смена открыта
        case 2: return 'warning'   // Смена истекла
        default: return 'info'
      }
    }
  }
}
</script>

<style scoped>
.loading {
  padding: 20px;
}

.error {
  margin: 20px 0;
}

.kkt-details {
  padding: 10px 0;
}

.info-card {
  margin-bottom: 0;
}

.info-card h3 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: #606266;
  min-width: 120px;
}

.value {
  color: #303133;
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
}

.fiscal-number {
  color: #409eff;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.fiscal-sign {
  color: #67c23a;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expiration-date {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.expiration-date.expired {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.expiration-date.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.expiration-date.caution {
  background-color: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.expiration-date.normal {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #c2e7b0;
}
</style>
