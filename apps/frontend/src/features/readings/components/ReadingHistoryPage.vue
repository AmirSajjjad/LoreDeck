<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import { getReadingHistory } from '@/features/readings/api'
import type { ReadingHistoryPage } from '@/features/readings/types'
import { ApiError } from '@/types/api'

const PAGE_SIZE = 20
const route = useRoute()
const router = useRouter()
const page = ref<ReadingHistoryPage>()
const loading = ref(true)
const errorMessage = ref<string>()

function normalizeOffset(value: unknown): number {
  const parsed = typeof value === 'string' && /^\d+$/.test(value) ? Number(value) : 0
  return Number.isSafeInteger(parsed) ? Math.floor(parsed / PAGE_SIZE) * PAGE_SIZE : 0
}

const offset = computed(() => normalizeOffset(route.query.offset))
const hasPrevious = computed(() => offset.value > 0)
const hasNext = computed(() => !!page.value && offset.value + page.value.limit < page.value.total)

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('fa-IR', { dateStyle: 'medium', timeStyle: 'short' }).format(
    new Date(value),
  )
}

function spreadLabel(spread: 'one_card' | 'three_card'): string {
  return spread === 'one_card' ? 'یک‌کارتی' : 'سه‌کارتی'
}

async function loadHistory(): Promise<void> {
  loading.value = true
  errorMessage.value = undefined
  try {
    page.value = await getReadingHistory(PAGE_SIZE, offset.value)
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'دریافت تاریخچه با خطا روبه‌رو شد.'
  } finally {
    loading.value = false
  }
}

function navigate(nextOffset: number): void {
  void router.push({ name: 'reading-history', query: nextOffset ? { offset: nextOffset } : {} })
}

watch(
  () => route.query.offset,
  (value) => {
    const validOffset = normalizeOffset(value)
    if (String(validOffset) !== value && !(validOffset === 0 && value === undefined)) {
      void router.replace({
        name: 'reading-history',
        query: validOffset ? { offset: validOffset } : {},
      })
      return
    }
    void loadHistory()
  },
  { immediate: true },
)
</script>

<template>
  <section class="mx-auto grid w-full max-w-4xl gap-6" aria-labelledby="history-heading">
    <header>
      <p class="text-sm font-semibold text-accent">حساب کاربری</p>
      <h1 id="history-heading" class="mt-2 text-3xl font-bold">تاریخچهٔ خوانش‌ها</h1>
    </header>
    <LoadingState v-if="loading" message="در حال دریافت تاریخچه…" />
    <ErrorState
      v-else-if="errorMessage"
      title="تاریخچه دریافت نشد"
      :message="errorMessage"
      retryable
      @retry="loadHistory"
    />
    <EmptyState
      v-else-if="!page?.items.length"
      title="هنوز خوانشی ذخیره نشده"
      message="خوانش‌هایی که با حساب کاربری انجام می‌دهید اینجا نمایش داده می‌شوند."
    >
      <RouterLink class="font-semibold text-accent hover:underline" :to="{ name: 'reading-create' }"
        >ساخت خوانش تازه</RouterLink
      >
    </EmptyState>
    <template v-else>
      <ol class="grid gap-4">
        <li v-for="item in page.items" :key="item.id">
          <BaseCard>
            <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div class="min-w-0">
                <p class="break-words font-semibold text-accent">{{ item.deck.title }}</p>
                <p class="mt-2 break-words">{{ item.question || 'بدون پرسش' }}</p>
                <p class="mt-2 text-sm text-muted">
                  {{ spreadLabel(item.spread) }} ·
                  <time :datetime="item.created_at">{{ formatDate(item.created_at) }}</time>
                </p>
              </div>
              <RouterLink
                class="shrink-0 font-semibold text-accent hover:underline"
                :to="{ name: 'reading-history-detail', params: { historyId: item.id } }"
                >مشاهدهٔ خوانش</RouterLink
              >
            </div>
          </BaseCard>
        </li>
      </ol>
      <nav class="flex items-center justify-between gap-3" aria-label="صفحه‌بندی تاریخچه">
        <BaseButton
          variant="secondary"
          :disabled="!hasPrevious"
          @click="navigate(Math.max(0, offset - PAGE_SIZE))"
          >صفحهٔ قبل</BaseButton
        >
        <span class="text-sm text-muted"
          >{{ offset + 1 }} تا {{ Math.min(offset + PAGE_SIZE, page.total) }} از
          {{ page.total }}</span
        >
        <BaseButton variant="secondary" :disabled="!hasNext" @click="navigate(offset + PAGE_SIZE)"
          >صفحهٔ بعد</BaseButton
        >
      </nav>
    </template>
  </section>
</template>
