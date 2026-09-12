<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-page text-foreground" dir="rtl">
    <AppHeader />
    <main id="main-content" class="mx-auto flex w-full max-w-6xl flex-1 px-page py-section">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
