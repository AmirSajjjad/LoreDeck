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
