"""Background replacement: solid color or another image."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def apply_color_background(
    input_path: str | Path,
    output_path: str | Path,
    color: tuple[int, int, int, int],
) -> str:
    """Composite a transparent PNG over a solid color background.

    Args:
        input_path: Transparent PNG (RGBA)
        output_path: Destination file
        color: RGBA tuple, e.g. (255, 255, 255, 255) for white

    Returns:
        Output path
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as fg:
        fg = fg.convert("RGBA")
        bg = Image.new("RGBA", fg.size, color)
        bg.alpha_composite(fg)
        # Drop alpha if no transparency remains (saves space).
        out = bg.convert("RGB") if color[3] == 255 else bg
        out.save(output_path, format="PNG", optimize=True)
    return str(output_path)


def apply_image_background(
    foreground_path: str | Path,
    background_path: str | Path,
    output_path: str | Path,
    fit: str = "cover",
) -> str:
    """Composite a transparent PNG over a background image.

    Args:
        foreground_path: Transparent PNG (RGBA)
        background_path: Source background image (any size)
        output_path: Destination file
        fit: How to fit the bg image: "cover" (crop to fg size) or "stretch"

    Returns:
        Output path
    """
    foreground_path = Path(foreground_path)
    background_path = Path(background_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(foreground_path) as fg, Image.open(background_path) as bg_src:
        fg = fg.convert("RGBA")
        target_size = fg.size

        if fit == "cover":
            bg = _cover_crop(bg_src.convert("RGBA"), target_size)
        elif fit == "stretch":
            bg = bg_src.convert("RGBA").resize(target_size, Image.LANCZOS)
        elif fit == "contain":
            bg = _contain_fit(bg_src.convert("RGBA"), target_size)
        else:
            raise ValueError(f"fit must be 'cover', 'stretch', or 'contain', got {fit!r}")

        bg.alpha_composite(fg)
        out = bg.convert("RGB")
        out.save(output_path, format="PNG", optimize=True)
    return str(output_path)


def _cover_crop(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Resize and center-crop to exactly fill target_size."""
    target_w, target_h = target_size
    target_ratio = target_w / target_h
    src_w, src_h = img.size
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Source is wider → scale to height, crop sides.
        new_h = target_h
        new_w = int(src_w * (target_h / src_h))
    else:
        # Source is taller → scale to width, crop top/bottom.
        new_w = target_w
        new_h = int(src_h * (target_w / src_w))

    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _contain_fit(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Resize to fit inside target_size, pad with transparent."""
    target_w, target_h = target_size
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas
