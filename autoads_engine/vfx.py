"""
vfx.py — Visual Effects (VFX) Engine for AutoAds
=================================================
Provides categorized visual effects overlays, replacing indiscriminate sparkle use:
  1. BEAUTY  — Radiance glow, 4-point diamond glimmers, porcelain sheen
  2. INFO    — Clinical measurement crosshairs, animated micro-scan lines
  3. IMPACT  — Dynamic vignette shockwave, edge flash pulse
  4. PRODUCT — Specular luxury light sweep (diagonal gleam across product)
"""

from __future__ import annotations
import os
import math
from typing import Optional, Dict
from PIL import Image, ImageDraw

from autoads_engine.scene_model import VFXCategory


class VFXEngine:
    """
    Manages procedural and frame-sequence VFX assets per category.
    Generates high quality transparent 1080x1920 overlay frame sequences.
    """

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.dirs = {
            VFXCategory.BEAUTY:  os.path.join(base_dir, "vfx_beauty"),
            VFXCategory.INFO:    os.path.join(base_dir, "vfx_info"),
            VFXCategory.IMPACT:  os.path.join(base_dir, "vfx_impact"),
            VFXCategory.PRODUCT: os.path.join(base_dir, "vfx_product"),
        }
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)

    def get_pattern(self, category: VFXCategory) -> Optional[str]:
        """Returns the FFmpeg file pattern for the given VFX category."""
        target_dir = self.dirs.get(category)
        if not target_dir:
            return None
        self.ensure_assets(category)
        return os.path.join(target_dir, "fx_%03d.png")

    def ensure_assets(self, category: VFXCategory, num_frames: int = 60):
        """Ensures that frames exist for the requested VFX category."""
        target_dir = self.dirs.get(category)
        if not target_dir:
            return

        existing = [f for f in os.listdir(target_dir) if f.endswith(".png")]
        if len(existing) >= num_frames:
            return

        print(f">> [VFXEngine] Generating procedural {category.value} overlay ({num_frames} frames)...")

        if category == VFXCategory.BEAUTY:
            self._generate_beauty_frames(target_dir, num_frames)
        elif category == VFXCategory.INFO:
            self._generate_info_frames(target_dir, num_frames)
        elif category == VFXCategory.IMPACT:
            self._generate_impact_frames(target_dir, num_frames)
        elif category == VFXCategory.PRODUCT:
            self._generate_product_frames(target_dir, num_frames)

    def _generate_beauty_frames(self, out_dir: str, num_frames: int):
        """Soft 4-point diamond glimmers with sinusoidal pulse."""
        coords = [(320, 750), (740, 820), (520, 680), (410, 960), (680, 1100)]
        for f in range(num_frames):
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            phase = f / num_frames * 2 * math.pi
            for i, (cx, cy) in enumerate(coords):
                scale = 0.5 + 0.5 * math.sin(phase + i * 1.3)
                if scale < 0.2:
                    continue
                size = int(32 * scale)
                alpha = int(220 * scale)
                # 4-point diamond sparkle
                d.line([(cx - size, cy), (cx + size, cy)], fill=(255, 255, 230, alpha), width=3)
                d.line([(cx, cy - size), (cx, cy + size)], fill=(255, 255, 230, alpha), width=3)
                r_core = max(2, int(size * 0.28))
                d.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=(255, 255, 255, alpha))
            img.save(os.path.join(out_dir, f"fx_{f+1:03d}.png"))

    def _generate_info_frames(self, out_dir: str, num_frames: int):
        """Clinical micro measurement crosshairs and scanning laser accent."""
        for f in range(num_frames):
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            # Scanning horizontal cyan line traveling downward in mid section
            scan_y = int(600 + 500 * (f / num_frames))
            d.line([(180, scan_y), (900, scan_y)], fill=(0, 230, 255, 140), width=2)
            d.line([(240, scan_y - 1), (840, scan_y - 1)], fill=(255, 255, 255, 180), width=1)
            # Corner targeting brackets
            pad = 220
            d.line([(pad, 600), (pad + 40, 600)], fill=(0, 230, 255, 180), width=3)
            d.line([(pad, 600), (pad, 640)], fill=(0, 230, 255, 180), width=3)
            d.line([(1080 - pad, 600), (1080 - pad - 40, 600)], fill=(0, 230, 255, 180), width=3)
            d.line([(1080 - pad, 600), (1080 - pad, 640)], fill=(0, 230, 255, 180), width=3)
            img.save(os.path.join(out_dir, f"fx_{f+1:03d}.png"))

    def _generate_impact_frames(self, out_dir: str, num_frames: int):
        """Edge vignette shockwave pulse for high-tension moments."""
        for f in range(num_frames):
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            # Edge darkening pulse
            intensity = 0.5 + 0.5 * math.sin(f / num_frames * 4 * math.pi)
            border_alpha = int(90 * intensity)
            d.rectangle([0, 0, 1080, 1920], outline=(255, 50, 50, border_alpha), width=16)
            img.save(os.path.join(out_dir, f"fx_{f+1:03d}.png"))

    def _generate_product_frames(self, out_dir: str, num_frames: int):
        """Diagonal specular light beam sweep across packaging."""
        for f in range(num_frames):
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            # Diagonal beam sweeping from x = -400 to 1480
            progress = f / num_frames
            sweep_x = int(-300 + 1680 * progress)
            sweep_w = 120
            # Draw semi-transparent diagonal white sheen polygon
            pts = [
                (sweep_x - sweep_w, 0),
                (sweep_x + sweep_w, 0),
                (sweep_x + sweep_w - 300, 1920),
                (sweep_x - sweep_w - 300, 1920)
            ]
            d.polygon(pts, fill=(255, 255, 255, 65))
            img.save(os.path.join(out_dir, f"fx_{f+1:03d}.png"))
