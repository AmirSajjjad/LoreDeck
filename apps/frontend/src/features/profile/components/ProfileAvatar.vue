<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { resolveProfileImageUrl } from '@/features/profile/utils/profileImage'

const props = defineProps<{ source: string | null; displayName: string }>()
const imageFailed = ref(false)
const imageUrl = computed(() => resolveProfileImageUrl(props.source))
const fallbackLetter = computed(() => props.displayName.trim().charAt(0) || 'ل')

watch(
  () => props.source,
  () => {
    imageFailed.value = false
  },
)
</script>

<template>
  <div
    v-if="!imageUrl || imageFailed"
    class="grid size-24 shrink-0 place-items-center rounded-full border border-line bg-surface-secondary text-3xl font-bold text-accent"
    role="img"
    :aria-label="`تصویر جایگزین ${displayName}`"
  >
    {{ fallbackLetter }}
  </div>
  <img
    v-else
    :src="imageUrl"
    :alt="`تصویر نمایه ${displayName}`"
    class="size-24 shrink-0 rounded-full border border-line object-cover"
    @error="imageFailed = true"
  />
</template>
