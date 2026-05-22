<template>
  <el-card>
    <!-- Filter bar -->
    <el-form :model="filters" inline style="margin-bottom: 16px">
      <el-form-item label="订单平台">
        <el-select v-model="filters.order_platform" clearable placeholder="全部" style="width: 130px">
          <el-option label="去哪儿" value="去哪儿" />
          <el-option label="携程" value="携程" />
          <el-option label="美团" value="美团" />
          <el-option label="飞猪" value="飞猪" />
          <el-option label="同程" value="同程" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>
      <el-form-item label="预订日期">
        <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item v-if="authStore.isAdmin || authStore.isFinance" label="业务员">
        <el-select v-model="filters.salesperson" clearable placeholder="全部" style="width: 120px">
          <el-option label="全部" value="" />
          <el-option v-for="emp in employees" :key="emp.id" :label="emp.display_name" :value="emp.display_name" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.order_status" clearable placeholder="全部" style="width: 120px">
          <el-option label="未处理" value="未处理" />
          <el-option label="已确认" value="已确认" />
          <el-option label="已入住" value="已入住" />
          <el-option label="已取消" value="已取消" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchOrders">查询</el-button>
        <el-button v-if="authStore.isAdmin || authStore.isFinance" type="success" @click="handleExport">导出Excel</el-button>
      </el-form-item>
    </el-form>

    <!-- Table -->
    <el-table v-loading="loading" :data="orders" border stripe style="width: 100%">
      <el-table-column prop="order_platform" label="平台" width="80" />
      <el-table-column prop="order_number" label="订单号" width="140" />
      <el-table-column prop="room_name" label="房型" width="120" />
      <el-table-column prop="guest_name" label="入住人" width="100" />
      <el-table-column prop="salesperson" label="业务员" width="100" />
      <el-table-column prop="hotel_name" label="酒店" width="140" />
      <el-table-column prop="booking_date" label="预订日期" width="110" />
      <el-table-column prop="order_status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.order_status)" size="small">{{ row.order_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="viewOrder(row)">查看</el-button>
          <el-button v-if="canEdit(row)" link type="primary" size="small" @click="editOrder(row)">编辑</el-button>
          <el-button v-if="canDelete(row)" link type="danger" size="small" @click="deleteOrder(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 16px; display: flex; justify-content: flex-end">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchOrders" />
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const orders = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const employees = ref([])
const loading = ref(false)

const filters = reactive({
  order_platform: '',
  dateRange: [],
  salesperson: '',
  order_status: '',
})

onMounted(async () => {
  if (authStore.isAdmin || authStore.isFinance) {
    const users = await api.get('/users/')
    employees.value = users.filter(u => u.role === 'employee')
  }
  fetchOrders()
})

async function fetchOrders() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      order_platform: filters.order_platform || undefined,
      booking_date_start: filters.dateRange?.[0] || undefined,
      booking_date_end: filters.dateRange?.[1] || undefined,
      salesperson: filters.salesperson || undefined,
      order_status: filters.order_status || undefined,
    }
    const res = await api.get('/orders/', { params })
    orders.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function statusType(status) {
  const map = { '未处理': 'info', '已确认': 'warning', '已入住': 'success', '已取消': 'danger' }
  return map[status] || 'info'
}

function canEdit(row) {
  if (authStore.isAdmin) return true
  if (authStore.isEmployee) {
    const oneMonthAgo = new Date()
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
    return row.created_by === authStore.user?.id && new Date(row.created_at) >= oneMonthAgo
  }
  return false
}

function canDelete(row) {
  return canEdit(row)
}

function viewOrder(row) {
  router.push(`/orders/edit/${row.id}`)
}

function editOrder(row) {
  router.push(`/orders/edit/${row.id}`)
}

async function deleteOrder(row) {
  try {
    await ElMessageBox.confirm(`确认删除订单 ${row.order_number}？`, '提示', { type: 'warning' })
    await api.delete(`/orders/${row.id}`)
    ElMessage.success('删除成功')
    fetchOrders()
  } catch (e) {
    // Cancelled
  }
}

async function handleExport() {
  try {
    const params = {
      order_platform: filters.order_platform || undefined,
      booking_date_start: filters.dateRange?.[0] || undefined,
      booking_date_end: filters.dateRange?.[1] || undefined,
    }
    const token = localStorage.getItem('token')
    const urlParams = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v) urlParams.set(k, v) })
    const url = `/api/orders/export?${urlParams.toString()}`
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    const blob = await res.blob()
    const dlUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = dlUrl
    link.download = `orders_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(dlUrl)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}
</script>
