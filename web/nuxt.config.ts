export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: false },
  app: {
    head: {
      link: [
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossorigin: "",
        },
        {
          rel: "stylesheet",
          href:
            "https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Fira+Code:wght@400;500;700&family=Inter:wght@400;500;700;800;900&family=Jost:wght@400;500;700;800&family=Roboto+Condensed:wght@400;500;700&family=Source+Sans+3:wght@400;500;700&display=swap",
        },
      ],
    },
  },
  css: ["~/assets/css/main.css"],
  modules: ["@pinia/nuxt"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? "http://localhost:8000/api",
    },
  },
  typescript: {
    strict: true,
    typeCheck: false,
  },
})
