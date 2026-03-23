import http from './http'

export function fetchDetectionRecords(page = 1, pageSize = 10) {
  return http.get('/records', { params: { page, page_size: pageSize } })
}

export function fetchDetectionRecordDetail(recordId) {
  return http.get(`/records/${recordId}`)
}
