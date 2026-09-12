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
import { signupSchema } from '@/features/auth/schemas/authSchemas'
import type { SignupFormValues, SignupRequest } from '@/features/auth/types'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/types/api'

const emit = defineEmits<{ authenticated: [] }>()
const auth = useAuthStore()
const submissionError = ref<string>()

const { handleSubmit, isSubmitting, setFieldError } = useForm<SignupFormValues>({
  validationSchema: toTypedSchema(signupSchema),
  initialValues: {
    username: '',
    password: '',
    passwordConfirmation: '',
    phone_number: '',
    name: '',
    email: '',
  },
})

const { formError, applyFieldErrors, clearFormError } = useFastApiValidationErrors(
  ['username', 'password', 'phone_number', 'name', 'email'] as const,
  setFieldError,
)
const visibleError = computed(() => formError.value ?? submissionError.value)

const submit = handleSubmit(async (values) => {
  submissionError.value = undefined
  clearFormError()
  const request: SignupRequest = {
    username: values.username,
    password: values.password,
    phone_number: values.phone_number,
    name: values.name,
    email: values.email,
  }

  try {
    await auth.signup(request)
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
  <BaseCard class="m-auto w-full max-w-xl" elevated>
    <template #header>
      <p class="text-sm font-semibold text-accent">آغاز روایت</p>
      <h1 class="mt-2 text-3xl font-bold">ساخت حساب</h1>
      <p class="mt-3 text-sm text-muted">فیلدهای ستاره‌دار الزامی هستند.</p>
    </template>

    <form class="grid gap-5" novalidate @submit="submit">
      <BaseAlert v-if="visibleError" variant="destructive" title="ثبت‌نام انجام نشد">{{
        visibleError
      }}</BaseAlert>
      <ValidatedInput
        id="signup-username"
        name="username"
        label="نام کاربری"
        autocomplete="username"
        required
        :loading="isSubmitting"
      />
      <div class="grid gap-5 sm:grid-cols-2">
        <ValidatedInput
          id="signup-password"
          name="password"
          label="رمز عبور"
          type="password"
          autocomplete="new-password"
          hint="دست‌کم ۸ نویسه"
          required
          :loading="isSubmitting"
        />
        <ValidatedInput
          id="signup-password-confirmation"
          name="passwordConfirmation"
          label="تکرار رمز عبور"
          type="password"
          autocomplete="new-password"
          required
          :loading="isSubmitting"
        />
      </div>
      <ValidatedInput
        id="signup-name"
        name="name"
        label="نام نمایشی (اختیاری)"
        autocomplete="name"
        :loading="isSubmitting"
      />
      <ValidatedInput
        id="signup-email"
        name="email"
        label="ایمیل (اختیاری)"
        type="email"
        autocomplete="email"
        :loading="isSubmitting"
      />
      <ValidatedInput
        id="signup-phone"
        name="phone_number"
        label="شماره تلفن (اختیاری)"
        type="tel"
        autocomplete="tel"
        placeholder="+989121234567"
        hint="با کد کشور و بدون فاصله"
        dir="ltr"
        :loading="isSubmitting"
      />
      <BaseButton class="w-full" type="submit" :loading="isSubmitting">ساخت حساب</BaseButton>
    </form>

    <template #footer>
      <p class="text-center text-sm text-muted">
        قبلاً ثبت‌نام کرده‌اید؟
        <RouterLink class="font-semibold text-accent hover:underline" :to="{ name: 'sign-in' }"
          >وارد شوید</RouterLink
        >
      </p>
    </template>
  </BaseCard>
</template>
