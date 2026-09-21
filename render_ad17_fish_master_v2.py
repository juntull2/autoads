"""
Master Rendering Pipeline for Retiragen ad17 Benchmark Video (V4 - Fully Calibrated with Whisper & Overlays):
- 22 Perfectly Calibrated Unique Cuts matching exact Whisper speech boundaries (Total: 47.361s)
- Realistic Graphic Overlays:
  - Cut 1: Instagram Q&A Question Sticker (@minji_beauty 님의 질문: 언니 피부 진짜 깐달걀 같아요ㅠㅠ 하얘진 비결이 뭐예요? 💖)
  - Cut 2: Clinic Expense Tag (피부과 프락셀 10회+ | 총 180만원 💸)
  - Cut 3: Date Stamp 1 (● 2025.07.03 프락셀 직후)
  - Cut 4: Date Stamp 2 (● 2025.08.15 화장 들뜸/피지)
  - Cut 11: Side-by-Side Dual Split Screen (비포 vs 애프터 2분할 비교 + 4px 화이트 라인 디바이더 + ✨ 별빛 파티클)
  - Cut 17: High-Spec USP Card (✨ 스위스 레티놀 + GPH 300Da 초저분자 콜라겐 27,000mg 꽉 채움! ✨) + hflip!
- CapCut PopSub Subtitle Burn (ad17_fish_subtitles_synced.ass, Jalnan 2, MarginV 340, Spring-Pop Bounce, Emojis)
- Master Audio: 100% Fish Audio TTS, zero camera microphone audio (-an), BGM ducked at -27dB, 6 SFX, and 1.41s Outro Hold!
"""

import os
import sys
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
ROOT_DIR = r"C:\Users\5700G\Desktop\레티라겐"
MODEL_DIR = r"C:\Users\5700G\Desktop\레티라겐\윤라영님모델_소스"
XHS_DIR = r"C:\Users\5700G\Desktop\레티라겐\xhs_sources"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17_fish")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks_conti")
SPLIT_DIR = os.path.join(BUILD_DIR, "split_frames_conti")
SPARKLE_DIR = os.path.join(WORKDIR, "build_temp_v9", "sparkles")
OVERLAY_DIR = os.path.join(BUILD_DIR, "overlays_conti")

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPLIT_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"

def resolve_asset(path):
    if os.path.exists(path):
        return path
    dirname = os.path.dirname(path)
    base = os.path.basename(path)
    if os.path.exists(dirname):
        for f in os.listdir(dirname):
            if base[:8].lower() in f.lower():
                return os.path.join(dirname, f)
    return path

def render_split_chunk(out_chunk_path, duration=3.350):
    if os.path.exists(out_chunk_path):
        try:
            p_res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', out_chunk_path], capture_output=True, text=True)
            if abs(float(p_res.stdout.strip()) - duration) < 0.05:
                return
        except Exception:
            pass
            
    print(f">> Pre-rendering Side-by-Side Dual Split Screen ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))
    
    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))
    f_tag = ImageFont.truetype(FONT_JALNAN, 36)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0,fps=30',
        '-an', f'{SPLIT_DIR}/left_%03d.png'
    ], capture_output=True, check=True)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:00', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0,fps=30',
        '-an', f'{SPLIT_DIR}/right_%03d.png'
    ], capture_output=True, check=True)
    
    for f in range(total_frames):
        lp = f'{SPLIT_DIR}/left_{f+1:03d}.png'
        rp = f'{SPLIT_DIR}/right_{f+1:03d}.png'
        if not os.path.exists(lp) or not os.path.exists(rp):
            continue
        img_l = Image.open(lp).convert('RGBA')
        img_r = Image.open(rp).convert('RGBA')
        
        sp_idx = (f % 90)
        sp_file = os.path.join(SPARKLE_DIR, f'sp_{sp_idx:03d}.png')
        if os.path.exists(sp_file):
            sp_img = Image.open(sp_file).convert('RGBA').crop((270, 0, 810, 1920))
            img_r = Image.alpha_composite(img_r, sp_img)
            
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        canvas.paste(img_l, (0, 0))
        canvas.paste(img_r, (540, 0))
        
        d = ImageDraw.Draw(canvas)
        # White center divider line
        d.line([(540, 0), (540, H)], fill=(255, 255, 255, 230), width=4)
        
        # Before Tag
        d.rounded_rectangle([195, 120, 345, 185], radius=16, fill=(40, 40, 50, 210), outline=(255, 100, 100, 240), width=2)
        d.text((270, 152), '비포', fill=(255, 120, 120), font=f_tag, anchor='mm')
        
        # After Tag
        d.rounded_rectangle([735, 120, 885, 185], radius=16, fill=(245, 140, 190, 240), outline=(255, 255, 255, 255), width=2)
        d.text((810, 152), '애프터', fill=(255, 255, 255), font=f_tag, anchor='mm')
        
        lbl_img = os.path.join(OVERLAY_DIR, "05_after_label.png")
        if os.path.exists(lbl_img):
            lbl = Image.open(lbl_img).convert('RGBA')
            canvas = Image.alpha_composite(canvas, lbl)
            
        canvas.convert('RGB').save(f'{SPLIT_DIR}/comp_{f:03d}.png')
        
    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{SPLIT_DIR}/comp_%03d.png',
        '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-an',
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Pre-rendered Split Chunk: {out_chunk_path}")


def render_all_cuts():
    split_chunk = os.path.join(CHUNK_DIR, "c11_split.mp4")
    render_split_chunk(split_chunk, duration=3.350)
    
    # 22 Cuts perfectly calibrated with Whisper Speech Boundaries (Total: 47.361s)
    cuts = [
        # Scene 1: Hook (0.00s ~ 1.35s, dur: 1.350)
        {
            "id": 1, "name": "c01_hook_greeting",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 인사하는 장면2 - Trim.mp4")),
            "ss": 0.0, "dur": 1.350, "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "01_insta_qna.png")
        },
        # Scene 2: Laser Agony & Flaking (1.35s ~ 7.95s, dur: 6.600)
        {
            "id": 2, "name": "c02_laser_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4")),
            "ss": 0.0, "dur": 2.350, "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "01_cost_tag.png")
        },
        {
            "id": 3, "name": "c03_powder_flaking_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "결혼준비_2_메이크업_파우더터치.mp4")),
            "ss": 0.5, "dur": 1.550, "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "02_date_stamp.png")
        },
        {
            "id": 4, "name": "c04_xhs_sebum_shine",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\17.mp4")),
            "ss": 1.0, "dur": 2.700, "zoom": True, "hflip": False
        },
        # Scene 3: Paradigm Shift & Concept (7.95s ~ 16.30s, dur: 8.350)
        {
            "id": 5, "name": "c05_model_confident",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "드루와.mp4")),
            "ss": 0.1, "dur": 1.400, "zoom": True, "hflip": False
        },
        {
            "id": 6, "name": "c06_model_smiling_point",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "따봉.mp4")),
            "ss": 0.5, "dur": 1.450, "zoom": True, "hflip": False
        },
        {
            "id": 7, "name": "c07_model_x_gesture",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "엑스.mp4")),
            "ss": 0.5, "dur": 2.350, "zoom": True, "hflip": False
        },
        {
            "id": 8, "name": "c08_model_worrying",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "답답해 - Trim.mp4")),
            "ss": 0.2, "dur": 1.350, "zoom": True, "hflip": False
        },
        {
            "id": 9, "name": "c09_pouring_pills_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 쏟아붓는.mp4")),
            "ss": 0.2, "dur": 1.800, "zoom": True, "hflip": False
        },
        # Scene 4: Shock Reaction (16.30s ~ 18.50s, dur: 2.200)
        {
            "id": 10, "name": "c10_shocked_phone",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4")),
            "ss": 0.2, "dur": 2.200, "zoom": True, "hflip": False
        },
        # Scene 5: Side-by-Side Before & After + Mechanism (18.50s ~ 29.90s, dur: 11.400)
        {
            "id": 11, "name": "c11_split",
            "asset": split_chunk,
            "ss": 0.0, "dur": 3.350, "zoom": False, "hflip": False, "prebuilt": True
        },
        {
            "id": 12, "name": "c12_collagen_matrix_3d",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "새살 차오르기 2.mp4")),
            "ss": 0.5, "dur": 3.000, "zoom": True, "hflip": False
        },
        {
            "id": 13, "name": "c13_sebum_control_broll",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\05.mp4")),
            "ss": 0.5, "dur": 3.100, "zoom": True, "hflip": False
        },
        {
            "id": 14, "name": "c14_glass_skin_after_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "여드름 애프터 1.mp4")),
            "ss": 0.5, "dur": 1.950, "zoom": True, "hflip": False
        },
        # Scene 6: High-Spec Ingredients & Product (29.90s ~ 40.05s, dur: 10.150)
        {
            "id": 15, "name": "c15_formula_macro_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 성분 소개.mp4")),
            "ss": 0.2, "dur": 3.350, "zoom": True, "hflip": False
        },
        {
            "id": 16, "name": "c16_product_closeup_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 확대샷.mp4")),
            "ss": 0.5, "dur": 2.250, "zoom": True, "hflip": False
        },
        {
            "id": 17, "name": "c17_package_hflip",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4")),
            "ss": 0.5, "dur": 2.250, "zoom": True, "hflip": True,
            "overlay": os.path.join(OVERLAY_DIR, "07_usp_card.png")
        },
        {
            "id": 18, "name": "c18_cheek_closeup",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4")),
            "ss": 0.3, "dur": 2.300, "zoom": True, "hflip": False
        },
        # Scene 7: Climax & Ending CTA + Outro Hold (40.05s ~ 47.361s, dur: 7.311)
        {
            "id": 19, "name": "c19_secret_whisper",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4")),
            "ss": 0.5, "dur": 1.450, "zoom": True, "hflip": False
        },
        {
            "id": 20, "name": "c20_model_taking_pill",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4")),
            "ss": 2.0, "dur": 1.950, "zoom": True, "hflip": False
        },
        {
            "id": 21, "name": "c21_pointing_cta",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4")),
            "ss": 0.2, "dur": 2.500, "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "08_cta_box.png")
        },
        {
            "id": 22, "name": "c22_outro_hold_smile",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4")),
            "ss": 0.3, "dur": 1.411, "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "08_cta_box.png")
        }
    ]
    
    rendered_chunks = []
    print(f">> Rendering {len(cuts)} balanced cuts (CRITICAL: -an applied to all chunks)...")
    for cut in cuts:
        chunk_out = os.path.join(CHUNK_DIR, f"{cut['name']}.mp4")
        dur = cut["dur"]
        ss = cut["ss"]
        asset = cut["asset"]
        
        if cut.get("prebuilt") and os.path.exists(cut["asset"]):
            rendered_chunks.append(cut["asset"])
            continue
            
        need_render = True
        if os.path.exists(chunk_out):
            try:
                p_res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', chunk_out], capture_output=True, text=True)
                cur_dur = float(p_res.stdout.strip())
                if abs(cur_dur - dur) < 0.05:
                    need_render = False
                    rendered_chunks.append(chunk_out)
            except Exception:
                pass
                
        if need_render:
            vf_filters = []
            vf_filters.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
            
            if cut.get("hflip"):
                vf_filters.append("hflip")
                
            if cut.get("zoom"):
                vf_filters.append(f"scale=eval=frame:w='1080*(1+0.15*t/{dur:.3f})':h='1920*(1+0.15*t/{dur:.3f})',crop=1080:1920")
                
            vf_filters.append("fps=30,tpad=stop_mode=clone:stop_duration=5")
            base_vf = ",".join(vf_filters)
            
            # Check overlay
            overlay_f = cut.get("overlay")
            if overlay_f and os.path.exists(overlay_f):
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(ss),
                    '-i', asset,
                    '-i', overlay_f,
                    '-filter_complex', f"[0:v]{base_vf}[base];[base][1:v]overlay=0:0:format=auto[v]",
                    '-map', '[v]',
                    '-t', str(dur),
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                    '-an',
                    chunk_out
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(ss),
                    '-i', asset,
                    '-vf', base_vf,
                    '-t', str(dur),
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                    '-an',
                    chunk_out
                ]
            subprocess.run(cmd, check=True, capture_output=True)
            rendered_chunks.append(chunk_out)
            print(f"   [{cut['id']:02d}/22] Rendered {cut['name']} (target: {dur:.3f}s, silent video)")
        else:
            print(f"   [{cut['id']:02d}/22] Reusing {cut['name']} (verified: {dur:.3f}s)")
            
    return rendered_chunks

def concat_and_burn():
    chunks = render_all_cuts()
    concat_txt = os.path.join(BUILD_DIR, "concat_list_v4.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in chunks:
            rel_p = os.path.relpath(c, BUILD_DIR).replace('\\', '/')
            f.write(f"file '{rel_p}'\n")
            
    raw_merged = os.path.join(BUILD_DIR, "raw_visual_merged_v4.mp4")
    print(">> Concatenating visual chunks...")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', "concat_list_v4.txt",
        '-c', 'copy', raw_merged
    ], cwd=BUILD_DIR, check=True, capture_output=True)
    
    probe_raw = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', raw_merged], capture_output=True, text=True)
    raw_dur = float(probe_raw.stdout.strip())
    print(f">> Merged Visual Track Duration: {raw_dur:.3f}s")
    
    master_audio = os.path.join(BUILD_DIR, "master_audio_fish.wav")
    ass_subs = os.path.join(BUILD_DIR, "ad17_fish_conti_subs.ass").replace('\\', '/').replace(':', '\\:')
    
    final_output = os.path.join(WORKDIR, "ad17_retiragen_fish_remastered.mp4")
    print(f">> Burning Perfectly Synced PopSub Subtitles & Muxing Master Audio into: {final_output}...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', raw_merged,
        '-i', master_audio,
        '-filter_complex', f"[0:v]subtitles='{ass_subs}'[v]",
        '-map', '[v]',
        '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '256k',
        final_output
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(">> FINAL CALIBRATED VIDEO EXPORTED SUCCESSFULLY!")
    
    probe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', final_output
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    final_dur = float(res.stdout.strip())
    print(f">> Final Video Duration: {final_dur:.3f}s")
    
    # 16-Tile Sheet
    tile_out = os.path.join(WORKDIR, "ad17_tile16_fish.jpg")
    step = final_dur / 17.0
    subprocess.run([
        'ffmpeg', '-y', '-i', final_output,
        '-vf', f"fps=1/{step:.3f},scale=270:480,tile=4x4",
        '-frames:v', '1', tile_out
    ], check=True, capture_output=True)
    print(f">> 16-Tile Sheet: {tile_out}")

if __name__ == "__main__":
    concat_and_burn()
