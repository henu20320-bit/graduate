import { createRouter, createWebHistory } from 'vue-router'

import AlertsView from '../views/AlertsView.vue'
import DashboardView from '../views/DashboardView.vue'
import DetectView from '../views/DetectView.vue'
import RecordsView from '../views/RecordsView.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/detect',
    name: 'detect',
    component: DetectView,
  },
  {
    path: '/records',
    name: 'records',
    component: RecordsView,
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: AlertsView,
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
