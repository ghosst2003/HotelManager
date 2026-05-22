<template>
  <div>
    <el-table :data="items" border style="width: 100%" size="default">
      <el-table-column label="日期" width="150">
        <template #default="{ row }">
          <el-date-picker v-model="row.date" type="date" value-format="YYYY-MM-DD" size="small" style="width: 130px" />
        </template>
      </el-table-column>
      <el-table-column label="间数" width="90">
        <template #default="{ row }">
          <el-input-number v-model="row.room_count" :min="1" size="small" style="width: 80px" />
        </template>
      </el-table-column>
      <el-table-column label="成本价" width="120">
        <template #default="{ row }">
          <el-input-number v-model="row.cost_price" :precision="2" :min="0" size="small" style="width: 110px" />
        </template>
      </el-table-column>
      <el-table-column label="销售价" width="120">
        <template #default="{ row }">
          <el-input-number v-model="row.sale_price" :precision="2" :min="0" size="small" style="width: 110px" />
        </template>
      </el-table-column>
      <el-table-column label="毛利" width="100">
        <template #default="{ row }">
          {{ ((row.sale_price || 0) - (row.cost_price || 0)).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="毛利率" width="100">
        <template #default="{ row }">
          <template v-if="(row.sale_price || 0) > 0">
            {{ ((((row.sale_price || 0) - (row.cost_price || 0)) / (row.sale_price || 1)) * 100).toFixed(1) }}%
          </template>
          <template v-else>-</template>
        </template>
      </el-table-column>
      <el-table-column label="业务员" width="120">
        <template #default="{ row }">
          <el-input v-model="row.salesperson" size="small" placeholder="可选" />
        </template>
      </el-table-column>
      <el-table-column label="确认号" width="130">
        <template #default="{ row }">
          <el-input v-model="row.confirmation_number" size="small" placeholder="可选" />
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="120">
        <template #default="{ row }">
          <el-input v-model="row.remarks" size="small" placeholder="可选" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ $index }">
          <el-button type="danger" link size="small" @click="removeRow($index)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="primary" plain size="small" style="margin-top: 8px" @click="addRow">+ 添加行</el-button>

    <div style="margin-top: 10px; font-weight: bold; color: #666">
      合计: {{ totalNights }}晚 | 成本: {{ totalCost.toFixed(2) }} | 销售: {{ totalSale.toFixed(2) }} | 毛利: {{ totalProfit.toFixed(2) }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const items = defineModel('items', { default: () => [] })

function addRow() {
  items.value.push({
    date: null,
    room_count: 1,
    cost_price: 0,
    sale_price: 0,
    salesperson: '',
    confirmation_number: '',
    remarks: '',
  })
}

function removeRow(index) {
  items.value.splice(index, 1)
}

const totalNights = computed(() => items.value.reduce((s, r) => s + (r.room_count || 0), 0))
const totalCost = computed(() => items.value.reduce((s, r) => s + (r.cost_price || 0), 0))
const totalSale = computed(() => items.value.reduce((s, r) => s + (r.sale_price || 0), 0))
const totalProfit = computed(() => totalSale.value - totalCost.value)
</script>
