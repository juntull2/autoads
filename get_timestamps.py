import whisper
import json
import os

model = whisper.load_model('base')
results = {}
for i in range(1, 11):
    wav = f"c:/adforge/temp_audio/retiragen_pore_v2/scene_{i:02d}.wav"
    res = model.transcribe(wav, word_timestamps=True, language='ko')
    words = []
    for seg in res['segments']:
        for w in seg.get('words', []):
            words.append({'word': w['word'], 'start': round(w['start'], 2), 'end': round(w['end'], 2)})
    results[f"scene_{i:02d}"] = {
        'text': res['text'].strip(),
        'words': words
    }
    print(f"Scene {i:02d}: {res['text'].strip()}")

with open('word_timestamps.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Done: word_timestamps.json saved")
