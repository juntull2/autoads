"""
camera.py — Camera Motion Engine
==================================
Generates FFmpeg filter_complex expressions for each CameraMotion type.
Intensity is scaled by scene intensity (0.0–1.0) and preset multiplier.

Key design decisions:
- Returns filter strings to be injected into the existing chunk rendering pipeline.
- Micro-shake is implemented via Pillow frame-by-frame (fallback to zoom for FFmpeg-only).
- All filters produce output as [cam_out] label.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple

from autoads_engine.scene_model import CameraMotion, ScenePurpose


# ---------------------------------------------------------------------------
# Base zoom factors per motion type
# ---------------------------------------------------------------------------
# (base_start_scale, base_end_scale) relative to 1.0
_ZOOM_PARAMS: dict[CameraMotion, tuple[float, float]] = {
    CameraMotion.STATIC:        (1.00, 1.00),
    CameraMotion.SLOW_ZOOM_IN:  (1.00, 1.06),  # 6% zoom over clip duration
    CameraMotion.PUSH_IN:       (1.00, 1.10),  # 10% push
    CameraMotion.FAST_PUSH:     (1.00, 1.16),  # 16% for hook energy
    CameraMotion.PULL_OUT:      (1.14, 1.00),  # start zoomed, pull back
    CameraMotion.PUNCH_ZOOM:    (1.00, 1.22),  # aggressive punch
    CameraMotion.PAN_LEFT:      (1.10, 1.10),  # pan within zoomed frame
    CameraMotion.PAN_RIGHT:     (1.10, 1.10),
    CameraMotion.MICRO_SHAKE:   (1.06, 1.06),  # zoomed base for shake crop
}

W, H = 1080, 1920


class CameraEngine:
    """
    Produces FFmpeg filter_complex fragments for camera motion.

    Args:
        intensity_scale: Global multiplier for motion intensity (from preset).
                         1.0 = normal, 0.5 = subtle, 1.5 = aggressive.
    """

    def __init__(self, intensity_scale: float = 1.0):
        self.intensity_scale = intensity_scale

    def get_filter(
        self,
        motion: CameraMotion,
        scene_intensity: float = 1.0,
        clip_duration: float = 2.0,
        input_label: str = "scaled",
        output_label: str = "cam_out",
    ) -> str:
        """
        Return a single FFmpeg filter expression for the given camera motion.

        The input is assumed to already be 1080x1920 (from scale+crop).
        The output is [output_label] ready for subsequent filters.

        For MICRO_SHAKE, returns a zoomed static filter because true shake
        requires frame-by-frame processing (handled in render_chunk).
        """
        effective = min(1.5, scene_intensity * self.intensity_scale)
        base_start, base_end = _ZOOM_PARAMS.get(motion, (1.00, 1.08))

        # Scale zoom delta by effective intensity (but keep start at 1.0 for zoom-in types)
        if motion in (CameraMotion.STATIC,):
            return f"[{input_label}]null[{output_label}]"

        if motion == CameraMotion.PULL_OUT:
            # start = 1.0 + (base_start-1.0)*eff, end=1.0
            s_scale = 1.0 + (base_start - 1.0) * effective
            return (
                f"[{input_label}]"
                f"scale=w='iw*({s_scale:.4f}-({s_scale:.4f}-1.0)*t/{clip_duration:.4f})'"
                f":h='ih*({s_scale:.4f}-({s_scale:.4f}-1.0)*t/{clip_duration:.4f})'"
                f":eval=frame,"
                f"crop={W}:{H}"
                f"[{output_label}]"
            )

        if motion in (CameraMotion.PAN_LEFT, CameraMotion.PAN_RIGHT):
            zoom = 1.0 + (base_end - 1.0) * effective
            if motion == CameraMotion.PAN_LEFT:
                # Pan from right to left within zoomed frame
                pan_expr = f"(iw-{W})*t/{clip_duration:.4f}"
            else:
                # Pan from left to right
                pan_expr = f"(iw-{W})*(1-t/{clip_duration:.4f})"
            return (
                f"[{input_label}]"
                f"scale=w='iw*{zoom:.4f}':h='ih*{zoom:.4f}':eval=frame,"
                f"crop={W}:{H}:x='{pan_expr}':y=0"
                f"[{output_label}]"
            )

        if motion == CameraMotion.PUNCH_ZOOM:
            # Fast ramp up to peak in first 30% of clip, then slow ease
            peak = 1.0 + (base_end - 1.0) * effective
            # Use sin easing: scale = 1 + delta * sin(pi/2 * min(t/ramp, 1))
            ramp = clip_duration * 0.35
            return (
                f"[{input_label}]"
                f"scale="
                f"w='iw*(1+{peak-1.0:.4f}*sin(min(t/{ramp:.4f},1)*PI/2))'"
                f":h='ih*(1+{peak-1.0:.4f}*sin(min(t/{ramp:.4f},1)*PI/2))'"
                f":eval=frame,"
                f"crop={W}:{H}"
                f"[{output_label}]"
            )

        if motion == CameraMotion.MICRO_SHAKE:
            # Provide zoomed base; actual shake offsets applied in Pillow path
            zoom = 1.0 + (base_end - 1.0) * effective
            return (
                f"[{input_label}]"
                f"scale=w='iw*{zoom:.4f}':h='ih*{zoom:.4f}':eval=frame,"
                f"crop={W}:{H}"
                f"[{output_label}]"
            )

        # Default: linear zoom-in (SLOW_ZOOM_IN, PUSH_IN, FAST_PUSH)
        end_scale = 1.0 + (base_end - 1.0) * effective
        rate = (end_scale - 1.0) / clip_duration
        return (
            f"[{input_label}]"
            f"scale=w='iw*(1+{rate:.6f}*t)':h='ih*(1+{rate:.6f}*t)':eval=frame,"
            f"crop={W}:{H}"
            f"[{output_label}]"
        )

    def get_shake_offsets(
        self,
        frame_count: int,
        fps: float = 30.0,
        amplitude: float = 4.0,
        scene_intensity: float = 1.0,
    ) -> list[tuple[int, int]]:
        """
        Return (dx, dy) pixel offsets for MICRO_SHAKE, one per frame.
        Used by Pillow-based frame compositor.
        """
        amp = amplitude * min(1.5, scene_intensity * self.intensity_scale)
        offsets = []
        for f in range(frame_count):
            t = f / fps
            dx = int(amp * math.sin(2 * math.pi * 8 * t))
            dy = int(amp * 0.4 * math.sin(2 * math.pi * 6 * t + math.pi / 3))
            offsets.append((dx, dy))
        return offsets

    def build_legacy_zoom_filter(
        self,
        zoom: bool,
        input_label: str = "scaled",
        output_label: str = "cam_out",
        clip_dur: float = 2.0,
    ) -> str:
        """
        Backward-compat shim: converts v9 zoom=True/False flag to a filter.
        Used when a cut has no explicit camera motion set.
        """
        if not zoom:
            return f"[{input_label}]null[{output_label}]"
        return (
            f"[{input_label}]"
            f"scale=w='iw*(1+0.07*t)':h='ih*(1+0.07*t)':eval=frame,"
            f"crop={W}:{H}"
            f"[{output_label}]"
        )
