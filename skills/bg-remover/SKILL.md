---
name: bg-remover
description: Remove or replace image backgrounds using AI. Use this skill when the user wants to remove a background from a photo, create a transparent PNG, isolate a subject, replace a background with a solid color or another image, or batch-process product photos. Powered by the open-source rembg library with 16 specialized AI models (BiRefNet, ISNet, U2Net, SAM) for portraits, anime, products, and general images. Runs locally, no API keys, no cloud.
allowed-tools: Bash, Read, Glob
argument-hint: "<image-path> [--model NAME] [--bg-color HEX] [--bg-image PATH]"
---

# Background Remover

Professional AI-powered image background removal and replacement tool. Works on JPG, PNG, WebP, BMP, TIFF inputs and outputs transparent PNG or compressed WebP.

## When to Activate

Activate this skill when the user says things like:

- "Remove the background from this image"
- "Make this PNG transparent"
- "Cut out the subject from this photo"
- "Replace the background with white / green / #FF0000"
- "Put this person on a beach background"
- "Process all images in this folder"
- "Remove background from this anime character"
- "Make a profile picture (no background)"
- "Batch process these product photos"

## Prerequisites Check (run on first invocation)

```bash
python3 --version    # Must be 3.11+
```

If the user has never used this skill, run the auto-installer (it's safe and idempotent):

```bash
python3 "<skill-dir>/scripts/install.py"
```

The installer:
- Detects Python version
- Installs `rembg[cpu]` and dependencies via pip
- Shows a clear success/failure message

## Core Command Pattern

```bash
python3 "<skill-dir>/scripts/bg-remover.py" [OPTIONS] <input>
```

`<skill-dir>` is the directory containing this `SKILL.md` (so `scripts/bg-remover.py` resolves correctly from any CWD).

## Decision Tree — How to Invoke

### 1. Single image, just remove background
```bash
python3 "<skill-dir>/scripts/bg-remover.py" <input>
```
Default behavior: produces `<input-stem>-no-bg.png` next to the input, transparent PNG, model = `auto`.

### 2. User specifies a model
Respect their choice. Examples:
- `--model birefnet-portrait` → high quality on people
- `--model isnet-anime` → anime/illustration
- `--model birefnet-general` → products, general purpose
- `--model birefnet-massive` → highest quality (slow)

Full list of 16 models: see `references/models-guide.md`.

### 3. Replace background with a solid color
```bash
python3 "<skill-dir>/scripts/bg-remover.py" <input> --bg-color "#FFFFFF"
```
Accepts any hex color (`#FFF`, `#FFFFFF`, `#00FF00`, etc.).

### 4. Replace background with another image
```bash
python3 "<skill-dir>/scripts/bg-remover.py" <input> --bg-image <bg.jpg>
```
The bg image is resized to match the foreground.

### 5. Process multiple images
```bash
python3 "<skill-dir>/scripts/bg-remover.py" --batch <input-dir> --output <output-dir>
```
Use `--threads N` to control CPU usage (default: all cores).

### 6. Enable alpha matting (best for hair/fur/glass edges)
Add `--alpha-matting` to any of the above commands. Adds ~2× processing time but dramatically improves edge quality on difficult subjects.

### 7. Output as WebP (smaller files)
Add `--format webp` to any of the above.

## Auto Model Selection (default `--auto`)

When the user does not specify a model, the script auto-detects the best one based on image heuristics:

| Heuristic | Model |
|-----------|-------|
| Detected face | `birefnet-portrait` |
| Mostly flat colors (anime/illustration) | `isnet-anime` |
| Mostly white/light bg + product-like | `birefnet-general` |
| Fallback | `u2net` |

The detection is fast (no model inference) and adds no measurable time.

## Output Path Conventions

- **Single file, no `-o`**: writes to `<input-stem>-no-bg.png` next to the input
- **Single file with `-o PATH`**: writes to that exact path
- **Batch, no `-o`**: creates `<input-dir>/<input-dir-name>-no-bg/` subfolder
- **Batch with `-o DIR`**: writes to that directory

After the script runs, **always show the user the output path** and confirm the file was created.

## Error Handling

The script returns clear error messages. Common issues:

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: rembg` | Dependencies not installed | Run `install.py` first |
| `Python 3.11+ required` | Old Python | Upgrade Python |
| `Model X not found` | Typo in model name | Check `references/models-guide.md` |
| `Out of memory` | Image too large | Resize input or use a smaller model |
| `Could not load image` | Corrupt/unsupported file | Check file format and integrity |

If the script fails, read the error message, fix the root cause, and re-run. Do not silently retry.

## Performance Tips (mention when relevant)

- **First run** for a model: ~30-60s (model download, cached after)
- **Subsequent runs**: <2s for typical images (CPU)
- **Large images (4K+)**: 5-10s, consider downscaling first
- **Batch mode**: use `--threads N` to control CPU usage (don't max out on laptops)

## Examples in Conversation

**User**: "Remove the background from cat.jpg"
**You**: Run `bg-remover.py cat.jpg` → output: `cat-no-bg.png`

**User**: "I need a clean PNG of this portrait for my LinkedIn"
**You**: Run `bg-remover.py -m birefnet-portrait --alpha-matting portrait.jpg`

**User**: "Make all my product photos have a white background"
**You**: Run `bg-remover.py -b ./products -o ./white-bg --bg-color "#FFFFFF" -m birefnet-general`

**User**: "Cut out this anime character"
**You**: Run `bg-remover.py -m isnet-anime character.png`

## Reference Files (load on demand)

- `references/models-guide.md` — detailed model comparison
- `references/commands.md` — every CLI flag with examples
- `references/troubleshooting.md` — error fixes

Do not load these into context unless the user asks a specific question. They exist for progressive disclosure.

## After Every Run

1. Confirm the output file path
2. Show a brief summary: input size, model used, time, output size
3. Offer next steps (replace bg, batch process, etc.)

Never claim success without verifying the output file exists. Use `ls -la <output>` or similar.
