<script setup lang="ts">
withDefaults(defineProps<{ title?: string; message: string }>(), { title: 'موردی پیدا نشد' })
</script>

<template>
  <section class="m-auto max-w-lg text-center" role="status">
    <h2 class="text-xl font-semibold">{{ title }}</h2>
    <p class="mt-2 text-gray-300">{{ message }}</p>
    <div v-if="$slots.default" class="mt-4"><slot /></div>
  </section>
</template>
