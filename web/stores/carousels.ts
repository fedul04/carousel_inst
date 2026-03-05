import { defineStore } from "pinia"

interface Preview {
  title: string
  body: string
}

export interface CarouselListItem {
  id: string
  title: string
  status: string
  language: string
  slides_count: number
  created_at: string
  preview: Preview | null
}

interface ListResponse {
  items: CarouselListItem[]
  total: number
  limit: number
  offset: number
}

export const useCarouselStore = defineStore("carousels", {
  state: () => ({
    items: [] as CarouselListItem[],
    total: 0,
    loading: false,
    error: "" as string,
  }),
  actions: {
    async fetchList(filters: { status?: string; lang?: string } = {}) {
      const api = useApi()
      this.loading = true
      this.error = ""
      try {
        const query = new URLSearchParams()
        if (filters.status) query.set("status", filters.status)
        if (filters.lang) query.set("lang", filters.lang)
        query.set("limit", "30")
        query.set("offset", "0")
        const response = await api.get<ListResponse>(`/carousels?${query.toString()}`)
        this.items = response.items
        this.total = response.total
      } catch (error: any) {
        this.error = error?.data?.detail ?? error?.message ?? "Не удалось загрузить карусели"
      } finally {
        this.loading = false
      }
    },
  },
})

