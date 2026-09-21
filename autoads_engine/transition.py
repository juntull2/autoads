"""
transition.py — Transition Engine
====================================
Generates FFmpeg filter expressions for cut transitions.
Applied at the start of each chunk as a fade/zoom-in effect.

Design: Returns a filter string fragment to append to the chunk's
filter_complex chain. Input label = previous video node, output = 'trans_out'.
"""

from __future__ import annotations
from autoads_engine.scene_model import TransitionType, ScenePurpose


# ---------------------------------------------------------------------------
# FFmpeg filter expressions per transition type
# 
# Convention: {input_label} and {output_label} are format placeholders.
# Duration (d) scales with intensity.
# ---------------------------------------------------------------------------

def _build_filter(
    transition: TransitionType,
    input_label: str,
    output_label: str,
    intensity: float = 1.0,
) -> str:
    """Return a single FFmpeg filter fragment for a transition."""

    if transition == TransitionType.HARD_CUT:
        # No-op: just pass through
        return f"[{input_label}]null[{output_label}]"

    elif transition == TransitionType.FLASH:
        d = round(0.06 + 0.04 * intensity, 3)
        return f"[{input_label}]fade=t=in:st=0:d={d}:color=white[{output_label}]"

    elif transition == TransitionType.WHITE_FLASH:
        d = round(0.10 + 0.08 * intensity, 3)
        return f"[{input_label}]fade=t=in:st=0:d={d}:color=white[{output_label}]"

    elif transition == TransitionType.FADE:
        d = round(0.20 + 0.10 * intensity, 3)
        return f"[{input_label}]fade=t=in:st=0:d={d}:color=black[{output_label}]"

    elif transition == TransitionType.ZOOM_CUT:
        # Brief over-zoom at start then settle — creates a snap-in feel
        # Uses a zoomed crop that quickly normalizes: starts at 1.18, eases to 1.0
        zoom = round(1.18 + 0.06 * intensity, 4)
        ramp = round(0.20 + 0.10 * (1 - intensity), 4)
        return (
            f"[{input_label}]"
            f"scale=w='iw*({zoom:.4f}-({zoom:.4f}-1)*min(t/{ramp:.4f},1))'"
            f":h='ih*({zoom:.4f}-({zoom:.4f}-1)*min(t/{ramp:.4f},1))'"
            f":eval=frame,"
            f"crop=1080:1920"
            f"[{output_label}]"
        )

    elif transition == TransitionType.BLUR_IN:
        # Gaussian blur dissolves to sharp — simulates focus pull
        d = round(0.12 + 0.08 * intensity, 3)
        radius = round(20 + 10 * intensity)
        return (
            f"[{input_label}]"
            f"boxblur=luma_radius='max(1,{radius}*(1-t/{d:.3f}))':luma_power=1"
            f":enable='lt(t,{d:.3f})',"
            f"fade=t=in:st=0:d={d:.3f}:alpha=1"
            f"[{output_label}]"
        )

    # Fallback
    return f"[{input_label}]null[{output_label}]"


class TransitionEngine:
    """
    Selects and builds transition filters for video chunks.

    Args:
        intensity_scale: Global multiplier for transition intensity.
    """

    def __init__(self, intensity_scale: float = 1.0):
        self.intensity_scale = intensity_scale

    def get_filter(
        self,
        transition: TransitionType,
        scene_intensity: float = 1.0,
        input_label: str = "cam_out",
        output_label: str = "trans_out",
    ) -> str:
        """Return FFmpeg filter fragment for the transition."""
        effective = min(1.5, scene_intensity * self.intensity_scale)
        return _build_filter(transition, input_label, output_label, effective)

    def from_legacy_flash_flag(
        self,
        flash: bool,
        scene_purpose: ScenePurpose,
        scene_intensity: float,
        input_label: str = "cam_out",
        output_label: str = "trans_out",
    ) -> str:
        """
        Backward-compat shim: converts v9 flash=True/False to a filter.
        If flash=True, derive the appropriate transition from scene purpose.
        If flash=False, HARD_CUT.
        """
        if not flash:
            return self.get_filter(
                TransitionType.HARD_CUT, scene_intensity, input_label, output_label
            )
        # Map purpose → appropriate flash type
        from autoads_engine.scene_model import PURPOSE_TRANSITION
        transition = PURPOSE_TRANSITION.get(scene_purpose, TransitionType.FLASH)
        return self.get_filter(transition, scene_intensity, input_label, output_label)
