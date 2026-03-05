# Carousel MVP (FastAPI + Nuxt)

MVP для тестового задания: создание карусели из исходных данных, настройка формата, асинхронная LLM-генерация, редактирование слайдов/дизайна, экспорт ZIP PNG `1080x1350`.

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2
- DB: PostgreSQL
- Storage: MinIO (S3-compatible)
- Frontend: Nuxt 3 (Vue 3 + Pinia)
- Export: Playwright (server-side screenshot) + ZIP

## Run (Docker Compose)
1. Скопировать `.env.example` в `.env` и при необходимости заполнить `LLM_API_KEY`.
2. Запустить:
```bash
docker compose up --build
```
3. URLs:
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- MinIO console: `http://localhost:9001`
- For export links from API: keep `S3_PUBLIC_ENDPOINT_URL=http://localhost:9000` in `.env`.
- For export of local static backgrounds (e.g. `/figma_refs/...`), keep `FRONTEND_ASSET_BASE_URL=http://web:3000` in `.env`.

## API examples (curl)
Создать черновик:
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

Запустить генерацию:
```bash
curl -X POST http://localhost:8000/api/generations \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"<CAROUSEL_ID>"}'
```

Проверить генерацию:
```bash
curl http://localhost:8000/api/generations/<GENERATION_ID>
```

Обновить дизайн:
```bash
curl -X PATCH http://localhost:8000/api/carousels/<CAROUSEL_ID>/design \
  -H "Content-Type: application/json" \
  -d '{
    "template":"bold",
    "bg":{"type":"color","value":"#3B37D2","overlay":0.15},
    "layout":{"padding":48,"align_x":"left","align_y":"top"},
    "header":{"show":true,"text":"@username"},
    "footer":{"show":true,"text":"Draft AI"},
    "apply_to_all":true
  }'
```

Запустить экспорт:
```bash
curl -X POST http://localhost:8000/api/exports \
  -H "Content-Type: application/json" \
  -d '{"carousel_id":"<CAROUSEL_ID>","format":"png"}'
```

Проверить экспорт:
```bash
curl http://localhost:8000/api/exports/<EXPORT_ID>
```

Загрузка ассета (фон):
```bash
curl -X POST http://localhost:8000/api/assets/upload \
  -F "file=@./local-image.png"
```

## Frontend routes
- `/carousels` — список каруселей
- `/carousels/new` — создание + запуск генерации
- `/carousels/[id]/editor` — редактор слайдов/дизайна + экспорт

## Tests
Backend:
```bash
cd backend
python -m pytest -q
```

Frontend:
```bash
cd web
npm i
npm run test
```

E2E (при поднятом стеке):
```bash
cd web
E2E_RUN=1 npm run test:e2e
```

## What is simplified
- `FR` поддержан в API/UI как best-effort (контент зависит от модели).
- При отсутствии `LLM_API_KEY` используется mock-генерация (флоу и статусы сохраняются).
- `BackgroundTasks` реализованы; дополнительный `worker` в compose опционально добирает queued-job.
- Visual fidelity к Figma сделан по доступным экспортам/ассетам (`from_figma`, `Shablon.fig`) и MCP-метаданным, не pixel-perfect на всех экранах.
- SSE/WebSocket статусов не включены (polling).

## Repo structure
```text
backend/
  app/
  alembic/
web/
docker-compose.yml
.env.example
```
