---
id: hama-engine
type: index
track: invest
status: active
last_review: 2026-11-07
---

# 엔진 — 하마 릴스 공장 (한 장)

사실 하나 → 훅 → 대본 → 레일 모션 → 목소리 → MP4 → 관문 → 사이트. **캐러셀은 안 한다(11/07 하림님 «캐러셀 할 필요 없어»).** 전부 아래 명령으로 돈다. 손으로 고치지 않는다. 고칠 땐 규칙 한 줄(`hooks.json`) 또는 부품 한 함수(`parts.py`).

## 매일 돌리는 순서

| 단계 | 명령 | 결과 |
|---|---|---|
| 1 새 편 찾기 | `python3 엔진/find.py run --n 5 [--brief "이번 판 지시 한 문장"]` | `콘텐츠/찾은/<key>.json` (사실·출처·훅·약속·쉬운 말) |
| 2 대본·렌더 | `python3 엔진/hook.py rebuild 콘텐츠/찾은/<key>.json --direct` | `out/작업/<key>-rail/` + `out/릴스/<key>-rail.mp4`. 끝에 납품 검사 자동 |
| 3 관문 | `python3 엔진/motion/rail/director.py --review` | `out/작업/review.md`. FAIL 넷만 막는다(지어낸 숫자·매수 콜·이름 없음·훅에 $ 없음) |
| 4 소리 대조 | `python3 엔진/voicecheck.py --all --md` | `out/작업/voice-check.md` 불일치 0 이어야 올린다 |
| 5 대지 | `python3 엔진/hook.py sheet --all` | `out/작업/hook-sheet.png` (첫 장면 1.2초 프레임) |
| 6 사이트 | `python3 엔진/site.py` | `사이트/` (배포는 하림님: `cd 사이트 && vercel --prod`) |
| 7 올리기 큐 | `python3 엔진/find.py queue` | `out/작업/upload-queue.json` → Claude 가 **하마 올리기 판**(https://claude.ai/artifact/8RZbWNxiiuyxheZiPoW2Ma, 원본 `엔진/dashboard.html`)의 db 에 넣는다. 통과(FAIL 아님·목소리 0·캡션·MP4)만, 내일부터 하루 2편 |
| 7b 폰·메일 (11/09) | `find.py queue` 가 같이 함 | 영상은 맥 `out/릴스/` 경로 그대로(11/09 «컴으로 할라구», iCloud 복사 뺌) + `out/작업/발행표.txt`(10일치, 🐶·🪙 는 :dog:·:coin:). Claude 가 Drive «하마-발행표.txt»로 올린다(create_file → 옛 파일 휴지통. 루틴 trig_0186cqgJ 는 제목으로 최신 파일을 찾으니 고칠 것 없음). **10일마다 갱신 안 하면 아침 메일이 «발행표 갱신 필요»로 온다** |
| 하루 1편 + 스토리 3장 · A/B (11/09~12/7) | `find.py caption <key> --b` | B 캡션은 `caption_b`. 큐가 하루 1편, A·B 번갈아(`ab`), 스토리 3장(`story`: 공유·투표 또는 질문·키워드). 12/7쯤 하림님 인사이트로 정본 결정. GitHub 비공개 HarimJung/hama-the-gold-digger |
| 7c 스토리 배경 (11/09) | `python3 엔진/story.py [날짜]` | 2장(투표·질문 스티커 자리)·3장(댓글 키워드) PNG 1080×1920 → `out/스토리/<날짜>-2.png·-3.png`. 릴스 피부 그대로, 글은 큐 캡션에서만. 1장은 인스타 공유 버튼 |

올릴 것: MP4 = `out/릴스/<key>-rail.mp4`, 캡션 = `콘텐츠/찾은/<key>.json` 의 `caption`. 게시는 하림님 손.
하림님이 판에서 «올렸다»를 누르면 db `posted/<key>` 에 남는다. 새 큐를 짜기 전에 Claude 가 `posted` 를 읽어 `out/작업/posted.json`(키 목록)으로 적고 → `find.py queue` 가 올린 편은 다시 잡지 않는다 → 판의 `queue`·`excluded` 를 통째로 바꾼다(옛 문서는 지운다).
캡션 = `prompts/caption.md` 한 곳(11/08 승인, 11/09 첫 줄 개정): 첫 줄 80자는 **훅을 되풀이하지 않고 훅 금액도 다시 안 쓴다**. 26 훅 유형을 줄인 여섯 꼴(curious·myth·warning·quick·feel·possible) 중 하나로 영상이 안 한 말을 궁금하게, 최근 6편이 쓴 꼴은 피한다(`caption_family`, 금액 반복은 경고) · 말하듯 이어지는 1~2문장 · «Comment KEYWORD and I'll send you my …» · 짧은 질문 · «Dig #N · a Toronto chihuahua on the road to $1M»(번호는 `find.py queue`). `hook.py rebuild --direct` 가 대본 뒤에 자동으로 쓰고, 따로는 `find.py caption <key|all> [--dry]`. 관문: 출처에 없는 숫자·금지 표현·키워드 없음이면 옛 캡션 유지. 볼드 유니코드 금지.

규칙이 바뀌었을 때(모델 없이, 대본 그대로): `python3 엔진/hook.py rebuild --all` → 51편 매핑·렌더 다시(3워커, 약 25분).
상태 보기: `python3 엔진/find.py stats` · `find.py plan` (발행 달력) · `director.py --stats` (꼴·부품 분포) · `hook.py --stats`.

## 파일 (정본은 한 곳씩)

| 파일 | 역할 |
|---|---|
| `find.py` + `find/` + `prompts/find-*.md` · `caption.md` | 찾기: 신호 → 주제 → 사실 검증 → 씨앗 → 속장·쉬운 말 · 캡션(대본 뒤) · 올리기 큐 |
| `hook.py` + `hooks.json` + `prompts/hook.md` | 훅 공식(이름+잃은 $+질문)·관문·도장·일괄 rebuild. `hooks.json grammar` = 감독 상수 한 소스 |
| `motion/rail/director.py` + `prompts/rail.md` | 대본(kallaway 9칸)과 장면→부품 매핑. 최근 6편과 안 겹치게 (`motion-ledger.json`) |
| `motion/rail/build_rail.py` | 레일 HTML·TTS(Kokoro af_heart)·낱말 싱크·숫자 관문·정지 금지·렌더 |
| `motion/rail/parts.py` · `charts.py` · `skin.css` | 부품(가족 48)·차트(덤벨·폭포)·피부(동결) |
| `chart.py` | 진짜 주가 창 (hook·site 가 같이 씀) |
| `deliver.py` · `reader.py` · `voicecheck.py` | 납품 실측(−14 LUFS·정지·검은 프레임) · 낯선 사람 읽기 · 목소리 대조 |
| `shoot.py`·`ink.py` | 대지(contact sheet) 함수. `hook.py sheet` 가 쓴다 |
| `site.py` | 정적 사이트 (lazyowen 꼴) |
| `build.py` | director·build_rail 명령줄 래퍼 (`--direct/--redirect/--reopen/--remap/--rail`) |
| `snapshots/` | `soxl-approved-2026-11-06.*` 승인 편 동결본 · `engine-before-*` 되돌림 기준 · `template.*` 11/03 피부 기록 |
| `assets/` | 하마 얼굴·폰트 |
| `out/.tts-cache/` | 목소리 캐시(줄 해시). 지워도 다음 빌드가 다시 만든다 |

밖에 있는 것: 편 정본 `콘텐츠/찾은/`, 속장 예시 `콘텐츠/31일/`, 레퍼 노트 `REF/*.md`, TTS 가상환경 `~/.local/share/hama-tts`.

## 하림님이 정한 규칙 (어기면 FAIL 또는 경고)

- 훅 1초: 대상 이름 + 진짜 잃은 금액 + 얻는 질문. 숫자는 출처에 있는 것만. 매수·매도 콜 금지
- 몸통 첫 줄은 «그게 뭔지». 쉬운 말(초등 6학년). 정지 1.5초 넘으면 경고. 그림은 말하는 숫자 하나만 말한다
- 한 편씩 안 본다: 정답 편 → 규칙 → 관문 → 일괄. 피드백은 `hooks.json` 한 줄로 들어간다
- 릴스만 만든다(캐러셀 없음). 목소리는 af_heart 고정(클론 폐기)

## 2026-11-07 대청소

캐러셀 전부(cards.py·carousel.py·out/캐러셀)·옛 덱 빌더(template.html·check.py·run.py·plan.json·무대 PNG)·클론 TTS·시험 디렉·렌더 캐시·미참조 목소리 캐시를 `_휴지통-2026-11-07/` 로 옮김(약 2.3GB). 돌아가는 것을 확인한 뒤 하림님이 비운다.
