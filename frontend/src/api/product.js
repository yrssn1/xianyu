import request from '../utils/request'

const api = request

export function getProducts(params) {
  return api.get('/products', { params })
}

export function getProduct(id) {
  return api.get(`/products/${id}`)
}

export function createProduct(data) {
  return api.post('/products', data)
}

export function updateProduct(id, data) {
  return api.put(`/products/${id}`, data)
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}`)
}

export function uploadImages(productId, files) {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  return api.post(`/products/${productId}/images`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteImage(productId, imageId) {
  return api.delete(`/products/${productId}/images/${imageId}`)
}
