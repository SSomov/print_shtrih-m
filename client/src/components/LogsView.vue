<template>
  <div class="logs-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Просмотр логов</span>
          <el-button @click="refreshLogs">Обновить</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="Логи чеков" name="checks">
          <div class="filters">
            <el-select v-model="checkStatus" placeholder="Статус" @change="loadCheckLogs">
              <el-option label="Все" value="" />
              <el-option label="Успешно" value="success" />
              <el-option label="Ошибка" value="error" />
            </el-select>
            <el-input-number v-model="checkPageSize" :min="10" :max="100" @change="loadCheckLogs" />
          </div>
          
          <el-table :data="checkLogs" v-loading="checkLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="timestamp" label="Время" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Статус" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="Сообщение" />
            <el-table-column prop="result_code" label="Код результата" width="120" />
            <el-table-column prop="document_number" label="Номер чека" width="120">
              <template #default="scope">
                <span v-if="scope.row.document_number">{{ scope.row.document_number }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="fiscal_sign" label="Фискальный признак" width="150">
              <template #default="scope">
                <span v-if="scope.row.fiscal_sign" class="fiscal-sign">{{ scope.row.fiscal_sign }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100">
              <template #default="scope">
                <el-button size="small" @click="viewCheckDetails(scope.row)">Детали</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-pagination
            v-model:current-page="checkPage"
            :page-size="checkPageSize"
            :total="checkTotal"
            @current-change="loadCheckLogs"
            layout="total, prev, pager, next"
          />
        </el-tab-pane>
        
        <el-tab-pane label="Логи ЕГАИС" name="egais">
          <div class="filters">
            <el-select v-model="egaisStatus" placeholder="Статус" @change="loadEgaisLogs">
              <el-option label="Все" value="" />
              <el-option label="Успешно" value="success" />
              <el-option label="Ошибка" value="error" />
              <el-option label="Сохранено" value="saved" />
            </el-select>
            <el-input-number v-model="egaisPageSize" :min="10" :max="100" @change="loadEgaisLogs" />
          </div>
          
          <el-table :data="egaisLogs" v-loading="egaisLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="timestamp" label="Время" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Статус" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="qr_code" label="QR код" width="150">
              <template #default="scope">
                <span v-if="scope.row.qr_code" class="qr-code">{{ scope.row.qr_code.substring(0, 15) }}...</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="sign" label="Подпись" width="120">
              <template #default="scope">
                <span v-if="scope.row.sign" class="sign-code">{{ scope.row.sign.substring(0, 12) }}...</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100">
              <template #default="scope">
                <el-button size="small" @click="viewEgaisDetails(scope.row)">Детали</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-pagination
            v-model:current-page="egaisPage"
            :page-size="egaisPageSize"
            :total="egaisTotal"
            @current-change="loadEgaisLogs"
            layout="total, prev, pager, next"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- Диалог деталей -->
    <el-dialog v-model="detailsVisible" :title="detailsTitle" width="80%">
      <pre class="details-content">{{ detailsContent }}</pre>
    </el-dialog>
  </div>
</template>

<script>
import { logsApi } from '../api'

export default {
  name: 'LogsView',
  data() {
    return {
      activeTab: 'checks',
      checkLogs: [],
      checkLoading: false,
      checkPage: 1,
      checkPageSize: 20,
      checkTotal: 0,
      checkStatus: '',
      egaisLogs: [],
      egaisLoading: false,
      egaisPage: 1,
      egaisPageSize: 20,
      egaisTotal: 0,
      egaisStatus: '',
      detailsVisible: false,
      detailsTitle: '',
      detailsContent: ''
    }
  },
  mounted() {
    this.loadCheckLogs()
  },
  methods: {
    async loadCheckLogs() {
      this.checkLoading = true
      try {
        const params = {
          page: this.checkPage,
          limit: this.checkPageSize
        }
        if (this.checkStatus) {
          params.status = this.checkStatus
        }
        
        const result = await logsApi.getCheckLogs(params)
        if (result.data.status === 'success') {
          this.checkLogs = result.data.data
          this.checkTotal = result.data.pagination.total
        } else {
          this.$message.error('Ошибка загрузки логов чеков')
        }
      } catch (error) {
        this.$message.error('Ошибка: ' + error.message)
      } finally {
        this.checkLoading = false
      }
    },
    
    async loadEgaisLogs() {
      this.egaisLoading = true
      try {
        const params = {
          page: this.egaisPage,
          limit: this.egaisPageSize
        }
        if (this.egaisStatus) {
          params.status = this.egaisStatus
        }
        
        const result = await logsApi.getEgaisLogs(params)
        if (result.data.status === 'success') {
          this.egaisLogs = result.data.data
          this.egaisTotal = result.data.pagination.total
        } else {
          this.$message.error('Ошибка загрузки логов ЕГАИС')
        }
      } catch (error) {
        this.$message.error('Ошибка: ' + error.message)
      } finally {
        this.egaisLoading = false
      }
    },
    
    handleTabClick(tab) {
      if (tab.name === 'egais' && this.egaisLogs.length === 0) {
        this.loadEgaisLogs()
      }
    },
    
    viewCheckDetails(row) {
      this.detailsTitle = `Детали чека #${row.id}`
      this.detailsContent = JSON.stringify(row, null, 2)
      this.detailsVisible = true
    },
    
    viewEgaisDetails(row) {
      this.detailsTitle = `Детали ЕГАИС #${row.id}`
      this.detailsContent = JSON.stringify(row, null, 2)
      this.detailsVisible = true
    },
    
    refreshLogs() {
      if (this.activeTab === 'checks') {
        this.loadCheckLogs()
      } else {
        this.loadEgaisLogs()
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('ru-RU')
    },
    
    getStatusType(status) {
      switch (status) {
        case 'success': return 'success'
        case 'error': return 'danger'
        case 'saved': return 'warning'
        default: return 'info'
      }
    }
  }
}
</script>

<style scoped>
.filters {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.details-content {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}

.qr-code {
  font-family: monospace;
  font-size: 12px;
}

.sign-code {
  font-family: monospace;
  font-size: 11px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 3px;
}

.fiscal-sign {
  font-family: monospace;
  font-size: 11px;
  color: #409eff;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
