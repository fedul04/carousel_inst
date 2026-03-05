<script setup lang="ts">
import {
  buildFullDesignPatch,
  normalizeDesignState,
  type DesignState,
} from "~/utils/editor"
import {
  deepMerge,
  mergeStyleTokens,
  normalizeStyleTokens,
  type StyleTokens,
} from "~/utils/styleTokens"
import {
  TEMPLATE_OPTIONS,
  type TemplatePreset,
} from "~/utils/templates"

interface DesignPayload {
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
  style_tokens: Partial<StyleTokens>
}

interface CarouselDetails {
  id: string
  title: string
  status: string
  language: string
  slides_count: number
  design: DesignPayload | null
}

interface SlideItem {
  id: string
  carousel_id: string
  order: number
  title: string
  body: string
  footer_cta: string | null
  design_overrides: Record<string, any>
}

interface SlidesResponse {
  items: SlideItem[]
}

interface ExportJob {
  id: string
  status: string
  download_url: string | null
  error: string | null
}

interface AssetUploadResponse {
  id: string
  url: string | null
}

interface GenerationArtifacts {
  summary: string | null
  hook_variants: string[]
  title_variants: string[]
  cta_variants: string[]
  opening_lines: string[]
  post_caption_variants: string[]
  image_prompts: string[]
  audience_pains: string[]
  hashtags: string[]
  keywords: string[]
  visual_directions: string[]
}

interface GenerationJobResponse {
  id: string
  status: string
  result_json: {
    artifacts?: Partial<GenerationArtifacts>
    ingestion?: Record<string, any>
  } | null
}

const route = useRoute()
const config = useRuntimeConfig()
const api = useApi()
const carouselId = computed(() => String(route.params.id))

const carousel = ref<CarouselDetails | null>(null)
const slides = ref<SlideItem[]>([])
const selectedSlideId = ref("")
const loading = ref(true)
const errorText = ref("")
const saveInfo = ref("")
const uploadingPhoto = ref(false)
const latestUploadedPhotoId = ref<string | null>(null)
const latestUploadedPhotoUrl = ref<string | null>(null)
const generationArtifacts = ref<GenerationArtifacts | null>(null)
const generationIngestion = ref<Record<string, any> | null>(null)

const applyToAll = ref(false)
const activeTab = ref<"background" | "title" | "text">("background")

const designState = reactive<DesignState>(
  normalizeDesignState({
    template: "classic",
    bgType: "color",
    bgValue: "#F4F1E9",
    bgOverlay: 0,
    layoutPadding: 56,
    alignX: "left",
    alignY: "top",
    showHeader: true,
    showFooter: true,
    headerText: "@username",
    footerText: "Draft AI",
    styleTokens: normalizeStyleTokens(),
  }),
)

const basePhotoItems: Array<{ id: string; url: string }> = [
  { id: "figma-1", url: "/figma_refs/fb8c5a6efbbc99461884b01e0c0d9c0b25278045.jpg" },
  { id: "figma-2", url: "/figma_refs/09a288417744927a5d1e6901a3c4c518009c968d.png" },
  { id: "figma-3", url: "/figma_refs/b83b9f51cfeda5c7c271d9e2b0ddce2fa7284de6.png" },
  { id: "figma-4", url: "/figma_refs/d97e2f06663a9e5e7371b9ac39584b34c431f440.png" },
  { id: "figma-5", url: "/figma_refs/a8c04599225cc08f5f53201e2214775ab0501d03.png" },
]

const photoItems = ref<Array<{ id: string; url: string }>>([...basePhotoItems])

const buildAssetContentUrl = (assetId: string) => {
  const apiBase = String(config.public.apiBase || "http://localhost:8000/api").replace(/\/$/, "")
  return `${apiBase}/assets/${assetId}/content`
}

const addUploadedPhoto = (assetId: string) => {
  const item = { id: assetId, url: buildAssetContentUrl(assetId) }
  photoItems.value = [item, ...photoItems.value.filter((entry) => entry.id !== item.id)]
}

const collectDesignAssetIds = (
  design: DesignPayload | null,
  slideItems: SlideItem[],
): string[] => {
  const ids = new Set<string>()
  const globalId = design?.style_tokens?.background?.image_asset_id
  if (typeof globalId === "string" && globalId.length > 0) {
    ids.add(globalId)
  }

  for (const slide of slideItems) {
    const value = slide.design_overrides?.style_tokens?.background?.image_asset_id
    if (typeof value === "string" && value.length > 0) {
      ids.add(value)
    }
  }

  return [...ids]
}

const normalizeArtifacts = (
  raw: Partial<GenerationArtifacts> | undefined,
): GenerationArtifacts | null => {
  if (!raw) return null
  const toList = (value: unknown) =>
    Array.isArray(value)
      ? value
          .map((item) => String(item || "").trim())
          .filter(Boolean)
      : []
  const summary = raw.summary ? String(raw.summary).trim() : null
  const normalized: GenerationArtifacts = {
    summary,
    hook_variants: toList(raw.hook_variants),
    title_variants: toList(raw.title_variants),
    cta_variants: toList(raw.cta_variants),
    opening_lines: toList(raw.opening_lines),
    post_caption_variants: toList(raw.post_caption_variants),
    image_prompts: toList(raw.image_prompts),
    audience_pains: toList(raw.audience_pains),
    hashtags: toList(raw.hashtags),
    keywords: toList(raw.keywords),
    visual_directions: toList(raw.visual_directions),
  }
  const hasContent =
    Boolean(normalized.summary) ||
    normalized.hook_variants.length > 0 ||
    normalized.title_variants.length > 0 ||
    normalized.cta_variants.length > 0 ||
    normalized.opening_lines.length > 0 ||
    normalized.post_caption_variants.length > 0 ||
    normalized.image_prompts.length > 0 ||
    normalized.audience_pains.length > 0 ||
    normalized.hashtags.length > 0 ||
    normalized.keywords.length > 0 ||
    normalized.visual_directions.length > 0
  return hasContent ? normalized : null
}

const normalizeSlideAssetUrls = (slideItems: SlideItem[]): SlideItem[] =>
  slideItems.map((slide) => {
    const imageAssetId = slide.design_overrides?.style_tokens?.background?.image_asset_id
    if (
      slide.design_overrides?.bg_type === "image" &&
      typeof imageAssetId === "string" &&
      imageAssetId.length > 0
    ) {
      return {
        ...slide,
        design_overrides: {
          ...slide.design_overrides,
          bg_value: buildAssetContentUrl(imageAssetId),
        },
      }
    }
    return slide
  })

const exportJob = ref<ExportJob | null>(null)
const exportPolling = ref<number | null>(null)

const selectedSlide = computed(() =>
  slides.value.find((slide) => slide.id === selectedSlideId.value),
)

const refreshSlides = async () => {
  const currentId = selectedSlideId.value
  const slidesResponse = await api.get<SlidesResponse>(`/carousels/${carouselId.value}/slides`)
  slides.value = normalizeSlideAssetUrls(slidesResponse.items)
  if (currentId && slides.value.some((slide) => slide.id === currentId)) {
    selectedSlideId.value = currentId
    return
  }
  if (slides.value.length > 0) {
    selectedSlideId.value = slides.value[0].id
  }
}

const effectiveDesignState = computed<DesignState>(() => {
  const overrides = selectedSlide.value?.design_overrides || {}
  const styleTokens = mergeStyleTokens(
    normalizeStyleTokens(designState.styleTokens),
    overrides.style_tokens || {},
  )
  const bgType = (overrides.bg_type || designState.bgType) as DesignState["bgType"]
  let bgValue = overrides.bg_value || designState.bgValue
  const imageAssetId = styleTokens.background.image_asset_id
  if (bgType === "image" && typeof imageAssetId === "string" && imageAssetId.length > 0) {
    bgValue = buildAssetContentUrl(imageAssetId)
  }

  return normalizeDesignState({
    template: (overrides.template || designState.template) as DesignState["template"],
    bgType,
    bgValue,
    bgOverlay:
      typeof overrides.bg_overlay === "number" ? overrides.bg_overlay : designState.bgOverlay,
    layoutPadding:
      typeof overrides.layout_padding === "number"
        ? overrides.layout_padding
        : designState.layoutPadding,
    alignX: (overrides.align_x || designState.alignX) as DesignState["alignX"],
    alignY: (overrides.align_y || designState.alignY) as DesignState["alignY"],
    showHeader:
      typeof overrides.show_header === "boolean"
        ? overrides.show_header
        : designState.showHeader,
    showFooter:
      typeof overrides.show_footer === "boolean"
        ? overrides.show_footer
        : designState.showFooter,
    headerText: overrides.header_text || designState.headerText,
    footerText: overrides.footer_text || designState.footerText,
    styleTokens,
  })
})

const canvasDesign = computed(() => {
  const styleTokens = normalizeStyleTokens(designState.styleTokens)
  let bgValue = designState.bgValue
  const imageAssetId = styleTokens.background.image_asset_id
  if (
    designState.bgType === "image" &&
    typeof imageAssetId === "string" &&
    imageAssetId.length > 0
  ) {
    bgValue = buildAssetContentUrl(imageAssetId)
  }

  return {
    template: designState.template,
    bg_type: designState.bgType,
    bg_value: bgValue,
    bg_overlay: designState.bgOverlay,
    layout_padding: designState.layoutPadding,
    align_x: designState.alignX,
    align_y: designState.alignY,
    show_header: designState.showHeader,
    show_footer: designState.showFooter,
    header_text: designState.headerText,
    footer_text: designState.footerText,
    style_tokens: styleTokens,
  }
})

const setDesignStateFromPayload = (design: DesignPayload | null) => {
  if (!design) return
  const nextState = normalizeDesignState({
    template: design.template,
    bgType: design.bg_type,
    bgValue: design.bg_value,
    bgOverlay: design.bg_overlay,
    layoutPadding: design.layout_padding,
    alignX: design.align_x,
    alignY: design.align_y,
    showHeader: design.show_header,
    showFooter: design.show_footer,
    headerText: design.header_text,
    footerText: design.footer_text,
    styleTokens: normalizeStyleTokens(design.style_tokens),
  })
  Object.assign(designState, nextState)
}

const loadData = async () => {
  loading.value = true
  errorText.value = ""
  try {
    const [carouselResponse, slidesResponse, latestGeneration] = await Promise.all([
      api.get<CarouselDetails>(`/carousels/${carouselId.value}`),
      api.get<SlidesResponse>(`/carousels/${carouselId.value}/slides`),
      api
        .get<GenerationJobResponse>(`/generations/by-carousel/${carouselId.value}/latest`)
        .catch(() => null),
    ])
    carousel.value = carouselResponse
    slides.value = normalizeSlideAssetUrls(slidesResponse.items)
    photoItems.value = [...basePhotoItems]
    if (slides.value.length > 0) {
      selectedSlideId.value = slides.value[0].id
    }
    setDesignStateFromPayload(carouselResponse.design)
    const existingAssetIds = collectDesignAssetIds(carouselResponse.design, slides.value)
    for (const assetId of existingAssetIds) {
      addUploadedPhoto(assetId)
    }
    generationArtifacts.value = normalizeArtifacts(
      latestGeneration?.result_json?.artifacts,
    )
    const ingestion = latestGeneration?.result_json?.ingestion
    generationIngestion.value =
      ingestion && typeof ingestion === "object" && !Array.isArray(ingestion)
        ? ingestion
        : null
  } catch (error: any) {
    errorText.value = error?.data?.detail ?? error?.message ?? "Не удалось загрузить редактор"
  } finally {
    loading.value = false
  }
}

const saveSlide = async () => {
  if (!selectedSlide.value) return
  saveInfo.value = ""
  await api.patch(`/carousels/${carouselId.value}/slides/${selectedSlide.value.id}`, {
    title: selectedSlide.value.title,
    body: selectedSlide.value.body,
    footer_cta: selectedSlide.value.footer_cta,
  })
  saveInfo.value = "Текст слайда сохранен"
}

const toSlideOverridesPatch = (patch: Record<string, any>) => {
  const overrides: Record<string, any> = {}
  if (patch.template !== undefined) {
    overrides.template = patch.template
  }
  if (patch.bg) {
    overrides.bg_type = patch.bg.type
    overrides.bg_value = patch.bg.value
    overrides.bg_overlay = patch.bg.overlay
  }
  if (patch.layout) {
    overrides.layout_padding = patch.layout.padding
    overrides.align_x = patch.layout.align_x
    overrides.align_y = patch.layout.align_y
  }
  if (patch.header) {
    overrides.show_header = patch.header.show
    overrides.header_text = patch.header.text
  }
  if (patch.footer) {
    overrides.show_footer = patch.footer.show
    overrides.footer_text = patch.footer.text
  }
  if (patch.style_tokens) {
    overrides.style_tokens = patch.style_tokens
  }
  return overrides
}

const mergeOverrides = (current: Record<string, any>, patch: Record<string, any>) => {
  const next = { ...current }
  for (const [key, value] of Object.entries(patch)) {
    if (
      key === "style_tokens" &&
      value &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      next.style_tokens &&
      typeof next.style_tokens === "object" &&
      !Array.isArray(next.style_tokens)
    ) {
      next.style_tokens = deepMerge(next.style_tokens, value)
      continue
    }
    next[key] = value
  }
  return next
}

const applyPatchToCurrentSlide = async (patch: Record<string, any>) => {
  if (!selectedSlide.value) return
  const overridesPatch = toSlideOverridesPatch(patch)
  if (Object.keys(overridesPatch).length === 0) return

  const mergedOverrides = mergeOverrides(selectedSlide.value.design_overrides || {}, overridesPatch)
  const updatedSlide = await api.patch<SlideItem>(
    `/carousels/${carouselId.value}/slides/${selectedSlide.value.id}`,
    {
      design_overrides: mergedOverrides,
    },
  )
  const normalizedUpdatedSlide = normalizeSlideAssetUrls([updatedSlide])[0]
  slides.value = slides.value.map((slide) =>
    slide.id === normalizedUpdatedSlide.id ? normalizedUpdatedSlide : slide,
  )
  const imageAssetId = normalizedUpdatedSlide.design_overrides?.style_tokens?.background?.image_asset_id
  if (typeof imageAssetId === "string" && imageAssetId.length > 0) {
    addUploadedPhoto(imageAssetId)
  }
}

const patchDesign = async (patch: Record<string, any>, mode: "panel" | "global" = "panel") => {
  saveInfo.value = ""
  if (mode === "panel" && !applyToAll.value) {
    await applyPatchToCurrentSlide(patch)
    saveInfo.value = "Настройки применены к текущему слайду"
    return
  }

  const response = await api.patch<DesignPayload>(`/carousels/${carouselId.value}/design`, {
    ...patch,
    apply_to_all: applyToAll.value,
  })
  setDesignStateFromPayload(response)
  const imageAssetId = response.style_tokens?.background?.image_asset_id
  if (typeof imageAssetId === "string" && imageAssetId.length > 0) {
    addUploadedPhoto(imageAssetId)
  }
  if (applyToAll.value) {
    await refreshSlides()
  }
  saveInfo.value = "Настройки дизайна сохранены"
}

const saveFullDesign = async () => {
  const response = await api.patch<DesignPayload>(`/carousels/${carouselId.value}/design`, {
    ...buildFullDesignPatch(designState, false),
    apply_to_all: false,
  })
  setDesignStateFromPayload(response)
  saveInfo.value = "Макет сохранен"
}

const applyTemplate = async (template: TemplatePreset) => {
  saveInfo.value = ""
  const response = await api.patch<DesignPayload>(`/carousels/${carouselId.value}/design`, {
    template,
    apply_to_all: false,
  })
  setDesignStateFromPayload(response)
  saveInfo.value = "Шаблон обновлен"
}

const uploadBackgroundPhoto = async (file: File) => {
  uploadingPhoto.value = true
  try {
    const formData = new FormData()
    formData.append("file", file)
    const uploaded = await $fetch<AssetUploadResponse>("/assets/upload", {
      baseURL: config.public.apiBase,
      method: "POST",
      body: formData,
    })
    addUploadedPhoto(uploaded.id)
    latestUploadedPhotoId.value = uploaded.id
    latestUploadedPhotoUrl.value = buildAssetContentUrl(uploaded.id)
    saveInfo.value = "Фото загружено. Нажмите «Применить», чтобы сохранить фон."
  } catch (error: any) {
    saveInfo.value = error?.data?.detail ?? error?.message ?? "Не удалось загрузить фото"
  } finally {
    uploadingPhoto.value = false
  }
}

const stopExportPolling = () => {
  if (exportPolling.value) {
    clearInterval(exportPolling.value)
    exportPolling.value = null
  }
}

const pollExport = (jobId: string) => {
  stopExportPolling()
  exportPolling.value = window.setInterval(async () => {
    const job = await api.get<ExportJob>(`/exports/${jobId}`)
    exportJob.value = job
    if (job.status === "done" || job.status === "failed") {
      stopExportPolling()
    }
  }, 1500)
}

const runExport = async () => {
  exportJob.value = await api.post<ExportJob>("/exports", {
    carousel_id: carouselId.value,
    format: "png",
  })
  pollExport(exportJob.value.id)
}

onMounted(loadData)
onBeforeUnmount(stopExportPolling)
</script>

<template>
  <main class="editor-shell editor-shell-light">
    <header class="page-header">
      <div>
        <p class="eyebrow">Редактор</p>
        <h1>{{ carousel?.title || "Редактор карусели" }}</h1>
      </div>
      <div class="actions-row">
        <NuxtLink class="btn btn-secondary" to="/carousels">Назад</NuxtLink>
        <button class="btn btn-primary" :disabled="loading" @click="runExport">
          Экспорт ZIP
        </button>
      </div>
    </header>

    <p v-if="errorText" class="error-text">{{ errorText }}</p>
    <p v-if="saveInfo" class="ok-text">{{ saveInfo }}</p>
    <p v-if="loading">Загрузка редактора...</p>

    <section v-if="!loading && selectedSlide" class="editor-layout editor-layout-light">
      <aside class="slides-panel light-panel">
        <h3>Слайды</h3>
        <button
          v-for="slide in slides"
          :key="slide.id"
          class="slide-picker"
          :class="{ active: slide.id === selectedSlideId }"
          @click="selectedSlideId = slide.id"
        >
          {{ slide.order }}. {{ slide.title }}
        </button>
      </aside>

      <section class="preview-panel light-panel">
        <div class="preview-canvas-wrap">
          <SlideCanvas :slide="selectedSlide" :design="canvasDesign" />
        </div>

        <section class="control-card control-card-inline">
          <div class="control-card-header">
            <h4>Макет и служебный текст</h4>
          </div>
          <label>
            Отступ контента: {{ designState.layoutPadding }}
            <input v-model.number="designState.layoutPadding" type="range" min="16" max="120" />
          </label>
          <label>
            Выравнивание по горизонтали
            <select v-model="designState.alignX">
              <option value="left">Слева</option>
              <option value="center">По центру</option>
              <option value="right">Справа</option>
            </select>
          </label>
          <label>
            Выравнивание по вертикали
            <select v-model="designState.alignY">
              <option value="top">Сверху</option>
              <option value="center">По центру</option>
              <option value="bottom">Снизу</option>
            </select>
          </label>
          <label class="toggle-row">
            <input v-model="designState.showHeader" type="checkbox" />
            Показывать шапку
          </label>
          <label>
            Текст шапки
            <input v-model="designState.headerText" type="text" />
          </label>
          <label class="toggle-row">
            <input v-model="designState.showFooter" type="checkbox" />
            Показывать подвал
          </label>
          <label>
            Текст подвала
            <input v-model="designState.footerText" type="text" />
          </label>

          <div class="actions-row">
            <button class="btn btn-secondary" @click="loadData">Отмена</button>
            <button class="btn btn-primary" @click="saveFullDesign">Применить</button>
          </div>
        </section>

        <section class="control-card control-card-inline">
          <label>
            Заголовок слайда
            <textarea v-model="selectedSlide.title" rows="2" />
          </label>
          <label>
            Текст слайда
            <textarea v-model="selectedSlide.body" rows="5" />
          </label>
          <label>
            Footer CTA
            <input v-model="selectedSlide.footer_cta" type="text" />
          </label>
          <button class="btn btn-secondary" @click="saveSlide">Сохранить текст слайда</button>
        </section>
      </section>

      <aside class="controls-panel light-panel">
        <section class="control-card">
          <div class="control-card-header">
            <h4>Шаблон</h4>
          </div>
          <div class="template-grid">
            <button
              v-for="preset in TEMPLATE_OPTIONS"
              :key="preset.id"
              class="template-card"
              :class="{ active: designState.template === preset.id }"
              :style="preset.previewStyle"
              @click="applyTemplate(preset.id)"
            >
              {{ preset.label }}
            </button>
          </div>
        </section>

        <div class="tab-row">
          <button
            class="chip-btn"
            :class="{ active: activeTab === 'background' }"
            @click="activeTab = 'background'"
          >
            Фон
          </button>
          <button
            class="chip-btn"
            :class="{ active: activeTab === 'title' }"
            @click="activeTab = 'title'"
          >
            Заголовок
          </button>
          <button
            class="chip-btn"
            :class="{ active: activeTab === 'text' }"
            @click="activeTab = 'text'"
          >
            Текст
          </button>
        </div>

        <DesignBackgroundPanel
          v-if="activeTab === 'background'"
          :state="effectiveDesignState"
          :apply-to-all="applyToAll"
          :photos="photoItems"
          :last-uploaded-id="latestUploadedPhotoId"
          :last-uploaded-url="latestUploadedPhotoUrl"
          :uploading="uploadingPhoto"
          @upload="uploadBackgroundPhoto"
          @apply="patchDesign"
          @cancel="saveInfo = 'Изменения отменены'"
          @update:apply-to-all="applyToAll = $event"
        />
        <DesignTitlePanel
          v-if="activeTab === 'title'"
          :state="effectiveDesignState"
          :apply-to-all="applyToAll"
          @apply="patchDesign"
          @cancel="saveInfo = 'Изменения отменены'"
          @update:apply-to-all="applyToAll = $event"
        />
        <DesignTextPanel
          v-if="activeTab === 'text'"
          :state="effectiveDesignState"
          :apply-to-all="applyToAll"
          @apply="patchDesign"
          @cancel="saveInfo = 'Изменения отменены'"
          @update:apply-to-all="applyToAll = $event"
        />

        <section v-if="generationArtifacts" class="control-card">
          <div class="control-card-header">
            <h4>AI-артефакты</h4>
          </div>
          <p v-if="generationArtifacts.summary" class="control-caption">
            {{ generationArtifacts.summary }}
          </p>

          <div class="group" v-if="generationArtifacts.hook_variants.length">
            <strong>Хуки</strong>
            <span v-for="(item, idx) in generationArtifacts.hook_variants" :key="`hook-${idx}`">
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.title_variants.length">
            <strong>Варианты заголовков</strong>
            <span
              v-for="(item, idx) in generationArtifacts.title_variants"
              :key="`title-${idx}`"
            >
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.cta_variants.length">
            <strong>Варианты CTA</strong>
            <span v-for="(item, idx) in generationArtifacts.cta_variants" :key="`cta-${idx}`">
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.opening_lines.length">
            <strong>Первые строки поста</strong>
            <span
              v-for="(item, idx) in generationArtifacts.opening_lines"
              :key="`open-${idx}`"
            >
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.post_caption_variants.length">
            <strong>Варианты подписи к посту</strong>
            <span
              v-for="(item, idx) in generationArtifacts.post_caption_variants"
              :key="`caption-${idx}`"
            >
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.audience_pains.length">
            <strong>Боли аудитории</strong>
            <span
              v-for="(item, idx) in generationArtifacts.audience_pains"
              :key="`pain-${idx}`"
            >
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.image_prompts.length">
            <strong>Промпты для изображений</strong>
            <span
              v-for="(item, idx) in generationArtifacts.image_prompts"
              :key="`img-${idx}`"
            >
              • {{ item }}
            </span>
          </div>

          <div class="group" v-if="generationArtifacts.hashtags.length">
            <strong>Хештеги</strong>
            <div class="card-tags">
              <span
                v-for="(tag, idx) in generationArtifacts.hashtags"
                :key="`tag-${idx}`"
                class="tag"
              >
                #{{ tag }}
              </span>
            </div>
          </div>

          <div class="group" v-if="generationArtifacts.keywords.length">
            <strong>Ключевые слова</strong>
            <div class="card-tags">
              <span
                v-for="(word, idx) in generationArtifacts.keywords"
                :key="`kw-${idx}`"
                class="tag"
              >
                {{ word }}
              </span>
            </div>
          </div>

          <div class="group" v-if="generationArtifacts.visual_directions.length">
            <strong>Визуальные направления</strong>
            <span
              v-for="(item, idx) in generationArtifacts.visual_directions"
              :key="`visual-${idx}`"
            >
              • {{ item }}
            </span>
          </div>
        </section>

        <section v-if="generationIngestion" class="control-card">
          <div class="control-card-header">
            <h4>Источник генерации</h4>
          </div>
          <div class="group">
            <span v-for="(value, key) in generationIngestion" :key="`ing-${key}`">
              <strong>{{ key }}:</strong> {{ String(value) }}
            </span>
          </div>
        </section>

        <div v-if="exportJob" class="job-box">
          <p>
            Статус экспорта:
            <StatusBadge :value="exportJob.status" />
          </p>
          <a
            v-if="exportJob.download_url"
            class="btn btn-primary"
            :href="exportJob.download_url"
            target="_blank"
          >
            Скачать ZIP
          </a>
          <p v-if="exportJob.error" class="error-text">{{ exportJob.error }}</p>
        </div>
      </aside>
    </section>
  </main>
</template>

