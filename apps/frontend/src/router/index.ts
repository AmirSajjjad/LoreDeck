import { createRouter, createWebHistory } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
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
        },
        {
          path: 'sign-up',
          name: 'sign-up',
          component: () => import('@/features/auth/views/SignUpView.vue'),
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
          path: 'readings/new',
          name: 'reading-create',
          component: () => import('@/features/readings/views/CreateReadingView.vue'),
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

export default router
