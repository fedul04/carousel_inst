<script setup lang="ts">
interface CreateResponse {
  id: string
  title: string
  status: string
}

interface GenerationResponse {
  id: string
  status: string
  estimated_tokens: number
  error: string | null
}

const api = useApi()
const router = useRouter()

const sourceType = ref<"text" | "video" | "links">("text")
const sourceLabels: Record<"text" | "video" | "links", string> = {
  text: "Текст",
  video: "Видео",
  links: "Ссылки",
}
const title = ref("")
const sourceText = ref("")
const videoUrl = ref("")
const linksText = ref("")
const notes = ref("")
const slidesCount = ref(8)
const language = ref<"RU" | "EN" | "FR">("RU")
const styleSample = ref("")

const creating = ref(false)
const createdCarouselId = ref("")
const generationJob = ref<GenerationResponse | null>(null)
const generationPolling = ref<number | null>(null)
const errorText = ref("")

const sourcePayload = computed(() => {
  if (sourceType.value === "text") {
    return { text: sourceText.value }
  }
  if (sourceType.value === "video") {
    return { video_url: videoUrl.value, notes: notes.value }
  }
  return {
    links: linksText.value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean),
    notes: notes.value,
  }
})

const createCarousel = async () => {
  creating.value = true
  errorText.value = ""
  try {
    const response = await api.post<CreateResponse>("/carousels", {
      title: title.value,
      source_type: sourceType.value,
      source_payload: sourcePayload.value,
      format: {
        slides_count: slidesCount.value,
        language: language.value,
        style_sample_text: styleSample.value,
      },
    })
    createdCarouselId.value = response.id
  } catch (error: any) {
    errorText.value = error?.data?.detail ?? error?.message ?? "Не удалось создать карусель"
  } finally {
    creating.value = false
  }
}

const stopPolling = () => {
  if (generationPolling.value) {
    clearInterval(generationPolling.value)
    generationPolling.value = null
  }
}

const pollGeneration = (jobId: string) => {
  stopPolling()
  generationPolling.value = window.setInterval(async () => {
    const job = await api.get<GenerationResponse>(`/generations/${jobId}`)
    generationJob.value = job
    if (job.status === "done") {
      stopPolling()
      await router.push(`/carousels/${createdCarouselId.value}/editor`)
    }
    if (job.status === "failed") {
      stopPolling()
      errorText.value = job.error || "Генерация завершилась ошибкой"
    }
  }, 2000)
}

const runGeneration = async () => {
  if (!createdCarouselId.value) return
  errorText.value = ""
  try {
    const job = await api.post<GenerationResponse>("/generations", {
      carousel_id: createdCarouselId.value,
    })
    generationJob.value = job
    pollGeneration(job.id)
  } catch (error: any) {
    errorText.value =
      error?.data?.detail ?? error?.message ?? "Не удалось запустить генерацию"
  }
}

onBeforeUnmount(stopPolling)
</script>

<template>
  <main class="page-shell page-two-col page-shell-light">
    <section class="panel panel-light">
      <p class="eyebrow">Шаг 1</p>
      <h1>Создать карусель</h1>

      <div class="source-switch">
        <button
          v-for="kind in ['text', 'video', 'links']"
          :key="kind"
          class="chip-btn"
          :class="{ active: sourceType === kind }"
          @click="sourceType = kind as 'text' | 'video' | 'links'"
        >
          {{ sourceLabels[kind as 'text' | 'video' | 'links'] }}
        </button>
      </div>

      <label>
        Заголовок
        <input v-model="title" type="text" placeholder="Название карусели" />
      </label>

      <label v-if="sourceType === 'text'">
        Исходный текст
        <textarea
          v-model="sourceText"
          rows="6"
          placeholder="Вставьте текст поста или черновик"
        />
      </label>

      <template v-else-if="sourceType === 'video'">
        <label>
          Ссылка на видео
          <input v-model="videoUrl" type="text" placeholder="https://..." />
        </label>
        <p class="muted">
          Для YouTube автоматически извлекаются субтитры (если доступны).
        </p>
        <label>
          Заметки
          <textarea v-model="notes" rows="4" placeholder="Дополнительные заметки" />
        </label>
      </template>

      <template v-else>
        <label>
          Ссылки (по одной в строке)
          <textarea v-model="linksText" rows="5" placeholder="https://..." />
        </label>
        <p class="muted">
          По ссылкам автоматически извлекается текст страниц для генерации.
        </p>
        <label>
          Заметки
          <textarea v-model="notes" rows="4" placeholder="Список тезисов" />
        </label>
      </template>

      <p class="eyebrow">Шаг 2</p>
      <div class="format-grid">
        <label>
          Количество слайдов
          <input v-model.number="slidesCount" type="range" min="6" max="10" />
          <span>{{ slidesCount }}</span>
        </label>
        <label>
          Язык
          <select v-model="language">
            <option value="RU">RU</option>
            <option value="EN">EN</option>
            <option value="FR">FR</option>
          </select>
        </label>
      </div>

      <label>
        Пример стиля текста
        <textarea v-model="styleSample" rows="5" placeholder="Вставьте пример тона и стиля" />
      </label>

      <div class="actions-row">
        <button class="btn btn-primary" :disabled="creating || !title" @click="createCarousel">
          {{ creating ? "Создание..." : "Создать черновик" }}
        </button>
        <button
          class="btn btn-secondary"
          :disabled="!createdCarouselId"
          @click="router.push(`/carousels/${createdCarouselId}/editor`)"
        >
          Открыть редактор
        </button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
    </section>

    <section class="panel panel-light panel-ghost-light">
      <p class="eyebrow">Шаг 3</p>
      <h2>Генерация</h2>
      <p class="muted">
        После создания черновика запустите генерацию. Интерфейс остаётся активным во время polling.
      </p>
      <button class="btn btn-primary" :disabled="!createdCarouselId" @click="runGeneration">
        Сгенерировать
      </button>
      <div v-if="generationJob" class="job-box">
        <p>Оценка токенов: {{ generationJob.estimated_tokens }}</p>
        <p>
          Статус:
          <StatusBadge :value="generationJob.status" />
        </p>
      </div>
    </section>
  </main>
</template>
