<template>
  <div class="page-shell">
    <div class="page-header">
      <div>
        <h1 class="page-title">鸟类检测与识别系统仪表盘</h1>
        <div class="page-subtitle">基于 YOLOv8 的自动观测、珍稀预警与统计分析展示首页</div>
      </div>
      <el-radio-group v-model="selectedDays" size="large" @change="loadDashboard">
        <el-radio-button :label="7">近7天</el-radio-button>
        <el-radio-button :label="30">近30天</el-radio-button>
      </el-radio-group>
    </div>

    <el-row :gutter="18" style="margin-bottom: 18px;">
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard title="总检测次数" :value="overview.totalDetections" caption="累计检测记录" />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard title="今日检测次数" :value="overview.todayDetections" caption="今日新增识别" />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard title="珍稀鸟类次数" :value="overview.rareBirdDetections" caption="珍稀物种识别" />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard title="预警次数" :value="overview.alertCount" caption="自动预警触发" />
      </el-col>
    </el-row>

    <el-row :gutter="18" style="margin-bottom: 18px;">
      <el-col :xs="24" :lg="12">
        <ChartPanel title="鸟类种类频次" subtitle="按识别种类统计检测频次" :option="speciesChartOption" />
      </el-col>
      <el-col :xs="24" :lg="12">
        <ChartPanel title="检测趋势" subtitle="按日期统计近阶段检测变化" :option="trendChartOption" />
      </el-col>
    </el-row>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="10">
        <ChartPanel title="珍稀鸟类预警占比" subtitle="展示珍稀预警等级构成" :option="rareChartOption" />
      </el-col>
      <el-col :xs="24" :lg="14">
        <div class="panel-card alert-panel">
          <h3 class="chart-title">最近预警列表</h3>
          <p class="chart-subtitle">展示最近一次预警与当前预警分布，适合答辩演示说明</p>

          <div class="alert-highlight" v-if="latestAlert">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 8px;">
              <div class="alert-highlight-title">{{ latestAlert.title }} · {{ latestAlert.species_name }}</div>
              <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <el-tag v-if="latestAlert.sustained_occurrence" type="danger">持续出现</el-tag>
                <el-tag :class="['level-tag', `is-${latestAlert.alert_level}`]" effect="dark">
                  {{ latestAlert.alert_level.toUpperCase() }}
                </el-tag>
              </div>
            </div>
            <p class="alert-highlight-text">{{ latestAlert.message }}</p>
          </div>

          <el-table :data="alertTableData" stripe style="width: 100%;">
            <el-table-column prop="species_name" label="鸟类名称" min-width="140" />
            <el-table-column prop="alert_level" label="预警等级" width="120">
              <template #default="scope">
                <el-tag :class="['level-tag', `is-${scope.row.alert_level}`]" effect="dark">
                  {{ scope.row.alert_level.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="120">
              <template #default="scope">
                {{ Number(scope.row.confidence || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="特征" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.sustained_occurrence" type="danger">持续出现</el-tag>
                <span v-else class="muted-text">普通</span>
              </template>
            </el-table-column>
            <el-table-column prop="detected_at" label="检测时间" min-width="180" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { fetchLatestAlert, fetchAlertList } from '../api/alerts'
import { fetchDailyTrend, fetchOverviewStats, fetchRareBirdStats, fetchSpeciesFrequency } from '../api/stats'
import ChartPanel from '../components/ChartPanel.vue'
import StatCard from '../components/StatCard.vue'

const selectedDays = ref(7)
const overview = ref({
  totalDetections: 0,
  todayDetections: 0,
  rareBirdDetections: 0,
  alertCount: 0,
})
const speciesFrequency = ref({ categories: [], series: [{ data: [] }] })
const dailyTrend = ref({ dates: [], series: [{ data: [] }] })
const rareBirdStats = ref({
  totalRareAlerts: 0,
  highAlerts: 0,
  mediumAlerts: 0,
  speciesDistribution: [],
})
const latestAlert = ref(null)
const alertTableData = ref([])

const speciesChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 18, top: 20, bottom: 48 },
  xAxis: {
    type: 'category',
    data: speciesFrequency.value.categories,
    axisLabel: { interval: 0, rotate: 18, color: '#5b7083' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#e6edf4' } },
  },
  series: [
    {
      name: speciesFrequency.value.series?.[0]?.name || '检测频次',
      type: 'bar',
      barWidth: 26,
      data: speciesFrequency.value.series?.[0]?.data || [],
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: '#2f6f5f',
      },
    },
  ],
}))

const trendChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 18, top: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: dailyTrend.value.dates,
    axisLabel: { color: '#5b7083' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#e6edf4' } },
  },
  series: [
    {
      name: dailyTrend.value.series?.[0]?.name || '检测趋势',
      type: 'line',
      smooth: true,
      data: dailyTrend.value.series?.[0]?.data || [],
      symbolSize: 8,
      lineStyle: { width: 3, color: '#1f5f8b' },
      itemStyle: { color: '#1f5f8b' },
      areaStyle: {
        color: 'rgba(31, 95, 139, 0.12)',
      },
    },
  ],
}))

const rareChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: {
    bottom: 0,
    icon: 'circle',
  },
  series: [
    {
      name: '预警占比',
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '44%'],
      label: { formatter: '{b}: {d}%' },
      data: [
        { name: '高等级预警', value: rareBirdStats.value.highAlerts, itemStyle: { color: '#c2410c' } },
        { name: '中等级预警', value: rareBirdStats.value.mediumAlerts, itemStyle: { color: '#d97706' } },
      ],
    },
  ],
}))

function normalizeAlertRows(alertResponse, latestResponse) {
  const rows = alertResponse?.data?.items || []
  const mappedRows = rows.slice(0, 6).map((item) => ({
    species_name: item.species?.chinese_name || item.species?.english_name || '未知鸟类',
    alert_level: item.alert_level,
    confidence: latestResponse?.data?.confidence || 0,
    detected_at: item.created_at,
    sustained_occurrence: Boolean(item.sustained_occurrence),
  }))

  if (mappedRows.length === 0 && latestResponse?.data) {
    return [latestResponse.data]
  }
  return mappedRows
}

async function loadDashboard() {
  const [overviewRes, speciesRes, trendRes, rareRes, latestAlertRes, alertListRes] = await Promise.all([
    fetchOverviewStats(),
    fetchSpeciesFrequency(selectedDays.value),
    fetchDailyTrend(selectedDays.value),
    fetchRareBirdStats(selectedDays.value),
    fetchLatestAlert(),
    fetchAlertList(1, 6),
  ])

  overview.value = overviewRes.data
  speciesFrequency.value = speciesRes.data
  dailyTrend.value = trendRes.data
  rareBirdStats.value = rareRes.data
  latestAlert.value = latestAlertRes.data
  alertTableData.value = normalizeAlertRows(alertListRes, latestAlertRes)
}

onMounted(() => {
  loadDashboard()
})
</script>
