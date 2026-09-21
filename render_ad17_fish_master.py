"""
Master Rendering Pipeline for Retiragen ad17 Fish Remastered (V3 - Fixed Audio & Legible Font):
1. FISH AUDIO EXCLUSIVE AUDIO:
   - Chunk render commands MUST use '-an' so ZERO camera audio leaks into the video!
   - Final mux MUST use '-map 0:v:0 -map 1:a:0' to strictly mux Fish Audio TTS!
2. MAXIMUM LEGIBILITY SUBTITLES:
   - Jalnan 2 (68px, 5.0px solid black outline, 2.0px soft shadow, MarginV: 340)
   - Spring-pop bounce (90% -> 110% -> 100%)
3. BALANCED B-ROLL COMPOSITION (60% B-roll / 40% Model)
4. CLEAN TOP AREA (NO top banners, NO comment stickers)
5. OUTRO HOLD 1.22s (Zero truncation)
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
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks_v3")
SPLIT_DIR = os.path.join(BUILD_DIR, "split_frames")
SPARKLE_DIR = os.path.join(WORKDIR, "build_temp_v9", "sparkles")

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
            if base[:10].lower() in f.lower():
                return os.path.join(dirname, f)
    return path

def render_split_chunk(out_chunk_path, duration=2.60):
    if os.path.exists(out_chunk_path) and os.path.getsize(out_chunk_path) > 0:
        return
    print(f">> Pre-rendering Side-by-Side Dual Split Screen ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))
    
    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))
    f_tag = ImageFont.truetype(FONT_JALNAN, 36)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0',
        '-r', '30', '-an', f'{SPLIT_DIR}/left_%03d.png'
    ], capture_output=True, check=True)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:00', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0',
        '-r', '30', '-an', f'{SPLIT_DIR}/right_%03d.png'
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
        d.line([(540, 0), (540, H)], fill=(255, 255, 255, 220), width=4)
        
        d.rounded_rectangle([195, 120, 345, 185], radius=16, fill=(40, 40, 50, 210), outline=(255, 100, 100, 240), width=2)
        d.text((270, 152), '비포', fill=(255, 120, 120), font=f_tag, anchor='mm')
        
        d.rounded_rectangle([735, 120, 885, 185], radius=16, fill=(245, 140, 190, 240), outline=(255, 255, 255, 255), width=2)
        d.text((810, 152), '애프터', fill=(255, 255, 255), font=f_tag, anchor='mm')
        
        canvas.convert('RGB').save(f'{SPLIT_DIR}/comp_{f:03d}.png')
        
    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{SPLIT_DIR}/comp_%03d.png',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-an', # NO AUDIO
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Pre-rendered Split Chunk: {out_chunk_path}")


def render_all_cuts():
    split_chunk = os.path.join(CHUNK_DIR, "c10_split.mp4")
    render_split_chunk(split_chunk, duration=2.60)
    
    # 21 Balanced Cuts matching Fish Audio timeline (Exact Total: 47.361s)
    # 60% B-roll / 40% Model
    cuts = [
        # Scene 1: Opening Hook (0.000s ~ 1.269s, dur: 1.269)
        {
            "id": 1, "name": "c01_hook_greeting",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 인사하는 장면2 - Trim.mp4")),
            "ss": 0.0, "dur": 1.269, "zoom": True, "hflip": False
        },
        # Scene 2: Laser Agony & Flaking (1.344s ~ 7.903s, dur: 6.559)
        {
            "id": 2, "name": "c02_laser_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4")),
            "ss": 0.0, "dur": 2.100, "zoom": True, "hflip": False
        },
        {
            "id": 3, "name": "c03_powder_flaking_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "결혼준비_2_메이크업_파우더터치.mp4")),
            "ss": 0.5, "dur": 2.200, "zoom": True, "hflip": False
        },
        {
            "id": 4, "name": "c04_xhs_sebum_shine",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\17.mp4")),
            "ss": 1.0, "dur": 2.259, "zoom": True, "hflip": False
        },
        # Scene 3: Paradigm Shift & Concept (7.978s ~ 16.236s, dur: 8.258)
        {
            "id": 5, "name": "c05_model_confident",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "드루와.mp4")),
            "ss": 0.2, "dur": 1.800, "zoom": True, "hflip": False
        },
        {
            "id": 6, "name": "c06_skincare_cream_broll",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\03.mp4")),
            "ss": 0.5, "dur": 1.800, "zoom": True, "hflip": False
        },
        {
            "id": 7, "name": "c07_model_x_gesture",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "엑스.mp4")),
            "ss": 0.5, "dur": 2.200, "zoom": True, "hflip": False
        },
        {
            "id": 8, "name": "c08_pouring_pills_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 쏟아붓는.mp4")),
            "ss": 0.2, "dur": 2.458, "zoom": True, "hflip": False
        },
        # Scene 4: Shock Reaction (16.311s ~ 18.423s, dur: 2.112)
        {
            "id": 9, "name": "c09_shocked_phone",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4")),
            "ss": 0.2, "dur": 2.112, "zoom": True, "hflip": False
        },
        # Scene 5: Side-by-Side Before & After + Mechanism (18.498s ~ 29.828s, dur: 11.330)
        {
            "id": 10, "name": "c10_split",
            "asset": split_chunk,
            "ss": 0.0, "dur": 2.600, "zoom": False, "hflip": False, "prebuilt": True
        },
        {
            "id": 11, "name": "c11_sebum_control_broll",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\05.mp4")),
            "ss": 0.5, "dur": 2.200, "zoom": True, "hflip": False
        },
        {
            "id": 12, "name": "c12_collagen_matrix_3d",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "새살 차오르기 2.mp4")),
            "ss": 0.5, "dur": 2.400, "zoom": True, "hflip": False
        },
        {
            "id": 13, "name": "c13_model_taking_pill",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4")),
            "ss": 2.0, "dur": 2.100, "zoom": True, "hflip": False
        },
        {
            "id": 14, "name": "c14_glass_skin_after_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "여드름 애프터 1.mp4")),
            "ss": 0.5, "dur": 2.030, "zoom": True, "hflip": False
        },
        # Scene 6: High-Spec Ingredients & Product (29.903s ~ 39.945s, dur: 10.042)
        {
            "id": 15, "name": "c15_formula_macro_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 성분 소개.mp4")),
            "ss": 0.2, "dur": 1.800, "zoom": True, "hflip": False
        },
        {
            "id": 16, "name": "c16_product_closeup_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 확대샷.mp4")),
            "ss": 0.5, "dur": 2.400, "zoom": True, "hflip": False
        },
        {
            "id": 17, "name": "c17_package_hflip",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4")),
            "ss": 0.5, "dur": 3.200, "zoom": True, "hflip": True
        },
        {
            "id": 18, "name": "c18_cheek_closeup",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4")),
            "ss": 0.3, "dur": 2.642, "zoom": True, "hflip": False
        },
        # Scene 7: Climax & Ending CTA (40.020s ~ 47.361s, dur: 7.341)
        {
            "id": 19, "name": "c19_secret_whisper",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4")),
            "ss": 0.5, "dur": 2.200, "zoom": True, "hflip": False
        },
        {
            "id": 20, "name": "c20_pointing_cta",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4")),
            "ss": 0.2, "dur": 2.600, "zoom": True, "hflip": False
        },
        {
            "id": 21, "name": "c21_outro_hold_smile",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4")),
            "ss": 0.3, "dur": 3.170, "zoom": True, "hflip": False
        }
    ]
    
    rendered_chunks = []
    print(f">> Rendering {len(cuts)} balanced cuts (CRITICAL: -an applied to all chunks)...")
    for cut in cuts:
        chunk_out = os.path.join(CHUNK_DIR, f"{cut['name']}.mp4")
        dur = cut["dur"]
        ss = cut["ss"]
        asset = cut["asset"]
        
        # Check if prebuilt or already rendered with accurate duration
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
            vf_str = ",".join(vf_filters)
            
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(ss),
                '-i', asset,
                '-vf', vf_str,
                '-t', str(dur),
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-an', # CRITICAL: ZERO CAMERA AUDIO
                chunk_out
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            rendered_chunks.append(chunk_out)
            print(f"   [{cut['id']:02d}/21] Rendered {cut['name']} (target: {dur:.3f}s, silent video)")
        else:
            print(f"   [{cut['id']:02d}/21] Reusing {cut['name']} (duration verified: {dur:.3f}s)")
        
    return rendered_chunks

def concat_and_burn():
    chunks = render_all_cuts()
    concat_txt = os.path.join(BUILD_DIR, "concat_list_v3.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in chunks:
            # Use relative path from BUILD_DIR to avoid Windows unicode path demuxer quirks
            rel_p = os.path.relpath(c, BUILD_DIR).replace('\\', '/')
            f.write(f"file '{rel_p}'\n")
            
    raw_merged = os.path.join(BUILD_DIR, "raw_visual_merged_v3.mp4")
    print(">> Concatenating silent visual chunks...")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', "concat_list_v3.txt",
        '-c', 'copy', raw_merged
    ], cwd=BUILD_DIR, check=True, capture_output=True)
    
    probe_raw = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', raw_merged], capture_output=True, text=True)
    raw_dur = float(probe_raw.stdout.strip())
    print(f">> Merged Visual Track Duration: {raw_dur:.3f}s")
    
    master_audio = os.path.join(BUILD_DIR, "master_audio_fish.wav")
    ass_subs = os.path.join(BUILD_DIR, "ad17_fish_subtitles.ass").replace('\\', '/').replace(':', '\\:')
    
    final_output = os.path.join(WORKDIR, "ad17_retiragen_fish_remastered.mp4")
    print(f">> Burning Jalnan 2 Subtitles & STRICTLY MUXING Fish Audio TTS into: {final_output}...")
    
    # CRITICAL: -map 0:v:0 -map 1:a:0 ensures 100% video from raw_merged, 100% audio from master_audio_fish.wav!
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
    print(">> FINAL REMASTERED VIDEO EXPORTED WITH FISH AUDIO & JALNAN 2 SUBTITLES!")
    
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
