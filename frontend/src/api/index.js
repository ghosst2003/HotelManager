import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useAuthStore } from '@/store/auth'

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
      const auth = useAuthStore()
      auth.logout()
      ElMessage.error('登录已过期，请重新登录')
      router.replace('/login')
    } else if (err.response?.status === 403) {
      ElMessage.error(err.response.data?.detail || '权限不足')
    } else if (err.response?.status === 404) {
      ElMessage.error('资源不存在')
    } else if (err.response?.status === 422) {
      const errors = err.response.data?.detail
      if (Array.isArray(errors)) {
        ElMessage.error(errors.map(e => e.msg || e.message).join('；'))
      } else if (typeof errors === 'string') {
        ElMessage.error(errors)
      } else {
        ElMessage.error('数据格式错误')
      }
    } else {
      ElMessage.error(err.response?.data?.detail || '请求失败')
    }
    return Promise.reject(err)
  }
)

export default api
