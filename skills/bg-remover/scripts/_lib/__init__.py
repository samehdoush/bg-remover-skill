"""Internal library for bg-remover skill.

Modules (all importable independently):
    models:     Model catalog and auto-selection heuristics (no rembg needed)
    processor:  Core rembg wrapper with session caching (needs rembg)
    background: Background replacement (color + image, no rembg)
    utils:      Image I/O, format conversion, validation (no rembg)
"""

__all__ = [
    "models",
    "processor",
    "background",
    "utils",
]
