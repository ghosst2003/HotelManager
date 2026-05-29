<template>
  <el-card>
    <template #header>
      <span>{{ isEdit ? '编辑订单' : '录入订单' }}</span>
    </template>
    <el-form v-loading="loading" :model="form" label-width="110px" :rules="rules" ref="formRef">
      <!-- 基本信息 -->
      <h3 style="color: #c0392b; margin-bottom: 16px">基本信息</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="订单平台" prop="order_platform">
            <el-select v-model="form.order_platform" placeholder="请选择" style="width: 100%">
              <el-option label="去哪儿" value="去哪儿" />
              <el-option label="携程" value="携程" />
              <el-option label="美团" value="美团" />
              <el-option label="飞猪" value="飞猪" />
              <el-option label="同程" value="同程" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="业务员" prop="salesperson">
            <el-select v-if="authStore.isAdmin" v-model="form.salesperson" placeholder="请选择业务员" style="width: 100%">
              <el-option v-for="emp in employees" :key="emp.id" :label="emp.display_name" :value="emp.display_name" />
            </el-select>
            <el-input v-else v-model="form.salesperson" placeholder="自动填入" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="订单号" prop="order_number">
            <el-input v-model="form.order_number" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="房型" prop="room_name">
            <el-input v-model="form.room_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="酒店名称" prop="hotel_name">
            <el-input v-model="form.hotel_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="入住人数" prop="guest_count">
            <el-input-number v-model="form.guest_count" :min="1" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="入住人" prop="guest_name">
            <el-input v-model="form.guest_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="预订日期" prop="booking_date">
            <el-date-picker v-model="form.booking_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 预订详情 -->
      <h3 style="color: #c0392b; margin: 24px 0 16px">预订详情</h3>
      <OrderItemTable v-model:items="form.items" />

      <!-- 其他信息 -->
      <h3 style="color: #c0392b; margin: 24px 0 16px">其他信息</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="确认号">
            <el-input v-model="form.confirmation_number" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="订单状态">
            <el-select v-model="form.order_status" style="width: 100%">
              <el-option label="未处理" value="未处理" />
              <el-option label="已确认" value="已确认" />
              <el-option label="已入住" value="已入住" />
              <el-option label="已取消" value="已取消" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="其他备注">
            <el-input v-model="form.other_remarks" type="textarea" :rows="3" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item style="margin-top: 24px">
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存数据</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/api'
import OrderItemTable from '@/components/OrderItemTable.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const submitting = ref(false)
const isEdit = ref(false)
const employees = ref([])
const loading = ref(false)

const form = reactive({
  order_platform: '',
  order_number: '',
  room_name: '',
  guest_name: '',
  hotel_name: '',
  guest_count: 1,
  booking_date: '',
  confirmation_number: '',
  order_status: '未处理',
  other_remarks: '',
  items: [],
})

const rules = {
  order_platform: [{ required: true, message: '请选择订单平台', trigger: 'change' }],
  order_number: [{ required: true, message: '请输入订单号', trigger: 'blur' }],
  room_name: [{ required: true, message: '请输入房型', trigger: 'blur' }],
  guest_name: [{ required: true, message: '请输入入住人', trigger: 'blur' }],
  hotel_name: [{ required: true, message: '请输入酒店名称', trigger: 'blur' }],
  booking_date: [{ required: true, message: '请选择预订日期', trigger: 'change' }],
}

onMounted(async () => {
  if (authStore.isAdmin) {
    loading.value = true
    try {
      const users = await api.get('/users/')
      employees.value = users.filter(u => u.role === 'employee')
    } finally {
      loading.value = false
    }
    form.salesperson = employees.value[0]?.display_name || ''
  } else {
    form.salesperson = authStore.user?.display_name || ''
  }
  if (route.params.id) {
    isEdit.value = true
    loading.value = true
    try {
      const order = await api.get(`/orders/${route.params.id}`)
      Object.assign(form, {
        order_platform: order.order_platform,
        order_number: order.order_number,
        room_name: order.room_name,
        guest_name: order.guest_name,
        hotel_name: order.hotel_name,
        guest_count: order.guest_count,
        booking_date: order.booking_date,
        confirmation_number: order.confirmation_number || '',
        order_status: order.order_status,
        other_remarks: order.other_remarks || '',
        items: order.items.map(i => ({
          date: i.date,
          room_count: i.room_count,
          cost_price: Number(i.cost_price),
          sale_price: Number(i.sale_price),
          salesperson: i.salesperson || '',
          confirmation_number: i.confirmation_number || '',
          remarks: i.remarks || '',
          additional_expenses: (i.additional_expenses || []).map(e => ({
            item: e.item || '',
            cost: Number(e.cost || 0),
            expense: Number(e.expense || 0),
          })),
          _showExpenses: false,
        })),
      })
    } finally {
      loading.value = false
    }
  } else {
    form.items.push({
      date: new Date().toISOString().slice(0, 10),
      room_count: 1, cost_price: 0, sale_price: 0,
      salesperson: '', confirmation_number: '', remarks: '',
      additional_expenses: [],
      _showExpenses: false,
    })
  }
})

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const cleanItems = form.items.map(item => {
      const { _showExpenses, ...rest } = item
      // Filter out empty expenses
      rest.additional_expenses = (rest.additional_expenses || []).filter(
        e => e.item || e.cost || e.expense,
      )
      if (!rest.additional_expenses.length) {
        delete rest.additional_expenses
      }
      return rest
    })
    const payload = { ...form, items: cleanItems, salesperson: form.salesperson }
    if (isEdit.value) {
      await api.put(`/orders/${route.params.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/orders/', payload)
      ElMessage.success('保存成功')
    }
    router.push('/orders')
  } catch (e) {
    // Error handled by interceptor
  } finally {
    submitting.value = false
  }
}
</script>
