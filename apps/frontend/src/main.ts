import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { getEnvironment } from '@/api/environment'
import App from '@/App.vue'
import router from '@/router'
import '@/assets/styles/main.css'

getEnvironment()

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')
