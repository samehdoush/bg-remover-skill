# Troubleshooting

Common issues and their fixes.

## Installation

### "Python 3.10 or older detected"
**Problem**: rembg requires Python 3.11-3.13.
**Fix**: Install a newer Python:
- macOS: `brew install python@3.12`
- Linux: `sudo apt install python3.12`
- Windows: download from https://python.org/downloads/

### "No module named 'rembg'"
**Problem**: Dependencies not installed.
**Fix**:
```bash
python3 bg-remover.py --install
# or manually:
pip install "rembg[cpu]" pillow
```

### "pip: command not found"
**Fix**:
```bash
python3 -m ensurepip --upgrade
# or install pip manually:
curl https://bootstrap.pypa.io/get-pip.py | python3
```

### SSL / certificate errors during install
**Fix**:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org "rembg[cpu]"
```

## Models

### "Model X not found"
**Problem**: Typo or unsupported model name.
**Fix**: Run `bg-remover --list-models` to see all valid names. Common typos: `birefnnet`, `birefnet-portaits`, `isnet-general_use`.

### First run is very slow
**Cause**: Model is being downloaded (100-900 MB depending on model).
**Fix**: This is one-time. Models are cached at `~/.u2net/`. Subsequent runs of the same model are fast.

To pre-download a model:
```bash
python3 -c "from rembg import new_session; new_session('birefnet-general')"
```

### Model download is stuck or fails
**Fix**:
1. Check your internet connection.
2. Try a different model (some are smaller and download faster).
3. Manually download from the rembg model index and place in `~/.u2net/`:
   ```bash
   wget -O ~/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
   ```

### "Could not load model: ONNX Runtime error"
**Cause**: Corrupt or partial model file.
**Fix**:
```bash
rm -rf ~/.u2net/
# Will be re-downloaded on next run
```

## Performance

### Very slow on large images
**Fix**:
- Resize the input first: `sips -Z 2048 photo.jpg` (macOS) or `magick photo.jpg -resize 2048x photo-small.jpg` (ImageMagick)
- Use a faster model: `u2net`, `u2netp`, `isnet-anime`, `silueta`
- Enable multi-threading: `--threads 8` (adjust to your CPU)

### Out of memory errors
**Cause**: Image too large for available RAM.
**Fix**:
- Resize input to max 2048px on longest side
- Use a smaller model (`u2netp`, `birefnet-general-lite`, `silueta`)

### High CPU usage, fan spinning
**Cause**: This is normal — rembg is CPU-intensive. Each image can use 100% of one core.
**Fix**:
- Use `--threads N` to limit parallelism
- Batch process during off-hours

## Image Quality

### Background is partially removed (haze, fringe)
**Fix**:
- Try a different model: `birefnet-dis` or `birefnet-portrait` are best for tricky edges
- Enable alpha matting: `--alpha-matting` (2× slower but dramatically better)
- If subject is anime: `isnet-anime`
- If product photo: `birefnet-general`

### Subject has a "halo" or color fringe
**Cause**: Edge artifacts from the model.
**Fix**:
- Enable alpha matting: `--alpha-matting`
- Try `birefnet-dis` (best for edges)

### Hair / fur looks "blocky"
**Fix**:
- Use `birefnet-portrait -a` for people
- Use `birefnet-dis -a` for animal fur
- Enable alpha matting: `--alpha-matting`

### Subject is too small in output (low resolution)
**Cause**: rembg preserves original resolution; the model just decides what's foreground.
**Fix**:
- Ensure your input image is high resolution
- For best quality, source 2000px+ images

## Background Replacement

### "Background image not found"
**Fix**: Use absolute path or check current working directory:
```bash
bg-remover --bg-image /full/path/to/bg.jpg subject.jpg
```

### Subject looks misplaced on the new background
**Cause**: The script always center-composites.
**Fix**: Post-process in an image editor if you need precise placement. The skill outputs the transparent PNG by default, so you can use any tool for final compositing.

### WebP file is larger than expected
**Fix**: Reduce quality: `--quality 80` or `--quality 70`.

## macOS-Specific

### "Operation not permitted" on first run
**Cause**: macOS Gatekeeper blocking the script.
**Fix**:
```bash
chmod +x bg-remover.py
xattr -d com.apple.quarantine bg-remover.py  # if downloaded from internet
```

### Python not found
**Fix**:
```bash
brew install python@3.12
# Then use the absolute path:
/opt/homebrew/bin/python3.12 bg-remover.py photo.jpg
```

## Windows-Specific

### Long path errors
**Fix**: Enable long paths in Windows or use shorter input/output paths.

### "python" vs "python3"
**Fix**: Use `py` launcher:
```bash
py bg-remover.py photo.jpg
```

## Still stuck?

1. Check the [rembg issues](https://github.com/danielgatis/rembg/issues) — your error may already be documented.
2. Run with `--quiet` removed to see full error output.
3. Try a different model to isolate model-specific vs environment-specific issues.
4. Test with a known-good image (e.g. a simple portrait) to verify rembg itself works.
