import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { onUnauthorized, setAccessTokenProvider } from '@/api/auth'
import { getEnvironment } from '@/api/environment'
import App from '@/App.vue'
import { readAccessToken } from '@/features/auth/tokenStorage'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import '@/assets/styles/main.css'

getEnvironment()

const app = createApp(App)
const pinia = createPinia()
const auth = useAuthStore(pinia)

setAccessTokenProvider({ getAccessToken: readAccessToken })
onUnauthorized(() => {
  const currentRoute = router.currentRoute.value
  const redirect = currentRoute.fullPath
  const requiresAuthentication = currentRoute.matched.some(
    (route) => route.meta.requiresAuth === true,
  )
  auth.clearSession()
  if (requiresAuthentication) {
    void router.replace({ name: 'sign-in', query: { redirect } })
  }
})

app.use(pinia)
app.use(router)
app.mount('#app')
