---
id: hama
type: index
track: invest
status: active
last_review: 2026-11-07
---

# 하마 더 골드 디거

토론토 치와와 하마가 돈을 굴리는 여정을 기록하는 영문 인스타 계정. 투자 조언이 아니라 여정 기록. 이 폴더에는 하마 자료만 둔다.

## 핵심 = 엔진. 전부 `엔진/` 명령으로 돈다

| 명령 | 하는 일 |
|---|---|
| `python3 엔진/find.py run` | 찾기 한 바퀴: 웹 조사→주제→사실검증→훅→본문→릴스 |
| `python3 엔진/find.py plan` | 발행 달력 (오늘 뭘 올릴지) |
| `python3 엔진/find.py stats` | 상태 (신호·주제·완성 수) |
| `python3 엔진/hook.py rebuild 콘텐츠/찾은/<편>.json --direct` | 한 편 대본·렌더·납품 검사 |
| `python3 엔진/motion/rail/director.py --review` | 관문 표 (FAIL 넷만 막는다) |

자세한 순서와 파일은 `엔진/_index.md` 한 장.

매일 아침 7:57 (토론토) 그날 영상+캡션이 Gmail로 온다 (클라우드 루틴 trig_0186cqgJCKWsvkG6hhiWH4Sp, 발행표는 Drive «하마-발행표.txt»(11/09 새 파일 1jrhutO98wA7tFuMolnx2KNOsh6mDC92y, `find.py queue` 산출물을 Claude 가 올림, 10일치), 영상은 맥 엔진/out/릴스/, 하루 2편 A/B 캡션). 게시는 하림님 손.

## 폴더 (2026-11-04 정리)

| 폴더 | 크기 | 역할 |
|---|---|---|
| `엔진/` | | **정본.** find.py(찾기)·hook.py(훅·일괄)·motion/rail/(감독·레일·부품)·deliver/reader/voicecheck.py(관문)·cards.py(캐러셀)·site.py·prompts/·hooks.json. 명령 순서는 `엔진/_index.md` |
| `엔진/out/` | | 산출물: `릴스/`(발행 MP4) · `캐러셀/` · `작업/`(레일 HTML·관문 표) · `.tts-cache`(목소리 캐시) |
| `콘텐츠/찾은/` | | 편 정본 json (사실·출처·훅·대본·캡션 전부 이 안에) |
| `콘텐츠/31일/` | | 11월 초 수동 기획 기록 (기록용, 달력은 find.py plan 이 대체) |
| `하마-제작실/` | 80M | 레퍼런스·시안 역사 (42장 레퍼, 모션 시안 6종, deck) + `원본-목소리/`(하림님 녹음). 디자인 정답의 출처 — 지우지 않는다 |
| `REF/` | 3M | 외부 레퍼런스 노트 fx-*.md (영상 원본은 11/07 휴지통) |
| `_휴지통-2026-11-07/` | 2.3G | 11/07 대청소로 옮긴 것. 엔진이 도는 걸 확인한 뒤 하림님이 비운다 |
| `하마 배경 사진/` `뮤즈 볼크/` | 24M | 사진 원자료 |
| `99-ops/` | | 핸드오프 (세션 시작할 때 최신 것부터) |

- 자료: [[hama-vault]]
