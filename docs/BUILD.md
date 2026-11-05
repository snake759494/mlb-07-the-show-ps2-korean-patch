# 재빌드 방법

필요한 것: Python 3.10+ (Pillow, numpy, capstone), xdelta3. 검증용 `tools/emu.py`는 Windows용 PCSX2 v2.x와 zstandard를 씁니다.

## 준비

도구는 저장소 루트에 원본 ISO와 글꼴이 있다고 가정합니다.

```
<저장소>/
  MLB 07 - The Show (USA) (v2.00).iso   해시가 README 표와 일치하는 원본
  Galmuri11-Bold.ttf                     갈무리11 Bold
  NanumSquareNeo-eHv.ttf                 나눔스퀘어 네오 Heavy
  tools/ translation/ ...
```

글꼴 파일은 저장소에 없으므로 따로 받으세요(`docs/FONT_CREDITS.md`).

원본 ISO에서 빌드에 필요한 파일(실행파일, 게임 모듈 REL, 글꼴 bin/tx2)을 `work/`로 꺼냅니다.

```
python tools/extract.py
```

## 빌드

```
python tools/make.py
```

결과는 저장소 루트의 `MLB 07 - The Show (USA) (v2.00) (Korean).iso`입니다. 같은 입력이면 릴리즈와 바이트 단위로 같은 ISO가 나옵니다(SHA-256은 README 표 참고). `python tools/make.py -n`은 ISO를 만들지 않고 변환만 해 봅니다.

xdelta는 다음 옵션으로 만듭니다(2차 압축·경로 헤더 없음).

```
xdelta3 -e -S none -A -s "MLB 07 - The Show (USA) (v2.00).iso" "MLB 07 - The Show (USA) (v2.00) (Korean).iso" MLB07_THE_SHOW_PS2_KO_v1.0.xdelta
```

시험용 환경 변수(`make.py`):
- `NONAME`: 선수 이름을 바꾸지 않습니다. `NOALIAS`: 머리 파일 경로 별칭을 넣지 않습니다. `N8=none`: 경기용 로스터 이름을 바꾸지 않습니다.
- `NOJERSEY`: 유니폼 등 이름을 비우지 않습니다(한글 성이 깨진 글자로 나옴).
- `NOGT`: 게임 팁 본문을 다시 나누지 않습니다. `GT_SAFE`: 팁 줄바꿈 폭 여유(기본 0.9).
- `NOINL`: REL 고정 칸 문자열을 바꾸지 않습니다. `NOEXREL`: 추가 번역을 REL에 쓰지 않습니다.
- `ORIGFONT`: 글꼴을 바꾸지 않습니다. `NOSTR`, `ORIGREL`: REL 문자열 / REL 전체를 원본으로 둡니다.
- `SEL`: `모듈:시작:끝`(세미콜론으로 여럿)으로 REL 문자열 번역 범위를 제한합니다. 멈춤 원인을 이분 탐색할 때 썼습니다.

## 번역 수정

`translation/ko_<번호>.json`(기본)과 `translation/ko_x<번호>.json`(추가)은 `{영문: 한글}`입니다. 값이 원문과 같으면 바꾸지 않습니다. 선수 이름은 `names_ko_*.json`(`first`·`last`), 팀은 `teams_ko.json`(`city`·`nick`)입니다. 지침은 `translation/STYLE.md`입니다.

쓸 수 있는 글자는 한글 완성형과 ASCII뿐이며, `^...^` 제어 코드와 `%1` 같은 치환자는 원문과 같은 개수여야 합니다. 어기면 빌드에서 빠집니다.
