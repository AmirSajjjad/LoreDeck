<script setup lang="ts">
import { useField } from 'vee-validate'
import BaseTextarea from '@/components/common/BaseTextarea.vue'

const props = withDefaults(
  defineProps<{
    id: string
    name: string
    label: string
    modelValue?: string
    placeholder?: string
    hint?: string
    rows?: number
    required?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { rows: 4, required: false, disabled: false, loading: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const { value, errorMessage, meta, handleChange, handleBlur } = useField<string>(
  () => props.name,
  undefined,
  { syncVModel: props.modelValue !== undefined },
)

function onBlur(event: FocusEvent): void {
  handleBlur(event)
  emit('blur', event)
}
</script>

<template>
  <BaseTextarea
    :id="id"
    :model-value="value"
    :label="label"
    :name="name"
    :placeholder="placeholder"
    :hint="hint"
    :error="errorMessage"
    :rows="rows"
    :required="required"
    :disabled="disabled"
    :loading="loading"
    :data-touched="meta.touched || undefined"
    @update:model-value="handleChange"
    @blur="onBlur"
  />
</template>
