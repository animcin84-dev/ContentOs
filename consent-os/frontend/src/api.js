import axios from 'axios'

const BASE_URL = '/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Inject JWT token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ────────────────────────────────────────────────────────────────────────
export const authRegister = (email, name, password) =>
  api.post('/auth/register', { email, name, password })

export const authLogin = (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return axios.post(`${BASE_URL}/auth/token`, form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const authMe = () => api.get('/auth/me')

// ── Consents ────────────────────────────────────────────────────────────────────
export const getConsents = () => api.get('/consents')
export const revokeConsent = (id) => api.delete(`/consents/${id}/revoke`)
export const verifyExternalRevoke = (externalId, searchName) => 
    api.post(`/verify-external-revoke`, { external_id: externalId, search_name: searchName })

// ── History ─────────────────────────────────────────────────────────────────────
export const getHistory = () => api.get('/history')

// ── Stats ───────────────────────────────────────────────────────────────────────
export const getStats = () => api.get('/stats')

// ── Advanced ────────────────────────────────────────────────────────────────────
export const runRescan = () => api.post('/rescan')
export const massRevoke = () => api.post('/webhooks/mass-revoke')
export const deepWebScan = () => api.post('/leak-scanner')
