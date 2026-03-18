import http from './http'

export function fetchOverviewStats() {
  return http.get('/stats/overview')
}

export function fetchSpeciesFrequency(days = 7) {
  return http.get('/stats/species-frequency', { params: { days } })
}

export function fetchDailyTrend(days = 7) {
  return http.get('/stats/daily-trend', { params: { days } })
}

export function fetchRareBirdStats(days = 7) {
  return http.get('/stats/rare-birds', { params: { days } })
}

export function fetchMigrationTrend(days = 7) {
  return http.get('/stats/migration-trend', { params: { days } })
}
