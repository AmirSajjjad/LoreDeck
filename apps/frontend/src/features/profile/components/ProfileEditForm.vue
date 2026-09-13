<script setup lang="ts">
import { computed, ref } from 'vue'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { API_ERROR_MESSAGES } from '@/api/messages'
import BaseAlert from '@/components/common/BaseAlert.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import ValidatedInput from '@/components/common/ValidatedInput.vue'
import { useFastApiValidationErrors } from '@/composables/useFastApiValidationErrors'
import { updateProfile } from '@/features/profile/api'
import { profileFormSchema } from '@/features/profile/schemas/profileSchema'
import type { Profile, ProfileFormValues } from '@/features/profile/types'
import { createProfileUpdate, profileToFormValues } from '@/features/profile/utils/profileUpdate'
import { ApiError } from '@/types/api'

const props = defineProps<{ profile: Profile }>()
const emit = defineEmits<{ updated: [profile: Profile]; cancel: [] }>()
const submissionError = ref<string>()
const notice = ref<string>()

const { handleSubmit, isSubmitting, setFieldError } = useForm<ProfileFormValues>({
  validationSchema: toTypedSchema(profileFormSchema),
  initialValues: profileToFormValues(props.profile),
})

const fields = ['username', 'phone_number', 'profile_pic', 'name', 'email'] as const
const { formError, applyFieldErrors, clearFormError } = useFastApiValidationErrors(
  fields,
  setFieldError,
)
const visibleError = computed(() => formError.value ?? submissionError.value)

const submit = handleSubmit(async (values) => {
  submissionError.value = undefined
  notice.value = undefined
  clearFormError()

  const request = createProfileUpdate(values, props.profile)
  if (Object.keys(request).length === 0) {
    notice.value = 'تغییری برای ذخیره وجود ندارد.'
    return
  }

  try {
    emit('updated', await updateProfile(request))
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
  <form class="grid gap-5" novalidate @submit="submit">
    <BaseAlert v-if="visibleError" variant="destructive" title="ذخیره انجام نشد">{{
      visibleError
    }}</BaseAlert>
    <BaseAlert v-if="notice" variant="info">{{ notice }}</BaseAlert>
    <ValidatedInput
      id="profile-username"
      name="username"
      label="نام کاربری"
      autocomplete="username"
      required
      :loading="isSubmitting"
    />
    <ValidatedInput
      id="profile-name"
      name="name"
      label="نام نمایشی"
      autocomplete="name"
      hint="برای حذف نام نمایشی، این فیلد را خالی بگذارید."
      :loading="isSubmitting"
    />
    <ValidatedInput
      id="profile-email"
      name="email"
      label="ایمیل"
      type="email"
      autocomplete="email"
      hint="برای حذف ایمیل، این فیلد را خالی بگذارید."
      dir="ltr"
      :loading="isSubmitting"
    />
    <ValidatedInput
      id="profile-phone"
      name="phone_number"
      label="شماره تلفن"
      type="tel"
      autocomplete="tel"
      placeholder="+989121234567"
      hint="شماره را با کد کشور وارد کنید؛ برای حذف، فیلد را خالی بگذارید."
      dir="ltr"
      :loading="isSubmitting"
    />
    <ValidatedInput
      id="profile-picture"
      name="profile_pic"
      label="نشانی تصویر نمایه"
      type="url"
      autocomplete="url"
      hint="بارگذاری فایل پشتیبانی نمی‌شود؛ یک نشانی تصویر وارد کنید یا برای حذف، فیلد را خالی بگذارید."
      dir="ltr"
      :loading="isSubmitting"
    />
    <div class="flex flex-col-reverse gap-3 sm:flex-row">
      <BaseButton variant="secondary" :disabled="isSubmitting" @click="emit('cancel')"
        >انصراف</BaseButton
      >
      <BaseButton type="submit" :loading="isSubmitting" loading-label="در حال ذخیره"
        >ذخیره تغییرات</BaseButton
      >
    </div>
  </form>
</template>
