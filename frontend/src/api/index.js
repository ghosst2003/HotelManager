import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (err.response?.status === 403) {
      ElMessage.error(err.response.data?.detail || '权限不足')
    } else if (err.response?.status === 404) {
      ElMessage.error('资源不存在')
    } else {
      ElMessage.error(err.response?.data?.detail || '请求失败')
    }
    return Promise.reject(err)
  }
)

export default api
