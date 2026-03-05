<script setup lang="ts">
const store = useCarouselStore()

const statusFilter = ref("")
const langFilter = ref("")

const load = async () => {
  await store.fetchList({
    status: statusFilter.value || undefined,
    lang: langFilter.value || undefined,
  })
}

onMounted(load)
</script>

<template>
  <main class="page-shell page-shell-light">
    <header class="page-header">
      <div>
        <p class="eyebrow">Мои карусели</p>
        <h1>Генерация + Редактор</h1>
      </div>
      <NuxtLink to="/carousels/new" class="btn btn-primary">Создать карусель</NuxtLink>
    </header>

    <section class="toolbar toolbar-light">
      <label>
        Статус
        <select v-model="statusFilter">
          <option value="">Все</option>
          <option value="draft">Черновик</option>
          <option value="generating">Генерация</option>
          <option value="ready">Готово</option>
          <option value="failed">Ошибка</option>
        </select>
      </label>
      <label>
        Язык
        <select v-model="langFilter">
          <option value="">Все</option>
          <option value="RU">RU</option>
          <option value="EN">EN</option>
          <option value="FR">FR</option>
        </select>
      </label>
      <button class="btn btn-secondary" :disabled="store.loading" @click="load">Применить</button>
    </section>

    <p v-if="store.error" class="error-text">{{ store.error }}</p>
    <p v-if="store.loading">Загрузка каруселей...</p>

    <section v-if="!store.loading" class="cards-grid">
      <CarouselCard v-for="item in store.items" :key="item.id" :item="item" />
    </section>
  </main>
</template>
