export function makePreviewBody(body: string, maxLength = 120): string {
  const normalized = body.replace(/\s+/g, " ").trim()
  if (normalized.length <= maxLength) {
    return normalized
  }
  return `${normalized.slice(0, maxLength - 1)}…`
}
