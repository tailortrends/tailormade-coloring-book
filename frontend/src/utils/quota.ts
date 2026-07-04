/**
 * Derive quota display values from the backend's /api/v1/auth/me response.
 * This mirrors the backend's tier logic and is the single place that computation
 * lives, shared by the quota widget and the dashboard.
 */
export interface QuotaFields {
  subscription_tier?: string
  subscription_active?: boolean
  one_time_credits?: number
  books_generated_this_month?: number
  books_generated_total?: number
}

export interface Quota {
  tier: string
  active: boolean
  oneTimeCredits: number
  total: number
  thisMonth: number
  limit: number
  remaining: number
  tierLabel: string
  isAtLimit: boolean
}

export function computeQuota(me: QuotaFields): Quota {
  const tier = me.subscription_tier ?? 'free'
  const active = me.subscription_active ?? false
  const oneTimeCredits = me.one_time_credits ?? 0
  const total = me.books_generated_total ?? 0
  const thisMonth = me.books_generated_this_month ?? 0

  // Free = 1 book lifetime.
  let limit = 1
  let remaining = Math.max(0, 1 - total)
  let tierLabel = 'Free'

  if (tier === 'teacher' && active) {
    limit = 25
    remaining = Math.max(0, 25 - thisMonth)
    tierLabel = 'Teacher'
  } else if (tier === 'family' && active) {
    limit = 12
    remaining = Math.max(0, 12 - thisMonth)
    tierLabel = 'Family'
  } else if (oneTimeCredits > 0) {
    limit = oneTimeCredits
    remaining = oneTimeCredits
    tierLabel = 'Single Book'
  }

  return {
    tier,
    active,
    oneTimeCredits,
    total,
    thisMonth,
    limit,
    remaining,
    tierLabel,
    isAtLimit: remaining <= 0,
  }
}
