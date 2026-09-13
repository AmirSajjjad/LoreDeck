import type { AxiosResponse } from 'axios'
import { vi } from 'vitest'
import { apiClient } from '@/api/client'

export function apiResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Response',
    headers: {},
    config: { headers: {} as AxiosResponse<T>['config']['headers'] },
  }
}

export function mockApiMethod(method: 'get' | 'post' | 'patch') {
  return vi.spyOn(apiClient, method)
}
