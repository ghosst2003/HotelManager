<template>
  <el-card>
    <template #header><span>操作日志</span></template>
    <el-form :model="filters" inline style="margin-bottom: 16px">
      <el-form-item label="操作类型">
        <el-select v-model="filters.action" clearable placeholder="全部" style="width: 130px">
          <el-option label="创建订单" value="create" />
          <el-option label="修改订单" value="update" />
          <el-option label="删除订单" value="delete" />
          <el-option label="登录" value="login" />
          <el-option label="导出" value="export" />
          <el-option label="创建用户" value="user_create" />
          <el-option label="禁用用户" value="user_disable" />
          <el-option label="启用用户" value="user_enable" />
          <el-option label="删除用户" value="user_delete" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间范围">
        <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DDTHH:mm:ss" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchLogs">查询</el-button>
      </el-form-item>
    </el-form>
    <el-table v-loading="loading" :data="logs" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ actionLabel(row.action) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="entity_type" label="类型" width="80" />
      <el-table-column prop="entity_id" label="记录ID" width="90" />
      <el-table-column label="详情" min-width="200">
        <template #default="{ row }">
          {{ JSON.stringify(row.details) }}
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
    <div style="margin-top: 16px; display: flex; justify-content: flex-end">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchLogs" />
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const filters = reactive({ action: '', dateRange: [] })

onMounted(() => fetchLogs())

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      action: filters.action || undefined,
      date_start: filters.dateRange?.[0] || undefined,
      date_end: filters.dateRange?.[1] || undefined,
    }
    const res = await api.get('/logs/', { params })
    logs.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function actionLabel(action) {
  const map = {
    create: '创建订单', update: '修改订单', delete: '删除订单',
    login: '登录', export: '导出',
    user_create: '创建用户', user_disable: '禁用用户',
    user_enable: '启用用户', user_delete: '删除用户',
  }
  return map[action] || action
}
</script>
