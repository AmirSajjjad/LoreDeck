import { expect, test } from '@playwright/test'
import { mockLoreDeckApi, signIn, type ApiFixtureState } from './fixtures/api'

let state: ApiFixtureState
test.beforeEach(async ({ page }) => {
  state = await mockLoreDeckApi(page)
})

test('protected routes preserve a safe destination for guests', async ({ page }) => {
  await page.goto('/profile')
  await expect(page).toHaveURL('/sign-in?redirect=/profile')
  await page.getByLabel('نام کاربری').fill('sara')
  await page.getByLabel('رمز عبور').fill('password')
  await page.getByRole('button', { name: 'ورود' }).click()
  await expect(page).toHaveURL('/profile')
})

test('user signs in with keyboard access and signs out', async ({ page }) => {
  await page.goto('/sign-in')
  await page.getByLabel('نام کاربری').fill('sara')
  await page.getByLabel('رمز عبور').fill('password')
  await page.getByLabel('رمز عبور').press('Tab')
  await expect(page.getByRole('button', { name: 'ورود' })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('link', { name: 'سارا' })).toBeVisible()
  await page.getByRole('button', { name: 'خروج' }).click()
  await expect(page.getByRole('link', { name: 'ورود' })).toBeVisible()
})

test('a new user can sign up', async ({ page }) => {
  await page.goto('/sign-up')
  await page.getByLabel('نام کاربری').fill('new-user')
  await page.getByLabel('رمز عبور').first().fill('password')
  await page.getByLabel('تکرار رمز عبور').fill('password')
  await page.getByRole('button', { name: 'ساخت حساب' }).click()
  await expect(page).toHaveURL('/')
  await expect(page.getByRole('button', { name: 'خروج' })).toBeVisible()
})

test('authenticated user updates profile and creates a reading with bearer auth', async ({
  page,
}) => {
  await signIn(page)
  await page.getByRole('link', { name: 'سارا' }).click()
  await page.getByRole('button', { name: 'ویرایش نمایه' }).click()
  await page.getByLabel('نام نمایشی').fill('سارای تازه')
  await page.getByRole('button', { name: 'ذخیره تغییرات' }).click()
  await expect(page.getByText('تغییرات ذخیره شد')).toBeVisible()
  expect(state.profileRequests.at(-1)).toMatchObject({ name: 'سارای تازه' })

  await page.getByRole('link', { name: 'خوانش تازه' }).first().click()
  await page.getByLabel('دستهٔ کارت').selectOption('1')
  await page.getByRole('button', { name: 'آغاز خوانش' }).click()
  await expect(page.getByRole('heading', { name: 'کارت‌های شما' })).toBeVisible()
  expect(state.readingRequests.at(-1)?.headers.authorization).toBe('Bearer e2e-token')
})

test('authenticated user views history and a saved detail', async ({ page }) => {
  await signIn(page)
  await page.getByRole('link', { name: 'تاریخچه' }).click()
  await expect(page.getByRole('heading', { name: 'تاریخچهٔ خوانش‌ها' })).toBeVisible()
  await expect(page.getByText('مسیر من چیست؟')).toBeVisible()
  await page.getByRole('link', { name: 'مشاهدهٔ خوانش' }).click()
  await expect(page.getByRole('heading', { name: 'خوانش ذخیره‌شده' })).toBeVisible()
  await expect(page.locator('.reading-card h2')).toHaveText(['ماه', 'خورشید', 'جهان'])
})
