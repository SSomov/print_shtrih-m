<template>
  <div class="egais-xml-upload-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Отправка EGAIS XML документа</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="150px" @submit.prevent="submitXml">
        <el-form-item label="XML файл">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".xml"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Перетащите XML файл сюда или <em>нажмите для выбора</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Поддерживаются только XML файлы (например: egais_xml_20250912_102558.xml)
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item v-if="selectedFile" label="Выбранный файл">
          <el-tag type="success" size="large">
            <el-icon><document /></el-icon>
            {{ selectedFile.name }}
          </el-tag>
        </el-form-item>
        
        <el-form-item label="Описание">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="Описание отправляемого документа (необязательно)"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitXml" 
            :loading="loading"
            :disabled="!selectedFile"
          >
            <el-icon><upload /></el-icon>
            Отправить в EGAIS
          </el-button>
          <el-button @click="resetForm">
            <el-icon><refresh /></el-icon>
            Сбросить
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- Результат отправки -->
      <el-card v-if="result" class="result-card" :class="result.status">
        <template #header>
          <div class="result-header">
            <el-icon v-if="result.status === 'success'"><success-filled /></el-icon>
            <el-icon v-else-if="result.status === 'error'"><circle-close-filled /></el-icon>
            <el-icon v-else><warning-filled /></el-icon>
            <span>{{ result.status === 'success' ? 'Успешно отправлено' : 'Ошибка отправки' }}</span>
          </div>
        </template>
        
        <div v-if="result.message" class="result-message">
          <strong>Сообщение:</strong> {{ result.message }}
        </div>
        
        <div v-if="result.xml_file" class="result-file">
          <strong>XML файл:</strong> {{ result.xml_file }}
        </div>
        
        <div v-if="result.saved_file" class="result-file">
          <strong>Ответ сохранен в:</strong> {{ result.saved_file }}
        </div>
        
        <div v-if="result.qr_code" class="result-qr">
          <strong>QR код:</strong> 
          <el-tag type="success">{{ result.qr_code }}</el-tag>
        </div>
        
        <div v-if="result.egais_response" class="result-response">
          <el-collapse>
            <el-collapse-item title="Ответ ЕГАИС" name="response">
              <pre>{{ result.egais_response }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script>
import { egaisApi } from '../api'
import { 
  UploadFilled, 
  Document, 
  Upload, 
  Refresh, 
  SuccessFilled, 
  CircleCloseFilled, 
  WarningFilled 
} from '@element-plus/icons-vue'

export default {
  name: 'EgaisXmlUploadForm',
  components: {
    UploadFilled,
    Document,
    Upload,
    Refresh,
    SuccessFilled,
    CircleCloseFilled,
    WarningFilled
  },
  data() {
    return {
      loading: false,
      selectedFile: null,
      form: {
        description: ''
      },
      result: null
    }
  },
  methods: {
    handleFileChange(file) {
      if (file.raw && file.raw.type === 'text/xml' || file.name.endsWith('.xml')) {
        this.selectedFile = file.raw
        this.result = null
      } else {
        this.$message.error('Пожалуйста, выберите XML файл')
        this.$refs.uploadRef.clearFiles()
      }
    },
    
    handleFileRemove() {
      this.selectedFile = null
      this.result = null
    },
    
    async submitXml() {
      if (!this.selectedFile) {
        this.$message.error('Пожалуйста, выберите XML файл')
        return
      }
      
      this.loading = true
      this.result = null
      
      try {
        const formData = new FormData()
        formData.append('xml_file', this.selectedFile)
        formData.append('description', this.form.description)
        
        const response = await egaisApi.sendXmlFile(formData)
        
        if (response.data.error) {
          this.result = {
            status: 'error',
            message: response.data.error
          }
          this.$message.error('Ошибка отправки: ' + response.data.error)
        } else {
          this.result = {
            status: 'success',
            message: response.data.message,
            xml_file: response.data.xml_file,
            saved_file: response.data.saved_file,
            qr_code: response.data.qr_code,
            egais_response: response.data.egais_response
          }
          this.$message.success('XML документ успешно отправлен в EGAIS')
        }
      } catch (error) {
        this.result = {
          status: 'error',
          message: error.response?.data?.error || error.message
        }
        this.$message.error('Ошибка: ' + (error.response?.data?.error || error.message))
      } finally {
        this.loading = false
      }
    },
    
    resetForm() {
      this.selectedFile = null
      this.form.description = ''
      this.result = null
      this.$refs.uploadRef.clearFiles()
    }
  }
}
</script>

<style scoped>
.egais-xml-upload-form {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.result-card {
  margin-top: 20px;
}

.result-card.success {
  border-left: 4px solid #67c23a;
}

.result-card.error {
  border-left: 4px solid #f56c6c;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.result-message,
.result-file,
.result-qr {
  margin-bottom: 10px;
}

.result-response {
  margin-top: 15px;
}

.result-response pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 7px;
}

.el-tag {
  margin-left: 8px;
}
</style>
