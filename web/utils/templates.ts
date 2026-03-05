export type TemplatePreset =
  | "classic"
  | "bold"
  | "minimal"
  | "neon"
  | "soft"
  | "noir"
  | "aurora"
  | "sunset"
  | "synthwave"
  | "paper"
  | "matrix"
  | "candy"
  | "lava"
  | "frost"
  | "mono"
  | "velvet"
  | "blueprint"
  | "hologram"
  | "cosmos"
  | "ember"
  | "oasis"
  | "graphite"
  | "citrus"
  | "vintage"

export interface TemplateOption {
  id: TemplatePreset
  label: string
  previewStyle: Record<string, string>
}

export const TEMPLATE_OPTIONS: TemplateOption[] = [
  {
    id: "classic",
    label: "Classic",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.02) 46%, rgba(0,0,0,0.3) 100%), repeating-linear-gradient(0deg, rgba(17,19,25,0.12) 0 1px, transparent 1px 18px), repeating-linear-gradient(90deg, rgba(17,19,25,0.12) 0 1px, transparent 1px 18px), linear-gradient(165deg, #ffe14a 0%, #f6cd22 52%, #efb100 100%)",
      backgroundSize: "auto, auto, auto, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "bold",
    label: "Bold",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(8,10,24,0.28) 100%), radial-gradient(circle at 18% 18%, rgba(255,255,255,0.42) 0 1.4px, transparent 1.8px), radial-gradient(circle at 76% 72%, rgba(255,255,255,0.25) 0 1.1px, transparent 1.6px), linear-gradient(160deg, #3540f0 0%, #4730cb 48%, #23257f 100%)",
      backgroundSize: "auto, 22px 22px, 28px 28px, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "minimal",
    label: "Minimal",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0.22) 100%), repeating-linear-gradient(0deg, rgba(43,48,58,0.1) 0 1px, transparent 1px 26px), linear-gradient(165deg, #f8f4ea 0%, #efe6d6 54%, #e5d7c4 100%)",
      backgroundSize: "auto, auto, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "neon",
    label: "Neon",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.5) 100%), radial-gradient(circle at 26% 26%, rgba(0,255,240,0.64) 0 14%, transparent 40%), radial-gradient(circle at 78% 74%, rgba(255,56,187,0.54) 0 18%, transparent 44%), linear-gradient(155deg, #181b36 0%, #1b1a43 50%, #111321 100%)",
      backgroundSize: "auto, auto, auto, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "soft",
    label: "Soft",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(30,35,44,0.24) 100%), radial-gradient(circle at 82% 18%, rgba(255,255,255,0.55) 0 16%, transparent 44%), radial-gradient(circle at 18% 78%, rgba(255,255,255,0.35) 0 14%, transparent 40%), linear-gradient(165deg, #ffd2df 0%, #ffdbc0 42%, #cfe7ff 100%)",
      backgroundSize: "auto, auto, auto, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "noir",
    label: "Noir",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.24) 100%), repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 34px), linear-gradient(165deg, #1a1d24 0%, #212634 50%, #0e1118 100%)",
      backgroundSize: "auto, auto, auto",
      backgroundPosition: "center",
    },
  },
  {
    id: "aurora",
    label: "Aurora",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 16% 18%, rgba(94,233,255,0.46) 0 18%, transparent 52%), radial-gradient(circle at 84% 74%, rgba(146,119,255,0.38) 0 22%, transparent 58%), linear-gradient(160deg, #0b1b2b 0%, #10293f 48%, #1d3f55 100%)",
    },
  },
  {
    id: "sunset",
    label: "Sunset",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 14% 20%, rgba(255,242,182,0.62) 0 20%, transparent 50%), linear-gradient(160deg, #ffd26a 0%, #ff955f 40%, #ff6f7f 72%, #6f3b9d 100%)",
    },
  },
  {
    id: "synthwave",
    label: "Synthwave",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.5) 100%), linear-gradient(140deg, #2b174f 0%, #1a103f 45%, #0b0f2d 100%)",
    },
  },
  {
    id: "paper",
    label: "Paper",
    previewStyle: {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(50,61,79,0.05) 0 1px, transparent 1px 28px), linear-gradient(165deg, #fdf4e8 0%, #f7eadb 56%, #efe0cc 100%)",
    },
  },
  {
    id: "matrix",
    label: "Matrix",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.75) 100%), linear-gradient(160deg, #0a1f15 0%, #0d2f1f 48%, #15492c 100%)",
    },
  },
  {
    id: "candy",
    label: "Candy",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 18% 16%, rgba(255,255,255,0.52) 0 16%, transparent 48%), radial-gradient(circle at 82% 72%, rgba(255,255,255,0.38) 0 18%, transparent 52%), linear-gradient(150deg, #ff7db7 0%, #ff9d73 38%, #ffd56c 72%, #8bc6ff 100%)",
    },
  },
  {
    id: "lava",
    label: "Lava",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 18% 20%, rgba(255,197,112,0.34) 0 15%, transparent 42%), radial-gradient(circle at 86% 78%, rgba(255,82,82,0.24) 0 18%, transparent 50%), linear-gradient(150deg, #2a1311 0%, #5e1f1a 42%, #b53b24 74%, #f26a2a 100%)",
    },
  },
  {
    id: "frost",
    label: "Frost",
    previewStyle: {
      backgroundImage:
        "linear-gradient(180deg, rgba(255,255,255,0.36) 0%, rgba(255,255,255,0.08) 100%), radial-gradient(circle at 12% 18%, rgba(255,255,255,0.66) 0 18%, transparent 50%), linear-gradient(160deg, #d9f3ff 0%, #c9e8ff 48%, #b1dcff 100%)",
    },
  },
  {
    id: "mono",
    label: "Mono",
    previewStyle: {
      backgroundImage:
        "repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 30px), linear-gradient(165deg, #191a1f 0%, #262833 52%, #111217 100%)",
    },
  },
  {
    id: "velvet",
    label: "Velvet",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 84% 16%, rgba(255,255,255,0.18) 0 16%, transparent 48%), linear-gradient(145deg, #2e1038 0%, #4f1f60 46%, #27102f 100%)",
    },
  },
  {
    id: "blueprint",
    label: "Blueprint",
    previewStyle: {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(209,232,255,0.22) 0 1px, transparent 1px 26px), repeating-linear-gradient(90deg, rgba(209,232,255,0.2) 0 1px, transparent 1px 26px), linear-gradient(165deg, #113463 0%, #1b4a87 52%, #0f2a4f 100%)",
    },
  },
  {
    id: "hologram",
    label: "Hologram",
    previewStyle: {
      backgroundImage:
        "linear-gradient(115deg, rgba(255,255,255,0.18) 0 12%, rgba(255,255,255,0) 12% 100%), linear-gradient(145deg, #6e57ff 0%, #2fd4ff 34%, #6dffb6 62%, #f9ff7a 100%)",
    },
  },
  {
    id: "cosmos",
    label: "Cosmos",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 18% 14%, rgba(121,156,255,0.54) 0 18%, transparent 52%), radial-gradient(circle at 84% 76%, rgba(199,110,255,0.46) 0 20%, transparent 56%), linear-gradient(160deg, #090b1b 0%, #17173a 46%, #0f2c55 100%)",
    },
  },
  {
    id: "ember",
    label: "Ember",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 16% 18%, rgba(255,177,88,0.5) 0 16%, transparent 48%), radial-gradient(circle at 82% 74%, rgba(255,75,75,0.34) 0 20%, transparent 54%), linear-gradient(150deg, #250f0f 0%, #4a1816 48%, #8a2e24 100%)",
    },
  },
  {
    id: "oasis",
    label: "Oasis",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 88% 18%, rgba(255,255,255,0.45) 0 20%, transparent 52%), linear-gradient(160deg, #d8fff7 0%, #bdf3e7 46%, #94decb 100%)",
    },
  },
  {
    id: "graphite",
    label: "Graphite",
    previewStyle: {
      backgroundImage:
        "repeating-linear-gradient(0deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 26px), linear-gradient(165deg, #17191f 0%, #252a36 54%, #0f1116 100%)",
    },
  },
  {
    id: "citrus",
    label: "Citrus",
    previewStyle: {
      backgroundImage:
        "radial-gradient(circle at 14% 22%, rgba(255,255,255,0.56) 0 14%, transparent 44%), linear-gradient(158deg, #f9f871 0%, #d3f45a 44%, #8de86e 100%)",
    },
  },
  {
    id: "vintage",
    label: "Vintage",
    previewStyle: {
      backgroundImage:
        "repeating-linear-gradient(90deg, rgba(58,39,20,0.06) 0 1px, transparent 1px 30px), linear-gradient(165deg, #f4e6cc 0%, #e9d7b7 52%, #d8bf98 100%)",
    },
  },
]

export function isDarkTemplate(template: TemplatePreset): boolean {
  return (
    template === "bold" ||
    template === "neon" ||
    template === "noir" ||
    template === "aurora" ||
    template === "synthwave" ||
    template === "matrix" ||
    template === "lava" ||
    template === "mono" ||
    template === "velvet" ||
    template === "blueprint" ||
    template === "cosmos" ||
    template === "ember" ||
    template === "graphite"
  )
}
