<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="grid min-h-screen place-items-center px-4 text-center" dir="rtl">
    <section aria-labelledby="not-found-title">
      <h1 id="not-found-title" class="text-3xl font-semibold">صفحه پیدا نشد</h1>
      <p class="mt-3 text-gray-300">نشانی واردشده معتبر نیست.</p>
      <RouterLink
        class="mt-5 inline-block rounded-md border border-white/40 px-4 py-2 hover:bg-white/10"
        :to="{ name: 'home' }"
      >
        بازگشت به خانه
      </RouterLink>
    </section>
  </main>
</template>
