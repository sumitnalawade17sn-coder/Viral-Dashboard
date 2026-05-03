import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const fetchSummary = () => api.get('/api/dashboard/summary').then(r => r.data)
export const fetchContent = (params) => api.get('/api/content', { params }).then(r => r.data)
export const fetchAnalysis = () => api.get('/api/analysis').then(r => r.data)
export const fetchRecommendations = () => api.get('/api/recommendations').then(r => r.data)
export const fetchSearches = () => api.get('/api/searches').then(r => r.data)
export const saveSearch = (payload) => api.post('/api/searches', payload).then(r => r.data)
