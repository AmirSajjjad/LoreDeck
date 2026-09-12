<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    label?: string
    size?: 'small' | 'medium' | 'large'
  }>(),
  { label: 'در حال بارگذاری', size: 'medium' },
)

const sizeClass = computed(
  () => ({ small: 'size-4', medium: 'size-6', large: 'size-9' })[props.size],
)
</script>

<template>
  <span class="inline-flex items-center gap-2" role="status">
    <span
      class="block animate-spin rounded-full border-2 border-current/30 border-t-current"
      :class="sizeClass"
      aria-hidden="true"
    />
    <span class="sr-only">{{ label }}</span>
  </span>
</template>
