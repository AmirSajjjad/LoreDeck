<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    id: string
    modelValue: string
    label: string
    type?: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url'
    name?: string
    autocomplete?: string
    placeholder?: string
    hint?: string
    error?: string
    required?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { type: 'text', required: false, disabled: false, loading: false },
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
    <input
      v-bind="$attrs"
      :id="id"
      :value="modelValue"
      :type="type"
      :name="name"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled || loading"
      :aria-busy="loading || undefined"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      class="min-h-11 w-full rounded-control border border-line bg-elevated px-3.5 py-2 text-foreground placeholder:text-muted/70 hover:border-accent/60 disabled:cursor-not-allowed disabled:opacity-55 aria-invalid:border-destructive"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="emit('blur', $event)"
    />
    <p v-if="hint" :id="`${id}-hint`" class="text-sm text-muted">{{ hint }}</p>
    <p v-if="error" :id="`${id}-error`" class="text-sm text-destructive">{{ error }}</p>
  </div>
</template>
