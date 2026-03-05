<script setup lang="ts">
import type { PatternSettings, PatternType } from "~/utils/styleTokens"

const props = defineProps<{
  modelValue: PatternSettings
}>()

const emit = defineEmits<{
  "update:modelValue": [value: PatternSettings]
}>()

const patternTypes: PatternType[] = [
  "dots",
  "texture2",
  "squares",
  "lines",
  "grid",
  "bubbles",
]

const labels: Record<PatternType, string> = {
  dots: "Точки",
  texture2: "Текстура 2",
  squares: "Квадраты",
  lines: "Линии",
  grid: "Сетка",
  bubbles: "Пузыри",
}

const update = (patch: Partial<PatternSettings>) => {
  emit("update:modelValue", { ...props.modelValue, ...patch })
}
</script>

<template>
  <div class="pattern-picker">
    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="modelValue.enabled"
        @change="update({ enabled: ($event.target as HTMLInputElement).checked })"
      />
      Узор
    </label>

    <div class="pattern-types">
      <button
        v-for="kind in patternTypes"
        :key="kind"
        type="button"
        class="chip-btn"
        :class="{ active: modelValue.type === kind }"
        :disabled="!modelValue.enabled"
        @click="update({ type: kind })"
      >
        {{ labels[kind] }}
      </button>
    </div>

    <label>
      Прозрачность: {{ modelValue.opacity.toFixed(2) }}
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        :disabled="!modelValue.enabled"
        :value="modelValue.opacity"
        @input="update({ opacity: Number(($event.target as HTMLInputElement).value) })"
      />
    </label>
    <label>
      Масштаб: {{ modelValue.scale.toFixed(2) }}
      <input
        type="range"
        min="0.4"
        max="2.5"
        step="0.05"
        :disabled="!modelValue.enabled"
        :value="modelValue.scale"
        @input="update({ scale: Number(($event.target as HTMLInputElement).value) })"
      />
    </label>
  </div>
</template>
