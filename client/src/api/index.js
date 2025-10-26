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
  // Пробитие чека наличными
  cashPayment: (order) => api.post('/payment/cash', order),
  
  // Пробитие чека картой
  cardPayment: (order) => api.post('/payment/card', order),
  
  // Создание счета
  createInvoice: (order) => api.post('/invoice', order)
}

// API для ЕГАИС
export const egaisApi = {
  // Отправка чека в ЕГАИС
  sendCheck: (order) => api.post('/send-egais-check', order),
  
  // Отправка XML файла в ЕГАИС
  sendXmlFile: (formData) => api.post('/send-egais-xml', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// API для логов
export const logsApi = {
  // Получение логов чеков
  getCheckLogs: (params) => api.get('/logs/checks', { params }),
  
  // Получение логов ЕГАИС
  getEgaisLogs: (params) => api.get('/logs/egais', { params }),
  
  // Получение статистики
  getStats: () => api.get('/logs/stats'),
  
  // Получение информации о ККТ
  getKktInfo: () => api.get('/kkt-info'),
  
  // Получение срока действия ФН
  getFnExpiration: () => api.get('/fn-expiration'),
  
  // Получение параметров текущей смены ФН
  getFnSessionParams: () => api.get('/fn-session-params')
}

// API для печати
export const printApi = {
  // Печать X-отчета
  printXReport: () => api.get('/print/xreport'),
  
  // Печать Z-отчета
  printZReport: (employee) => api.post('/print/zreport', employee),
  
  // Печать кухонной марки
  printKitchenMark: (data) => api.post('/print/kitchen-mark', data),
  
  // Печать счета
  printInvoice: (order) => api.post('/print/invoice', order)
}

// API для авторизации
export const authApi = {
  // Вход в систему
  login: (username, password) => api.post('/auth/login', { username, password })
}

// API для управления пользователями
export const usersApi = {
  // Получить список пользователей
  getUsers: () => api.get('/users'),
  
  // Создать нового пользователя
  createUser: (userData) => api.post('/users', userData),
  
  // Обновить пользователя
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  
  // Удалить пользователя (деактивация)
  deleteUser: (userId) => api.delete(`/users/${userId}`)
}

export default api
