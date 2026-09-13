import { afterEach, beforeEach, vi } from 'vitest'
import { apiClient } from '@/api/client'
import { resetUnauthorizedEvent, setAccessTokenProvider } from '@/api/auth'
import { useReadingResultState } from '@/features/readings/readingResultState'

const blockedAdapter = async (): Promise<never> => {
  throw new Error('Unexpected real network request from a unit test.')
}

beforeEach(() => {
  apiClient.defaults.adapter = blockedAdapter
})

afterEach(() => {
  document.body.innerHTML = ''
  window.sessionStorage.clear()
  setAccessTokenProvider({ getAccessToken: () => null })
  resetUnauthorizedEvent()
  useReadingResultState().clearResult()
  vi.restoreAllMocks()
})
