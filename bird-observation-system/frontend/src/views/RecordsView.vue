<template>
  <div class="page-shell">
    <div class="page-header">
      <div>
        <h1 class="page-title">检测记录</h1>
        <div class="page-subtitle">展示系统保存的识别结果，便于说明检测、落库与追溯链路。</div>
      </div>

      <div class="page-actions">
        <el-select v-model="sourceFilter" placeholder="来源类型" clearable style="width: 150px;">
          <el-option label="图片" value="image" />
          <el-option label="视频" value="video" />
          <el-option label="摄像头" value="camera" />
        </el-select>
        <el-select v-model="alertFilter" placeholder="预警状态" clearable style="width: 150px;">
          <el-option label="已预警" value="alert" />
          <el-option label="普通记录" value="normal" />
        </el-select>
        <el-button type="primary" @click="loadRecords">刷新数据</el-button>
      </div>
    </div>

    <div class="panel-card table-panel">
      <div class="table-toolbar">
        <div class="table-toolbar-title">记录列表</div>
        <div class="table-toolbar-meta">当前页共 {{ filteredRecords.length }} 条可见记录</div>
      </div>

      <el-table v-loading="loading" :data="filteredRecords" stripe style="width: 100%;">
        <el-table-column prop="id" label="编号" width="90" />
        <el-table-column prop="species_name" label="鸟类名称" min-width="160" />
        <el-table-column prop="source_type" label="来源类型" width="110" />
        <el-table-column prop="confidence" label="置信度" width="120">
          <template #default="scope">
            {{ Number(scope.row.confidence || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="alert_level" label="预警等级" width="120">
          <template #default="scope">
            <el-tag :class="['level-tag', `is-${scope.row.alert_level || 'none'}`]" effect="dark">
              {{ String(scope.row.alert_level || 'none').toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capture_time" label="检测时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.capture_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="source_file" label="源文件" min-width="220" show-overflow-tooltip />
        <el-table-column label="结果图" width="120">
          <template #default="scope">
            <el-link v-if="scope.row.result_image_path" :href="buildAssetUrl(scope.row.result_image_path)" target="_blank" type="primary">
              查看结果
            </el-link>
            <span v-else class="muted-text">无</span>
          </template>
        </el-table-column>
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

import { fetchDetectionRecords } from '../api/records'

const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const records = ref([])
const sourceFilter = ref('')
const alertFilter = ref('')

const filteredRecords = computed(() =>
  records.value.filter((item) => {
    const sourceMatched = !sourceFilter.value || item.source_type === sourceFilter.value
    const alertMatched =
      !alertFilter.value ||
      (alertFilter.value === 'alert' ? item.is_alert : !item.is_alert)
    return sourceMatched && alertMatched
  }),
)

function normalizeRecord(item) {
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

function buildAssetUrl(path) {
  if (!path) {
    return '#'
  }
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  return `${window.location.origin}/${String(path).replace(/^\/+/, '')}`
}

async function loadRecords() {
  loading.value = true
  try {
    const response = await fetchDetectionRecords(page.value, pageSize.value)
    records.value = (response.data?.items || []).map(normalizeRecord)
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

function handlePageChange(value) {
  page.value = value
  loadRecords()
}

function handleSizeChange(value) {
  pageSize.value = value
  page.value = 1
  loadRecords()
}

onMounted(() => {
  loadRecords()
})
</script>
