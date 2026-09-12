<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="border-b border-line bg-elevated/90">
    <a
      class="fixed start-4 top-3 z-50 -translate-y-20 rounded-control bg-accent px-4 py-2 font-semibold text-accent-contrast transition-transform focus:translate-y-0"
      href="#main-content"
    >
      رفتن به محتوای اصلی
    </a>
    <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-page py-4">
      <RouterLink
        class="inline-flex items-center gap-2 rounded-control text-lg font-bold"
        :to="{ name: 'home' }"
      >
        <span
          class="grid size-8 place-items-center rounded-full border border-accent text-accent"
          aria-hidden="true"
          >✦</span
        >
        <span>لور دک</span>
      </RouterLink>
      <nav aria-label="ناوبری اصلی">
        <ul class="flex flex-wrap items-center gap-1 text-sm">
          <li>
            <RouterLink
              class="block rounded-control px-3 py-2 text-muted transition-colors hover:bg-surface-secondary hover:text-foreground"
              active-class="bg-surface-secondary text-foreground"
              :to="{ name: 'home' }"
              >خانه</RouterLink
            >
          </li>
          <li>
            <RouterLink
              class="block rounded-control px-3 py-2 text-muted transition-colors hover:bg-surface-secondary hover:text-foreground"
              active-class="bg-surface-secondary text-foreground"
              :to="{ name: 'sign-in' }"
              >ورود</RouterLink
            >
          </li>
          <li>
            <RouterLink
              class="block rounded-control border border-accent/70 px-3 py-2 font-semibold text-accent transition-colors hover:bg-accent hover:text-accent-contrast"
              :to="{ name: 'sign-up' }"
              >ثبت‌نام</RouterLink
            >
          </li>
        </ul>
      </nav>
    </div>
  </header>
</template>
