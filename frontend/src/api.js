import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aios_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('aios_token')
      localStorage.removeItem('aios_user')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export default api

// Auth
export const login = (username, password, totp_code = null) =>
  api.post('/auth/login', { username, password, totp_code })

export const getMe = () => api.get('/auth/me')

export const setup2FA = () => api.post('/auth/setup-2fa')

export const verify2FA = (code) => api.post('/auth/verify-2fa', { code })

// Agents
export const listAgents = () => api.get('/agents')

export const getAgent = (id) => api.get(`/agents/${id}`)

export const startAgent = (id) => api.post(`/agents/${id}/start`)

export const stopAgent = (id) => api.post(`/agents/${id}/stop`)

export const getAgentToken = (id) => api.get(`/agent-token/${id}`)

// Messages
export const getMessages = (limit = 100) => api.get(`/messages?limit=${limit}`)

export const sendMessage = (content, message_type = 'chat') =>
  api.post('/messages', { content, message_type })

// Interactive session
export const startSession = () => api.post('/messages/session/start')

export const stopSession = () => api.post('/messages/session/stop')

export const getSessionStatus = () => api.get('/messages/session/status')

// Permissions
export const getPermissions = (agentId) => api.get(`/permissions/${agentId}`)

export const togglePermission = (agentId, key, enabled) =>
  api.put(`/permissions/${agentId}/${key}`, { enabled })

// Requests
export const getRequests = (status = null) => {
  const url = status ? `/requests?status=${status}` : '/requests'
  return api.get(url)
}

export const createRequest = (request_type, description, detail_json = null) =>
  api.post('/requests', { request_type, description, detail_json })

export const resolveRequest = (id, status) =>
  api.put(`/requests/${id}`, { status })
