import { z } from 'zod'
import { REQUIRED_TEXT_MESSAGE } from '@/utils/validation'

const usernameSchema = z
  .string()
  .trim()
  .min(1, REQUIRED_TEXT_MESSAGE)
  .max(255, 'نام کاربری نمی‌تواند بیشتر از ۲۵۵ نویسه باشد.')

const optionalNameSchema = z.preprocess(
  (value) => (typeof value === 'string' && value.trim() === '' ? undefined : value),
  z.string().trim().max(255, 'نام نمی‌تواند بیشتر از ۲۵۵ نویسه باشد.').optional(),
)

const optionalEmailSchema = z.preprocess((value) => {
  if (typeof value !== 'string') return value
  const normalized = value.trim().toLowerCase()
  return normalized === '' ? undefined : normalized
}, z.string().email('نشانی ایمیل معتبر نیست.').optional())

const optionalPhoneSchema = z.preprocess(
  (value) => (typeof value === 'string' && value.trim() === '' ? undefined : value),
  z
    .string()
    .trim()
    .max(16, 'شماره تلفن نمی‌تواند بیشتر از ۱۶ نویسه باشد.')
    .regex(/^\+[1-9]\d{7,14}$/, 'شماره تلفن باید با قالب بین‌المللی مانند ‎+989121234567 باشد.')
    .optional(),
)

export const signinSchema = z.object({
  username: usernameSchema,
  password: z.string().min(1, REQUIRED_TEXT_MESSAGE),
})

export const signupRequestSchema = z.object({
  username: usernameSchema,
  password: z.string().min(8, 'رمز عبور باید دست‌کم ۸ نویسه باشد.'),
  phone_number: optionalPhoneSchema,
  name: optionalNameSchema,
  email: optionalEmailSchema,
})

export const signupSchema = signupRequestSchema
  .extend({ passwordConfirmation: z.string().min(1, 'تکرار رمز عبور الزامی است.') })
  .refine((values) => values.password === values.passwordConfirmation, {
    path: ['passwordConfirmation'],
    message: 'تکرار رمز عبور با رمز عبور یکسان نیست.',
  })

export const publicUserSchema = z.object({
  id: z.number().int(),
  username: z.string(),
  phone_number: z.string().nullable(),
  profile_pic: z.string().nullable(),
  name: z.string().nullable(),
  email: z.string().nullable(),
  telegram_id: z.number().int().nullable(),
  created_at: z.string().datetime({ offset: true }),
})

export const authenticationResponseSchema = z.object({
  access_token: z.string().min(1),
  token_type: z.literal('bearer'),
  expires_in: z.number().int().positive(),
  user: publicUserSchema,
})
