<template>
  <div class="check-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Пробитие чека</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px" @submit.prevent="submitCheck">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Номер заказа">
              <el-input v-model="form.num" placeholder="Введите номер заказа" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Тип документа">
              <el-select v-model="form.typedoc" placeholder="Тип документа">
                <el-option label="Чек" value="check" />
                <el-option label="Возврат" value="return" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Тип оплаты">
              <el-select v-model="paymentType" placeholder="Выберите тип оплаты">
                <el-option label="Наличные" value="cash" />
                <el-option label="Карта" value="card" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Зал">
              <el-input v-model="form.hall" placeholder="Номер зала" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Стол">
              <el-input v-model="form.table" placeholder="Номер стола" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Официант">
              <el-input v-model="form.waiter" placeholder="Имя официанта" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Сотрудник ФИО">
              <el-input v-model="form.employee_fio" placeholder="ФИО сотрудника" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="ИНН сотрудника">
              <el-input v-model="form.employee_inn" placeholder="ИНН сотрудника" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Должность">
              <el-input v-model="form.employee_pos" placeholder="Должность" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Общая скидка %">
              <el-input-number v-model="form.alldiscount" :min="0" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">Товары</el-divider>
        
        <div v-for="(item, index) in form.products" :key="index" class="product-item">
          <el-card>
            <el-row :gutter="10">
              <el-col :span="8">
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
                <el-form-item label="Маркировка">
                  <el-switch v-model="item.mark" active-value="1" inactive-value="0" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-button type="danger" @click="removeProduct(index)">Удалить</el-button>
              </el-col>
            </el-row>
            
            <el-row v-if="item.mark === '1'" :gutter="10">
              <el-col :span="8">
                <el-form-item label="GTIN">
                  <el-input v-model="item.GTIN" placeholder="GTIN код" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="QR код">
                  <el-input v-model="item.qr" placeholder="QR код маркировки" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Алкокод">
                  <el-input v-model="item.alc_code" placeholder="Алкокод для ЕГАИС" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>
        </div>
        
        <el-button type="primary" @click="addProduct">Добавить товар</el-button>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="submitCheck" :loading="loading">
            Пробить чек
          </el-button>
          <el-button @click="resetForm">Сбросить</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { checkApi } from '../api'

export default {
  name: 'CheckForm',
  data() {
    return {
      loading: false,
      paymentType: 'cash',
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
            mark: '0',
            GTIN: '',
            qr: '',
            alc_code: '',
            egais_mark_code: ''
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
        mark: '0',
        GTIN: '',
        qr: '',
        alc_code: '',
        egais_mark_code: ''
      })
    },
    removeProduct(index) {
      if (this.form.products.length > 1) {
        this.form.products.splice(index, 1)
      }
    },
    async submitCheck() {
      this.loading = true
      try {
        let result
        if (this.paymentType === 'cash') {
          result = await checkApi.cashPayment(this.form)
        } else {
          result = await checkApi.cardPayment(this.form)
        }
        
        if (result.data.status === 'success') {
          this.$message.success('Чек успешно пробит!')
          this.$emit('check-created', result.data)
        } else {
          this.$message.error('Ошибка: ' + result.data.message)
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
            mark: '0',
            GTIN: '',
            qr: '',
            alc_code: '',
            egais_mark_code: ''
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
