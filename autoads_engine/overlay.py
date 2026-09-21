"""
overlay.py — Graphic Overlay Engine for Meta Reels Commercials
===============================================================
Generates and manages high-impact visual graphic overlays:
  1. Arrow      — Curved / straight pointer (CTA link, feature focus)
  2. Circle     — Organic circle highlight around trouble zone or stat
  3. Underline  — Bold neon brush underline below key text
  4. Highlight  — Semi-transparent marker highlight box
  5. Badge      — Modern compact sticker badge (e.g., '1위', '임상입증', '50% OFF')
  6. Check      — Vivid green/cyan checkmark icon
  7. X          — Red warning cross mark for pain points
  8. Burst      — Starburst / comic pop accent for discounts and impact

Supports:
  - Purpose & Keyword driven automatic overlay selection.
  - High-resolution PIL RGBA overlay rendering (1080x1920 viewport).
  - Clean ASS vector/tag overlay generation for subtitle layer integration.
"""

from __future__ import annotations
import math
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont

from autoads_engine.scene_model import ScenePurpose


class OverlayType(str, Enum):
    ARROW     = "arrow"
    CIRCLE    = "circle"
    UNDERLINE = "underline"
    HIGHLIGHT = "highlight"
    BADGE     = "badge"
    CHECK     = "check"
    X         = "x"
    BURST     = "burst"


@dataclass
class OverlaySpec:
    """Specification for a visual overlay instance."""
    overlay_type: OverlayType
    start_time: float               # seconds relative to scene/cut start
    end_time: float                 # seconds relative to scene/cut start
    position: Tuple[int, int]       # (x, y) center or anchor
    size: Tuple[int, int]           # (width, height)
    text: str = ""                  # text for badges or callouts
    color: Tuple[int, int, int, int] = (255, 230, 0, 255) # RGBA
    outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    line_width: int = 4
    rotation: float = 0.0           # degrees


class GraphicOverlayEngine:
    """
    Selects, configures, and renders graphic overlays tailored for vertical
    commercials (1080x1920) without cluttering the safe zones.
    """

    def __init__(self, font_path: Optional[str] = None):
        self.font_path = font_path or r"C:\Windows\Fonts\malgunbd.ttf"

    def select_overlays_for_scene(
        self,
        purpose: ScenePurpose,
        duration: float,
        keywords: Optional[List[str]] = None,
    ) -> List[OverlaySpec]:
        """
        Automatically selects appropriate graphic overlays based on scene purpose and keywords.
        """
        overlays: List[OverlaySpec] = []
        kw_list = [k.lower() for k in (keywords or [])]

        if purpose == ScenePurpose.HOOK:
            # Impact burst on hook
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.BURST,
                start_time=0.1,
                end_time=min(1.6, duration),
                position=(880, 420),
                size=(180, 180),
                color=(255, 225, 0, 240),
            ))

        elif purpose in (ScenePurpose.PROBLEM, ScenePurpose.AGITATION):
            # Red X or trouble zone circle
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.X,
                start_time=0.2,
                end_time=min(2.0, duration),
                position=(820, 520),
                size=(160, 160),
                color=(255, 45, 45, 240),
                line_width=12,
            ))
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.CIRCLE,
                start_time=0.6,
                end_time=min(2.4, duration),
                position=(540, 920),
                size=(320, 320),
                color=(255, 50, 50, 210),
                line_width=8,
            ))

        elif purpose in (ScenePurpose.SOLUTION, ScenePurpose.BENEFIT):
            # Check mark + Underline
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.CHECK,
                start_time=0.2,
                end_time=min(2.0, duration),
                position=(840, 460),
                size=(150, 150),
                color=(0, 235, 140, 245),
                line_width=12,
            ))
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.UNDERLINE,
                start_time=0.4,
                end_time=min(2.2, duration),
                position=(540, 1630),
                size=(460, 16),
                color=(0, 229, 255, 230),
                line_width=8,
            ))

        elif purpose == ScenePurpose.PRODUCT:
            # Ingredient badge + Highlight
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.BADGE,
                start_time=0.2,
                end_time=min(2.2, duration),
                position=(540, 340),
                size=(380, 70),
                text="🔬 초저분자 300Da 특허원료",
                color=(25, 30, 45, 225),
                outline_color=(0, 230, 255, 255),
            ))

        elif purpose == ScenePurpose.PROOF:
            # Verification check
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.CHECK,
                start_time=0.1,
                end_time=min(2.0, duration),
                position=(820, 320),
                size=(130, 130),
                color=(0, 240, 150, 240),
                line_width=10,
            ))

        elif purpose == ScenePurpose.CTA:
            # Downward pointer arrow + 50% burst
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.ARROW,
                start_time=0.2,
                end_time=duration,
                position=(540, 1400),
                size=(160, 220),
                color=(255, 220, 0, 255),
                line_width=10,
                rotation=180.0,
            ))
            overlays.append(OverlaySpec(
                overlay_type=OverlayType.BADGE,
                start_time=0.0,
                end_time=duration,
                position=(540, 320),
                size=(440, 80),
                text="🔥 기간 한정 50% 반값",
                color=(235, 35, 35, 240),
                outline_color=(255, 255, 255, 255),
            ))

        return overlays

    def render_overlay_image(
        self,
        spec: OverlaySpec,
        canvas_size: Tuple[int, int] = (1080, 1920)
    ) -> Image.Image:
        """
        Renders a transparent RGBA PIL Image with the given overlay specification.
        """
        img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx, cy = spec.position
        w, h = spec.size

        if spec.overlay_type == OverlayType.CIRCLE:
            rx, ry = w // 2, h // 2
            d.ellipse(
                [cx - rx, cy - ry, cx + rx, cy + ry],
                outline=spec.color,
                width=spec.line_width,
            )

        elif spec.overlay_type == OverlayType.X:
            rx, ry = w // 2, h // 2
            pad = 8
            d.line([(cx - rx + pad, cy - ry + pad), (cx + rx - pad, cy + ry - pad)], fill=spec.color, width=spec.line_width)
            d.line([(cx + rx - pad, cy - ry + pad), (cx - rx + pad, cy + ry - pad)], fill=spec.color, width=spec.line_width)

        elif spec.overlay_type == OverlayType.CHECK:
            rx, ry = w // 2, h // 2
            pts = [
                (cx - rx + 15, cy),
                (cx - rx // 4, cy + ry - 15),
                (cx + rx - 10, cy - ry + 15)
            ]
            d.line(pts, fill=spec.color, width=spec.line_width, joint="curve")

        elif spec.overlay_type == OverlayType.UNDERLINE:
            rx, ry = w // 2, h // 2
            d.line([(cx - rx, cy), (cx + rx, cy)], fill=spec.color, width=spec.line_width)

        elif spec.overlay_type == OverlayType.HIGHLIGHT:
            rx, ry = w // 2, h // 2
            d.rounded_rectangle(
                [cx - rx, cy - ry, cx + rx, cy + ry],
                radius=12,
                fill=spec.color,
            )

        elif spec.overlay_type == OverlayType.BADGE:
            rx, ry = w // 2, h // 2
            d.rounded_rectangle(
                [cx - rx, cy - ry, cx + rx, cy + ry],
                radius=ry,
                fill=spec.color,
                outline=spec.outline_color,
                width=3,
            )
            if spec.text:
                try:
                    font = ImageFont.truetype(self.font_path, int(h * 0.46))
                except Exception:
                    font = ImageFont.load_default()
                d.text((cx, cy), spec.text, fill=(255, 255, 255, 255), font=font, anchor="mm")

        elif spec.overlay_type == OverlayType.BURST:
            rx, ry = w // 2, h // 2
            pts = []
            num_points = 12
            for i in range(num_points * 2):
                radius = rx if i % 2 == 0 else rx * 0.58
                angle = i * math.pi / num_points
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                pts.append((px, py))
            d.polygon(pts, fill=spec.color, outline=spec.outline_color)

        elif spec.overlay_type == OverlayType.ARROW:
            # Vertical pointer arrow pointing down
            rx, ry = w // 2, h // 2
            shaft_w = spec.line_width * 2
            head_h = ry
            d.rectangle([cx - shaft_w // 2, cy - ry, cx + shaft_w // 2, cy], fill=spec.color)
            head_pts = [(cx - rx, cy), (cx + rx, cy), (cx, cy + ry)]
            d.polygon(head_pts, fill=spec.color, outline=spec.outline_color)

        return img

    def build_ass_overlay_dialogues(
        self,
        specs: List[OverlaySpec],
        scene_abs_start: float,
        format_time_fn,
    ) -> List[str]:
        """
        Builds ASS Dialogue lines (Layer 1) for overlays so they integrate natively
        into the subtitle stream with microsecond sync and zero extra FFmpeg complexity.
        """
        lines = []
        for s in specs:
            t_start = format_time_fn(scene_abs_start + s.start_time)
            t_end   = format_time_fn(scene_abs_start + s.end_time)
            cx, cy  = s.position

            if s.overlay_type == OverlayType.BADGE and s.text:
                txt = (
                    rf"{{\an5\pos({cx},{cy})\bord4\3c&H000000&\c&H0000E5FF&"
                    rf"\fscx90\fscy90\t(0,60,\fscx108\fscy108)\t(60,120,\fscx100\fscy100)}}"
                    rf"【 {s.text} 】"
                )
                lines.append(f"Dialogue: 1,{t_start},{t_end},PopSub,,0,0,0,,{txt}\n")

            elif s.overlay_type == OverlayType.BURST:
                txt = (
                    rf"{{\an5\pos({cx},{cy})\c&H0000FFFF&\fscx60\fscy60"
                    rf"\t(0,60,\fscx125\fscy125)\t(60,120,\fscx100\fscy100)}}💥"
                )
                lines.append(f"Dialogue: 1,{t_start},{t_end},PopSub,,0,0,0,,{txt}\n")

            elif s.overlay_type == OverlayType.CHECK:
                txt = (
                    rf"{{\an5\pos({cx},{cy})\c&H00AAFFAA&\fscx70\fscy70"
                    rf"\t(0,50,\fscx120\fscy120)\t(50,110,\fscx100\fscy100)}}✅"
                )
                lines.append(f"Dialogue: 1,{t_start},{t_end},PopSub,,0,0,0,,{txt}\n")

            elif s.overlay_type == OverlayType.X:
                txt = (
                    rf"{{\an5\pos({cx},{cy})\c&H000040FF&\fscx70\fscy70"
                    rf"\t(0,40,\fscx125\fscy125)\t(40,100,\fscx100\fscy100)}}❌"
                )
                lines.append(f"Dialogue: 1,{t_start},{t_end},PopSub,,0,0,0,,{txt}\n")

            elif s.overlay_type == OverlayType.ARROW:
                txt = (
                    rf"{{\an5\pos({cx},{cy})\c&H0000E5FF&\fscx80\fscy80"
                    rf"\t(0,60,\fscx115\fscy115)\t(60,120,\fscx100\fscy100)}}👇"
                )
                lines.append(f"Dialogue: 1,{t_start},{t_end},PopSub,,0,0,0,,{txt}\n")

        return lines
