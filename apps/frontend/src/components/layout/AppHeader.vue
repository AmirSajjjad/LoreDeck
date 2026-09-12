<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="border-b border-white/15">
    <div class="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4">
      <RouterLink class="rounded-sm text-lg font-semibold" :to="{ name: 'home' }"
        >لور دک</RouterLink
      >
      <nav aria-label="ناوبری اصلی">
        <ul class="flex flex-wrap items-center gap-4 text-sm">
          <li>
            <RouterLink class="rounded-sm hover:underline" :to="{ name: 'home' }">خانه</RouterLink>
          </li>
          <li>
            <RouterLink class="rounded-sm hover:underline" :to="{ name: 'sign-in' }"
              >ورود</RouterLink
            >
          </li>
          <li>
            <RouterLink class="rounded-sm hover:underline" :to="{ name: 'sign-up' }"
              >ثبت‌نام</RouterLink
            >
          </li>
        </ul>
      </nav>
    </div>
  </header>
</template>
