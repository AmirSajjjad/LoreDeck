<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import ReadingResultCard from '@/features/readings/components/ReadingResultCard.vue'
import { useReadingResultState } from '@/features/readings/readingResultState'
import { readingResponseSchema } from '@/features/readings/schemas/readingSchemas'

const { currentResult } = useReadingResultState()
const heading = ref<HTMLElement>()
const parsedResult = computed(() => readingResponseSchema.safeParse(currentResult.value))
const result = computed(() => (parsedResult.value.success ? parsedResult.value.data : undefined))
const isMissing = computed(() => currentResult.value === undefined)
const isSingleCard = computed(() => result.value?.cards.length === 1)

onMounted(async () => {
  await nextTick()
  heading.value?.focus()
})
</script>

<template>
  <section class="mx-auto grid w-full max-w-6xl gap-8" aria-label="نتیجهٔ خوانش">
    <BaseCard v-if="!result" class="mx-auto w-full max-w-lg text-center" elevated>
      <p class="text-sm font-semibold text-accent">نتیجهٔ خوانش</p>
      <h1 ref="heading" class="mt-2 text-2xl font-bold" tabindex="-1">
        {{ isMissing ? 'نتیجه‌ای برای نمایش وجود ندارد' : 'نتیجهٔ خوانش قابل نمایش نیست' }}
      </h1>
      <p class="mt-4 text-muted">
        {{
          isMissing
            ? 'نتیجه فقط تا زمانی که صفحه باز است در حافظه نگه داشته می‌شود.'
            : 'پاسخ دریافت‌شده کامل یا معتبر نبود؛ برای ادامه یک خوانش تازه بسازید.'
        }}
      </p>
      <RouterLink
        class="mt-6 inline-flex min-h-11 items-center justify-center rounded-control border border-accent bg-accent px-5 py-2.5 font-semibold text-accent-contrast transition-colors hover:bg-accent/90"
        :to="{ name: 'reading-create' }"
      >
        ساخت خوانش تازه
      </RouterLink>
    </BaseCard>

    <template v-else>
      <header class="text-center">
        <p class="text-sm font-semibold text-accent">خوانش آماده است</p>
        <h1 ref="heading" class="mt-2 text-3xl font-bold sm:text-4xl" tabindex="-1">
          کارت‌های شما
        </h1>
        <p class="mx-auto mt-3 max-w-2xl text-muted">
          کارت‌ها را به همان ترتیبی که برای خوانش شما انتخاب شده‌اند مرور کنید.
        </p>
      </header>

      <div
        class="grid items-start gap-6"
        :class="isSingleCard ? 'mx-auto w-full max-w-sm' : 'md:grid-cols-3'"
      >
        <ReadingResultCard v-for="item in result.cards" :key="item.position" :item="item" />
      </div>

      <BaseCard v-if="result.summary.trim()" class="mx-auto w-full max-w-3xl" elevated>
        <h2 class="text-2xl font-bold">جمع‌بندی خوانش</h2>
        <p class="mt-4 whitespace-pre-line break-words leading-8 text-muted">
          {{ result.summary }}
        </p>
      </BaseCard>

      <nav
        class="flex flex-col justify-center gap-3 sm:flex-row"
        aria-label="اقدام‌های نتیجهٔ خوانش"
      >
        <RouterLink
          class="inline-flex min-h-11 items-center justify-center rounded-control border border-accent bg-accent px-5 py-2.5 font-semibold text-accent-contrast transition-colors hover:bg-accent/90"
          :to="{ name: 'reading-create' }"
        >
          خوانش تازه
        </RouterLink>
        <RouterLink
          class="inline-flex min-h-11 items-center justify-center rounded-control border border-line bg-surface-secondary px-5 py-2.5 font-semibold transition-colors hover:border-accent/70"
          :to="{ name: 'home' }"
        >
          بازگشت به خانه
        </RouterLink>
      </nav>
    </template>
  </section>
</template>
