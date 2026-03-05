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

const draft = ref<TypographyTokens>({ ...props.state.styleTokens.title })

watch(
  () => props.state.styleTokens.title,
  (value) => {
    draft.value = { ...value }
  },
  { deep: true, immediate: true },
)

const apply = () => {
  emit("apply", {
    style_tokens: {
      title: draft.value,
    },
  })
}

const cancel = () => {
  draft.value = { ...props.state.styleTokens.title }
  emit("cancel")
}
</script>

<template>
  <section class="control-card">
    <div class="control-card-header">
      <h4>Заголовок</h4>
    </div>

    <TypographyControls v-model="draft" title-label="Заголовка" />

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
