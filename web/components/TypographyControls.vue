<script setup lang="ts">
import type { FontName, TextCase, TypographyTokens } from "~/utils/styleTokens"
import { FONT_LABELS } from "~/utils/styleTokens"

const props = defineProps<{
  modelValue: TypographyTokens
  titleLabel: string
}>()

const emit = defineEmits<{
  "update:modelValue": [value: TypographyTokens]
}>()

const expanded = ref(false)
const fonts = Object.keys(FONT_LABELS) as FontName[]
const caseModes: Array<{ id: TextCase; label: string }> = [
  { id: "upper", label: "AA" },
  { id: "title", label: "Aa" },
  { id: "lower", label: "aa" },
]

const update = (patch: Partial<TypographyTokens>) => {
  emit("update:modelValue", { ...props.modelValue, ...patch })
}
</script>

<template>
  <div class="typography-controls">
    <p class="control-caption">Шрифт {{ titleLabel.toLowerCase() }}</p>
    <div class="font-chips">
      <button
        v-for="font in fonts"
        :key="font"
        type="button"
        class="chip-btn chip-btn-tiny"
        :class="{ active: modelValue.font === font }"
        @click="update({ font })"
      >
        {{ FONT_LABELS[font] }}
      </button>
    </div>

    <label>
      Размер {{ titleLabel.toLowerCase() }}: {{ modelValue.size }}
      <input
        type="range"
        min="16"
        max="140"
        step="1"
        :value="modelValue.size"
        @input="update({ size: Number(($event.target as HTMLInputElement).value) })"
      />
    </label>

    <button type="button" class="details-toggle" @click="expanded = !expanded">
      Больше настроек
      <span>{{ expanded ? "▲" : "▼" }}</span>
    </button>

    <div v-if="expanded" class="advanced-group">
      <label>
        Межстрочный интервал: {{ modelValue.line_height.toFixed(2) }}
        <input
          type="range"
          min="0.7"
          max="2"
          step="0.01"
          :value="modelValue.line_height"
          @input="
            update({ line_height: Number(($event.target as HTMLInputElement).value) })
          "
        />
      </label>
      <label>
        Межбуквенный интервал: {{ modelValue.letter_spacing.toFixed(1) }}
        <input
          type="range"
          min="-2"
          max="12"
          step="0.1"
          :value="modelValue.letter_spacing"
          @input="
            update({ letter_spacing: Number(($event.target as HTMLInputElement).value) })
          "
        />
      </label>
      <div class="case-switch">
        <button
          v-for="item in caseModes"
          :key="item.id"
          type="button"
          class="chip-btn chip-btn-case"
          :class="{ active: modelValue.case === item.id }"
          @click="update({ case: item.id })"
        >
          {{ item.label }}
        </button>
      </div>
      <label>
        Жирность: {{ modelValue.weight }}
        <input
          type="range"
          min="100"
          max="900"
          step="100"
          :value="modelValue.weight"
          @input="update({ weight: Number(($event.target as HTMLInputElement).value) })"
        />
      </label>
    </div>
  </div>
</template>
