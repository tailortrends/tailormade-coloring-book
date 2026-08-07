import { api } from './client'

interface CheckoutResponse {
  checkout_url: string
}

interface PortalResponse {
  portal_url: string
}

export interface StripeConfig {
  publishable_key: string
  mode: string
  price_ids: {
    family: string
    teacher: string
    single: string
  }
}

/**
 * Fetch the active Stripe config (publishable key, mode, and the price IDs for
 * that mode). The frontend reads price IDs from here instead of hardcoding
 * VITE_STRIPE_*_PRICE_ID, so they always match the backend's active mode.
 */
export async function getStripeConfig(): Promise<StripeConfig> {
  return api.get<StripeConfig>('/api/v1/stripe/config')
}

export async function createCheckoutSession(
  priceId: string,
  successUrl: string,
  cancelUrl: string,
): Promise<void> {
  const { checkout_url } = await api.post<CheckoutResponse>(
    '/api/v1/stripe/create-checkout-session',
    { price_id: priceId, success_url: successUrl, cancel_url: cancelUrl },
  )
  window.location.href = checkout_url
}

export async function createPortalSession(): Promise<void> {
  const { portal_url } = await api.post<PortalResponse>(
    '/api/v1/stripe/create-portal-session',
  )
  window.location.href = portal_url
}
