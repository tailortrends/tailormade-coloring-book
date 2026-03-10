import { getAuth } from 'firebase/auth'

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') as string
const DEFAULT_TIMEOUT_MS = 30_000

interface RequestOptions extends Omit<RequestInit, 'body' | 'signal'> {
  body?: unknown
  timeout?: number
  signal?: AbortSignal
}

async function getAuthToken(): Promise<string | null> {
  try {
    const user = getAuth().currentUser
    if (!user) return null
    return await user.getIdToken()
  } catch {
    return null
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown,
  ) {
    super(`API ${status}: ${statusText}`)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers: customHeaders, timeout = DEFAULT_TIMEOUT_MS, signal: externalSignal, ...rest } = options

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData

  const headers: Record<string, string> = {
    // Let the browser set Content-Type (with multipart boundary) for FormData
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(customHeaders as Record<string, string>),
  }

  const token = await getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const timeoutController = new AbortController()
  const timer = setTimeout(() => timeoutController.abort(), timeout)

  // Compose: abort if either the timeout fires or the caller aborts
  const combinedController = new AbortController()
  const onExternalAbort = () => combinedController.abort()
  const onTimeoutAbort = () => combinedController.abort()
  timeoutController.signal.addEventListener('abort', onTimeoutAbort)
  externalSignal?.addEventListener('abort', onExternalAbort)
  // If the external signal was already aborted, abort immediately
  if (externalSignal?.aborted) combinedController.abort()

  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...rest,
      headers,
      body: body !== undefined ? (isFormData ? (body as FormData) : JSON.stringify(body)) : undefined,
      signal: combinedController.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    if (err instanceof DOMException && err.name === 'AbortError') {
      // Distinguish user cancellation from timeout
      if (externalSignal?.aborted) {
        throw new ApiError(0, 'Request Cancelled', {
          detail: 'Request was cancelled.',
        })
      }
      throw new ApiError(0, 'Request Timeout', {
        detail: `Request timed out after ${timeout / 1000}s. Please try again.`,
      })
    }
    throw new ApiError(0, 'Network Error', {
      detail: 'Unable to reach the server. Check your internet connection and try again.',
    })
  } finally {
    clearTimeout(timer)
    timeoutController.signal.removeEventListener('abort', onTimeoutAbort)
    externalSignal?.removeEventListener('abort', onExternalAbort)
  }

  if (!response.ok) {
    let errorBody: unknown
    try {
      errorBody = await response.json()
    } catch {
      errorBody = await response.text()
    }
    throw new ApiError(response.status, response.statusText, errorBody)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export const api = {
  get<T>(path: string, options?: Omit<RequestOptions, 'method'>): Promise<T> {
    return request<T>(path, { ...options, method: 'GET' })
  },

  post<T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(path, { ...options, method: 'POST', body })
  },

  put<T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(path, { ...options, method: 'PUT', body })
  },

  delete<T>(path: string, options?: Omit<RequestOptions, 'method'>): Promise<T> {
    return request<T>(path, { ...options, method: 'DELETE' })
  },
}
