type RequestOptions = Omit<Parameters<typeof $fetch>[1], "baseURL">

export function useApi() {
  const config = useRuntimeConfig()

  const request = async <T>(url: string, options?: RequestOptions): Promise<T> => {
    return await $fetch<T>(url, {
      baseURL: config.public.apiBase,
      ...options,
    })
  }

  return {
    get: <T>(url: string, options?: RequestOptions) =>
      request<T>(url, { method: "GET", ...options }),
    post: <T>(url: string, body?: unknown, options?: RequestOptions) =>
      request<T>(url, { method: "POST", body, ...options }),
    patch: <T>(url: string, body?: unknown, options?: RequestOptions) =>
      request<T>(url, { method: "PATCH", body, ...options }),
  }
}

