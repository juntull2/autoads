"""
compare_v9_v10.py — AutoAds v9 vs v10 Before/After Comparison Sheet Generator
===============================================================================
Extracts 16 frames at evenly-spaced timestamps from both v9 and v10 final renders,
then assembles a single high-resolution 16-tile comparison sheet:

  Left column  → v9 (baseline, before)
  Right column → v10 (AutoAds engine, after)

Each row = same timestamp, labeled with the scene/purpose info.

Output:
  retiragen_compare_v9_v10.jpg  — 16 rows x 2 columns at 540x960 per cell

Usage:
    python compare_v9_v10.py
    python compare_v9_v10.py --v9 path/to/v9.mp4 --v10 path/to/v10.mp4
    python compare_v9_v10.py --frames 8
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

# ── Path resolution ────────────────────────────────────────────────────────

_curr = os.path.abspath(os.path.dirname(__file__))


def _resolve(primary: str, fallbacks: list) -> str:
    if os.path.exists(primary):
        return primary
    for fb in fallbacks:
        if os.path.exists(fb):
            return fb
    return primary


WORKDIR = os.environ.get(
    "AUTOADS_WORKDIR",
    _resolve(
        r"C:\Users\5700G\Desktop\레티라겐 레퍼런스",
        [r"C:\Users\임준모\Desktop\레티라겐 레퍼런스", os.path.join(_curr, "build_output")]
    )
)

FONT_PATH = _resolve(
    r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf",
    [
        r"C:\Users\임준모\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
)

# Scene purpose labels — proportional to video duration
SCENE_LABELS = [
    "HOOK", "PROBLEM", "AGITATION", "PROOF", "AGITATION",
    "SOLUTION", "BENEFIT", "PRODUCT", "BENEFIT", "CTA",
]

PURPOSE_COLORS = {
    "HOOK":       (255, 220,  80),
    "PROBLEM":    (255,  90,  90),
    "AGITATION":  (255, 140,  40),
    "SOLUTION":   (100, 220, 160),
    "PROOF":      (100, 180, 255),
    "BENEFIT":    (200, 120, 255),
    "PRODUCT":    ( 80, 200, 255),
    "CTA":        (255, 200,  60),
}


def get_video_duration(path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def extract_frame(video_path: str, timestamp: float, out_path: str,
                  width: int = 540, height: int = 960) -> bool:
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{timestamp:.3f}",
        "-i", video_path,
        "-frames:v", "1",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
        "-q:v", "2",
        out_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0 and os.path.exists(out_path)


def load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def build_comparison_sheet(
    v9_path: str,
    v10_path: str,
    out_path: str,
    num_frames: int = 16,
    cell_w: int = 540,
    cell_h: int = 960,
    margin: int = 8,
    header_h: int = 64,
    row_label_w: int = 82,
) -> None:
    """
    Build a side-by-side v9/v10 comparison tile sheet.
    Layout per row:  [row label] | [v9 frame] | [v10 frame]
    """
    dur_v9  = get_video_duration(v9_path)
    dur_v10 = get_video_duration(v10_path)
    dur     = min(dur_v9, dur_v10)

    ts_start = 0.5
    ts_end   = dur - 0.5
    timestamps = [
        ts_start + i * (ts_end - ts_start) / max(num_frames - 1, 1)
        for i in range(num_frames)
    ]

    tmp_dir = os.path.join(os.path.dirname(out_path), "_compare_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    total_w = row_label_w + margin + (cell_w + margin) * 2
    total_h = header_h + num_frames * (cell_h + margin) + margin + 40
    canvas  = Image.new("RGB", (total_w, total_h), (16, 16, 22))
    draw    = ImageDraw.Draw(canvas)

    font_hdr  = load_font(30)
    font_row  = load_font(19)
    font_lbl  = load_font(17)
    font_ts   = load_font(14)

    x_offsets = [
        row_label_w + margin,
        row_label_w + margin + cell_w + margin,
    ]

    # Column headers
    hdr_data = [
        ("v9  (Before — Baseline)", (50, 50, 75), (190, 190, 220)),
        ("v10 (After — AutoAds Engine)", (28, 80, 52), (90, 255, 170)),
    ]
    for (lbl, bg, fg), xo in zip(hdr_data, x_offsets):
        draw.rectangle([xo, 0, xo + cell_w, header_h], fill=bg)
        bbox = draw.textbbox((0, 0), lbl, font=font_hdr)
        tw = bbox[2] - bbox[0]
        tx = xo + max((cell_w - tw) // 2, 8)
        ty = (header_h - (bbox[3] - bbox[1])) // 2
        draw.text((tx + 2, ty + 2), lbl, font=font_hdr, fill=(0, 0, 0))
        draw.text((tx, ty), lbl, font=font_hdr, fill=fg)

    # Vertical divider
    div_x = row_label_w + margin + cell_w + margin // 2
    draw.line([(div_x, 0), (div_x, total_h)], fill=(70, 70, 95), width=2)

    # Row label background
    draw.rectangle([0, 0, row_label_w, total_h], fill=(20, 20, 30))

    print(f">> Extracting {num_frames} frames x 2 videos...")

    for row_i, ts in enumerate(timestamps):
        y_top = header_h + row_i * (cell_h + margin)

        scene_idx = min(
            int(ts / dur * len(SCENE_LABELS)),
            len(SCENE_LABELS) - 1
        )
        purpose = SCENE_LABELS[scene_idx]
        p_color = PURPOSE_COLORS.get(purpose, (200, 200, 200))

        # Row label panel
        draw.rectangle([0, y_top, row_label_w, y_top + cell_h], fill=(18, 18, 28))
        badge_h = 26
        draw.rounded_rectangle(
            [4, y_top + 8, row_label_w - 4, y_top + 8 + badge_h],
            radius=5, fill=p_color
        )
        purpose_short = purpose[:4]
        bbox = draw.textbbox((0, 0), purpose_short, font=font_lbl)
        tx = 4 + (row_label_w - 8 - (bbox[2] - bbox[0])) // 2
        draw.text(
            (tx, y_top + 8 + (badge_h - (bbox[3] - bbox[1])) // 2),
            purpose_short, font=font_lbl, fill=(10, 10, 10)
        )
        draw.text((5, y_top + 42), f"#{row_i+1:02d}", font=font_ts, fill=(70, 70, 90))
        draw.text((5, y_top + cell_h - 24), f"{ts:.1f}s",
                  font=font_ts, fill=(130, 130, 160))

        for col_i, (vid_path, tag) in enumerate([(v9_path, "v9"), (v10_path, "v10")]):
            frame_path = os.path.join(tmp_dir, f"frame_{tag}_r{row_i:02d}.jpg")
            x_left = x_offsets[col_i]

            ok = extract_frame(vid_path, ts, frame_path, cell_w, cell_h)
            if ok:
                try:
                    img = Image.open(frame_path).convert("RGB")
                    canvas.paste(img, (x_left, y_top))
                except Exception as e:
                    draw.rectangle([x_left, y_top, x_left+cell_w, y_top+cell_h],
                                   fill=(40, 20, 20))
                    draw.text((x_left+10, y_top+10), f"Error",
                              font=font_ts, fill=(255, 80, 80))
            else:
                draw.rectangle([x_left, y_top, x_left+cell_w, y_top+cell_h],
                               fill=(28, 28, 28))
                draw.text((x_left+10, y_top+40), f"[Missing]\n{ts:.2f}s",
                          font=font_ts, fill=(100, 100, 100))

            # Version badge
            badge_bg  = (30, 80, 48) if col_i == 1 else (45, 45, 72)
            badge_txt = "v10" if col_i == 1 else "v9 "
            badge_fg  = (90, 255, 155) if col_i == 1 else (180, 180, 215)
            draw.rounded_rectangle(
                [x_left + 6, y_top + 6, x_left + 58, y_top + 28],
                radius=4, fill=badge_bg
            )
            draw.text((x_left + 10, y_top + 8), badge_txt,
                      font=font_ts, fill=badge_fg)

        print(f"  [{row_i+1:02d}/{num_frames}] {ts:.2f}s  {purpose}")

    # Footer
    fy = total_h - 38
    draw.rectangle([0, fy, total_w, total_h], fill=(12, 12, 18))
    footer = (
        f"AutoAds v9->v10 Comparison  |  "
        f"v9: {Path(v9_path).name}  |  v10: {Path(v10_path).name}  |  "
        f"{num_frames} frames  |  duration={dur:.1f}s"
    )
    draw.text((10, fy + 10), footer, font=font_ts, fill=(90, 90, 115))

    canvas.save(out_path, quality=93)
    print(f">> Comparison sheet saved: {out_path}")

    # Cleanup tmp
    for f in os.listdir(tmp_dir):
        try:
            os.remove(os.path.join(tmp_dir, f))
        except Exception:
            pass
    try:
        os.rmdir(tmp_dir)
    except Exception:
        pass


def find_video(workdir: str, patterns: list) -> str:
    for pat in patterns:
        p = os.path.join(workdir, pat)
        if os.path.exists(p):
            return p
    return None


def main():
    parser = argparse.ArgumentParser(
        description="AutoAds v9 vs v10 Before/After Comparison Sheet"
    )
    parser.add_argument("--v9",     default=None, help="Path to v9 final render mp4")
    parser.add_argument("--v10",    default=None, help="Path to v10 final render mp4")
    parser.add_argument("--out",    default=None, help="Output JPEG path")
    parser.add_argument("--frames", type=int, default=16, help="Number of comparison frames")
    args = parser.parse_args()

    v9_path = args.v9 or find_video(WORKDIR, [
        "retiragen_v9.mp4",
        "retiragen_hypit_v9.mp4",
        "retiragen_v9_meta_reels_fast.mp4",
    ])
    v10_path = args.v10 or find_video(WORKDIR, [
        "retiragen_v10_meta_reels_fast.mp4",
        "retiragen_v10_beauty_ads.mp4",
        "retiragen_v10_ugc.mp4",
        "retiragen_v10_aggressive_sales.mp4",
    ])

    # Fallback: scan workdir for any v9/v10 mp4
    if not v9_path:
        for f in sorted(os.listdir(WORKDIR)):
            if "v9" in f.lower() and f.endswith(".mp4"):
                v9_path = os.path.join(WORKDIR, f)
                break
    if not v10_path:
        for f in sorted(os.listdir(WORKDIR)):
            if "v10" in f.lower() and f.endswith(".mp4"):
                v10_path = os.path.join(WORKDIR, f)
                break

    if not v9_path or not os.path.exists(v9_path):
        print("ERROR: v9 video not found.")
        print(f"  Searched in: {WORKDIR}")
        print("  Use: python compare_v9_v10.py --v9 /path/to/v9.mp4 --v10 /path/to/v10.mp4")
        sys.exit(1)
    if not v10_path or not os.path.exists(v10_path):
        print("ERROR: v10 video not found.")
        print(f"  Searched in: {WORKDIR}")
        print("  Use: python compare_v9_v10.py --v9 /path/to/v9.mp4 --v10 /path/to/v10.mp4")
        sys.exit(1)

    out_path = args.out or os.path.join(WORKDIR, "retiragen_compare_v9_v10.jpg")

    print("=" * 70)
    print(">> AutoAds v9 vs v10 — Before/After Comparison Sheet")
    print(f"   v9  : {v9_path}")
    print(f"   v10 : {v10_path}")
    print(f"   Out : {out_path}")
    print(f"   Frames: {args.frames}")
    print("=" * 70)

    build_comparison_sheet(
        v9_path=v9_path,
        v10_path=v10_path,
        out_path=out_path,
        num_frames=args.frames,
    )

    print("=" * 70)
    print(">> Done.")


if __name__ == "__main__":
    main()
