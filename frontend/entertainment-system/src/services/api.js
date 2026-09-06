const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://reckond.onrender.com/'
const tokenKey = 'reckond_tokens'

function getTokens() {
  try { return JSON.parse(localStorage.getItem(tokenKey) || 'null') } catch { return null }
}

export function getStoredUser() {
  try { return JSON.parse(localStorage.getItem('reckond_user') || 'null') } catch { return null }
}

export function clearSession() {
  localStorage.removeItem(tokenKey)
  localStorage.removeItem('reckond_user')
}

let refreshPromise = null

async function refreshTokens() {
  const current = getTokens()
  if (!current?.refresh_token) throw new Error('Session expired')
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: current.refresh_token }),
    }).then(async (response) => {
      if (!response.ok) throw new Error('Session expired')
      const tokens = await response.json()
      localStorage.setItem(tokenKey, JSON.stringify(tokens))
      return tokens
    }).finally(() => { refreshPromise = null })
  }
  return refreshPromise
}

async function request(path, options = {}, retry = true) {
  const tokens = getTokens()
  const headers = new Headers(options.headers || {})
  if (tokens?.access_token) headers.set('Authorization', `Bearer ${tokens.access_token}`)
  if (options.body && !(options.body instanceof URLSearchParams)) headers.set('Content-Type', 'application/json')
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (response.status === 401 && retry && tokens?.refresh_token) {
    await refreshTokens()
    return request(path, options, false)
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Something went wrong')
  }
  if (response.status === 204) return null
  return response.json()
}

export const api = {
  login: async (email, password) => {
    const tokens = await request('/auth/login', { method: 'POST', body: new URLSearchParams({ username: email, password }) })
    localStorage.setItem(tokenKey, JSON.stringify(tokens))
    const user = await request('/users/me')
    localStorage.setItem('reckond_user', JSON.stringify(user))
    return user
  },
  me: () => request('/users/me'),
  register: (payload) => request('/auth/', { method: 'POST', body: JSON.stringify(payload) }),
  media: (mediaType = '', limit = 20) => request(`/media/?limit=${limit}${mediaType ? `&media_type=${mediaType}` : ''}`),
  search: (query, mediaType) => request(`/media/search?query=${encodeURIComponent(query)}&media_type=${mediaType}`),
  searchAll: async (query, mediaTypes) => {
    const results = await Promise.allSettled(mediaTypes.map((mediaType) => api.search(query, mediaType)))
    const successful = results.filter((result) => result.status === 'fulfilled').flatMap((result) => result.value)
    if (successful.length || results.some((result) => result.status === 'fulfilled')) return successful
    throw results.find((result) => result.status === 'rejected')?.reason || new Error('Search failed')
  },
  importMedia: (externalId, mediaType) => request('/media/import', { method: 'POST', body: JSON.stringify({ external_id: externalId, media_type: mediaType }) }),
  details: (id) => request(`/media/${id}`),
  recommendations: () => request('/recommendations/for-you'),
  watchlist: () => request('/watchlist/'),
  addToWatchlist: (id) => request('/watchlist/', { method: 'POST', body: JSON.stringify({ entertainment_id: id }) }),
  removeFromWatchlist: (id) => request(`/watchlist/${id}`, { method: 'DELETE' }),
  getRating: (id) => request(`/ratings/${id}`),
  saveRating: (id, rating) => request('/ratings/', { method: 'POST', body: JSON.stringify({ entertainment_id: id, rating }) }),
  getReview: (id) => request(`/reviews/${id}`),
  saveReview: (id, content, existing = false) => request(`/reviews/${existing ? id : ''}`, { method: existing ? 'PUT' : 'POST', body: JSON.stringify(existing ? { content } : { entertainment_id: id, content }) }),
  addLog: (id, action) => request('/logs/', { method: 'POST', body: JSON.stringify({ entertainment_id: id, action, logged_at: new Date().toISOString() }) }),
  ratings: () => request('/ratings/'),
  reviews: () => request('/reviews/'),
  logs: () => request('/logs/'),
}
