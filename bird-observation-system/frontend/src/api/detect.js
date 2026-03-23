import http from './http'

export function detectImage(file, weightPath = '') {
  const formData = new FormData()
  formData.append('file', file)

  return http.post('/detect/image', formData, {
    params: weightPath ? { weight_path: weightPath } : {},
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000,
  })
}
