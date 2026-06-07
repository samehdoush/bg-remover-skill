# Models Guide

The `bg-remover` skill ships with all 16 models from the [rembg](https://github.com/danielgatis/rembg) library. Each model has different strengths; pick the one that best matches your image type.

## Quick Reference

| Model | Best for | Speed | Quality |
|-------|----------|-------|---------|
| `u2net` | General purpose (default) | Fast | Good |
| `u2netp` | Quick previews, low-power | Very fast | Acceptable |
| `u2net_human_seg` | Full body silhouettes | Fast | Good |
| `u2net_cloth_seg` | Fashion/garment isolation | Fast | Good |
| `silueta` | Lightweight general | Fast | Acceptable |
| `isnet-general-use` | Complex general scenes | Fast | Very good |
| `isnet-anime` | Anime & illustration | Fast | Excellent |
| `birefnet-general` | Products, general high quality | Medium | Excellent |
| `birefnet-general-lite` | Faster BiRefNet | Fast | Very good |
| `birefnet-portrait` | Portraits, headshots, hair | Medium | Excellent |
| `birefnet-dis` | Thin structures, complex edges | Medium | Excellent |
| `birefnet-hrsod` | High-resolution scenes | Medium | Excellent |
| `birefnet-cod` | Camouflaged subjects | Medium | Excellent |
| `birefnet-massive` | Maximum accuracy | Slow | Best |
| `bria-rmbg` | Commercial e-commerce | Fast | Excellent |
| `sam` | Interactive (point prompts) | Slow | Excellent |

## Detailed Descriptions

### u2net (default)
The original rembg workhorse. Solid general-purpose segmentation, but struggles with fine details like hair, fur, and transparent objects. Use when you need decent results fast and don't have a specific subject type in mind.

### u2netp
A pruned (smaller, faster) version of u2net. **43 MB** on disk, ~2× faster. Use for previews or low-power hardware. Quality is noticeably lower.

### u2net_human_seg
Specialized for full-body human silhouettes. Better at extracting a person from busy backgrounds than u2net. Use for full-body photos (not headshots).

### u2net_cloth_seg
Parses clothing into upper body, lower body, and full body categories. Best for fashion photography where you want to isolate a specific garment.

### silueta
Same architecture as u2net but with a reduced checkpoint (43 MB). Sweet spot between u2netp and u2net.

### isnet-general-use
ISNet (Image Segmentation Net) trained for general use. Often a noticeable improvement over u2net on complex scenes with multiple subjects.

### isnet-anime
**The best model for anime, manga, and illustrations.** Trained specifically on illustrated content. Preserves line art and flat color regions cleanly. Do NOT use on photos.

### birefnet-general
**BiRefNet** (Bilateral Reference Network) is state-of-the-art as of 2025. Outperforms rembg/u2net on hair accuracy (94% vs 81%) and transparent/glass objects (78% vs 59%). Use as your default for product photos and high-quality general work.

### birefnet-general-lite
Faster, slightly less accurate version of `birefnet-general`. Use when you need BiRefNet quality at u2net speed.

### birefnet-portrait
**The best model for portraits, headshots, and profile pictures.** Specialized for human faces and hair. Recommended for LinkedIn, dating apps, ID photos, etc.

### birefnet-dis
BiRefNet trained for **Dichotomous Image Segmentation (DIS)** — best for thin structures and complex contours like bicycle spokes, plants, hair, and intricate objects.

### birefnet-hrsod
BiRefNet for **High-Resolution Salient Object Detection**. Use on very large images (4K+) where smaller models lose detail.

### birefnet-cod
BiRefNet for **Camouflaged Object Detection**. Use when the subject blends into the background (animals in nature, military patterns, etc.).

### birefnet-massive
BiRefNet trained on the largest combined dataset. **The highest accuracy of any model** but the slowest. Use when quality is critical and you can wait 5-10× longer.

### bria-rmbg
State-of-the-art model from **BRIA AI** for commercial use. Excellent on product photos, fast inference, and licensed for commercial deployment.

### sam
**Segment Anything Model (Meta)**. Interactive — requires you to pass point prompts or bounding boxes. Not recommended for fully automatic workflows but unbeatable when you need to isolate a specific region.

## Auto-Detection Logic

When you use `bg-remover` without specifying a model (or with `--auto`), the script uses these heuristics:

1. **Few unique colors (< 800 in a 256-pixel thumbnail)** → `isnet-anime`
   - Catches anime, manga, flat-color illustrations

2. **Skin-tone pixels detected (> 4% of image)** → `birefnet-portrait`
   - Catches portraits, group photos, people

3. **Very bright background (avg value > 200 in HSV)** → `birefnet-general`
   - Catches product photography on white/light backgrounds

4. **Default** → `u2net`
   - Safe general-purpose choice

The auto-detect adds no measurable time (no model inference).

## Recommendations by Use Case

| Use case | Recommended model |
|----------|------------------|
| Profile picture | `birefnet-portrait` |
| Group photo | `birefnet-general` |
| Anime character | `isnet-anime` |
| Product on white bg | `birefnet-general` |
| Fashion / clothing | `birefnet-general` or `u2net_cloth_seg` |
| Animal / pet | `birefnet-dis` or `birefnet-general` |
| Car / vehicle | `birefnet-general` |
| Food | `birefnet-general` |
| Document / signature | `u2net` (good enough) |
| Critical print quality | `birefnet-massive` + `--alpha-matting` |
| Hair detail (single person) | `birefnet-portrait` + `--alpha-matting` |
| Transparent glass / bottle | `birefnet-dis` + `--alpha-matting` |

## Model File Sizes & First-Run Download

Models are auto-downloaded to `~/.u2net/` on first use. Subsequent runs use the cached copy.

| Model | Size |
|-------|------|
| `u2net` | 176 MB |
| `u2netp` | 4.7 MB |
| `u2net_human_seg` | 176 MB |
| `u2net_cloth_seg` | 176 MB |
| `silueta` | 43 MB |
| `isnet-general-use` | 168 MB |
| `isnet-anime` | 168 MB |
| `birefnet-general` | 218 MB |
| `birefnet-general-lite` | 79 MB |
| `birefnet-portrait` | 218 MB |
| `birefnet-dis` | 218 MB |
| `birefnet-hrsod` | 218 MB |
| `birefnet-cod` | 218 MB |
| `birefnet-massive` | 893 MB |
| `bria-rmbg` | 89 MB |
| `sam` | 2.4 GB (encoder + decoder) |

To clear the cache and force re-download:

```bash
rm -rf ~/.u2net/
```

Or set a custom location:

```bash
export U2NET_HOME=/path/to/your/models
```
