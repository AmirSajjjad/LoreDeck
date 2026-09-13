import { apiClient } from '@/api/client'
import { API_ERROR_MESSAGES } from '@/api/messages'
import { publicUserSchema } from '@/features/auth/schemas/authSchemas'
import type { Profile, ProfileUpdateRequest } from '@/features/profile/types'
import { ApiError } from '@/types/api'

function parseProfile(data: unknown): Profile {
  const result = publicUserSchema.safeParse(data)
  if (!result.success) throw new ApiError('unexpected', API_ERROR_MESSAGES.unexpected)
  return result.data
}

export async function getProfile(): Promise<Profile> {
  const response = await apiClient.get<unknown>('/users/profile')
  return parseProfile(response.data)
}

export async function updateProfile(request: ProfileUpdateRequest): Promise<Profile> {
  const response = await apiClient.patch<unknown>('/users/profile', request)
  return parseProfile(response.data)
}
