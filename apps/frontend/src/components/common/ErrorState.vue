<script setup lang="ts">
withDefaults(
  defineProps<{ title?: string; message: string; retryable?: boolean; retryLabel?: string }>(),
  { title: 'خطایی رخ داد', retryable: false, retryLabel: 'تلاش دوباره' },
)
defineEmits<{ retry: [] }>()
</script>

<template>
  <section class="m-auto max-w-lg text-center" role="alert">
    <h2 class="text-xl font-semibold">{{ title }}</h2>
    <p class="mt-2 text-gray-300">{{ message }}</p>
    <button
      v-if="retryable"
      type="button"
      class="mt-4 rounded-md border border-white/40 px-4 py-2 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
      @click="$emit('retry')"
    >
      {{ retryLabel }}
    </button>
  </section>
</template>
