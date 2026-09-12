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
onUnauthorized(() => auth.clearSession())

app.use(pinia)
app.use(router)
app.mount('#app')
