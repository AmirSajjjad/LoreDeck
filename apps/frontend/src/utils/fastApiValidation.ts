import { z } from 'zod'
import type {
  FieldError,
  NormalizedValidationErrors,
  UnmappedValidationError,
  ValidationLocationSegment,
} from '@/types/validation'

const MALFORMED_VALIDATION_MESSAGE = 'پاسخ اعتبارسنجی سرور قابل پردازش نیست.'
const UNMAPPED_VALIDATION_MESSAGE = 'بخشی از اطلاعات واردشده معتبر نیست.'
const INVALID_FIELD_MESSAGE = 'مقدار واردشده برای این فیلد معتبر نیست.'

const validationEnvelopeSchema = z.object({ detail: z.array(z.unknown()) })
const validationIssueSchema = z.object({
  loc: z.array(z.union([z.string(), z.number().int()])),
  msg: z.string().min(1),
  type: z.string().min(1),
})

function bodyLocationToField(location: ValidationLocationSegment[]): string | undefined {
  if (location[0] !== 'body' || location.length < 2) return undefined

  const segments = location.slice(1)
  const [first, ...rest] = segments
  if (typeof first !== 'string' || !/^[A-Za-z_][A-Za-z0-9_-]*$/.test(first)) return undefined

  let field = first
  for (const segment of rest) {
    if (typeof segment === 'number') {
      if (segment < 0) return undefined
      field += `[${segment}]`
      continue
    }

    if (!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(segment)) return undefined
    field += `.${segment}`
  }

  return field
}

function getFieldMessage(code: string): string {
  if (code === 'missing') return 'وارد کردن این فیلد الزامی است.'
  if (code === 'string_too_short') return 'مقدار واردشده کوتاه‌تر از حد مجاز است.'
  if (code === 'string_too_long') return 'مقدار واردشده طولانی‌تر از حد مجاز است.'
  return INVALID_FIELD_MESSAGE
}

export function normalizeFastApiValidationErrors(payload: unknown): NormalizedValidationErrors {
  const envelope = validationEnvelopeSchema.safeParse(payload)
  if (!envelope.success) {
    return { fieldErrors: [], unmappedErrors: [], formMessage: MALFORMED_VALIDATION_MESSAGE }
  }

  const fieldErrors: FieldError[] = []
  const unmappedErrors: UnmappedValidationError[] = []
  let hasMalformedIssue = false

  for (const rawIssue of envelope.data.detail) {
    const parsedIssue = validationIssueSchema.safeParse(rawIssue)
    if (!parsedIssue.success) {
      hasMalformedIssue = true
      continue
    }

    const issue = parsedIssue.data
    const field = bodyLocationToField(issue.loc)
    if (field) {
      fieldErrors.push({ field, message: getFieldMessage(issue.type), code: issue.type })
    } else {
      unmappedErrors.push({ location: issue.loc, message: issue.msg, code: issue.type })
    }
  }

  const formMessage = hasMalformedIssue
    ? MALFORMED_VALIDATION_MESSAGE
    : unmappedErrors.length > 0 || (fieldErrors.length === 0 && envelope.data.detail.length === 0)
      ? UNMAPPED_VALIDATION_MESSAGE
      : undefined

  return { fieldErrors, unmappedErrors, formMessage }
}
