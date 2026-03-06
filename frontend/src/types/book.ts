export interface BookPage {
  page_number: number
  image_url: string
  scene_description: string
}

export interface Book {
  book_id: string
  title: string
  theme: string
  age_range: string
  status: 'generating' | 'complete' | 'failed'
  page_count: number
  pdf_url: string | null
  page_urls: string[]
  created_at: string
}

export interface BookGenerateRequest {
  title: string
  theme: string
  age_range: string
  page_count: number
  story_prompt?: string
  character_names?: string[]
}

export interface CreateBookParams {
  child_name: string
  theme: string
  age_range: string
  page_count: number
}

export interface GenerationStatus {
  progress: number
  done: boolean
}

export interface LibraryImage {
  image_id: string
  theme: string
  tags: string[]
  age_range: string
  complexity: string
  r2_url: string
  clip_score: number
}

export interface LibraryIndex {
  themes: string[]
  images: LibraryImage[]
}
