<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BaseAlert from '@/components/common/BaseAlert.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import { getProfile } from '@/features/profile/api'
import ProfileAvatar from '@/features/profile/components/ProfileAvatar.vue'
import ProfileEditForm from '@/features/profile/components/ProfileEditForm.vue'
import type { Profile } from '@/features/profile/types'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/types/api'

const auth = useAuthStore()
const loading = ref(true)
const loadError = ref<string>()
const editing = ref(false)
const updateSucceeded = ref(false)
const profile = computed(() => auth.currentUser)
const displayName = computed(() => profile.value?.name || profile.value?.username || 'کاربر لور دک')
const createdAt = computed(() =>
  profile.value
    ? new Intl.DateTimeFormat('fa-IR', { dateStyle: 'long' }).format(
        new Date(profile.value.created_at),
      )
    : '',
)

async function loadProfile(): Promise<void> {
  loading.value = true
  loadError.value = undefined
  try {
    auth.synchronizeUser(await getProfile())
  } catch (error) {
    loadError.value =
      error instanceof ApiError ? error.message : 'دریافت اطلاعات نمایه با خطا روبه‌رو شد.'
  } finally {
    loading.value = false
  }
}

function handleUpdated(updatedProfile: Profile): void {
  auth.synchronizeUser(updatedProfile)
  editing.value = false
  updateSucceeded.value = true
}

function startEditing(): void {
  updateSucceeded.value = false
  editing.value = true
}

onMounted(loadProfile)
</script>

<template>
  <LoadingState v-if="loading" message="در حال دریافت نمایه…" />
  <ErrorState
    v-else-if="loadError"
    title="نمایه دریافت نشد"
    :message="loadError"
    retryable
    @retry="loadProfile"
  />
  <section v-else-if="profile" class="mx-auto grid w-full max-w-3xl gap-5">
    <header>
      <p class="text-sm font-semibold text-accent">حساب کاربری</p>
      <h1 class="mt-2 text-3xl font-bold">نمایه من</h1>
      <p class="mt-2 text-muted">اطلاعات نمایه و راه‌های ارتباطی خود را مدیریت کنید.</p>
    </header>
    <BaseAlert v-if="updateSucceeded" variant="success" title="تغییرات ذخیره شد"
      >اطلاعات نمایه شما با موفقیت به‌روز شد.</BaseAlert
    >
    <BaseCard elevated>
      <template #header>
        <div class="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <ProfileAvatar :source="profile.profile_pic" :display-name="displayName" />
          <div class="min-w-0">
            <h2 class="break-words text-2xl font-bold">{{ displayName }}</h2>
            <p class="mt-1 break-all text-muted" dir="ltr">@{{ profile.username }}</p>
          </div>
        </div>
      </template>
      <ProfileEditForm
        v-if="editing"
        :profile="profile"
        @updated="handleUpdated"
        @cancel="editing = false"
      />
      <template v-else>
        <dl class="grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-sm text-muted">نام نمایشی</dt>
            <dd class="mt-1 break-words font-medium">{{ profile.name || 'ثبت نشده' }}</dd>
          </div>
          <div>
            <dt class="text-sm text-muted">ایمیل</dt>
            <dd class="mt-1 break-all font-medium" dir="ltr">{{ profile.email || 'ثبت نشده' }}</dd>
          </div>
          <div>
            <dt class="text-sm text-muted">شماره تلفن</dt>
            <dd class="mt-1 font-medium" dir="ltr">{{ profile.phone_number || 'ثبت نشده' }}</dd>
          </div>
          <div>
            <dt class="text-sm text-muted">عضویت از</dt>
            <dd class="mt-1 font-medium">{{ createdAt }}</dd>
          </div>
        </dl>
        <BaseButton class="mt-6 w-full sm:w-auto" @click="startEditing"> ویرایش نمایه </BaseButton>
      </template>
    </BaseCard>
  </section>
</template>
