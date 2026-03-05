<script setup lang="ts">
interface PhotoItem {
  id: string
  url: string
}

defineProps<{
  modelValue: string
  items: PhotoItem[]
  uploading?: boolean
}>()

const emit = defineEmits<{
  "update:modelValue": [value: string]
  upload: [file: File]
}>()

const uploadRef = ref<HTMLInputElement | null>(null)

const chooseFile = () => {
  uploadRef.value?.click()
}

const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    emit("upload", file)
    target.value = ""
  }
}
</script>

<template>
  <div class="photo-strip">
    <p class="photo-strip-label">Выбрать фото</p>
    <div class="photo-strip-list">
      <button type="button" class="photo-item photo-upload" :disabled="uploading" @click="chooseFile">
        <span v-if="uploading">...</span>
        <span v-else>+</span>
      </button>
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="photo-item"
        :class="{ active: modelValue === item.url }"
        @click="emit('update:modelValue', item.url)"
      >
        <img :src="item.url" alt="Фон" />
      </button>
    </div>
    <input
      ref="uploadRef"
      class="hidden-file"
      type="file"
      accept="image/png,image/jpeg,image/webp"
      @change="onFileChange"
    />
  </div>
</template>
