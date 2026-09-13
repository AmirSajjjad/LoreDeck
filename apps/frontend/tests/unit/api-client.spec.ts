import { AxiosError, AxiosHeaders, type AxiosResponse } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/api/client'
import { onUnauthorized, setAccessTokenProvider } from '@/api/auth'
import { ApiError } from '@/types/api'

describe('shared Axios client', () => {
  it('attaches a bearer token only when one is available', async () => {
    const observed: Array<string | undefined> = []
    apiClient.defaults.adapter = async (config) => {
      const authorization = config.headers.get('Authorization')
      observed.push(typeof authorization === 'string' ? authorization : undefined)
      return {
        data: {},
        status: 200,
        statusText: 'OK',
        headers: new AxiosHeaders(),
        config,
      }
    }

    await apiClient.get('/without-token')
    setAccessTokenProvider({ getAccessToken: () => 'test-token' })
    await apiClient.get('/with-token')

    expect(observed).toEqual([undefined, 'Bearer test-token'])
  })

  it('normalizes 401 and emits one unauthorized event until reset', async () => {
    const listener = vi.fn()
    const dispose = onUnauthorized(listener)
    apiClient.defaults.adapter = async (config): Promise<AxiosResponse> => {
      throw new AxiosError(
        'unauthorized',
        undefined,
        config,
        {},
        {
          status: 401,
          data: {},
          headers: new AxiosHeaders(),
          config,
          statusText: 'Unauthorized',
        },
      )
    }

    await expect(apiClient.get('/private')).rejects.toMatchObject<ApiError>({
      category: 'unauthorized',
      status: 401,
    })
    await expect(apiClient.get('/private-again')).rejects.toBeInstanceOf(ApiError)
    expect(listener).toHaveBeenCalledTimes(1)
    dispose()
  })
})
