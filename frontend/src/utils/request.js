import axios from 'axios'
import { message } from 'ant-design-vue'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器：自动附加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('[Request]', config.url, 'Token:', token ? '有' : '无')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理 401
request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const currentPath = router.currentRoute.value.path
      if (currentPath !== '/login') {
        localStorage.removeItem('token')
        message.error('登录已过期，请重新登录')
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default request
