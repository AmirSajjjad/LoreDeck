<script setup lang="ts">
import { computed } from 'vue'
import type { SelectOption } from '@/types/forms'

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    id: string
    modelValue: string
    label: string
    options: readonly SelectOption[]
    name?: string
    placeholder?: string
    hint?: string
    error?: string
    required?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { required: false, disabled: false, loading: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const describedBy = computed(
  () =>
    [props.hint && `${props.id}-hint`, props.error && `${props.id}-error`]
      .filter(Boolean)
      .join(' ') || undefined,
)
</script>

<template>
  <div class="grid gap-2">
    <label class="font-medium" :for="id">
      {{ label }}
      <span v-if="required" class="text-destructive" aria-hidden="true">*</span>
    </label>
    <select
      v-bind="$attrs"
      :id="id"
      :value="modelValue"
      :name="name"
      :required="required"
      :disabled="disabled || loading"
      :aria-busy="loading || undefined"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      class="min-h-11 w-full rounded-control border border-line bg-elevated px-3.5 py-2 text-foreground hover:border-accent/60 disabled:cursor-not-allowed disabled:opacity-55 aria-invalid:border-destructive"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      @blur="emit('blur', $event)"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </option>
    </select>
    <p v-if="hint" :id="`${id}-hint`" class="text-sm text-muted">{{ hint }}</p>
    <p v-if="error" :id="`${id}-error`" class="text-sm text-destructive" role="alert">
      {{ error }}
    </p>
  </div>
</template>
