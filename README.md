# Carousel MVP (FastAPI + Nuxt)

MVP по ТЗ: создание карусели из источника (`text`/`video`/`links`), настройка формата, асинхронная генерация слайдов, редактирование дизайна и текста, экспорт ZIP с PNG `1080x1350`.

## Что прислать
- GitHub репозиторий с кодом и этим README.
- Для проверки достаточно поднять проект через Docker и пройти flow:
  `create -> generate -> edit -> export`.

## Как запустить
1. Скопировать `.env.example` в `.env`.
2. Заполнить LLM-настройки (например OpenRouter):
   - `LLM_BASE_URL`
   - `LLM_API_KEY`
   - `LLM_MODEL`
3. Запустить стек:
```bash
docker compose up --build -d
```
4. Открыть сервисы:
   - Frontend: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`
   - MinIO console: `http://localhost:9001`
5. Для корректных ссылок на экспорт проверить в `.env`:
   - `S3_PUBLIC_ENDPOINT_URL=http://localhost:9000`
   - `FRONTEND_ASSET_BASE_URL=http://web:3000`

## Примеры запросов (curl)
Проверка здоровья:
```bash
curl http://localhost:8000/health
```

Создание черновика:
```bash
curl -X POST http://localhost:8000/api/carousels \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Рост продукта Q2",
    "source_type":"text",
    "source_payload":{"text":"Текст поста или заметки..."},
    "format":{"slides_count":8,"language":"RU","style_sample_text":"Тон уверенный, короткие фразы"}
  }'
```

Запуск генерации:
```bash
curl -X POST http://localhost:8000/api/generations \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"<CAROUSEL_ID>"}'
```

Проверка статуса генерации:
```bash
curl http://localhost:8000/api/generations/<GENERATION_ID>
```

Список слайдов:
```bash
curl http://localhost:8000/api/carousels/<CAROUSEL_ID>/slides
```

Редактирование текста слайда:
```bash
curl -X PATCH http://localhost:8000/api/carousels/<CAROUSEL_ID>/slides/<SLIDE_ID> \
  -H "Content-Type: application/json" \
  -d '{"title":"Новый заголовок","body":"Обновленный текст"}'
```

Загрузка изображения для фона:
```bash
curl -X POST http://localhost:8000/api/assets/upload \
  -F "file=@./local-image.png"
```

Обновление дизайна:
```bash
curl -X PATCH http://localhost:8000/api/carousels/<CAROUSEL_ID>/design \
  -H "Content-Type: application/json" \
  -d '{
    "template":"bold",
    "bg":{"type":"color","value":"#3B37D2","overlay":0.15},
    "layout":{"padding":48,"align_x":"left","align_y":"top"},
    "header":{"show":true,"text":"@username"},
    "footer":{"show":true,"text":"Draft AI"},
    "style_tokens":{"accent_color":"#3B37D2"},
    "apply_to_all":true
  }'
```

Запуск экспорта:
```bash
curl -X POST http://localhost:8000/api/exports \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"<CAROUSEL_ID>","format":"png"}'
```

Проверка статуса экспорта:
```bash
curl http://localhost:8000/api/exports/<EXPORT_ID>
```

Скачивание ZIP:
```bash
curl -L "http://localhost:8000/api/exports/<EXPORT_ID>/download" -o export.zip
```

## Что упрощено и почему
- FR язык реализован как best-effort:
  модель может генерировать FR, но без отдельной тонкой оптимизации промптов для FR в MVP.
- Статусы generation/export через polling, без SSE/WebSocket:
  уменьшает сложность first pass и ускоряет реализацию end-to-end.
- Нет auth/billing/roles:
  для тестового приоритет — продуктовый флоу создания и экспорта карусели.
- Асинхронность реализована через `BackgroundTasks` + таблицы job-статусов:
  достаточно для MVP и просто разворачивается в Docker.
- При пустом `LLM_API_KEY` используется mock-генерация:
  позволяет проверить весь интерфейс и экспорт даже без внешнего LLM.
