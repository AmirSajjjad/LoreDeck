<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import { getReadingHistoryDetail } from '@/features/readings/api'
import ReadingResultCard from '@/features/readings/components/ReadingResultCard.vue'
import type { ReadingHistoryDetail } from '@/features/readings/types'
import { ApiError } from '@/types/api'

const route = useRoute()
const detail = ref<ReadingHistoryDetail>()
const loading = ref(true)
const errorMessage = ref<string>()
const historyId = computed(() => Number(route.params.historyId))

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('fa-IR', { dateStyle: 'long', timeStyle: 'short' }).format(
    new Date(value),
  )
}

async function loadDetail(): Promise<void> {
  if (!Number.isSafeInteger(historyId.value) || historyId.value <= 0) {
    loading.value = false
    errorMessage.value = 'این خوانش پیدا نشد.'
    return
  }
  loading.value = true
  errorMessage.value = undefined
  try {
    detail.value = await getReadingHistoryDetail(historyId.value)
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError && error.category === 'not-found'
        ? 'این خوانش پیدا نشد.'
        : error instanceof ApiError
          ? error.message
          : 'دریافت خوانش با خطا روبه‌رو شد.'
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<template>
  <LoadingState v-if="loading" message="در حال دریافت خوانش…" />
  <ErrorState
    v-else-if="errorMessage"
    title="خوانش در دسترس نیست"
    :message="errorMessage"
    retryable
    @retry="loadDetail"
  />
  <section
    v-else-if="detail"
    class="mx-auto grid w-full max-w-6xl gap-8"
    aria-labelledby="history-detail-heading"
  >
    <header class="text-center">
      <p class="break-words text-sm font-semibold text-accent">{{ detail.deck.title }}</p>
      <h1 id="history-detail-heading" class="mt-2 text-3xl font-bold">خوانش ذخیره‌شده</h1>
      <time class="mt-3 block text-sm text-muted" :datetime="detail.created_at">{{
        formatDate(detail.created_at)
      }}</time>
      <p
        v-if="detail.question"
        class="mx-auto mt-5 max-w-3xl whitespace-pre-line break-words text-lg"
      >
        {{ detail.question }}
      </p>
    </header>
    <div
      class="grid items-start gap-6"
      :class="detail.cards.length === 1 ? 'mx-auto w-full max-w-sm' : 'md:grid-cols-3'"
    >
      <ReadingResultCard v-for="card in detail.cards" :key="card.position" :item="card" />
    </div>
    <BaseCard v-if="detail.summary?.trim()" class="mx-auto w-full max-w-3xl" elevated>
      <h2 class="text-2xl font-bold">جمع‌بندی خوانش</h2>
      <p class="mt-4 whitespace-pre-line break-words leading-8 text-muted">{{ detail.summary }}</p>
    </BaseCard>
    <nav class="flex flex-col justify-center gap-3 sm:flex-row" aria-label="اقدام‌های تاریخچه">
      <RouterLink
        class="font-semibold text-accent hover:underline"
        :to="{ name: 'reading-history' }"
        >بازگشت به تاریخچه</RouterLink
      >
      <RouterLink class="font-semibold text-accent hover:underline" :to="{ name: 'reading-create' }"
        >خوانش تازه</RouterLink
      >
    </nav>
  </section>
</template>
