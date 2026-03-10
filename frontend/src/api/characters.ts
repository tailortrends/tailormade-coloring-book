import { api } from './client'

export interface Character {
  character_id: string
  name: string
  relationship: string
  character_type: string
  original_url: string
  sketch_url: string
  created_at: any
}

export function createCharacter(formData: FormData): Promise<Character> {
  // The api client auto-detects FormData and skips JSON.stringify / Content-Type
  return api.post<Character>('/api/v1/characters/', formData)
}

export function listCharacters(): Promise<Character[]> {
  return api.get<Character[]>('/api/v1/characters/')
}

export function deleteCharacter(characterId: string): Promise<void> {
  return api.delete<void>(`/api/v1/characters/${characterId}`)
}
