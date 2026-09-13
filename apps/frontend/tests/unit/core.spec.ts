import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it } from 'vitest'
import { parseEnvironment } from '@/api/environment'
import { normalizeApiError } from '@/api/errors'
import { signinSchema, signupSchema } from '@/features/auth/schemas/authSchemas'
import { getSafeRedirect } from '@/features/auth/utils/redirect'
import { profileFormSchema } from '@/features/profile/schemas/profileSchema'
import { readingFormSchema } from '@/features/readings/schemas/readingSchemas'
import { resolveCardImageUrl } from '@/features/readings/utils/cardImage'
import { toReadingRequest } from '@/features/readings/utils/readingRequest'
import { normalizeFastApiValidationErrors } from '@/utils/fastApiValidation'

function axiosFailure(status?: number, data?: unknown, code?: string): AxiosError {
  return new AxiosError(
    'failure',
    code,
    { headers: new AxiosHeaders() },
    status ? undefined : {},
    status
      ? {
          data,
          status,
          statusText: 'Failure',
          headers: {},
          config: { headers: new AxiosHeaders() },
        }
      : undefined,
  )
}

describe('shared API infrastructure', () => {
  it('validates and normalizes the API origin', () => {
    expect(parseEnvironment({ VITE_API_BASE_URL: ' https://api.example.test/ ' })).toEqual({
      apiBaseUrl: 'https://api.example.test',
    })
    expect(parseEnvironment({ VITE_API_BASE_URL: '/api/' })).toEqual({ apiBaseUrl: '/api' })
    expect(() => parseEnvironment({ VITE_API_BASE_URL: '' })).toThrow('VITE_API_BASE_URL')
    expect(() => parseEnvironment({ VITE_API_BASE_URL: '//api.example.test' })).toThrow(
      'root-relative',
    )
    expect(() => parseEnvironment({ VITE_API_BASE_URL: 'file:///tmp/api' })).toThrow('HTTP(S)')
  })

  it.each([
    [401, 'unauthorized'],
    [403, 'forbidden'],
    [500, 'server'],
  ] as const)('normalizes HTTP %i as %s', (status, category) => {
    expect(normalizeApiError(axiosFailure(status)).category).toBe(category)
  })

  it('normalizes timeouts and network failures', () => {
    expect(normalizeApiError(axiosFailure(undefined, undefined, 'ETIMEDOUT')).category).toBe(
      'timeout',
    )
    expect(normalizeApiError(axiosFailure()).category).toBe('network')
  })

  it('maps valid 422 fields and safely handles malformed payloads', () => {
    const valid = normalizeApiError(
      axiosFailure(422, {
        detail: [{ loc: ['body', 'profile', 0, 'name'], msg: 'bad', type: 'missing' }],
      }),
    )
    expect(valid.fieldErrors).toEqual([
      { field: 'profile[0].name', message: 'وارد کردن این فیلد الزامی است.', code: 'missing' },
    ])
    expect(normalizeApiError(axiosFailure(422, { detail: 'bad' })).message).toContain(
      'قابل پردازش نیست',
    )
  })
})

describe('validation and feature boundary helpers', () => {
  it('returns Persian required messages for authentication', () => {
    expect(signinSchema.safeParse({ username: '', password: '' }).error?.issues[0]?.message).toBe(
      'وارد کردن این فیلد الزامی است.',
    )
    expect(
      signupSchema
        .safeParse({
          username: 'sara',
          password: 'password',
          passwordConfirmation: 'different',
        })
        .error?.issues.some((issue) => issue.path[0] === 'passwordConfirmation'),
    ).toBe(true)
  })

  it('validates profile and reading fields', () => {
    expect(
      profileFormSchema.safeParse({
        username: '',
        phone_number: '',
        profile_pic: '',
        name: '',
        email: '',
      }).success,
    ).toBe(false)
    expect(readingFormSchema.safeParse({ deck_id: '0', spread: 'bad', question: '' }).success).toBe(
      false,
    )
  })

  it('normalizes a blank reading question and preserves both spreads', () => {
    expect(toReadingRequest({ deck_id: '2', spread: 'one_card', question: '   ' })).toEqual({
      deck_id: 2,
      spread: 'one_card',
      question: null,
    })
    expect(
      toReadingRequest({ deck_id: '2', spread: 'three_card', question: '  راه من؟ ' }),
    ).toEqual({
      deck_id: 2,
      spread: 'three_card',
      question: 'راه من؟',
    })
  })

  it('rejects unsafe redirects and unsafe static paths', () => {
    expect(getSafeRedirect('/profile')).toBe('/profile')
    expect(getSafeRedirect('https://evil.example')).toBe('/')
    expect(resolveCardImageUrl('cards/moon.webp')).toBe('http://api.test/static/cards/moon.webp')
    expect(resolveCardImageUrl('../secret')).toBeUndefined()
    expect(resolveCardImageUrl('https://evil.example/card.png')).toBeUndefined()
  })

  it('preserves unmappable FastAPI validation details as a form error', () => {
    const result = normalizeFastApiValidationErrors({
      detail: [{ loc: ['query', 'limit'], msg: 'bad', type: 'greater_than' }],
    })
    expect(result.fieldErrors).toEqual([])
    expect(result.unmappedErrors).toHaveLength(1)
    expect(result.formMessage).toContain('معتبر نیست')
  })
})
