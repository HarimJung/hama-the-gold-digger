---
id: hama-motion-rail
type: index
track: invest
status: active
last_review: 2026-11-04
---

# 레일 릴스 틀 (mrcreates 문법, 골드 하나)

2026-11-04 하림님 «존나 좋다, 이렇게 하자». 레퍼(@mrcreates 682K 릴스, `REF/_index.md`)를 똑같이 따르고 색은 골드 하나, 내용은 하마 돈 이야기.

## 돌리기

```
python3 엔진/build.py 콘텐츠/31일/<편>.json --rail --render
```
→ `엔진/out/<편>-rail/` (HyperFrames 프로젝트) + `엔진/out/<편>-rail.mp4`

## 네 층

| 층 | 파일 | 바뀌나 |
|---|---|---|
| 피부 | `skin.css` | 동결. 모눈·골드·자막 상자·배지·카드 |
| 부품 | `parts.py` | 늘어난다. 부품 하나 = 함수 하나 → 화면 + 움직임 (+ 틱 시각) |
| 배선 | `build_rail.py` | 장면별 TTS → 장면 길이 → 단어 자막 → 레일·배지·아바타 → 숫자 관문 |
| 대본 | 편 json 의 `reel{}` | 편마다. `beats[{say, part?, badge?, data?}]` |

- `say` 는 자막 그대로 쓴다. 숫자는 `$122,000` 처럼, 강조 단어는 `*별표*`. 읽을 때만 말로 바꾼다(Kokoro 가 숫자를 «dollar 122, 000» 으로 읽어서).
- `part` 가 없는 장면은 앞 부품을 이어 간다. 부품 안의 «이 단어에서 움직여라»는 `data` 의 `*_at` 단어로 건다.
- 숫자 관문: `reel` 의 `$`·`%` 숫자가 같은 json(fact·slides·caption)에 없으면 빌드가 멈춘다.
- 목소리: Kokoro `af_heart` (하림님 목소리 전까지). 가상환경은 저장소 밖 `~/.local/share/hama-tts`. 캐시는 `out/.tts-cache/`.
- 음악: 보류(11/04). 틱 소리만.
- **물건도 움직인다(11/04 하림님).** «글자만 모션·물건 scale 팝 금지»(11/03)는 폐기. 찢어짐·3D 카드·폰 팝·줌 같은 물건 전환을 쓴다. 남는 주의 하나: 둥근 틀 안 하마 얼굴이 튕기는 이징에 잘리지 않게 틀째 움직인다.

## 부품 (2026-11-04)

hook · checkout · amount · toggle · counter · split · checklist · compare · tiles — 동결본 `~/Desktop/AI Video Editor/hama-100/src/template.2026-11-04-liked.html` 과 프레임 비교로 같음을 확인.

다음 부품(하마 전용, 한 라운드에 1~2개): 금 · 동전 더미 · 영수증 · 장표 · 돈 · 비트코인 · 주식. 움직임 레퍼는 하림님이 준다.

## 1라운드 (11/04): 전환·글자 — 쓸 때만 켜진다

대본에 안 쓰면 11/04 동결본과 같다. Day 4 를 다시 빌드해 본문 지문이 같음을 확인했다.

| 칸 | 어디에 | 하는 일 (fx-목록) |
|---|---|---|
| `"in":"pan"` | 장면 첫 beat | 앞 장면이 위로, 새 장면이 아래에서 올라옴 (D2) |
| `"in":"dissolve"` | 장면 첫 beat | 블러 겹침 전환 (D6) |
| `"out":"tear"` | 장면 첫 beat | 장면 끝에 지그재그로 찢겨 두 쪽이 떨어짐 + 금 별 (D1) |
| `"dark":true` | 장면 첫 beat | 그 장면 동안 검정 모눈 바탕, 자막 흰색 (D8). 손해 장면에만 |
| `"caption":"blur"` | rail{} | 자막 단어가 흐림 8px 에서 들어옴 (T1) |
| 부품 `swap` | | 큰 단어가 흐려지고 새 단어가 글자마다 올라옴 + 이탤릭 한 줄 (T3) |
| 부품 `stack` | | 아이소 3D 판이 날아와 쌓임 → 한 판 골드 강조 → 바로 서며 위아래로 나란히 (D3·H8) |
| 부품 `coins` · `receipt` | | 동전 더미 (H1) · 영수증 프린터 (H2) |

- 대본 칸 이름: 새 편은 `rail{}`. Day 4 는 `reel{}` (둘 다 읽는다). 예전 `reel{}` 메모 칸이 있는 편은 덮어쓰지 않는다.
| 부품 `chart` (11/05) | | 진짜 주가 창(엔진/chart.py, 밝은 하마 피부). 창 하나면 선이 그려지고 등락률이 튄다. 단기+장기 짝이면 한 달 선(로즈) → ZOOM OUT → 10년 선(골드) + 이번 달 구간 로즈. 감독이 chart 장이 있는 편의 compare 장면(없으면 첫 loss·myth·catch)에 건다 |
| 마이너스 숫자 (11/05) | | `-72%` 같은 단어·큰 숫자는 처음부터 로즈 (`.neg`). 훅이 부호를 달면 큰 숫자도 부호째 |

- 부품 안의 id 와 전환 id 가 겹치면 깨진다(11/04 영수증 `-hl` 사건). 전환은 `-tL`·`-tR`·`-sp` 만 쓴다.
- 시험판: `콘텐츠/31일/2026-11-03-01-main-v4.json` rail{} → `out/2026-11-03-01-main-v4-rail.mp4` (Day 2 · US dividends, 32초).

## 3단계 3라운드 (11/07): 첫 장면 5종 추가 (레퍼 `REF/fx-kyleherbel.md`)

첫 장면 10종 = hooknum · title2 · slam · tease · rollnum + **rise**(T4 마스크 상승) · **cover**(K2 잡지 표지, 마스트헤드 = 대상 이름) · **boil**(K3 손그림 선 떨림, 숫자·얼굴 둘레) · **glass**(K4 유리 글자 뒤, 긴 이름은 핵심 낱말 하나) · **window**(K5 당겨 나오는 창). 데이터는 전부 hooknum 과 같은 `opener_data`. 정본: `parts.py` + `skin.css` + `director.OPENERS`/`build_rail.OPENERS` + `hooks.json shapes.*.opener_pref`(꼴마다 순서). 기존 47편은 그대로이고 새 감독·`--reopen` 때 least_used 로 들어간다. 시험판 `out/작업/r3-<이름>-rail/`, MP4 `out/릴스/3단계-샘플/r3-*.mp4`. T8 굵기 파도는 피부에 가변 폰트가 없어 보류.

## 11/07 저녁: 하림님 «줌아웃 안 맞고·US 어스·말만 많고 모션 없음» → 규칙 (정본 한 곳씩)

- 주가 창 장면: «zoom out·fell·sits below» 줄에만 (맨 % 는 수수료 줄도 잡았다). 줌아웃 짝 = 같은 티커 짧은 창→긴 창. 티커가 둘이면 둘째 창이 둘째 티커를 말할 때 아래로. 그리기는 줌 줄보다 앞 (빈 창 금지).
- 장면은 멈추지 않는다: 모든 장면 느린 푸시인(scale 1→1.035) + 말 줄마다 범프 (build_rail). 관문 `--review` 가 «정지 N초»(STILL_MAX 5초, 자막 제외) 를 잰다.
- 장면 쪼개기 3줄부터 · 오도미터는 $100 이상 · `US$87,249` → «… U.S. dollars».
- `build.py --redirect`: 대본 그대로, 매핑만 새 규칙으로 (모델 없이). 47편 일괄은 하림님 판정 뒤.

## 4라운드 (11/07 저녁, 두 세션 분담 · claude-37): 가족 7개 ○→● + 정지 금지 + 납품 층 + 낯선 사람 읽기

- 하림님 «나는 정지 너무 싫어, 정지하면 사람들이 넘겨» → 기준 `hooks.json grammar.still_max` 1.5초 (review 트윈 정지·deliver 실측 정지 둘 다). 원인 실측: 긴 숫자 토큰(«$156,700» 2.4초 발음) 동안 그림·자막이 안 바뀜. 고침은 전부 결정론(build_rail «7 정지 금지»): ① 숫자 낱말을 1초 넘게 읽으면 자막 낱말 아래 골드 바가 읽는 동안 자라고(`.w --sw` / `.em --box`), 첫 장면 큰 숫자는 글자가 차례로 튀며(`parts.dg` 글자 span, 밑줄도 그 구간) · 이어지는 줄의 숫자 칩은 0 → 숫자로 센다 ② 그림 트윈 틈이 `grammar.gap_max`(1.5초) 넘으면 말하는 낱말 칩 → 자막 낱말 펄스 → 얼굴 끄덕임(자막 없는 장면, 장면당 2번, 마지막 수단) ③ odometer·counter·coins 의 숫자 움직임 길이 = 그 숫자를 말하는 구간(`Seg.span`) ④ 첫 장면(parts): 말하는 낱말이 튀고(`_karaoke` scale), 약속 낱말은 올라오며 첫 낱말에 얼굴이 끄덕이고(`_promise`), 도장은 큰 숫자를 다 읽는 순간 다시 쾅(`ostamp`). 숫자 문턱 0.8초, 공백 관문은 색만 바뀌는 카라오케 트윈을 움직임으로 안 센다. 실측은 ffmpeg freezedetect(n=0.001, 자막 포함) — 색·투명도·얇은 선만 바뀌면 기계도 눈도 멈춘 걸로 본다. 푸시인 같은 멈춤 가리기는 안 쓴다.
- 부품 7개 `parts.py`+`skin.css`(fx-목록 ●): **fan**(D5 카드 부채→세로 목록+골드 체크, check) · **hub**(U7 하마 허브 둘레 항목 0/N→N/N, check 2~4개) · **paid**(U10 버튼→골드 링→체크→DONE + 금액 줄, step) · **tabs**(U2 알약 미끄러짐 old→new, step·rehook) · **tag**(T9 라벨 커짐+별+결과 칩, myth·catch·rehook) · **tail**(T10 결론 $·%+골드 줄+이탤릭 꼬리, closing·loss, 돈이 있을 때만) · **badge**(U14 ✓ old → ! new 로즈, catch·myth). 지금 대본의 데이터 꼴(items · label/sub · old/new)만 받아 `--redirect` 로 들어간다. 1순위 분리는 `hooks.json grammar.roles`(check 가 checklist 하나뿐이던 것, flip 다섯 역할이 글자교체에 몰리던 것을 푼다).
- 납품 층 `엔진/deliver.py`: 렌더 뒤 실제 MP4 를 잰다(−14 LUFS 2패스 loudnorm, 자막까지 멈춘 정지 ≥1.5초, 검은 프레임, 첫 프레임 평탄도, 릴스 스펙). `hook.py rebuild` 끝에서 `deliver.check(stem, norm=True)`. 표 `out/작업/deliver.md`. ffmpeg 만 쓴다(ffmpeg-skill 설치 불필요).
- 낯선 사람 읽기 `엔진/reader.py`: haiku 가 대본만 읽고 «이게 뭐야·숫자 하나·나는 뭘 해»를 답하고 subject·felt·plain.do(뜻 겹침 포함)와 대조. 경고만, 재작성 없음(레드팀 3번). 표 `out/작업/reader.md`. 기준선(11/07, 고치기 전) 51편 중 48 통과.
- 격리 시험대: scratchpad `r4/harness.py` — build_rail 뼈대 그대로 한 부품 = 한 HyperFrames 프로젝트 → `snapshot --at` → 대지 1장. 새 부품은 여기서 프레임을 보고 붙인다.
- **목소리 관문 (11/07 밤 사고 뒤)**: `tts()`·`heard()` 는 줄마다 고유 임시 파일/폴더(공용 say.txt 가 3워커에서 남의 소리를 저장했다). `times()` 는 받아 적은 말이 대본 줄의 반도 안 맞으면 그 줄을 지우고 다시 만들고, `voice_ratio` < .3 이면 멈춘다. 전수 대조는 `엔진/voicecheck.py --all --md` (`--purge` 로 오염 캐시 삭제).
