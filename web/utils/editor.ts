import {
  type StyleTokens,
  type StyleTokensPatch,
  normalizeStyleTokens,
} from "./styleTokens"
import type { TemplatePreset } from "./templates"

export interface DesignState {
  template: TemplatePreset
  bgType: "color" | "image"
  bgValue: string
  bgOverlay: number
  layoutPadding: number
  alignX: "left" | "center" | "right"
  alignY: "top" | "center" | "bottom"
  showHeader: boolean
  showFooter: boolean
  headerText: string
  footerText: string
  styleTokens: StyleTokens
}

export function normalizeDesignState(input: Partial<DesignState>): DesignState {
  return {
    template: input.template || "classic",
    bgType: input.bgType || "color",
    bgValue: input.bgValue || "#F4F1E9",
    bgOverlay: typeof input.bgOverlay === "number" ? input.bgOverlay : 0,
    layoutPadding: typeof input.layoutPadding === "number" ? input.layoutPadding : 56,
    alignX: input.alignX || "left",
    alignY: input.alignY || "top",
    showHeader: input.showHeader ?? true,
    showFooter: input.showFooter ?? true,
    headerText: input.headerText || "@username",
    footerText: input.footerText || "Draft AI",
    styleTokens: normalizeStyleTokens(input.styleTokens),
  }
}

export function buildFullDesignPatch(state: DesignState, applyToAll: boolean) {
  return {
    template: state.template,
    bg: {
      type: state.bgType,
      value: state.bgValue,
      overlay: state.bgOverlay,
    },
    layout: {
      padding: state.layoutPadding,
      align_x: state.alignX,
      align_y: state.alignY,
    },
    header: {
      show: state.showHeader,
      text: state.headerText,
    },
    footer: {
      show: state.showFooter,
      text: state.footerText,
    },
    style_tokens: state.styleTokens,
    apply_to_all: applyToAll,
  }
}

export function buildStyleTokensPatch(
  patch: StyleTokensPatch,
  applyToAll: boolean,
) {
  return {
    style_tokens: patch,
    apply_to_all: applyToAll,
  }
}
