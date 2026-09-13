import { mount, type ComponentMountingOptions, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { createMemoryHistory, createRouter, type RouteRecordRaw, type Router } from 'vue-router'
import type { Component } from 'vue'

const defaultRoutes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: { template: '<div />' } },
  { path: '/readings/new', name: 'reading-create', component: { template: '<div />' } },
  { path: '/readings/result', name: 'reading-result', component: { template: '<div />' } },
  { path: '/sign-in', name: 'sign-in', component: { template: '<div />' } },
  { path: '/sign-up', name: 'sign-up', component: { template: '<div />' } },
]

export interface RenderResult<T extends Component> {
  wrapper: VueWrapper<InstanceType<T>>
  pinia: Pinia
  router: Router
}

export async function renderWithApp<T extends Component>(
  component: T,
  options: ComponentMountingOptions<T> = {},
  routes: RouteRecordRaw[] = defaultRoutes,
): Promise<RenderResult<T>> {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createRouter({ history: createMemoryHistory(), routes })
  await router.push('/')
  await router.isReady()
  const wrapper = mount(component, {
    ...options,
    global: {
      ...options.global,
      plugins: [pinia, router, ...(options.global?.plugins ?? [])],
    },
  })
  return { wrapper, pinia, router }
}
