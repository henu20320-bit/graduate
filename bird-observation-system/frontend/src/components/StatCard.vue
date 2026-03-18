<template>
  <div class="panel-card metric-card">
    <div class="metric-label">{{ title }}</div>
    <div class="metric-value">{{ value }}</div>
    <div style="margin-top: 14px;">
      <span class="metric-badge">{{ caption }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: 0,
  },
  caption: {
    type: String,
    default: '实时统计',
  },
})
</script>
