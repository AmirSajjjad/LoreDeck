<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import SignInForm from '@/features/auth/components/SignInForm.vue'
import { getSafeRedirect } from '@/features/auth/utils/redirect'

const route = useRoute()
const router = useRouter()

function navigateAfterAuthentication(): void {
  void router.replace(getSafeRedirect(route.query.redirect))
}
</script>

<template>
  <SignInForm @authenticated="navigateAfterAuthentication" />
</template>
