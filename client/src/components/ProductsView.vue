<template>
  <div>
    <el-row :gutter="20">
      <!-- Управление категориями -->
      <el-col :span="6">
        <el-card header="Категории">
            <el-button @click="addCategory" type="primary" size="small" style="width: 100%; margin-bottom: 10px;">
            <el-icon><Plus /></el-icon> Добавить категорию
          </el-button>
          
          <el-tree
            :data="categoriesTree"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            @node-click="selectCategory"
            highlight-current
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
              <span>{{ node.label }}</span>
              <span>
                <el-button
                  type="text"
                  size="mini"
                  @click.stop="editCategory(data)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button
                  type="text"
                  size="mini"
                  @click.stop="deleteCategory(data)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- Список товаров -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="clearfix">
            <span>Товары</span>
            <div style="float: right;">
              <el-button 
                style="padding: 3px 0; margin-right: 10px;" 
                type="text" 
                @click="refresh"
              >
                <el-icon><Refresh /></el-icon> Обновить
              </el-button>
              <el-button 
                style="padding: 3px 0" 
                type="text" 
                @click="addProduct"
              >
                <el-icon><Plus /></el-icon> Добавить товар
              </el-button>
            </div>
            </div>
          </template>

          <el-table :data="products" v-loading="loading" style="width: 100%">
            <el-table-column prop="name" label="Название" width="200" />
            <el-table-column prop="price" label="Цена" width="100">
              <template #default="scope">
                {{ scope.row.price }} Р
              </template>
            </el-table-column>
            <el-table-column prop="barcode" label="Штрихкод" width="120" />
            <el-table-column prop="unit" label="Ед. изм." width="80" />
            <el-table-column label="Особенности" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.is_alcohol" size="mini" type="warning">Алко</el-tag>
                <el-tag v-if="scope.row.is_marked" size="mini" type="danger">Марк.</el-tag>
                <el-tag v-if="scope.row.is_draught" size="mini" type="info">Разл.</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="max_discount" label="Макс. скидка" width="100">
              <template #default="scope">
                {{ scope.row.max_discount }}%
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="120">
              <template #default="scope">
                <el-button @click="editProduct(scope.row)" type="text" size="small">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button @click="deleteProduct(scope.row)" type="text" size="small">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="pagination.total > 0"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pagination.page"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.limit"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            style="margin-top: 20px; text-align: center;"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- Диалог создания/редактирования категории -->
    <el-dialog 
      :title="editingCategory ? 'Редактировать категорию' : 'Новая категория'"
      v-model="showCategoryForm"
      width="400px"
    >
      <el-form :model="categoryForm" label-width="120px">
        <el-form-item label="Название">
          <el-input v-model="categoryForm.name" placeholder="Введите название категории" />
        </el-form-item>
        <el-form-item label="Родительская категория">
          <el-select v-model="categoryForm.parent_id" placeholder="Выберите родительскую категорию" clearable style="width: 100%">
            <el-option 
              :label="'Корневая категория'" 
              :value="0"
            />
            <el-option 
              v-for="cat in flatCategories" 
              :key="cat.id" 
              :label="cat.displayName" 
              :value="cat.id"
              :disabled="editingCategory && cat.id === editingCategory.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Описание">
          <el-input 
            v-model="categoryForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="Введите описание категории"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCategoryForm = false">Отмена</el-button>
          <el-button type="primary" @click="saveCategory">Сохранить</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Диалог создания/редактирования товара -->
    <el-dialog 
      :title="editingProduct ? 'Редактировать товар' : 'Новый товар'"
      v-model="showProductForm"
      width="800px"
    >
      <el-form :model="productForm" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Название" required>
              <el-input v-model="productForm.name" placeholder="Название товара" />
            </el-form-item>
            <el-form-item label="Категория" required>
              <el-select v-model="productForm.category_id" placeholder="Выберите категорию" style="width: 100%">
                <el-option 
                  v-for="cat in categories" 
                  :key="cat.id" 
                  :label="cat.name" 
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Цена" required>
              <el-input-number v-model="productForm.price" :precision="2" :min="0" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Штрихкод">
              <el-input v-model="productForm.barcode" placeholder="EAN код" />
            </el-form-item>
            <el-form-item label="Legacy Path">
              <el-input v-model="productForm.legacy_path" placeholder="Путь из старой системы" />
            </el-form-item>
            <el-form-item label="Единица измерения">
              <el-input v-model="productForm.unit" placeholder="шт" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="Описание">
              <el-input 
                v-model="productForm.description" 
                type="textarea" 
                :rows="3"
                placeholder="Описание товара"
              />
            </el-form-item>
            <el-form-item label="Макс. скидка (%)">
              <el-input-number v-model="productForm.max_discount" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="НДС (%)">
              <el-input-number v-model="productForm.tax_rate" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="Особенности">
              <el-checkbox v-model="productForm.is_alcohol">Алкогольный товар</el-checkbox>
              <el-checkbox v-model="productForm.is_marked">Маркированный товар</el-checkbox>
              <el-checkbox v-model="productForm.is_draught" :disabled="!productForm.is_alcohol">Разливное</el-checkbox>
              <el-checkbox v-model="productForm.is_bottled" :disabled="!productForm.is_alcohol">Бутылочное</el-checkbox>
            </el-form-item>

            <!-- ЕГАИС поля (показываются только для алкоголя) -->
            <div v-if="productForm.is_alcohol">
              <el-form-item label="Алкокод">
                <el-input v-model="productForm.alc_code" placeholder="Код алкогольной продукции" />
              </el-form-item>
              <el-form-item label="GTIN" v-if="productForm.is_marked">
                <el-input v-model="productForm.gtin" placeholder="GTIN для маркированных товаров" />
              </el-form-item>
            </div>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showProductForm = false">Отмена</el-button>
          <el-button type="primary" @click="saveProduct">Сохранить</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api/index.js'
import { Plus, Edit, Delete, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'ProductsView',
  components: {
    Plus,
    Edit,
    Delete,
    Refresh
  },
  data() {
    return {
      loading: false,
      categories: [],
      products: [],
      selectedCategory: null,
      pagination: {
        page: 1,
        limit: 20,
        total: 0
      },
      
      // Формы
      showCategoryForm: false,
      showProductForm: false,
      editingCategory: null,
      editingProduct: null,
      
      categoryForm: {
        name: '',
        description: '',
        parent_id: null
      },
      
      productForm: {
        name: '',
        description: '',
        category_id: null,
        price: 0,
        barcode: '',
        legacy_path: '',
        unit: 'шт',
        max_discount: 100,
        tax_rate: 20,
        is_alcohol: false,
        is_marked: false,
        is_draught: false,
        is_bottled: false,
        alc_code: '',
        egais_mark_code: '',
        gtin: ''
      }
    }
  },
  
  computed: {
    // Плоский список всех категорий для выбора родительской
    flatCategories() {
      const flatten = (tree, level = 0) => {
        let result = []
        for (const cat of tree) {
          result.push({
            ...cat,
            level: level,
            displayName: '  '.repeat(level) + cat.name
          })
          if (cat.children && cat.children.length > 0) {
            result = result.concat(flatten(cat.children, level + 1))
          }
        }
        return result
      }
      return flatten(this.categoriesTree)
    },
    
    // Иерархическая структура категорий для дерева
    categoriesTree() {
      const buildTree = (categories, parentId = null) => {
        return categories
          .filter(cat => (cat.parent_id === null && parentId === null) || (cat.parent_id === parentId))
          .map(cat => ({
            id: cat.id,
            name: cat.name,
            description: cat.description,
            parent_id: cat.parent_id,
            children: buildTree(categories, cat.id)
          }))
      }
      return buildTree(this.categories)
    }
  },
  
  mounted() {
    this.loadCategories()
    this.loadProducts()
  },
  
  methods: {
    async refresh() {
      this.$message.info('Обновление данных...')
      await Promise.all([
        this.loadCategories(),
        this.loadProducts()
      ])
      this.$message.success('Данные обновлены')
    },
    
    async loadCategories() {
      try {
        const response = await api.get('/categories')
        if (response.data.status === 'success') {
          this.categories = response.data.data
          console.log('Категории загружены:', this.categories)
        } else {
          this.$message.error('Ошибка загрузки категорий: ' + response.data.message)
        }
      } catch (error) {
        console.error('Ошибка загрузки категорий:', error)
        this.$message.error('Ошибка загрузки категорий: ' + (error.response?.data?.message || error.message))
      }
    },
    
    async loadProducts() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          limit: this.pagination.limit
        }
        
        if (this.selectedCategory) {
          params.category_id = this.selectedCategory.id
        }
        
        const response = await api.get('/products', { params })
        if (response.data.status === 'success') {
          this.products = response.data.data
          this.pagination = response.data.pagination
          console.log('Товары загружены:', this.products)
        } else {
          this.$message.error('Ошибка загрузки товаров: ' + response.data.message)
        }
      } catch (error) {
        console.error('Ошибка загрузки товаров:', error)
        this.$message.error('Ошибка загрузки товаров: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
      }
    },
    
    selectCategory(category) {
      this.selectedCategory = category
      this.pagination.page = 1
      this.loadProducts()
    },
    
    // Категории
    addCategory() {
      this.editingCategory = null
      this.categoryForm = { name: '', description: '', parent_id: null }
      this.showCategoryForm = true
    },
    
    editCategory(category) {
      this.editingCategory = category
      this.categoryForm = {
        name: category.name,
        description: category.description || '',
        parent_id: category.parent_id || 0
      }
      this.showCategoryForm = true
    },
    
    async saveCategory() {
      try {
        const formData = new FormData()
        formData.append('name', this.categoryForm.name)
        if (this.categoryForm.description) {
          formData.append('description', this.categoryForm.description)
        }
        
        // Обработка parent_id
        if (this.categoryForm.parent_id !== null && this.categoryForm.parent_id !== undefined) {
          if (this.categoryForm.parent_id === 0) {
            // Корневая категория - отправляем 0 для обновления, для создания не отправляем
            if (this.editingCategory) {
              formData.append('parent_id', '0')
            }
            // При создании не отправляем parent_id, будет создана корневая категория
          } else {
            formData.append('parent_id', this.categoryForm.parent_id.toString())
          }
        }
        
        if (this.editingCategory) {
          await api.put(`/categories/${this.editingCategory.id}`, formData)
          this.$message.success('Категория обновлена')
        } else {
          await api.post('/categories', formData)
          this.$message.success('Категория создана')
        }
        
        this.showCategoryForm = false
        this.editingCategory = null
        this.categoryForm = { name: '', description: '', parent_id: null }
        this.loadCategories()
      } catch (error) {
        this.$message.error('Ошибка сохранения категории: ' + error.message)
      }
    },
    
    async deleteCategory(category) {
      try {
        await this.$confirm(`Удалить категорию "${category.name}"?`, 'Подтверждение', {
          confirmButtonText: 'Удалить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        })
        
        await api.delete(`/categories/${category.id}`)
        this.$message.success('Категория удалена')
        this.loadCategories()
        
        if (this.selectedCategory && this.selectedCategory.id === category.id) {
          this.selectedCategory = null
          this.loadProducts()
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('Ошибка удаления категории: ' + error.message)
        }
      }
    },
    
    // Товары
    addProduct() {
      this.editingProduct = null
      this.resetProductForm()
      this.showProductForm = true
    },
    
    editProduct(product) {
      this.editingProduct = product
      this.productForm = { ...product }
      this.productForm.category_id = product.category.id
      this.showProductForm = true
    },
    
    async saveProduct() {
      try {
        if (this.editingProduct) {
          await api.put(`/products/${this.editingProduct.id}`, this.productForm)
          this.$message.success('Товар обновлен')
        } else {
          await api.post('/products', this.productForm)
          this.$message.success('Товар создан')
        }
        
        this.showProductForm = false
        this.editingProduct = null
        this.resetProductForm()
        this.loadProducts()
      } catch (error) {
        this.$message.error('Ошибка сохранения товара: ' + error.message)
      }
    },
    
    async deleteProduct(product) {
      try {
        await this.$confirm(`Удалить товар "${product.name}"?`, 'Подтверждение', {
          confirmButtonText: 'Удалить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        })
        
        await api.delete(`/products/${product.id}`)
        this.$message.success('Товар удален')
        this.loadProducts()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('Ошибка удаления товара: ' + error.message)
        }
      }
    },
    
    resetProductForm() {
      this.productForm = {
        name: '',
        description: '',
        category_id: this.selectedCategory ? this.selectedCategory.id : null,
        price: 0,
        barcode: '',
        legacy_path: '',
        unit: 'шт',
        max_discount: 100,
        tax_rate: 20,
        is_alcohol: false,
        is_marked: false,
        is_draught: false,
        is_bottled: false,
        alc_code: '',
        egais_mark_code: '',
        gtin: ''
      }
    },
    
    // Пагинация
    handleSizeChange(val) {
      this.pagination.limit = val
      this.pagination.page = 1
      this.loadProducts()
    },
    
    handleCurrentChange(val) {
      this.pagination.page = val
      this.loadProducts()
    }
  },
  
  watch: {
    showProductForm(val) {
      if (val && !this.editingProduct) {
        this.resetProductForm()
      }
    },
    
    showCategoryForm(val) {
      if (!val) {
        this.editingCategory = null
        this.categoryForm = { name: '', description: '' }
      }
    }
  }
}
</script>

<style scoped>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.el-tree-node__content:hover .custom-tree-node span:last-child {
  display: inline-block;
}

.custom-tree-node span:last-child {
  display: none;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
</style>
