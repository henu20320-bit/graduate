<template>
  <div class="panel-card chart-card">
    <h3 class="chart-title">{{ title }}</h3>
    <p class="chart-subtitle">{{ subtitle }}</p>
    <div ref="chartRef" class="chart-body"></div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  option: {
    type: Object,
    required: true,
  },
})

const chartRef = ref(null)
let chartInstance

function renderChart() {
  if (!chartRef.value) {
    return
  }
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  chartInstance.setOption(props.option, true)
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(async () => {
  await nextTick()
  renderChart()
  window.addEventListener('resize', handleResize)
})

watch(
  () => props.option,
  async () => {
    await nextTick()
    renderChart()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>
