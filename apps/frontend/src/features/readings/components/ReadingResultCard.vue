<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import type { RenderableReadingCard } from '@/features/readings/types'
import { resolveCardImageUrl } from '@/features/readings/utils/cardImage'

const props = defineProps<{ item: RenderableReadingCard }>()
const imageLoading = ref(true)
const imageFailed = ref(false)

const positionLabel = computed(
  () =>
    ({
      past: 'گذشته',
      present: 'اکنون',
      future: 'آینده',
    })[props.item.position],
)
const orientationLabel = computed(() => ({ upright: 'مستقیم' })[props.item.orientation])
const imageUrl = computed(() => resolveCardImageUrl(props.item.card.image_path))
const showImage = computed(() => imageUrl.value && !imageFailed.value)
</script>

<template>
  <article
    class="reading-card h-full overflow-hidden rounded-card border border-line bg-surface shadow-elevated"
  >
    <div class="relative aspect-[2/3] w-full overflow-hidden bg-surface-secondary">
      <div
        v-if="!showImage"
        class="grid size-full place-items-center p-6 text-center text-muted"
        role="img"
        :aria-label="`تصویر کارت ${item.card.title} در دسترس نیست`"
      >
        <span>
          <span class="block text-4xl text-accent" aria-hidden="true">✦</span>
          <span class="mt-3 block text-sm">تصویر کارت در دسترس نیست</span>
        </span>
      </div>
      <template v-else>
        <div
          v-if="imageLoading"
          class="absolute inset-0 grid place-items-center"
          aria-hidden="true"
        >
          <BaseSpinner size="large" label="در حال بارگذاری تصویر کارت" />
        </div>
        <img
          :src="imageUrl"
          :alt="`تصویر کارت ${item.card.title}`"
          loading="lazy"
          decoding="async"
          class="size-full object-cover transition-opacity"
          :class="imageLoading ? 'opacity-0' : 'opacity-100'"
          @load="imageLoading = false"
          @error="imageFailed = true"
        />
      </template>
    </div>

    <div class="grid gap-4 p-5">
      <div class="flex flex-wrap items-center justify-between gap-2 text-sm">
        <span class="font-semibold text-accent">جایگاه: {{ positionLabel }}</span>
        <span class="text-muted">جهت: {{ orientationLabel }}</span>
      </div>
      <div>
        <p v-if="item.card.number !== null" class="text-sm text-muted">
          شمارهٔ {{ item.card.number.toLocaleString('fa-IR') }}
        </p>
        <h2 class="mt-1 break-words text-2xl font-bold">{{ item.card.title }}</h2>
        <p
          v-if="item.card.description"
          class="mt-3 whitespace-pre-line text-sm leading-7 text-muted"
        >
          {{ item.card.description }}
        </p>
      </div>
      <section v-if="item.story?.trim()" class="border-t border-line pt-4" aria-label="روایت کارت">
        <h3 class="font-semibold">روایت این کارت</h3>
        <p class="mt-2 whitespace-pre-line break-words text-sm leading-8 text-muted">
          {{ item.story }}
        </p>
      </section>
    </div>
  </article>
</template>

<style scoped>
.reading-card {
  animation: card-reveal 280ms ease-out both;
}

@keyframes card-reveal {
  from {
    opacity: 0;
    transform: translateY(0.75rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .reading-card {
    animation: none;
  }
}
</style>
