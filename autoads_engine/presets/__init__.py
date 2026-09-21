"""
presets/__init__.py — Preset Registry
========================================
Preset = a named configuration that sets all engine parameters.
Each preset defines the aesthetic style for a type of ad.

Usage:
    from autoads_engine.presets import get_preset
    cfg = get_preset("meta_reels_fast")
    camera_engine = CameraEngine(intensity_scale=cfg["camera_intensity_scale"])
"""

from __future__ import annotations
from typing import Dict, Any, List

from autoads_engine.scene_model import (
    CaptionAnimStyle, CameraMotion, TransitionType
)


# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

_PRESETS: Dict[str, Dict[str, Any]] = {

    "meta_reels_fast": {
        "description": "Fast-paced Meta Reels — aggressive edits, strong captions",
        "camera_intensity_scale":    1.2,
        "caption_intensity_scale":   1.2,
        "sfx_intensity_scale":       1.0,
        "transition_intensity_scale": 1.1,
        "global_intensity_scale":    1.0,
        "default_caption_anim":      CaptionAnimStyle.PUNCH,
        "default_transition":        TransitionType.FLASH,
        "keyword_highlight":         True,
        "auto_sfx":                  True,
        "bgm_volume_db":             -27,
        "outro_hold_s":              1.05,
    },

    "beauty_ads": {
        "description": "Soft beauty ad — elegant, warm, glowing",
        "camera_intensity_scale":    0.8,
        "caption_intensity_scale":   0.9,
        "sfx_intensity_scale":       0.7,
        "transition_intensity_scale": 0.8,
        "global_intensity_scale":    0.85,
        "default_caption_anim":      CaptionAnimStyle.POP,
        "default_transition":        TransitionType.WHITE_FLASH,
        "keyword_highlight":         True,
        "auto_sfx":                  True,
        "bgm_volume_db":             -27,
        "outro_hold_s":              1.2,
    },

    "product_ads": {
        "description": "Product-focused ad — clean transitions, strong product emphasis",
        "camera_intensity_scale":    1.0,
        "caption_intensity_scale":   1.0,
        "sfx_intensity_scale":       0.9,
        "transition_intensity_scale": 1.0,
        "global_intensity_scale":    0.95,
        "default_caption_anim":      CaptionAnimStyle.POP,
        "default_transition":        TransitionType.ZOOM_CUT,
        "keyword_highlight":         True,
        "auto_sfx":                  True,
        "bgm_volume_db":             -27,
        "outro_hold_s":              1.1,
    },

    "testimonial": {
        "description": "UGC testimonial style — natural, minimal effects",
        "camera_intensity_scale":    0.6,
        "caption_intensity_scale":   0.7,
        "sfx_intensity_scale":       0.4,
        "transition_intensity_scale": 0.6,
        "global_intensity_scale":    0.65,
        "default_caption_anim":      CaptionAnimStyle.SLIDE_UP,
        "default_transition":        TransitionType.HARD_CUT,
        "keyword_highlight":         False,
        "auto_sfx":                  False,
        "bgm_volume_db":             -30,
        "outro_hold_s":              1.0,
    },

    "ugc": {
        "description": "Raw UGC feel — almost no effects, max authenticity",
        "camera_intensity_scale":    0.5,
        "caption_intensity_scale":   0.6,
        "sfx_intensity_scale":       0.3,
        "transition_intensity_scale": 0.4,
        "global_intensity_scale":    0.55,
        "default_caption_anim":      CaptionAnimStyle.FADE_IN,
        "default_transition":        TransitionType.HARD_CUT,
        "keyword_highlight":         False,
        "auto_sfx":                  False,
        "bgm_volume_db":             -30,
        "outro_hold_s":              1.0,
    },

    "aggressive_sales": {
        "description": "High-urgency sales — max energy, frequent SFX",
        "camera_intensity_scale":    1.4,
        "caption_intensity_scale":   1.4,
        "sfx_intensity_scale":       1.2,
        "transition_intensity_scale": 1.3,
        "global_intensity_scale":    1.1,
        "default_caption_anim":      CaptionAnimStyle.PUNCH,
        "default_transition":        TransitionType.FLASH,
        "keyword_highlight":         True,
        "auto_sfx":                  True,
        "bgm_volume_db":             -25,
        "outro_hold_s":              1.0,
    },
}

# Default preset if none specified
DEFAULT_PRESET = "meta_reels_fast"


def get_preset(name: str = DEFAULT_PRESET) -> Dict[str, Any]:
    """
    Get a preset configuration dict by name.
    Falls back to DEFAULT_PRESET if name is not found.
    """
    if name not in _PRESETS:
        print(f"[Presets] Unknown preset '{name}', using '{DEFAULT_PRESET}'.")
        name = DEFAULT_PRESET
    return dict(_PRESETS[name])


def list_presets() -> List[str]:
    """Return a list of available preset names."""
    return list(_PRESETS.keys())
