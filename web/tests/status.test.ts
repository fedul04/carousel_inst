import { describe, expect, it } from "vitest"

import { statusClass, statusLabel } from "../utils/status"

describe("status utils", () => {
  it("maps known labels", () => {
    expect(statusLabel("ready")).toBe("Готово")
    expect(statusLabel("failed")).toBe("Ошибка")
  })

  it("maps classes", () => {
    expect(statusClass("done")).toBe("status-success")
    expect(statusClass("running")).toBe("status-info")
    expect(statusClass("unknown")).toBe("status-neutral")
  })
})
