<script setup lang="ts">
import { applyTextCase, mergeStyleTokens, normalizeStyleTokens, type StyleTokens } from "~/utils/styleTokens"
import { isDarkTemplate, type TemplatePreset } from "~/utils/templates"

interface SlideLike {
  order: number
  title: string
  body: string
  footer_cta?: string | null
  design_overrides?: Record<string, any>
}

interface DesignLike {
  template: TemplatePreset
  bg_type: "color" | "image"
  bg_value: string
  bg_overlay: number
  layout_padding: number
  align_x: "left" | "center" | "right"
  align_y: "top" | "center" | "bottom"
  show_header: boolean
  show_footer: boolean
  header_text: string
  footer_text: string
  style_tokens?: Partial<StyleTokens>
}

const props = defineProps<{
  slide: SlideLike
  design: DesignLike
  compact?: boolean
}>()

const EXPORT_CANVAS_WIDTH = 1080
const MIN_PREVIEW_SCALE = 0.22

const canvasRef = ref<HTMLElement | null>(null)
const previewScale = ref(420 / EXPORT_CANVAS_WIDTH)
let resizeObserver: ResizeObserver | null = null

const fontFamilyMap: Record<string, string> = {
  inter: '"Inter", "Segoe UI", Arial, sans-serif',
  fira_code: '"Fira Code", "Consolas", "Courier New", monospace',
  roboto_condensed: '"Roboto Condensed", "Arial Narrow", Arial, sans-serif',
  jost: '"Jost", "Segoe UI", Arial, sans-serif',
  caveat: '"Caveat", "Segoe UI", Arial, sans-serif',
  source_sans_3: '"Source Sans 3", "Segoe UI", Arial, sans-serif',
}

const merged = computed(() => {
  const overrides = props.slide.design_overrides || {}
  const baseStyleTokens = normalizeStyleTokens(props.design.style_tokens || {})
  const styleTokens = overrides.style_tokens
    ? mergeStyleTokens(baseStyleTokens, overrides.style_tokens)
    : baseStyleTokens

  return {
    ...props.design,
    template: (overrides.template || props.design.template) as DesignLike["template"],
    bg_type: (overrides.bg_type || props.design.bg_type) as DesignLike["bg_type"],
    bg_value: overrides.bg_value || props.design.bg_value,
    bg_overlay:
      typeof overrides.bg_overlay === "number"
        ? overrides.bg_overlay
        : props.design.bg_overlay,
    layout_padding:
      typeof overrides.layout_padding === "number"
        ? overrides.layout_padding
        : props.design.layout_padding,
    align_x: (overrides.align_x || props.design.align_x) as DesignLike["align_x"],
    align_y: (overrides.align_y || props.design.align_y) as DesignLike["align_y"],
    show_header:
      typeof overrides.show_header === "boolean"
        ? overrides.show_header
        : props.design.show_header,
    show_footer:
      typeof overrides.show_footer === "boolean"
        ? overrides.show_footer
        : props.design.show_footer,
    header_text: overrides.header_text || props.design.header_text,
    footer_text: overrides.footer_text || props.design.footer_text,
    style_tokens: styleTokens,
  }
})

const currentStyleTokens = computed(() => merged.value.style_tokens)
const contentPadding = computed(() =>
  Math.round(merged.value.layout_padding * previewScale.value),
)

const canvasStyle = computed(() => {
  const d = merged.value
  if (d.bg_type === "image") {
    return {
      backgroundImage: `url(${d.bg_value})`,
      backgroundSize: "cover",
      backgroundPosition: "center",
    }
  }
  return buildTemplateBackgroundStyle(
    d.template,
    d.bg_value,
    currentStyleTokens.value.accent_color,
  )
})

const patternStyle = computed(() => {
  const tokens = currentStyleTokens.value
  const pattern = tokens.background.pattern
  if (!pattern.enabled) {
    return { display: "none" }
  }
  const alpha = Math.max(0, Math.min(1, pattern.opacity))
  const color = hexToRgba(tokens.accent_color, alpha)
  const scale = Math.max(0.4, Math.min(2.5, pattern.scale))

  if (pattern.type === "texture2") {
    const size = `${Math.round(28 * scale)}px`
    return {
      backgroundImage: `repeating-linear-gradient(45deg, ${color} 0 1px, transparent 1px ${size})`,
    }
  }
  if (pattern.type === "squares") {
    const size = `${Math.round(26 * scale)}px`
    return {
      backgroundImage:
        `repeating-linear-gradient(0deg, ${color} 0 1px, transparent 1px ${size}),` +
        `repeating-linear-gradient(90deg, ${color} 0 1px, transparent 1px ${size})`,
    }
  }
  if (pattern.type === "lines") {
    const size = `${Math.round(24 * scale)}px`
    return {
      backgroundImage: `repeating-linear-gradient(90deg, ${color} 0 1px, transparent 1px ${size})`,
    }
  }
  if (pattern.type === "grid") {
    const size = `${Math.round(22 * scale)}px`
    return {
      backgroundImage:
        `repeating-linear-gradient(0deg, ${color} 0 1px, transparent 1px ${size}),` +
        `repeating-linear-gradient(90deg, ${color} 0 1px, transparent 1px ${size})`,
    }
  }
  if (pattern.type === "bubbles") {
    const size = `${Math.round(84 * scale)}px`
    const soft = hexToRgba(tokens.accent_color, alpha * 0.65)
    return {
      backgroundImage:
        `radial-gradient(circle at 18% 22%, ${color} 0 18px, transparent 19px),` +
        `radial-gradient(circle at 78% 30%, ${soft} 0 14px, transparent 15px),` +
        `radial-gradient(circle at 62% 78%, ${color} 0 20px, transparent 21px)`,
      backgroundSize: `${size} ${size}`,
    }
  }
  const size = `${Math.round(24 * scale)}px`
  return {
    backgroundImage: `radial-gradient(circle, ${color} 0 1.5px, transparent 1.8px)`,
    backgroundSize: `${size} ${size}`,
  }
})

const overlayOpacity = computed(() => {
  const d = merged.value
  const dimming = currentStyleTokens.value.background.dimming
  const extra = dimming.enabled ? dimming.strength : 0
  return Math.min(1, Math.max(0, d.bg_overlay + extra))
})

const textColor = computed(() => (isDarkTemplate(merged.value.template) ? "#f8f9fb" : "#111319"))
const alignClass = computed(
  () => `align-x-${merged.value.align_x} align-y-${merged.value.align_y}`,
)

function computeTextComplexity(raw: string) {
  const plain = raw.replaceAll(/\*\*(.+?)\*\*/gs, "$1").trim()
  const lines = plain.split(/\n+/).map((line) => line.trim()).filter(Boolean)
  const words = plain.split(/\s+/).filter(Boolean)
  const longestWord = words.reduce((max, word) => Math.max(max, word.length), 0)
  return {
    length: plain.length,
    lines: Math.max(1, lines.length),
    longestWord,
  }
}

function computeTextFit(raw: string, kind: "title" | "body") {
  const metrics = computeTextComplexity(raw)
  if (kind === "title") {
    const score = metrics.length + metrics.longestWord * 1.9 + metrics.lines * 34
    if (score > 220) return 0.58
    if (score > 188) return 0.66
    if (score > 154) return 0.74
    if (score > 126) return 0.84
    return 1
  }
  const score = metrics.length + metrics.longestWord * 1.5 + metrics.lines * 18
  if (score > 760) return 0.62
  if (score > 620) return 0.7
  if (score > 500) return 0.78
  if (score > 390) return 0.86
  return 1
}

const titleStyle = computed(() => {
  const title = currentStyleTokens.value.title
  const scale = previewScale.value
  const fit = computeTextFit(props.slide.title, "title")
  return {
    fontFamily: fontFamilyMap[title.font],
    fontSize: `${Math.max(14, Math.round(title.size * scale * fit))}px`,
    lineHeight: String(title.line_height),
    letterSpacing: `${(title.letter_spacing * scale).toFixed(2)}px`,
    fontWeight: String(title.weight),
  }
})

const bodyStyle = computed(() => {
  const body = currentStyleTokens.value.body
  const scale = previewScale.value
  const fit = computeTextFit(props.slide.body, "body")
  return {
    fontFamily: fontFamilyMap[body.font],
    fontSize: `${Math.max(11, Math.round(body.size * scale * fit))}px`,
    lineHeight: String(body.line_height),
    letterSpacing: `${(body.letter_spacing * scale).toFixed(2)}px`,
    fontWeight: String(body.weight),
  }
})

const titleHtml = computed(() =>
  richTextToHtml(
    props.slide.title,
    currentStyleTokens.value.title.case,
    currentStyleTokens.value.highlight_color,
  ),
)

const bodyHtml = computed(() =>
  richTextToHtml(
    props.slide.body,
    currentStyleTokens.value.body.case,
    currentStyleTokens.value.highlight_color,
  ),
)

function hexToRgba(hex: string, alpha: number) {
  const value = hex.replace("#", "").trim()
  const normalized =
    value.length === 3
      ? value
          .split("")
          .map((char) => `${char}${char}`)
          .join("")
      : value
  const safe = normalized.length === 6 ? normalized : "3B37D2"
  const r = Number.parseInt(safe.slice(0, 2), 16)
  const g = Number.parseInt(safe.slice(2, 4), 16)
  const b = Number.parseInt(safe.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function buildTemplateBackgroundStyle(
  template: TemplatePreset,
  bgValue: string,
  accentColor: string,
) {
  if (template === "bold") {
    return { background: resolveTemplateBase(bgValue, "#3B37D2") }
  }
  if (template === "minimal") {
    return { background: bgValue || "#F4F1E9" }
  }
  if (template === "neon") {
    const base = resolveTemplateBase(bgValue, "#131A3A")
    const glow = hexToRgba(accentColor, 0.58)
    const glowSoft = hexToRgba(accentColor, 0.22)
    return {
      backgroundImage:
        `radial-gradient(circle at 18% 18%, ${glow} 0 16%, transparent 48%),` +
        `radial-gradient(circle at 82% 74%, ${glowSoft} 0 20%, transparent 55%),` +
        `linear-gradient(160deg, ${base} 0%, #0d122b 100%)`,
      backgroundSize: "cover",
      backgroundPosition: "center",
    }
  }
  if (template === "soft") {
    const base = resolveTemplateBase(bgValue, "#E9EDF7")
    const tint = hexToRgba(accentColor, 0.22)
    return {
      backgroundImage:
        `radial-gradient(circle at 84% 16%, ${tint} 0 28%, transparent 56%),` +
        `linear-gradient(165deg, ${base} 0%, #ffffff 66%)`,
    }
  }
  if (template === "noir") {
    const base = resolveTemplateBase(bgValue, "#15171D")
    const line = hexToRgba("#FFFFFF", 0.08)
    return {
      backgroundColor: base,
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.18) 100%)," +
        `repeating-linear-gradient(90deg, ${line} 0 1px, transparent 1px 34px)`,
    }
  }
  if (template === "aurora") {
    const base = resolveTemplateBase(bgValue, "#10293F")
    const glowA = hexToRgba(accentColor, 0.48)
    const glowB = hexToRgba("#64E8FF", 0.36)
    return {
      backgroundImage:
        `radial-gradient(circle at 18% 18%, ${glowB} 0 18%, transparent 52%),` +
        `radial-gradient(circle at 84% 74%, ${glowA} 0 22%, transparent 58%),` +
        `linear-gradient(160deg, #0b1b2b 0%, ${base} 48%, #1d3f55 100%)`,
      backgroundSize: "cover",
      backgroundPosition: "center",
    }
  }
  if (template === "sunset") {
    const base = resolveTemplateBase(bgValue, "#FF955F")
    return {
      backgroundImage:
        "radial-gradient(circle at 14% 20%, rgba(255,242,182,0.62) 0 20%, transparent 50%)," +
        `linear-gradient(160deg, #ffd26a 0%, ${base} 42%, #ff6f7f 72%, #6f3b9d 100%)`,
    }
  }
  if (template === "synthwave") {
    const base = resolveTemplateBase(bgValue, "#1A103F")
    const neon = hexToRgba(accentColor, 0.4)
    return {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.46) 100%)," +
        `radial-gradient(circle at 78% 16%, ${neon} 0 14%, transparent 44%),` +
        `linear-gradient(145deg, #2b174f 0%, ${base} 52%, #0b0f2d 100%)`,
      backgroundSize: "cover",
      backgroundPosition: "center",
    }
  }
  if (template === "paper") {
    const base = resolveTemplateBase(bgValue, "#F7EADB")
    return {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(50,61,79,0.05) 0 1px, transparent 1px 28px)," +
        `linear-gradient(165deg, #fdf4e8 0%, ${base} 56%, #efe0cc 100%)`,
    }
  }
  if (template === "matrix") {
    const base = resolveTemplateBase(bgValue, "#0D2F1F")
    const grid = hexToRgba("#86FFB5", 0.14)
    return {
      backgroundImage:
        "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.76) 100%)," +
        `repeating-linear-gradient(90deg, ${grid} 0 1px, transparent 1px 26px),` +
        `linear-gradient(160deg, #0a1f15 0%, ${base} 48%, #15492c 100%)`,
    }
  }
  if (template === "candy") {
    const base = resolveTemplateBase(bgValue, "#FF9D73")
    return {
      backgroundImage:
        "radial-gradient(circle at 18% 16%, rgba(255,255,255,0.52) 0 16%, transparent 48%)," +
        "radial-gradient(circle at 82% 72%, rgba(255,255,255,0.38) 0 18%, transparent 52%)," +
        `linear-gradient(150deg, #ff7db7 0%, ${base} 38%, #ffd56c 72%, #8bc6ff 100%)`,
    }
  }
  if (template === "lava") {
    const base = resolveTemplateBase(bgValue, "#5E1F1A")
    return {
      backgroundImage:
        "radial-gradient(circle at 18% 20%, rgba(255,197,112,0.34) 0 15%, transparent 42%)," +
        "radial-gradient(circle at 86% 78%, rgba(255,82,82,0.24) 0 18%, transparent 50%)," +
        `linear-gradient(150deg, #2a1311 0%, ${base} 42%, #b53b24 74%, #f26a2a 100%)`,
    }
  }
  if (template === "frost") {
    const base = resolveTemplateBase(bgValue, "#C9E8FF")
    return {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.36) 0%, rgba(255,255,255,0.08) 100%)," +
        "radial-gradient(circle at 12% 18%, rgba(255,255,255,0.66) 0 18%, transparent 50%)," +
        `linear-gradient(160deg, #d9f3ff 0%, ${base} 48%, #b1dcff 100%)`,
    }
  }
  if (template === "mono") {
    const base = resolveTemplateBase(bgValue, "#262833")
    return {
      backgroundImage:
        "repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 30px)," +
        `linear-gradient(165deg, #191a1f 0%, ${base} 52%, #111217 100%)`,
    }
  }
  if (template === "velvet") {
    const base = resolveTemplateBase(bgValue, "#4F1F60")
    return {
      backgroundImage:
        "radial-gradient(circle at 84% 16%, rgba(255,255,255,0.18) 0 16%, transparent 48%)," +
        `linear-gradient(145deg, #2e1038 0%, ${base} 46%, #27102f 100%)`,
    }
  }
  if (template === "blueprint") {
    const base = resolveTemplateBase(bgValue, "#1B4A87")
    return {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(209,232,255,0.22) 0 1px, transparent 1px 26px)," +
        "repeating-linear-gradient(90deg, rgba(209,232,255,0.2) 0 1px, transparent 1px 26px)," +
        `linear-gradient(165deg, #113463 0%, ${base} 52%, #0f2a4f 100%)`,
    }
  }
  if (template === "hologram") {
    return {
      backgroundImage:
        "linear-gradient(115deg, rgba(255,255,255,0.18) 0 12%, rgba(255,255,255,0) 12% 100%)," +
        "linear-gradient(145deg, #6e57ff 0%, #2fd4ff 34%, #6dffb6 62%, #f9ff7a 100%)",
    }
  }
  if (template === "cosmos") {
    const base = resolveTemplateBase(bgValue, "#17173A")
    return {
      backgroundImage:
        "radial-gradient(circle at 18% 14%, rgba(121,156,255,0.54) 0 18%, transparent 52%)," +
        "radial-gradient(circle at 84% 76%, rgba(199,110,255,0.46) 0 20%, transparent 56%)," +
        `linear-gradient(160deg, #090b1b 0%, ${base} 46%, #0f2c55 100%)`,
    }
  }
  if (template === "ember") {
    const base = resolveTemplateBase(bgValue, "#4A1816")
    return {
      backgroundImage:
        "radial-gradient(circle at 16% 18%, rgba(255,177,88,0.5) 0 16%, transparent 48%)," +
        "radial-gradient(circle at 82% 74%, rgba(255,75,75,0.34) 0 20%, transparent 54%)," +
        `linear-gradient(150deg, #250f0f 0%, ${base} 48%, #8a2e24 100%)`,
    }
  }
  if (template === "oasis") {
    const base = resolveTemplateBase(bgValue, "#BDF3E7")
    return {
      backgroundImage:
        "radial-gradient(circle at 88% 18%, rgba(255,255,255,0.45) 0 20%, transparent 52%)," +
        `linear-gradient(160deg, #d8fff7 0%, ${base} 46%, #94decb 100%)`,
    }
  }
  if (template === "graphite") {
    const base = resolveTemplateBase(bgValue, "#252A36")
    return {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 26px)," +
        `linear-gradient(165deg, #17191f 0%, ${base} 54%, #0f1116 100%)`,
    }
  }
  if (template === "citrus") {
    const base = resolveTemplateBase(bgValue, "#D3F45A")
    return {
      backgroundImage:
        "radial-gradient(circle at 14% 22%, rgba(255,255,255,0.56) 0 14%, transparent 44%)," +
        `linear-gradient(158deg, #f9f871 0%, ${base} 44%, #8de86e 100%)`,
    }
  }
  if (template === "vintage") {
    const base = resolveTemplateBase(bgValue, "#E9D7B7")
    return {
      backgroundImage:
        "repeating-linear-gradient(90deg, rgba(58,39,20,0.06) 0 1px, transparent 1px 30px)," +
        `linear-gradient(165deg, #f4e6cc 0%, ${base} 52%, #d8bf98 100%)`,
    }
  }
  return { background: bgValue || "#F5ED4D" }
}

function resolveTemplateBase(bgValue: string, fallback: string) {
  const value = (bgValue || "").trim().toLowerCase()
  if (!value || value === "#f4f1e9" || value === "#f5ed4d") {
    return fallback
  }
  return bgValue
}

function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;")
}

function richTextToHtml(text: string, mode: "upper" | "title" | "lower", highlightColor: string) {
  const segments: string[] = []
  const regex = /\*\*(.+?)\*\*/gs
  let cursor = 0
  for (const match of text.matchAll(regex)) {
    const start = match.index ?? 0
    if (start > cursor) {
      const plain = applyTextCase(text.slice(cursor, start), mode)
      segments.push(escapeHtml(plain).replaceAll("\n", "<br />"))
    }
    const highlighted = applyTextCase(match[1] || "", mode)
    segments.push(
      `<span class="canvas-highlight" style="color:${escapeHtml(highlightColor)}">${escapeHtml(highlighted).replaceAll("\n", "<br />")}</span>`,
    )
    cursor = start + match[0].length
  }
  if (cursor < text.length) {
    const plain = applyTextCase(text.slice(cursor), mode)
    segments.push(escapeHtml(plain).replaceAll("\n", "<br />"))
  }
  return segments.join("") || "&nbsp;"
}

const updatePreviewScale = () => {
  const width = canvasRef.value?.clientWidth || 420
  const raw = width / EXPORT_CANVAS_WIDTH
  previewScale.value = Math.max(MIN_PREVIEW_SCALE, Math.min(1, raw))
}

onMounted(() => {
  updatePreviewScale()
  if (typeof ResizeObserver !== "undefined" && canvasRef.value) {
    resizeObserver = new ResizeObserver(() => updatePreviewScale())
    resizeObserver.observe(canvasRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
})
</script>

<template>
  <div
    ref="canvasRef"
    class="slide-canvas"
    :class="[`template-${merged.template}`, alignClass, compact ? 'compact' : '']"
    :style="canvasStyle"
  >
    <div class="pattern-layer" :style="patternStyle" />
    <div class="overlay" :style="{ opacity: String(overlayOpacity) }" />
    <div class="canvas-content" :style="{ padding: `${contentPadding}px`, color: textColor }">
      <div v-if="merged.show_header" class="canvas-header">
        <span>{{ merged.header_text }}</span>
        <span>{{ slide.order }}</span>
      </div>
      <div class="canvas-main">
        <h3 class="canvas-title" :style="titleStyle" v-html="titleHtml" />
        <p class="canvas-body" :style="bodyStyle" v-html="bodyHtml" />
      </div>
      <div v-if="merged.show_footer" class="canvas-footer">
        <span>{{ slide.footer_cta || merged.footer_text }}</span>
        <span>&rarr;</span>
      </div>
    </div>
  </div>
</template>
