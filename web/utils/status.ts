export function statusLabel(status: string): string {
  switch (status) {
    case "draft":
      return "Черновик"
    case "generating":
      return "Генерация"
    case "ready":
      return "Готово"
    case "failed":
      return "Ошибка"
    case "queued":
      return "В очереди"
    case "running":
      return "В работе"
    case "done":
      return "Завершено"
    default:
      return status
  }
}

export function statusClass(status: string): string {
  switch (status) {
    case "ready":
    case "done":
      return "status-success"
    case "failed":
      return "status-error"
    case "generating":
    case "queued":
    case "running":
      return "status-info"
    default:
      return "status-neutral"
  }
}
