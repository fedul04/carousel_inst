export type PatternType =
  | "dots"
  | "texture2"
  | "squares"
  | "lines"
  | "grid"
  | "bubbles"

export type FontName =
  | "inter"
  | "fira_code"
  | "roboto_condensed"
  | "jost"
  | "caveat"
  | "source_sans_3"

export type TextCase = "upper" | "title" | "lower"

export interface PatternSettings {
  enabled: boolean
  type: PatternType
  opacity: number
  scale: number
}

export interface DimmingSettings {
  enabled: boolean
  strength: number
}

export interface BackgroundStyleTokens {
  pattern: PatternSettings
  dimming: DimmingSettings
  image_asset_id: string | null
}

export interface TypographyTokens {
  font: FontName
  size: number
  line_height: number
  letter_spacing: number
  weight: number
  case: TextCase
}

export interface StyleTokens {
  accent_color: string
  highlight_color: string
  background: BackgroundStyleTokens
  title: TypographyTokens
  body: TypographyTokens
}

export type StyleTokensPatch = Partial<{
  accent_color: string
  highlight_color: string
  background: Partial<{
    pattern: Partial<PatternSettings>
    dimming: Partial<DimmingSettings>
    image_asset_id: string | null
  }>
  title: Partial<TypographyTokens>
  body: Partial<TypographyTokens>
}>

export const FONT_LABELS: Record<FontName, string> = {
  inter: "Inter",
  fira_code: "Fira Code",
  roboto_condensed: "Roboto Condensed",
  jost: "Jost",
  caveat: "Caveat",
  source_sans_3: "Source Sans 3",
}

export const DEFAULT_STYLE_TOKENS: StyleTokens = {
  accent_color: "#3B37D2",
  highlight_color: "#3B37D2",
  background: {
    pattern: {
      enabled: false,
      type: "dots",
      opacity: 0.18,
      scale: 1,
    },
    dimming: {
      enabled: false,
      strength: 0,
    },
    image_asset_id: null,
  },
  title: {
    font: "inter",
    size: 82,
    line_height: 0.98,
    letter_spacing: 0,
    weight: 800,
    case: "title",
  },
  body: {
    font: "inter",
    size: 44,
    line_height: 1.28,
    letter_spacing: 0,
    weight: 500,
    case: "title",
  },
}

export function deepMerge<T extends Record<string, any>>(base: T, patch: Record<string, any>): T {
  const result: Record<string, any> = { ...base }
  for (const [key, value] of Object.entries(patch)) {
    if (
      value &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      result[key] &&
      typeof result[key] === "object" &&
      !Array.isArray(result[key])
    ) {
      result[key] = deepMerge(result[key], value)
    } else {
      result[key] = value
    }
  }
  return result as T
}

export function normalizeStyleTokens(raw?: Partial<StyleTokens> | null): StyleTokens {
  return deepMerge(DEFAULT_STYLE_TOKENS, raw || {})
}

export function mergeStyleTokens(base: StyleTokens, patch: StyleTokensPatch): StyleTokens {
  return normalizeStyleTokens(deepMerge(base, patch as Record<string, any>))
}

export function applyTextCase(text: string, mode: TextCase): string {
  if (mode === "upper") return text.toUpperCase()
  if (mode === "lower") return text.toLowerCase()
  // "Aa" mode in UI means natural casing (no forced transform).
  return text
}
