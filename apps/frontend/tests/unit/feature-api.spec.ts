import { describe, expect, it } from 'vitest'
import { ApiError } from '@/types/api'
import { getProfile, updateProfile } from '@/features/profile/api'
import {
  createReading,
  getDecks,
  getReadingHistory,
  getReadingHistoryDetail,
} from '@/features/readings/api'
import { apiResponse, mockApiMethod } from './helpers/network'

const user = {
  id: 1,
  username: 'sara',
  phone_number: null,
  profile_pic: null,
  name: 'سارا',
  email: null,
  telegram_id: null,
  created_at: '2026-01-01T00:00:00Z',
}
const reading = {
  cards: [
    {
      position: 'present',
      orientation: 'upright',
      card: { title: 'خورشید', description: null, number: 19, image_path: null },
      story: 'روایت',
    },
  ],
  summary: 'جمع‌بندی',
}

describe('feature API boundaries', () => {
  it('loads active decks and rejects malformed responses', async () => {
    const get = mockApiMethod('get').mockResolvedValueOnce(apiResponse([{ id: 2, title: 'رایدر' }]))
    await expect(getDecks()).resolves.toEqual([{ id: 2, title: 'رایدر' }])
    expect(get).toHaveBeenCalledWith('/decks')
    get.mockResolvedValueOnce(apiResponse([{ id: 0, title: 'خراب' }]))
    await expect(getDecks()).rejects.toBeInstanceOf(ApiError)
  })

  it('constructs reading, profile, and history requests at the shared client boundary', async () => {
    const post = mockApiMethod('post').mockResolvedValueOnce(apiResponse(reading))
    await expect(
      createReading({ deck_id: 2, spread: 'one_card', question: null }),
    ).resolves.toEqual(reading)
    expect(post).toHaveBeenCalledWith('/readings', {
      deck_id: 2,
      spread: 'one_card',
      question: null,
    })

    const get = mockApiMethod('get')
      .mockResolvedValueOnce(apiResponse(user))
      .mockResolvedValueOnce(apiResponse({ items: [], total: 0, limit: 20, offset: 0 }))
      .mockResolvedValueOnce(
        apiResponse({
          id: 4,
          created_at: '2026-01-02T00:00:00Z',
          question: null,
          deck: { id: 2, title: 'رایدر' },
          spread: 'one_card',
          ...reading,
        }),
      )
    await expect(getProfile()).resolves.toEqual(user)
    await expect(getReadingHistory(20, 0)).resolves.toMatchObject({ total: 0, items: [] })
    await expect(getReadingHistoryDetail(4)).resolves.toMatchObject({ id: 4, summary: 'جمع‌بندی' })
    expect(get).toHaveBeenNthCalledWith(2, '/readings/history', {
      params: { limit: 20, offset: 0 },
    })

    const patch = mockApiMethod('patch').mockResolvedValueOnce(
      apiResponse({ ...user, name: 'نام تازه' }),
    )
    await expect(updateProfile({ name: 'نام تازه' })).resolves.toMatchObject({ name: 'نام تازه' })
    expect(patch).toHaveBeenCalledWith('/users/profile', { name: 'نام تازه' })
  })
})
