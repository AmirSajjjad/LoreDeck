import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '@/types/api'

const { signin, signup, getProfile } = vi.hoisted(() => ({
  signin: vi.fn(),
  signup: vi.fn(),
  getProfile: vi.fn(),
}))

vi.mock('@/features/auth/api', () => ({ signin, signup }))
vi.mock('@/features/profile/api', () => ({ getProfile }))

import { useAuthStore } from '@/stores/auth'

const user = {
  id: 1,
  username: 'sara',
  phone_number: null,
  profile_pic: null,
  name: 'سارا',
  email: null,
  telegram_id: null,
  created_at: '2026-01-01T00:00:00Z',
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('authentication store', () => {
  it('accepts a successful sign-in and persists only the token', async () => {
    signin.mockResolvedValue({
      access_token: 'access',
      token_type: 'bearer',
      expires_in: 3600,
      user,
    })
    const auth = useAuthStore()
    await auth.signin({ username: 'sara', password: 'secret' })
    expect(auth.currentUser).toEqual(user)
    expect(auth.isAuthenticated).toBe(true)
    expect(sessionStorage.getItem('loredeck.access-token')).toBe('access')
  })

  it('initializes a stored session and clears an unauthorized session', async () => {
    sessionStorage.setItem('loredeck.access-token', 'access')
    getProfile.mockResolvedValueOnce(user)
    const valid = useAuthStore()
    await valid.initializeSession()
    expect(valid.status).toBe('authenticated')

    setActivePinia(createPinia())
    getProfile.mockRejectedValueOnce(new ApiError('unauthorized', 'نشست نامعتبر است.'))
    const invalid = useAuthStore()
    await invalid.initializeSession()
    expect(invalid.status).toBe('guest')
    expect(sessionStorage.getItem('loredeck.access-token')).toBeNull()
  })

  it('logs out and can synchronize an updated profile', async () => {
    signin.mockResolvedValue({
      access_token: 'access',
      token_type: 'bearer',
      expires_in: 3600,
      user,
    })
    const auth = useAuthStore()
    await auth.signin({ username: 'sara', password: 'secret' })
    auth.synchronizeUser({ ...user, name: 'سارای تازه' })
    expect(auth.currentUser?.name).toBe('سارای تازه')
    auth.logout()
    expect(auth.status).toBe('guest')
    expect(auth.currentUser).toBeUndefined()
  })
})
