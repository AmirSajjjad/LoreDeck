<script setup lang="ts">
import BaseSpinner from '@/components/common/BaseSpinner.vue'

withDefaults(defineProps<{ message?: string }>(), { message: 'در حال بارگذاری…' })
</script>

<template>
  <section class="m-auto text-center text-muted" aria-live="polite">
    <BaseSpinner size="large" :label="message" />
    <p class="mt-3">{{ message }}</p>
  </section>
</template>
