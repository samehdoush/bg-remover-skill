#!/usr/bin/env python3
"""Auto-install rembg and dependencies for the bg-remover skill.

This script is idempotent: running it multiple times is safe. It will:
1. Detect the Python version (3.11, 3.12, 3.13 required)
2. Check if `rembg` is already importable
3. If not, install `rembg[cpu]` via pip
4. Verify the install and report status

Usage:
    python3 install.py
    python3 install.py --gpu    # install with CUDA GPU support
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import NoReturn


MIN_PY = (3, 11)
MAX_PY_EXCLUSIVE = (3, 15)


def die(msg: str, code: int = 1) -> NoReturn:
    print(f"\n[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def check_python_version() -> None:
    v = sys.version_info
    if v < MIN_PY:
        die(
            f"Python {v.major}.{v.minor} is too old. "
            f"Requires Python {MIN_PY[0]}.{MIN_PY[1]}+."
        )
    if v >= MAX_PY_EXCLUSIVE:
        die(
            f"Python {v.major}.{v.minor} is too new. "
            f"Maximum supported is Python {MAX_PY_EXCLUSIVE[0]}.{MAX_PY_EXCLUSIVE[1] - 1}."
            f" Note: rembg officially supports 3.11-3.13 but may work on newer versions."
        )
    ok(f"Python {v.major}.{v.minor}.{v.micro} detected")


def pip_command() -> list[str]:
    """Return a base pip command (use `python3 -m pip` for portability)."""
    return [sys.executable, "-m", "pip"]


def is_rembg_installed() -> bool:
    try:
        import rembg  # noqa: F401
        return True
    except ImportError:
        return False


def get_installed_rembg_version() -> str | None:
    try:
        import rembg
        return getattr(rembg, "__version__", "unknown")
    except ImportError:
        return None


def ensure_pip() -> None:
    """Bootstrap pip if missing."""
    try:
        subprocess.run(
            pip_command() + ["--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        info("pip not found, attempting bootstrap...")
        subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            check=False,
        )


def install_rembg(gpu: bool = False) -> None:
    extra = "gpu" if gpu else "cpu"
    spec = f"rembg[{extra}]"
    info(f"Installing {spec} (this may take a minute)...")
    cmd = pip_command() + ["install", "--upgrade", spec]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        die(
            f"Failed to install {spec}. "
            f"Try running manually: {' '.join(cmd)}\n"
            f"Underlying error: {e}"
        )


def main() -> int:
    gpu = "--gpu" in sys.argv
    print("=" * 60)
    print(" bg-remover skill — dependency installer")
    print("=" * 60)

    check_python_version()
    ensure_pip()

    if is_rembg_installed():
        version = get_installed_rembg_version()
        ok(f"rembg is already installed (version: {version})")
        if gpu:
            info("GPU support requested — re-installing with [gpu] extra...")
            install_rembg(gpu=True)
    else:
        info("rembg is not installed — installing now")
        install_rembg(gpu=gpu)

    # Re-verify
    if not is_rembg_installed():
        die("rembg still not importable after install. See error above.")

    version = get_installed_rembg_version()
    ok(f"rembg {version} ready")

    # Quick model smoke test info
    info("Model weights will auto-download to ~/.u2net/ on first use (~200MB).")

    print()
    print("Installation complete. You can now use:")
    print("  python3 bg-remover.py <image>")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        die("Interrupted by user", code=130)
