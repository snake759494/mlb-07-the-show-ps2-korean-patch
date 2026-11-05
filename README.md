# MLB 07 더 쇼 PS2 한글패치

PS2 북미판 **MLB 07: The Show (SCUS-97556, v2.00)**용 비공식 한국어 패치입니다. 메뉴, 옵션, 경기 HUD, 도움말, 게임 팁, 선수 소개, 커리어·프랜차이즈 문구를 한국어로 바꿨습니다. **팀 이름과 선수 이름**도 한글로 나오며, 선수 이름을 바꿔도 **선수 얼굴(머리 모델)이 그대로 나오도록** 머리 파일 경로를 연결했습니다. 현재 배포판은 **v1.0 (2026-11-05)**입니다.

[패치 다운로드](https://github.com/snake759494/mlb-07-the-show-ps2-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 한글패치 **MLB07_THE_SHOW_PS2_KO_v1.0.xdelta** 하나입니다.

저장소에는 제작 소스와 번역만 공개합니다. 원본 디스크 이미지와 완성된 디스크 이미지, 추출한 게임 파일, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

「MLB 07: The Show」는 Sony Computer Entertainment America(SCEA San Diego)가 2007년에 낸 메이저리그 야구 게임입니다. 시범 경기, 감독 모드, 라이벌전, 커리어(Road to the Show), 프랜차이즈, 시즌, 홈런 더비, 킹 오브 더 다이아몬드를 지원합니다.

이 패치는 **PS2 북미판 SCUS-97556 v2.00의 DVD ISO**에만 적용됩니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SCUS-97556 (v2.00) |
| 원본 형식 | 수정되지 않은 북미판 DVD ISO |
| 원본 ISO 크기 | 4,386,258,944 바이트 |
| **원본 ISO MD5** | `f946e0b4d61b7c4af9b78c22eaa9d4e5` |
| 원본 ISO SHA-1 | `d92b752ebbb4a46f8beaad1c7f107d33a8202f47` |
| 원본 ISO SHA-256 | `054d4fefe7936f08a9d823857748785bd1e0697237db546274330c09d89634ba` |

| 항목 | 값 |
| --- | --- |
| xdelta 크기 | 34,915,984 바이트 |
| xdelta SHA-256 | `5924e6d494e558b8d27db008bbba80d11020406e684ffb68620b0a0232f990a5` |
| 결과 ISO 크기 | 4,419,864,576 바이트 |
| 결과 ISO MD5 | `78493dbdef3b73f4a1aee6cb1baf609a` |
| 결과 ISO SHA-256 | `d3ca0065955390a44423360f40babba99404fa162c59204963b714ccf0066fec` |
| 게임 CRC (PCSX2) | `DC34A11C` (원본과 같음, 실행파일은 고치지 않음) |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath ".\MLB 07 - The Show (USA) (v2.00).iso"
```

결과가 위 표의 MD5와 다르면 적용을 중단하세요. CHD, CSO, 압축 이미지에는 적용할 수 없습니다. v1.00 등 다른 판에도 적용되지 않습니다.

### xdelta UI 사용

1. 릴리즈에서 `MLB07_THE_SHOW_PS2_KO_v1.0.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구(예: xdelta UI)에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `.iso`를 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `MLB 07 - The Show (USA) (v2.00) (Korean).iso`).
5. 결과 파일이 4.1GB이므로 저장할 드라이브에 여유 공간이 5GB 이상 있어야 합니다. FAT32 드라이브에는 4GB 넘는 파일을 저장할 수 없습니다.

xdelta는 호환성을 위해 2차 압축·파일 경로 헤더 없이(`-S none -A`) 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s ".\MLB 07 - The Show (USA) (v2.00).iso" '.\MLB07_THE_SHOW_PS2_KO_v1.0.xdelta' '.\MLB 07 - The Show (USA) (v2.00) (Korean).iso'
```

해시 검사까지 한 번에 하려면 `python tools/apply_release.py --xdelta xdelta3.exe --source "MLB 07 - The Show (USA) (v2.00).iso" --patch MLB07_THE_SHOW_PS2_KO_v1.0.xdelta --output "MLB 07 - The Show (USA) (v2.00) (Korean).iso"`를 쓰세요.

### PCSX2에서 실행

결과 ISO를 PCSX2에서 엽니다. 원본판의 세이브 스테이트는 불러오지 마세요(게임 모듈 내용이 다릅니다). 원본판에서 만든 로스터·프랜차이즈 세이브를 불러오면 그 안의 선수 이름은 영문으로 남습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 화면 문자열 | 기본 번역 약 11,400개, 추가 번역 약 2,240개. 메뉴·옵션·HUD·도움말·게임 팁·선수 소개·커리어 문구 |
| 화면세트(UI 레이아웃) | 486개 파일의 표시 문자열, 게임 팁 화면 34개는 본문을 칸별로 다시 나눔 |
| 게임 모듈(REL) | FE·GAME·HRDERBY 모듈 문자열 약 6,500개(옮겨 넣기), 구조체 안 고정 칸 문자열 약 550개(제자리) |
| 팀·선수 | 도시 101개·팀 이름 84개, 선수 이름 1,457개·성 2,965개, 머리 파일 경로 별칭 1,821개 |
| 글꼴 | 한글 **1,089자**. 메뉴·경기 글자는 갈무리11 Bold, 큰 글자는 나눔스퀘어 네오 Heavy |

영어 전용 게임에 한글을 표시하려고 글자 그리기 함수에 훅을 넣어, 2바이트 코드(`0x80|k>>7`, `0x80|k&0x7F`)를 한 글자로 그리게 했습니다. 선수 이름을 바꾸면 머리 파일(`data/heads/성_이름/PackFile.ps2`)을 찾지 못해 얼굴이 사라지므로, 한글 이름으로 만든 경로를 원래 머리 파일에 연결하는 별칭 항목을 WAD 디렉터리에 추가했습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다.
- 야구 용어는 국내 중계 표기를 따랐습니다: 평균자책점, 마무리 투수, 지명타자, 뎁스 차트.
- 팀 이름은 한글로(타이거스, 카디널스), 선수 이름은 국내 MLB 중계 표기와 외래어 표기법을 따랐습니다.
- 지침은 `translation/STYLE.md`에 있습니다.

### 번역하지 않은 것

- 게임이 내부 열쇠로 쓰는 한 단어 영문 문자열(On/Off/Medium 등 일부 옵션 값, 위치·유니폼 이름). 바꾸면 로스터가 비거나 경기가 멈춥니다.
- 통계·포지션 약어, 팀 약자, 상표
- 그림 글자(READY, ROAD/HOME, 로고), 음성, 동영상, 크레디트

## 알려진 한계

- **유니폼 등 이름은 비어 있습니다.** 등 이름은 영문 글자 텍스처로 그려서 한글 성을 표시할 수 없고, 영문 성을 따로 둘 공간도 없어 등번호만 나오게 했습니다.
- 옵션 값 중 ON/OFF/MEDIUM 같은 일부 단어와 ALC/NLC, "2007 EXHIBITION GAME", 경기 중 일부 기록 문구("9th in AL in Batting Avg." 등)는 영문입니다.
- 도시 이름이 한글이 되면서 구장 선택 목록의 정렬 순서가 원본과 다릅니다.
- 장내 아나운서가 선수 이름을 부르는 기능은 확인하지 못했습니다.
- 인게임 확인은 PCSX2로 메인 메뉴, 팀·투수·구장 선택, 시범 경기(디트로이트 대 세인트루이스) 진행까지 했습니다. 커리어, 프랜차이즈, 시즌, 홈런 더비, 온라인 메뉴, 메모리 카드 실제 저장, 실기는 확인하지 못했습니다. 칸을 넘치거나 글자가 깨지거나 얼굴이 사라지는 화면이 있으면 이슈로 알려 주세요.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/` | 빌드·검증 도구(Python). `extract.py` 게임 파일 추출, `make.py` 전체 빌드, `build.py` ISO 조립, `codepatch.py` REL 문자열·글자 훅, `gtips.py` 게임 팁 분할, `emu.py` PCSX2 조작, `apply_release.py` 해시 검사 후 적용 |
| `translation/` | 번역 (`{영문: 한글}` JSON), 선수·팀 이름, 대상 파일 목록 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처 |
| `LICENSES/` | 글꼴 라이선스 전문 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
