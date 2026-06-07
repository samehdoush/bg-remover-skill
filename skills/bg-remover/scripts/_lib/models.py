"""Model catalog and auto-selection heuristics for rembg models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class ModelInfo:
    name: str
    description: str
    best_for: str
    speed: Literal["very_fast", "fast", "medium", "slow"]
    quality: Literal["acceptable", "good", "very_good", "excellent", "best"]
    category: Literal["general", "portrait", "anime", "product", "specialty"]
    needs_extra: bool = False


MODELS: dict[str, ModelInfo] = {
    "u2net": ModelInfo(
        name="u2net",
        description="Pre-trained model for general use cases. The original rembg default.",
        best_for="General purpose, default choice when nothing else fits",
        speed="fast",
        quality="good",
        category="general",
    ),
    "u2netp": ModelInfo(
        name="u2netp",
        description="Lightweight version of u2net. Smaller model file, faster inference.",
        best_for="Quick previews, low-power devices, batch processing many small images",
        speed="very_fast",
        quality="acceptable",
        category="general",
    ),
    "u2net_human_seg": ModelInfo(
        name="u2net_human_seg",
        description="Pre-trained model for human segmentation. Full body silhouettes.",
        best_for="Full body person shots, silhouette extraction",
        speed="fast",
        quality="good",
        category="portrait",
    ),
    "u2net_cloth_seg": ModelInfo(
        name="u2net_cloth_seg",
        description="Pre-trained model for clothes parsing (upper body, lower body, full body).",
        best_for="Fashion photography, garment isolation",
        speed="fast",
        quality="good",
        category="product",
    ),
    "silueta": ModelInfo(
        name="silueta",
        description="Same as u2net but reduced to 43MB. Good lightweight option.",
        best_for="Lightweight general use, low-spec hardware",
        speed="fast",
        quality="acceptable",
        category="general",
    ),
    "isnet-general-use": ModelInfo(
        name="isnet-general-use",
        description="ISNet variant for general use. Better than u2net on complex scenes.",
        best_for="Complex general scenes, mixed subjects",
        speed="fast",
        quality="very_good",
        category="general",
    ),
    "isnet-anime": ModelInfo(
        name="isnet-anime",
        description="High-accuracy segmentation for anime characters and illustrations.",
        best_for="Anime, manga, illustrations, line art",
        speed="fast",
        quality="excellent",
        category="anime",
    ),
    "birefnet-general": ModelInfo(
        name="birefnet-general",
        description="BiRefNet general-purpose model. SOTA 2025, excellent on hair and edges.",
        best_for="Product photos, portraits, general high-quality output",
        speed="medium",
        quality="excellent",
        category="general",
    ),
    "birefnet-general-lite": ModelInfo(
        name="birefnet-general-lite",
        description="Lightweight BiRefNet. Faster, slightly lower quality.",
        best_for="Quick general processing when birefnet-general is too slow",
        speed="fast",
        quality="very_good",
        category="general",
    ),
    "birefnet-portrait": ModelInfo(
        name="birefnet-portrait",
        description="BiRefNet specialized for human portraits. Best hair/face edges.",
        best_for="Portraits, headshots, profile pictures, hair detail",
        speed="medium",
        quality="excellent",
        category="portrait",
    ),
    "birefnet-dis": ModelInfo(
        name="birefnet-dis",
        description="BiRefNet for dichotomous image segmentation. Handles thin structures.",
        best_for="Thin structures, complex contours, fine details",
        speed="medium",
        quality="excellent",
        category="specialty",
    ),
    "birefnet-hrsod": ModelInfo(
        name="birefnet-hrsod",
        description="BiRefNet for high-resolution salient object detection.",
        best_for="Very high resolution images, large complex scenes",
        speed="medium",
        quality="excellent",
        category="specialty",
    ),
    "birefnet-cod": ModelInfo(
        name="birefnet-cod",
        description="BiRefNet for camouflaged object detection.",
        best_for="Subjects blending into background, low contrast scenes",
        speed="medium",
        quality="excellent",
        category="specialty",
    ),
    "birefnet-massive": ModelInfo(
        name="birefnet-massive",
        description="BiRefNet trained on the largest dataset. Highest accuracy.",
        best_for="Maximum quality, no time constraint, critical output",
        speed="slow",
        quality="best",
        category="general",
    ),
    "bria-rmbg": ModelInfo(
        name="bria-rmbg",
        description="State-of-the-art background removal by BRIA AI. Commercial-grade.",
        best_for="Commercial e-commerce, professional photo editing",
        speed="fast",
        quality="excellent",
        category="product",
    ),
    "sam": ModelInfo(
        name="sam",
        description="Segment Anything Model. Interactive point-based prompts.",
        best_for="Interactive use, custom regions, requires prompt input",
        speed="slow",
        quality="excellent",
        category="specialty",
        needs_extra=True,
    ),
}


def get_model_info(name: str) -> ModelInfo:
    if name not in MODELS:
        available = ", ".join(sorted(MODELS.keys()))
        raise ValueError(
            f"Unknown model '{name}'. Available models: {available}"
        )
    return MODELS[name]


def list_models() -> list[str]:
    return sorted(MODELS.keys())


def suggest_model(image_path: str | Path) -> str:
    """Heuristic-based model suggestion from image content.

    Detects (no ML inference, just pixel analysis):
    - Faces (heuristic) → birefnet-portrait
    - Flat colors / anime-like → isnet-anime
    - Light background + product-like → birefnet-general
    - Default → u2net
    """
    try:
        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            w, h = rgb.size
            arr = np.asarray(rgb.resize((min(256, w), min(256, h))))

        # 1. Anime / illustration heuristic: high saturation, few unique colors,
        #    or large flat regions.
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        if unique_colors < 800:
            return "isnet-anime"

        # 2. Portrait heuristic: detect skin-tone regions.
        # Convert to HSV and check for skin-tone pixels in expected range.
        hsv = np.asarray(rgb.resize((128, 128)).convert("HSV"))
        h_ch, s_ch, v_ch = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        skin_mask = (
            ((h_ch >= 0) & (h_ch <= 25) | (h_ch >= 165) & (h_ch <= 180))
            & (s_ch >= 30)
            & (s_ch <= 170)
            & (v_ch >= 60)
            & (v_ch <= 255)
        )
        skin_ratio = float(skin_mask.sum()) / skin_mask.size
        if skin_ratio > 0.04:
            return "birefnet-portrait"

        # 3. Product / light-bg heuristic: dominant background brightness
        avg_value = float(v_ch.mean())
        if avg_value > 200:
            return "birefnet-general"

        # 4. Fallback
        return "u2net"

    except Exception:
        return "u2net"
