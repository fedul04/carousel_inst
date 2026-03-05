<script setup lang="ts">
import { makePreviewBody } from "~/utils/preview"

const props = defineProps<{
  item: {
    id: string
    title: string
    status: string
    language: string
    slides_count: number
    created_at: string
    preview: { title: string; body: string } | null
  }
}>()

const createdLabel = computed(() =>
  new Date(props.item.created_at).toLocaleString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }),
)
</script>

<template>
  <article class="carousel-card">
    <div class="preview-card">
      <div class="preview-header">
        <span>@username</span>
        <span>1/{{ item.slides_count }}</span>
      </div>
      <h3>{{ item.preview?.title || item.title }}</h3>
      <p>{{ makePreviewBody(item.preview?.body || "Слайды появятся после генерации.") }}</p>
      <div class="preview-footer">
        <span>Draft AI</span>
        <span>&rarr;</span>
      </div>
    </div>

    <div class="card-body">
      <div class="card-title-row">
        <h4>{{ item.title }}</h4>
        <StatusBadge :value="item.status" />
      </div>
      <p class="card-meta">{{ createdLabel }}</p>
      <div class="card-tags">
        <span class="tag">{{ item.language }}</span>
        <span class="tag">{{ item.slides_count }} слайдов</span>
      </div>
      <NuxtLink :to="`/carousels/${item.id}/editor`" class="btn btn-secondary">Открыть</NuxtLink>
    </div>
  </article>
</template>
