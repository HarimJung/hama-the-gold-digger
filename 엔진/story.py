#!/usr/bin/env python3
"""스토리 2·3장 배경 (11/09 하림님 «스토리에 들어갈 거 없지?»). 릴스 피부(motion/rail/skin.css) 그대로: 흰 모눈 · 골드 하나 · Inter + Playfair 이탤릭.

1장은 인스타가 만든다(릴스 아래 종이비행기 → 스토리에 추가). 여기선 2장(투표·질문 스티커 자리)과 3장(댓글 키워드)만 찍는다.
글은 큐(out/작업/upload-queue.json)의 캡션에서만 가져온다. 숫자를 새로 쓰지 않는다.

  python3 엔진/story.py            # 오늘 (토론토)
  python3 엔진/story.py 2026-11-10 # 그날
결과: out/스토리/<날짜>-2.png · -3.png (1080×1920)
"""
import json, re, sys, html, pathlib, datetime, subprocess
from zoneinfo import ZoneInfo
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P))
from shoot import SHELL

FACE = (P / 'assets' / 'hama-face.png').resolve()
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;800&family=Playfair+Display:ital,wght@1,700&display=swap');
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1920px;overflow:hidden;background:#fff;color:#16140F;font-family:Inter,sans-serif;position:relative}
.grid{position:absolute;inset:0;background-image:linear-gradient(#ECE9E1 2px,transparent 2px),linear-gradient(90deg,#ECE9E1 2px,transparent 2px);background-size:90px 90px}
.glow{position:absolute;left:-200px;right:-200px;bottom:-560px;height:1300px;background:radial-gradient(closest-side,rgba(227,190,90,.55),rgba(227,190,90,0))}
.wrap{position:absolute;left:90px;right:90px;top:300px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:44px}
.face{width:250px;height:250px;border-radius:50%;background:#fff url('file://FACE') center/contain no-repeat;border:8px solid #E3BE5A}
.kick{font:500 34px/1 Inter;letter-spacing:.14em;color:#8C877C}
h1{font:800 92px/1.08 Inter;letter-spacing:-.02em;text-wrap:balance}
.box{font:italic 700 150px/1 'Playfair Display';background:rgba(227,190,90,.24);border:4px solid #E3BE5A;border-radius:24px;padding:24px 44px}
.sub{font:500 52px/1.3 Inter;color:#16140F;text-wrap:balance}
.slot{width:100%;height:420px}
.foot{position:absolute;left:0;right:0;bottom:380px;text-align:center;font:500 32px Inter;color:#8C877C;letter-spacing:.06em}
"""


def page(body, dig):
    return (f"<!doctype html><meta charset=utf-8><style>{CSS.replace('FACE', str(FACE))}</style>"
            f"<div class=grid></div><div class=glow></div><div class=wrap>{body}</div>"
            f"<div class=foot>{html.escape(dig)}</div>")


def frames(row):
    cap = row['caption']
    lines = [l.strip() for l in cap.split('\n') if l.strip()]
    q = next((l for l in lines if l.endswith('?') and not l.startswith('🐶')), 'Did you know this?')
    word = (re.search(r'Comment (\S+)', cap) or [None, ''])[1]
    gift = (re.search(r"send you (?:my |the )?(.+?)\s*🪙", cap) or [None, 'it'])[1]
    dig = (re.search(r'(Dig #\d+)', cap) or [None, ''])[1] + ' · HAMA THE GOLD DIGGER'
    f2 = page(f"<div class=face></div><div class=kick>QUICK QUESTION</div><h1>{html.escape(q)}</h1><div class=slot></div>", dig)
    f3 = page(f"<div class=face></div><div class=kick>TODAY'S REEL</div><div class=sub>Comment</div><div class=box>{html.escape(word)}</div>"
              f"<div class=sub>under today's reel and I'll send you my {html.escape(gift)}</div>", dig)
    return f2, f3


def shoot(htm, png):
    tmp = png.with_suffix('.html'); tmp.write_text(htm, encoding='utf-8')
    subprocess.run([str(SHELL), '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--window-size=1080,1920', '--virtual-time-budget=4000', '--allow-file-access-from-files',
                    f'--screenshot={png}', f'file://{tmp}'], check=True, capture_output=True)


def main(day=None):
    day = day or str(datetime.datetime.now(ZoneInfo('America/Toronto')).date())
    q = json.load(open(P / 'out' / '작업' / 'upload-queue.json', encoding='utf-8'))['queue']
    rows = [r for r in q if r['date'] == day]
    if not rows: raise SystemExit(f'{day}: 큐에 없는 날')
    out = P / 'out' / '스토리'; out.mkdir(parents=True, exist_ok=True)
    for r in rows:
        tag = day if len(rows) == 1 else f"{day}-{r['slot']}"
        for n, htm in zip((2, 3), frames(r)):
            shoot(htm, out / f'{tag}-{n}.png'); print(out / f'{tag}-{n}.png')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
