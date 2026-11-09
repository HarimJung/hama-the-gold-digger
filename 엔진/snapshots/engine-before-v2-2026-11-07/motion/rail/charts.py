"""차트 층 (11/07, diagram-design 문법을 9:16 에 옮김). 그림은 말하는 숫자 하나만 말한다.
데이터 모양 → 타입: 두 값과 그 차이 → dumbbell · 시작액 − 단계 = 끝액 → waterfall.
부품 규약은 parts.py 와 같다: (html, js, ticks). 막대·점마다 data-value 를 단다(숫자 계약: 그림 = 숫자).
피부 토큰: ink·soft·line·gold·goldink·rose (skin.css :root). 강조색(rose)은 한 요소만."""
import re
from html import escape as e

def _n(v):
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v).replace("−", "-"))
    return float(m.group(0).replace(",", "")) if m else 0.0

def _ticks(top):
    """0 → top 사이 눈금 4개쯤, 깔끔한 단위."""
    import math
    raw = top / 4; mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    step = next(x * mag for x in (1, 2, 2.5, 5, 10) if x * mag >= raw)
    return [i * step for i in range(int(top // step) + 2)]

def _fmt(v):
    return f"${abs(v):,.0f}" if abs(v) >= 10 or v == 0 else f"${abs(v):,.2f}"

# ── 덤벨: 한 줄, 한 눈금 위에 점 둘, 둘 사이 거리가 메시지 ──────────────────────
def dumbbell(p, s, d):
    """d = {"a": {"k","big","ft"}, "b": {"k","big","ft","at"}, "gap"?, "gap_at"?}. a 가 큰 쪽(손해)·b 가 작은 쪽일 수도, 반대일 수도."""
    a, b = d["a"], d["b"]; va, vb = abs(_n(a["big"])), abs(_n(b["big"]))
    tk = _ticks(max(va, vb)); top = tk[-1] or 1
    X0, X1, Y = 80, 920, 300
    x = lambda v: X0 + (X1 - X0) * v / top
    grid = "".join(f'<line x1="{x(t):.0f}" y1="200" x2="{x(t):.0f}" y2="400" class="g"/><text x="{x(t):.0f}" y="440" class="tk">{e(_fmt(t))}</text>' for t in tk)
    xa, xb = x(va), x(vb)
    svg = (f'<svg class="db" viewBox="0 0 1000 520">{grid}'
           f'<line id="{p}-ln" x1="{xa:.0f}" y1="{Y}" x2="{xb:.0f}" y2="{Y}" class="ln" pathLength="1"/>'
           f'<circle id="{p}-da" cx="{xa:.0f}" cy="{Y}" r="26" class="da" data-value="{va:g}" data-name="{e(a["k"])}"/>'
           f'<circle id="{p}-db" cx="{xb:.0f}" cy="{Y}" r="26" class="dbb" data-value="{vb:g}" data-name="{e(b["k"])}"/>'
           f'<text id="{p}-la" x="{xa:.0f}" y="{Y - 60}" class="va">{e(a["big"])}</text><text x="{xa:.0f}" y="{Y - 110}" class="ka">{e(a["k"])}</text>'
           f'<text id="{p}-lb" x="{xb:.0f}" y="{Y - 60}" class="vb">{e(b["big"])}</text><text x="{xb:.0f}" y="{Y - 110}" class="kb">{e(b["k"])}</text>'
           + (f'<text id="{p}-lg" x="{(xa + xb) / 2:.0f}" y="{Y + 70}" class="gap">{e(d["gap"])} gap</text>' if d.get("gap") else "") + '</svg>')
    html = f'<div class="card" id="{p}-c"><div class="k">{e(a.get("ft") or "")} · {e(b.get("ft") or "")}</div>{svg}</div>'
    tb = s.w(b["at"])
    js = (f'pop("#{p}-c",{s.t0});'
          f'tl.fromTo("#{p}-da",{{scale:0,transformOrigin:"center"}},{{scale:1,duration:.35,ease:"back.out(2)"}},{s.t0 + .4:.2f});tl.fromTo("#{p}-la",{{opacity:0}},{{opacity:1,duration:.25}},{s.t0 + .5:.2f});'
          f'tl.fromTo("#{p}-ln",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:.6,ease:"power2.out"}},{tb:.2f});'
          f'tl.fromTo("#{p}-db",{{scale:0,transformOrigin:"center"}},{{scale:1,duration:.35,ease:"back.out(2)"}},{tb + .5:.2f});tl.fromTo("#{p}-lb",{{opacity:0}},{{opacity:1,duration:.25}},{tb + .6:.2f});')
    ticks = [round(tb + .5, 2)]
    if d.get("gap"):
        tg = max(s.w(d.get("gap_at", 1)), tb + .9)
        js += f'tl.fromTo("#{p}-lg",{{opacity:0,scale:1.5,transformOrigin:"center"}},{{opacity:1,scale:1,duration:.3,ease:"power4.in"}},{tg:.2f});'
        ticks.append(round(tg + .3, 2))
    return html, js, ticks

# ── 폭포: 시작 총액 → ±단계 → 끝 총액. 총액은 바닥에서, 다리는 직전 수준에서 ──────────
def waterfall(p, s, d):
    """d = {"title", "rows": [[label, value, at], ...], "total": [label, value, at]}. rows[0] 이 시작 총액, 나머지는 부호 있는 다리, total 이 끝."""
    rows = d["rows"]; tl_, tv, tat = d["total"]
    bars = [{"name": rows[0][0], "v": abs(_n(rows[0][1])), "role": "total", "at": rows[0][2]}]
    run = bars[0]["v"]
    for lab, val, at in rows[1:]:
        dv = _n(val); dv = -abs(dv) if ("-" in str(val) or "−" in str(val)) else dv
        bars.append({"name": lab, "v": dv, "role": "delta", "at": at, "from": run}); run += dv
    bars.append({"name": tl_, "v": abs(_n(tv)), "role": "total", "at": tat})
    top = max([bars[0]["v"], bars[-1]["v"]] + [b.get("from", 0) for b in bars]) or 1
    H0, H1 = 60, 420; y = lambda v: H1 - (H1 - H0) * v / top
    n = len(bars); pitch = 840 / n; w = pitch * .6
    focal = min((i for i, b in enumerate(bars) if b["role"] == "delta"), key=lambda i: bars[i]["v"], default=None)   # 가장 큰 감소 하나만 강조
    svg = [f'<svg class="wf" viewBox="0 0 1000 520"><line x1="80" y1="{H1}" x2="920" y2="{H1}" class="ax"/>']
    prev_lvl = None
    for i, b in enumerate(bars):
        x0 = 80 + pitch * i + (pitch - w) / 2
        if b["role"] == "total": lo, hi = 0, b["v"]
        else: lo, hi = sorted((b["from"], b["from"] + b["v"]))
        cls = "tot" if b["role"] == "total" else ("foc" if i == focal else ("dn" if b["v"] < 0 else "up"))
        lab = _fmt(b["v"]) if b["role"] == "total" else ("−" if b["v"] < 0 else "+") + _fmt(b["v"])
        svg.append(f'<rect id="{p}-b{i}" x="{x0:.0f}" y="{y(hi):.0f}" width="{w:.0f}" height="{max(2, y(lo) - y(hi)):.0f}" class="{cls}" data-role="{b["role"]}" data-value="{b["v"]:g}" data-name="{e(b["name"])}"/>')
        ly = y(hi) - 14 if b["v"] >= 0 or b["role"] == "total" else y(lo) + 44
        svg.append(f'<text id="{p}-t{i}" x="{x0 + w / 2:.0f}" y="{ly:.0f}" class="v {cls}">{e(lab)}</text><text x="{x0 + w / 2:.0f}" y="{H1 + 44}" class="nm">{e(b["name"])}</text>')
        lvl = b["v"] if b["role"] == "total" else b["from"] + b["v"]
        if i + 1 < n:   # 다리 선: 지금 수준을 다음 막대로 나른다
            svg.append(f'<line id="{p}-c{i}" x1="{x0 + w:.0f}" y1="{y(lvl):.0f}" x2="{x0 + pitch:.0f}" y2="{y(lvl):.0f}" class="carry" data-carry="{lvl:g}" pathLength="1"/>')
    svg.append("</svg>")
    html = f'<div class="card" id="{p}-c"><div class="k">{e(d["title"])}</div>{"".join(svg)}</div>'
    js = f'pop("#{p}-c",{s.t0});'; ticks = []
    for i, b in enumerate(bars):
        t = s.w(b["at"]) if b["at"] is not None else s.t0 + .4 + i * .5
        js += (f'tl.fromTo("#{p}-b{i}",{{scaleY:0,transformOrigin:"center bottom"}},{{scaleY:1,duration:.45,ease:"expo.out"}},{t:.2f});'
               f'tl.fromTo("#{p}-t{i}",{{opacity:0}},{{opacity:1,duration:.2}},{t + .3:.2f});')
        if i + 1 < n: js += f'tl.fromTo("#{p}-c{i}",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:.3}},{t + .4:.2f});'
        if b["role"] == "total" and i: ticks.append(round(t, 2))
    return html, js, ticks

if __name__ == "__main__":   # 자가 검사: 그림 숫자 = 데이터 숫자
    class S:
        t0, t1 = 0.0, 6.0
        def w(self, x, n=1): return 1.0 if x == "$220" else 2.0
    h, j, t = dumbbell("x", S(), {"a": {"k": "BANK FUND", "big": "$1,940", "ft": "a year"}, "b": {"k": "ONE ETF", "big": "$220", "ft": "same $100,000", "at": "$220"}, "gap": "$1,720", "gap_at": "gap"})
    assert 'data-value="1940"' in h and 'data-value="220"' in h and "$1,720 gap" in h
    h, j, t = waterfall("y", S(), {"title": "US DIVIDEND", "rows": [["US company pays", "$1,000", 0], ["15% at the border", "−$150", 1]], "total": ["Lands in your TFSA", "$850", 2]})
    assert 'data-role="total" data-value="1000"' in h and 'data-value="-150"' in h and 'data-value="850"' in h and 'data-carry="850"' in h
    print("charts ok")
