"""
Retiragen Remaster v4: 
1. 100% Perfect Voice-to-Video Sync (20 tailored cuts matching script 1:1)
2. ZERO Textboxes - Clean Floating Variety Subtitles with Dynamic Pop Animation
3. "샤방샤방" Radiant Beauty Sparkles (Champagne & Diamond Stars on Glowing Skin)
4. Smooth Scene Transitions (White Flash Bloom & Dissolves)
5. 5 Clean, Purposeful Sound Effects + Balanced Jazz BGM
"""

import os
import sys
import json
import math
import subprocess
from PIL import Image, ImageDraw, ImageFilter
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
BASE_DIR = r"C:\Users\5700G\Desktop\레티라겐"
SFX_DIR = r"C:\Users\5700G\Desktop\효과음"
AUDIO_DIR = r"C:\adforge\temp_audio\retiragen_pore_v2"
BUILD_DIR = os.path.join(WORKDIR, "build_temp_v4")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks")
SPARKLE_DIR = os.path.join(BUILD_DIR, "sparkles")
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPARKLE_DIR, exist_ok=True)

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

# Step 1: Ensure Sparkles are generated
def ensure_sparkles():
    if len(os.listdir(SPARKLE_DIR)) >= 90:
        print(">> Sparkle frames already exist.")
        return
    print(">> Generating 90 high-end sparkle frames...")
    subprocess.run(["python", os.path.join(WORKDIR, "generate_sparkles.py")], check=True)

def main():
    print("=" * 70)
    print(">> Retiragen Remaster v4 (Flawless Sync & Beauty Aesthetic) Starting...")
    print("=" * 70)

    ensure_sparkles()

    # 10 Audio Scenes with Exact Cuts Tailored to Spoken Words
    # Total runtime: ~48.37s
    scene_defs = [
        # Scene 1 (3.21s): "전 피부과 프락셀 안 받아도 모공 요철 제로예요."
        {
            "id": 1,
            "audio": os.path.join(AUDIO_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.76, "text": "전 피부과 프락셀 안 받아도"},
                {"start": 1.76, "end": 3.21, "text": "{\\c&H0033EEFF&}모공 요철 제로{\\c&H00FFFFFF&}예요!"}
            ],
            "cuts": [
                {
                    "name": "01_smile",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 0.0, "dur": 3.21,
                    "punch": 1.05, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 2 (4.39s): "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고,"
        {
            "id": 2,
            "audio": os.path.join(AUDIO_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.28, "text": "유명한 모공 앰플,"},
                {"start": 1.28, "end": 2.64, "text": "{\\c&H0088FFFF&}레티놀 크림{\\c&H00FFFFFF&} 다 써봐도"},
                {"start": 2.64, "end": 4.39, "text": "{\\c&H0055AAFF&}개기름 뜨고 화장 밀리고,{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "02_mirror_cream",
                    "asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 2.10,
                    "punch": 1.10, "sparkles": False, "flash": True
                },
                {
                    "name": "03_oil_paper",
                    "asset": os.path.join(BASE_DIR, "기름종이.mp4"),
                    "start": 1.0, "dur": 2.29,
                    "punch": 1.05, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 3 (4.15s): "심할 땐 피부가 아예 뒤집어지더라고요. 결국 나비존 요철만 푹 파였죠"
        {
            "id": 3,
            "audio": os.path.join(AUDIO_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.00, "text": "심할 땐 피부가 {\\c&H005555FF&}뒤집어지더라고요.{\\c&H00FFFFFF&}"},
                {"start": 2.00, "end": 4.15, "text": "결국 {\\c&H0033EEFF&}나비존 요철만 푹 파였죠{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "04_annoyed",
                    "asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"),
                    "start": 1.5, "dur": 2.00,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "05_pore_closeup",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"),
                    "start": 2.5, "dur": 2.15,
                    "punch": 1.15, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 4 (4.88s): "근데 귤껍질 같던 볼살 매끈해진 거 보이세요? 전 레티놀 크림을 삼키기 시작했어요."
        {
            "id": 4,
            "audio": os.path.join(AUDIO_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.45, "text": "근데 귤껍질 같던 볼살 {\\c&H0033EEFF&}매끈해진 거 보이세요?{\\c&H00FFFFFF&}"},
                {"start": 2.45, "end": 4.88, "text": "전 {\\c&H0033EEFF&}레티놀 크림을 삼키기{\\c&H00FFFFFF&} 시작했어요."}
            ],
            "cuts": [
                {
                    "name": "06_secret_cheek",
                    "asset": os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4"),
                    "start": 0.0, "dur": 2.45,
                    "punch": 1.15, "sparkles": True, "flash": True
                },
                {
                    "name": "07_pill_palm",
                    "asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"),
                    "start": 0.3, "dur": 2.43,
                    "punch": 1.08, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 5 (1.88s): "엥? 레티놀 크림을 삼켜요?"
        {
            "id": 5,
            "audio": os.path.join(AUDIO_DIR, "scene_05.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.88, "text": "{\\c&H0033EEFF&}엥?! 레티놀 크림을 삼켜요?!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "08_shocked_phone",
                    "asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.88,
                    "punch": 1.25, "sparkles": False, "flash": True
                }
            ]
        },
        # Scene 6 (7.08s): "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 점점 더 팽팽하게 차오르는 거예요!"
        {
            "id": 6,
            "audio": os.path.join(AUDIO_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.66, "text": "저도 처음엔 안 믿었는데,"},
                {"start": 1.66, "end": 3.00, "text": "아니 땡볕 야구장을 다녀와도"},
                {"start": 3.00, "end": 4.42, "text": "피지가 터지기는커녕"},
                {"start": 4.42, "end": 7.08, "text": "{\\c&H0033EEFF&}요철이 팽팽하게 차오르는 거예요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "09_hesitant",
                    "asset": os.path.join(MODEL_DIR, "고민.mp4"),
                    "start": 0.5, "dur": 1.66,
                    "punch": 1.10, "sparkles": False, "flash": True
                },
                {
                    "name": "10_sun_heat",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\14.mp4"),
                    "start": 2.0, "dur": 2.76,
                    "punch": 1.15, "sparkles": False, "flash": False
                },
                {
                    "name": "11_skin_recovery_3d",
                    "asset": os.path.join(BASE_DIR, "새살 차오르기.mp4"),
                    "start": 1.0, "dur": 2.66,
                    "punch": 1.18, "sparkles": True, "flash": True
                }
            ]
        },
        # Scene 7 (4.86s): "그렇게 한 달 정도 꾸준히 먹어보니, 이젠 프라이머 없이도 매끈한 17호 피부가 됐어요."
        {
            "id": 7,
            "audio": os.path.join(AUDIO_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.80, "text": "그렇게 한 달 정도 꾸준히 먹어보니,"},
                {"start": 1.80, "end": 3.00, "text": "이젠 프라이머 없이도"},
                {"start": 3.00, "end": 4.86, "text": "{\\c&H0033EEFF&}매끈한 17호 피부{\\c&H00FFFFFF&}가 됐어요!"}
            ],
            "cuts": [
                {
                    "name": "12_taking_pill",
                    "asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"),
                    "start": 2.0, "dur": 2.00,
                    "punch": 1.05, "sparkles": False, "flash": True
                },
                {
                    "name": "13_shade17_skin",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업2 - Trim.mp4"),
                    "start": 0.0, "dur": 2.86,
                    "punch": 1.15, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 8 (8.99s): "알고 보니 속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리라는데, 와, 피부과 프락셀 레이저가 피부 자체에 이식된 느낌?"
        {
            "id": 8,
            "audio": os.path.join(AUDIO_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.40, "text": "{\\c&H0033EEFF&}속피지선부터 바짝 말려주고{\\c&H00FFFFFF&}"},
                {"start": 2.40, "end": 4.80, "text": "{\\c&H00FFAAFF&}초저분자 콜라겐을 메워주는 원리!{\\c&H00FFFFFF&}"},
                {"start": 4.80, "end": 6.80, "text": "와, 피부과 프락셀 레이저가"},
                {"start": 6.80, "end": 8.99, "text": "{\\c&H0033EEFF&}피부 자체에 이식된 느낌?!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "14_sebum_dry_3d",
                    "asset": os.path.join(BASE_DIR, "피지,모낭 없애는.mp4"),
                    "start": 0.5, "dur": 2.40,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "15_collagen_mesh_3d",
                    "asset": os.path.join(BASE_DIR, "Collagen_fibers_repairing_skin_t…_202609041402.mp4"),
                    "start": 0.5, "dur": 2.40,
                    "punch": 1.15, "sparkles": True, "flash": False
                },
                {
                    "name": "16_laser_clinic",
                    "asset": os.path.join(BASE_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4"),
                    "start": 0.5, "dur": 2.00,
                    "punch": 1.10, "sparkles": False, "flash": False
                },
                {
                    "name": "17_cheek_touch",
                    "asset": os.path.join(MODEL_DIR, "환하게 인사하는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 2.19,
                    "punch": 1.15, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 9 (3.81s): "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요!"
        {
            "id": 9,
            "audio": os.path.join(AUDIO_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.80, "text": "하루 종일 자연광 맞아도"},
                {"start": 1.80, "end": 3.81, "text": "{\\c&H0033EEFF&}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&}이 쭈욱 유지돼요!"}
            ],
            "cuts": [
                {
                    "name": "18_daylight_skin",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"),
                    "start": 0.5, "dur": 1.80,
                    "punch": 1.15, "sparkles": True, "flash": True
                },
                {
                    "name": "19_daylight_smile",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 1.0, "dur": 2.01,
                    "punch": 1.20, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 10 (5.12s): "30일 기간 한정 반값 할인도 한다는데, 궁금한 분들은 아래 비밀링크 참고해 보세요"
        {
            "id": 10,
            "audio": os.path.join(AUDIO_DIR, "scene_10.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 2.50, "text": "{\\c&H0033EEFF&}30일 기간 한정 반값 할인!{\\c&H00FFFFFF&}"},
                {"start": 2.50, "end": 5.12, "text": "궁금한 분들은 {\\c&H0033EEFF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~"}
            ],
            "cuts": [
                {
                    "name": "20_product_macro",
                    "asset": os.path.join(BASE_DIR, "제품 확대샷.mp4"),
                    "start": 1.0, "dur": 2.50,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "21_cta_down_thumbs",
                    "asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"),
                    "start": 0.5, "dur": 2.62,
                    "punch": 1.10, "sparkles": False, "flash": False
                }
            ]
        }
    ]

    # Verify and compute exact total timeline
    print(">> Processing 21 Video Chunks with Dynamic Punch-in & Beauty Sparkles...")
    all_chunks = []
    chunk_idx = 0

    for s_idx, s in enumerate(scene_defs):
        s_dur = get_audio_duration(s["audio"])
        s["dur"] = s_dur
        # normalize sub_cues
        for sc in s["sub_cues"]:
            if sc["end"] is None or sc["end"] > s_dur:
                sc["end"] = s_dur

        for c_idx, c in enumerate(s["cuts"]):
            chunk_idx += 1
            chunk_file = os.path.join(CHUNK_DIR, f"chunk_{chunk_idx:02d}.mp4")
            all_chunks.append(chunk_file)

            # Build ffmpeg filter graph for this chunk
            # 1. Base scale + crop
            punch = c.get("punch", 1.0)
            target_w = int(1080 * punch)
            target_h = int(1920 * punch)
            if target_w % 2 != 0: target_w += 1
            if target_h % 2 != 0: target_h += 1

            # Base input
            filter_chains = []
            filter_chains.append(f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop=1080:1920[scaled]")
            curr_v = "[scaled]"

            # 2. Sparkles if enabled
            if c.get("sparkles", False):
                filter_chains.append(f"[1:v]fps=30[sp];{curr_v}[sp]overlay=0:0:shortest=1[sparkled]")
                curr_v = "[sparkled]"

            # 3. Transition: white flash bloom at entrance (0.08s)
            if c.get("flash", False):
                filter_chains.append(f"{curr_v}fade=t=in:st=0:d=0.08:color=white[flashed]")
                curr_v = "[flashed]"

            # Final format
            filter_chains.append(f"{curr_v}fps=30,format=yuv420p[out]")
            vf_str = ";".join(filter_chains)

            # Skip if already rendered
            if not os.path.exists(chunk_file) or os.path.getsize(chunk_file) == 0:
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(c["start"]),
                    "-t", str(c["dur"]),
                    "-i", c["asset"]
                ]
                if c.get("sparkles", False):
                    sp_pattern = os.path.join(SPARKLE_DIR, "sp_%03d.png")
                    cmd.extend(["-stream_loop", "-1", "-r", "30", "-i", sp_pattern])

                cmd.extend([
                    "-filter_complex", vf_str,
                    "-map", "[out]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-an",
                    chunk_file
                ])
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"   ✓ Chunk {chunk_idx:02d}: {c['name']} ({c['dur']:.2f}s) rendered.")
            else:
                print(f"   ✓ Chunk {chunk_idx:02d}: {c['name']} already exists.")

    # Concat all chunks
    print(">> Concatenating 21 chunks...")
    concat_list = os.path.join(BUILD_DIR, "chunks.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(f"file '{ch.replace('\\\\', '/')}'\n")

    raw_visual = os.path.join(BUILD_DIR, "raw_visual.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_visual
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)
    print(">> Raw visual concatenated successfully.")

    # Step 2: Build Master Audio
    print(">> Mixing Master Audio (Fish Audio TTS + Ducked Jazz BGM + 5 Meaningful SFX)...")
    master_narr = AudioSegment.empty()
    scene_offsets = []
    curr_offset = 0.0

    for s in scene_defs:
        scene_offsets.append(curr_offset)
        seg = AudioSegment.from_wav(s["audio"])
        master_narr += seg
        curr_offset += len(seg) / 1000.0

    total_len_ms = len(master_narr)
    total_dur_s = total_len_ms / 1000.0
    print(f"   Total Narration Duration: {total_dur_s:.2f}s")

    # BGM setup
    bgm_path = find_sfx("Its Jazz full.wav") or find_sfx("Its Jazz 30 sec.wav")
    if not bgm_path:
        bgm_path = os.path.join(SFX_DIR, r"1_BGM(일상)\Its Jazz 30 sec.wav")
    bgm = AudioSegment.from_wav(bgm_path) - 27 # -27dB ducking for clear narration
    loop_bgm = AudioSegment.empty()
    while len(loop_bgm) < total_len_ms + 2000:
        loop_bgm += bgm
    loop_bgm = loop_bgm[:total_len_ms].fade_in(400).fade_out(1500)

    # Base mix
    mix_audio = loop_bgm.overlay(master_narr)

    # 5 Purposeful SFX
    # 1. 0.00s: Opening Snap
    sfx_snap = find_sfx("Finger Snap") or find_sfx("snap")
    if sfx_snap:
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_snap)[:1000] - 8, position=0)

    # 2. Scene 3 + 2.0s: Suspense Riser (나비존 요철 파임)
    sfx_suspense = find_sfx("Suspense 1") or find_sfx("스릴러")
    if sfx_suspense:
        pos_ms = int((scene_offsets[2] + 2.0) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_suspense)[:2000] - 12, position=pos_ms)

    # 3. Scene 4 + 2.45s: Magic Chime (레티놀 삼키기 시작)
    sfx_ding = find_sfx("Ding Chime") or find_sfx("bell")
    if sfx_ding:
        pos_ms = int((scene_offsets[3] + 2.45) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_ding)[:1500] - 8, position=pos_ms)

    # 4. Scene 5 + 0.0s: Pop Accent (엥?! 삼켜요? 쇼크 리액션)
    sfx_pop = find_sfx("물음표") or find_sfx("pop")
    if sfx_pop:
        pos_ms = int(scene_offsets[4] * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_pop)[:1000] - 6, position=pos_ms)

    # 5. Scene 10 + 2.5s: Subtle Click (비밀링크 안내)
    sfx_click = find_sfx("Mouse Click") or find_sfx("클릭")
    if sfx_click:
        pos_ms = int((scene_offsets[9] + 2.5) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_click)[:800] - 10, position=pos_ms)

    master_audio_path = os.path.join(WORKDIR, "master_audio_v4.wav")
    mix_audio.export(master_audio_path, format="wav")
    print(f">> Master Audio exported to {master_audio_path}")

    # Step 3: Generate Dynamic Animated ASS Subtitles (NO BOXES, PURE VARIETY STYLE)
    print(">> Generating Dynamic Pop-Animated ASS Subtitles (Jalnan 2)...")
    ass_path = os.path.join(WORKDIR, "subtitles_v4.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
Title: Retiragen Shortform Pop Subtitles v4
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: VarietyPop,Jalnan 2,74,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,2.0,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for s_idx, s in enumerate(scene_defs):
            s_base = scene_offsets[s_idx]
            for cue in s["sub_cues"]:
                st = s_base + cue["start"]
                et = s_base + cue["end"]

                st_h = int(st // 3600)
                st_m = int((st % 3600) // 60)
                st_s = st % 60
                st_str = f"{st_h}:{st_m:02d}:{st_s:05.2f}"

                et_h = int(et // 3600)
                et_m = int((et % 3600) // 60)
                et_s = et % 60
                et_str = f"{et_h}:{et_m:02d}:{et_s:05.2f}"

                # Native ASS Pop Animation: starts at 85%, bounces to 110% in 120ms, settles to 100% in 220ms
                anim_prefix = "{\\fscx85\\fscy85\\t(0,120,\\fscx110\\fscy110)\\t(120,220,\\fscx100\\fscy100)}"
                f.write(f"Dialogue: 0,{st_str},{et_str},VarietyPop,,0,0,0,,{anim_prefix}{cue['text']}\n")

    print(f">> Subtitles saved to {ass_path}")

    # Step 4: Final Master Video Assembly (Burning Subtitles & Muxing Audio)
    print(">> Assembling Final Commercial Master Video...")
    final_mp4 = os.path.join(WORKDIR, "retiragen_shortform_hypit.mp4")
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    cmd_final = [
        "ffmpeg", "-y",
        "-i", raw_visual,
        "-i", master_audio_path,
        "-vf", f"subtitles='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_mp4
    ]
    subprocess.run(cmd_final, check=True)
    print(f"✅ Final Commercial Video Successfully Created at: {final_mp4}")

    # Step 5: Generate 16-Frame Tile Sheet for Visual Inspection
    tile_sheet = os.path.join(WORKDIR, "retiragen_hypit_tile16_final.jpg")
    tile_artifact = r"C:\Users\5700G\.gemini\antigravity-ide\brain\dbf7f899-383b-4576-bd82-ea14ebea7e97\retiragen_hypit_tile16_final.jpg"
    print(">> Generating 16-Frame Verification Tile Sheet with Hypit...")
    cmd_tile = f'hypit media tile "{final_mp4}" --frames 16 --columns 4 --to "{tile_sheet}"'
    subprocess.run(cmd_tile, shell=True, check=True)
    
    # Copy to artifact dir for instant view
    Image.open(tile_sheet).save(tile_artifact)
    print(f"✅ Verification Tile Sheet ready at: {tile_artifact}")

    # Step 6: Update Hypit SVML
    total_frames = int(round(total_dur_s * 30))
    svml_content = f"""<composition width="1080" height="1920" fps="30" duration="{total_dur_s:.3f}s">
  <video src="{final_mp4.replace('\\', '/')}" in="0s" out="{total_dur_s:.3f}s" />
  <audio src="{master_audio_path.replace('\\', '/')}" in="0s" out="{total_dur_s:.3f}s" />
</composition>
"""
    with open(os.path.join(WORKDIR, "main.svml"), "w", encoding="utf-8") as f:
        f.write(svml_content)
    print(">> Updated main.svml!")

if __name__ == "__main__":
    main()
