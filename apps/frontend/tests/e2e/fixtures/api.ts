import type { Page, Route } from '@playwright/test'

export const testUser = {
  id: 1,
  username: 'sara',
  phone_number: null,
  profile_pic: null,
  name: 'سارا',
  email: 'sara@example.test',
  telegram_id: null,
  created_at: '2026-01-01T00:00:00Z',
}

const cards = {
  past: {
    position: 'past',
    orientation: 'upright',
    card: { title: 'ماه', description: 'نگاه به گذشته', number: 18, image_path: null },
    story: 'روایت گذشته',
  },
  present: {
    position: 'present',
    orientation: 'upright',
    card: { title: 'خورشید', description: null, number: 19, image_path: null },
    story: 'روایت اکنون',
  },
  future: {
    position: 'future',
    orientation: 'upright',
    card: { title: 'جهان', description: 'نگاه به آینده', number: 21, image_path: null },
    story: 'روایت آینده',
  },
}

export interface ApiFixtureState {
  readingRequests: Array<{ headers: Record<string, string>; payload: unknown }>
  profileRequests: unknown[]
}

async function json(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

export async function mockLoreDeckApi(page: Page): Promise<ApiFixtureState> {
  const state: ApiFixtureState = { readingRequests: [], profileRequests: [] }

  await page.route('http://api.test/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const method = request.method()

    if (path === '/decks' && method === 'GET') {
      await json(route, [{ id: 1, title: 'رایدر–ویت' }])
      return
    }
    if (path === '/readings' && method === 'POST') {
      const payload = request.postDataJSON() as { spread: 'one_card' | 'three_card' }
      state.readingRequests.push({ headers: request.headers(), payload })
      await json(route, {
        cards:
          payload.spread === 'three_card'
            ? [cards.past, cards.present, cards.future]
            : [cards.present],
        summary: 'جمع‌بندی خوانش',
      })
      return
    }
    if ((path === '/users/signin' || path === '/users/signup') && method === 'POST') {
      await json(route, {
        access_token: 'e2e-token',
        token_type: 'bearer',
        expires_in: 3600,
        user: testUser,
      })
      return
    }
    if (path === '/users/profile' && method === 'GET') {
      await json(route, testUser)
      return
    }
    if (path === '/users/profile' && method === 'PATCH') {
      const payload = request.postDataJSON()
      state.profileRequests.push(payload)
      await json(route, { ...testUser, ...(payload as object) })
      return
    }
    if (path === '/readings/history' && method === 'GET') {
      await json(route, {
        items: [
          {
            id: 11,
            created_at: '2026-01-02T10:30:00Z',
            question: 'مسیر من چیست؟',
            deck: { id: 1, title: 'رایدر–ویت' },
            spread: 'three_card',
          },
        ],
        total: 1,
        limit: 20,
        offset: 0,
      })
      return
    }
    if (path === '/readings/history/11' && method === 'GET') {
      await json(route, {
        id: 11,
        created_at: '2026-01-02T10:30:00Z',
        question: 'مسیر من چیست؟',
        deck: { id: 1, title: 'رایدر–ویت' },
        spread: 'three_card',
        cards: [cards.past, cards.present, cards.future],
        summary: 'جمع‌بندی ذخیره‌شده',
      })
      return
    }

    await json(route, { detail: 'Unexpected test request' }, 500)
  })

  return state
}

export async function signIn(page: Page): Promise<void> {
  await page.goto('/sign-in')
  await page.getByLabel('نام کاربری').fill('sara')
  await page.getByLabel('رمز عبور').fill('password')
  await page.getByRole('button', { name: 'ورود' }).click()
  await page.waitForURL('/')
}
