"""Image I/O, format conversion, and utility functions."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

SUPPORTED_INPUT_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
SUPPORTED_OUTPUT_FORMATS = {"png", "webp"}


def is_valid_image(path: str | Path) -> bool:
    p = Path(path)
    if not p.is_file():
        return False
    if p.suffix.lower() not in SUPPORTED_INPUT_FORMATS:
        return False
    try:
        with Image.open(p) as img:
            img.verify()
        return True
    except Exception:
        return False


def load_image(path: str | Path) -> Image.Image:
    return Image.open(path)


def save_image(
    img: Image.Image,
    output_path: str | Path,
    format: str = "png",
    quality: int = 95,
) -> str:
    """Save PIL image to path with format conversion."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower()
    if fmt not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(f"Unsupported output format: {format}. Use png or webp.")

    # Adjust suffix if user gave a different one.
    if output_path.suffix.lower() not in (f".{fmt}",):
        output_path = output_path.with_suffix(f".{fmt}")

    if fmt == "png":
        img.save(output_path, format="PNG", optimize=True)
    elif fmt == "webp":
        # For WebP, drop alpha if image is RGB only.
        save_img = img
        if img.mode == "RGBA":
            # Preserve transparency in WebP.
            save_img = img
        save_img.save(
            output_path,
            format="WEBP",
            quality=quality,
            method=6,
        )
    return str(output_path)


def parse_color(color: str) -> tuple[int, int, int, int]:
    """Parse a hex color string to RGBA tuple.

    Accepts: #FFF, #FFFF, #FFFFFF, #FFFFFFFF, FFF, FFFFFF
    """
    if not isinstance(color, str):
        raise TypeError(f"color must be a string, got {type(color).__name__}")
    s = color.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]+", s):
        raise ValueError(f"Invalid color '{color}'. Use hex like #FF0000.")

    s_len = len(s)
    if s_len == 3:
        r, g, b = (int(c * 2, 16) for c in s)
        a = 255
    elif s_len == 4:
        r, g, b, a = (int(c * 2, 16) for c in s)
    elif s_len == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        a = 255
    elif s_len == 8:
        r, g, b, a = (
            int(s[0:2], 16),
            int(s[2:4], 16),
            int(s[4:6], 16),
            int(s[6:8], 16),
        )
    else:
        raise ValueError(f"Invalid color length {s_len} for '{color}'.")
    return (r, g, b, a)


def list_images(
    directory: str | Path,
    recursive: bool = False,
    extensions: tuple[str, ...] = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif",
    ),
) -> list[Path]:
    d = Path(directory)
    if not d.is_dir():
        raise NotADirectoryError(f"Not a directory: {d}")
    pattern = "**/*" if recursive else "*"
    return sorted(
        f for f in d.glob(pattern) if f.is_file() and f.suffix.lower() in extensions
    )


def format_time(seconds: float) -> str:
    """Format a duration in human-readable form."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {int(secs)}s"


def format_bytes(n: int) -> str:
    """Format byte count for human display."""
    f = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if f < 1024:
            return f"{f:.1f}{unit}"
        f /= 1024
    return f"{f:.1f}TB"


def default_output_path(input_path: str | Path, suffix: str = "-no-bg") -> Path:
    """Generate default output path next to the input file."""
    p = Path(input_path)
    return p.with_name(f"{p.stem}{suffix}.png")
