import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role || '')
  const isAdmin = computed(() => role.value === 'admin')
  const isFinance = computed(() => role.value === 'finance')
  const isEmployee = computed(() => role.value === 'employee')

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function setUserInfo(info) {
    user.value = info
    localStorage.setItem('user', JSON.stringify(info))
  }

  return { user, token, isLoggedIn, role, isAdmin, isFinance, isEmployee, login, logout, setUserInfo }
})
