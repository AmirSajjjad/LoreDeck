<script setup lang="ts">
import { useField } from 'vee-validate'
import BaseInput from '@/components/common/BaseInput.vue'

const props = withDefaults(
  defineProps<{
    id: string
    name: string
    label: string
    modelValue?: string
    type?: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url'
    autocomplete?: string
    placeholder?: string
    hint?: string
    required?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { modelValue: '', type: 'text', required: false, disabled: false, loading: false },
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
  <BaseInput
    :id="id"
    :model-value="value"
    :label="label"
    :name="name"
    :type="type"
    :autocomplete="autocomplete"
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
