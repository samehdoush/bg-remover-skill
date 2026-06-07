#!/usr/bin/env python3
"""bg-remover — Professional image background removal and replacement CLI.

Powered by rembg (https://github.com/danielgatis/rembg) with 16 AI models.

Usage:
    bg-remover photo.jpg                                  # single file, auto model
    bg-remover -m birefnet-portrait portrait.jpg         # specific model
    bg-remover -b ./photos -o ./transparent               # batch
    bg-remover --bg-color "#FFFFFF" product.jpg           # replace bg with color
    bg-remover --bg-image studio.jpg subject.jpg          # replace bg with image
    bg-remover --alpha-matting portrait.jpg               # best edge quality

Run `bg-remover --help` for the full flag list.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Allow `python3 bg-remover.py` from any CWD.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Lazy imports: only modules that don't need rembg at import time.
from _lib.models import MODELS, get_model_info, list_models  # noqa: E402
from _lib.utils import (  # noqa: E402
    default_output_path,
    format_bytes,
    format_time,
    is_valid_image,
    list_images,
    parse_color,
)


BANNER = r"""
  ____  _                                          _
 | __ )| |__  _ __ ___  _ __ ___  _   _ _ __   __| |___
 |  _ \| '_ \| '__/ _ \| '_ ` _ \| | | | '_ \ / _` / __|
 | |_) | | | | | | (_) | | | | | | |_| | |_) | (_| \__ \
 |____/|_| |_|_|  \___/|_| |_| |_|\__, | .__/ \__,_|___/
                                  |___/|_|
        AI background removal · 16 models · 100% local
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bg-remover",
        description="Remove or replace image backgrounds using AI (powered by rembg).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  bg-remover photo.jpg                              # auto-detect, transparent PNG
  bg-remover -m birefnet-portrait face.jpg          # best for portraits
  bg-remover -m isnet-anime character.png           # best for anime
  bg-remover -b ./photos -o ./out                   # batch process
  bg-remover --bg-color "#FFFFFF" product.jpg       # solid color background
  bg-remover --bg-image studio.jpg subject.jpg      # custom image background
  bg-remover -a -f webp portrait.jpg                # alpha matting + WebP output
  bg-remover --list-models                          # show all available models
""",
    )
    p.add_argument(
        "input",
        nargs="?",
        help="Input image file (or directory with --batch).",
    )
    p.add_argument(
        "-o",
        "--output",
        help="Output file or directory. Defaults: <input-stem>-no-bg.png next to input.",
    )
    p.add_argument(
        "-m",
        "--model",
        default="auto",
        help="AI model to use (default: auto-detect). Use --list-models to see all.",
    )
    p.add_argument(
        "--auto",
        action="store_true",
        help="Auto-select best model based on image content (default behavior).",
    )
    p.add_argument(
        "-a",
        "--alpha-matting",
        action="store_true",
        help="Enable alpha matting for better edges (slower, great for hair/fur).",
    )
    p.add_argument(
        "--bg-color",
        metavar="HEX",
        help="Replace background with a solid color (e.g. #FFFFFF, #00FF00).",
    )
    p.add_argument(
        "--bg-image",
        metavar="PATH",
        help="Replace background with another image.",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=["png", "webp"],
        default="png",
        help="Output format (default: png).",
    )
    p.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Treat input as a directory; process all images in it.",
    )
    p.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="With --batch: recurse into subdirectories.",
    )
    p.add_argument(
        "--only-mask",
        action="store_true",
        help="Save only the alpha mask (grayscale PNG).",
    )
    p.add_argument(
        "--threads",
        type=int,
        default=None,
        help="ONNX runtime thread count (default: CPU count).",
    )
    p.add_argument(
        "--quality",
        type=int,
        default=95,
        help="WebP quality (1-100, default: 95).",
    )
    p.add_argument(
        "--list-models",
        action="store_true",
        help="List all available models and exit.",
    )
    p.add_argument(
        "--install",
        action="store_true",
        help="Run the dependency installer and exit.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-image progress output.",
    )
    return p


def print_banner() -> None:
    if sys.stdout.isatty():
        print(BANNER)


def list_models_pretty() -> None:
    print(f"{'Model':<28} {'Speed':<12} {'Quality':<12} Best for")
    print("-" * 90)
    for name in list_models():
        info = get_model_info(name)
        print(
            f"{name:<28} {info.speed:<12} {info.quality:<12} {info.best_for}"
        )


def ensure_deps() -> None:
    try:
        import rembg  # noqa: F401
    except ImportError:
        print("[bg-remover] rembg not installed. Running installer...")
        installer = _HERE / "install.py"
        if not installer.exists():
            print(
                "[ERROR] install.py not found next to bg-remover.py. "
                "Run: pip install \"rembg[cpu]\" pillow",
                file=sys.stderr,
            )
            sys.exit(1)
        rc = subprocess_install(installer)
        if rc != 0:
            print("[ERROR] Dependency installation failed.", file=sys.stderr)
            sys.exit(1)


_heavy_loaded = False


def load_heavy_deps():
    """Lazy-load modules that depend on rembg (only when actually processing)."""
    global _heavy_loaded
    if _heavy_loaded:
        return
    global process_image, batch_process
    global apply_color_background, apply_image_background
    global suggest_model
    from _lib.processor import batch_process, process_image
    from _lib.background import apply_color_background, apply_image_background
    from _lib.models import suggest_model
    _heavy_loaded = True


def subprocess_install(script: Path) -> int:
    import subprocess
    return subprocess.run([sys.executable, str(script)], check=False).returncode


def resolve_model(args_model: str, image_path: str | None) -> str:
    """Resolve which model to use, applying auto-detection if needed."""
    if args_model and args_model != "auto":
        if args_model not in MODELS:
            print(
                f"[ERROR] Unknown model '{args_model}'.",
                file=sys.stderr,
            )
            print(f"Run with --list-models to see all {len(MODELS)} available models.", file=sys.stderr)
            sys.exit(2)
        return args_model
    if image_path is None:
        return "u2net"
    if not is_valid_image(image_path):
        return "u2net"
    suggested = suggest_model(image_path)
    return suggested


def print_progress(label: str, frac: float) -> None:
    bar_w = 30
    filled = int(bar_w * frac)
    bar = "█" * filled + "░" * (bar_w - filled)
    sys.stdout.write(f"\r  [{bar}] {int(frac * 100):3d}%  {label:<40}")
    sys.stdout.flush()
    if frac >= 1.0:
        sys.stdout.write("\n")
        sys.stdout.flush()


def process_single(args) -> int:
    load_heavy_deps()
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 1
    if not is_valid_image(input_path):
        print(f"[ERROR] Not a valid image: {input_path}", file=sys.stderr)
        return 1

    model = resolve_model(args.model, str(input_path))
    if not args.quiet:
        print(f"  Model:      {model} ({get_model_info(model).best_for})")
        print(f"  Input:      {input_path}  ({format_bytes(input_path.stat().st_size)})")
        if args.alpha_matting:
            print("  Alpha mat:  enabled (best edge quality)")

    # Stage 1: background removal
    tmp_no_bg = _HERE / f".__tmp_{input_path.stem}.png"
    try:
        info = process_image(
            input_path,
            tmp_no_bg,
            model_name=model,
            alpha_matting=args.alpha_matting,
            only_mask=args.only_mask,
        )
    except Exception as e:
        print(f"[ERROR] Failed to process image: {e}", file=sys.stderr)
        return 1

    # Stage 2: optional background replacement
    if args.bg_color or args.bg_image:
        if args.only_mask:
            print(
                "[WARN] --only-mask ignores --bg-color/--bg-image.",
                file=sys.stderr,
            )
        else:
            try:
                final_path = _resolve_final_path(args, input_path)
                if args.bg_color:
                    color = parse_color(args.bg_color)
                    apply_color_background(tmp_no_bg, final_path, color)
                else:
                    bg = Path(args.bg_image)
                    if not bg.is_file():
                        print(f"[ERROR] Background image not found: {bg}", file=sys.stderr)
                        return 1
                    apply_image_background(tmp_no_bg, bg, final_path)
            except Exception as e:
                print(f"[ERROR] Background replacement failed: {e}", file=sys.stderr)
                return 1
            try:
                tmp_no_bg.unlink()
            except OSError:
                pass
    else:
        # No bg replacement — move/convert the transparent PNG to final path.
        from PIL import Image
        final_path = _resolve_final_path(args, input_path)
        with Image.open(tmp_no_bg) as img:
            from _lib.utils import save_image
            final_path = Path(
                save_image(img, final_path, format=args.format, quality=args.quality)
            )
        try:
            tmp_no_bg.unlink()
        except OSError:
            pass

    # Summary
    out_size = final_path.stat().st_size
    if not args.quiet:
        print(f"  Output:     {final_path}  ({format_bytes(out_size)})")
        print(f"  Time:       {format_time(info['time_seconds'])}")

    print(f"\n[OK] Saved: {final_path}")
    return 0


def _resolve_final_path(args, input_path: Path) -> Path:
    if args.output:
        out = Path(args.output)
        if out.is_dir() or (not out.suffix and not out.exists()):
            out.mkdir(parents=True, exist_ok=True)
            return out / f"{input_path.stem}-no-bg.{args.format}"
        out.parent.mkdir(parents=True, exist_ok=True)
        # Force output extension to match format.
        return out.with_suffix(f".{args.format}")
    return default_output_path(input_path).with_suffix(f".{args.format}")


def process_batch(args) -> int:
    load_heavy_deps()
    input_dir = Path(args.input)
    if not input_dir.is_dir():
        print(f"[ERROR] Not a directory: {input_dir}", file=sys.stderr)
        return 1

    # Pick a model ONCE for the batch (use first image for auto-detect).
    candidates = list_images(input_dir, recursive=args.recursive)
    if not candidates:
        print(f"[ERROR] No images found in {input_dir}", file=sys.stderr)
        return 1

    model = resolve_model(args.model, str(candidates[0]))
    if not args.quiet:
        print(f"  Found:      {len(candidates)} images")
        print(f"  Model:      {model} ({get_model_info(model).best_for})")
        print(f"  Input dir:  {input_dir}")

    if args.output:
        out_dir = Path(args.output)
    else:
        out_dir = input_dir / f"{input_dir.name}-no-bg"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.threads:
        os.environ.setdefault("OMP_NUM_THREADS", str(args.threads))

    def cb(name: str, frac: float) -> None:
        if not args.quiet:
            print_progress(name, frac)

    t0 = time.perf_counter()
    results = batch_process(
        input_dir,
        out_dir,
        model_name=model,
        alpha_matting=args.alpha_matting,
        only_mask=args.only_mask,
        recursive=args.recursive,
        progress_callback=cb,
    )
    total = time.perf_counter() - t0

    success = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    print()
    print(f"[DONE] {len(success)}/{len(results)} processed in {format_time(total)}")
    print(f"  Output: {out_dir}")
    if failed:
        print(f"  Failures: {len(failed)}")
        for r in failed[:5]:
            print(f"    - {r['input']}: {r['error']}")
        if len(failed) > 5:
            print(f"    ... and {len(failed) - 5} more")
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_models:
        list_models_pretty()
        return 0

    if args.install:
        rc = subprocess_install(_HERE / "install.py")
        return rc

    if not args.input:
        parser.print_help()
        return 1

    print_banner()
    ensure_deps()

    if args.threads:
        os.environ["OMP_NUM_THREADS"] = str(args.threads)

    if args.batch:
        return process_batch(args)
    return process_single(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[ABORT] Interrupted by user", file=sys.stderr)
        sys.exit(130)
