<template>
  <el-card>
    <template #header>
      <span>用户管理</span>
      <el-button type="primary" size="small" style="float: right" @click="showCreateDialog = true">+ 新建用户</el-button>
    </template>
    <el-table v-loading="loading" :data="users" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="display_name" label="姓名" width="120" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="roleType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link :type="row.is_active ? 'warning' : 'success'" size="small" @click="toggleUser(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button link type="danger" size="small" @click="deleteUser(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- Create dialog -->
  <el-dialog v-model="showCreateDialog" title="新建用户" width="400px">
    <el-form :model="newUser" :rules="newRules" ref="newFormRef" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="newUser.username" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="newUser.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="姓名" prop="display_name">
        <el-input v-model="newUser.display_name" />
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="newUser.role" style="width: 100%">
          <el-option label="员工" value="employee" />
          <el-option label="财务" value="finance" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCreateDialog = false">取消</el-button>
      <el-button type="primary" @click="handleCreate">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const users = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newFormRef = ref(null)

const newUser = reactive({ username: '', password: '', display_name: '', role: 'employee' })
const newRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
}

onMounted(() => fetchUsers())

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await api.get('/users/')
  } finally {
    loading.value = false
  }
}

function roleType(role) {
  return { admin: 'danger', finance: 'warning', employee: '' }[role] || ''
}

function roleLabel(role) {
  return { admin: '管理员', finance: '财务', employee: '员工' }[role] || ''
}

async function toggleUser(row) {
  await ElMessageBox.confirm(`确认${row.is_active ? '禁用' : '启用'}用户 ${row.username}？`, '提示')
  await api.put(`/users/${row.id}/toggle`)
  ElMessage.success('操作成功')
  fetchUsers()
}

async function deleteUser(row) {
  await ElMessageBox.confirm(`确认删除用户 ${row.username}？`, '提示', { type: 'warning' })
  await api.delete(`/users/${row.id}`)
  ElMessage.success('删除成功')
  fetchUsers()
}

async function handleCreate() {
  const valid = await newFormRef.value.validate().catch(() => false)
  if (!valid) return
  await api.post('/users/', newUser)
  ElMessage.success('创建成功')
  showCreateDialog.value = false
  Object.assign(newUser, { username: '', password: '', display_name: '', role: 'employee' })
  fetchUsers()
}
</script>
