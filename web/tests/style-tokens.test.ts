import { describe, expect, it } from "vitest"
import {
  applyTextCase,
  mergeStyleTokens,
  normalizeStyleTokens,
} from "../utils/styleTokens"

describe("style tokens helpers", () => {
  it("applies text case modes", () => {
    expect(applyTextCase("hello world", "upper")).toBe("HELLO WORLD")
    expect(applyTextCase("HELLO WORLD", "lower")).toBe("hello world")
    expect(applyTextCase("hELLo woRLD", "title")).toBe("hELLo woRLD")
  })

  it("deep-merges partial style tokens", () => {
    const base = normalizeStyleTokens()
    const merged = mergeStyleTokens(base, {
      title: { size: 90 },
      background: { pattern: { enabled: true, type: "grid" } },
    })

    expect(merged.title.size).toBe(90)
    expect(merged.background.pattern.enabled).toBe(true)
    expect(merged.background.pattern.type).toBe("grid")
    expect(merged.body.size).toBe(base.body.size)
  })
})
