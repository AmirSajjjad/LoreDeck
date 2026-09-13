<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useReadingResultState } from '@/features/readings/readingResultState'

const { currentResult } = useReadingResultState()
</script>

<template>
  <section class="mx-auto w-full max-w-3xl" aria-label="نتیجهٔ خوانش">
    <EmptyState
      v-if="!currentResult"
      title="نتیجه‌ای برای نمایش وجود ندارد"
      message="این نتیجه فقط تا زمانی که صفحه باز است در حافظه نگه داشته می‌شود. یک خوانش تازه بسازید."
    >
      <RouterLink
        class="font-semibold text-accent hover:underline"
        :to="{ name: 'reading-create' }"
      >
        ساخت خوانش تازه
      </RouterLink>
    </EmptyState>
    <BaseCard v-else elevated>
      <p class="text-sm font-semibold text-accent">خوانش آماده است</p>
      <h1 id="reading-result-heading" class="mt-2 text-3xl font-bold">کارت‌های شما انتخاب شدند</h1>
      <p class="mt-4 text-muted">نمایش کامل کارت‌ها و تفسیر خوانش در فاز بعد تکمیل می‌شود.</p>
      <p class="mt-5 text-sm text-muted" role="status">
        {{ currentResult.cards.length }} کارت برای این خوانش آماده است.
      </p>
    </BaseCard>
  </section>
</template>
