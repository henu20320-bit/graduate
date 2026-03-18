import http from './http'

export function fetchLatestAlert() {
  return http.get('/alerts/latest')
}

export function fetchAlertList(page = 1, pageSize = 10) {
  return http.get('/alerts', { params: { page, page_size: pageSize } })
}
