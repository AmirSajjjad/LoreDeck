import { z } from 'zod'
import { REQUIRED_TEXT_MESSAGE } from '@/utils/validation'

const nullableTextField = (maximum: number, message: string) =>
  z.string().trim().max(maximum, message)

export const profileFormSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, REQUIRED_TEXT_MESSAGE)
    .max(255, 'نام کاربری نمی‌تواند بیشتر از ۲۵۵ نویسه باشد.'),
  phone_number: z
    .string()
    .trim()
    .max(16, 'شماره تلفن نمی‌تواند بیشتر از ۱۶ نویسه باشد.')
    .refine(
      (value) => value === '' || /^\+[1-9]\d{7,14}$/.test(value),
      'شماره تلفن باید با قالب بین‌المللی مانند ‎+989121234567 باشد.',
    ),
  profile_pic: nullableTextField(500, 'مرجع تصویر نمی‌تواند بیشتر از ۵۰۰ نویسه باشد.'),
  name: nullableTextField(255, 'نام نمی‌تواند بیشتر از ۲۵۵ نویسه باشد.'),
  email: z
    .string()
    .trim()
    .toLowerCase()
    .refine(
      (value) => value === '' || z.string().email().safeParse(value).success,
      'نشانی ایمیل معتبر نیست.',
    ),
})
