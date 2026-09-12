<script setup lang="ts">
import { computed, ref } from 'vue'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { RouterLink } from 'vue-router'
import { API_ERROR_MESSAGES } from '@/api/messages'
import BaseAlert from '@/components/common/BaseAlert.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import ValidatedInput from '@/components/common/ValidatedInput.vue'
import { useFastApiValidationErrors } from '@/composables/useFastApiValidationErrors'
import { signinSchema } from '@/features/auth/schemas/authSchemas'
import type { SigninRequest } from '@/features/auth/types'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/types/api'

const emit = defineEmits<{ authenticated: [] }>()
const auth = useAuthStore()
const submissionError = ref<string>()

const { handleSubmit, isSubmitting, setFieldError } = useForm<SigninRequest>({
  validationSchema: toTypedSchema(signinSchema),
  initialValues: { username: '', password: '' },
})

const { formError, applyFieldErrors, clearFormError } = useFastApiValidationErrors(
  ['username', 'password'] as const,
  setFieldError,
)
const visibleError = computed(() => formError.value ?? submissionError.value)

const submit = handleSubmit(async (values) => {
  submissionError.value = undefined
  clearFormError()

  try {
    await auth.signin(values)
    emit('authenticated')
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.category === 'validation') {
        applyFieldErrors(error.fieldErrors, error.fieldErrors.length ? undefined : error.message)
      } else {
        submissionError.value = error.message
      }
      return
    }

    submissionError.value = API_ERROR_MESSAGES.unexpected
  }
})
</script>

<template>
  <BaseCard class="m-auto w-full max-w-md" elevated>
    <template #header>
      <p class="text-sm font-semibold text-accent">بازگشت به لور دک</p>
      <h1 class="mt-2 text-3xl font-bold">ورود به حساب</h1>
      <p class="mt-3 text-sm text-muted">نام کاربری و رمز عبور خود را وارد کنید.</p>
    </template>

    <form class="grid gap-5" novalidate @submit="submit">
      <BaseAlert v-if="visibleError" variant="destructive" title="ورود انجام نشد">
        {{ visibleError }}
      </BaseAlert>
      <ValidatedInput
        id="signin-username"
        name="username"
        label="نام کاربری"
        autocomplete="username"
        required
        :loading="isSubmitting"
      />
      <ValidatedInput
        id="signin-password"
        name="password"
        label="رمز عبور"
        type="password"
        autocomplete="current-password"
        required
        :loading="isSubmitting"
      />
      <BaseButton class="w-full" type="submit" :loading="isSubmitting">ورود</BaseButton>
    </form>

    <template #footer>
      <p class="text-center text-sm text-muted">
        حساب ندارید؟
        <RouterLink class="font-semibold text-accent hover:underline" :to="{ name: 'sign-up' }"
          >ثبت‌نام کنید</RouterLink
        >
      </p>
    </template>
  </BaseCard>
</template>
