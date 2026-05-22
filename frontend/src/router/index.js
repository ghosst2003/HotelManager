import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/orders' },
      { path: 'orders', component: () => import('@/views/OrderList.vue') },
      { path: 'orders/new', component: () => import('@/views/OrderForm.vue') },
      { path: 'orders/edit/:id', component: () => import('@/views/OrderForm.vue') },
      { path: 'users', component: () => import('@/views/UserManagement.vue'), meta: { requiresAdmin: true } },
      { path: 'logs', component: () => import('@/views/OperationLog.vue'), meta: { requiresAdmin: true } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
  if (to.meta.guest && auth.isLoggedIn) return '/'
  if (to.meta.requiresAdmin && !auth.isAdmin) return '/'
})

export default router
