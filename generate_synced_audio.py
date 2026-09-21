"""
Generate beat-synchronized master audio for Retiragen Shortform video.
Matches the 11 beats of source.mp4 (total 36.884s)
"""

import os
import sys
import json
import asyncio
import subprocess
import edge_tts

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(WORKDIR, "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

TOTAL_DURATION = 36.884 # exact length of source.mp4

BEATS = [
    {
        "id": 1,
        "start": 0.00,
        "end": 1.80,
        "text": "전 피부과 프락셀 안 받아도 모공 요철 제로예요.",
        "rate": "+25%"
    },
    {
        "id": 2,
        "start": 1.80,
        "end": 6.10,
        "text": "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고, 심할 땐 피부가 아예 뒤집어지더라고요.",
        "rate": "+20%"
    },
    {
        "id": 3,
        "start": 6.10,
        "end": 7.50,
        "text": "결국 나비존 요철만 푹 파였죠",
        "rate": "+25%"
    },
    {
        "id": 4,
        "start": 7.50,
        "end": 9.80,
        "text": "근데 귤껍질 같던 볼살 매끈해진 거 보이세요?",
        "rate": "+20%"
    },
    {
        "id": 5,
        "start": 9.80,
        "end": 11.60,
        "text": "전 레티놀 크림을 삼키기 시작했어요.",
        "rate": "+20%"
    },
    {
        "id": 6,
        "start": 11.60,
        "end": 12.80,
        "text": "엥? 레티놀 크림을 삼켜요?",
        "rate": "+25%"
    },
    {
        "id": 7,
        "start": 12.80,
        "end": 17.50,
        "text": "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 점점 더 팽팽하게 차오르는 거예요!",
        "rate": "+18%"
    },
    {
        "id": 8,
        "start": 17.50,
        "end": 21.50,
        "text": "그렇게 한 달 정도 꾸준히 먹어보니, 이젠 프라이머 없이도 매끈한 17호 피부가 됐어요.",
        "rate": "+18%"
    },
    {
        "id": 9,
        "start": 21.50,
        "end": 28.50,
        "text": "알고 보니 속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리라는데, 와, 피부과 프락셀 레이저가 피부 자체에 이식된 느낌?",
        "rate": "+18%"
    },
    {
        "id": 10,
        "start": 28.50,
        "end": 31.50,
        "text": "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요!",
        "rate": "+20%"
    },
    {
        "id": 11,
        "start": 31.50,
        "end": 36.884,
        "text": "30일 기간 한정 반값 할인도 한다는데, 궁금한 분들은 아래 비밀링크 참고해 보세요",
        "rate": "+18%"
    }
]

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

async def generate_beat_tts():
    print(">> Generating TTS audio for 11 beats...")
    voice = "ko-KR-SunHiNeural"
    
    for beat in BEATS:
        bid = beat["id"]
        raw_mp3 = os.path.join(TEMP_DIR, f"raw_beat_{bid:02d}.mp3")
        norm_wav = os.path.join(TEMP_DIR, f"beat_{bid:02d}.wav")
        
        # 1. edge-tts 생성
        comm = edge_tts.Communicate(beat["text"], voice, rate=beat["rate"])
        await comm.save(raw_mp3)
        
        # 2. 길이 측정 및 필요 시 atempo 미세 보정
        slot_duration = beat["end"] - beat["start"]
        cur_duration = get_audio_duration(raw_mp3)
        
        print(f"Beat {bid:02d}: slot={slot_duration:.2f}s, tts={cur_duration:.2f}s")
        
        # 슬롯에 맞추기 위해 템포 조절 (약간의 여유 마진 0.1초 남김)
        target_max = slot_duration - 0.05
        if cur_duration > target_max:
            speed = min(2.0, cur_duration / target_max)
            cmd = [
                "ffmpeg", "-y", "-i", raw_mp3,
                "-filter:a", f"atempo={speed:.3f}",
                "-ar", "48000", "-ac", "2",
                norm_wav
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", raw_mp3,
                "-ar", "48000", "-ac", "2",
                norm_wav
            ]
        subprocess.run(cmd, capture_output=True, check=True)
        beat["wav_path"] = norm_wav

def build_master_audio():
    print(">> Mixing 11 beats into master_audio.wav...")
    
    # 1. 36.884s 무음 베이스 트랙 생성
    base_silence = os.path.join(TEMP_DIR, "base_silence.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=48000:cl=stereo",
        "-t", f"{TOTAL_DURATION}",
        "-c:a", "pcm_s16le", base_silence
    ], capture_output=True, check=True)
    
    # 2. 복합 필터(amix / adelay)로 각 비트 음성을 시작 타임코드에 딜레이 배치
    inputs = ["-i", base_silence]
    filter_parts = []
    
    for i, beat in enumerate(BEATS):
        inputs.extend(["-i", beat["wav_path"]])
        delay_ms = int(beat["start"] * 1000)
        # adelay filter uses milliseconds: adelay=delay_ms|delay_ms
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms},volume=1.3[a{i+1}];")
        
    # BGM 및 SFX 추가
    bgm_path = r"C:\Users\5700G\Desktop\효과음\1_BGM(일반)\Its Jazz 30 sec.wav"
    sfx_snap = r"C:\Users\5700G\Desktop\효과음\0_오프닝 효과음(가장앞부분에배치)\HMNMisc_Finger Snap.wav"
    sfx_whoosh = r"C:\Users\5700G\Desktop\효과음\5_화면전환효과\Whoosh Transition 1.wav"
    
    has_bgm = os.path.exists(bgm_path)
    has_snap = os.path.exists(sfx_snap)
    has_whoosh = os.path.exists(sfx_whoosh)
    
    next_idx = len(BEATS) + 1
    mix_sources = ["[0:a]"] + [f"[a{i+1}]" for i in range(len(BEATS))]
    
    if has_bgm:
        inputs.extend(["-i", bgm_path])
        filter_parts.append(f"[{next_idx}:a]aloop=loop=-1:size=2e+09,volume=0.08,afade=t=out:st=34:d=2.8[abgm];")
        mix_sources.append("[abgm]")
        next_idx += 1
        
    if has_snap:
        inputs.extend(["-i", sfx_snap])
        filter_parts.append(f"[{next_idx}:a]volume=0.9[asnap];")
        mix_sources.append("[asnap]")
        next_idx += 1
        
    if has_whoosh:
        inputs.extend(["-i", sfx_whoosh])
        # 1.8초 전환 지점에 배치
        filter_parts.append(f"[{next_idx}:a]adelay=1800|1800,volume=0.7[awhoosh];")
        mix_sources.append("[awhoosh]")
        next_idx += 1

    total_mix_count = len(mix_sources)
    mix_cmd = "".join(filter_parts) + "".join(mix_sources) + f"amix=inputs={total_mix_count}:duration=first:dropout_transition=2[aout]"
    
    master_wav = os.path.join(WORKDIR, "master_audio.wav")
    final_cmd = [
        "ffmpeg", "-y"
    ] + inputs + [
        "-filter_complex", mix_cmd,
        "-map", "[aout]",
        "-t", f"{TOTAL_DURATION}",
        "-ar", "48000",
        "-c:a", "pcm_s16le",
        master_wav
    ]
    
    subprocess.run(final_cmd, capture_output=True, check=True)
    dur = get_audio_duration(master_wav)
    print(f">> Master audio successfully created: {master_wav} ({dur:.2f}s)")

if __name__ == "__main__":
    asyncio.run(generate_beat_tts())
    build_master_audio()
