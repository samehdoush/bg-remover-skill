# Examples Gallery

Real-world usage examples for the `bg-remover` skill.

## 1. Profile Picture

```bash
bg-remover -m birefnet-portrait -a me.jpg
# Produces: me-no-bg.png (perfect hair edges, transparent bg)
```

Use case: LinkedIn, Twitter, Instagram, dating apps.

## 2. E-commerce Product Photos

```bash
# Batch process 500 product photos onto white background
bg-remover -b ./raw-products -o ./white-clean \
  -m birefnet-general --bg-color "#FFFFFF" --threads 4
```

Use case: Shopify, Amazon, eBay listings.

## 3. Anime Sticker Pack

```bash
bg-remover -b ./anime-characters -o ./stickers -m isnet-anime -f webp -q 85
```

Use case: Telegram stickers, Discord emojis, Twitch emotes.

## 4. Family Photo → Beach

```bash
bg-remover --bg-image tropical-beach-sunset.jpg family-photo.jpg
# Output: family-photo-no-bg.png  (family composited on the beach)
```

Use case: Personalized greeting cards, social media.

## 5. Passport Photo

```bash
bg-remover -m birefnet-portrait -a --bg-color "#FFFFFF" passport.jpg
```

Use case: Visa applications, official documents.

## 6. Pet Cutout

```bash
bg-remover -m birefnet-dis -a dog-photo.jpg
# Best for fur detail
```

Use case: Custom merchandise, pet portraits.

## 7. Logo on Transparent

```bash
bg-remover -m birefnet-general --only-mask logo.png
# Then composite onto any color in your design tool
```

Use case: Brand assets, presentations.

## 8. Bulk Image Processing (CI/CD)

```bash
# Process every image in a project, fail-fast
bg-remover -b ./public/uploads -o ./public/cleaned -r --quiet
echo "Done. Check ./public/cleaned for output."
```

Use case: Web app backends, CMS migrations.

## 9. Video Frame Extraction (via FFmpeg)

```bash
# Extract frames → process → reassemble
mkdir frames
ffmpeg -i video.mp4 -vf fps=1 frames/frame-%04d.png
bg-remover -b frames -o frames-clean -m birefnet-general
ffmpeg -i frames-clean/frame-%04d.png -r 30 -c:v libx264 -pix_fmt yuv420p output.mp4
```

Use case: Removing background from talking-head videos.

## 10. Pipeline: Remove bg → Add gradient

```bash
# First get transparent PNG
bg-remover -m birefnet-general subject.png

# Then composite on a gradient (requires ImageMagick)
convert -size 2000x2000 gradient:'#FF6B35-#004E89' bg-gradient.jpg
composite subject-no-bg.png bg-gradient.jpg -gravity center final.jpg
```

Use case: Marketing materials, banner ads.

## Performance Recipes

### Laptop (4 cores, 8GB RAM)
```bash
bg-remover -b ./photos --threads 2 --quiet
```

### Desktop (16 cores, 32GB RAM)
```bash
bg-remover -b ./photos --threads 8
```

### Server (many cores, no GUI)
```bash
OMP_NUM_THREADS=16 bg-remover -b ./huge-dataset -o ./output --quiet
```

## Quick "Cheat Sheet"

| I want to... | Command |
|--------------|---------|
| Just remove bg | `bg-remover photo.jpg` |
| Best for portraits | `bg-remover -m birefnet-portrait -a face.jpg` |
| Best for anime | `bg-remover -m isnet-anime character.png` |
| Best for products | `bg-remover -m birefnet-general product.jpg` |
| White background | `bg-remover --bg-color "#FFFFFF" photo.jpg` |
| Custom background | `bg-remover --bg-image bg.jpg photo.jpg` |
| Smaller file (WebP) | `bg-remover -f webp photo.jpg` |
| Batch process | `bg-remover -b ./in -o ./out` |
| Get mask only | `bg-remover --only-mask photo.jpg` |
| See all models | `bg-remover --list-models` |
| Install deps | `bg-remover --install` |
