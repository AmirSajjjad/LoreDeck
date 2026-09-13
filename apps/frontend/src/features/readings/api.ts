import { z } from 'zod'
import { apiClient } from '@/api/client'
import { API_ERROR_MESSAGES } from '@/api/messages'
import { deckSchema, readingResponseSchema } from '@/features/readings/schemas/readingSchemas'
import type { Deck, ReadingRequest, ReadingResponse } from '@/features/readings/types'
import { ApiError } from '@/types/api'

function parseResponse<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data)
  if (!result.success) throw new ApiError('unexpected', API_ERROR_MESSAGES.unexpected)
  return result.data
}

export async function getDecks(): Promise<Deck[]> {
  const response = await apiClient.get<unknown>('/decks')
  return parseResponse(z.array(deckSchema), response.data)
}

export async function createReading(request: ReadingRequest): Promise<ReadingResponse> {
  const response = await apiClient.post<unknown>('/readings', request)
  return parseResponse(readingResponseSchema, response.data)
}
