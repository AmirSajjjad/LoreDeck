<script setup lang="ts">
withDefaults(defineProps<{ elevated?: boolean }>(), { elevated: false })
</script>

<template>
  <article
    class="rounded-card border border-line bg-surface p-5 sm:p-7"
    :class="elevated ? 'bg-elevated shadow-elevated' : ''"
  >
    <header v-if="$slots.header" class="mb-5"><slot name="header" /></header>
    <slot />
    <footer v-if="$slots.footer" class="mt-5"><slot name="footer" /></footer>
  </article>
</template>
