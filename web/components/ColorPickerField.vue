<script setup lang="ts">
const props = defineProps<{
  label: string
  modelValue: string
}>()

const emit = defineEmits<{
  "update:modelValue": [value: string]
}>()

const onColorInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit("update:modelValue", target.value)
}

const onTextInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit("update:modelValue", target.value)
}
</script>

<template>
  <label class="color-field">
    <span>{{ label }}</span>
    <div class="color-field-row">
      <input
        class="color-swatch"
        type="color"
        :value="modelValue"
        @input="onColorInput"
      />
      <input
        class="color-text"
        type="text"
        :value="modelValue"
        @input="onTextInput"
      />
    </div>
  </label>
</template>
