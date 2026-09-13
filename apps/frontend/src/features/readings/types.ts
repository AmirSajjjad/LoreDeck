import type { z } from 'zod'
import type {
  deckSchema,
  readingFormSchema,
  readingRequestSchema,
  readingResponseSchema,
  spreadSchema,
} from '@/features/readings/schemas/readingSchemas'

export type Deck = z.infer<typeof deckSchema>
export type Spread = z.infer<typeof spreadSchema>
export type ReadingFormValues = z.infer<typeof readingFormSchema>
export type ReadingRequest = z.infer<typeof readingRequestSchema>
export type ReadingResponse = z.infer<typeof readingResponseSchema>
