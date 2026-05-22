<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="layout-aside">
      <div class="logo">客房销售管理</div>
      <el-menu :default-active="activeMenu" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/orders">
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/orders/new" v-if="authStore.isEmployee || authStore.isAdmin">
          <span>录入订单</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="authStore.isAdmin">
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/logs" v-if="authStore.isAdmin">
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left"></div>
        <div class="header-right">
          <span>{{ authStore.user?.display_name }} ({{ roleLabel }})</span>
          <el-button link type="primary" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/orders')) return path.includes('/new') || path.includes('/edit') ? '/orders' : '/orders'
  return path
})

const roleLabel = computed(() => {
  const map = { admin: '管理员', finance: '财务', employee: '员工' }
  return map[authStore.role] || ''
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.layout-aside { background: #304156; }
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #434a50;
}
.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  background: #fff;
}
.header-right { display: flex; align-items: center; gap: 12px; }
.layout-main { background: #f0f2f5; padding: 20px; }
</style>
