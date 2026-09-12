import axios from 'axios'
import { emitUnauthorized, resolveAccessToken } from '@/api/auth'
import { getEnvironment } from '@/api/environment'
import { normalizeApiError } from '@/api/errors'

const API_TIMEOUT_MS = 10_000

export const apiClient = axios.create({
  baseURL: getEnvironment().apiBaseUrl,
  timeout: API_TIMEOUT_MS,
  responseType: 'json',
  headers: { Accept: 'application/json' },
})

apiClient.interceptors.request.use(async (config) => {
  const token = await resolveAccessToken()
  if (token && !config.headers.has('Authorization')) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (cause: unknown) => {
    const error = normalizeApiError(cause)
    if (error.category === 'unauthorized') emitUnauthorized(error)
    return Promise.reject(error)
  },
)
