"""
Synthesize 7 scenes using Fish Audio S2.1 Pro Free API
Voice ID: 4e118bfbb83e401c84699c09b5f08257 (20대 여성 밝은 SNS톤 - Original Hypit Voice)
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17_fish")
SCENE_DIR = os.path.join(BUILD_DIR, "fish_scenes")
os.makedirs(SCENE_DIR, exist_ok=True)

def get_api_key():
    if os.environ.get("FISH_AUDIO_API_KEY"):
        return os.environ.get("FISH_AUDIO_API_KEY")
    for p in [os.path.join(WORKDIR, "fish_api_key.txt"), r"C:\adforge\fish_api_key.txt"]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read().strip()
    return ""

API_KEY = get_api_key()
VOICE_ID = "4e118bfbb83e401c84699c09b5f08257"
URL = "https://api.fish.audio/v1/tts"

SCENES = [
    {
        "id": 1,
        "text": "제가 하얘진 비결이요?"
    },
    {
        "id": 2,
        "text": "저 작년에 피부과 프락셀만 10번 넘게 받았어요. 그래서 요철 다 메꿔졌냐고요? 아뇨, 붉은기만 오래 가고 화장은 여전히 떴어요."
    },
    {
        "id": 3,
        "text": "그럼 어떻게 매끈해졌냐고요? 여드름 흉터 체질을 바꿨어요. 바르는 화장품만으로는 여드름 절대 못 지우거든요. 근데 체질은 바꾸기 어려워요. 이 먹는 레티놀 크림이 없다면요!"
    },
    {
        "id": 4,
        "text": "엥? 레티놀 크림을 먹는다고요??"
    },
    {
        "id": 5,
        "text": "먹기 전과 2주 뒤 모습이에요. 스위스산 레티놀이 속피지선부터 말려주고, 300달톤 콜라겐이 패인 흉터 속살을 팽팽하게 밀어 올려줘요. 피지가 잡히니까 속살이 차오르는 속도가 훨씬 빨라져요! 딱 2주만 먹어도 깐달걀 피부 돼요"
    },
    {
        "id": 6,
        "text": "300달톤 GPH 초저분자 콜라겐 비싸서 찾아보기 힘든데, 레티라겐은 스위스 레티놀에 초저분자 콜라겐 27,000mg까지 꽉 채웠더라고요. 먹는 순간 속에서 팽팽하게 차오르는 느낌!"
    },
    {
        "id": 7,
        "text": "속부터 매끈한 깐달걀 피부? 제가 흉터 지운 건 바르지 않고 먹었기 때문이에요! 아래 링크에서 반값 특가일 때 무조건 쟁여두세요!"
    }
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "model": "s2.1-pro-free"
}

for s in SCENES:
    out_mp3 = os.path.join(SCENE_DIR, f"scene_{s['id']:02d}.mp3")
    out_wav = os.path.join(SCENE_DIR, f"scene_{s['id']:02d}.wav")
    
    data = {
        "text": s["text"],
        "reference_id": VOICE_ID,
        "format": "mp3"
    }
    
    req = urllib.request.Request(URL, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            with open(out_mp3, "wb") as f:
                f.write(content)
                
            # Convert to wav and apply 1.2x tempo via pydub / ffmpeg filter
            subprocess.run([
                'ffmpeg', '-y', '-i', out_mp3,
                '-filter:a', 'atempo=1.20',
                out_wav
            ], check=True, capture_output=True)
            
            dur = len(AudioSegment.from_file(out_wav)) / 1000.0
            print(f"Scene {s['id']:02d} Generated: {dur:.2f}s | {s['text'][:25]}...")
    except Exception as e:
        print(f"Error Scene {s['id']:02d}: {e}")
