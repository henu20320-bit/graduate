<template>
  <div class="page-shell">
    <div class="page-header">
      <div>
        <h1 class="page-title">图片检测演示</h1>
        <div class="page-subtitle">用于演示“上传图片 -> YOLOv8识别 -> 预警联动 -> 结果入库”的完整流程。</div>
      </div>
    </div>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="10">
        <div class="panel-card detect-panel">
          <h3 class="chart-title">上传检测图片</h3>
          <p class="chart-subtitle">当前页面直接调用后端图片检测接口，适合答辩现场演示识别效果。</p>

          <el-upload
            class="detect-upload"
            drag
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将图片拖到此处，或 <em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">建议上传单张鸟类图像，便于说明识别与预警过程。</div>
            </template>
          </el-upload>

          <div v-if="selectedFile" class="detect-meta">
            <div><strong>文件名：</strong>{{ selectedFile.name }}</div>
            <div><strong>文件大小：</strong>{{ formatFileSize(selectedFile.size) }}</div>
          </div>

          <div class="detect-actions">
            <el-button type="primary" :disabled="!selectedFile || loading" :loading="loading" @click="runDetect">
              开始检测
            </el-button>
            <el-button :disabled="loading" @click="resetState">清空结果</el-button>
          </div>

          <div v-if="previewUrl" class="detect-preview">
            <img :src="previewUrl" alt="preview" class="detect-preview-image" />
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="14">
        <div class="panel-card detect-panel">
          <h3 class="chart-title">检测结果</h3>
          <p class="chart-subtitle">展示模型识别结果、预警结果以及后端返回的结果路径。</p>

          <div v-if="result" class="detect-result-meta">
            <div class="detect-result-grid">
              <div class="detect-result-item"><span>来源类型</span><strong>{{ result.source_type }}</strong></div>
              <div class="detect-result-item"><span>源文件</span><strong>{{ result.source_name }}</strong></div>
              <div class="detect-result-item"><span>推理耗时</span><strong>{{ result.inference_time_ms }} ms</strong></div>
              <div class="detect-result-item"><span>检测数量</span><strong>{{ result.detections.length }}</strong></div>
            </div>
            <div class="detect-path">
              <strong>结果路径：</strong>{{ result.result_path || '未返回' }}
            </div>
          </div>

          <div v-if="result?.alerts?.length" class="alert-highlight">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap;">
              <div class="alert-highlight-title">预警结果</div>
              <el-tag type="danger">已触发 {{ result.alerts.length }} 条预警</el-tag>
            </div>
            <p
              v-for="alert in result.alerts"
              :key="`${alert.alert_id || alert.species_name}-${alert.detected_at}`"
              class="alert-highlight-text"
              style="margin-bottom: 8px;"
            >
              {{ alert.species_name }}：{{ alert.message }}
            </p>
          </div>

          <el-table v-if="result" :data="result.detections" stripe style="width: 100%;">
            <el-table-column prop="class_name" label="模型类别" min-width="140" />
            <el-table-column prop="species_name" label="物种名称" min-width="160">
              <template #default="scope">
                {{ scope.row.species_name || '未匹配物种' }}
              </template>
            </el-table-column>
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
            <el-table-column label="边界框" min-width="220">
              <template #default="scope">
                {{ formatBbox(scope.row.bbox) }}
              </template>
            </el-table-column>
          </el-table>

          <div v-else class="empty-block">上传一张图片后即可看到检测结果。</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { onBeforeUnmount, ref } from 'vue'

import { detectImage } from '../api/detect'

const loading = ref(false)
const selectedFile = ref(null)
const previewUrl = ref('')
const result = ref(null)

function revokePreview() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
}

function handleFileChange(uploadFile) {
  const raw = uploadFile.raw
  if (!raw) {
    return
  }
  revokePreview()
  selectedFile.value = raw
  previewUrl.value = URL.createObjectURL(raw)
}

function resetState() {
  selectedFile.value = null
  result.value = null
  revokePreview()
}

function formatFileSize(size) {
  if (!size && size !== 0) {
    return '-'
  }
  if (size < 1024) {
    return `${size} B`
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  }
  return `${(size / 1024 / 1024).toFixed(2)} MB`
}

function formatBbox(bbox) {
  if (!Array.isArray(bbox) || bbox.length !== 4) {
    return '-'
  }
  return bbox.map((item) => Number(item).toFixed(2)).join(', ')
}

async function runDetect() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择一张图片')
    return
  }

  loading.value = true
  try {
    const response = await detectImage(selectedFile.value)
    result.value = response.data
    ElMessage.success('图片检测完成')
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  revokePreview()
})
</script>
