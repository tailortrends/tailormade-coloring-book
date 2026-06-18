export function getApiErrorDetail(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null && 'body' in error) {
    const body = (error as { body?: unknown }).body
    if (typeof body === 'object' && body !== null && 'detail' in body) {
      const detail = (body as { detail?: unknown }).detail
      if (typeof detail === 'string' && detail.trim()) {
        return detail
      }
    }
  }

  return fallback
}
