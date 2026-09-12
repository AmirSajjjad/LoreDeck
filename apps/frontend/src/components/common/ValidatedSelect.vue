<script setup lang="ts">
import { useField } from 'vee-validate'
import BaseSelect from '@/components/common/BaseSelect.vue'
import type { SelectOption } from '@/types/forms'

const props = withDefaults(
  defineProps<{
    id: string
    name: string
    label: string
    options: readonly SelectOption[]
    modelValue?: string
    placeholder?: string
    hint?: string
    required?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { modelValue: '', required: false, disabled: false, loading: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const { value, errorMessage, meta, handleChange, handleBlur } = useField<string>(
  () => props.name,
  undefined,
  { syncVModel: true },
)

function onBlur(event: FocusEvent): void {
  handleBlur(event)
  emit('blur', event)
}
</script>

<template>
  <BaseSelect
    :id="id"
    :model-value="value"
    :label="label"
    :name="name"
    :options="options"
    :placeholder="placeholder"
    :hint="hint"
    :error="errorMessage"
    :required="required"
    :disabled="disabled"
    :loading="loading"
    :data-touched="meta.touched || undefined"
    @update:model-value="handleChange"
    @blur="onBlur"
  />
</template>
