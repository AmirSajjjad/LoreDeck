import { getEnvironment } from '@/api/environment'

export function resolveProfileImageUrl(source: string | null): string | undefined {
  if (!source?.trim()) return undefined

  try {
    const url = new URL(source, `${getEnvironment().apiBaseUrl}/`)
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.toString() : undefined
  } catch {
    return undefined
  }
}
