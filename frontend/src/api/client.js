import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
})

export const artistsApi = {
  list: (params) => api.get('/artists/', { params }),
  get: (id) => api.get(`/artists/${id}/`),
  create: (data) => api.post('/artists/', data),
  update: (id, data) => api.put(`/artists/${id}/`, data),
  delete: (id) => api.delete(`/artists/${id}/`)
}

export const albumsApi = {
  list: (params) => api.get('/albums/', { params }),
  get: (id) => api.get(`/albums/${id}/`),
  create: (data) => api.post('/albums/', data),
  update: (id, data) => api.put(`/albums/${id}/`, data),
  delete: (id) => api.delete(`/albums/${id}/`),
  addTrack: (id, data) => api.post(`/albums/${id}/tracks/`, data),
  removeTrack: (albumId, trackId) => api.delete(`/albums/${albumId}/tracks/${trackId}/`)
}

export const songsApi = {
  list: (params) => api.get('/songs/', { params }),
  get: (id) => api.get(`/songs/${id}/`),
  create: (data) => api.post('/songs/', data),
  update: (id, data) => api.put(`/songs/${id}/`, data),
  delete: (id) => api.delete(`/songs/${id}/`)
}

export const statsApi = {
  get: () => api.get('/stats/')
}

export default api
