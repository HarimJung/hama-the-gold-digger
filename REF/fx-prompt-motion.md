---
id: hama-ref-prompt-motion
type: reference
track: invest
status: active
last_review: 2026-11-04
---

# Prompt Motion — Opus 5.5 모션 영상 + 프롬프트 갤러리

- 주소: https://prompt-motion.com/ (하림님이 2026-11-04 링크로 줌)
- 무엇: «A collection of motion videos made with Claude Opus 5.5, with the prompts and skills behind them.» 운영 «Curated by @p4nthera_». 영상·프롬프트 저작권은 각 제작자.
- 읽은 범위(11/04): 홈 앞부분, `/templates`, 항목 4개. 나머지 약 118개 항목의 제목·프롬프트는 **확인 안 됨**.
- 카테고리(항목 수, 원문): Product UI 105 · Phone 22 · Charts 34 · Diagrams 31 · Kinetic type 98 · Shapes 43 · Particles 43 · Characters 27 · Photos 23 · Music 51 · Code 21. 유형 필터 Prompt / Skill.

## 프롬프트 원문 (읽은 것만, 손대지 않음)

### 1. «showreel» 프롬프트 — 가장 많이 쓰임 (49편)

@stephanlivera «Claude motion designer showreel» (https://prompt-motion.com/stephanlivera-df17a2), @shneural, @ajith_io 가 같은 문장. Opus 5.5 · Effort Max.

```
make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out.
```

- `/templates/showreel` 은 이 프롬프트를 칸으로 바꾼 템플릿. 원문 **확인 안 됨**.

### 2. «Shape morphing through UI states» — @twoclipping (https://prompt-motion.com/twoclipping-5cba86)

태그 Product UI · Charts · Music. Stack HTML + Playwright. 1440×1440, 60fps.

```
<inputs> Ask me for: 8 to 12 UI states I want the shape to become (e.g. button, loader, player, slider, toggle, tabs, chart, command palette, toast), pure black and white or one accent color, and a royalty-free song around 120 BPM (e.g. Mixkit, free for commercial use). </inputs> <direction> Dribbble-level UI motion. One shape, never cut: every state is the same element morphing its size, radius and color while its content swaps with a short blur. A cursor drives every change with real clicks and drags. Light warm-gray canvas, black and white components, one clean UI font (Geist). Springs everywhere, a tiny overshoot at most. The camera zooms so each state fills the frame. The last frame is the first frame, so it loops. Banned: bouncy easing, particle bursts, glows, gradients on UI chrome, mismatched icon strokes, dead time, anything that looks like a template. </direction> <structure> 120 BPM, 7 bars, something happens on every beat. Button → loader → check → dynamic island → music player with a play/pause morph → scrub the progress bar → it becomes a volume slider that stretches when dragged past max → a toggle flips on the beat → the knob becomes a liquid tab indicator → the tabs open into a chart that draws itself, with a tooltip on hover → it collapses into ⌘K → type to filter → enter → toast → back to the button. </structure> <build> 1. One HTML file, square 1440x1440. Every style is computed from time inside seek(t): no CSS transitions, no timers, no state carried between frames. 2. Springs are closed-form step responses. A value that changes target many times is the sum of one spring per change, so it stays a pure function of time. 3. The tab indicator's two edges ride different springs, so the leading edge stretches ahead of the trailing one. Same trick for the toggle knob. 4. Drags are direct manipulation: while the cursor is held, the value is computed from its position. On release it springs back from wherever it was. 5. Analyze the song with numpy for the beat grid and start on a downbeat. Place every UI sound by its measured peak. 6. Render with Playwright: 4 subframes per frame, blended with ffmpeg tmix for motion blur at 60fps. 7. Render one frame per beat before the full render. Fix anything off the grid, cramped or hard to read. </build> <gotchas> Never put will-change on anything the camera scales or the text renders blurry. Text that swaps inside a morphing container needs its own enter and exit timing or it overlaps. Make the last frame identical to the first, cursor position and speed included, or the loop stutters. </gotchas> <start> Ask me for the inputs, then show me the state list on the beat grid before you write any code. </start>
```

## 하마 엔진에 옮길 것 (제안, 승인 전)

- **한 물건이 끊기지 않고 모양을 바꾼다(morph).** 버튼 → 로더 → 체크 → 카드 → 차트. 레일 릴스 장면 사이를 «페이드» 대신 같은 카드가 변하는 것으로 잇는 전환 후보.
- **커서가 직접 누르고 끈다.** 금액 고르기·토글·슬라이더에 커서를 넣으면 «내가 하는 것» 느낌. mrcreates 탭 리플과 같은 계열.
- **스프링 두 개로 늘어나는 지시자**(앞 가장자리가 먼저 간다). 탭·토글 손잡이에.
- **4 서브프레임 + tmix 모션 블러.** HyperFrames 렌더 뒤 ffmpeg 로 붙일 수 있는지 **확인 안 됨**.
- **박자마다 하나씩.** 음악은 보류(11/04)지만, 목소리 단어를 박자 대신 쓰는 지금 방식과 같은 원리.
- 금지 목록(바운스 이징·파티클·글로·템플릿 티)은 이 작가의 취향. 우리는 레퍼가 쓰는 금빛 글로·별을 쓰므로 그대로 따르지 않는다.
