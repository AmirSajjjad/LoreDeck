import { expect, test } from '@playwright/test'
import { mockLoreDeckApi } from './fixtures/api'

test('an expired session is cleared before a protected page is shown', async ({ page }) => {
  await mockLoreDeckApi(page)
  await page.route('http://api.test/users/profile', async (route) => {
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Invalid token' }),
    })
  })
  await page.addInitScript(() => {
    window.sessionStorage.setItem('loredeck.access-token', 'expired-test-token')
  })

  await page.goto('/profile')
  await expect(page).toHaveURL('/sign-in?redirect=/profile')
  await expect(page.getByRole('heading', { name: 'ورود به حساب' })).toBeVisible()
  expect(
    await page.evaluate(() => window.sessionStorage.getItem('loredeck.access-token')),
  ).toBeNull()
})

test('public and not-found pages do not overflow representative viewports', async ({ page }) => {
  await mockLoreDeckApi(page)
  const viewports = [
    { width: 320, height: 720 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1440, height: 900 },
  ]

  for (const viewport of viewports) {
    await page.setViewportSize(viewport)
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'لور دک' })).toBeVisible()
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)

    await page.goto('/مسیر-ناموجود-بسیار-طولانی')
    await expect(page.getByRole('heading', { name: 'صفحه پیدا نشد' })).toBeVisible()
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)
  }
})
