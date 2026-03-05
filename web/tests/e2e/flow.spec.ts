import { expect, test } from "@playwright/test"

test.describe("carousel flow", () => {
  test.skip(!process.env.E2E_RUN, "Set E2E_RUN=1 to execute against running stack")

  test("create -> generate -> edit -> export", async ({ page, request }) => {
    await page.goto("/carousels/new")
    await page.getByPlaceholder("Название карусели").fill("E2E карусель")
    await page
      .getByPlaceholder("Вставьте текст поста или черновик")
      .fill("Это тестовый текст для генерации слайдов в e2e.")

    await page.getByRole("button", { name: "Создать черновик" }).click()
    await page.getByRole("button", { name: "Сгенерировать" }).click()

    await page.waitForURL(/\/carousels\/.+\/editor/, { timeout: 90_000 })
    await expect(page.getByRole("button", { name: "Экспорт ZIP" })).toBeVisible()
    const urlMatch = page.url().match(/\/carousels\/([^/]+)\/editor/)
    const carouselId = urlMatch?.[1]
    expect(carouselId).toBeTruthy()

    await page.getByRole("button", { name: /^Текст$/ }).click()
    await page.getByRole("button", { name: "Больше настроек" }).click()
    await page
      .locator(".typography-controls input[type='range']")
      .first()
      .fill("56")
    await page.getByRole("button", { name: "Применить" }).first().click()

    await page.getByRole("button", { name: /^Фон$/ }).click()
    await page.getByLabel("Узор").check()
    await page.getByRole("button", { name: "Сетка" }).click()
    await page.getByRole("button", { name: "Применить" }).first().click()

    // apply_to_all выключен по умолчанию: изменения должны лечь в текущий слайд, не в global design.
    const designResp = await request.get(`http://localhost:8000/api/carousels/${carouselId}/design`)
    expect(designResp.ok()).toBeTruthy()
    const designJson = await designResp.json()
    expect(designJson.style_tokens.body.size).toBe(44)

    const slidesResp = await request.get(`http://localhost:8000/api/carousels/${carouselId}/slides`)
    expect(slidesResp.ok()).toBeTruthy()
    const slidesJson = await slidesResp.json()
    const firstSlide = slidesJson.items?.[0]
    expect(firstSlide.design_overrides.style_tokens.body.size).toBe(56)
    expect(firstSlide.design_overrides.style_tokens.background.pattern.enabled).toBe(true)

    await page.getByRole("button", { name: "Экспорт ZIP" }).click()
    await expect(page.getByRole("link", { name: "Скачать ZIP" })).toBeVisible({
      timeout: 90_000,
    })
  })
})
