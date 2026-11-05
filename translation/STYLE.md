# MLB 07 The Show (PS2) 한국어 번역 지침

입력: `chunk_XX.json` (영문 문자열 배열). 출력: `ko_XX.json` = `{ "영문 원문": "한국어 번역", ... }` — 입력의 모든 항목을 키로 포함 (번역하지 않을 항목은 원문 그대로 값으로).
JSON은 UTF-8, `ensure_ascii=False`. 직접 번역할 것(외부 번역기 사용 금지). Python으로 파일을 쓰면 편하다.

## 반드시 지킬 것
1. **제어 코드 보존**: `^n^`(줄바꿈), `^j0^ ^j1^ ^j2^`(정렬), `^b숫자^`(버튼 아이콘), `^t숫자^`, `^c숫자^`(색), `^r^`(®), `^e^`, `^d..^` 등 `^...^` 형태는 글자 그대로 유지. 문장 앞머리 코드(`^j1^` 등)는 앞머리에 그대로 둔다. 버튼 코드는 의미에 맞게 위치 이동 가능.
2. **치환자 보존**: `%1 %2 ... %9` 는 모두 그대로 포함 (순서는 한국어 어순에 맞게 바꿔도 됨). 같은 개수를 유지.
3. **사용 가능한 문자**: 한글 완성형 음절 + ASCII(영문, 숫자, 기호)만. 한자, 전각 문자, 유니코드 특수문장부호(… “ ” ‘ ’ · ～ ※ 등) 금지 → ASCII로 (`...`, `"`, `'`, `-`).
4. **번역하지 말 것(원문 그대로)**: 선수/사람 이름, 팀명·도시명·구장명·회사명(예: "Oriole Park", "Boston Red Sox", "Tempe, AZ"), 상표(DUALSHOCK, PlayStation, MLB, SportsConnect, News2Go 등은 문장 안에서도 영문 유지), 디버그/내부 식별자처럼 보이는 것(밑줄·카멜케이스·"GT_ ..."·"BP1 Color Reset"·"PRating 1-Star HL" 같은 것), 통계 약어(AVG, ERA, RBI, HR, OBP, SLG, OPS, IP, SO, BB, W-L 등 — 단독 약어는 그대로).
5. **길이**: 화면 공간이 좁다. 메뉴/버튼/라벨은 간결하게(원문 영문 글자 수 이하를 목표, 한글 1글자 ≈ 영문 2글자 폭). 대문자 원문도 한국어는 그냥 평범하게.
6. 문장/설명은 자연스러운 한국어 존댓말 안내체(~합니다/~하세요). 선수·구단주·코치 대사·피드백은 상황에 맞는 구어체(반말/존댓말 자연스럽게).
7. 줄 끝 공백, 앞뒤 공백 등 원문 공백 구조는 가능하면 유지.

## 용어집
Exhibition 시범 경기 / Manager Mode 감독 모드 / Rivalry 라이벌전 / Career 커리어 / Franchise 프랜차이즈 / Season 시즌 / Home Run Derby 홈런 더비 / King of the Diamond 킹 오브 더 다이아몬드 / Quick Game 빠른 경기 / Online 온라인 / Options 옵션 / Load Game 불러오기 / Save 저장(게임 데이터), 세이브(투수 기록) / Profile 프로필 / Roster 로스터 / Lineup 라인업 / Rotation 로테이션 / Bullpen 불펜 / Depth Chart 뎁스 차트 / Free Agent(s) FA / Trade 트레이드 / Draft 드래프트 / Contract 계약 / Salary 연봉 / Budget 예산 / Scout 스카우트 / Minor League 마이너리그 / All-Star 올스타 / Playoffs 포스트시즌(플레이오프) / World Series 월드 시리즈 / Pennant 리그 우승 / Pitcher 투수 / Starting Pitcher 선발 투수 / Relief Pitcher 구원 투수 / Closer 마무리 투수 / Catcher 포수 / First/Second/Third Base 1루/2루/3루 / Shortstop 유격수 / Left/Center/Right Field 좌익수/중견수/우익수 (위치는 좌익/중견/우익) / Designated Hitter 지명타자 / Batter 타자 / Runner 주자 / Inning 이닝 / Strikeout 삼진 / Walk 볼넷 / Hit 안타 / Single 단타 / Double 2루타 / Triple 3루타 / Home Run 홈런 / Stolen Base 도루 / Pickoff 견제 / Bunt 번트 / Fastball 직구(4-Seam 포심, 2-Seam 투심) / Curveball 커브 / Slider 슬라이더(구종) / Changeup 체인지업 / Splitter 스플리터 / Cutter 커터 / Sinker 싱커 / Knuckleball 너클볼 / Sliders(게임 설정 조절바) 슬라이더(설정) / Difficulty 난이도 / Rookie 루키 / Veteran 베테랑 / All-Star(난이도) 올스타 / Legend 레전드 / Advance 진행 / Back 뒤로 / Help 도움말 / Accept 확인 / Cancel 취소 / Select 선택 / Yes 예 / No 아니오 / OK 확인 / Memory Card 메모리 카드 / Controller 컨트롤러 / Analog 아날로그 / Widescreen 와이드스크린 / Player Card 선수 카드 / Stats 기록 / Ratings 능력치 / Attributes 능력치 / Goals 목표 / Points 포인트 / Unlock 잠금 해제 / Morale 사기 / Injury 부상 / Disabled List 부상자 명단 / Trainer 트레이너 / Coach 코치 / Owner 구단주 / Fan 팬 / Attendance 관중 / Ticket 티켓 / Vendor 매점 / Facilities 시설 / Marketing 마케팅 / Revenue 수입 / Expense 지출.
