---
id: hama-repo-readme
type: readme
track: invest
status: active
last_review: 2026-11-09
---

# Hama the Gold Digger — guide for any AI tool

@hamathegolddigger is an English Instagram account. Hama is a real black-and-tan chihuahua in Toronto who "digs up" money that Canadian beginners are losing, on the road to $1M. It is a journey log, not financial advice. Folder and file names are Korean; the content is English.

## Rules that never change

1. **Numbers only from sources.** Every $ and % must already be in the post's `fact`, `sources` or script. If you don't have it, leave a blank. Never round or convert.
2. **No buy/sell calls, no price predictions, no "guaranteed".**
3. **Hama never owns, buys, sells or loses money.** Hama finds, digs, sniffs, sends.
4. **Reels and stories only. No carousels.**
5. **Hama is the real dog.** Use the photos in `뮤즈 볼크/사진/하마/` or the reel face `엔진/assets/hama-face.png`. Do not draw or generate a new Hama; generated characters were rejected.
6. **Plain words** (grade 6): "box" for account, "cut" for tax, "pays you" for dividend.
7. **Voice:** warm, a bit cheeky, spoken, on the reader's side. No em dashes, no "here's the thing", "game changer", "it's not X, it's Y". Reel voiceover is a calm female voice (Kokoro `af_heart`).
8. **The owner posts everything by hand.** Tools draft; they never publish.

## Where things are

| Need | File |
|---|---|
| All posts, one JSON each (fact, sources, hook, script, caption A, caption B) | `콘텐츠/찾은/<key>.json` |
| What to post each day (date, hook, caption, A/B, 3 story frames) | `엔진/out/작업/upload-queue.json` |
| Caption rules | `엔진/prompts/caption.md` |
| Hook rules (name + dollars lost + a question) | `엔진/hooks.json`, `엔진/prompts/hook.md` |
| Reel script shape (9 beats: hook, lock-in, body, rehook, close, CTA) | `엔진/prompts/rail.md` |
| Real Hama photos (10) | `뮤즈 볼크/사진/하마/`, list in `뮤즈 볼크/사진/2026-10-27-사진-목록.md` |
| Approved look (butter background, gold ink, rose ink, bold 700) | `엔진/motion/rail/skin.css`, `하마-제작실/브랜드-리셋/사진콜라주-표지-v1.png` |
| Reference creators and effects | `REF/`, `하마-제작실/레퍼런스/` |
| Instagram growth notes (hooks, Trial Reels, weekly review) | `REF/ops-insta-7links.md` |
| Engine (Python, runs on the owner's Mac) | `엔진/` — start at `엔진/_index.md` |

## How to make each format

- **Reel (1 a day).** Take one post JSON. Hook = name + the dollar gap the viewer loses + a question ("SOXL sellers missed $71,000. Want it back?"). Script follows the 9 beats in `rail.md`. Caption follows `caption.md`. The finished MP4s are rendered on the Mac and are not in this repo.
- **Story (3 frames a day).** From `upload-queue.json` → `story`: (1) share today's reel, (2) poll sticker with the caption's closing question, (3) "Comment KEYWORD under today's reel and I'll send it to you".
- **Real-photo post or story background.** Use one real photo from `뮤즈 볼크/사진/하마/` plus flat graphics in the approved look. Keep Hama's face whole and uncropped. Never put an invented number on it.

## Right now (2026-11-09)

- Caption A/B test: A = `caption` (old style), B = `caption_b` (first line says something the reel didn't). The queue alternates A and B. The winner is chosen from keyword comments per 1,000 views.
- Nothing has been posted yet. Profile photo still to be chosen by the owner.
