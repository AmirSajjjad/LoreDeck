import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { resetUnauthorizedEvent } from '@/api/auth'
import { signin as requestSignin, signup as requestSignup } from '@/features/auth/api'
import type { PublicUser, SigninRequest, SignupRequest } from '@/features/auth/types'
import { clearAccessToken, readAccessToken, writeAccessToken } from '@/features/auth/tokenStorage'
import { getProfile } from '@/features/profile/api'
import { ApiError } from '@/types/api'

export type AuthenticationStatus =
  'unknown' | 'initializing' | 'authenticated' | 'guest' | 'unavailable'

export const useAuthStore = defineStore('auth', () => {
  const status = ref<AuthenticationStatus>('unknown')
  const currentUser = ref<PublicUser>()
  let initialization: Promise<void> | undefined

  const isAuthenticated = computed(() => status.value === 'authenticated')
  const isInitializing = computed(
    () => status.value === 'unknown' || status.value === 'initializing',
  )

  function clearSession(): void {
    clearAccessToken()
    currentUser.value = undefined
    status.value = 'guest'
  }

  function acceptAuthentication(accessToken: string, user: PublicUser): void {
    writeAccessToken(accessToken)
    currentUser.value = user
    status.value = 'authenticated'
    resetUnauthorizedEvent()
  }

  async function signin(request: SigninRequest): Promise<void> {
    const response = await requestSignin(request)
    acceptAuthentication(response.access_token, response.user)
  }

  async function signup(request: SignupRequest): Promise<void> {
    const response = await requestSignup(request)
    acceptAuthentication(response.access_token, response.user)
  }

  async function initializeSession(): Promise<void> {
    if (status.value !== 'unknown' && status.value !== 'initializing') return
    if (initialization) return initialization

    status.value = 'initializing'
    initialization = (async () => {
      if (!readAccessToken()) {
        status.value = 'guest'
        return
      }

      try {
        currentUser.value = await getProfile()
        status.value = 'authenticated'
        resetUnauthorizedEvent()
      } catch (error) {
        if (error instanceof ApiError && error.category === 'unauthorized') {
          clearSession()
          return
        }

        currentUser.value = undefined
        status.value = 'unavailable'
      }
    })()

    try {
      await initialization
    } finally {
      initialization = undefined
    }
  }

  function logout(): void {
    clearSession()
  }

  function synchronizeUser(user: PublicUser): void {
    currentUser.value = user
  }

  return {
    status,
    currentUser,
    isAuthenticated,
    isInitializing,
    signin,
    signup,
    initializeSession,
    clearSession,
    logout,
    synchronizeUser,
  }
})
