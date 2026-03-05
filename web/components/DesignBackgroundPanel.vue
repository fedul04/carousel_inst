<script setup lang="ts">
import type { DesignState } from "~/utils/editor"
import type { PatternSettings } from "~/utils/styleTokens"

interface PhotoItem {
  id: string
  url: string
}

const props = defineProps<{
  state: DesignState
  applyToAll: boolean
  photos: PhotoItem[]
  lastUploadedId?: string | null
  lastUploadedUrl?: string | null
  uploading?: boolean
}>()

const emit = defineEmits<{
  apply: [payload: Record<string, any>]
  cancel: []
  "update:applyToAll": [value: boolean]
  upload: [file: File]
}>()

const draft = reactive({
  bgType: "color" as "color" | "image",
  bgValue: "#F4F1E9",
  bgOverlay: 0,
  accentColor: "#3B37D2",
  pattern: {
    enabled: false,
    type: "dots",
    opacity: 0.18,
    scale: 1,
  } as PatternSettings,
  dimmingEnabled: false,
  dimmingStrength: 0,
  imageAssetId: null as string | null,
})

const isCustomAsset = (id: string) => !id.startsWith("figma-")

const findPhotoById = (id: string | null | undefined) => {
  if (!id) return null
  return props.photos.find((item) => item.id === id) || null
}

const resolveBackgroundUrl = (imageAssetId: string | null, fallback: string) => {
  const photo = findPhotoById(imageAssetId)
  return photo?.url || fallback
}

const resetDraft = () => {
  draft.bgType = props.state.bgType
  draft.imageAssetId = props.state.styleTokens.background.image_asset_id
  draft.bgValue = resolveBackgroundUrl(draft.imageAssetId, props.state.bgValue)
  draft.bgOverlay = props.state.bgOverlay
  draft.accentColor = props.state.styleTokens.accent_color
  draft.pattern = { ...props.state.styleTokens.background.pattern }
  draft.dimmingEnabled = props.state.styleTokens.background.dimming.enabled
  draft.dimmingStrength = props.state.styleTokens.background.dimming.strength
}

watch(
  () => props.state,
  () => resetDraft(),
  { deep: true, immediate: true },
)

watch(
  () => props.lastUploadedId,
  (id) => {
    if (!id) return
    const photo = findPhotoById(id)
    if (photo) {
      onPhotoSelect(photo.url)
    }
  },
)

watch(
  () => props.lastUploadedUrl,
  (url) => {
    if (!url) return
    onPhotoSelect(url)
  },
)

watch(
  () => props.photos,
  () => {
    if (draft.bgType !== "image") return
    const photo = findPhotoById(draft.imageAssetId)
    if (photo) {
      draft.bgValue = photo.url
    }
  },
  { deep: true },
)

watch(
  () => draft.bgType,
  (next) => {
    if (next === "color") {
      draft.imageAssetId = null
      const value = draft.bgValue.trim()
      const isHexColor = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(value)
      if (!isHexColor) {
        draft.bgValue = "#F4F1E9"
      }
      return
    }
    const current = draft.bgValue.trim().toLowerCase()
    const looksLikeColor = current.startsWith("#") || current.startsWith("rgb")
    if (next === "image" && looksLikeColor && props.photos.length > 0) {
      onPhotoSelect(props.photos[0].url)
    }
  },
)

const onPhotoSelect = (url: string) => {
  draft.bgType = "image"
  const photo = props.photos.find((item) => item.url === url)
  draft.bgValue = photo?.url || url
  draft.imageAssetId = photo && isCustomAsset(photo.id) ? photo.id : null
}

const onBackgroundUrlInput = () => {
  draft.imageAssetId = null
}

const apply = () => {
  const imageAssetId = draft.bgType === "image" ? draft.imageAssetId : null
  emit("apply", {
    bg: {
      type: draft.bgType,
      value: draft.bgValue,
      overlay: draft.bgOverlay,
    },
    style_tokens: {
      accent_color: draft.accentColor,
      background: {
        pattern: draft.pattern,
        dimming: {
          enabled: draft.dimmingEnabled,
          strength: draft.dimmingStrength,
        },
        image_asset_id: imageAssetId,
      },
    },
  })
}

const cancel = () => {
  resetDraft()
  emit("cancel")
}
</script>

<template>
  <section class="control-card">
    <div class="control-card-header">
      <h4>Фон</h4>
    </div>

    <label>
      Тип фона
      <div class="segmented">
        <button
          type="button"
          class="chip-btn"
          :class="{ active: draft.bgType === 'color' }"
          @click="draft.bgType = 'color'"
        >
          Цвет
        </button>
        <button
          type="button"
          class="chip-btn"
          :class="{ active: draft.bgType === 'image' }"
          @click="draft.bgType = 'image'"
        >
          Фото
        </button>
      </div>
    </label>

    <ColorPickerField
      v-if="draft.bgType === 'color'"
      label="Цвет фона"
      v-model="draft.bgValue"
    />
    <ColorPickerField label="Акцентный цвет" v-model="draft.accentColor" />

    <PatternPicker v-if="draft.bgType === 'color'" v-model="draft.pattern" />

    <PhotoStripPicker
      v-if="draft.bgType === 'image'"
      :items="photos"
      :uploading="uploading"
      :model-value="draft.bgValue"
      @update:model-value="onPhotoSelect"
      @upload="emit('upload', $event)"
    />

    <label class="toggle-row">
      <input v-model="draft.dimmingEnabled" type="checkbox" />
      Затемнение
    </label>
    <label>
      Сила затемнения: {{ draft.dimmingStrength.toFixed(2) }}
      <input
        v-model.number="draft.dimmingStrength"
        type="range"
        min="0"
        max="1"
        step="0.01"
        :disabled="!draft.dimmingEnabled"
      />
    </label>

    <label v-if="draft.bgType === 'image'">
      URL фона
      <input v-model="draft.bgValue" type="text" @input="onBackgroundUrlInput" />
    </label>
    <label>
      Прозрачность наложения: {{ draft.bgOverlay.toFixed(2) }}
      <input v-model.number="draft.bgOverlay" type="range" min="0" max="1" step="0.01" />
    </label>

    <label class="toggle-row">
      <input
        :checked="applyToAll"
        type="checkbox"
        @change="emit('update:applyToAll', ($event.target as HTMLInputElement).checked)"
      />
      Применить ко всем слайдам
    </label>

    <div class="actions-row">
      <button type="button" class="btn btn-secondary" @click="cancel">Отмена</button>
      <button type="button" class="btn btn-primary" @click="apply">Применить</button>
    </div>
  </section>
</template>
