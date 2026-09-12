import { createRouter, createWebHistory } from 'vue-router'
import { getSafeRedirect } from '@/features/auth/utils/redirect'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/PublicLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        {
          path: 'sign-in',
          name: 'sign-in',
          component: () => import('@/features/auth/views/SignInView.vue'),
          meta: { guestOnly: true },
        },
        {
          path: 'sign-up',
          name: 'sign-up',
          component: () => import('@/features/auth/views/SignUpView.vue'),
          meta: { guestOnly: true },
        },
        {
          path: 'readings/new',
          name: 'reading-create',
          component: () => import('@/features/readings/views/CreateReadingView.vue'),
        },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/AuthenticatedLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/features/profile/views/ProfileView.vue'),
        },
        {
          path: 'readings',
          name: 'reading-history',
          component: () => import('@/features/readings/views/ReadingHistoryView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.initializeSession()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'sign-in', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    const destination = getSafeRedirect(to.query.redirect)
    return destination === to.fullPath ? { name: 'home' } : destination
  }
})

export default router
