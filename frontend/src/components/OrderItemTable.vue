<template>
  <div>
    <el-table ref="tableRef" :data="items" border style="width: 100%" size="default" row-key="_uid" @expand-change="onExpandChange">
      <el-table-column type="expand" width="36">
        <template #header>
          <span style="visibility: hidden">&nbsp;</span>
        </template>
        <template #default="{ row }">
          <div style="padding: 10px 20px; background: #fafafa;">
            <div style="font-size: 12px; font-weight: 600; color: #666; margin-bottom: 8px">
              附加费用明细（合计: ¥{{ expensesTotal(row).toFixed(2) }}）
            </div>

            <el-table :data="row.additional_expenses || []" border size="small" style="width: 100%; margin-bottom: 8px">
              <el-table-column label="事项" width="128">
                <template #default="{ row: exp }">
                  <el-input v-model="exp.item" size="small" placeholder="费用事项" style="width: 118px" />
                </template>
              </el-table-column>
              <el-table-column label="成本" width="140">
                <template #default="{ row: exp }">
                  <el-input-number v-model="exp.cost" :precision="2" :min="0" size="small" style="width: 120px" />
                </template>
              </el-table-column>
              <el-table-column label="支出" width="140">
                <template #default="{ row: exp }">
                  <el-input-number v-model="exp.expense" :precision="2" :min="0" size="small" style="width: 120px" />
                </template>
              </el-table-column>
              <el-table-column label="利润" width="120">
                <template #default="{ row: exp }">
                  {{ ((exp.expense || 0) - (exp.cost || 0)).toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="70">
                <template #default="{ $index: expIdx }">
                  <el-button type="danger" link size="small" @click="removeExpense(row, expIdx)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-button type="warning" plain size="small" @click="addExpense(row)">+ 添加附加费用</el-button>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="日期" width="140">
        <template #default="{ row }">
          <el-date-picker v-model="row.date" type="date" value-format="YYYY-MM-DD" size="small" style="width: 125px" />
        </template>
      </el-table-column>
      <el-table-column label="间数" width="80">
        <template #default="{ row }">
          <el-input-number v-model="row.room_count" :min="1" size="small" style="width: 70px" />
        </template>
      </el-table-column>
      <el-table-column label="成本价" width="105">
        <template #default="{ row }">
          <el-input-number v-model="row.cost_price" :precision="2" :min="0" size="small" style="width: 95px" />
        </template>
      </el-table-column>
      <el-table-column label="销售价" width="105">
        <template #default="{ row }">
          <el-input-number v-model="row.sale_price" :precision="2" :min="0" size="small" style="width: 95px" />
        </template>
      </el-table-column>
      <el-table-column label="额外费用" width="100">
        <template #default="{ row }">
          <span style="color: #666; font-size: 13px">{{ expensesTotal(row).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="毛利" width="90">
        <template #default="{ row }">
          {{ calcGrossProfit(row).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="毛利率" width="90">
        <template #default="{ row }">
          <template v-if="(row.sale_price || 0) > 0">
            {{ ((calcGrossProfit(row) / (row.sale_price || 1)) * 100).toFixed(1) }}%
          </template>
          <template v-else>-</template>
        </template>
      </el-table-column>
      <el-table-column label="确认号" width="120">
        <template #default="{ row }">
          <el-input v-model="row.confirmation_number" size="small" placeholder="可选" />
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="120">
        <template #default="{ row }">
          <el-input v-model="row.remarks" size="small" placeholder="可选" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row, $index }">
          <el-button type="warning" link size="small" @click="toggleExpenses(row)">
            {{ isExpanded(row) ? '收起' : '附加项' }}
          </el-button>
          <el-button type="danger" link size="small" @click="removeRow($index)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-button type="primary" plain size="small" style="margin-top: 8px" @click="addRow">+ 添加行</el-button>

    <div style="margin-top: 10px; font-weight: bold; color: #666">
      合计: {{ totalNights }}晚 | 成本: {{ totalCost.toFixed(2) }} | 销售: {{ totalSale.toFixed(2) }} | 附加费用合计: {{ totalExpenses.toFixed(2) }} | 毛利: {{ totalProfit.toFixed(2) }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const items = defineModel('items', { default: () => [] })
const tableRef = ref(null)
const expandedIds = ref(new Set())

// Assign stable unique ID to each item
let uidCounter = 0
function ensureUid(item) {
  if (!item._uid) {
    item._uid = ++uidCounter
  }
}

// Ensure all items have _uid when data changes
watch(items, (newItems) => {
  newItems.forEach(ensureUid)
}, { deep: true, immediate: true })

function newRow() {
  return {
    date: null,
    room_count: 1,
    cost_price: 0,
    sale_price: 0,
    confirmation_number: '',
    remarks: '',
    additional_expenses: [],
  }
}

function addRow() {
  const row = newRow()
  items.value.push(row)
}

function removeRow(index) {
  const removed = items.value[index]
  expandedIds.value.delete(removed._uid)
  items.value.splice(index, 1)
}

function isExpanded(row) {
  return expandedIds.value.has(row._uid)
}

function toggleExpenses(row) {
  if (!row.additional_expenses) {
    row.additional_expenses = []
  }
  tableRef.value.toggleRowExpansion(row, !isExpanded(row))
}

function onExpandChange(row, expandedRows) {
  expandedIds.value = new Set(expandedRows.map(r => r._uid))
}

function addExpense(row) {
  if (!row.additional_expenses) {
    row.additional_expenses = []
  }
  row.additional_expenses.push({ item: '', cost: 0, expense: 0 })
}

function removeExpense(row, expenseIndex) {
  row.additional_expenses.splice(expenseIndex, 1)
}

function expenseProfit(exp) {
  return (exp.expense || 0) - (exp.cost || 0)
}

function expensesTotal(row) {
  if (!row.additional_expenses) return 0
  return row.additional_expenses.reduce((sum, e) => sum + expenseProfit(e), 0)
}

function calcGrossProfit(row) {
  return ((row.sale_price || 0) - (row.cost_price || 0)) + expensesTotal(row)
}

const totalNights = computed(() => items.value.reduce((s, r) => s + (r.room_count || 0), 0))
const totalCost = computed(() => items.value.reduce((s, r) => s + (r.cost_price || 0), 0))
const totalSale = computed(() => items.value.reduce((s, r) => s + (r.sale_price || 0), 0))
const totalExpenses = computed(() => items.value.reduce((s, r) => s + expensesTotal(r), 0))
const totalProfit = computed(() => totalSale.value - totalCost.value + totalExpenses.value)
</script>
