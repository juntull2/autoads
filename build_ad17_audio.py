"""
Build master audio for Retiragen ad17 benchmark video.
- 1.2x Speech speed (rate='+20%') via Edge-TTS (ko-KR-SunHiNeural)
- Tight 70ms dead-air compression between cues
- 6 Essential SFX at precise beats
- Gentle jazz/acoustic BGM ducked at -27dB
- Minimum 1.05s outro hold at tail (Zero truncation)
"""

import os
import sys
import json
import asyncio
import subprocess
import edge_tts
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17")
AUDIO_DIR = os.path.join(BUILD_DIR, "audio_chunks")
os.makedirs(AUDIO_DIR, exist_ok=True)

SFX_DIR = r"C:\Users\5700G\Desktop\효과음"

# Script cues strictly matching user script 100% verbatim
SCRIPT_CUES = [
    # Scene 1: Opening Hook
    {"scene": 1, "id": 1, "text": "제가 하얘진 비결이요?", "display": "🌸 제가 하얘진 비결이요? 🌸", "highlight": "비결", "sfx": "snap"},
    
    # Scene 2: Laser Clinic Agony & Makeup Flaking
    {"scene": 2, "id": 2, "text": "저 작년에", "display": "저 작년에 🏥", "highlight": "작년에", "sfx": None},
    {"scene": 2, "id": 3, "text": "피부과 프락셀만 10번 넘게 받았어요.", "display": "피부과 프락셀만 10번 넘게 받았어요", "highlight": "프락셀만 10번 넘게", "sfx": None},
    {"scene": 2, "id": 4, "text": "그래서 요철 다 메꿔졌냐고요?", "display": "그래서 요철 다 메꿔졌냐고요? 🤔", "highlight": "요철 다", "sfx": None},
    {"scene": 2, "id": 5, "text": "아뇨, 붉은기만 오래 가고", "display": "아뇨, 붉은기만 오래 가고", "highlight": "붉은기만", "sfx": "riser"},
    {"scene": 2, "id": 6, "text": "화장은 여전히 떴어요.", "display": "화장은 여전히 떴어요 😭💦", "highlight": "화장은 여전히", "sfx": None},
    
    # Scene 3: Paradigm Shift & Solution Concept
    {"scene": 3, "id": 7, "text": "그럼 어떻게 매끈해졌냐고요?", "display": "그럼 어떻게 매끈해졌냐고요? 💡", "highlight": "어떻게 매끈해졌냐고요?", "sfx": None},
    {"scene": 3, "id": 8, "text": "여드름 흉터 체질을 바꿨어요.", "display": "여드름 흉터 체질을 바꿨어요 ✨", "highlight": "흉터 체질을", "sfx": None},
    {"scene": 3, "id": 9, "text": "바르는 화장품만으로는", "display": "바르는 화장품만으로는 ❌", "highlight": "바르는 화장품만으로는", "sfx": None},
    {"scene": 3, "id": 10, "text": "여드름 절대 못 지우거든요.", "display": "여드름 절대 못 지우거든요 🙅‍♀️", "highlight": "절대 못 지우거든요", "sfx": None},
    {"scene": 3, "id": 11, "text": "근데 체질은 바꾸기 어려워요.", "display": "근데 체질은 바꾸기 어려워요 🥺", "highlight": "바꾸기 어려워요", "sfx": None},
    {"scene": 3, "id": 12, "text": "이 먹는 레티놀 크림이 없다면요!", "display": "이 먹는 레티놀 크림이 없다면요! 💊", "highlight": "먹는 레티놀 크림", "sfx": "ding"},
    
    # Scene 4: Shock Reaction
    {"scene": 4, "id": 13, "text": "엥? 레티놀 크림을 먹는다고요??", "display": "⚡ 엥?! 레티놀 크림을 먹는다고요?! ⚡", "highlight": "레티놀 크림을 먹는다고요", "sfx": "pop"},
    
    # Scene 5: Side-by-Side Before & After Split Screen + Mechanism
    {"scene": 5, "id": 14, "text": "먹기 전과 2주 뒤 모습이에요.", "display": "먹기 전과 2주 뒤 모습이에요 🩵", "highlight": "2주 뒤 모습", "sfx": "whoosh"},
    {"scene": 5, "id": 15, "text": "스위스산 레티놀이", "display": "스위스산 레티놀이 🇨🇭", "highlight": "스위스산 레티놀", "sfx": None},
    {"scene": 5, "id": 16, "text": "속피지선부터 말려주고,", "display": "속피지선부터 말려주고 ⚡", "highlight": "속피지선부터", "sfx": None},
    {"scene": 5, "id": 17, "text": "300달톤 콜라겐이", "display": "300달톤 콜라겐이 🧬", "highlight": "300달톤 콜라겐", "sfx": None},
    {"scene": 5, "id": 18, "text": "패인 흉터 속살을", "display": "패인 흉터 속살을", "highlight": "패인 흉터 속살을", "sfx": None},
    {"scene": 5, "id": 19, "text": "팽팽하게 밀어 올려줘요!", "display": "팽팽하게 밀어 올려줘요! 🚀", "highlight": "팽팽하게 밀어 올려줘요", "sfx": None},
    {"scene": 5, "id": 20, "text": "피지가 잡히니까", "display": "피지가 잡히니까 💧", "highlight": "피지가 잡히니까", "sfx": None},
    {"scene": 5, "id": 21, "text": "속살이 차오르는 속도가", "display": "속살이 차오르는 속도가", "highlight": "차오르는 속도", "sfx": None},
    {"scene": 5, "id": 22, "text": "훨씬 빨라져요!", "display": "훨씬 빨라져요! ⚡✨", "highlight": "훨씬 빨라져요", "sfx": None},
    {"scene": 5, "id": 23, "text": "딱 2주만 먹어도", "display": "딱 2주만 먹어도 🗓️", "highlight": "딱 2주만 먹어도", "sfx": None},
    {"scene": 5, "id": 24, "text": "깐달걀 피부 돼요", "display": "깐달걀 피부 돼요 🥚✨", "highlight": "깐달걀 피부", "sfx": "ding"},
    
    # Scene 6: Spec Highlight Card & Package
    {"scene": 6, "id": 25, "text": "300달톤 GPH 초저분자 콜라겐", "display": "300달톤 GPH 초저분자 콜라겐", "highlight": "300달톤 GPH", "sfx": None},
    {"scene": 6, "id": 26, "text": "비싸서 찾아보기 힘든데,", "display": "비싸서 찾아보기 힘든데 💸", "highlight": "찾아보기 힘든데", "sfx": None},
    {"scene": 6, "id": 27, "text": "레티라겐은 스위스 레티놀에", "display": "레티라겐은 스위스 레티놀에 🇨🇭", "highlight": "레티라겐은", "sfx": None},
    {"scene": 6, "id": 28, "text": "초저분자 콜라겐 27,000mg까지", "display": "초저분자 콜라겐 27,000mg까지 꽉! 💯", "highlight": "27,000mg까지", "sfx": None},
    {"scene": 6, "id": 29, "text": "꽉 채웠더라고요.", "display": "꽉 채웠더라고요 👏✨", "highlight": "꽉 채웠더라고요", "sfx": "ding"},
    {"scene": 6, "id": 30, "text": "먹는 순간 속에서", "display": "먹는 순간 속에서", "highlight": "먹는 순간", "sfx": None},
    {"scene": 6, "id": 31, "text": "팽팽하게 차오르는 느낌!", "display": "팽팽하게 차오르는 느낌! 💖", "highlight": "팽팽하게 차오르는", "sfx": None},
    
    # Scene 7: Climax & Ending CTA
    {"scene": 7, "id": 32, "text": "속부터 매끈한 깐달걀 피부?", "display": "속부터 매끈한 깐달걀 피부? 🥚", "highlight": "깐달걀 피부?", "sfx": None},
    {"scene": 7, "id": 33, "text": "제가 흉터 지운 건", "display": "제가 흉터 지운 건", "highlight": "제가 흉터 지운 건", "sfx": None},
    {"scene": 7, "id": 34, "text": "바르지 않고 먹었기 때문이에요!", "display": "바르지 않고 먹었기 때문이에요! 🤫", "highlight": "먹었기 때문이에요!", "sfx": None},
    {"scene": 7, "id": 35, "text": "아래 링크에서 반값 특가일 때", "display": "아래 링크에서 반값 특가일 때 🏷️", "highlight": "반값 특가일 때", "sfx": "click"},
    {"scene": 7, "id": 36, "text": "무조건 쟁여두세요!", "display": "무조건 쟁여두세요! 🛒👇", "highlight": "무조건 쟁여두세요!", "sfx": None}
]

def find_sfx(kw):
    for root, dirs, files in os.walk(SFX_DIR):
        for f in files:
            if kw.lower() in f.lower():
                return os.path.join(root, f)
    return None

async def synthesize_all():
    print(">> Synthesizing TTS cues with Edge-TTS (ko-KR-SunHiNeural, +20%)...")
    for cue in SCRIPT_CUES:
        out_f = os.path.join(AUDIO_DIR, f"cue_{cue['id']:02d}.mp3")
        tts = edge_tts.Communicate(cue["text"], "ko-KR-SunHiNeural", rate="+20%")
        await tts.save(out_f)
    print(f">> Successfully synthesized {len(SCRIPT_CUES)} cues.")

def build_master_audio():
    print(">> Assembling timeline, mixing SFX, BGM, and Outro Hold...")
    
    # Track timestamps
    timeline = []
    current_time_ms = 0
    PAUSE_MS = 75 # 75ms tight pause between cues
    
    combined_speech = AudioSegment.silent(duration=0)
    
    for cue in SCRIPT_CUES:
        mp3_f = os.path.join(AUDIO_DIR, f"cue_{cue['id']:02d}.mp3")
        seg = AudioSegment.from_file(mp3_f)
        
        # trim any silence from start/end of seg
        seg_dur = len(seg)
        start_ms = current_time_ms
        end_ms = start_ms + seg_dur
        
        cue_info = dict(cue)
        cue_info["start"] = round(start_ms / 1000.0, 3)
        cue_info["end"] = round(end_ms / 1000.0, 3)
        cue_info["dur"] = round(seg_dur / 1000.0, 3)
        timeline.append(cue_info)
        
        combined_speech += seg
        combined_speech += AudioSegment.silent(duration=PAUSE_MS)
        current_time_ms += seg_dur + PAUSE_MS
    
    speech_dur_ms = len(combined_speech)
    print(f">> Spoken speech duration: {speech_dur_ms / 1000.0:.3f}s")
    
    # 1.05s Outro Hold at tail
    OUTRO_HOLD_MS = 1150
    total_timeline_ms = speech_dur_ms + OUTRO_HOLD_MS
    master = AudioSegment.silent(duration=total_timeline_ms)
    master = master.overlay(combined_speech, position=0)
    
    # Overlay SFX
    sfx_map = {
        "snap": find_sfx("스냅"),
        "riser": find_sfx("라이저"),
        "whoosh": find_sfx("우쉬"),
        "ding": find_sfx("차임"),
        "pop": find_sfx("팝"),
        "click": find_sfx("클릭")
    }
    
    for item in timeline:
        sfx_key = item.get("sfx")
        if sfx_key and sfx_key in sfx_map and sfx_map[sfx_key]:
            sfx_f = sfx_map[sfx_key]
            pos_ms = int(item["start"] * 1000)
            try:
                sfx_seg = AudioSegment.from_file(sfx_f)
                # adjust volume
                if sfx_key == "snap":
                    sfx_seg = sfx_seg - 6
                elif sfx_key == "riser":
                    sfx_seg = sfx_seg - 12
                elif sfx_key == "whoosh":
                    sfx_seg = sfx_seg - 8
                elif sfx_key == "ding":
                    sfx_seg = sfx_seg - 10
                elif sfx_key == "pop":
                    sfx_seg = sfx_seg - 8
                elif sfx_key == "click":
                    sfx_seg = sfx_seg - 6
                master = master.overlay(sfx_seg, position=pos_ms)
                print(f"   [SFX] Added {sfx_key} at {item['start']}s ({os.path.basename(sfx_f)})")
            except Exception as e:
                print(f"   [SFX Error] {sfx_key}: {e}")
                
    # Add BGM (-27dB ducking)
    bgm_candidates = [
        find_sfx("bgm"),
        os.path.join(WORKDIR, "scratch", "test_free.mp3"),
        os.path.join(SFX_DIR, "BGM.mp3")
    ]
    bgm_file = None
    for cand in bgm_candidates:
        if cand and os.path.exists(cand):
            bgm_file = cand
            break
            
    if bgm_file:
        try:
            bgm = AudioSegment.from_file(bgm_file)
            bgm = bgm - 27 # Ducking to -27dB
            # loop bgm to match total duration
            loops = int(total_timeline_ms / len(bgm)) + 1
            bgm_looped = (bgm * loops)[:total_timeline_ms]
            bgm_looped = bgm_looped.fade_in(800).fade_out(1200)
            master = master.overlay(bgm_looped, position=0)
            print(f">> BGM added with -27dB ducking ({os.path.basename(bgm_file)})")
        except Exception as e:
            print(f">> BGM loading error: {e}")
            
    out_master_wav = os.path.join(BUILD_DIR, "master_audio_ad17.wav")
    master.export(out_master_wav, format="wav")
    print(f">> Master Audio exported to: {out_master_wav}")
    print(f">> Total Audio Duration: {len(master)/1000.0:.3f}s (Outro Hold: {OUTRO_HOLD_MS/1000.0:.2f}s)")
    
    # Save timestamps json
    meta_json = os.path.join(BUILD_DIR, "ad17_timestamps.json")
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": round(len(master) / 1000.0, 3),
            "spoken_duration": round(speech_dur_ms / 1000.0, 3),
            "outro_hold": round(OUTRO_HOLD_MS / 1000.0, 3),
            "cues": timeline
        }, f, indent=2, ensure_ascii=False)
    print(f">> Timestamps JSON saved to: {meta_json}")

if __name__ == "__main__":
    asyncio.run(synthesize_all())
    build_master_audio()
