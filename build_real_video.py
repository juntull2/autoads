"""
AdForge x Hypit: Retiragen Commercial Shortform Video Remastered
Builds agency-grade commercial 9:16 vertical video from clean raw assets:
- Model clips from C:\\Users\\5700G\\Desktop\\레티라겐\\윤라영님모델_소스
- UGC clips from C:\\Users\\5700G\\Desktop\\레티라겐\\xhs_sources
- Audio from Fish Audio S2.1 Pro in c:\\adforge\\temp_audio\\retiragen_pore_v2
- Motion graphics overlays (Warning target, Skin glow, 2-step Mechanism, 50% CTA)
- Pretendard-Black Safe Zone Subtitles (MarginV=480)
- Hypit SVML / SVRun native integration
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
MODEL_DIR = r"C:\Users\5700G\Desktop\레티라겐\윤라영님모델_소스"
XHS_DIR = r"C:\Users\5700G\Desktop\레티라겐\xhs_sources"
SFX_DIR = r"C:\Users\5700G\Desktop\효과음"
AUDIO_DIR = r"C:\adforge\temp_audio\retiragen_pore_v2"
TEMP_DIR = os.path.join(WORKDIR, "build_temp")
OVERLAY_DIR = os.path.join(TEMP_DIR, "overlays")
os.makedirs(OVERLAY_DIR, exist_ok=True)

FONT_BLACK = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Black.otf"
FONT_BOLD = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Bold.otf"

def find_sfx(kw):
    for root, dirs, files in os.walk(SFX_DIR):
        for f in files:
            if kw in f:
                return os.path.join(root, f)
    return None

def generate_overlays():
    print(">> Generating motion graphic overlay badges...")
    f_title = ImageFont.truetype(FONT_BLACK, 40)
    f_badge = ImageFont.truetype(FONT_BLACK, 34)

    # 1. Warning & Target
    img_warn = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d_warn = ImageDraw.Draw(img_warn)
    d_warn.rounded_rectangle([120, 260, 960, 360], radius=50, fill=(20, 10, 10, 220), outline=(255, 45, 45, 255), width=4)
    d_warn.text((540, 310), '⚠️ WARNING : 나비존 요철 & 피지 과다', fill=(255, 255, 255), font=f_title, anchor='mm')
    cx, cy, r = 540, 960, 160
    d_warn.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 50, 50, 240), width=5)
    d_warn.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], outline=(255, 255, 255, 255), width=3)
    d_warn.line([cx - r - 35, cy, cx - r + 25, cy], fill=(255, 50, 50, 255), width=4)
    d_warn.line([cx + r - 25, cy, cx + r + 35, cy], fill=(255, 50, 50, 255), width=4)
    d_warn.line([cx, cy - r - 35, cx, cy - r + 25], fill=(255, 50, 50, 255), width=4)
    d_warn.line([cx, cy + r - 25, cx, cy + r + 35], fill=(255, 50, 50, 255), width=4)
    p_warn = os.path.join(OVERLAY_DIR, "warn.png")
    img_warn.save(p_warn)

    # 2. Skin Glow Badge
    img_glow = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d_glow = ImageDraw.Draw(img_glow)
    d_glow.rounded_rectangle([180, 260, 900, 355], radius=45, fill=(10, 20, 30, 215), outline=(255, 230, 80, 255), width=3)
    d_glow.text((540, 307), '✨ [무보정 17호 깐달걀결 검증]', fill=(255, 245, 150), font=f_title, anchor='mm')
    def draw_sparkle(draw, x, y, size):
        draw.line([x - size, y, x + size, y], fill=(255, 255, 220, 240), width=3)
        draw.line([x, y - size, x, y + size], fill=(255, 255, 220, 240), width=3)
        draw.ellipse([x - size//3, y - size//3, x + size//3, y + size//3], fill=(255, 255, 255, 255))
    draw_sparkle(d_glow, 320, 780, 40)
    draw_sparkle(d_glow, 760, 840, 50)
    draw_sparkle(d_glow, 520, 710, 30)
    p_glow = os.path.join(OVERLAY_DIR, "glow.png")
    img_glow.save(p_glow)

    # 3. Mechanism Badges
    img_mech = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d_mech = ImageDraw.Draw(img_mech)
    d_mech.rounded_rectangle([70, 250, 1010, 345], radius=45, fill=(10, 25, 45, 225), outline=(0, 230, 255, 255), width=3)
    d_mech.text((540, 297), '🔬 스위스산 순수 레티놀 → 속피지선 바짝 건조', fill=(255, 255, 255), font=f_badge, anchor='mm')
    d_mech.rounded_rectangle([70, 365, 1010, 460], radius=45, fill=(40, 15, 30, 225), outline=(255, 65, 150, 255), width=3)
    d_mech.text((540, 412), '🧬 초저분자 300Da 콜라겐 → 진피 요철 꽉 채움', fill=(255, 255, 255), font=f_badge, anchor='mm')
    p_mech = os.path.join(OVERLAY_DIR, "mech.png")
    img_mech.save(p_mech)

    # 4. CTA Banner
    img_cta = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d_cta = ImageDraw.Draw(img_cta)
    d_cta.rounded_rectangle([150, 260, 930, 360], radius=50, fill=(240, 35, 35, 235), outline=(255, 255, 255, 255), width=4)
    d_cta.text((540, 310), '🔥 30일 기간 한정 50% 반값 할인', fill=(255, 255, 255), font=f_title, anchor='mm')
    p_cta = os.path.join(OVERLAY_DIR, "cta.png")
    img_cta.save(p_cta)

    return {"warn": p_warn, "glow": p_glow, "mech": p_mech, "cta": p_cta}

def get_audio_duration(p):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def main():
    print("=" * 70)
    print(">> Starting Retiragen Commercial Video Build Pipeline...")
    print("=" * 70)

    overlays = generate_overlays()

    # Define Scenes with exact Fish Audio files
    scenes = [
        {
            "id": 1,
            "audio": os.path.join(AUDIO_DIR, "scene_01.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 1.40, "text": "전 피부과 프락셀 안 받아도"},
                {"start": 1.40, "end": None, "text": "{\\c&H0000E6FF&\\fscx108\\fscy108}모공 요철 제로{\\c&H00FFFFFF&\\fscx100\\fscy100}예요!"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"), "ratio": 0.45, "punch": 1.00},
                {"asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"), "ratio": 0.55, "punch": 1.20}
            ],
            "sfx": [
                {"kw": "Finger Snap", "t": 0.0, "vol": -3},
                {"kw": "Whoosh Transition 1", "t": 1.4, "vol": -8}
            ]
        },
        {
            "id": 2,
            "audio": os.path.join(AUDIO_DIR, "scene_02.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 2.10, "text": "유명한 모공 앰플, 레티놀 크림 다 써봐도"},
                {"start": 2.10, "end": None, "text": "{\\c&H0000E6FF&\\fscx108\\fscy108}개기름 뜨고 화장 밀리고,{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"), "ratio": 0.48, "punch": 1.00},
                {"asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"), "ratio": 0.52, "punch": 1.18}
            ],
            "sfx": [
                {"kw": "Whoosh Transition 2", "t": 2.1, "vol": -8}
            ]
        },
        {
            "id": 3,
            "audio": os.path.join(AUDIO_DIR, "scene_03.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 2.00, "text": "심할 땐 피부가 아예 뒤집어지더라고요."},
                {"start": 2.00, "end": None, "text": "결국 {\\c&H0000E6FF&\\fscx108\\fscy108}나비존 요철만 푹 파였죠{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"), "ratio": 1.00, "punch": 1.12, "overlay": "warn"}
            ],
            "sfx": [
                {"kw": "Suspense 1", "t": 0.0, "vol": -5},
                {"kw": "쨍그랑", "t": 2.0, "vol": -8}
            ]
        },
        {
            "id": 4,
            "audio": os.path.join(AUDIO_DIR, "scene_04.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 2.40, "text": "근데 귤껍질 같던 볼살 매끈해진 거 보이세요?"},
                {"start": 2.40, "end": None, "text": "전 {\\c&H0000E6FF&\\fscx108\\fscy108}레티놀 크림을 삼키기{\\c&H00FFFFFF&\\fscx100\\fscy100} 시작했어요."}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4"), "ratio": 0.49, "punch": 1.15},
                {"asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"), "ratio": 0.51, "punch": 1.08}
            ],
            "sfx": [
                {"kw": "Whoosh Transition 1", "t": 0.0, "vol": -8},
                {"kw": "Ding Sound Effect.mp3", "t": 2.4, "vol": -8}
            ]
        },
        {
            "id": 5,
            "audio": os.path.join(AUDIO_DIR, "scene_05.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": None, "text": "{\\c&H0000E6FF&\\fscx112\\fscy112}엥?! 레티놀 크림을 삼켜요?!{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"), "ratio": 1.00, "punch": 1.25}
            ],
            "sfx": [
                {"kw": "느낌표 물음표", "t": 0.0, "vol": -5}
            ]
        },
        {
            "id": 6,
            "audio": os.path.join(AUDIO_DIR, "scene_06.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 3.40, "text": "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도"},
                {"start": 3.40, "end": None, "text": "피지가 터지기는커녕 {\\c&H0000E6FF&\\fscx108\\fscy108}요철이 점점 팽팽하게 차오르는 거예요!{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"), "ratio": 0.48, "punch": 1.00},
                {"asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\14.mp4"), "ratio": 0.52, "punch": 1.18}
            ],
            "sfx": [
                {"kw": "뽁", "t": 0.0, "vol": -6},
                {"kw": "Ding Ding Sound Effect", "t": 3.4, "vol": -8}
            ]
        },
        {
            "id": 7,
            "audio": os.path.join(AUDIO_DIR, "scene_07.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 2.20, "text": "그렇게 한 달 정도 꾸준히 먹어보니,"},
                {"start": 2.20, "end": None, "text": "이젠 프라이머 없이도 {\\c&H0000E6FF&\\fscx108\\fscy108}매끈한 17호 피부{\\c&H00FFFFFF&\\fscx100\\fscy100}가 됐어요."}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"), "ratio": 0.45, "punch": 1.00},
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"), "ratio": 0.55, "punch": 1.18, "overlay": "glow"}
            ],
            "sfx": [
                {"kw": "Whoosh Transition 1", "t": 0.0, "vol": -8},
                {"kw": "Ding Sound Effect.mp3", "t": 2.2, "vol": -8}
            ]
        },
        {
            "id": 8,
            "audio": os.path.join(AUDIO_DIR, "scene_08.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 4.50, "text": "속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리!"},
                {"start": 4.50, "end": None, "text": "와, {\\c&H0000E6FF&\\fscx108\\fscy108}피부과 프락셀 레이저가 피부에 이식된 느낌?{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4"), "ratio": 0.50, "punch": 1.00, "overlay": "mech"},
                {"asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"), "ratio": 0.50, "punch": 1.18}
            ],
            "sfx": [
                {"kw": "Finger Snap", "t": 0.0, "vol": -6},
                {"kw": "Ding Ding Sound Effect", "t": 4.5, "vol": -8}
            ]
        },
        {
            "id": 9,
            "audio": os.path.join(AUDIO_DIR, "scene_09.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 1.70, "text": "하루 종일 자연광 맞아도"},
                {"start": 1.70, "end": None, "text": "{\\c&H0000E6FF&\\fscx108\\fscy108}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&\\fscx100\\fscy100}이 쭈욱 유지돼요!"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"), "ratio": 0.45, "punch": 1.00},
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"), "ratio": 0.55, "punch": 1.20, "overlay": "glow"}
            ],
            "sfx": [
                {"kw": "Whoosh Transition 1", "t": 0.0, "vol": -8},
                {"kw": "Ding Sound Effect.mp3", "t": 1.7, "vol": -8}
            ]
        },
        {
            "id": 10,
            "audio": os.path.join(AUDIO_DIR, "scene_10.wav"),
            "sub_chunks": [
                {"start": 0.00, "end": 2.40, "text": "{\\c&H0000E6FF&\\fscx108\\fscy108}30일 기간 한정 반값 할인!{\\c&H00FFFFFF&\\fscx100\\fscy100}"},
                {"start": 2.40, "end": None, "text": "궁금한 분들은 아래 비밀링크 참고해 보세요~"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"), "ratio": 0.47, "punch": 1.00, "overlay": "cta"},
                {"asset": os.path.join(MODEL_DIR, "따봉.mp4"), "ratio": 0.53, "punch": 1.18}
            ],
            "sfx": [
                {"kw": "Mouse Click", "t": 0.0, "vol": -4},
                {"kw": "Ding Ding Sound Effect", "t": 2.4, "vol": -6}
            ]
        }
    ]

    # Measure actual audio durations
    total_audio_dur = 0.0
    for s in scenes:
        s["dur"] = get_audio_duration(s["audio"])
        total_audio_dur += s["dur"]
        for ch in s["sub_chunks"]:
            if ch["end"] is None:
                ch["end"] = s["dur"]

    print(f">> Total Audio Duration: {total_audio_dur:.2f}s across {len(scenes)} scenes.")

    # 1. Render Video Cuts
    cut_files = []
    cut_idx = 0
    for s in scenes:
        scene_dur = s["dur"]
        for c in s["cuts"]:
            cut_idx += 1
            dur = scene_dur * c["ratio"]
            punch = c.get("punch", 1.0)
            overlay_key = c.get("overlay")
            out_cut = os.path.join(TEMP_DIR, f"cut_{cut_idx:02d}.mp4")

            base_w, base_h = 1080, 1920
            scaled_w = int(round(base_w * punch))
            scaled_h = int(round(base_h * punch))
            scaled_w = scaled_w if scaled_w % 2 == 0 else scaled_w + 1
            scaled_h = scaled_h if scaled_h % 2 == 0 else scaled_h + 1

            vf = [
                f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase",
                f"crop={base_w}:{base_h}:(in_w-out_w)/2:(in_h-out_h)/2",
                "fps=30"
            ]

            if overlay_key and overlay_key in overlays:
                ov_path = overlays[overlay_key].replace("\\", "/")
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", "0.2", "-t", f"{dur:.3f}",
                    "-stream_loop", "-1", "-i", c["asset"],
                    "-i", ov_path,
                    "-t", f"{dur:.3f}",
                    "-filter_complex", f"[0:v]{','.join(vf)}[v0];[v0][1:v]overlay=0:0[vout]",
                    "-map", "[vout]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-an", out_cut
                ]
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", "0.2", "-t", f"{dur:.3f}",
                    "-stream_loop", "-1", "-i", c["asset"],
                    "-t", f"{dur:.3f}",
                    "-vf", ",".join(vf),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-an", out_cut
                ]
            subprocess.run(cmd, capture_output=True, check=True)
            cut_files.append(out_cut)
            print(f"  [Cut {cut_idx:02d}] Scene {s['id']} ({dur:.2f}s, punch={punch}x)")

    # 2. Concat Cuts
    vcat_list = os.path.join(TEMP_DIR, "vcat.txt")
    with open(vcat_list, "w", encoding="utf-8") as f:
        for cp in cut_files:
            f.write(f"file '{cp.replace(chr(92), '/')}'\n")

    raw_video = os.path.join(TEMP_DIR, "video_cuts_concat.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vcat_list,
        "-c", "copy", raw_video
    ], capture_output=True, check=True)

    # 3. Mix Audio with SFX & ducked BGM
    print(">> Mixing Voice, Layered SFX, and BGM...")
    master_voice = AudioSegment.empty()
    curr_ms = 0
    sfx_overlays = []

    for s in scenes:
        seg = AudioSegment.from_file(s["audio"])
        master_voice += seg
        for cue in s.get("sfx", []):
            fpath = find_sfx(cue["kw"])
            if fpath and os.path.exists(fpath):
                sfx_snd = AudioSegment.from_file(fpath) + cue.get("vol", -6)
                cue_pos_ms = curr_ms + int(cue["t"] * 1000)
                sfx_overlays.append((cue_pos_ms, sfx_snd))
        curr_ms += len(seg)

    total_len_ms = len(master_voice)
    full_audio = master_voice
    for pos_ms, snd in sfx_overlays:
        full_audio = full_audio.overlay(snd, position=pos_ms)

    bgm_path = find_sfx("Its Jazz 30 sec")
    if bgm_path and os.path.exists(bgm_path):
        bgm = AudioSegment.from_file(bgm_path) - 26
        bgm_looped = bgm * (int(total_len_ms / len(bgm)) + 2)
        bgm_trimmed = bgm_looped[:total_len_ms].fade_in(400).fade_out(1500)
        full_audio = full_audio.overlay(bgm_trimmed)

    mixed_audio_path = os.path.join(WORKDIR, "master_audio.wav")
    full_audio.export(mixed_audio_path, format="wav")
    print(f"  -> Exported master_audio.wav ({len(full_audio)/1000:.2f}s)")

    # 4. Generate Safe Zone Subtitles (ASS)
    ass_path = os.path.join(WORKDIR, "subtitles.ass")
    print(">> Generating Pretendard-Black Safe Zone Subtitles...")
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Pretendard-Black,64,&H00FFFFFF,&H000000FF,&H00181818,&H90000000,-1,0,0,0,100,100,0,0,1,3.2,3.5,2,40,40,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    base_time = 0.0

    def fmt_time(t):
        hrs = int(t // 3600)
        mins = int((t % 3600) // 60)
        secs = int(t % 60)
        cs = int(round((t - int(t)) * 100))
        if cs >= 100:
            cs = 99
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

    for s in scenes:
        for ch in s["sub_chunks"]:
            t_start = fmt_time(base_time + ch["start"])
            t_end = fmt_time(base_time + ch["end"])
            events.append(f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{ch['text']}")
        base_time += s["dur"]

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")
    print(f"  -> Exported subtitles.ass")

    # 5. Burn Subtitles into Master Visual CFR Video
    master_visual_path = os.path.join(WORKDIR, "master_visual.mp4")
    print(f">> Burning Subtitles into master_visual.mp4...")
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")

    cmd_burn = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-vf", f"subtitles='{escaped_ass}'",
        "-r", "30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an",
        master_visual_path
    ]
    subprocess.run(cmd_burn, capture_output=True, check=True)
    print("  -> Burned master_visual.mp4 successfully.")

    # 6. Calculate Exact Frame Boundary for Hypit Timeline
    visual_dur = get_audio_duration(master_visual_path)
    total_frames = int(round(visual_dur * 30.0))
    hypit_dur_sec = total_frames / 30.0
    print(f">> Hypit Exact Frame Duration: {total_frames} frames ({hypit_dur_sec:.3f}s)")

    # 7. Update main.svml
    svml_path = os.path.join(WORKDIR, "main.svml")
    svml_content = f"""<?svml using="@hypit/markup@1"?>
<svml>
  <import as="time" from="@hypit/timeline-author@1"/>
  <import as="spatial" from="@hypit/spatial@1"/>
  <import as="film" from="@hypit/film@1"/>
  <import as="media" from="@hypit/media@1"/>
  <import as="pipeline" from="@hypit/media-pipeline@1"/>
  <import as="media-track" from="@hypit/media-track@1"/>
  <import as="audio" from="@hypit/audio-track@1"/>
  <import as="render" from="@hypit/render-hyperframes@1"/>
  <import as="style" source="./main.svs"/>

  <time:Clock id="clock" frame-rate="30"/>
  <time:Timeline id="timeline" clock={{clock}} end="{hypit_dur_sec:.3f}s"/>
  <spatial:Canvas id="canvas" width="1080" height="1920"/>
  <spatial:Frame id="full" within={{canvas}} left="0%" top="0%" right="100%" bottom="100%"/>

  <media:Video id="raw-video" src="./master_visual.mp4"/>
  <media:Audio id="raw-audio" src="./master_audio.wav"/>

  <pipeline:Normalize id="norm-video" source={{raw-video}} clock={{clock}}
    video="primary-moving" audio="none" span-authority="video"/>
  <pipeline:Normalize id="norm-audio" source={{raw-audio}} clock={{clock}}
    video="none" audio="default" span-authority="audio"/>

  <media-track:Track id="video-layer" timeline={{timeline.timeline}} canvas={{canvas}}>
    <media-track:Item id="main-video" media={{norm-video.media}} frame={{full}}
      at="0s" for="{hypit_dur_sec:.3f}s" appearance={{style.media.full}}/>
  </media-track:Track>

  <audio:Track id="audio-layer" timeline={{timeline.timeline}}>
    <audio:Item id="master-sound" source={{norm-audio.media}} at="0s" for="{hypit_dur_sec:.3f}s" playback="once"/>
  </audio:Track>

  <film:Film id="main" canvas={{canvas}} timeline={{timeline.timeline}} appearance={{style.film.main}}>
    <film:Track source={{video-layer.visual}}/>
    <film:Track source={{audio-layer.audio}}/>
  </film:Film>

  <render:Video id="final" composition={{main.composition}} timeline={{timeline.timeline}}/>
</svml>
"""
    with open(svml_path, "w", encoding="utf-8") as f:
        f.write(svml_content)
    print("  -> Updated main.svml")

    # 8. Run Hypit Build
    print(">> Running hypit build ./main.svrun...")
    cmd_build = ["hypit", "build", "./main.svrun"]
    res = subprocess.run(cmd_build, cwd=WORKDIR, capture_output=True, text=True, shell=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

    # 9. Copy or Export Final Commercial Video to retiragen_shortform_hypit.mp4
    final_output = os.path.join(WORKDIR, "retiragen_shortform_hypit.mp4")
    print(f">> Exporting final master video to {final_output}...")
    # Hypit outputs build artifacts or we can mux the master_visual.mp4 + master_audio.wav into the pristine retiragen_shortform_hypit.mp4
    cmd_export = [
        "ffmpeg", "-y",
        "-i", master_visual_path,
        "-i", mixed_audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_export, capture_output=True, check=True)
    print(f">> Final commercial shortform ready: {final_output}")

    # 10. Generate 16-frame Verification Tile Sheet
    tile_output = os.path.join(WORKDIR, "retiragen_hypit_tile16.jpg")
    cmd_tile = [
        "hypit", "media", "tile", final_output,
        "--frames", "16", "--columns", "4",
        "--to", tile_output
    ]
    subprocess.run(cmd_tile, capture_output=True, check=True, shell=True)
    print(f">> Verification Tile Sheet generated: {tile_output}")

if __name__ == "__main__":
    main()
