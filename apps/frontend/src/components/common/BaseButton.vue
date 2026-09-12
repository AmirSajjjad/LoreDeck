<script setup lang="ts">
import { computed } from 'vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    loading?: boolean
    loadingLabel?: string
  }>(),
  {
    variant: 'primary',
    type: 'button',
    disabled: false,
    loading: false,
    loadingLabel: 'در حال انجام',
  },
)

const emit = defineEmits<{ click: [event: MouseEvent] }>()

const variantClass = computed(
  () =>
    ({
      primary: 'border-accent bg-accent text-accent-contrast hover:bg-accent/90',
      secondary: 'border-line bg-surface-secondary text-foreground hover:border-accent/70',
      ghost: 'border-transparent bg-transparent text-foreground hover:bg-surface-secondary',
      destructive:
        'border-destructive/70 bg-destructive-surface text-destructive hover:border-destructive',
    })[props.variant],
)
</script>

<template>
  <button
    :type="type"
    class="inline-flex min-h-11 items-center justify-center gap-2 rounded-control border px-5 py-2.5 font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-55"
    :class="variantClass"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    @click="emit('click', $event)"
  >
    <BaseSpinner v-if="loading" size="small" :label="loadingLabel" />
    <slot />
  </button>
</template>
