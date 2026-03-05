import { describe, expect, it } from "vitest"

import { buildFullDesignPatch, type DesignState } from "../utils/editor"
import { normalizeStyleTokens } from "../utils/styleTokens"

describe("editor design patch", () => {
  it("builds payload with required keys", () => {
    const state: DesignState = {
      template: "bold",
      bgType: "color",
      bgValue: "#222222",
      bgOverlay: 0.3,
      layoutPadding: 52,
      alignX: "center",
      alignY: "top",
      showHeader: true,
      showFooter: false,
      headerText: "@username",
      footerText: "Draft AI",
      styleTokens: normalizeStyleTokens(),
    }

    const payload = buildFullDesignPatch(state, true)
    expect(payload.template).toBe("bold")
    expect(payload.bg.value).toBe("#222222")
    expect(payload.layout.align_x).toBe("center")
    expect(payload.style_tokens.body.size).toBeGreaterThan(10)
    expect(payload.apply_to_all).toBe(true)
  })
})
