import { api } from './client'

export interface Profile {
  profile_id: string
  uid: string
  name: string
  age: number
  favorite_themes: string[]
  avatar_color: string
  created_at: string
  is_default: boolean
}

export interface ProfileCreate {
  name: string
  age: number
  favorite_themes: string[]
}

export interface ProfileUpdate {
  name?: string
  age?: number
  favorite_themes?: string[]
}

export function listProfiles(): Promise<Profile[]> {
  return api.get<Profile[]>('/api/v1/profiles/')
}

export function getProfile(profileId: string): Promise<Profile> {
  return api.get<Profile>(`/api/v1/profiles/${profileId}`)
}

export function createProfile(data: ProfileCreate): Promise<Profile> {
  return api.post<Profile>('/api/v1/profiles/', data)
}

export function updateProfile(profileId: string, data: ProfileUpdate): Promise<Profile> {
  return api.put<Profile>(`/api/v1/profiles/${profileId}`, data)
}

export function deleteProfile(profileId: string): Promise<void> {
  return api.delete<void>(`/api/v1/profiles/${profileId}`)
}

export function setDefaultProfile(profileId: string): Promise<Profile> {
  return api.put<Profile>(`/api/v1/profiles/${profileId}/set-default`)
}
