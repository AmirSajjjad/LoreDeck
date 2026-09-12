import { ref } from 'vue'
import type { FieldError } from '@/types/validation'
import { normalizeFastApiValidationErrors } from '@/utils/fastApiValidation'

type SetFieldError<TField extends string> = (field: TField, message: string | undefined) => void

export function useFastApiValidationErrors<TField extends string>(
  fields: readonly TField[],
  setFieldError: SetFieldError<TField>,
) {
  const formError = ref<string>()
  const knownFields = new Set<string>(fields)

  function applyFieldErrors(errors: readonly FieldError[], fallbackMessage?: string): void {
    const unmappedFieldError = errors.some((error) => {
      if (!knownFields.has(error.field)) return true

      setFieldError(error.field as TField, error.message)
      return false
    })

    formError.value =
      fallbackMessage ??
      (unmappedFieldError ? 'بخشی از خطاهای فرم به فیلد مشخصی مرتبط نشد.' : undefined)
  }

  function applyValidationErrors(payload: unknown): void {
    const normalized = normalizeFastApiValidationErrors(payload)
    applyFieldErrors(normalized.fieldErrors, normalized.formMessage)
  }

  function clearFormError(): void {
    formError.value = undefined
  }

  return { formError, applyFieldErrors, applyValidationErrors, clearFormError }
}
