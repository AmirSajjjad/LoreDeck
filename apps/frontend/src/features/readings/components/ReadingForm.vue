<script setup lang="ts">
import { computed, ref } from 'vue'
import { toTypedSchema } from '@vee-validate/zod'
import { useField, useForm } from 'vee-validate'
import { API_ERROR_MESSAGES } from '@/api/messages'
import BaseAlert from '@/components/common/BaseAlert.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import ValidatedSelect from '@/components/common/ValidatedSelect.vue'
import ValidatedTextarea from '@/components/common/ValidatedTextarea.vue'
import { useFastApiValidationErrors } from '@/composables/useFastApiValidationErrors'
import { createReading } from '@/features/readings/api'
import { readingFormSchema } from '@/features/readings/schemas/readingSchemas'
import type { Deck, ReadingFormValues, ReadingResponse, Spread } from '@/features/readings/types'
import { toReadingRequest } from '@/features/readings/utils/readingRequest'
import { ApiError } from '@/types/api'

const props = defineProps<{ decks: readonly Deck[] }>()
const emit = defineEmits<{
  created: [result: ReadingResponse]
  'deck-unavailable': []
}>()

const submissionError = ref<string>()
const { handleSubmit, isSubmitting, setFieldError } = useForm<ReadingFormValues>({
  validationSchema: toTypedSchema(readingFormSchema),
  initialValues: { deck_id: '', spread: 'one_card', question: '' },
})
const { value: spread, errorMessage: spreadError } = useField<Spread>('spread')
const { formError, applyFieldErrors, clearFormError } = useFastApiValidationErrors(
  ['deck_id', 'spread', 'question'] as const,
  setFieldError,
)
const visibleError = computed(() => formError.value ?? submissionError.value)
const deckOptions = computed(() =>
  props.decks.map((deck) => ({ value: String(deck.id), label: deck.title })),
)

const submit = handleSubmit(async (values) => {
  submissionError.value = undefined
  clearFormError()

  try {
    emit('created', await createReading(toReadingRequest(values)))
  } catch (error) {
    if (!(error instanceof ApiError)) {
      submissionError.value = API_ERROR_MESSAGES.unexpected
      return
    }
    if (error.category === 'validation') {
      applyFieldErrors(error.fieldErrors, error.fieldErrors.length ? undefined : error.message)
      return
    }
    if (error.category === 'not-found') {
      setFieldError('deck_id', 'این دسته دیگر در دسترس نیست؛ دستهٔ دیگری انتخاب کنید.')
      submissionError.value = 'دستهٔ انتخاب‌شده در دسترس نیست؛ فهرست در حال به‌روزرسانی است.'
      emit('deck-unavailable')
      return
    }
    if (error.category === 'conflict') {
      submissionError.value = 'این دسته کارت فعال کافی برای چیدمان انتخاب‌شده ندارد.'
      return
    }
    submissionError.value = error.message
  }
})
</script>

<template>
  <BaseCard elevated>
    <form class="grid gap-6" novalidate @submit="submit">
      <BaseAlert v-if="visibleError" variant="destructive" title="خوانش ساخته نشد">
        {{ visibleError }}
      </BaseAlert>

      <ValidatedSelect
        id="reading-deck"
        name="deck_id"
        label="دستهٔ کارت"
        placeholder="یک دسته را انتخاب کنید"
        hint="فقط دسته‌های فعال نمایش داده می‌شوند."
        :options="deckOptions"
        required
        :loading="isSubmitting"
      />

      <fieldset
        class="grid gap-3"
        :disabled="isSubmitting"
        :aria-invalid="spreadError ? true : undefined"
        :aria-describedby="spreadError ? 'reading-spread-error' : undefined"
      >
        <legend class="font-medium">چیدمان <span class="text-destructive">*</span></legend>
        <div class="grid gap-3 sm:grid-cols-2">
          <label
            class="flex cursor-pointer gap-3 rounded-card border border-line bg-elevated p-4 hover:border-accent/60"
          >
            <input
              v-model="spread"
              type="radio"
              name="spread"
              value="one_card"
              class="mt-1 accent-accent"
            />
            <span
              ><strong class="block">یک‌کارتی</strong
              ><span class="mt-1 block text-sm text-muted"
                >یک نگاه کوتاه به لحظهٔ اکنون.</span
              ></span
            >
          </label>
          <label
            class="flex cursor-pointer gap-3 rounded-card border border-line bg-elevated p-4 hover:border-accent/60"
          >
            <input
              v-model="spread"
              type="radio"
              name="spread"
              value="three_card"
              class="mt-1 accent-accent"
            />
            <span
              ><strong class="block">سه‌کارتی</strong
              ><span class="mt-1 block text-sm text-muted"
                >گذشته، اکنون و آیندهٔ مسیر پرسش.</span
              ></span
            >
          </label>
        </div>
        <p
          v-if="spreadError"
          id="reading-spread-error"
          class="text-sm text-destructive"
          role="alert"
        >
          {{ spreadError }}
        </p>
      </fieldset>

      <ValidatedTextarea
        id="reading-question"
        name="question"
        label="پرسش (اختیاری)"
        placeholder="پرسش یا موضوعی که در ذهن دارید…"
        hint="می‌توانید این بخش را خالی بگذارید."
        :loading="isSubmitting"
      />

      <BaseButton
        class="w-full sm:w-auto"
        type="submit"
        :loading="isSubmitting"
        loading-label="در حال انتخاب کارت‌ها"
      >
        آغاز خوانش
      </BaseButton>
    </form>
  </BaseCard>
</template>
