#!/usr/bin/env python3
"""렌더된 표지 PNG 를 재서 1초 관문 S-1c·S-1d 를 판정한다.

CSS 숫자를 읽어서는 상속·덮어쓰기를 못 본다. 그려진 픽셀을 본다.
사용: python3 엔진/ink.py <png>   ·   통과 0 / 실패 1
"""
import sys, pathlib
from PIL import Image

SAFE = (0.10, 0.90)                 # 머리띠·발띠 사이. 비율이라 9:16 도 그대로 쓴다
MIN_FILL  = 0.18                    # S-1d 채워진 비율
MAX_BAND  = 120                     # S-1d 완전 빈 가로 띠 최대 높이(px)
MIN_HERO  = 0.55                    # S-1c 주인공 가로폭 / 캔버스 폭
FILL_DIFF = 12                      # 배경과 이만큼 다르면 «채워졌다». 크림 위 흰 카드(차이 28)도 잡아야 한다

def measure(path):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    px = im.load()
    # 배경은 가장자리 띠에서 제일 많이 쓰인 색이다.
    # 좌상단 한 점은 라벨 띠일 수 있고, 전체 최빈색은 꽉 찬 장에서 내용이 배경이 돼버린다.
    ring = [px[x, y] for y in (4, H - 5) for x in range(0, W, 3)]
    ring += [px[x, y] for x in (4, W - 5) for y in range(0, H, 3)]
    bg = max(set(ring), key=ring.count)
    def inked(c):
        return sum(abs(a-b) for a, b in zip(c, bg)) > FILL_DIFF

    top, bot = round(H*SAFE[0]), round(H*SAFE[1])
    rows, ink, widest = [], 0, 0
    for y in range(top, bot):
        xs = [x for x in range(W) if inked(px[x, y])]
        rows.append(len(xs))
        ink += len(xs)
        if xs:
            widest = max(widest, xs[-1] - xs[0] + 1)

    total = W * len(rows)
    ratio = ink / total if total else 0

    band = run = 0                                   # 완전 빈 가로 띠
    for n in rows:
        run = run + 1 if n == 0 else 0
        band = max(band, run)

    return {'w': W, 'h': H, 'fill': ratio, 'band': band, 'span': widest / W}


TOK = {'white':(255,255,255),'cream':(253,248,236),'gold':(227,190,90),
       'butter':(251,239,196),'ink':(42,38,34),'rose':(232,99,124),'blush':(252,227,231)}

def palette(path, step=2):
    """색 예산과 최대 검정 덩어리. «귀엽다»를 재는 게 아니라 안 귀여울 조건을 거른다."""
    im = Image.open(path).convert('RGB'); W, H = im.size; px = im.load()
    n = {k: 0 for k in TOK}; dark = []
    for y in range(H):
        d = 0
        for x in range(0, W, step):
            c = px[x, y]
            for k, t in TOK.items():
                if sum(abs(a-b) for a, b in zip(c, t)) < (10 if k in ('white','cream') else 60):
                    n[k] += step
                    if k == 'ink': d += step
                    break
        dark.append(d)
    tot = W * H
    best = run = 0
    for d in dark:
        run = run + 1 if d > W * .6 else 0
        best = max(best, run)
    out = {k: v / tot for k, v in n.items()}
    out['slab'] = best * W * .9 / tot
    return out


# C-1·C-2 기준값. 2026-11-03 승인된 재현본 6장을 실측해서 다시 잡았다.
#   하마-제작실/시안-레퍼재현/deck.html  (전이 끈 상태, 1080x1350)
#   금계열  9.3 · 12.9 · 36.8 · 27.9 · 5.1 · 15.0 %     표지 = 9.3
#   브랜드  2.34 · 0.53 · 1.32 · 0.58 · 0.33 · 1.04 %   표지 = 2.34
# 이전 값(18~30% · 2.5% 이상)은 내가 만든 성긴 표지에서 역산한 것이라 승인된 레퍼가 떨어졌다.
# 바꿀 때는 레퍼를 다시 재서 바꾼다. 내 작업물로 내 작업물을 재면 또 같은 일이 난다.
WARM = (0.06, 0.45)                 # C-1 금 계열 하한·상한
MIN_BRAND = 0.015                   # C-2 골드+로즈. 레퍼 표지 2.34% 의 64%
MAX_SLAB = 0.02                     # C-3 검정 한 덩어리. 레퍼는 전부 0


def cute_gate(path):
    """브랜드가 화면에 실제로 있나. 금이 0.5% 면 크림 위 검은 글씨일 뿐이다.
    표지 전용이다. 속장은 글이 많아 금이 적은 게 정상이다 (shoot.py 가 1장에만 돌린다)."""
    p = palette(path)
    warm = p['gold'] + p['butter'] + p['rose'] + p['blush']
    brand = p['gold'] + p['rose']
    out = []
    if not WARM[0] <= warm <= WARM[1]:
        out.append(f"C-1 금 계열 {warm*100:.1f}% — {WARM[0]*100:.0f}~{WARM[1]*100:.0f}% 사이여야 한다")
    if brand < MIN_BRAND:
        out.append(f"C-2 브랜드색(골드+로즈) {brand*100:.2f}% — {MIN_BRAND*100:.1f}% 미만이면 안 보인다")
    if p['slab'] > MAX_SLAB:
        out.append(f"C-3 검정 한 덩어리 {p['slab']*100:.1f}% — {MAX_SLAB*100:.0f}% 이하. 큰 면을 검정으로 안 채운다")
    return out, p


def main():
    if len(sys.argv) < 2:
        raise SystemExit('사용: python3 엔진/ink.py <png>')
    p = pathlib.Path(sys.argv[1])
    from PIL import Image as _I
    _w,_h=_I.open(p).size
    if (_w,_h) not in {(1080,1350),(1080,1920)}:
        print(f"  {p.name}  {_w}x{_h}")
        print("  FAIL  1080x1350(4:5) 또는 1080x1920(9:16) 이 아니다")
        print('  BLOCKED'); return 1
    m = measure(p)
    fails = []
    if m['fill'] < MIN_FILL:
        fails.append(f"S-1d 채움 {m['fill']*100:.1f}% — {MIN_FILL*100:.0f}% 이상이어야 한다. 화면이 비었다")
    if m['band'] > MAX_BAND:
        fails.append(f"S-1d 빈 띠 {m['band']}px — {MAX_BAND}px 이하. 띄엄띄엄 금지")
    if m['span'] < MIN_HERO:
        fails.append(f"S-1c 제일 넓은 줄이 가로 {m['span']*100:.1f}% — {MIN_HERO*100:.0f}% 이상 채워야 한다")

    print(f"  {p.name}  {m['w']}x{m['h']}")
    print(f"  채움 {m['fill']*100:5.1f}%   빈 띠 {m['band']:4d}px   최대 가로 {m['span']*100:5.1f}%")
    cf, pal = cute_gate(p)
    print(f"  골드 {pal['gold']*100:4.2f}%  로즈 {pal['rose']*100:4.2f}%  버터 {pal['butter']*100:5.2f}%  "
          f"블러시 {pal['blush']*100:4.2f}%  검정덩어리 {pal['slab']*100:4.2f}%")
    fails += cf
    for f in fails:
        print('  FAIL ', f)
    print('  ' + ('PASS' if not fails else 'BLOCKED'))
    return 1 if fails else 0


def demo():
    """자체 점검: 빈 캔버스는 떨어지고, 꽉 찬 캔버스는 통과해야 한다."""
    import tempfile, os
    d = tempfile.mkdtemp()
    blank = Image.new('RGB', (1080, 1350), (253, 248, 236))
    bp = os.path.join(d, 'blank.png'); blank.save(bp)
    assert measure(bp)['fill'] == 0, '빈 캔버스가 0이 아니다'

    # 크림 위 흰 카드도 «채워짐» 으로 잡혀야 한다 (차이 28)
    full = Image.new('RGB', (1080, 1350), (253, 248, 236))
    for y in range(135, 1215):
        for x in range(40, 1040):
            full.putpixel((x, y), (255, 255, 255))
    fp = os.path.join(d, 'full.png'); full.save(fp)
    m = measure(fp)
    assert m['fill'] > MIN_FILL and m['band'] == 0 and m['span'] > MIN_HERO, m
    print('demo ok', m)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo()
    else:
        sys.exit(main())
