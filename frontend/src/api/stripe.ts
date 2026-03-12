import { api } from './client'

interface CheckoutResponse {
  checkout_url: string
}

interface PortalResponse {
  portal_url: string
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
