import { API_ERROR_MESSAGES } from '@/api/messages'
import { apiClient } from '@/api/client'
import { authenticationResponseSchema, publicUserSchema } from '@/features/auth/schemas/authSchemas'
import type {
  AuthenticationResponse,
  PublicUser,
  SigninRequest,
  SignupRequest,
} from '@/features/auth/types'
import { ApiError } from '@/types/api'

function parseAuthenticationResponse(data: unknown): AuthenticationResponse {
  const result = authenticationResponseSchema.safeParse(data)
  if (!result.success) throw new ApiError('unexpected', API_ERROR_MESSAGES.unexpected)
  return result.data
}

export async function signin(request: SigninRequest): Promise<AuthenticationResponse> {
  const response = await apiClient.post<unknown>('/users/signin', request)
  return parseAuthenticationResponse(response.data)
}

export async function signup(request: SignupRequest): Promise<AuthenticationResponse> {
  const response = await apiClient.post<unknown>('/users/signup', request)
  return parseAuthenticationResponse(response.data)
}

export async function getCurrentUser(): Promise<PublicUser> {
  const response = await apiClient.get<unknown>('/users/profile')
  const result = publicUserSchema.safeParse(response.data)
  if (!result.success) throw new ApiError('unexpected', API_ERROR_MESSAGES.unexpected)
  return result.data
}
