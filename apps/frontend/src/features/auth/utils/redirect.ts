const DEFAULT_REDIRECT = '/'
const INTERNAL_ORIGIN = 'https://loredeck.invalid'

export function getSafeRedirect(value: unknown): string {
  const hasControlCharacter =
    typeof value === 'string' &&
    Array.from(value).some((character) => {
      const code = character.charCodeAt(0)
      return code <= 31 || code === 127
    })

  if (
    typeof value !== 'string' ||
    !value.startsWith('/') ||
    value.startsWith('//') ||
    value.includes('\\') ||
    hasControlCharacter
  ) {
    return DEFAULT_REDIRECT
  }

  try {
    const destination = new URL(value, INTERNAL_ORIGIN)
    if (destination.origin !== INTERNAL_ORIGIN) return DEFAULT_REDIRECT
    return `${destination.pathname}${destination.search}${destination.hash}`
  } catch {
    return DEFAULT_REDIRECT
  }
}
