---
id: hama-ref-fx-notes
type: reference
track: invest
status: active
last_review: 2026-11-04
---

# 효과·프롬프트 목록 — 뮤즈 볼크 노트 · 레퍼런스 42장 · Stageshow

**확인 범위.** 지정 노트는 전부 읽었다. 뮤즈 볼크의 나머지 노트는 모션 관련 단어로 훑었고, 11/04 mrcreates 노트와 `REF/_index.md`도 포함했다. 핸드오프, REFS.md, _index.md, Stageshow의 craft·framing·motion·choreography, number-story.html, rail/parts.py도 읽었다.

**직접 본 이미지.** 13, 15, 02, 05, 10, 17, 28, 29, 30~42(charliehills 13장 전부), 19장 대지. 01·06·18·20~24는 열어 보지 않았고 REFS.md 설명만 따랐다.

**알아 둘 점.**
- charliehills 캡처는 14/19장까지라 장면 16개 중 12개만 있다. 13~16번 장면은 확인 안 됨.
- mrcreates 녹화 영상(.mov)은 재생하지 않았다. 내용은 11/04 세션이 쓴 `REF/_index.md` 기록을 따랐다.
- astapable은 원본 파일이 없고 핸드오프에 한 줄만 있다.
- dihichi(10)·joosikbiseo(05)·amirasky(02)는 캡처에 음소거 아이콘이 있어 영상이다. 정지 화면만 봤으므로 실제 움직임은 확인 안 됨.

---

## 1. 효과·기법 표

| # | 이름 | 출처 (+계정) | 무엇이 움직이나 (시작 → 끝) | 무엇을 말하나 / 언제 | 만드는 법 한 줄 |
|---|---|---|---|---|---|
| 1 | Bars → trend | shots/31 (charliehills) | 막대 7개가 하나씩 스프링으로 솟고 살짝 넘쳤다 돌아옴 → 빛나는 선이 꼭대기를 그음 → 점이 선을 따라 끝까지 가고, 끝에서 성장 숫자가 크게 초록으로 뜸 | 꾸준히 넣으면 추세가 생긴다, 결산 장면 | 막대 scaleY에 `back.out` + stagger, SVG path의 strokeDashoffset, 점은 MotionPath(또는 길이 비율 보간), 숫자 scale 팝 |
| 2 | Monthly → yearly | shots/32 | 세그먼트 토글 알약이 스프링으로 미끄러짐 → 가격이 기계식 오도미터로 굴러 £29에서 £290 → «2 months free» 뱃지가 튀어 들어옴 | 월 금액과 연 금액 비교 (예: $100/월 → $1,200/년) | 알약 x 이동, 자릿수마다 세로 숫자 띠를 yPercent로 굴림, 뱃지 `back.out` |
| 3 | Dots → logo | shots/33 | 광택 구슬 약 150개가 가장자리에서 흘러 들어와 한 번 소용돌이친 뒤 로고 모양으로 스냅 → 반사광이 한 번 스침 | 흩어진 돈이 한 덩어리로 모인다 | 점 좌표를 미리 계산해 두고 GSAP stagger로 보간(난수는 시드 고정), 마지막에 glint 그라디언트 sweep |
| 4 | Island → live | shots/34 | 폰 상단 검은 알약이 스프링으로 펼쳐짐 → 3·2·1 카운트다운이 넘어감 → 빨간 점이 뛰며 «LIVE»와 한 줄 → 다시 알약으로 접힘 | 지금 시작, 마감 임박 (예: TFSA 한도 갱신일) | 알약 width·borderRadius를 함께 트윈, 숫자 flip, 점 scale yoyo, 역방향으로 접기 |
| 5 | Visits → sales (깔때기) | shots/35 | 기울어진 3D 유리 깔때기 위로 입자 수백 개가 쏟아짐 → 아래로는 적은 수만 빠져 카운터에 떨어짐 → 카운터가 «600 sales»까지 굴러감 | 많이 들어와도 남는 건 적다 (수수료·세금으로 새는 돈) | 입자 div나 SVG circle을 시드 고정 경로로, 깔때기는 SVG 그라디언트, 카운터는 #8 방식 |
| 6 | Click → done | shots/36 | 커서가 큰 광택 버튼을 누르면 버튼이 찌그러짐 → 원으로 변하며 파란 진행 링이 차오름 → 초록 체크와 잔물결 → 다시 «Published» 버튼으로 커짐 | 한 번 누르면 끝 (자동이체 설정) | width→원 morph, SVG 링 strokeDashoffset, 체크 path 그리기, ripple은 scale+opacity |
| 7 | Card → paid | shots/37 | 지갑형 카드가 주머니에서 올라옴 → «Pay £4,850» 버튼 둘레를 빛의 고리가 돎 → 초록 체크가 «Paid»로 안착하고 카드가 다시 내려앉음 | 결제·이체 한 번의 순간 | 카드 y 이동 + 주머니 overflow 마스크, 둘레 빛은 conic-gradient 회전, 체크 path |
| 8 | 0 → 12,480 자릿수 카운터 | shots/38 | 잠금화면 위젯에서 자릿수마다 따로 기계식으로 굴러감 (빠른 자리는 흐림, 아직 0인 자리는 회색) → «+18% this month» 칩이 튀어 들어옴 | 결산 숫자, 복리 결과. REFS.md는 «하마 결산 장에 그대로»라고 적음 | 자릿수별 세로 띠의 yPercent를 서로 다른 시간으로, 빠를 때만 filter blur. Stageshow 규칙: 끝자리부터 돌고, 변하지 않는 자리는 가만 |
| 9 | Weight → bold | shots/39 | 가변 폰트 굵기가 글자마다 파도처럼 hairline에서 black으로 쓸림 → 글자가 숨쉬듯 움직임 → 마침표가 파란 점이 되어 한 번 튐 | 훅 한 줄 강조 | 글자를 span으로 나눠 `font-variation-settings` 'wght' 트윈 + stagger (가변 폰트 필요), 점 y 바운스 |
| 10 | Sketch → app (세로 와이프) | shots/40 | 연필선 와이어프레임 위로 세로 와이프 손잡이가 지나가며 완성 화면(링 차트 86%, 카드 2장)을 드러냄 | 계획(스케치) → 실제 결과, 전후 비교 | 두 레이어 겹치고 위 레이어 clip-path inset 트윈, 손잡이 x 동기 |
| 11 | Drag → booked | shots/41 | 커서가 캘린더 블록을 끌면 자석처럼 칸에 스냅 → 보라로 바뀌고 이름이 뜸 → 작은 아바타가 떨어짐 | 날짜 정하기 (매달 15일 적립일) | 블록 x/y 트윈, 끝 `back.out`, backgroundColor 트윈 약 200ms (Stageshow: 먼 색끼리는 200ms) |
| 12 | Alerts → stack | shots/42 | 잠금화면에 알림이 하나씩 스프링으로 떨어져 깔끔한 더미로 쌓임 → 뱃지 숫자가 합계까지 올라감 | 입금 알림이 쌓인다 (배당·적립) | 카드 y 드롭 + stagger, 아래 카드는 scale 0.95로 뒤로, 뱃지는 #8 카운터 |
| 13 | 장면 13~16 | charliehills | **확인 안 됨** (캡처 없음) | | |
| 14 | «전 → 후» 두 단어 제목 | shots/30~42 | 정지 화면 문법. «Bars → trend»처럼 오른쪽 단어만 색 | 장면 이름 붙이기. REFS.md는 하마 각도를 이 틀로 다시 쓰자고 제안 | 텍스트 + 액센트 색 한 단어 |
| 15 | LIVE 숫자 칩 | REF/_index.md (mrcreates) | «LIVE 1,284,407 editing» 칩의 숫자가 올라감 | 훅에서 «지금 다들 한다» | 카운터 칩. 우리 rail `hook` 부품에 이미 칩 있음 |
| 16 | 결제창 목업 + 취소선 | REF/_index.md | $497 강의 결제창 등장 → «not claude.ai in a browser»에 취소선 | «돈 내지 마» 반전 | 카드 팝 + 취소선 scaleX. rail `checkout`의 strike에 이미 있음 |
| 17 | 단어 하나씩 + 핵심어 선택 상자 | REF/_index.md, 뮤즈 볼크/2026-11-04-참조-mrcreates-에버그린-키트.md | 위 한 줄에 단어가 하나씩 들어옴, 핵심 단어 하나만 세리프 이탤릭 + 에디터 선택 상자 | 자막 겸 키네틱 타입 | 단어 span stagger, 상자는 border 박스 scaleX |
| 18 | 세로 체크 레일 12칸 | REF/_index.md | 12칸이 재생되며 차례로 체크됨. 끝에서 전체가 위에서 아래로 체크 | 끝까지 보게 만드는 진행 막대 | rail `checklist`에 있음 (선 scaleY + 체크 strokeDash) |
| 19 | 단계 배지 | REF/_index.md | 아바타 + «04 Five tools» 알약, 단계마다 바뀜 | 지금 몇 단계인지 | 알약 텍스트 교체 (롤) |
| 20 | 폴더 가지치기 | REF/_index.md | AI Video Editor 폴더에서 하위 폴더 3개가 가지처럼 뻗음 | 하나에서 여럿으로 나뉨 (통장 3개 나누기) | SVG 선 그리기 + 카드 stagger |
| 21 | Cloud/Local 토글 | REF/_index.md, 같은 계정 다른 릴스 «토글 6개» | 토글 손잡이가 넘어가고 트랙 색이 바뀜 | 설정 하나 켜기 | rail `toggle`에 있음 |
| 22 | 0/5 → 5/5 허브 | REF/_index.md | 가운데 아이콘 둘레 점선 원 «0/5 tools» → 도구 5개가 차서 «5/5» | 갖출 것 N개 다 채우기 | 원 둘레 노드 stagger 팝 + 분수 카운터 |
| 23 | 카드 3장 3D 쌓기 | REF/_index.md | Cut·Captions·Music 카드 3장이 3D로 쌓임 | 한 번에 처리되는 일 묶음 | perspective + rotateX + y stagger |
| 24 | 훅 상자 커짐 + 파형 칩 | REF/_index.md | «THE HOOK» 상자가 커지고 음성 파형 칩이 뜸 | «말로 고친다» 장면 | 상자 scale, 파형은 막대 scaleY 반복 (시간 함수로) |
| 25 | TOOLS 대 YOUR TASTE 두 카드 | REF/_index.md | 아이콘 5개 카드와 AaAa·색 점·곡선 카드가 나란히 | 마무리 대비 한 줄 | 두 카드 팝 |
| 26 | 글자 타일 낙하 (키워드 CTA) | REF/_index.md | 파란 빛이 켜지고 E D I T O R 글자 타일이 회전하며 떨어짐 | 댓글 키워드 CTA | rail `tiles`에 있음 (y:-260, rotation, `back.out`) |
| 27 | 취소선 → 도달률 감소 | REF/_index.md («Forget hashtags») | 해시태그 6개에 빨간 취소선 → 아바타에서 사람 아이콘으로 부채꼴 선 → 막대 92%→90%→49%→7%로 줄며 빨개지고 선이 흐려짐 | 손해가 커지는 걸 숫자로 보여줌 (수수료가 갉아먹는 돈) | 취소선 scaleX, 막대 scaleX + 색 트윈, 선 opacity |
| 28 | 원본/편집본 분할 + 갈라지는 로고 + 솟는 큰 글자 | 뮤즈 볼크/2026-10-27-참조-클로드-코드-자동-편집.md (프롬왓 노션 키트 장면 A), 뮤즈 볼크/2026-10-27-참조-릴-2.md (prompt_what) | 두 창이 나란히, 뒤에서 로고가 갈라지고 큰 글자(HOOK_WORD)가 솟아오름 | 첫 화면 훅. 노트는 «HAMA 같은 영문 채널명»으로 교체하자고 제안 | 로고 두 반쪽 x 반대로, 글자 y 상승 + clip 마스크 |
| 29 | 작업 창 타이핑 | 같은 노트 (장면 B) | 파일이 창으로 들어가고 한 줄이 타이핑됨 | 과정 시연 | 글자 수를 시간 함수로 (steps) |
| 30 | 코드 흐름 + 렌더 막대 | 같은 노트 (장면 C) | 코드가 흐르고 막대가 차오름 | 진행 중 | 목록 y 스크롤 + bar scaleX |
| 31 | 말로 고치면 미리보기가 바뀜 | 같은 노트 (장면 D) | 채팅 두 문장 → 미리보기 색이 바뀜 | 전후 비교 | 말풍선 팝 + 색 트윈 |
| 32 | 큰 글자 판 | 같은 노트 (장면 E) | 얼굴 옆에 큰 판 두 장 + 강조 판 하나 | 핵심 문장 박기 | 판 팝 stagger |
| 33 | 댓글 → DM으로 날아가는 자료 | 같은 노트 (장면 F) | 댓글이 달리고 자료 페이지가 DM으로 날아감 | 키워드 CTA | 카드 날기 (Stageshow «Fly»: 커지며 이동, 600ms 이상, 끝은 부드럽게) |
| 34 | 단어별 자막 + 스티커 칩 + 파랑 선택 박스 | 같은 노트, 뮤즈 볼크/2026-10-27-참조-릴-2.md | 모든 단어에 단어별 자막, 스티커는 각각 고칠 수 있는 레이어 | 말하는 영상 위 자막 | Whisper 단어 타이밍 → span. rail 구조와 같음 |
| 35 | 인물 뒤로 들어가는 글자 | 뮤즈 볼크/2026-10-27-참조-릴-2.md (prompt_what) | 인물을 프레임 단위로 잘라 글자가 인물 뒤에 들어감 | 깊이감 | 컷아웃 PNG 시퀀스를 글자 위 레이어로. 하마 사진에 쓸 수 있을지는 확인 안 됨 |
| 36 | 픽셀 마스코트 라벨 | 뮤즈 볼크/2026-10-27-참조-릴-2.md, 노션 키트 | 마스코트가 라벨로 따라다님 | 노트는 하마 캐릭터로 바꾸자고 적음 | (메모리 «그린 캐릭터 금지»와 부딪힘. 실제 하마 사진만) |
| 37 | 장면 4종 섞기, 2~3초마다 전환 | 뮤즈 볼크/2026-11-02-링크-브레인.md 1번 (낭만빌더 스타일 시트) | 얼굴 전체 / 얼굴 위 카드 / 위 그래픽+아래 얼굴 / 그래픽 전체를 2~3초마다 바꿈 | 리듬 | 장면 clip 교체 |
| 38 | 첫 장면 은유 물건 하나 3D로 크게 | 같은 곳 | 주제를 은유하는 물건 하나가 크게 | 훅 | 물건 하나 + 그림자 |
| 39 | 하단 문장 자막 + 핵심어 민트 박스 | 같은 곳 | 문장 단위 한 화면, 흰 글자 + 검정 테두리 + 약한 그림자, 핵심 단어 하나만 색 박스 | 자막 스타일 | CSS. 세이프존 x 65~888, y 288~1248 |
| 40 | 장면 전환마다 효과음, 쉼 0.2~0.3초 | 같은 곳 · 뮤즈 볼크/2026-11-03-참조-링크3개-수확.md 5절 (clone-me) | 화면 요소가 나올 때마다 작은 클릭 소리. 0.5초 무음 컷, 1.1배속, -14 LUFS (링크 브레인은 -16) | 마감 손질 | ffmpeg. rail에 tick.wav·tock.wav 있음 |
| 41 | 흰 띠 + 검정 한 줄 + 라임 점 + 비트마다 물건 교체 | 99-ops/handoffs/2026-11-03_하마-엔진.md 8차 (astapable, 저장 7,233) | 비트마다 물건 하나가 바뀜, 15~19초 | number-story가 이 문법이라고 적혀 있음 | 원본 영상은 **확인 안 됨** |
| 42 | 노트북 화면을 찍은 영상 + 가운데 3줄 자막 | shots/13, 15 (luna_workwithai) | 폰으로 노트북 화면(animejs.com, motion.dev)을 찍음, 가운데에 흰 굵은 자막 «도구명 / 쓰는 때» | 도구 소개형. 모션그래픽이 아니라 실사 촬영 | 화면 안 3D 원통은 사이트 데모. 움직임은 정지 화면이라 **확인 안 됨** |
| 43 | 0~3초 하마 등장 + 금 곡괭이 한 번 휘두르기 | 뮤즈 볼크/2026-10-31-하마-콘텐츠-엔진-프롬프트.md (릴스 6장면 명세) | 곡괭이 한 번 | 하마 시그니처 훅 | 명세만 있고 레퍼 영상 없음. 메모리 «그린 캐릭터 금지»와 충돌 가능 |
| 44 | 시각 규모 비유 | 같은 파일 5절 (Humphrey Yang 쌀 비유 → 하마 간식) | 원본 **확인 안 됨** | 큰 숫자를 물건 개수로 | 확인 안 됨 |
| 45 | Stageshow 움직임 규칙 | ~/.agents/skills/stageshow/references/motion.md | 이동 곡선 `cubic-bezier(0.45,0,0.1,1)`, 등장 곡선 `cubic-bezier(0.25,0.8,0.25,1)` 0.8~1초. 묶음 안 stagger 40~80ms, 격자는 80~120ms. 결과 2초 정지, 3초 넘게 멈춘 것 없음. «Nothing pops», 단단한 물건은 반투명으로 흐려지지 않고 움직여서 들어옴. 숫자는 끝자리부터 롤. 카드는 바로 위에서 통째로 떨어지고 착지는 부드럽게, 반동 없음 | 전 장면 공통 규칙 | GSAP CustomEase나 cubic 문자열 |
| 46 | Stageshow 배치 규칙 | ~/.agents/skills/stageshow/references/framing.md, craft.md | 주인공 하나 + 위성 1~2개가 가장자리에 반쯤 걸침. 주인공 10~40%를 무대 밖으로 자름. 큰 숫자는 하나. 금액은 숫자만 가운데, $는 왼쪽에 매달기. 종이(영수증)는 Tilted stack -6°·4°·-2° | 정지 프레임 | CSS |

### 이미 엔진에 있는 것

`엔진/motion/number-story.html` 한 파일에 다섯 가지가 있다.
- 훅 숫자가 흐림에서 선명해지고, 골드 밑줄이 scaleX로 그어짐
- 단어가 블러 상태로 들어오고 70~80ms 간격
- 1.4초 카운트업 + 골드 막대 + 동전 더미 (`back.out`)
- 넣은 돈과 시간이 보탠 돈 두 막대가 scaleX로 자람
- 하마 사진은 페이드, 알약은 미끄러짐

`엔진/motion/rail/parts.py`의 부품은 hook, checkout, amount, toggle, counter, split, checklist, compare, tiles, coins, receipt. checkout은 취소선 + 도장을 찍고, compare는 곡선을 그리고, tiles는 타일을 떨어뜨리고, coins는 동전을 떨어뜨리고, receipt는 프린터처럼 steps(16)으로 내려온다.

**아직 없는 것:** 1, 2(오도미터), 3, 4, 5, 6, 7, 8(자릿수별 롤), 9, 10, 11, 12, 20, 22, 23, 27(줄어드는 막대).

---

## 2. 출처에 있는 모션 프롬프트

### A. charliehills 브리프 (shots/30, 화면에서 그대로 옮김)

```
Make me a motion graphic. Follow this motion brief exactly:
THE BAR    Apple keynote quality. If it would not survive in an Apple keynote, it is not done.
FORMAT     1080 x 960. Exactly 6 seconds. The last frame matches the first.
ONE RULE   One hero object fills 60 to 70% of the frame. ONE satisfying change, then reset.
LOOK       Bright and clean. Frosted glass, soft shadows, real depth. One or two system colours.
TYPE       Heavy weights. At most 5 words. The key number 120px or more.
MOTION     Spring physics on everything. Hold the after state for 1.2 seconds.
NEVER      Grey placeholder bars, stock icons, emoji, dark backgrounds.
THE SCENE  Bars that turn into a trend
```

같은 장 아래 문구: «I paste this first, then add one scene at the end.»

### B. charliehills «SWAP IN THIS SCENE» (shots/31~42, 캡처에서 그대로 옮김)

- 01 (31): A frosted glass chart widget "[your metric]". Seven bars spring up one by one with a small overshoot, then a glowing line draws through their tops and a dot rides it to the end, where "[your growth figure]" pops in huge in green. / I used: Weekly sign-ups, +200%.
- 02 (32): An iOS-style segmented control (Monthly | Yearly) above a premium pricing card "[your plan name]". The selection pill slides across with a spring, and the price rolls from [monthly price] to [yearly price] on a mechanical odometer while a small "[your offer]" badge springs in. / I used: Pro, £29 to £290, "2 months free".
- 03 (33): Around 150 small glossy spheres drift in from the edges, swirl once, then snap together into [describe your logo mark in one line], which catches a specular glint. / I used: a bold original mark (a rounded squircle with a cut-out arc).
- 04 (34): A black pill at the top of a phone screen expands with a spring into a live activity: a countdown 3, 2, 1 flipping, then a red pulsing dot and "LIVE" with "[your event line]". Then it shrinks back to the pill. / I used: "Webinar starts now".
- 05 (35): A 3D glass funnel, slightly tilted. Hundreds of tiny glowing particles pour in at the top and fewer fall out at the bottom into a counter that rolls up to "[your result]". / I used: "600 sales".
- 06 (36): A large glossy "[your button word]" button. A cursor clicks it, the button squashes, morphs into a circle with a blue progress ring that fills, then snaps into a green tick with a soft ripple, and grows back reading "[the done word]". / I used: Publish, then Published.
- 07 (37): A wallet-style payment card slides up out of a pocket, a ring of light runs around a "Pay [your amount]" button, and a big green tick lands with "Paid" as the card settles back. / I used: £4,850.
- 08 (38): A lock-screen widget "[your metric]". Each digit rolls independently like a mechanical counter from 0 to [your number], with a soft blur on the fast digits, then a small "[your change line]" chip springs in. / I used: Subscribers, 12,480, "+18% this month".
- 09 (39): The headline "[your headline]" in a variable font. The weight sweeps from hairline to black letter by letter like a wave, the letters breathe, and the full stop becomes a blue dot that bounces once. / I used: "Make it move."
- 10 (40): A phone frame. A pencil-line wireframe of an app screen sits inside. A vertical wipe handle sweeps across and reveals the finished, colourful app screen ("[your app name]", [two or three things on the screen]) under it. / I used: "Daily Focus", a ring chart and two cards.
- 11 (41): A calendar week view in a glass window. A cursor drags an event block onto [day and time], it magnetically snaps into its slot, turns purple and reads "[your event]", and a small avatar drops in. / I used: Thursday 11:00, "Call with Sam".
- 12 (42): A phone lock screen. Notifications drop in one after another with springs ("[alert one]", "[alert two]"), stack into a neat pile, and the pile badge counts up to "[your total]". / I used: "New order £42", "New order £96", "12 new orders".
- 13~16: 확인 안 됨

### C. mrcreates 키트 (뮤즈 볼크/2026-11-04-참조-mrcreates-에버그린-키트.md 전문 절, 하림님이 붙인 원문)

편집 프롬프트이고 모션은 3번 항목 한 줄이다.

```
Edit my new video into an Instagram Reel:
[FILE NAME] in my Raw Footage folder

1. Remove every pause longer than 0.1 seconds.
2. Follow my approved brand sheet.
3. Add captions, music, and motion graphics.
4. Use anything useful from my References folder.

Show me a storyboard to review first. After I approve it, export the final video to my Exports folder.
```

- 고칠 때 한 줄: «Make the hook bigger.»
- 브랜드 시트 프롬프트(Prompt 2)는 레퍼에서 무엇을 뽑을지 나열한다. 원문 그대로: «Study what they have in common: fonts, colors, caption style, cuts, zooms, pacing, motion graphics, music, and sound.» «Make it inspired by these videos, not a copy of them.»

### D. 원문이 아니라 요약이거나 확인 안 됨

- **Awesome Opus 5.5 Videos (yihui-dev).** 99-ops/handoffs/2026-11-03_하마-엔진.md에 «30초 모션그래픽, 최고로, go all out»으로만 적혀 있다. 한국어로 옮긴 요약이라 원문 확인 안 됨.
- **스토리보드 프롬프트 빌더 (존코바디자인).** 뮤즈 볼크/2026-11-02-링크-브레인.md 5번 예시 «첨부한 이미지의 캐릭터와 무드를 반영해서, 건물 사이로 파쿠르 하는 역동적인 15초 시나리오 프롬프트 작성, 컷은 많이 넣어 속도감 있게» 뒤에 `/storyboard-prompt-builder`를 붙인다. 노트 문장이라 원문 그대로인지 확인 안 됨. 개인 참고용으로만 쓰라는 제작자 조건이 있다.
- **프롬왓 노션 요청문 7개.** 1차 요청, 다듬기 예문 4개, 마무리, 단축 요청. 코드 블록이 로딩 상태라 못 읽음, 확인 안 됨 (뮤즈 볼크/2026-10-27-참조-클로드-코드-자동-편집.md).
- **UCHAL 아티클 프롬프트.** 본문을 열지 않음, 확인 안 됨 (뮤즈 볼크/2026-10-30-참조-영상-만드는-방법.md).
- **e1genqq 모션그래픽 링크, X 링크 1~3번, 신영선 가이드북 Docs.** 본문 확인 안 됨 (뮤즈 볼크/2026-10-30-참조-모션그래픽.md, 2026-11-01-참조-X-링크-모음.md, 2026-11-02-링크-브레인.md).
- **henry_upnomad STEP 01 (shots/28).** 훅 쓰기 프롬프트라 모션과는 무관하다. 장치 쪽으로는 «회색 카드 안 복사용 전문»이라는 R12 무대.

---

## 3. 레퍼에 나온 돈 관련 시각 물건

| 물건 | 보이는 레퍼 |
|---|---|
| 막대 차트 + 추세선 + 끝점 | 31 (charliehills), 02 (amirasky IRP 막대 + 상승 화살표) |
| 가격 카드 + 오도미터 숫자 | 32 (£29) |
| 결제 카드 / Pay 버튼 / 결제창 | 37 (£4,850), mrcreates 결제창 $497 (REF 기록) |
| 자릿수 카운터 위젯 | 38 (00,000 → 12,480), 35 (600 sales 카드) |
| 깔때기 + 입자 | 35 |
| 진행 링 차트 (%) | 40 (86%) |
| 알림 스택 + 뱃지 (입금 알림형) | 42 (New order £28·£96, 뱃지 2) |
| 도넛 (조각마다 이름+%, 가운데 원형 사진) | 17 (SPY·QQQ 39%, GLD·BTC 5%, TLT 2%), «*정보 출처» 각주 |
| 동전 / 금괴 아이콘 | 17 (비트코인 동전, GLD 금괴), 02 (돼지저금통 + $ 동전) |
| 지폐 다발 · 은행 건물 · 통장 책 · TAX 체크리스트 | 02 (CMA 책 + 지폐, BANK, IRP 책, TAX 클립보드) |
| 상승 차트 카드 (지수명) | 02 (S&P500 / NASDAQ100) |
| 4색 구간 + 캔들형 가격선 + 연도 반복 | 05 (침체·회복·상승·과열) |
| 선 2개 비교 + 끝점 큰 금액 라벨 | 10 (몰빵 59.5억 vs 적립 22.1억, 영상). 20·21은 REFS 기준, 안 봄 |
| 번호 박스 행 + 오른쪽 일러스트 | 02 (1~5) |
| 표 (행×열 조회표, 비율 막대) | 01·06·18·24 (REFS 기준, 안 봄) |
| 순위 막대 · 별점 비교표 · 격자 인포 | 23 · 22 · 19 (REFS 기준, 안 봄) |
| 티커 칩 | 02 (QQQ·SOXX 칩), 17 (티커 글자). 흐르는 시세 띠(ticker tape)는 어느 레퍼에도 확인 안 됨 |
| 캘린더 블록 | 41 (적립일 같은 용도로 바꿔 쓸 수 있음) |
| 영수증 | 레퍼 이미지에는 없음. Stageshow framing의 «Tilted stack / Satellite focus» 규칙에만 나오고, 우리 rail `receipt` 부품은 이미 있음 |
| 체크리스트 / 토글 | mrcreates 레일·토글 (REF 기록) |

## 관련 파일

- 하마-제작실/레퍼런스/REFS.md (7절에 charliehills 정리, 12개 장면 표)
- 하마-제작실/레퍼런스/shots/30~42-charliehills-claude-motion.png (프롬프트 원문)
- REF/_index.md (mrcreates 흐름 11단계)
- 뮤즈 볼크/2026-10-27-참조-클로드-코드-자동-편집.md (장면 6개)
- 뮤즈 볼크/2026-11-02-링크-브레인.md (낭만빌더 스타일 시트)
- 엔진/motion/number-story.html, 엔진/motion/rail/parts.py (이미 있는 것)
- ~/.agents/skills/stageshow/references/motion.md (이징·스태거 수치)
