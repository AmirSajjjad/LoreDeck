import { readingRequestSchema } from '@/features/readings/schemas/readingSchemas'
import type { ReadingFormValues, ReadingRequest } from '@/features/readings/types'

export function toReadingRequest(values: ReadingFormValues): ReadingRequest {
  const question = values.question.trim()
  return readingRequestSchema.parse({
    deck_id: Number(values.deck_id),
    spread: values.spread,
    question: question || null,
  })
}
