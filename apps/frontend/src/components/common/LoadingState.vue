<script setup lang="ts">
withDefaults(defineProps<{ message?: string }>(), { message: 'در حال بارگذاری…' })
</script>

<template>
  <section class="m-auto text-center" role="status" aria-live="polite">
    <span
      class="mx-auto block size-8 animate-spin rounded-full border-2 border-gray-500 border-t-white"
      aria-hidden="true"
    />
    <p class="mt-3">{{ message }}</p>
  </section>
</template>
