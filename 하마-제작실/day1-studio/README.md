---
id: hama-readme
type: note
track: invest
status: archive
last_review: 2026-11-04
---

# 하마 Day1 제작 시안

이 프로젝트는 사용자가 채팅에 붙인 31일 계획의 첫날을 실제로 렌더한다. 편집 상태는 아이디어, 발행 승인은 없다.

- `out/day1-reel.mp4`: 30초, 1080×1920, 30fps, 무음 모션 릴스.
- `out/day1-mini.png`: 3-ETF 역할 빈칸 피드.
- `out/day1-save.png`: 복리 구조 저장 카드.
- `out/day1-morning-1.png`, `out/day1-morning-2.png`: 아침 스토리 2장.
- `out/day1-night-1.png`, `out/day1-night-2.png`: 밤 스토리 2장.
- `out/캡션과-발행메모.txt`: 캡션과 실제 스티커 추가 안내.
- `day1.json`: 원본·출처·빈칸·제작 상태.
- `운영-반영.md`: 매일 네 묶음 운영과 원본 우선 규칙.

`npm run dev`로 편집 미리보기를 연다. `node scripts/render-day1.mjs`로 출력한다. 반복 출력은 out/의 같은 이름을 덮어쓰므로 수정 전 버전을 보존한다.

골드·블랙·크림 HEX, 한국어 시스템 폰트, 하마 캐릭터는 이번 시안이다. 확정된 브랜드 자산으로 취급하지 않는다. Anatomy kit로 만든 46부품 트레이를 Remotion 프레임에 연결했다. 완전한 인터랙티브 Anatomy 페이지나 31일 무인 제작 엔진까지 구현한 것은 아니다.

가격·종목·비중은 빈칸이다. 투표·질문 이미지는 실제 스티커가 아니므로 인스타 앱에서 추가해야 한다. 업로드·예약·DM·댓글 전송 기능은 연결하지 않았다.
