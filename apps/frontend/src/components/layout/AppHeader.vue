<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { RouterLink, useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const { currentUser, isAuthenticated } = storeToRefs(auth)

function logout(): void {
  auth.logout()
  void router.push({ name: 'home' })
}
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
              :to="{ name: 'reading-create' }"
              >خوانش تازه</RouterLink
            >
          </li>
          <li v-if="!isAuthenticated">
            <RouterLink
              class="block rounded-control px-3 py-2 text-muted transition-colors hover:bg-surface-secondary hover:text-foreground"
              active-class="bg-surface-secondary text-foreground"
              :to="{ name: 'sign-in' }"
              >ورود</RouterLink
            >
          </li>
          <li v-if="!isAuthenticated">
            <RouterLink
              class="block rounded-control border border-accent/70 px-3 py-2 font-semibold text-accent transition-colors hover:bg-accent hover:text-accent-contrast"
              :to="{ name: 'sign-up' }"
              >ثبت‌نام</RouterLink
            >
          </li>
          <template v-else>
            <li>
              <RouterLink
                class="block max-w-40 truncate rounded-control px-3 py-2 text-muted transition-colors hover:bg-surface-secondary hover:text-foreground"
                active-class="bg-surface-secondary text-foreground"
                :to="{ name: 'profile' }"
                :title="currentUser?.name || currentUser?.username || 'پروفایل'"
                >{{ currentUser?.name || currentUser?.username || 'پروفایل' }}</RouterLink
              >
            </li>
            <li>
              <RouterLink
                class="block rounded-control px-3 py-2 text-muted transition-colors hover:bg-surface-secondary hover:text-foreground"
                active-class="bg-surface-secondary text-foreground"
                :to="{ name: 'reading-history' }"
                >تاریخچه</RouterLink
              >
            </li>
            <li><BaseButton variant="ghost" @click="logout">خروج</BaseButton></li>
          </template>
        </ul>
      </nav>
    </div>
  </header>
</template>
