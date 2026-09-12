export type ValidationLocationSegment = string | number

export interface FieldError {
  field: string
  message: string
  code: string
}

export interface UnmappedValidationError {
  location: ValidationLocationSegment[]
  message: string
  code: string
}

export interface NormalizedValidationErrors {
  fieldErrors: FieldError[]
  unmappedErrors: UnmappedValidationError[]
  formMessage?: string
}
