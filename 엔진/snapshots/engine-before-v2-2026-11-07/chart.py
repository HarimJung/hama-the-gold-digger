#!/usr/bin/env python3
"""주가 창. 진짜 시세를 받아(Yahoo Finance 차트 API, 키 없음) 주식 앱 창 모양, 하마 밝은 피부로 그린다.
레퍼런스: 하림님 11/05 캡처 3장 (IREN 1M · SOXL 1M · SOXL 10Y). 캡처 대신 이걸 쓴다. 캐러셀 chart 장·릴스 chart 부품이 같은 창을 쓴다.
  python3 엔진/chart.py SOXL 1mo          # 받아서 요약만
  python3 엔진/chart.py SOXL 10y --html   # 창 하나를 out/작업/chart-SOXL-10y.html 로
  python3 엔진/chart.py selftest
숫자는 받은 값에서만 나온다. 기간 등락 = 첫 값 → 마지막 값 (앱의 «Past Month»와 같은 식)."""
import datetime, json, pathlib, sys, urllib.request
from html import escape as e

SRC = "https://query1.finance.yahoo.com/v8/finance/chart/{t}?range={r}&interval={i}"
STEP = {"1d": "5m", "5d": "30m", "1mo": "60m", "3mo": "1d", "6mo": "1d", "ytd": "1d", "1y": "1d", "2y": "1wk", "5y": "1wk", "10y": "1wk", "max": "1mo"}
TAB = {"1d": "1D", "5d": "1W", "1mo": "1M", "3mo": "3M", "6mo": "6M", "ytd": "YTD", "1y": "1Y", "2y": "2Y", "5y": "5Y", "10y": "10Y", "max": "ALL"}
PAST = {"1d": "Today", "5d": "Past Week", "1mo": "Past Month", "3mo": "Past 3 Months", "6mo": "Past 6 Months", "ytd": "Year to Date",
        "1y": "Past Year", "2y": "Past 2 Years", "5y": "Past 5 Years", "10y": "Past 10 Years", "max": "All Time"}

def fetch(ticker, rng="1mo"):
    t = ticker.upper()
    for q in (t, t + ".TO"):   # 캐나다 상장(VFV·XEQT)은 Yahoo 에서 .TO 가 붙는다. 화면 티커는 그대로
        try:
            raw = json.load(urllib.request.urlopen(urllib.request.Request(SRC.format(t=q, r=rng, i=STEP[rng]), headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
            res = raw["chart"]["result"][0]; m = res["meta"]; res["timestamp"]; break   # 빈 결과(시세 없음)도 다음 후보로
        except Exception:
            if q.endswith(".TO"): raise
    pts = [(t_, round(c, 2)) for t_, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c]
    vols = [v or 0 for v in res["indicators"]["quote"][0].get("volume", [])]
    c = summarize(t, pts, rng)
    c.update(name=m.get("longName") or m.get("shortName") or t, exch=m.get("fullExchangeName", ""), cur=m.get("currency", "USD"),
             last=round(m.get("regularMarketPrice", c["last"]), 2), day_pct=round(m.get("regularMarketChangePercent", 0), 2),
             day_hi=m.get("regularMarketDayHigh"), day_lo=m.get("regularMarketDayLow"), vol=m.get("regularMarketVolume"),
             w52_hi=m.get("fiftyTwoWeekHigh"), w52_lo=m.get("fiftyTwoWeekLow"), vols=vols[-len(pts):],
             src=f"https://finance.yahoo.com/quote/{m.get('symbol', t)}", src_label="Yahoo Finance",
             as_of=datetime.datetime.fromtimestamp(m.get("regularMarketTime", pts[-1][0])).strftime("%Y-%m-%d %H:%M"))
    c["period_pct"] = round((c["last"] / c["closes"][0] - 1) * 100, 2)
    return c

def summarize(t, pts, rng):
    v = [c for _, c in pts]; hi = max(v)
    return {"ticker": t, "range": rng, "ts": [a for a, _ in pts], "closes": v, "hi": hi,
            "hi_date": datetime.date.fromtimestamp(pts[v.index(hi)][0]).isoformat(), "last": v[-1],
            "period_pct": round((v[-1] / v[0] - 1) * 100, 2), "from_hi_pct": round((v[-1] / hi - 1) * 100, 1)}

def pct(x): return f"{'+' if x > 0 else '-'}{abs(x):,.1f}".replace(".0", "") + "%"   # 숫자 표시 정본: 소수 1자리. 훅·창·제목·대본이 이 글자를 쓴다 (11/05 레드팀: -72.8 / -72.83 / -72)
def num(x, d=2):
    if x is None: return "–"
    for s, k in (("B", 1e9), ("M", 1e6)):
        if abs(x) >= k: return f"{x / k:.{1 if s == 'M' else 3}f}{s}"
    return f"{x:,.{d}f}"

def ticks(c):
    """아래 날짜 눈금 5개 + 오른쪽 가격 눈금 4개 (레퍼처럼)."""
    ts = c["ts"]; days = (ts[-1] - ts[0]) / 86400
    fmt = (lambda d: str(d.day)) if days < 45 else (lambda d: d.strftime("%b")) if days < 400 else (lambda d: str(d.year))
    xs = []
    if days >= 400:   # 해마다 하나, 짝수 해만
        seen = set()
        for i, t in enumerate(ts):
            y = datetime.date.fromtimestamp(t).year
            if y not in seen and y % 2 == 0 and i > 0: seen.add(y); xs.append((i / (len(ts) - 1), str(y)))
    else:
        for k in range(5):
            i = round(k * (len(ts) - 1) / 5); xs.append((i / (len(ts) - 1), fmt(datetime.date.fromtimestamp(ts[i]))))
    lo, hi = min(c["closes"]), max(c["closes"])
    ys = [hi - k * (hi - lo) / 4 for k in range(4)]
    return xs, ys

def svg(c, w=1000, h=400, mark=None):
    v = c["closes"]; lo, hi = min(v), max(v); span = (hi - lo) or 1
    up = c["period_pct"] >= 0; col = "#C99A22" if up else "#D8415C"   # 하마 피부: 상승 골드 · 하락 로즈 (11/05 «밝은 창, 우리 컨셉»)
    xs = [i * w / max(1, len(v) - 1) for i in range(len(v))]
    ys = [12 + (hi - x) * (h - 24) / span for x in v]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    g = "".join(f'<line x1="0" x2="{w}" y1="{k * h / 4:.0f}" y2="{k * h / 4:.0f}"/>' for k in range(1, 4))
    gid = f"g{c['ticker']}{c['range']}"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="chsvg">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".30"/><stop offset="1" stop-color="{col}" stop-opacity=".04"/></linearGradient></defs>'
            f'<g class="grid" stroke="#ECE9E1" stroke-width="1.5">{g}</g>'
            f'<path class="cf" d="{d} L{w},{h} L0,{h} Z" fill="url(#{gid})"/>'
            f'<path class="cl" d="{d}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round" pathLength="1"/>'
            + (_mark(c, xs, ys, mark, h) if mark else "") +
            f'<line x1="0" x2="{w}" y1="{h}" y2="{h}" stroke="#D9D4C7" stroke-width="2"/></svg>')

def _mark(c, xs, ys, t0, h):
    """장기 선 위에 단기 구간(t0 이후)을 로즈로 덧칠 + 띠. 줌아웃 끝에 «여기가 이번 달»."""
    k = next((i for i, t in enumerate(c["ts"]) if t >= t0), len(xs) - 1); k = min(k, len(xs) - 2)
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs[k:], ys[k:]))
    return (f'<rect class="cm" x="{xs[k]:.1f}" y="0" width="{xs[-1] - xs[k] + 6:.1f}" height="{h}" fill="rgba(216,65,92,.13)"/>'
            f'<path class="cmr" d="{d}" fill="none" stroke="#D8415C" stroke-width="6" stroke-linejoin="round"/>')

def window(c, pid="", mark=None):
    """밝은 주식 창 (하마 피부). 글자 크기는 모두 em — 바깥에서 .chw 의 font-size 하나로 키운다."""
    up = c["period_pct"] >= 0
    tabs = "".join(f'<span class="{"on" if k == c["range"] else ""}">{v}</span>' for k, v in TAB.items())
    xs, ys = ticks(c)
    xl = "".join(f'<span style="left:{x * 100:.1f}%">{e(t)}</span>' for x, t in xs)
    yl = "".join(f"<span>{num(y, 0 if y >= 10 else 2)}</span>" for y in ys)
    vb = max(c.get("vols") or [1]) or 1
    vol = "".join(f'<i style="height:{max(6, 100 * x / vb):.0f}%"></i>' for x in (c.get("vols") or [])[-160:])
    st = [("High", num(c.get("day_hi"))), ("Low", num(c.get("day_lo"))), ("Vol", num(c.get("vol"))), ("52W H", num(c.get("w52_hi"))), ("52W L", num(c.get("w52_lo")))]
    stats = "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in st)
    return (f'<div class="chw" id="{pid}w"><div class="chtop"><div><b class="tk">{e(c["ticker"])}</b><span class="nm">{e(c["name"])}</span>'
            f'<div class="ex">{e(c["exch"])} · {e(c["cur"])}</div></div>'
            f'<div class="px"><b>{num(c["last"])}</b><em class="{"up" if up else "dn"}" id="{pid}pc">{pct(c["period_pct"])}</em><span>{PAST[c["range"]]}</span></div></div>'
            f'<div class="tabs">{tabs}</div><div class="plot"><div class="area" id="{pid}a">{svg(c, mark=mark)}</div><div class="yax">{yl}</div></div>'
            f'<div class="xax">{xl}</div><div class="vol">{vol}</div><div class="stats">{stats}</div>'
            f'<div class="src">{e(c["src_label"])} · {e(c["as_of"])} ET</div></div>')

CSS = """
.chw{background:#fff;color:#16140F;border:2px solid #ECE9E1;border-radius:1.2em;padding:1.3em 1.4em 1em;font-family:"Inter",-apple-system,sans-serif;box-shadow:0 1em 3em rgba(22,20,15,.08)}
.chw .chtop{display:flex;justify-content:space-between;align-items:flex-start;gap:1em}
.chw .chtop>div:first-child{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chw .tk{font-size:2.9em;font-weight:800;letter-spacing:-.03em;line-height:1;margin-right:.35em}
.chw .nm{font-size:1.2em;color:#8C877C;font-weight:500;vertical-align:.4em;text-overflow:ellipsis}
.chw .ex{color:#8C877C;font-size:1em;margin-top:.45em;font-weight:500}
.chw .px{text-align:right;white-space:nowrap}.chw .px b{font-size:1.35em;font-weight:700;margin-right:.6em}
.chw .px em{font-style:normal;font-size:1.35em;font-weight:800;display:inline-block}.chw .px span{display:block;color:#8C877C;font-size:1em;margin-top:.1em;font-weight:500}
.chw .up{color:#9A7414}.chw .dn{color:#D8415C}
.chw .tabs{display:flex;justify-content:space-between;border-top:1.5px solid #ECE9E1;margin-top:1em;padding:.75em 0 .6em;font-size:1.05em;font-weight:700;color:#8C877C}
.chw .tabs span{padding:.35em .6em;border-radius:2em}.chw .tabs .on{background:#16140F;color:#fff}
.chw .plot{display:flex;border-top:1.5px solid #ECE9E1}
.chw .area{flex:1;height:16em;border-left:1.5px solid #ECE9E1}.chw .chsvg{width:100%;height:100%;display:block}
.chw .yax{width:3.4em;display:flex;flex-direction:column;justify-content:space-around;text-align:right;font-weight:700;font-size:1.05em;color:#16140F}
.chw .xax{position:relative;height:1.7em;margin-right:3.4em;font-weight:700;font-size:1.05em;color:#16140F}
.chw .xax span{position:absolute;top:.3em;padding-left:.35em;border-left:1.5px solid #ECE9E1}
.chw .vol{display:flex;align-items:flex-end;gap:2px;height:1.2em;margin:.5em 3.4em .6em 0}.chw .vol i{flex:1;background:#D9D4C7;border-radius:1px}
.chw .stats{display:grid;grid-template-columns:repeat(5,1fr);gap:.4em 1em;border-top:1.5px solid #ECE9E1;padding-top:.7em;font-size:1em}
.chw .stats div{display:flex;flex-direction:column}.chw .stats span{color:#8C877C;font-weight:500}.chw .stats b{font-weight:700;margin-top:.15em}
.chw .src{color:#8C877C;font-size:.8em;margin-top:.7em}
"""

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["selftest"]:
        pts = [(1790000000 + i * 86400, v) for i, v in enumerate([164.26, 140.0, 66.68, 45.09])]
        c = summarize("X", pts, "1mo")
        assert c["hi"] == 164.26 and c["from_hi_pct"] == -72.5 and c["period_pct"] == -72.55, c
        c.update(name="X", exch="NYSEArca", cur="USD", src_label="Yahoo Finance", as_of="2026-11-05 16:00")
        assert pct(-72.27) == "-72.3%" and pct(1330.21) == "+1,330.2%" and num(216.9e6) == "216.9M"
        assert 'class="tk">X<' in window(c) and "Past Month" in window(c)
        print("selftest ok")
    else:
        c = fetch(a[0], a[1] if len(a) > 1 else "1mo")
        print(json.dumps({k: v for k, v in c.items() if k not in ("ts", "closes", "vols")}, ensure_ascii=False))
        if "--html" in a:
            o = pathlib.Path(__file__).parent / "out" / "작업" / f"chart-{c['ticker']}-{c['range']}.html"
            o.write_text(f'<!doctype html><meta charset=utf-8><style>body{{margin:0;background:#fff;padding:40px;width:1000px}}{CSS}.chw{{font-size:22px}}</style>{window(c)}')
            print(o)
