#!/usr/bin/env python3
"""덱 HTML -> 장별 PNG + 대지 한 장 + 관문 수치.

사람은 contact.png 한 장만 본다. 9장을 따로 열지 않는다.
파일 이름이 곧 업로드 순서다 — 사람이 순서를 틀릴 수 없게.

사용:
  python3 엔진/shoot.py 콘텐츠/31일/2026-11-11-01-main.json
  python3 엔진/shoot.py <post.json> --ar 9x16
  python3 엔진/shoot.py <post.json> --only 1,3 --no-ink
"""
import json, sys, re, subprocess, pathlib, argparse
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P))
import ink

SHELL = pathlib.Path.home() / 'Library/Caches/ms-playwright/chromium_headless_shell-1148/chrome-mac/headless_shell'
SIZE = {'4x5': (1080, 1350), '9x16': (1080, 1920)}


def shoot_one(deck, n, out, ar):
    w, h = SIZE[ar]
    subprocess.run([str(SHELL), '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', f'--window-size={w},{h}',
                    # 구글 폰트를 기다린다. 빼면 Fredoka 없이 찍힌다.
                    '--virtual-time-budget=4000', f'--screenshot={out}',
                    f'file://{deck}?shot={n}&ar={ar}'], check=True, capture_output=True)


def contact(pngs, out, cols=3):
    """대지 한 장. 폰에서 이것만 보고 넘어가거나 되돌린다."""
    from PIL import Image
    ims = [Image.open(p) for p in pngs]
    w, h = ims[0].size
    sc = 360 / w
    tw, th = int(w * sc), int(h * sc)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * 12, rows * th + (rows + 1) * 12), (58, 53, 44))
    for i, im in enumerate(ims):
        x = 12 + (i % cols) * (tw + 12)
        y = 12 + (i // cols) * (th + 12)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('post')
    ap.add_argument('--ar', default='4x5', choices=list(SIZE))
    ap.add_argument('--only', default='')
    ap.add_argument('--no-ink', action='store_true')
    ap.add_argument('--outdir', default='')
    a = ap.parse_args()

    post = json.load(open(a.post, encoding='utf-8'))
    stem = pathlib.Path(a.post).stem
    deck = (P / 'out' / '캐러셀' / f'{stem}.html').resolve()
    if not deck.exists():
        raise SystemExit(f'{deck} 없음 — 먼저 build.py 를 돌린다')

    out = pathlib.Path(a.outdir) if a.outdir else P / 'out' / '캐러셀' / stem
    out.mkdir(parents=True, exist_ok=True)

    types = [s['type'] for s in post['slides']]
    want = [int(x) for x in a.only.split(',')] if a.only else range(1, len(types) + 1)

    pngs, report = [], {}
    for n in want:
        name = f"{n:02d}-{re.sub(r'[^a-z]', '', types[n-1])}.png"
        f = out / name
        shoot_one(deck, n, f, a.ar)
        pngs.append(f)
        if a.no_ink:
            continue
        m = ink.measure(f)
        bad = []
        if m['fill'] < ink.MIN_FILL: bad.append(f"채움 {m['fill']*100:.1f}%")
        if m['band'] > ink.MAX_BAND: bad.append(f"빈 띠 {m['band']}px")
        if m['span'] < ink.MIN_HERO: bad.append(f"가로 {m['span']*100:.1f}%")
        # 색 예산은 표지 전용이다. 속장은 글이 많아 금이 적은 게 정상이다.
        if n == 1:
            cf, pal = ink.cute_gate(f)
            bad += cf
            m |= {k: pal[k] for k in ('gold', 'rose', 'butter', 'slab')}
        report[name] = m | {'fails': bad}
        print(f"  {name}  채움 {m['fill']*100:5.1f}%  빈띠 {m['band']:4d}px  가로 {m['span']*100:5.1f}%"
              + ('  ~ ' + ' · '.join(bad) if bad else '  PASS'))

    if len(pngs) > 1:
        contact(pngs, out / 'contact.png')
        print(f"  대지: {out/'contact.png'}")
    if report:
        (out / 'shot.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    nbad = sum(1 for r in report.values() if r['fails'])
    # 잉크 측정은 눈으로 볼 거리지 결격이 아니다 (하림님 11/04 «결격 아니면 굴린다»)
    print(f"  {len(pngs)}장 · 경고 {nbad}장 · {out}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
