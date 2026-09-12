export interface AppEnvironment {
  apiBaseUrl: string
}

let cachedEnvironment: AppEnvironment | undefined

export function parseEnvironment(source: Pick<ImportMetaEnv, 'VITE_API_BASE_URL'>): AppEnvironment {
  const rawBaseUrl = source.VITE_API_BASE_URL?.trim()
  if (!rawBaseUrl) {
    throw new Error(
      'VITE_API_BASE_URL is required. Copy .env.sample to .env.local and configure it.',
    )
  }

  let parsedUrl: URL
  try {
    parsedUrl = new URL(rawBaseUrl)
  } catch {
    throw new Error('VITE_API_BASE_URL must be a valid absolute HTTP(S) URL.')
  }

  if (
    !['http:', 'https:'].includes(parsedUrl.protocol) ||
    parsedUrl.username ||
    parsedUrl.password ||
    parsedUrl.search ||
    parsedUrl.hash
  ) {
    throw new Error(
      'VITE_API_BASE_URL must use HTTP(S) and must not contain credentials, a query, or a fragment.',
    )
  }

  const apiBaseUrl = parsedUrl.toString().replace(/\/$/, '')
  return Object.freeze({ apiBaseUrl })
}

export function getEnvironment(): AppEnvironment {
  cachedEnvironment ??= parseEnvironment(import.meta.env)
  return cachedEnvironment
}
