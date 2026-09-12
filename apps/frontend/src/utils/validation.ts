import { z } from 'zod'

export const REQUIRED_TEXT_MESSAGE = 'وارد کردن این فیلد الزامی است.'

export function requiredText(message = REQUIRED_TEXT_MESSAGE) {
  return z.string().trim().min(1, message)
}

export function optionalText() {
  return z.preprocess((value) => {
    if (typeof value !== 'string') return value

    const normalized = value.trim()
    return normalized === '' ? undefined : normalized
  }, z.string().optional())
}
