<script setup lang="ts">
withDefaults(
  defineProps<{ title?: string; message: string; retryable?: boolean; retryLabel?: string }>(),
  { title: 'خطایی رخ داد', retryable: false, retryLabel: 'تلاش دوباره' },
)
defineEmits<{ retry: [] }>()
</script>

<template>
  <section class="m-auto w-full max-w-lg text-center">
    <BaseAlert variant="destructive" :title="title">
      <p>{{ message }}</p>
      <BaseButton v-if="retryable" class="mt-4" variant="destructive" @click="$emit('retry')">
        {{ retryLabel }}
      </BaseButton>
    </BaseAlert>
  </section>
</template>
import BaseAlert from '@/components/common/BaseAlert.vue' import BaseButton from
'@/components/common/BaseButton.vue'
