const ACCESS_TOKEN_KEY = 'loredeck.access-token'

function getSessionStorage(): Storage | undefined {
  if (typeof window === 'undefined') return undefined
  return window.sessionStorage
}

export function readAccessToken(): string | null {
  try {
    return getSessionStorage()?.getItem(ACCESS_TOKEN_KEY)?.trim() || null
  } catch {
    return null
  }
}

export function writeAccessToken(token: string): void {
  const normalized = token.trim()
  if (!normalized) throw new Error('Cannot store an empty access token.')
  getSessionStorage()?.setItem(ACCESS_TOKEN_KEY, normalized)
}

export function clearAccessToken(): void {
  try {
    getSessionStorage()?.removeItem(ACCESS_TOKEN_KEY)
  } catch {
    // A blocked storage API is equivalent to an already-cleared browser session.
  }
}
