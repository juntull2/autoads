# AutoAds (숏폼 커머셜 영상 자동 제작 파이프라인)

고전환율 뷰티/헬스케어 숏폼 커머셜(Reels, Shorts, TikTok)을 자동으로 연출하고 렌더링하는 AI 자동화 제작 파이프라인입니다.

## 🌟 주요 기능 (Key Features)

1. **AI 성우 & 오디오 마스터링 (Audio Pipeline)**
   - **Fish Audio TTS 연동**: 자연스러운 20대 여성 인플루언서 SNS 톤 보이스 합성
   - **1.2배속 타이트한 템포**: 정보 밀도를 극대화하는 0.05~0.15초 무음 압축
   - **카메라 원본 음성 완전 차단 (`-an`)** 및 BGM 사이드체인 더킹(-27dB)

2. **비포 & 애프터 듀얼 스플릿 연출 (Side-by-Side Dual Split)**
   - 좌측(비포, 540x1920) vs 우측(애프터, 540x1920) 30fps 동기화 분할 화면
   - 4px 화이트 디바이더 + 상단 네온 라벨 태그 + 애프터 영역 4-Point 별빛 파티클(✨) 합성

3. **고가독성 캡컷 스타일 팝 자막 (CapCut PopSub)**
   - **Jalnan 2 (잘난체 2)** 폰트 (68px, 5.0px 솔리드 블랙 외곽선, 2.0px 그림자)
   - 100% 가독성 보장 1줄 자막 (한 큐당 5~12자 분할)
   - 스프링 팝 바운스 (`90% ➔ 110% ➔ 100%`) 애니메이션

4. **다이내믹 카메라 & 컷 연출 (Dynamic Cinematography)**
   - 전 컷 부드러운 전진 줌(Ken Burns, 1.0x ➔ 1.15x) 적용
   - 셀카 반전 패키지 자동 좌우 반전 (`hflip`) 처리
   - B-roll 60% : 모델 40% 최적의 황금비 컷 구성
   - 엔딩 1.2초 아웃트로 홀드(대사 잘림 없는 여운 연출)

## 📁 주요 스크립트 구조

- `render_ad17_fish_master.py`: Fish Audio 기반 숏폼 커머셜 최종 렌더링 마스터 파이프라인
- `process_fish_audio_and_subs.py`: Fish Audio 생성 및 고가독성 ASS 자막 동기화 처리
- `generate_fish_tts.py`: Fish Audio API 호출 및 씬별 보이스 합성 모듈
- `AGENTS.md`: 숏폼 커머셜 연출 표준 규칙 가이드
- `subtitles*.ass`: PopSub 스타일 자막 템플릿
- `script.txt`: 영상 대본 및 씬 구성표

## 🚀 시작하기

### 1. 필수 요구사항
- Python 3.10+
- FFmpeg (시스템 PATH 등록)
- Jalnan 2 폰트 (Windows 글꼴 설치)

### 2. 환경 설정
`fish_api_key.txt` 파일에 Fish Audio API 키를 입력하거나 환경 변수를 설정합니다:
```bash
set FISH_AUDIO_API_KEY=your_api_key_here
```

### 3. 렌더링 실행
```bash
python render_ad17_fish_master.py
```
