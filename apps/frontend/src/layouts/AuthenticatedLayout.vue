<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col" dir="rtl">
    <AppHeader />
    <main id="main-content" class="mx-auto flex w-full max-w-5xl flex-1 px-4 py-8 sm:py-12">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
