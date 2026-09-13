<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import { getDecks } from '@/features/readings/api'
import ReadingForm from '@/features/readings/components/ReadingForm.vue'
import { useReadingResultState } from '@/features/readings/readingResultState'
import type { Deck, ReadingResponse } from '@/features/readings/types'
import { ApiError } from '@/types/api'

const router = useRouter()
const { setResult, clearResult } = useReadingResultState()
const decks = ref<Deck[]>([])
const loading = ref(true)
const loadError = ref<string>()

async function loadDecks(preserveCurrent = false): Promise<void> {
  if (!preserveCurrent) loading.value = true
  loadError.value = undefined
  try {
    decks.value = await getDecks()
  } catch (error) {
    if (!preserveCurrent || decks.value.length === 0) {
      loadError.value =
        error instanceof ApiError ? error.message : 'دریافت دسته‌ها با خطا روبه‌رو شد.'
    }
  } finally {
    loading.value = false
  }
}

function handleCreated(result: ReadingResponse): void {
  setResult(result)
  void router.push({ name: 'reading-result' })
}

onMounted(() => {
  clearResult()
  void loadDecks()
})
</script>

<template>
  <section class="mx-auto grid w-full max-w-3xl gap-6" aria-labelledby="create-reading-heading">
    <header>
      <p class="text-sm font-semibold text-accent">خوانش تازه</p>
      <h1 id="create-reading-heading" class="mt-2 text-3xl font-bold">
        پرسش خود را با کارت‌ها در میان بگذارید
      </h1>
      <p class="mt-3 text-muted">
        دسته و چیدمان را انتخاب کنید. ورود به حساب برای شروع الزامی نیست.
      </p>
    </header>

    <LoadingState v-if="loading" message="در حال دریافت دسته‌های کارت…" />
    <ErrorState
      v-else-if="loadError"
      title="دسته‌ها دریافت نشدند"
      :message="loadError"
      retryable
      @retry="loadDecks()"
    />
    <EmptyState
      v-else-if="decks.length === 0"
      title="دسته‌ای در دسترس نیست"
      message="در حال حاضر دستهٔ فعالی برای خوانش وجود ندارد."
    >
      <BaseButton variant="secondary" @click="loadDecks()">بررسی دوباره</BaseButton>
    </EmptyState>
    <ReadingForm
      v-else
      :decks="decks"
      @created="handleCreated"
      @deck-unavailable="loadDecks(true)"
    />
  </section>
</template>
