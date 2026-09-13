import { getEnvironment } from '@/api/environment'

export function resolveCardImageUrl(imagePath: string | null): string | undefined {
  const path = imagePath?.trim().replace(/^\/+/, '')
  if (!path || path.split('/').includes('..') || path.includes('\\')) return undefined

  const staticPath = path.startsWith('static/') ? path : `static/${path}`
  return new URL(staticPath, `${getEnvironment().apiBaseUrl}/`).toString()
}
