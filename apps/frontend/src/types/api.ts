import type { FieldError } from '@/types/validation'

export type ApiErrorCategory =
  | 'network'
  | 'timeout'
  | 'unauthorized'
  | 'forbidden'
  | 'validation'
  | 'not-found'
  | 'conflict'
  | 'server'
  | 'http'
  | 'unexpected'

export class ApiError extends Error {
  readonly category: ApiErrorCategory
  readonly status?: number
  readonly fieldErrors: FieldError[]

  constructor(
    category: ApiErrorCategory,
    message: string,
    options: { status?: number; fieldErrors?: FieldError[] } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.category = category
    this.status = options.status
    this.fieldErrors = options.fieldErrors ?? []
  }
}
