<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
</script>

<template>
  <main
    class="grid min-h-screen place-items-center bg-page px-page text-center text-foreground"
    dir="rtl"
  >
    <BaseCard elevated>
      <section aria-labelledby="not-found-title">
        <p class="text-sm font-semibold text-accent">خطای ۴۰۴</p>
        <h1 id="not-found-title" class="mt-2 text-3xl font-bold">صفحه پیدا نشد</h1>
        <p class="mt-3 text-muted">نشانی واردشده معتبر نیست.</p>
        <RouterLink
          class="mt-6 inline-flex min-h-11 items-center rounded-control border border-accent bg-accent px-5 py-2 font-semibold text-accent-contrast transition-colors hover:bg-accent/90"
          :to="{ name: 'home' }"
        >
          بازگشت به خانه
        </RouterLink>
      </section>
    </BaseCard>
  </main>
</template>
