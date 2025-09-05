<template>
  <div class="stats-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Статистика</span>
          <el-button @click="loadStats">Обновить</el-button>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-row :gutter="20" v-if="stats">
          <el-col :span="12">
            <el-card class="stats-card">
              <template #header>
                <span>Чеки</span>
              </template>
              <div class="stats-content">
                <div class="stat-item">
                  <span class="stat-label">Всего чеков:</span>
                  <el-tag type="info" size="large">{{ stats.checks.total }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Успешно:</span>
                  <el-tag type="success" size="large">{{ stats.checks.success }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Ошибки:</span>
                  <el-tag type="danger" size="large">{{ stats.checks.error }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Процент успеха:</span>
                  <el-tag :type="getSuccessRateType(stats.checks)" size="large">
                    {{ getSuccessRate(stats.checks) }}%
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="stats-card">
              <template #header>
                <span>ЕГАИС</span>
              </template>
              <div class="stats-content">
                <div class="stat-item">
                  <span class="stat-label">Всего отправок:</span>
                  <el-tag type="info" size="large">{{ stats.egais.total }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Успешно:</span>
                  <el-tag type="success" size="large">{{ stats.egais.success }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Ошибки:</span>
                  <el-tag type="danger" size="large">{{ stats.egais.error }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Сохранено:</span>
                  <el-tag type="warning" size="large">{{ stats.egais.saved }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Процент успеха:</span>
                  <el-tag :type="getSuccessRateType(stats.egais)" size="large">
                    {{ getSuccessRate(stats.egais) }}%
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <div v-if="!stats && !loading" class="no-data">
          <el-empty description="Нет данных для отображения" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { logsApi } from '../api'

export default {
  name: 'StatsView',
  data() {
    return {
      loading: false,
      stats: null
    }
  },
  mounted() {
    this.loadStats()
  },
  methods: {
    async loadStats() {
      this.loading = true
      try {
        const result = await logsApi.getStats()
        if (result.data.status === 'success') {
          this.stats = result.data
        } else {
          this.$message.error('Ошибка загрузки статистики')
        }
      } catch (error) {
        this.$message.error('Ошибка: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    getSuccessRate(data) {
      if (data.total === 0) return 0
      return Math.round((data.success / data.total) * 100)
    },
    
    getSuccessRateType(data) {
      const rate = this.getSuccessRate(data)
      if (rate >= 90) return 'success'
      if (rate >= 70) return 'warning'
      return 'danger'
    }
  }
}
</script>

<style scoped>
.stats-card {
  height: 100%;
}

.stats-content {
  padding: 10px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.stat-label {
  font-weight: 500;
  color: #606266;
}

.no-data {
  text-align: center;
  padding: 40px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
