<script setup lang="ts">
import BaseCard from '@/components/common/BaseCard.vue'

withDefaults(defineProps<{ title?: string; message: string }>(), { title: 'موردی پیدا نشد' })
</script>

<template>
  <section class="m-auto w-full max-w-lg text-center" role="status">
    <BaseCard>
      <h2 class="text-xl font-semibold text-foreground">{{ title }}</h2>
      <p class="mt-2 text-muted">{{ message }}</p>
      <div v-if="$slots.default" class="mt-5"><slot /></div>
    </BaseCard>
  </section>
</template>
