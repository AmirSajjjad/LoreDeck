<script setup lang="ts">
import BaseCard from '@/components/common/BaseCard.vue'

defineProps<{ title: string; description: string; eyebrow?: string }>()
</script>

<template>
  <section class="m-auto w-full max-w-2xl text-center" aria-labelledby="page-title">
    <BaseCard elevated>
      <p v-if="eyebrow" class="mb-3 text-sm font-semibold tracking-wide text-accent">
        {{ eyebrow }}
      </p>
      <h1 id="page-title" class="text-3xl font-bold text-foreground sm:text-4xl">{{ title }}</h1>
      <p class="mx-auto mt-4 max-w-xl leading-8 text-muted">{{ description }}</p>
      <div v-if="$slots.default" class="mt-6 text-start"><slot /></div>
    </BaseCard>
  </section>
</template>
