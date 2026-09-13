import { getEnvironment } from '@/api/environment'

export function resolveCardImageUrl(imagePath: string | null): string | undefined {
  const path = imagePath?.trim().replace(/^\/+/, '')
  if (!path || path.includes('://') || path.split('/').includes('..') || path.includes('\\')) {
    return undefined
  }

  const staticPath = path.startsWith('static/') ? path : `static/${path}`
  const apiBaseUrl = new URL(`${getEnvironment().apiBaseUrl}/`, window.location.origin)
  return new URL(staticPath, apiBaseUrl).toString()
}
