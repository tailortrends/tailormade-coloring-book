import { api } from './client'

export interface MeResponse {
  uid: string
  email: string | null
  subscription_tier?: string
  subscription_active?: boolean
  one_time_credits?: number
  books_generated_this_month?: number
  books_generated_total?: number
}

/**
 * Fetch the authenticated user's profile + quota fields from the backend, which
 * is the source of truth. Used by the quota widget instead of a direct
 * client-side Firestore read.
 */
export function getMe(): Promise<MeResponse> {
  return api.get<MeResponse>('/api/v1/auth/me')
}
