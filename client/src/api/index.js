import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

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

export default api
