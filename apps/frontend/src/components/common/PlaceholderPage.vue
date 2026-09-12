<script setup lang="ts">
defineProps<{ title: string; description: string }>()
</script>

<template>
  <section class="m-auto max-w-xl text-center" aria-labelledby="page-title">
    <h1 id="page-title" class="text-2xl font-semibold sm:text-3xl">{{ title }}</h1>
    <p class="mt-3 leading-7 text-gray-300">{{ description }}</p>
  </section>
</template>
