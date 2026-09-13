import type { z } from 'zod'
import type {
  deckSchema,
  readingFormSchema,
  readingHistoryDetailSchema,
  readingHistoryItemSchema,
  readingHistoryPageSchema,
  readingRequestSchema,
  readingResponseSchema,
  spreadSchema,
} from '@/features/readings/schemas/readingSchemas'

export type Deck = z.infer<typeof deckSchema>
export type Spread = z.infer<typeof spreadSchema>
export type ReadingFormValues = z.infer<typeof readingFormSchema>
export type ReadingRequest = z.infer<typeof readingRequestSchema>
export type ReadingResponse = z.infer<typeof readingResponseSchema>
export type ReadingCard = ReadingResponse['cards'][number]
export type ReadingHistoryItem = z.infer<typeof readingHistoryItemSchema>
export type ReadingHistoryPage = z.infer<typeof readingHistoryPageSchema>
export type ReadingHistoryDetail = z.infer<typeof readingHistoryDetailSchema>
export type RenderableReadingCard = ReadingCard | ReadingHistoryDetail['cards'][number]
