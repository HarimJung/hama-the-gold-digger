---
id: hama-cover-mockups-1103
type: index
track: invest
status: dropped
last_review: 2026-11-03
---
# 표지 시안 — 2026-11-03 (폐기)

**2026-11-03 하림님 반려.** 영어 산출물인데 한글로 짰고, 멀쩡한 직전 버전을 두고 새로 그렸다.
반려 사유는 **언어와 «새로 그렸다»** 였다. 레이아웃·사진 프레임·칩·아이브로우는 반려 목록에 없다.

**정정 (같은 날):** 앞서 이 자리에 «정본 표지는 build.py 가 뽑는 영어 덱» 이라고 적었는데 틀렸다.
하림님이 승인하신 것은 **HEX 색 토큰 뿐**이고 레이아웃을 승인한 기록은 없다. 색 승인을 레이아웃 승인으로 번역한 것이다.

**실제 작업 베이스는 11/03 «모션 시안 6종» 아티팩트다** — https://claude.ai/artifact/RcHxajj5tWPFVjCD1Vvf1q
(로컬: `../../variants-all.png`). 하림님 판정 «70% 완성, 30%만 채운다».

TFSA 1편 표지 4종. 레퍼런스는 `../브랜드-리셋/reference-images/` 의 aiscene.kr(표지 문법)과 organized.finance(본문 포맷).

| 파일 | 용도 |
|---|---|
| `covers.html` | 네 장 전부. `?only=A` 로 한 장만 1080×1350 |
| `out/cover-A~D.png` | 렌더 결과 (A 숫자 · B 취소선 · C 두 칸 · D 영수증) |
| `photos/` | 하마 사진 사본. 원본 정본은 `뮤즈 볼크/사진/하마/` |

```bash
python3 -m http.server 8777
headless_shell --headless --window-size=1080,1350 \
  --screenshot=out/cover-A.png "http://localhost:8777/covers.html?only=A"
```

색·글자 토큰 정본은 `../../엔진/template.html`. 여기서 바꾸지 않는다.
비교 페이지: https://claude.ai/artifact/GodTZUcP79v3kE8HfEG76S
