---
id: hama-ref-fx-registry
type: reference
track: invest
status: active
last_review: 2026-11-04
---

# 효과 후보 — HyperFrames 레지스트리 (CLI 0.9.12, 448개)

1080x1920 인스타 릴스 엔진(GSAP 정지 타임라인 하나, 흰 모눈종이, 금색 강조 하나)에 쓸 수 있는 레지스트리 블록과 컴포넌트, 그리고 문서에 적힌 모션 레시피를 정리한 조사 기록입니다.

## 조사 방법

- 읽은 문서: `~/.claude/skills/hyperframes-registry/SKILL.md`와 references, `~/.claude/skills/hyperframes/references/`의 motion.md, film.md, overlays.md, runtimes.md, types/vertical.md, types/data.md
- `npx hyperframes catalog --json`(CLI 0.9.12)으로 448개 전체를 뽑았습니다. 효과마다 영어로 검색했습니다(`words` 등급).
- 후보 53개는 스크래치 폴더에만 `add`해서 소스를 열어 봤습니다: `/private/tmp/claude-501/-Users-harimgemmajung-Gaia-----------/17d9f03e-399f-4e83-9aa9-842effa300e1/scratchpad/reg/`. 어떤 프로젝트에도 설치하지 않았습니다. 세션 스크래치라서 나중에 지워질 수 있습니다.
- 렌더는 돌리지 않았습니다. 표의 "모양" 칸은 카탈로그 설명과 소스 주석을 근거로 썼습니다.

## 넣는 방식 세 가지 (S / M / B)

- **S (붙여넣기 조각)**: 마크업, CSS, `tl.fromTo(..., startTime)` 몇 줄짜리입니다. 우리 타임라인에 그대로 넣으면 됩니다. 판정 **yes**.
- **M (마운트형 하위 장면)**: `#root`가 부모 상자를 채우고 크기가 `container-type:size` / `cqmin` 단위라 1080x1920에 그냥 맞습니다. 다만 자기 `gsap.timeline({paused:true})`를 `window.__timelines["이름"]`에 따로 등록합니다. 그대로 `data-composition-src`로 붙이면 타임라인이 두 개가 되어 "한 타임라인" 규칙을 어깁니다. 판정 **needs change (작음)**.
  - 고치는 법: IIFE를 복사하고 id(`#root`, `#tpr-from` 등)에 접두사를 붙입니다. 등록 줄을 `master.add(tl, t0)`로 바꿉니다. 슬롯은 `<template data-slot>`입니다.
- **B (1920x1080 블록)**: 화면 크기가 1920x1080으로 박혀 있습니다. 세로로 다시 짜야 합니다. 판정 **needs change (큼)**.

공통 주의: 강조색 변수는 거의 다 `green | blue | violet`뿐이고 gold가 없습니다. CSS의 `--accent`/`--brand` 토큰을 우리 금색으로 덮어써야 합니다. 기본 데모는 어두운 바탕이나 컬러인 것이 많아 흰 모눈종이에 맞게 다시 입혀야 합니다.

## 후보 표

기호 설명:
- "판정" 칸 = 우리 단일 정지 타임라인 안에서 1080x1920으로 돌릴 수 있나
- "넣는 법"의 `add` = 엔진 레포에서 `npx hyperframes add <이름>` (실행은 하림님 승인 후)
- 이야기 순간: 손실=loss, 비교=compare, 쌓임=accumulate, 단계=steps, 경고=warning, 드러냄=reveal

### 전환

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `torn-paper-rip` | 섬유결 있는 종이 찢김이 화면을 가로지르고, 윗장이 그림자를 달고 들립니다. tone에 `white`·`cream`·`kraft`, roughness 20~90. 시드 고정, rAF 없음 | 손실, 드러냄 | needs change(M) | IIFE 이식. from/to 슬롯에 장면 둘 |
| `paper-collage-reveal` | 찢은 종이 조각 6장이 흩어지며 밑 내용을 드러냅니다. tone `cream`·`kraft`·`mixed` | 드러냄 | needs change(M) | IIFE 이식 |
| `zoom-through-transition` | 초점 카드 안으로 뚫고 들어가 다음 장면으로 갑니다 | 드러냄, 단계 사이 | needs change(M) | IIFE 이식. depth 변수 |
| motion.md 레시피 "버튼 통과 줌" | 버튼 쪽으로 카메라가 블러 0.6초 → 버튼이 8%에서 250%로 0.35초, 강한 ease-in. 버튼 색이 다음 화면이 됩니다 | 드러냄 | yes(레시피) | 우리 tl에 직접 씁니다 |
| `modal-morph` | 작은 카드가 transform만으로 큰 패널로 펼쳐집니다(공유 요소 방식) | 단계, 드러냄 | needs change(M) | IIFE 이식 |
| `morph-swap` | A가 줄거나 모양을 바꾸며 B가 됩니다. 중심을 공유 | 비교 | needs change(M) | IIFE 이식 |
| `card-resize` | 작은 카드가 상세 패널로 커집니다 | 단계 | yes(S) | 조각 붙이기 |
| motion.md 레시피 "모프" | 컨테이너가 110px에서 880px로 0.2초 `power3.out`, 가로 블러 12→0 | 단계 | yes(레시피) | 직접 |
| 페이지 넘김(page curl) | 없음. 검색 결과가 `page-slide`뿐입니다 | 없음 | 없음 | 직접 제작 필요 |
| `transitions-destruction` | 1920 쇼케이스 안에 "Page Burn" 1종(캔버스) | 손실 | needs change(B) | 참고용. 그대로 쓰기 어렵습니다 |
| `vfx-shatter` | three.js + html-in-canvas로 화면이 조각나 깨집니다. `chrome://flags/#canvas-draw-element`가 필요합니다 | 손실, 경고 | no | 쓰지 않는 것을 권합니다 |
| `glitch` (블록) | 셰이더 디지털 글리치 | 경고 | needs change(B, WebGL). 세로 동작은 확인 안 됨 | add 후 검증 |
| `rgb-glitch-text` | 글자 빨강/청록 분리 지터. tone `ink`는 흰 바탕용 | 경고 | yes(S) | 조각 붙이기 |
| `whip-pan-cut` | 가로 휩 + 방향 블러. A와 B 속도를 맞춤 | 단계 사이, 비교 | needs change(M) | IIFE 이식 |
| `cut-the-curve` | 속도를 맞춘 방향 하드컷 | 단계 사이 | needs change(M) | IIFE 이식 |
| `whip-pan` (블록) | 셰이더 휩 | 단계 사이 | needs change(B, WebGL) | 위 `whip-pan-cut`이 낫습니다 |
| `iris-reveal` | 원형 clip-path가 지정한 점에서 열립니다 | 드러냄 | needs change(M) | IIFE 이식 |
| `directional-wipe` | 패널이 밀려 덮이는 와이프. RGB 번쩍 포함 | 단계 사이 | yes(S) | 조각 붙이기 |
| `halftone-dissolve` | 망점이 자라며 A가 B로 녹아듭니다. 잉크 점 1색 | 드러냄 | needs change(M). 캔버스 포함 | IIFE 이식 |
| `grid-pixelate-wipe` | 격자 사각형이 시차를 두고 사라집니다 | 단계 사이 | yes(S로 추정). 소스는 확인 안 됨 | add 후 확인 |

### 빛, 카메라, 3D

| id | 종류 | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|---|
| `light-leak` (블록) | 전환 | 셰이더 필름 빛샘. 장면을 텍스처로 캡처합니다 | 드러냄 | needs change(B, WebGL). 세로 동작은 확인 안 됨 | 쓰지 않는 것을 권합니다 |
| `organic-light-leak-overlay` | 오버레이 | CSS만 쓴 빛샘 층, 시간축 제어 | 드러냄 | needs change(B, 1920 고정, CSS라 고치기 쉬움) | 레이어만 떼어 쓰기 |
| `light-sweep-pass` | 오버레이 | 사선 키라이트 띠가 한 번 지나가며 음영을 바꿉니다 | 드러냄, 마무리 | needs change(M) | IIFE 이식 |
| `text-shimmer` | 오버레이 | 제목 글자에 반사광이 한 번 지나갑니다 | 드러냄 | needs change(M) | IIFE 이식 |
| `transitions-3d` | 3D | 1920 쇼케이스. rotationY 뒤집기 전환(종류 수는 확인 안 됨) | 비교 | needs change(B) | 레시피만 참고 |
| `camera-rig-depth-stack` | 3D | 카드 스택이 rotateX/Y와 z로 기울며 초점을 옮깁니다 | 쌓임, 비교 | yes(S) | 조각 붙이기 |
| `keyframe-scrub-stack` | 3D | 카드 3장이 back.out으로 겹쳐 쌓입니다 | 쌓임 | yes(S) | 조각 붙이기 |
| `spring-stack-shuffle` | 3D | 카드 3~5장 스택이 신호마다 뒤장이 앞으로 넘어오며 섞입니다 | 단계 | needs change(M) | IIFE 이식 |
| `split-tilt-cards` | 3D | 두 카드가 좌우에서 책 펼치듯 rotateY로 들어옵니다 | 비교 | needs change(M) | IIFE 이식 |
| `exploded-stack` | 3D | 아이소메트릭 판이 층별 라벨을 달고 벌어졌다 닫힙니다 | 단계(구조) | needs change(B, three.js WebGL) | 무겁습니다 |
| `tilt-card` | 3D | 깊이층 기울임 카드 | 드러냄 | yes(S) | 조각 붙이기 |
| `device-frame-stage` | 3D/UI | 폰 목업이 무대에 올라와 자리 잡습니다. 화면은 슬롯 | 단계 | needs change(M). 1920 기본값 있음 | IIFE 이식 |
| `parallax-device-dive` | 카메라 | 폰이 올라온 뒤 카메라가 화면 속으로 뚫고 들어갑니다 | 드러냄 | needs change(M) | IIFE 이식 |
| `push-in` | 카메라 | 가운데 제목에 느린 푸시인 | 경고 | needs change(M) | motion.md가 "느린 크립 스케일"을 생성물 티로 경고합니다 |
| `yt-camera-move` | 카메라 | 줌, 슬라이드, 3D 틸트팬 도우미 | 전반 | needs change(M) | 도우미 함수만 떼어 쓰기 |
| `before-after-wipe` / `comparison-split` | 오버레이 | 분할선이 before 위로 after를 밀어 덮고 멈춥니다 | 비교 | 앞은 확인 안 됨, 뒤는 needs change(M) | IIFE 이식 |

### 차트와 숫자

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `count-up` | 숫자가 올라가거나 내려가 작은 스케일 펄스로 착지. prefix/suffix 지원 | 쌓임, 손실 | needs change(M) | IIFE 이식 |
| `number-wheel` | 자릿수별 드럼이 굴러갑니다(odometer). spin 1~3회, tone `accent` | 쌓임 | yes(S) | 조각 붙이기 |
| `slot-machine-roll` | 슬롯머신 릴 글자 굴림 | 드러냄 | yes(S) | 조각 붙이기 |
| `number-pop-in` | 숫자가 블러에서 떠오르며 나타납니다 | 드러냄 | yes(S로 추정). 확인 안 됨 | add 후 확인 |
| `split-flap-board` | 공항 안내판식 플랩이 글자를 넘겨 착지 | 드러냄 | needs change(B) | 세로로 다시 짜기 |
| `ticker-takeover` | 모노 티커가 굴러가다 단어에 멈추고 번쩍인 뒤 전면 제목이 됩니다 | 드러냄, 경고 | needs change(M) | IIFE 이식 |
| `chart-story` | type에 `bars`·`line`·`donut`·`progress`. 읽는 순서대로 그려지고, emphasize로 강조할 하나를 고릅니다 | 비교, 쌓임 | needs change(M) | IIFE 이식. data/labels/unit 변수 |
| `decline-chart` | 지표 선이 내려가며 숫자가 줄고 배경이 어두워집니다 | 손실, 경고 | needs change(M). 어두워지는 효과를 흰 종이에 맞게 손봐야 합니다 | IIFE 이식 |
| `animated-bar-chart` | 막대 성장 + 선 그리기 작은 카드 | 쌓임 | yes(S) | 조각 붙이기 |
| `conic-progress-ring` | 원형 진행 링과 가운데 숫자 | 쌓임 | needs change(M) | IIFE 이식 |
| `mk-usage-arc` | 얇은 원형 게이지와 % 카운트 | 쌓임 | needs change(1920 표기 있음) | 이식 |
| `mk-line-graph` / `mk-progress-stat` | 미니멀 선 그래프 / 큰 숫자 + 진행 바. 라이트 테마 있음 | 비교 / 쌓임 | needs change(B) | 세로로 다시 짜기 |
| `data-chart`, `bar-chart-race` | NYT식 막대+선 / 막대 순위 경쟁 | 비교 | needs change(B) | 세로로 다시 짜기 |
| 주식 시세(stock ticker) 차트 | 전용 블록 없음. `news-ticker`는 방송 자막 띠입니다 | 없음 | 없음 | `decline-chart`나 `chart-story`의 line으로 대체 |

### 입자

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `apple-money-count` (블록) | $0에서 $10,000까지 카운트, 초록 번쩍, 지폐·동전 아이콘 62개가 시드 고정으로 터집니다. 효과음 wav 포함 | 쌓임 | needs change(B, 1920) | 동전/지폐 폭발 코드만 떼어 쓰기 |
| 동전/돈 입자 전용 | 없음 | 없음 | 없음 | 위 블록에서 떼어 쓰기 |
| `confetti` | 시드 고정 입자 폭발과 중력. 색이 5가지 | 드러냄(보상) | yes(S) | 색을 금색 하나로 덮어쓰기 |
| `caption-particle-burst` | 키워드에서 입자가 터집니다 | 쌓임 | 확인 안 됨 | add 후 확인 |

### 자막과 글자

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `caption-highlight` | 단어마다 배경 박스가 쓸고 지나갑니다(틱톡식, 기본 빨강) | 전반 | needs change(1920 표기 있음, 자체 tl) | 이식, 색은 금색 |
| `inline-highlight` | `--hf-highlight-scale` 0→1로 형광펜 띠가 칠해집니다 | 드러냄 | yes(S) | 조각 붙이기 |
| `marker-highlight` | 손그림 마커(하이라이트, 동그라미, 밑줄, 낙서)가 강조 단어 위에 그려집니다 | 경고, 드러냄 | needs change(M) | IIFE 이식 |
| `mk-callout-highlight` (블록) | 값 하나로 단어별 강조(가라오케) | 전반 | needs change(B) | 이식 |
| `per-word-rise`, `blur-in`, `staggered-fade-up` | 단어별로 블러에서 선명해지거나 올라옵니다 | 전반 | yes(S로 추정). 소스는 확인 안 됨 | add 후 확인 |
| `kinetic-type-swap` | 문장은 고정, 한 단어 칸만 슬롯처럼 바뀝니다 | 비교 | 확인 안 됨 | add 후 확인 |
| `strikethrough-replace` | 옛 글자에 취소선을 긋고 새 글자가 나타납니다. tint red/amber, tone `ink` | 손실, 비교 | yes(S) | 조각 붙이기 |
| `hw-underline` | 손그림 물결 밑줄과 두 번 긋는 취소선 | 손실 | 확인 안 됨 | add 후 확인 |

### UI 소품 (체크, 토글, 영수증)

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `marker-checklist-card` | 종이 카드 위에 마커 제목과 동그라미 단어, 체크 3줄이 스스로 그려집니다 | 단계 | needs change(M) | IIFE 이식. l1~l3, v1~v3 변수 |
| `mk-specs-list` (블록) | 줄이 미끄러져 들어오며 강조 밑줄이 쓸고 지나갑니다. 라이트 테마 있음 | 단계 | needs change(B) | 이식 |
| `success-check` | 링이 튀어나오며 체크 경로가 그려집니다 | 단계 완료 | yes(S) | 조각 붙이기. tint는 green/amber 고정이라 덮어쓰기 |
| `toggle-flip` | 큰 토글이 엄지 오버슈트와 함께 넘어갑니다 | 비교(켜기/끄기) | needs change(M) | IIFE 이식 |
| `settings-toggle-flow` | 설정 줄 3개 + 토글 | 단계 | yes(S) | 조각 붙이기 |
| 영수증/프린터 | 없음 | 없음 | 없음 | 직접 제작 |

### 지도

| id | 모양 | 이야기 순간 | 판정 | 넣는 법 |
|---|---|---|---|---|
| `world-map` (블록) | D3 세계 단계구분도 + 회전 지구 인셋 | 비교 | needs change(B) | film.md는 실제 장소를 구운 위성 영상으로 보여주라고 합니다 |

## 돈 교육 릴스용 상위 10 (추천 순)

1. **`number-wheel`** (S, yes): 금액이 자릿수별로 굴러 착지합니다. 그대로 붙여 쓸 수 있고 tone `accent`를 금색에 연결하면 됩니다. "쌓임"의 핵심입니다.
2. **`strikethrough-replace`** (S, yes): "$4.99 → $0" 같은 손실·비교 한 줄에 맞습니다. 잉크 바탕에 strike 색만 금색이나 붉은색으로 바꾸면 됩니다.
3. **`chart-story`** (M): 막대, 선, 도넛, 진행 바를 한 부품으로 처리하고 강조할 하나를 고를 수 있습니다. data.md의 "하나만 강조, 나머지 회색" 원칙과 맞습니다.
4. **`torn-paper-rip`** (M): `tone:"white"`로 흰 모눈종이 위 찢김 전환이 됩니다. 시드 고정이고 결정적입니다. 손실이나 드러냄 장면에 씁니다.
5. **`inline-highlight`** (S, yes): 금색 형광펜 띠입니다. "강조 단어 하나만 강조색" 규칙과 맞습니다.
6. **`marker-checklist-card`** (M): 종이 카드에 체크 3줄이 그려집니다. 단계 장면용이고, 종이 질감이 우리 톤과 같습니다.
7. **`count-up`** (M): 큰 숫자를 올리거나 내리고 펄스로 착지합니다. tabular 숫자 사용 여부는 확인 안 됨. 손실 장면은 내려가는 방향으로 씁니다.
8. **`decline-chart`** (M): 경고나 손실 장면에서 선이 꺾이고 숫자가 줄어듭니다. 배경이 어두워지는 부분은 흰 종이에 맞게 꺼야 합니다.
9. **`camera-rig-depth-stack`** / **`keyframe-scrub-stack`** (S, yes): 카드 쌓임을 3D 깊이로 보여줍니다. "쌓임"과 "비교"에 씁니다.
10. **`zoom-through-transition`** 또는 motion.md "버튼 통과 줌" 레시피: 장면 사이를 화면 속 물체를 통해 넘어갑니다. motion.md 기준 "슬라이드처럼 느껴질 때" 처방입니다.

번외: `apple-money-count`의 동전·지폐 폭발 코드는 떼어 쓸 가치가 있습니다(블록 전체는 1920이라 B). `confetti`는 단색으로 바꾸면 보상 장면에 씁니다. `device-frame-stage`, `parallax-device-dive`도 폰 목업이 필요한 장면이면 후보입니다.

## 직접 만들어야 할 것 (카탈로그에 없음)

- 페이지 넘김(page curl)
- 영수증/프린터
- 동전 입자 전용 부품
- 주식 시세 차트
- 아이소메트릭 카드 부채꼴: 가장 가까운 것이 `exploded-stack`인데 WebGL이라 무겁습니다
- 가벼운 산산조각(shatter): `vfx-shatter`는 Chrome 플래그가 필요해 쓰지 않습니다

스킬 규칙상 이런 빈칸은 `npx hyperframes feedback --search-miss ...`로 신고하게 되어 있습니다. 외부로 보내는 일이라 보내지 않았고, 하림님 판단으로 남겨 둡니다.

## 확인 안 됨

- 렌더로 직접 보지 않았습니다. 모양은 설명과 소스 주석 기준입니다.
- 소스를 열지 않은 항목: `grid-pixelate-wipe`, `number-pop-in`, `per-word-rise` 계열, `kinetic-type-swap`, `hw-underline`, `before-after-wipe`, `caption-particle-burst`
- 셰이더 블록(`glitch`, `light-leak`, `whip-pan`)의 1080x1920 동작
- `transitions-3d` 안에 든 전환의 수
- 하위 타임라인을 `master.add()`로 끼웠을 때 `onUpdate` 기반 paint가 그대로 도는지: GSAP 동작상 될 것으로 보지만 실제로 돌려 보지는 않았습니다
