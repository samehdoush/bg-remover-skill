# bg-remover-skill

A professional, AI-powered image background removal skill for Claude Code (and other AI coding agents). Built on top of the open-source [rembg](https://github.com/danielgatis/rembg) library with support for 16 specialized AI models, alpha matting, batch processing, and background replacement.

## Features

- **16 AI models** including BiRefNet (SOTA 2025), ISNet, U2Net, SAM, and BRIA-RMBG
- **Auto model selection** based on image content (portrait, anime, product, general)
- **Alpha matting** for flawless edges on hair, fur, and glass
- **Batch processing** with progress bar
- **Background replacement** with solid color OR custom image
- **Two output formats**: PNG (lossless transparent) and WebP (smaller size)
- **CPU-only** — no GPU required
- **Completely offline** after model download (no API keys, no cloud)
- **MIT licensed**, 100% free

## Installation

### Option 1: Install via vercel-labs/skills (recommended for Claude Code users)

```bash
# User-level (global) — works across all your projects
npx skills add samehdoush/bg-remover-skill -g -y
```

The CLI will auto-detect your installed agents (Claude Code, OpenCode, Cursor, etc.) and install accordingly. To install for Claude Code only:

```bash
npx skills add samehdoush/bg-remover-skill -a claude-code -g -y
```

### Option 2: Manual install (any agent)

Copy the `skills/bg-remover/` directory into your agent's skills folder:

| Agent | Path |
|-------|------|
| Claude Code | `~/.claude/skills/bg-remover/` |
| OpenCode | `~/.config/opencode/skills/bg-remover/` |
| Cursor | `~/.cursor/skills/bg-remover/` |

## Prerequisites

- **Python** 3.11, 3.12, or 3.13
- **pip** (bundled with Python)
- ~200 MB disk space for AI models (downloaded on first use)

The skill auto-installs `rembg` and dependencies on first run.

## Quick Start

### As a Claude Code skill

```
/bg-remover photo.jpg
/bg-remover --model birefnet-portrait face.jpg
/bg-remover --batch ./product-photos --out ./transparent
/bg-remover --bg-color "#00FF00" portrait.jpg
```

### As a standalone CLI tool

```bash
# Install dependencies (one-time)
python3 skills/bg-remover/scripts/install.py

# Process a single image
python3 skills/bg-remover/scripts/bg-remover.py photo.jpg

# Use a specific model
python3 skills/bg-remover/scripts/bg-remover.py -m birefnet-portrait portrait.jpg

# Batch process a folder
python3 skills/bg-remover/scripts/bg-remover.py -b ./photos -o ./transparent

# Replace background with a color
python3 skills/bg-remover/scripts/bg-remover.py --bg-color "#FFFFFF" product.jpg

# Replace background with another image
python3 skills/bg-remover/scripts/bg-remover.py --bg-image studio-bg.jpg product.jpg
```

## Usage

```
bg-remover [OPTIONS] INPUT
```

| Option | Description |
|--------|-------------|
| `INPUT` | Path to image file OR directory (with `--batch`) |
| `-o, --output PATH` | Output file or directory path |
| `-m, --model NAME` | AI model to use (default: `auto`) |
| `-a, --alpha-matting` | Enable alpha matting for better edges |
| `--bg-color HEX` | Replace background with solid color (e.g. `#FF0000`) |
| `--bg-image PATH` | Replace background with another image |
| `-f, --format EXT` | Output format: `png` (default) or `webp` |
| `-b, --batch` | Process all images in a directory |
| `--auto` | Auto-select best model based on image content |
| `--threads N` | Number of ONNX threads (default: CPU count) |
| `--quiet` | Suppress progress output |
| `-h, --help` | Show help message |

## Available Models

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `birefnet-portrait` | Human portraits | Fast | Excellent |
| `birefnet-general` | General purpose | Medium | Excellent |
| `birefnet-massive` | Highest accuracy (large model) | Slow | Best |
| `birefnet-dis` | Thin structures & complex edges | Medium | Excellent |
| `birefnet-cod` | Camouflaged objects | Medium | Excellent |
| `isnet-general-use` | General purpose | Fast | Very Good |
| `isnet-anime` | Anime & illustration | Fast | Excellent |
| `u2net` | Default general | Fast | Good |
| `u2netp` | Lightweight | Very Fast | Acceptable |
| `u2net_human_seg` | Full body silhouettes | Fast | Good |
| `u2net_cloth_seg` | Clothing parsing | Fast | Good |
| `silueta` | Lightweight alternative | Fast | Acceptable |
| `sam` | Interactive (point prompts) | Slow | Excellent |
| `bria-rmbg` | Commercial-grade | Fast | Excellent |

For details, see [`skills/bg-remover/references/models-guide.md`](skills/bg-remover/references/models-guide.md).

## Examples

```bash
# E-commerce product photo
bg-remover --auto --bg-color "#FFFFFF" product.png
# → clean product on white background

# Profile picture for social media
bg-remover -m birefnet-portrait me.jpg
# → transparent PNG ready for any background

# Anime character
bg-remover -m isnet-anime character.png
# → clean cutout preserving line art

# Batch process entire photoshoot
bg-remover -b ./raw-photos -o ./transparent --threads 4
# → processes all images with 4 CPU threads

# Replace with custom background
bg-remover --bg-image beach-sunset.jpg family-photo.jpg
# → family on the beach (composited)
```

## How It Works

1. Claude receives your request to remove/replace a background
2. The skill locates the image and runs the bundled Python script
3. The script auto-installs `rembg` if not present
4. A specialized AI model analyzes the image and creates a precise alpha mask
5. The mask is composited onto transparent / colored / custom background
6. The result is saved as PNG (lossless) or WebP (compressed)

## Performance

Tested on Apple M1 Pro (CPU only, no GPU):

| Image Size | Model | Time |
|------------|-------|------|
| 1024×1024 | u2net | 0.8s |
| 1024×1024 | birefnet-general | 1.4s |
| 2048×2048 | birefnet-massive | 4.2s |
| 4096×4096 | birefnet-portrait | 8.1s |

GPU acceleration available via `rembg[gpu]` (requires CUDA + cuDNN).

## Troubleshooting

Common issues and solutions are documented in [`skills/bg-remover/references/troubleshooting.md`](skills/bg-remover/references/troubleshooting.md).

Quick checks:
- **Python version**: `python3 --version` must be 3.11+
- **Install manually**: `pip install "rembg[cpu]" pillow`
- **Models cached at**: `~/.u2net/`
- **Force re-download**: `rm -rf ~/.u2net/`

## License

MIT — see [LICENSE](LICENSE).

## Credits

- **[rembg](https://github.com/danielgatis/rembg)** by Daniel Gatis — the underlying library
- **[BiRefNet](https://github.com/ZhengPeng7/BiRefNet)** — state-of-the-art segmentation model
- **[ONNX Runtime](https://onnxruntime.ai/)** — inference engine
