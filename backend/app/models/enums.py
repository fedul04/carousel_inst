from enum import StrEnum


class CarouselStatus(StrEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class GenerationStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ExportStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class SourceType(StrEnum):
    TEXT = "text"
    VIDEO = "video"
    LINKS = "links"


class TemplatePreset(StrEnum):
    CLASSIC = "classic"
    BOLD = "bold"
    MINIMAL = "minimal"
    NEON = "neon"
    SOFT = "soft"
    NOIR = "noir"
    AURORA = "aurora"
    SUNSET = "sunset"
    SYNTHWAVE = "synthwave"
    PAPER = "paper"
    MATRIX = "matrix"
    CANDY = "candy"
    LAVA = "lava"
    FROST = "frost"
    MONO = "mono"
    VELVET = "velvet"
    BLUEPRINT = "blueprint"
    HOLOGRAM = "hologram"
    COSMOS = "cosmos"
    EMBER = "ember"
    OASIS = "oasis"
    GRAPHITE = "graphite"
    CITRUS = "citrus"
    VINTAGE = "vintage"


class BgType(StrEnum):
    COLOR = "color"
    IMAGE = "image"
