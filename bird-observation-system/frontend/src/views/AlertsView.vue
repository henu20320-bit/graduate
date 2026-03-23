<template>
  <div class="page-shell">
    <div class="page-header">
      <div>
        <h1 class="page-title">预警记录</h1>
        <div class="page-subtitle">集中展示重点鸟类和珍稀鸟类预警结果，体现识别与业务联动能力。</div>
      </div>

      <div class="page-actions">
        <el-select v-model="levelFilter" placeholder="预警等级" clearable style="width: 150px;">
          <el-option label="高等级" value="high" />
          <el-option label="中等级" value="medium" />
        </el-select>
        <el-select v-model="sustainedFilter" placeholder="持续出现" clearable style="width: 150px;">
          <el-option label="持续出现预警" value="yes" />
          <el-option label="普通预警" value="no" />
        </el-select>
        <el-button type="primary" @click="loadAlerts">刷新数据</el-button>
      </div>
    </div>

    <div class="panel-card table-panel">
      <div class="table-toolbar">
        <div class="table-toolbar-title">预警列表</div>
        <div class="table-toolbar-meta">当前页共 {{ filteredAlerts.length }} 条可见预警</div>
      </div>

      <el-table v-loading="loading" :data="filteredAlerts" stripe style="width: 100%;">
        <el-table-column prop="id" label="编号" width="90" />
        <el-table-column prop="species_name" label="鸟类名称" min-width="180" />
        <el-table-column prop="alert_level" label="预警等级" width="120">
          <template #default="scope">
            <el-tag :class="['level-tag', `is-${scope.row.alert_level || 'none'}`]" effect="dark">
              {{ String(scope.row.alert_level || 'none').toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警特征" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.sustained_occurrence" type="danger">持续出现</el-tag>
            <span v-else class="muted-text">普通触发</span>
          </template>
        </el-table-column>
        <el-table-column prop="handled_status" label="处理状态" width="130" />
        <el-table-column prop="created_at" label="预警时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="alert_message" label="预警信息" min-width="360" show-overflow-tooltip />
      </el-table>

      <div class="table-pagination">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          :page-sizes="[10, 20, 50]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { fetchAlertList } from '../api/alerts'

const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const alerts = ref([])
const levelFilter = ref('')
const sustainedFilter = ref('')

const filteredAlerts = computed(() =>
  alerts.value.filter((item) => {
    const levelMatched = !levelFilter.value || item.alert_level === levelFilter.value
    const sustainedMatched =
      !sustainedFilter.value ||
      (sustainedFilter.value === 'yes' ? item.sustained_occurrence : !item.sustained_occurrence)
    return levelMatched && sustainedMatched
  }),
)

function normalizeAlert(item) {
  return {
    ...item,
    species_name:
      item.species?.chinese_name ||
      item.species?.english_name ||
      item.species?.model_class_name ||
      '未匹配物种',
  }
}

function formatDateTime(value) {
  if (!value) {
    return '-'
  }
  return String(value).replace('T', ' ').slice(0, 19)
}

async function loadAlerts() {
  loading.value = true
  try {
    const response = await fetchAlertList(page.value, pageSize.value)
    alerts.value = (response.data?.items || []).map(normalizeAlert)
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

function handlePageChange(value) {
  page.value = value
  loadAlerts()
}

function handleSizeChange(value) {
  pageSize.value = value
  page.value = 1
  loadAlerts()
}

onMounted(() => {
  loadAlerts()
})
</script>
