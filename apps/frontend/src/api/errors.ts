import axios from 'axios'
import { API_ERROR_MESSAGES } from '@/api/messages'
import { ApiError } from '@/types/api'
import { normalizeFastApiValidationErrors } from '@/utils/fastApiValidation'

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error
  if (!axios.isAxiosError(error)) return new ApiError('unexpected', API_ERROR_MESSAGES.unexpected)

  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return new ApiError('timeout', API_ERROR_MESSAGES.timeout)
  }

  const status = error.response?.status
  if (!status) {
    const category = error.request ? 'network' : 'unexpected'
    return new ApiError(category, API_ERROR_MESSAGES[category])
  }

  if (status === 401) {
    return new ApiError('unauthorized', API_ERROR_MESSAGES.unauthorized, { status })
  }
  if (status === 403) {
    return new ApiError('forbidden', API_ERROR_MESSAGES.forbidden, { status })
  }
  if (status === 422) {
    const validation = normalizeFastApiValidationErrors(error.response?.data)
    return new ApiError('validation', validation.formMessage ?? API_ERROR_MESSAGES.validation, {
      status,
      fieldErrors: validation.fieldErrors,
    })
  }
  if (status === 404) {
    return new ApiError('not-found', API_ERROR_MESSAGES['not-found'], { status })
  }
  if (status === 409) {
    return new ApiError('conflict', API_ERROR_MESSAGES.conflict, { status })
  }
  if (status >= 500) {
    return new ApiError('server', API_ERROR_MESSAGES.server, { status })
  }

  return new ApiError('http', API_ERROR_MESSAGES.http, { status })
}
