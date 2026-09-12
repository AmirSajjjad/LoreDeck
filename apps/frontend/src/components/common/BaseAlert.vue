<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'info' | 'success' | 'warning' | 'destructive'
    title?: string
  }>(),
  { variant: 'info', title: undefined },
)

const appearance = computed(
  () =>
    ({
      info: { className: 'border-line bg-surface-secondary text-foreground', label: 'اطلاع' },
      success: { className: 'border-success/60 bg-success-surface text-success', label: 'موفق' },
      warning: { className: 'border-warning/60 bg-warning-surface text-warning', label: 'هشدار' },
      destructive: {
        className: 'border-destructive/60 bg-destructive-surface text-destructive',
        label: 'خطا',
      },
    })[props.variant],
)
</script>

<template>
  <div
    class="rounded-control border p-4"
    :class="appearance.className"
    :role="variant === 'destructive' ? 'alert' : 'status'"
  >
    <p class="font-semibold">{{ title ?? appearance.label }}</p>
    <div class="mt-1 text-sm leading-7"><slot /></div>
  </div>
</template>
