<template>
  <div class="egais-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Отправка в ЕГАИС</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px" @submit.prevent="submitEgais">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Номер заказа">
              <el-input v-model="form.num" placeholder="Введите номер заказа" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Сотрудник ФИО">
              <el-input v-model="form.employee_fio" placeholder="ФИО сотрудника" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="ИНН сотрудника">
              <el-input v-model="form.employee_inn" placeholder="ИНН сотрудника" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Должность">
              <el-input v-model="form.employee_pos" placeholder="Должность" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">Алкогольные товары</el-divider>
        
        <div v-for="(item, index) in form.products" :key="index" class="product-item">
          <el-card>
            <el-row :gutter="10">
              <el-col :span="6">
                <el-form-item :label="`Товар ${index + 1}`">
                  <el-input v-model="item.name" placeholder="Название товара" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="Количество">
                  <el-input-number v-model="item.kolvo" :min="0.01" :precision="2" @change="item.kolvo = String(item.kolvo)" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="Цена">
                  <el-input-number v-model="item.price" :min="0" :precision="2" @change="item.price = String(item.price)" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="GTIN">
                  <el-input v-model="item.GTIN" placeholder="GTIN код" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="Алкокод">
                  <el-input v-model="item.alc_code" placeholder="Алкокод" />
                </el-form-item>
              </el-col>
              <el-col :span="2">
                <el-button type="danger" @click="removeProduct(index)">×</el-button>
              </el-col>
            </el-row>
            
            <el-row :gutter="10">
              <el-col :span="8">
                <el-form-item label="QR код маркировки">
                  <el-input v-model="item.qr" placeholder="QR код маркировки" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Код марки ЕГАИС">
                  <el-input v-model="item.egais_mark_code" placeholder="Код марки для ЕГАИС" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="ID ЕГАИС">
                  <el-input v-model="item.egais_id" placeholder="Идентификатор ЕГАИС" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>
        </div>
        
        <el-button type="primary" @click="addProduct">Добавить алкогольный товар</el-button>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="submitEgais" :loading="loading">
            Отправить в ЕГАИС
          </el-button>
          <el-button @click="resetForm">Сбросить</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { egaisApi } from '../api'

export default {
  name: 'EgaisForm',
  data() {
    return {
      loading: false,
      form: {
        num: '',
        typedoc: 'check',
        hall: '',
        table: '',
        create: new Date().toLocaleString('ru-RU'),
        waiter: '',
        employee_fio: '',
        employee_inn: '',
        employee_pos: '',
        alldiscount: '0',
        products: [
          {
            name: '',
            kolvo: '1',
            price: '0',
            GTIN: '',
            alc_code: '',
            qr: '',
            egais_mark_code: '',
            egais_id: '',
            mark: '1' // Всегда маркированные для ЕГАИС
          }
        ]
      }
    }
  },
  methods: {
    addProduct() {
      this.form.products.push({
        name: '',
        kolvo: 1,
        price: 0,
        GTIN: '',
        alc_code: '',
        qr: '',
        egais_mark_code: '',
        egais_id: '',
        mark: '1'
      })
    },
    removeProduct(index) {
      if (this.form.products.length > 1) {
        this.form.products.splice(index, 1)
      }
    },
    async submitEgais() {
      this.loading = true
      try {
        const result = await egaisApi.sendCheck(this.form)
        
        if (result.data.message) {
          this.$message.success('ЕГАИС: ' + result.data.message)
          this.$emit('egais-sent', result.data)
        } else if (result.data.error) {
          this.$message.error('Ошибка: ' + result.data.error)
        }
      } catch (error) {
        this.$message.error('Ошибка: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    resetForm() {
      this.form = {
        num: '',
        typedoc: 'check',
        hall: '',
        table: '',
        create: new Date().toLocaleString('ru-RU'),
        waiter: '',
        employee_fio: '',
        employee_inn: '',
        employee_pos: '',
        alldiscount: '0',
        products: [
          {
            name: '',
            kolvo: '1',
            price: '0',
            GTIN: '',
            alc_code: '',
            qr: '',
            egais_mark_code: '',
            egais_id: '',
            mark: '1'
          }
        ]
      }
    }
  }
}
</script>

<style scoped>
.product-item {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
