import { z } from 'zod'
import { REQUIRED_TEXT_MESSAGE } from '@/utils/validation'

export const spreadSchema = z.enum(['one_card', 'three_card'], {
  required_error: REQUIRED_TEXT_MESSAGE,
  invalid_type_error: REQUIRED_TEXT_MESSAGE,
})

export const readingRequestSchema = z.object({
  deck_id: z.number().int().positive(),
  spread: spreadSchema,
  question: z.string().nullable().optional(),
})

export const readingFormSchema = z.object({
  deck_id: z.string().regex(/^[1-9]\d*$/, 'یک دسته را انتخاب کنید.'),
  spread: spreadSchema,
  question: z.string(),
})

export const deckSchema = z.object({
  id: z.number().int().positive(),
  title: z.string(),
})

const publicCardSchema = z.object({
  title: z.string(),
  description: z.string().nullable(),
  number: z.number().int().nullable(),
  image_path: z.string().nullable(),
})

const readingCardSchema = z.object({
  position: z.enum(['past', 'present', 'future']),
  orientation: z.literal('upright'),
  card: publicCardSchema,
  story: z.string(),
})

export const readingResponseSchema = z.object({
  cards: z.array(readingCardSchema),
  summary: z.string(),
})

const historyDeckSchema = z.object({ id: z.number().int().positive(), title: z.string() })
const historyCardSchema = readingCardSchema.extend({ story: z.string().nullable() })

export const readingHistoryItemSchema = z.object({
  id: z.number().int().positive(),
  created_at: z.string().datetime({ offset: true }),
  question: z.string().nullable(),
  deck: historyDeckSchema,
  spread: spreadSchema,
})

export const readingHistoryPageSchema = z.object({
  items: z.array(readingHistoryItemSchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().min(1).max(100),
  offset: z.number().int().nonnegative(),
})

export const readingHistoryDetailSchema = z.object({
  id: z.number().int().positive(),
  created_at: z.string().datetime({ offset: true }),
  question: z.string().nullable(),
  deck: historyDeckSchema,
  spread: spreadSchema,
  cards: z.array(historyCardSchema),
  summary: z.string().nullable(),
})
