import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// Добавляем interceptor для отладки
api.interceptors.request.use(
  config => {
    console.log('API Request:', config.method.toUpperCase(), config.url, config.data || config.params)
    return config
  },
  error => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    console.log('API Response:', response.config.method.toUpperCase(), response.config.url, response.data)
    return response
  },
  error => {
    console.error('API Response Error:', error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API для чеков
export const checkApi = {
  cashPayment: (order) => api.post('/payment/cash', order),
  cardPayment: (order) => api.post('/payment/card', order),
  createInvoice: (order) => api.post('/invoice', order)
}

// API для ЕГАИС
export const egaisApi = {
  sendCheck: (order) => api.post('/send-egais-check', order),
  sendXmlFile: (formData) => api.post('/send-egais-xml', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// API для логов
export const logsApi = {
  getCheckLogs: (params) => api.get('/logs/checks', { params }),
  getEgaisLogs: (params) => api.get('/logs/egais', { params }),
  getStats: () => api.get('/logs/stats'),
  getKktInfo: () => api.get('/kkt-info'),
  getFnExpiration: () => api.get('/fn-expiration'),
  getFnSessionParams: () => api.get('/fn-session-params')
}

// API для печати
export const printApi = {
  printXReport: () => api.get('/print/xreport'),
  printZReport: (employee) => api.post('/print/zreport', employee),
  printKitchenMark: (data) => api.post('/print/kitchen-mark', data),
  printInvoice: (order) => api.post('/print/invoice', order)
}

// API для авторизации
export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password })
}

// API для управления пользователями
export const usersApi = {
  getUsers: () => api.get('/users'),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`)
}

// API для товаров и категорий
export const productsApi = {
  getProducts: (params) => api.get('/products', { params }),
  createProduct: (data) => api.post('/products', data),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),
  getCategories: () => api.get('/categories'),
  createCategory: (data) => api.post('/categories', data),
  updateCategory: (id, data) => api.put(`/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/categories/${id}`)
}

export default api

