import type { z } from 'zod'
import type { PublicUser } from '@/features/auth/types'
import type { profileFormSchema } from '@/features/profile/schemas/profileSchema'

export type Profile = PublicUser
export type ProfileFormValues = z.infer<typeof profileFormSchema>

export interface ProfileUpdateRequest {
  username?: string
  phone_number?: string | null
  profile_pic?: string | null
  name?: string | null
  email?: string | null
}
