<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import SignUpForm from '@/features/auth/components/SignUpForm.vue'
import { getSafeRedirect } from '@/features/auth/utils/redirect'

const route = useRoute()
const router = useRouter()

function navigateAfterAuthentication(): void {
  void router.replace(getSafeRedirect(route.query.redirect))
}
</script>

<template>
  <SignUpForm @authenticated="navigateAfterAuthentication" />
</template>
