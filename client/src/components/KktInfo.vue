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
      kktInfo: null
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
        const result = await logsApi.getKktInfo()
        if (result.data.status === 'success') {
          this.kktInfo = result.data.kkt_info
        } else {
          this.error = result.data.error || 'Ошибка получения данных ККТ'
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
</style>
