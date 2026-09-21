"""
Retiragen Remaster v3: High-readability Jalnan 2 Subtitles, Moderate SFX, Rich Transitions & Animations
"""

import os
import sys
import json
import math
import subprocess
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
BUILD_DIR = os.path.join(WORKDIR, "build_temp_v3")
OVERLAY_DIR = os.path.join(BUILD_DIR, "overlays")
os.makedirs(OVERLAY_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"

def find_sfx(kw):
    for root, dirs, files in os.walk(SFX_DIR):
        for f in files:
            if kw in f:
                return os.path.join(root, f)
    return None

def get_audio_duration(p):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

# 1. Generate Rich Overlays
def generate_rich_overlays():
    print(">> Generating 10 Rich Animation Overlays...")
    f_top = ImageFont.truetype(FONT_JALNAN, 38)
    f_lg = ImageFont.truetype(FONT_JALNAN, 40)
    f_md = ImageFont.truetype(FONT_JALNAN, 34)
    f_sm = ImageFont.truetype(FONT_JALNAN, 28)

    def draw_star(draw, x, y, r, color):
        draw.polygon([(x, y - r), (x + r*0.25, y - r*0.25), (x + r, y), (x + r*0.25, y + r*0.25), (x, y + r), (x - r*0.25, y + r*0.25), (x - r, y), (x - r*0.25, y - r*0.25)], fill=color)

    def base_canvas():
        img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Persistent Top Hook Bar (Safe area top, sleek glassmorphism)
        d.rounded_rectangle([180, 130, 900, 220], radius=45, fill=(15, 15, 25, 235), outline=(255, 60, 100, 255), width=3)
        d.ellipse([215, 165, 235, 185], fill=(255, 50, 50, 255))
        d.text((550, 175), '[ 피부과 대신 삼키는 레티놀? ]', fill=(255, 255, 255), font=f_top, anchor='mm')
        return img, d

    overlays = {}

    # Scene 1: Hook Sparkles
    img1, d1 = base_canvas()
    draw_star(d1, 260, 850, 36, (255, 120, 200, 240))
    draw_star(d1, 820, 800, 42, (255, 230, 80, 240))
    p1 = os.path.join(OVERLAY_DIR, 'ov_01.png')
    img1.save(p1)
    overlays['scene_01'] = p1

    # Scene 2: Stress Badge
    img2, d2 = base_canvas()
    d2.rounded_rectangle([160, 250, 920, 340], radius=45, fill=(35, 15, 15, 230), outline=(255, 80, 80, 255), width=3)
    d2.text((540, 295), '[ EMERGENCY ] 개기름 폭발 & 메이크업 들뜸', fill=(255, 255, 255), font=f_md, anchor='mm')
    p2 = os.path.join(OVERLAY_DIR, 'ov_02.png')
    img2.save(p2)
    overlays['scene_02'] = p2

    # Scene 3: Warning & Target Radar
    img3, d3 = base_canvas()
    d3.rounded_rectangle([120, 250, 960, 345], radius=45, fill=(25, 10, 10, 235), outline=(255, 45, 45, 255), width=4)
    # Draw vector warning triangle with !
    d3.polygon([(180, 320), (205, 270), (230, 320)], fill=(255, 50, 50))
    d3.text((205, 303), '!', fill=(255, 255, 255), font=f_md, anchor='mm')
    d3.text((560, 297), 'WARNING : 나비존 요철 & 피지 과다', fill=(255, 255, 255), font=f_lg, anchor='mm')
    cx, cy, r = 540, 960, 160
    d3.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 50, 50, 240), width=5)
    d3.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], outline=(255, 255, 255, 255), width=3)
    d3.line([cx - r - 35, cy, cx - r + 25, cy], fill=(255, 50, 50, 255), width=4)
    d3.line([cx + r - 25, cy, cx + r + 35, cy], fill=(255, 50, 50, 255), width=4)
    d3.line([cx, cy - r - 35, cx, cy - r + 25], fill=(255, 50, 50, 255), width=4)
    d3.line([cx, cy + r - 25, cx, cy + r + 35], fill=(255, 50, 50, 255), width=4)
    p3 = os.path.join(OVERLAY_DIR, 'ov_03.png')
    img3.save(p3)
    overlays['scene_03'] = p3

    # Scene 4: Secret & Solution
    img4, d4 = base_canvas()
    d4.rounded_rectangle([160, 250, 920, 340], radius=45, fill=(15, 25, 35, 230), outline=(0, 200, 255, 255), width=3)
    d4.text((540, 295), '[ SECRET ] 바르는 대신 \'삼키는\' 레티놀?!', fill=(255, 255, 255), font=f_md, anchor='mm')
    p4 = os.path.join(OVERLAY_DIR, 'ov_04.png')
    img4.save(p4)
    overlays['scene_04'] = p4

    # Scene 5: Comic Shock Bubble
    img5, d5 = base_canvas()
    d5.rounded_rectangle([140, 250, 940, 355], radius=50, fill=(40, 10, 45, 235), outline=(255, 230, 50, 255), width=4)
    d5.text((540, 302), '[ SHOCK ] 엥?! 레티놀을 삼켜요?!', fill=(255, 240, 80), font=f_lg, anchor='mm')
    p5 = os.path.join(OVERLAY_DIR, 'ov_05.png')
    img5.save(p5)
    overlays['scene_05'] = p5

    # Scene 6: Outdoor Activity Proof
    img6, d6 = base_canvas()
    d6.rounded_rectangle([140, 250, 940, 340], radius=45, fill=(20, 20, 30, 230), outline=(255, 180, 50, 255), width=3)
    d6.text((540, 295), '[ REAL TEST ] 땡볕 야외활동에도 피지 ZERO', fill=(255, 255, 255), font=f_md, anchor='mm')
    p6 = os.path.join(OVERLAY_DIR, 'ov_06.png')
    img6.save(p6)
    overlays['scene_06'] = p6

    # Scene 7: 17호 깐달걀결 검증
    img7, d7 = base_canvas()
    d7.rounded_rectangle([170, 250, 910, 345], radius=45, fill=(15, 20, 35, 230), outline=(255, 230, 80, 255), width=3)
    d7.text((540, 297), '[ 무보정 17호 깐달걀결 검증 ]', fill=(255, 245, 140), font=f_lg, anchor='mm')
    draw_star(d7, 320, 780, 40, (255, 255, 220, 240))
    draw_star(d7, 760, 840, 50, (255, 240, 150, 240))
    p7 = os.path.join(OVERLAY_DIR, 'ov_07.png')
    img7.save(p7)
    overlays['scene_07'] = p7

    # Scene 8: 2-step Mechanism
    img8, d8 = base_canvas()
    d8.rounded_rectangle([70, 245, 1010, 335], radius=45, fill=(10, 25, 45, 230), outline=(0, 230, 255, 255), width=3)
    d8.text((540, 290), '[STEP 1] 스위스산 순수 레티놀 → 속피지선 바짝 건조', fill=(255, 255, 255), font=f_md, anchor='mm')
    d8.rounded_rectangle([70, 350, 1010, 440], radius=45, fill=(40, 15, 30, 230), outline=(255, 65, 150, 255), width=3)
    d8.text((540, 395), '[STEP 2] 초저분자 300Da 콜라겐 → 진피 요철 꽉 채움', fill=(255, 255, 255), font=f_md, anchor='mm')
    p8 = os.path.join(OVERLAY_DIR, 'ov_08.png')
    img8.save(p8)
    overlays['scene_08'] = p8

    # Scene 9: Long-lasting Smooth Skin
    img9, d9 = base_canvas()
    d9.rounded_rectangle([170, 250, 910, 345], radius=45, fill=(15, 20, 35, 230), outline=(255, 230, 80, 255), width=3)
    d9.text((540, 297), '[ 깐달걀 피부 ] 하루 종일 무너짐 없는 광채결', fill=(255, 255, 255), font=f_md, anchor='mm')
    draw_star(d9, 300, 800, 40, (255, 255, 220, 240))
    draw_star(d9, 780, 750, 45, (255, 230, 100, 240))
    p9 = os.path.join(OVERLAY_DIR, 'ov_09.png')
    img9.save(p9)
    overlays['scene_09'] = p9

    # Scene 10: CTA Banner & Animated Downward Arrows
    img10, d10 = base_canvas()
    d10.rounded_rectangle([140, 250, 940, 350], radius=50, fill=(240, 35, 35, 235), outline=(255, 255, 255, 255), width=4)
    d10.text((540, 300), '[ 30일 기간 한정 ] 50% 반값 특별할인', fill=(255, 255, 255), font=f_lg, anchor='mm')
    d10.rounded_rectangle([220, 1370, 860, 1460], radius=45, fill=(255, 225, 0, 245), outline=(0, 0, 0, 255), width=3)
    for x in [260, 290, 790, 820]:
        d10.polygon([(x - 12, 1405), (x + 12, 1405), (x, 1425)], fill=(10, 10, 10))
    d10.text((540, 1415), '아래 비밀링크 바로가기', fill=(10, 10, 10), font=f_md, anchor='mm')
    p10 = os.path.join(OVERLAY_DIR, 'ov_10.png')
    img10.save(p10)
    overlays['scene_10'] = p10

    return overlays

def main():
    print("=" * 70)
    print(">> Retiragen Shortform Remaster v3 Starting...")
    print("=" * 70)

    overlays = generate_rich_overlays()

    # Scene definitions with exact Fish Audio WAVs and punchy cuts
    scenes = [
        {
            "id": 1,
            "audio": os.path.join(AUDIO_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.76, "text": "전 피부과 프락셀 안 받아도"},
                {"start": 1.76, "end": None, "text": "{\\c&H0000FFFF&\\fscx115\\fscy115}모공 요철 제로{\\c&H00FFFFFF&\\fscx100\\fscy100}예요!"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"), "t": 1.76, "punch": 1.00, "flash": False},
                {"asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"), "t": 1.45, "punch": 1.20, "flash": False}
            ],
            "overlay": overlays["scene_01"]
        },
        {
            "id": 2,
            "audio": os.path.join(AUDIO_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.28, "text": "유명한 모공 앰플,"},
                {"start": 1.28, "end": 2.64, "text": "{\\c&H0000FFFF&\\fscx112\\fscy112}레티놀 크림{\\c&H00FFFFFF&\\fscx100\\fscy100} 다 써봐도"},
                {"start": 2.64, "end": None, "text": "{\\c&H0055FFFF&\\fscx112\\fscy112}개기름 뜨고 화장 밀리고,{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"), "t": 2.20, "punch": 1.00, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"), "t": 2.19, "punch": 1.18, "flash": False}
            ],
            "overlay": overlays["scene_02"]
        },
        {
            "id": 3,
            "audio": os.path.join(AUDIO_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.92, "text": "심할 땐 피부가 {\\c&H005555FF&}뒤집어지더라고요.{\\c&H00FFFFFF&}"},
                {"start": 1.92, "end": None, "text": "결국 {\\c&H0000FFFF&\\fscx115\\fscy115}나비존 요철만 푹 파였죠{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"), "t": 4.15, "punch": 1.12, "flash": True}
            ],
            "overlay": overlays["scene_03"]
        },
        {
            "id": 4,
            "audio": os.path.join(AUDIO_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.54, "text": "근데 귤껍질 같던 볼살 {\\c&H0000FFFF&}매끈해진 거 보이세요?{\\c&H00FFFFFF&}"},
                {"start": 2.54, "end": None, "text": "전 {\\c&H0000FFFF&\\fscx115\\fscy115}레티놀 크림을 삼키기{\\c&H00FFFFFF&\\fscx100\\fscy100} 시작했어요."}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4"), "t": 2.54, "punch": 1.15, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"), "t": 2.34, "punch": 1.08, "flash": False}
            ],
            "overlay": overlays["scene_04"]
        },
        {
            "id": 5,
            "audio": os.path.join(AUDIO_DIR, "scene_05.wav"),
            "sub_cues": [
                {"start": 0.00, "end": None, "text": "{\\c&H0000FFFF&\\fscx120\\fscy120}엥?! 레티놀 크림을 삼켜요?!{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"), "t": 1.88, "punch": 1.25, "flash": True}
            ],
            "overlay": overlays["scene_05"]
        },
        {
            "id": 6,
            "audio": os.path.join(AUDIO_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.66, "text": "저도 처음엔 안 믿었는데,"},
                {"start": 1.66, "end": 3.00, "text": "아니 땡볕 야구장을 다녀와도"},
                {"start": 3.00, "end": 4.42, "text": "피지가 터지기는커녕"},
                {"start": 4.42, "end": None, "text": "{\\c&H0000FFFF&\\fscx115\\fscy115}요철이 팽팽하게 차오르는 거예요!{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"), "t": 3.30, "punch": 1.00, "flash": True},
                {"asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\14.mp4"), "t": 3.78, "punch": 1.18, "flash": False}
            ],
            "overlay": overlays["scene_06"]
        },
        {
            "id": 7,
            "audio": os.path.join(AUDIO_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.76, "text": "그렇게 한 달 정도 꾸준히 먹어보니,"},
                {"start": 1.76, "end": 2.92, "text": "이젠 프라이머 없이도"},
                {"start": 2.92, "end": None, "text": "{\\c&H0000FFFF&\\fscx118\\fscy118}매끈한 17호 피부{\\c&H00FFFFFF&\\fscx100\\fscy100}가 됐어요!"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"), "t": 2.20, "punch": 1.00, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"), "t": 2.66, "punch": 1.20, "flash": False}
            ],
            "overlay": overlays["scene_07"]
        },
        {
            "id": 8,
            "audio": os.path.join(AUDIO_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.38, "text": "{\\c&H00FFFF00&}속피지선부터 바짝 말려주고{\\c&H00FFFFFF&}"},
                {"start": 2.38, "end": 4.50, "text": "{\\c&H00FF88FF&}초저분자 콜라겐을 메워주는 원리!{\\c&H00FFFFFF&}"},
                {"start": 4.50, "end": 6.50, "text": "와, 피부과 프락셀 레이저가"},
                {"start": 6.50, "end": None, "text": "{\\c&H0000FFFF&\\fscx115\\fscy115}피부 자체에 이식된 느낌?!{\\c&H00FFFFFF&\\fscx100\\fscy100}"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4"), "t": 4.50, "punch": 1.00, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"), "t": 4.49, "punch": 1.18, "flash": False}
            ],
            "overlay": overlays["scene_08"]
        },
        {
            "id": 9,
            "audio": os.path.join(AUDIO_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.70, "text": "하루 종일 자연광 맞아도"},
                {"start": 1.70, "end": None, "text": "{\\c&H0000FFFF&\\fscx115\\fscy115}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&\\fscx100\\fscy100}이 쭈욱 유지돼요!"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"), "t": 1.70, "punch": 1.00, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"), "t": 2.11, "punch": 1.20, "flash": False}
            ],
            "overlay": overlays["scene_09"]
        },
        {
            "id": 10,
            "audio": os.path.join(AUDIO_DIR, "scene_10.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.40, "text": "{\\c&H0000FFFF&\\fscx120\\fscy120}30일 기간 한정 반값 할인!{\\c&H00FFFFFF&\\fscx100\\fscy100}"},
                {"start": 2.40, "end": None, "text": "궁금한 분들은 {\\c&H0000FFFF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~"}
            ],
            "cuts": [
                {"asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"), "t": 2.50, "punch": 1.00, "flash": True},
                {"asset": os.path.join(MODEL_DIR, "따봉.mp4"), "t": 2.62, "punch": 1.18, "flash": False}
            ],
            "overlay": overlays["scene_10"]
        }
    ]

    # Measure exact audio lengths
    total_audio_dur = 0.0
    for s in scenes:
        dur = get_audio_duration(s["audio"])
        s["dur"] = dur
        total_audio_dur += dur
        for sc in s["sub_cues"]:
            if sc["end"] is None:
                sc["end"] = dur

    print(f">> Total Audio Duration: {total_audio_dur:.3f}s")

    # 2. Render Video Cuts with Overlays and White Flash Transitions
    cut_files = []
    cut_idx = 0
    for s in scenes:
        ov_path = s["overlay"].replace("\\", "/")
        for c in s["cuts"]:
            cut_idx += 1
            dur = c["t"]
            punch = c.get("punch", 1.0)
            flash = c.get("flash", False)
            out_cut = os.path.join(BUILD_DIR, f"cut_{cut_idx:02d}.mp4")

            base_w, base_h = 1080, 1920
            scaled_w = int(round(base_w * punch))
            scaled_h = int(round(base_h * punch))
            scaled_w = scaled_w if scaled_w % 2 == 0 else scaled_w + 1
            scaled_h = scaled_h if scaled_h % 2 == 0 else scaled_h + 1

            vf = [
                f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase",
                f"crop={base_w}:{base_h}:(in_w-out_w)/2:(in_h-out_h)/2"
            ]
            if flash:
                vf.append("fade=t=in:st=0:d=0.08:color=white")
            vf.append("fps=30")

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
            subprocess.run(cmd, capture_output=True, check=True)
            cut_files.append(out_cut)
            print(f"  [Cut {cut_idx:02d}] Scene {s['id']:02d} ({dur:.2f}s, punch={punch:.2f}x, flash={flash})")

    # Concat cuts
    vcat_txt = os.path.join(BUILD_DIR, "vcat.txt")
    with open(vcat_txt, "w", encoding="utf-8") as f:
        for cp in cut_files:
            f.write(f"file '{cp.replace(chr(92), '/')}'\n")

    raw_video = os.path.join(BUILD_DIR, "raw_cuts_concat.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vcat_txt,
        "-c", "copy", raw_video
    ], capture_output=True, check=True)
    print(">> All 18 cuts concatenated.")

    # 3. Audio Mastering: 5 Moderate SFX + Ducked Jazz BGM
    print(">> Mixing Audio: Fish Audio Voice + 5 Clean SFX + Ducked Jazz BGM...")
    master_voice = AudioSegment.empty()
    curr_ms = 0
    sfx_events = []

    # 5 specific high-impact SFX
    sfx_snap = find_sfx("Finger Snap")
    sfx_suspense = find_sfx("Suspense 1")
    sfx_ding = find_sfx("Ding Sound Effect.mp3")
    sfx_pop = find_sfx("느낌표 물음표")
    sfx_click = find_sfx("Mouse Click")

    sfx_schedule = [
        {"pos_sec": 0.0, "path": sfx_snap, "vol": -4},
        {"pos_sec": 8.0, "path": sfx_suspense, "vol": -6},
        {"pos_sec": 14.3, "path": sfx_ding, "vol": -6},
        {"pos_sec": 16.7, "path": sfx_pop, "vol": -5},
        {"pos_sec": 43.5, "path": sfx_click, "vol": -4}
    ]

    for s in scenes:
        seg = AudioSegment.from_file(s["audio"])
        master_voice += seg

    total_len_ms = len(master_voice)
    full_audio = master_voice

    for ev in sfx_schedule:
        if ev["path"] and os.path.exists(ev["path"]):
            snd = AudioSegment.from_file(ev["path"]) + ev["vol"]
            pos_ms = int(ev["pos_sec"] * 1000)
            full_audio = full_audio.overlay(snd, position=pos_ms)

    bgm_path = find_sfx("Its Jazz 30 sec")
    if bgm_path and os.path.exists(bgm_path):
        bgm = AudioSegment.from_file(bgm_path) - 26
        bgm_looped = bgm * (int(total_len_ms / len(bgm)) + 2)
        bgm_trimmed = bgm_looped[:total_len_ms].fade_in(400).fade_out(1500)
        full_audio = full_audio.overlay(bgm_trimmed)

    master_audio_path = os.path.join(WORKDIR, "master_audio.wav")
    full_audio.export(master_audio_path, format="wav")
    print(f"  -> Exported master_audio.wav ({len(full_audio)/1000:.2f}s)")

    # 4. Generate High-Readability ASS Subtitles (Jalnan 2, MarginV=380, Outline=8)
    print(">> Generating High-Readability ASS Subtitles in Jalnan 2...")
    ass_path = os.path.join(WORKDIR, "subtitles.ass")
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Jalnan 2,78,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8.0,4.5,2,40,40,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def fmt_time(t):
        hrs = int(t // 3600)
        mins = int((t % 3600) // 60)
        secs = int(t % 60)
        cs = int(round((t - int(t)) * 100))
        if cs >= 100:
            cs = 99
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

    events = []
    base_time = 0.0
    for s in scenes:
        for cue in s["sub_cues"]:
            t0 = fmt_time(base_time + cue["start"])
            t1 = fmt_time(base_time + cue["end"])
            events.append(f"Dialogue: 0,{t0},{t1},Default,,0,0,0,,{cue['text']}")
        base_time += s["dur"]

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")
    print(f"  -> Exported subtitles.ass ({len(events)} cues)")

    # 5. Burn Subtitles into CFR 30fps Video
    master_visual_path = os.path.join(WORKDIR, "master_visual.mp4")
    print(">> Burning Subtitles into master_visual.mp4...")
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
    print(f"  -> Burned master_visual.mp4")

    # 6. Exact 30fps Duration & Hypit SVML Update
    visual_dur = get_audio_duration(master_visual_path)
    total_frames = int(round(visual_dur * 30.0))
    hypit_dur_sec = total_frames / 30.0
    print(f">> Hypit Duration: {total_frames} frames ({hypit_dur_sec:.3f}s)")

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

    # 7. Final Output Export
    final_output = os.path.join(WORKDIR, "retiragen_shortform_hypit.mp4")
    print(f">> Muxing Master Visual and Audio to {final_output}...")
    cmd_export = [
        "ffmpeg", "-y",
        "-i", master_visual_path,
        "-i", master_audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_export, capture_output=True, check=True)
    print(f">> Master Video Exported: {final_output}")

    # 8. Hypit 16-Frame Tile Sheet Generation
    tile_output = os.path.join(WORKDIR, "retiragen_hypit_tile16.jpg")
    tile_cmd_str = f'hypit media tile "{final_output}" --frames 16 --columns 4 --to "{tile_output}"'
    subprocess.run(tile_cmd_str, capture_output=True, check=True, shell=True)
    print(f">> 16-Frame Tile Sheet Exported: {tile_output}")

if __name__ == "__main__":
    main()
