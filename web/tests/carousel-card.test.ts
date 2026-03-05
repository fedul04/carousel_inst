import { describe, expect, it } from "vitest"

import { makePreviewBody } from "../utils/preview"

describe("carousel preview helper", () => {
  it("truncates long text", () => {
    const source = "x".repeat(200)
    const preview = makePreviewBody(source, 40)
    expect(preview.length).toBe(40)
    expect(preview.endsWith("…")).toBe(true)
  })
})
