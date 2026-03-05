<script setup lang="ts">
import type { DesignState } from "~/utils/editor"
import type { TypographyTokens } from "~/utils/styleTokens"

const props = defineProps<{
  state: DesignState
  applyToAll: boolean
}>()

const emit = defineEmits<{
  apply: [payload: Record<string, any>]
  cancel: []
  "update:applyToAll": [value: boolean]
}>()

const draftTypography = ref<TypographyTokens>({ ...props.state.styleTokens.body })
const highlightColor = ref(props.state.styleTokens.highlight_color)

watch(
  () => props.state.styleTokens,
  (value) => {
    draftTypography.value = { ...value.body }
    highlightColor.value = value.highlight_color
  },
  { deep: true, immediate: true },
)

const apply = () => {
  emit("apply", {
    style_tokens: {
      body: draftTypography.value,
      highlight_color: highlightColor.value,
    },
  })
}

const cancel = () => {
  draftTypography.value = { ...props.state.styleTokens.body }
  highlightColor.value = props.state.styleTokens.highlight_color
  emit("cancel")
}
</script>

<template>
  <section class="control-card">
    <div class="control-card-header">
      <h4>Текст</h4>
    </div>

    <ColorPickerField label="Цвет выделения" v-model="highlightColor" />
    <TypographyControls v-model="draftTypography" title-label="Текста" />

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
