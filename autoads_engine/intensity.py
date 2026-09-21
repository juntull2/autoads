"""
intensity.py — Editing Intensity Engine
==========================================
Manages the overall editing energy across the ad timeline.

Provides per-scene intensity values that modulate:
  - Camera motion scale
  - Caption animation scale
  - SFX volume
  - Transition strength

The core idea: a Meta Reels ad is NOT uniform in energy.
It follows a dramatic arc: Hook(high) → Problem(med) → Solution(high) → CTA(max).
"""

from __future__ import annotations
from typing import List, Dict

from autoads_engine.scene_model import SceneDef, ScenePurpose, PURPOSE_INTENSITY


class IntensityEngine:
    """
    Computes effective intensity for each scene, accounting for:
      1. Scene-level purpose baseline
      2. Scene-specific override
      3. Global preset multiplier
      4. Position-based arc adjustment (smooth curve)
    """

    def __init__(self, global_scale: float = 1.0):
        self.global_scale = global_scale

    def compute(self, scenes: List[SceneDef]) -> List[float]:
        """
        Returns a list of effective intensity values, one per scene.
        Values are in range [0.2, 1.0].
        """
        base = [self._base_intensity(s) for s in scenes]
        arc = self._arc_multipliers(len(scenes))
        result = []
        for b, a in zip(base, arc):
            val = b * a * self.global_scale
            result.append(max(0.2, min(1.0, val)))
        return result

    def _base_intensity(self, scene: SceneDef) -> float:
        """Get the canonical base intensity for a scene."""
        return scene.effective_intensity()

    def _arc_multipliers(self, n: int) -> List[float]:
        """
        Generate a smooth intensity arc curve for n scenes.
        Shape: high start → dip in middle → high end
        This creates the feel of a structured ad, not flat monotony.
        """
        if n <= 1:
            return [1.0]
        mults = []
        for i in range(n):
            t = i / (n - 1)  # 0.0 → 1.0
            # Curve: 1.0 at start/end, ~0.85 in middle
            # Using a simple U-curve: 1 - 0.15 * sin(pi*t)
            import math
            m = 1.0 - 0.15 * math.sin(math.pi * t)
            mults.append(m)
        return mults

    def per_scene_params(
        self, scenes: List[SceneDef]
    ) -> List[Dict[str, float]]:
        """
        Returns per-scene intensity parameters for all engines.
        """
        intensities = self.compute(scenes)
        return [
            {
                "scene_id": s.id,
                "intensity": eff,
                "camera_scale": eff,
                "caption_scale": eff,
                "sfx_scale": eff,
                "transition_scale": eff,
            }
            for s, eff in zip(scenes, intensities)
        ]
