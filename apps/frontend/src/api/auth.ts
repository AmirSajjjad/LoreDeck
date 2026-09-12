import type { ApiError } from '@/types/api'

export interface AccessTokenProvider {
  getAccessToken(): string | null | Promise<string | null>
}

export type UnauthorizedListener = (error: ApiError) => void

let tokenProvider: AccessTokenProvider | undefined
let unauthorizedDispatched = false
const unauthorizedListeners = new Set<UnauthorizedListener>()

export function setAccessTokenProvider(provider?: AccessTokenProvider): void {
  tokenProvider = provider
}

export async function resolveAccessToken(): Promise<string | undefined> {
  const token = (await tokenProvider?.getAccessToken())?.trim()
  return token || undefined
}

export function onUnauthorized(listener: UnauthorizedListener): () => void {
  unauthorizedListeners.add(listener)
  return () => unauthorizedListeners.delete(listener)
}

export function emitUnauthorized(error: ApiError): void {
  if (unauthorizedDispatched) return

  unauthorizedDispatched = true
  for (const listener of unauthorizedListeners) listener(error)
}

export function resetUnauthorizedEvent(): void {
  unauthorizedDispatched = false
}
