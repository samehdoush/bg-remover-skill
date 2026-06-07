"""Core rembg processing with session caching for performance."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Callable

from PIL import Image
from rembg import new_session, remove


_session_cache: dict[str, object] = {}


def get_session(model_name: str):
    """Get or create a cached rembg session for a model.

    Reusing sessions avoids reloading model weights on every call (huge speedup).
    """
    if model_name not in _session_cache:
        _session_cache[model_name] = new_session(model_name)
    return _session_cache[model_name]


def process_image(
    input_path: str | Path,
    output_path: str | Path,
    model_name: str = "u2net",
    alpha_matting: bool = False,
    alpha_matting_foreground_threshold: int = 240,
    alpha_matting_background_threshold: int = 10,
    alpha_matting_erode_size: int = 10,
    only_mask: bool = False,
    progress_callback: Callable[[float], None] | None = None,
) -> dict:
    """Process a single image: remove background, save as PNG/WebP.

    Args:
        input_path: Source image file
        output_path: Destination file
        model_name: rembg model to use
        alpha_matting: Enable alpha matting post-processing
        alpha_matting_foreground_threshold: Foreground mask threshold (0-255)
        alpha_matting_background_threshold: Background mask threshold (0-255)
        alpha_matting_erode_size: Erosion size for alpha matting
        only_mask: If True, save only the alpha mask
        progress_callback: Optional progress function (0.0 to 1.0)

    Returns:
        Dict with processing info: input_size, output_size, model, time_seconds
    """
    import time

    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    if progress_callback:
        progress_callback(0.05)

    session = get_session(model_name)

    if progress_callback:
        progress_callback(0.15)

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    if progress_callback:
        progress_callback(0.30)

    output_bytes = remove(
        input_bytes,
        session=session,
        alpha_matting=alpha_matting,
        alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
        alpha_matting_background_threshold=alpha_matting_background_threshold,
        alpha_matting_erode_size=alpha_matting_erode_size,
        only_mask=only_mask,
    )

    if progress_callback:
        progress_callback(0.80)

    with open(output_path, "wb") as f:
        f.write(output_bytes)

    if progress_callback:
        progress_callback(1.0)

    elapsed = time.perf_counter() - start

    in_size = input_path.stat().st_size
    out_size = output_path.stat().st_size
    with Image.open(input_path) as img:
        in_dims = img.size

    return {
        "input": str(input_path),
        "output": str(output_path),
        "model": model_name,
        "alpha_matting": alpha_matting,
        "time_seconds": round(elapsed, 2),
        "input_size_bytes": in_size,
        "output_size_bytes": out_size,
        "input_dimensions": in_dims,
    }


def batch_process(
    input_dir: str | Path,
    output_dir: str | Path,
    model_name: str = "u2net",
    alpha_matting: bool = False,
    only_mask: bool = False,
    recursive: bool = False,
    extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"),
    progress_callback: Callable[[str, float], None] | None = None,
) -> list[dict]:
    """Process all images in a directory.

    Args:
        input_dir: Source directory
        output_dir: Destination directory
        model_name: rembg model to use
        alpha_matting: Enable alpha matting
        only_mask: Save only masks
        recursive: Recurse into subdirectories
        extensions: File extensions to process
        progress_callback: Optional callback(filename, fraction)

    Returns:
        List of result dicts (one per image)
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = "**/*" if recursive else "*"
    files = sorted(
        f
        for f in input_dir.glob(pattern)
        if f.is_file() and f.suffix.lower() in extensions
    )

    if not files:
        return []

    # Pre-warm session to download model once.
    get_session(model_name)

    results = []
    for i, file in enumerate(files):
        rel = file.relative_to(input_dir)
        out_path = output_dir / rel
        out_path = out_path.with_name(out_path.stem + "-no-bg.png")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        def _cb(frac: float, _idx: int = i, _total: int = len(files), _name: str = file.name) -> None:
            if progress_callback:
                progress_callback(_name, (_idx + frac) / _total)

        try:
            info = process_image(
                file,
                out_path,
                model_name=model_name,
                alpha_matting=alpha_matting,
                only_mask=only_mask,
                progress_callback=_cb,
            )
            results.append(info)
        except Exception as e:
            results.append(
                {
                    "input": str(file),
                    "output": None,
                    "error": str(e),
                }
            )

    return results
