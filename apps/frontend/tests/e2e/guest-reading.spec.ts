import { expect, test } from '@playwright/test'
import { mockLoreDeckApi, type ApiFixtureState } from './fixtures/api'

let state: ApiFixtureState
test.beforeEach(async ({ page }) => {
  state = await mockLoreDeckApi(page)
})

test('guest starts and completes a one-card reading with the keyboard', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: 'شروع یک خوانش' }).click()
  await expect(page.getByRole('heading', { name: /پرسش خود را/ })).toBeVisible()

  await page.getByLabel('دستهٔ کارت').selectOption('1')
  await page.getByLabel(/یک‌کارتی/).check()
  await page.getByLabel('پرسش (اختیاری)').fill('   ')
  await page.getByRole('button', { name: 'آغاز خوانش' }).focus()
  await page.keyboard.press('Enter')

  await expect(page.getByRole('heading', { name: 'کارت‌های شما' })).toBeFocused()
  await expect(page.getByRole('heading', { name: 'خورشید <script>alert(1)</script>' })).toHaveCount(
    0,
  )
  await expect(page.getByRole('heading', { name: 'خورشید' })).toBeVisible()
  expect(state.readingRequests.at(-1)?.payload).toEqual({
    deck_id: 1,
    spread: 'one_card',
    question: null,
  })

  await page.reload()
  await expect(page.getByRole('heading', { name: 'نتیجه‌ای برای نمایش وجود ندارد' })).toBeVisible()
})

test('guest completes a three-card reading on a mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/readings/new')
  await page.getByLabel('دستهٔ کارت').selectOption('1')
  await page.getByLabel(/سه‌کارتی/).check()
  await page.getByLabel('پرسش (اختیاری)').fill('آینده چیست؟')
  await page.getByRole('button', { name: 'آغاز خوانش' }).click()

  await expect(page.locator('.reading-card h2')).toHaveText(['ماه', 'خورشید', 'جهان'])
  expect(state.readingRequests.at(-1)?.payload).toEqual({
    deck_id: 1,
    spread: 'three_card',
    question: 'آینده چیست؟',
  })
})
