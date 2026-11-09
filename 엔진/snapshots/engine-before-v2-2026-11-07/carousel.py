#!/usr/bin/env python3
"""post.json -> 검정 캐러셀 (릴스 다크 컷과 같은 얼굴: 검정 모눈 · 위 흰 한 줄 · 가운데 금색 큰 글).

11/06 하림님: «캐러셀은 더 쉽게, 더 훅, 이 대본·이 디자인으로». 장 하나 = 생각 하나.
글은 prompts/carousel.md 가 쓴다 (post.carousel 에 저장). 숫자는 입력에 있는 것만 — 없는 숫자는 FAIL, 나머지는 경고.

사용:
  python3 엔진/carousel.py <key>           # post.carousel 없으면 쓰고, 찍는다 → out/캐러셀/<key>-dark/NN.png + contact.png
  python3 엔진/carousel.py <key> --copy    # 글 다시 쓰기
"""
import json, sys, re, html, pathlib, subprocess
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P))
import hook, shoot, importlib.util
_s = importlib.util.spec_from_file_location('hama_site', P / 'site.py'); site = importlib.util.module_from_spec(_s); _s.loader.exec_module(site)   # 파이썬 내장 site 와 이름이 겹친다

OUT = P.parent / '콘텐츠' / '찾은'
e = html.escape
SITE = "https://hama-money.vercel.app"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;800;900&family=Playfair+Display:ital,wght@1,500&display=swap');
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;overflow:hidden;background:#16140F;color:#fff;font-family:Inter,sans-serif;position:relative;
  background-image:linear-gradient(rgba(255,255,255,.06) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.06) 2px,transparent 2px);background-size:90px 90px;background-position:-2px -2px}
.pill{position:absolute;left:0;right:0;top:120px;margin:auto;width:fit-content;height:64px;padding:0 30px;border-radius:32px;background:#E3BE5A;color:#16140F;font:800 24px/64px Inter;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap}
.top{position:absolute;left:80px;right:80px;top:260px;text-align:center;font:500 46px/1.3 Inter;letter-spacing:-.01em}
.big{position:absolute;left:60px;right:60px;top:50%;transform:translateY(-50%);text-align:center;color:#E3BE5A;font:900 1px/.98 Inter;letter-spacing:-.035em;text-wrap:balance}
.big.rose{color:#D8415C}
.note{position:absolute;left:100px;right:100px;bottom:230px;text-align:center;font:italic 500 38px/1.35 'Playfair Display',serif;color:#B9B3A6}
.foot{position:absolute;left:80px;right:80px;bottom:90px;display:flex;justify-content:space-between;font:800 22px Inter;letter-spacing:.14em;color:#7A7468;text-transform:uppercase}
.face{position:absolute;left:0;right:0;margin:auto;bottom:330px;width:150px;height:150px;border-radius:50%;background:url(FACE) center/cover;border:5px solid #E3BE5A}
"""

def size(t):   # 큰 글은 길이에 맞춰 (상자 960px, 두 줄까지)
    n = len(t); return 240 if n <= 7 else 190 if n <= 12 else 150 if n <= 20 else 120

def copy(d):
    word, thing = site.deliverable(d)
    hk = d.get('hooks') or {}
    payload = {"key": d['key'], "object": d.get('object'), "hook": hk.get('on_screen'), "promise": hk.get('promise'), "fact": d.get('fact'),
               "script": [b['say'] for b in (d.get('rail') or {}).get('beats') or [] if b.get('say')], "plain": d.get('plain'), "comment_word": word, "deliverable": thing}
    out = hook.ask_claude(payload, timeout=600, prompt_text=re.sub(r"\A---\n.*?\n---\n", "", (P / 'prompts' / 'carousel.md').read_text(encoding='utf-8'), flags=re.S))
    cards = (out.get('carousel') or {}).get('cards') or []
    if len(cards) < 4: raise SystemExit(f"  ✗ {d['key']}: 캐러셀 글 못 씀 — {out.get('reason', '')}")
    return {"cards": cards, "made_by": "엔진/carousel.py (prompts/carousel.md via claude -p)"}

def gate(d, cards):
    """FAIL = 입력에 없는 숫자뿐. 나머지는 경고 (11/04 «촘촘하게 말고 굴러가게»)."""
    have = set(re.findall(r"\d[\d,]*\.?\d*", json.dumps(d, ensure_ascii=False)))
    bad = [n for c in cards for n in re.findall(r"\d[\d,]*\.?\d*", c.get('top', '') + ' ' + c.get('big', '') + ' ' + c.get('note', '')) if n not in have]
    if bad: raise SystemExit(f"  ✗ FAIL 입력에 없는 숫자: {bad}")
    for i, c in enumerate(cards, 1):
        if len(c.get('big', '').split()) > 5: print(f"  ! {i}장 big 이 5단어 넘음: {c['big']}")
        if len(c.get('top', '').split()) > 10: print(f"  ! {i}장 top 이 10단어 넘음")
        if re.search(r"\b(buy|sell)\b", c.get('big', '') + c.get('top', ''), re.I): print(f"  ! {i}장 buy/sell 단어: 설명이면 OK, 콜이면 고칠 것")

def card_html(d, c, i, n):
    last = i == n
    big = e(c.get('big', ''))
    face = (P / 'assets' / 'hama-face.png').as_uri()
    return (f"<!doctype html><meta charset=utf-8><style>{CSS.replace('FACE', face)}</style>"
            + (f'<div class="pill">{e(d.get("object", ""))}</div>' if i == 1 else '')
            + f'<div class="top">{e(c.get("top", ""))}</div>'
            + f'<div class="big{" rose" if c.get("tone") == "rose" else ""}" style="font-size:{size(c.get("big", ""))}px">{big}</div>'
            + (f'<div class="face"></div>' if last else '')
            + (f'<div class="note">{e(c["note"])}</div>' if c.get('note') else '')
            + f'<div class="foot"><span>Hama the Gold Digger</span><span>{i} / {n}{"" if last else " →"}</span></div>')

def render(d, cards):
    out = P / 'out' / '캐러셀' / f'{d["key"]}-dark'; out.mkdir(parents=True, exist_ok=True)
    pngs = []
    for i, c in enumerate(cards, 1):
        h = out / f'{i:02d}.html'; h.write_text(card_html(d, c, i, len(cards)), encoding='utf-8')
        png = out / f'{i:02d}.png'
        subprocess.run([str(shoot.SHELL), '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1080,1350',
                        '--virtual-time-budget=4000', f'--screenshot={png}', h.as_uri()], check=True, capture_output=True)
        pngs.append(png)
    shoot.contact([str(p) for p in pngs], str(out / 'contact.png'), cols=4)
    return out

if __name__ == '__main__':
    key = [a for a in sys.argv[1:] if not a.startswith('--')][0]
    path = OUT / f'{key}.json'; d = json.load(open(path, encoding='utf-8'))
    if '--copy' in sys.argv or not d.get('carousel'):
        d['carousel'] = copy(d)
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    cards = d['carousel']['cards']
    gate(d, cards)
    out = render(d, cards)
    print(f"  ✓ {key}: {len(cards)}장 → {out.relative_to(P.parent)}/contact.png")
    for i, c in enumerate(cards, 1): print(f"   {i}. {c.get('top','')}  //  {c.get('big','')}")
