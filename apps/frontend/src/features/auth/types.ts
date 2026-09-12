import type { z } from 'zod'
import type {
  authenticationResponseSchema,
  publicUserSchema,
  signinSchema,
  signupRequestSchema,
  signupSchema,
} from '@/features/auth/schemas/authSchemas'

export type SigninRequest = z.infer<typeof signinSchema>
export type SignupRequest = z.infer<typeof signupRequestSchema>
export type SignupFormValues = z.infer<typeof signupSchema>
export type AuthenticationResponse = z.infer<typeof authenticationResponseSchema>
export type PublicUser = z.infer<typeof publicUserSchema>
