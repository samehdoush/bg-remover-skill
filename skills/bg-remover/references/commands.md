# Commands Reference

Complete CLI flag reference for `bg-remover`.

## Synopsis

```
bg-remover [OPTIONS] INPUT
```

## Positional Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Path to image file, or directory when using `--batch` |

## Options

### Output

| Flag | Description |
|------|-------------|
| `-o, --output PATH` | Output file or directory. Default: `<input-stem>-no-bg.png` next to input |
| `-f, --format FMT` | Output format: `png` (default) or `webp` |
| `--quality N` | WebP quality 1-100 (default: 95) |
| `--only-mask` | Save only the alpha mask as grayscale PNG |

### Model

| Flag | Description |
|------|-------------|
| `-m, --model NAME` | Model to use (default: `auto`). See `models-guide.md` |
| `--auto` | Auto-detect best model from image content (default behavior) |
| `--list-models` | List all 16 models and exit |
| `--install` | Run dependency installer and exit |

### Quality

| Flag | Description |
|------|-------------|
| `-a, --alpha-matting` | Enable alpha matting for hair/fur/glass edges (slower) |

### Background Replacement

| Flag | Description |
|------|-------------|
| `--bg-color HEX` | Replace background with solid color (e.g. `#FFFFFF`, `#00FF00`, `#FFF`) |
| `--bg-image PATH` | Replace background with another image (auto-resized to fit) |

### Batch

| Flag | Description |
|------|-------------|
| `-b, --batch` | Treat input as directory, process all images |
| `-r, --recursive` | With `--batch`: recurse into subdirectories |

### Performance

| Flag | Description |
|------|-------------|
| `--threads N` | ONNX Runtime thread count (default: CPU count) |

### Output Control

| Flag | Description |
|------|-------------|
| `--quiet` | Suppress per-image progress output |

## Examples

### Single image (auto model)
```bash
bg-remover photo.jpg
# → photo-no-bg.png
```

### Single image, specific model
```bash
bg-remover -m birefnet-portrait portrait.jpg
# → portrait-no-bg.png
```

### Background → solid color
```bash
bg-remover --bg-color "#FFFFFF" product.jpg
# → product-no-bg.jpg  (white background, JPG)
```

### Background → custom image
```bash
bg-remover --bg-image studio.jpg subject.jpg
# → subject-no-bg.png  (subject composited on studio)
```

### Best edge quality (alpha matting)
```bash
bg-remover -a -m birefnet-portrait headshot.jpg
# → headshot-no-bg.png  (perfect hair edges)
```

### WebP output (smaller files)
```bash
bg-remover -f webp -q 90 photo.jpg
# → photo-no-bg.webp
```

### Batch process a folder
```bash
bg-remover -b ./photos -o ./transparent
# processes all images in ./photos, saves to ./transparent
```

### Batch + recursive
```bash
bg-remover -b ./catalog -o ./cleaned -r
# processes ./catalog and all subdirectories
```

### Batch + white background (e-commerce)
```bash
bg-remover -b ./products -o ./white-bg -m birefnet-general --bg-color "#FFFFFF"
# all products composited on white
```

### Anime batch
```bash
bg-remover -b ./anime -o ./cutouts -m isnet-anime
```

### List models
```bash
bg-remover --list-models
```

### Custom thread count (laptop: leave cores for other work)
```bash
bg-remover -b ./huge-folder --threads 2
```

### Mask only (for compositing in Photoshop / GIMP)
```bash
bg-remover --only-mask portrait.jpg
# → portrait-no-bg.png  (grayscale mask, white = keep, black = remove)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (invalid input, file not found, etc.) |
| 2 | Partial success (some files failed in batch) |
| 130 | Interrupted by user (Ctrl+C) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `U2NET_HOME` | Override model cache directory (default: `~/.u2net/`) |
| `OMP_NUM_THREADS` | Override ONNX thread count (equivalent to `--threads`) |
| `MODEL_CHECKSUM_DISABLED` | Set to `1` to skip model hash verification (for custom ONNX files) |
