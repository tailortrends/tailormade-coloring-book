import { z } from 'zod'

/** Mirrors backend BookRequest validation in app/models/book.py */
export const bookGenerateSchema = z.object({
  title: z
    .string()
    .min(2, 'Title must be at least 2 characters')
    .max(80, 'Title must be at most 80 characters'),
  theme: z
    .string()
    .min(2, 'Theme is required'),
  age_range: z.enum(['2-4', '4-6', '6-9', '9-12'], {
    errorMap: () => ({ message: 'Please select an age range' }),
  } as any),
  page_count: z
    .number()
    .int()
    .min(4, 'Minimum 4 pages')
    .max(15, 'Maximum 15 pages'),
  story_prompt: z
    .string()
    .max(300, 'Story prompt must be at most 300 characters')
    .optional()
    .or(z.literal('')),
  character_names: z
    .array(z.string().max(50, 'Name too long'))
    .optional(),
})

export type BookGenerateFormData = z.infer<typeof bookGenerateSchema>

/** Mirrors backend profile creation */
export const profileSchema = z.object({
  name: z
    .string()
    .min(1, 'Name is required')
    .max(50, 'Name must be at most 50 characters'),
  age: z
    .number()
    .int()
    .min(2, 'Age must be at least 2')
    .max(12, 'Age must be at most 12'),
  favorite_themes: z
    .array(z.string())
    .min(1, 'Pick at least one theme')
    .max(3, 'Pick up to 3 themes'),
})

export type ProfileFormData = z.infer<typeof profileSchema>
