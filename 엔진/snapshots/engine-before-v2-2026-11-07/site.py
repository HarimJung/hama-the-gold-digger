#!/usr/bin/env python3
"""하마 머니 라이브러리: 콘텐츠/찾은/*.json → 정적 사이트 (사이트/).
  python3 엔진/site.py          # 전부 다시 찍는다 (홈 + 편 페이지)

꼴은 lazyowen.com 을 그대로 따른다 (하림님 11/05 밤 «레이지오웬 스타일로 정말 카피»):
  홈   = 가이드 도서관. 큰 띠 제목 → 검색·칩 → 2열 타일(태그·제목·두 문장·읽는 시간·STEP 수·화살표) → 숫자 띠 → 편지 → 바닥.
  편   = 가이드. 왼쪽 고정 차례 → 제목·메타(태그·N min·STEP N) → 테이프 붙은 요약 상자(쉬운 말 2~3문장) →
         «이 자료에 담긴 것» → STEP N. 제목 (표·상자 + «Word:» 풀이) → 왜 중요한가 → 공식 자료 → 도움됐다면 → 아래 고정 띠.
피부 값만 하마 (금·잉크·버터). 편이 늘면 그냥 다시 돌리면 된다."""
import json, re, glob, html, pathlib, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import chart   # 주식 창은 엔진 정본을 그대로 쓴다

P = pathlib.Path(__file__).parent.parent
OUT = P / "사이트"
IG = "https://www.instagram.com/hamathegolddigger/"
CAT = {"fear": "Born in fear", "etf": "ETF combos", "stocks": "Stocks", "crypto": "Bitcoin", "tax": "Tax & accounts", "compound": "Time"}

def e(s): return html.escape(str(s or ""))
def em(s):   # *별표* → 골드 강조. 원문에 있던 <b>·<em> 쌍은 살린다
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", e(s))
    return re.sub(r"&lt;(/?(?:b|em))&gt;", r"<\1>", s)
def cap1(t): return t[:1].upper() + t[1:]   # FHSA·IREN 은 그대로

CSS = """
:root{--cream:#FFFBEF;--band:#F6EED2;--card:#fff;--ink:#16140F;--sub:rgba(22,20,15,.72);--gold:#E3BE5A;--goldink:#9A7414;--golddeep:#7A5A0E;--rose:#D8415C;--footer:#1C1710;--line:rgba(22,20,15,.16);
--disp:"Inter",-apple-system,"Apple SD Gothic Neo",sans-serif;--pen:"Playfair Display",serif;--wrap:1080px;--nav-h:64px;--sb-h:58px}
*{box-sizing:border-box;margin:0}
html{scroll-padding-top:calc(var(--nav-h) + 16px)}
body{background:var(--cream);color:var(--ink);font-family:var(--disp);font-size:16.5px;line-height:1.7;-webkit-font-smoothing:antialiased;min-height:100dvh;display:flex;flex-direction:column;padding-top:var(--nav-h);overflow-x:clip}
a{color:inherit}
.wrap{width:100%;max-width:var(--wrap);margin:0 auto;padding:0 20px}
em{font-style:normal;color:var(--goldink);font-weight:800}
.neg{color:var(--rose)}
/* nav */
.nav{position:fixed;top:0;left:0;right:0;z-index:50;background:rgba(255,251,239,.93);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:26px;height:var(--nav-h)}
.nav .logo{font-weight:900;font-size:17px;letter-spacing:-.02em;text-decoration:none;white-space:nowrap}.nav .logo i{color:var(--goldink);font-style:normal}
.navlinks{margin-left:auto;display:none;gap:22px;font-size:14.5px;color:var(--sub)}.navlinks a{text-decoration:none}.navlinks a.on{color:var(--ink);font-weight:800;border-bottom:2px solid var(--goldink)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:13px 24px;border:0;border-radius:4px;font:900 15px var(--disp);letter-spacing:.02em;text-decoration:none;cursor:pointer;transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(154,116,20,.3)}
.btn-gold{background:var(--ink);color:var(--gold)}.btn-line{background:none;color:var(--ink);box-shadow:inset 0 0 0 2px var(--ink)}
.btn-sm{min-height:40px;padding:8px 16px;font-size:13.5px;margin-left:auto;white-space:nowrap}
@media(min-width:640px){.navlinks{display:flex}.btn-sm{margin-left:0}}
/* flood hero */
.flood{background:var(--gold);color:var(--ink);text-align:center;padding:64px 0 54px;border-bottom:1px solid var(--golddeep)}
.kicker{display:inline-block;background:var(--cream);color:var(--golddeep);font:900 12px var(--disp);letter-spacing:.16em;text-transform:uppercase;padding:8px 14px;border-radius:3px;box-shadow:4px 4px 0 var(--ink);margin-bottom:20px}
.h1{font-size:clamp(34px,6.4vw,60px);font-weight:900;letter-spacing:-.025em;line-height:1.14;text-wrap:balance}
.u{position:relative;white-space:nowrap;z-index:0}.u:after{content:"";position:absolute;left:-.08em;right:-.08em;top:.12em;bottom:.08em;background:var(--cream);z-index:-1;border-radius:.05em;transform:rotate(-1deg)}
.flood-body{max-width:34em;margin:16px auto 0;font-size:17px}
.pen{display:inline-block;font:italic 500 20px var(--pen);transform:rotate(-1deg);margin-top:16px}
/* library bar */
.lib-bar{position:sticky;top:var(--nav-h);z-index:30;background:rgba(255,251,239,.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.lib-row{display:flex;gap:8px;align-items:center;padding:10px 0}
.lib-search{flex:auto;display:flex;align-items:center;height:44px;border:1.5px solid var(--line);border-radius:999px;background:var(--card);padding:0 6px 0 16px}
.lib-search input{flex:auto;min-width:0;height:100%;border:0;background:none;font:500 16px var(--disp);color:var(--ink);outline:0}
.chips{display:flex;flex-wrap:wrap;gap:8px;padding:0 0 12px}
.chip{border:1.5px solid var(--ink);border-radius:999px;padding:6px 12px;font:800 13px var(--disp);background:var(--card);cursor:pointer}
.chip.on{background:var(--ink);color:var(--gold)}.chip small{color:var(--sub);font-weight:600;margin-left:4px}.chip.on small{color:var(--gold)}
.lib-count{color:var(--sub);font-size:13px;padding:14px 0 6px}
/* rows */
.g-grid{display:grid;grid-template-columns:minmax(0,1fr);gap:14px;padding:6px 0 40px}
@media(min-width:720px){.g-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:16px;min-height:170px;padding:22px 22px;background:var(--card);border:1px solid rgba(154,116,20,.22);border-radius:20px;text-decoration:none;transition:transform .16s,box-shadow .16s,border-color .16s}
.row:nth-child(2n){background:var(--band)}
.row:hover{transform:translateY(-3px);border-color:var(--goldink);box-shadow:0 16px 44px rgba(22,20,15,.12)}
.row:hover .arrow{transform:translateX(4px)}
.row.hide{display:none}
.rb{display:flex;flex-direction:column;gap:7px;min-width:0}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{font:900 11.5px/1.5 var(--disp);padding:2px 9px;border-radius:999px;color:var(--golddeep);background:rgba(227,190,90,.28)}
.tag.tool{color:var(--ink);background:none;box-shadow:inset 0 0 0 1px rgba(22,20,15,.3)}
.rt{font-size:clamp(17px,2vw,21px);font-weight:900;line-height:1.3;letter-spacing:-.015em}
.rd{color:var(--sub);font-size:14.5px;line-height:1.55;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.rm{color:var(--sub);font-size:12.5px}
.arrow{width:44px;height:44px;border-radius:50%;background:var(--ink);color:var(--gold);display:grid;place-items:center;font-weight:900;transition:transform .16s}
/* stats band */
.stats{background:var(--band);border-block:1px solid var(--line)}
.stats .wrap{display:grid;grid-template-columns:1fr 1fr;padding:18px 20px}
@media(min-width:840px){.stats .wrap{grid-template-columns:repeat(4,minmax(0,1fr));padding:0 20px}}
.stat{padding:16px 0;text-align:center}.stat b{display:block;font-size:clamp(30px,4.6vw,46px);font-weight:900;letter-spacing:-.02em;font-variant-numeric:tabular-nums}.stat b i{font-style:normal;color:var(--goldink)}.stat span{color:var(--sub);font-size:14px}
/* letter */
.letter{padding:48px 0}
.letter .box{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px;box-shadow:0 16px 50px rgba(22,20,15,.08);max-width:640px;margin:0 auto}
.letter h2{font-size:26px;font-weight:900;letter-spacing:-.02em}.letter p{color:var(--sub);margin:8px 0 16px;font-size:15px}
.letter form{display:flex;gap:8px}.letter input{flex:1;min-width:0;height:48px;border:1.5px solid var(--ink);border-radius:4px;padding:0 14px;font:500 15px var(--disp);background:#fff}
/* footer */
footer{background:var(--footer);color:var(--cream);margin-top:auto;padding:44px 0 56px;font-size:14px}
footer .wrap{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center}footer a{color:var(--cream);text-decoration:none;opacity:.85}footer .fine{width:100%;opacity:.5;font-size:12.5px;margin-top:14px}
/* guide page */
.layout{width:100%;max-width:84rem;margin:0 auto;padding:36px 20px 80px}
@media(min-width:1024px){.layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,44rem) minmax(0,1fr);column-gap:32px}.toc{display:block!important}}
.reader{min-width:0;max-width:44rem;margin:0 auto;grid-column:2;width:100%}
.toc{display:none;grid-column:1;position:sticky;top:calc(var(--nav-h) + 24px);align-self:start;max-width:15rem;font-size:14px}
.toc h4{font-size:14px;font-weight:900;margin-bottom:10px}
.toc ol{list-style:none;padding:0}.toc li{display:flex;gap:10px;padding:8px 6px;border-radius:8px}.toc li b{color:var(--goldink);min-width:14px}.toc a{text-decoration:none;color:var(--sub)}.toc li:hover{background:var(--band)}
.toc .extra{border-top:1px solid var(--line);margin-top:10px;padding-top:10px}
.head{margin-bottom:28px}
.head h1{font-size:clamp(30px,4.6vw,44px);font-weight:900;letter-spacing:-.025em;line-height:1.18}
.meta{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;margin-top:14px;color:var(--sub);font-size:13.5px}
.meta .tag{font-size:12.5px;padding:4px 12px}.meta .tag.tool{background:var(--card)}
.callout{position:relative;background:var(--card);border-radius:4px;padding:26px 20px 20px;margin:18px -8px 0;box-shadow:0 1px rgba(22,20,15,.05),0 12px 26px -16px rgba(22,20,15,.35);font-size:17px;line-height:1.75}
.callout:before{content:"";position:absolute;top:-12px;left:50%;transform:translate(-50%) rotate(-4deg);width:96px;height:26px;border-radius:2px;background:repeating-linear-gradient(45deg,rgba(227,190,90,.75) 0 8px,rgba(227,190,90,.45) 8px 16px)}
.callout b{font-weight:800}.callout .hl{background:linear-gradient(transparent 55%,rgba(227,190,90,.55) 55%)}
.inside{margin:34px 0 10px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.inside .ih{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:4px 12px}.inside h2{font-size:21px;font-weight:900}.inside .ih span{color:var(--sub);font-size:13px;font-weight:800;letter-spacing:.08em}
.inside ol{list-style:none;padding:0;margin-top:10px}.inside li a{display:flex;gap:12px;align-items:baseline;padding:10px 4px;border-top:1px solid var(--line);text-decoration:none;font-size:15.5px}.inside li:first-child a{border-top:0}.inside li b{color:var(--goldink);min-width:18px}.inside li span{margin-left:auto;color:var(--sub);font-size:13px;white-space:nowrap}
.prose h2{font-size:clamp(23px,3.4vw,30px);font-weight:900;letter-spacing:-.02em;line-height:1.32;border-top:1px solid var(--line);margin-top:2.2em;padding-top:1.1em}
.prose h2 small{display:block;font:900 12px var(--disp);letter-spacing:.14em;color:var(--goldink);margin-bottom:6px}
.prose p{margin:14px 0}.prose .lead{font-size:17px}
.prose blockquote{border-left:4px solid var(--gold);background:var(--band);border-radius:0 8px 8px 0;padding:12px 18px;margin:16px 0;font-size:15.5px}.prose blockquote b{font-weight:900}
.box2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.bx{border:1.5px solid var(--line);border-radius:14px;padding:14px;background:var(--card)}.bx.win{border-color:var(--goldink);background:rgba(227,190,90,.22)}
.bx .h{font:800 11px var(--disp);letter-spacing:.1em;color:var(--sub)}.bx.win .h{color:var(--goldink)}.bx .v{font-size:26px;font-weight:900;line-height:1.1;margin:8px 0}.bx p{font-size:13.5px;color:var(--sub);margin:4px 0 0;line-height:1.45}
.tablewrap{overflow-x:auto;margin:14px 0}.prose table{border-collapse:collapse;width:100%;font-size:15px;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.prose th{background:var(--band);font-weight:900;text-align:left;padding:10px 12px}.prose td{padding:10px 12px;border-top:1px solid var(--line);vertical-align:top}.prose tr.hi td{background:rgba(227,190,90,.22);font-weight:800}
.flow{display:grid;gap:12px;margin:14px 0}.flow .st{display:flex;gap:14px;align-items:baseline;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}.flow .st b{color:var(--goldink);font-size:20px;min-width:70px}.flow .st small{display:block;color:var(--sub)}
.check{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid var(--line);font-weight:600}.check:before{content:"✓";color:var(--goldink);font-weight:900}
.src{color:var(--sub);font-size:13px;margin-top:8px}
.chwrap{font-size:8px;margin:14px 0}@media(min-width:560px){.chwrap{font-size:10px}}.chwrap .lab{font:800 11px var(--disp);letter-spacing:.14em;color:var(--sub);margin:14px 0 6px}
.links{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:14px 0}.links a{display:flex;justify-content:space-between;gap:12px;padding:14px 16px;border-top:1px solid var(--line);text-decoration:none;font-size:15px;font-weight:700}.links a:first-child{border-top:0}.links a span{color:var(--sub);font-weight:500;white-space:nowrap;font-size:13px}
.thanks{background:var(--band);border:1px solid var(--line);border-radius:16px;padding:24px;margin-top:40px}.thanks h3{font-size:20px;font-weight:900;margin-bottom:6px}.thanks p{color:var(--sub);font-size:15px;margin-bottom:14px}.thanks .btns{display:flex;flex-wrap:wrap;gap:10px}
.stickybar{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--footer);color:var(--cream);padding:7px 0;border-top:1px solid rgba(255,251,239,.14)}
.stickybar .wrap{display:flex;align-items:center;gap:12px}.stickybar .word{font:900 13px var(--disp);letter-spacing:.1em}.stickybar .word i{font-style:normal;color:var(--gold)}.stickybar .btn{margin-left:auto;min-height:42px;padding:8px 14px;font-size:13px;background:var(--gold);color:var(--ink)}
body.guide{padding-bottom:var(--sb-h)}
""" + chart.CSS

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Playfair+Display:ital,wght@1,500&display=swap" rel="stylesheet">
<style>{css}</style></head><body class="{cls}">
<nav class="nav"><div class="wrap"><a class="logo" href="{home}">HAMA <i>THE GOLD DIGGER</i></a>
<div class="navlinks"><a href="{home}" class="{on}">Tables</a><a href="{ig}" rel="noopener">Instagram</a></div>
<a class="btn btn-gold btn-sm" href="{ig}" rel="noopener">Follow Hama</a></div></nav>"""

FOOT = """<footer><div class="wrap"><a href="{ig}">Instagram @hamathegolddigger</a><a href="{home}">All tables</a>
<div class="fine">© 2026 Hama the Gold Digger · A Toronto chihuahua saving to $1M. Every number checked against the source. General education, not financial advice.</div></div></footer></body></html>"""

# ---------- 편 재료 ----------
def deliverable(d):
    """릴스 끝의 약속: 댓글 키워드 → DM 으로 보내는 물건 이름. post.deliver (director 가 쓴다) 먼저, 없으면 tiles 비트의 dm 글에서."""
    dv = d.get("deliver") or {}
    if dv.get("word"): return dv["word"], dv.get("gift") or d.get("object", "").lower()
    for bt in (d.get("rail") or {}).get("beats") or []:
        if bt.get("part") == "tiles":
            dm = (bt["data"].get("dm") or ["", ""])[1]
            return bt["data"].get("word", ""), re.sub(r"^sent you\s+|\s*✨\s*$", "", dm).strip()
    return "", d.get("object", "").lower()

def checklist(d):
    if d.get("check"): return [i for i in d["check"] if not re.search(r"save this|follow", i, re.I)][:4]   # post.check (director)
    for bt in (d.get("rail") or {}).get("beats") or []:
        if bt.get("part") == "checklist":
            return [i for i in bt["data"].get("items", []) if not re.search(r"save this|follow", i, re.I)][:4]
    return []

def chart_beat(d):
    for b in (d.get("rail") or {}).get("beats") or []:
        if b.get("part") == "chart" and (b.get("data") or {}).get("chart"): return b["data"]
    return None

def steps(d):
    """STEP 목록: (제목, 본문 html). 장 하나 = STEP 하나. 주식 창·내 것 확인은 뒤에 붙는다."""
    out = [(re.sub(r"\*", "", s.get("title") or s.get("kicker", "").title()), slide_body(s, d)) for s in d.get("slides", []) if s["type"] not in ("hero", "chart")]   # 주식 창 장은 rail 데이터로 뒤에 붙는다
    cb = chart_beat(d)
    if cb:
        c, l = cb["chart"], cb.get("long")
        h = f'<div class="chwrap"><div class="lab">{e(chart.PAST[c["range"]].upper())} · {e(chart.pct(c["period_pct"]))}</div>' + chart.window(c, "w1")
        if l: h += f'<div class="lab">ZOOM OUT · {e(chart.PAST.get(l["range"], l["range"]).upper())} · {e(chart.pct(l["period_pct"]))}</div>' + chart.window(l, "w2")
        out.append((f"That was {chart.PAST[c['range']].lower()}. Now zoom out", h + "</div>"))
    ck = checklist(d)
    if ck: out.append(("Check your own, five minutes", "".join(f'<div class="check">{em(x)}</div>' for x in ck)))
    return out

def word_note(text, d, used):
    """이 STEP 본문에 나오는 어려운 말 하나를 «Word:» 인용으로. plain.words 에서. 한 편에서 같은 말은 한 번."""
    for w in (d.get("plain") or {}).get("words", []):
        t = w.get("term", "")
        if t and t not in used and re.search(r"\b" + re.escape(t) + r"\b", text, re.I):
            used.add(t); return f'<blockquote><b>{e(t)}</b> — {e(w.get("means", ""))}</blockquote>'
    return ""

def slide_body(s, d):
    t = s["type"]; h = ""
    if s.get("lead"): h += f'<p class="lead">{s["lead"] if "<" in str(s.get("lead","")) else em(s.get("lead",""))}</p>'
    if t == "two":
        h += '<div class="box2">'
        for b in s.get("boxes", []):
            h += (f'<div class="bx{" win" if b.get("win") else ""}"><div class="h">{e(b.get("h",""))}</div><div class="v{" neg" if str(b.get("v","")).startswith(("−","-")) else ""}">{e(b.get("v",""))}</div>'
                  + "".join(f'<p>{em(b.get(k,""))}</p>' for k in ("d", "d2", "d3") if b.get(k)) + "</div>")
        h += "</div>"
    elif t in ("grid", "table"):
        rows = s.get("rows", []); cols = s.get("cols") or [c for c in (s.get("h1"), s.get("h2"), s.get("h3")) if c]
        h += '<div class="tablewrap"><table>'
        if cols: h += "<tr>" + ("<th></th>" if s.get("rowlabel") or t == "grid" else "") + "".join(f"<th>{e(c)}</th>" for c in cols) + "</tr>"
        hi = s.get("hi")
        for i, r in enumerate(rows):
            if isinstance(r, dict):
                lab = em(r.get("a", "")) + (f'<br><small style="color:var(--sub)">{em(r["asub"])}</small>' if r.get("asub") else "")
                cells = [lab] + [em(c) for c in r.get("cells", [])] + [em(r[k]) for k in ("b", "c") if r.get(k) is not None]
            else: cells = [em(c) for c in r]
            h += f'<tr class="{"hi" if hi is not None and i == hi else ""}">' + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
        h += "</table></div>"
        if s.get("note"): h += f'<p class="src">{em(s["note"])}</p>'
    elif t == "flow":
        h += '<div class="flow">' + "".join(f'<div class="st"><b>{e(st.get("n",""))}</b><div>{em(st.get("t",""))}<small>{em(st.get("s",""))}</small></div></div>' for st in s.get("steps", [])) + "</div>"
        if s.get("tail"): h += f'<p>{em(s["tail"])}</p>'
    elif t == "mini":
        h += '<div class="tablewrap"><table>' + "".join(
            (f'<tr class="{"hi" if isinstance(r, dict) and r.get("ok") else ""}">'
             + "".join(f"<td>{em(c)}</td>" for c in ([r.get("t"), r.get("v")] if isinstance(r, dict) else (r if isinstance(r, list) else [r]))) + "</tr>")
            for r in s.get("rows", [])) + "</table></div>"
        if s.get("tail"): h += f'<p>{em(s["tail"])}</p>'
    elif t == "do":
        for c in s.get("checks", []):
            h += f'<div class="check">{em(c)}</div>' if not isinstance(c, dict) else f'<div class="check"><div><b>{em(c.get("h",""))}</b><br><span style="color:var(--sub);font-weight:400">{em(c.get("d",""))}</span></div></div>'
        if s.get("fine"): h += f'<p class="src">{em(s["fine"])}</p>'
    elif t == "chart":
        return ""   # 주식 창은 steps() 가 rail 데이터로 따로 붙인다
    if s.get("source_label"): h += f'<p class="src">{e(s["source_label"])}</p>'
    return h

def minutes(d):
    """읽는 시간: 화면에 실제로 찍히는 글자만 센다 (JSON 키는 안 센다)."""
    text = re.sub(r"<[^>]+>", " ", " ".join(t + " " + h for t, h in steps(d))) + " " + " ".join(str(v) for v in (d.get("plain") or {}).values() if isinstance(v, str))
    return max(2, round(len(re.findall(r"\w+", text)) / 180))

def blurb(d):
    """타일 두 문장: 문제(훅) + 해결(쉬운 말 so_what 또는 약속)."""
    pl = d.get("plain") or {}; hk = d.get("hooks", {})
    return hk.get("on_screen", "") + " " + (pl.get("so_what") or hk.get("promise", ""))

# ---------- 편 페이지 ----------
def post_page(d):
    hk = d.get("hooks", {}); pl = d.get("plain") or {}; w = d.get("why") or {}
    word, thing = deliverable(d); title = cap1(thing)
    st = steps(d); mins = minutes(d); used = set()
    tags = f'<span class="tag tool">{e(CAT.get(d.get("category"), d.get("category", "")))}</span>' + (f'<span class="tag">{e(w["ticker"])}</span>' if w.get("ticker") else f'<span class="tag">{e(d.get("series",""))}</span>')
    lead = pl.get("what") or d.get("lede") or ""
    first = re.split(r"(?<=\.)\s", lead, 1)
    callout = f'<div class="callout"><b>{e(first[0])}</b>' + (f' <span class="hl">{e(first[1])}</span>' if len(first) > 1 else "") + "</div>"
    toc = "".join(f'<li><b>{i + 1}</b><a href="#s{i + 1}">{e(t)}</a></li>' for i, (t, _) in enumerate(st))
    inside = "".join(f'<li><a href="#s{i + 1}"><b>{i + 1}</b>{e(t)}<span>{max(1, mins // len(st))} min</span></a></li>' for i, (t, _) in enumerate(st))
    body = ""
    for i, (t, h) in enumerate(st):
        body += f'<h2 id="s{i + 1}"><small>STEP {i + 1}</small>{em(t)}</h2>{h}{word_note(t + " " + h, d, used)}'
    if w.get("line"):
        body += (f'<h2 id="why"><small>WHY IT MATTERS</small>{e(w["line"])}</h2>' + (f'<p class="lead">{e(w["line2"])}</p>' if w.get("line2") else "") + (f'<p>{e(w["means"])}</p>' if w.get("means") else ""))
    if pl.get("do"): body += f'<blockquote><b>Today</b> — {e(pl["do"])}</blockquote>'
    seen = set(); srcs = [s for s in d.get("sources", []) if s.get("url") and not (s["url"] in seen or seen.add(s["url"]))]   # 같은 링크는 한 번
    if srcs: body += '<h2 id="src"><small>OFFICIAL SOURCES</small>Where every number came from</h2><div class="links">' + "".join(f'<a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s.get("label",""))}<span>opens in new tab ↗</span></a>' for s in srcs) + "</div>"
    thanks = (f'<div class="thanks"><h3>If this helped</h3><p>Follow Hama for one table a day. Saw this on a reel? Comment <b>{e(word)}</b> there and Hama sends the link.</p>'
              f'<div class="btns"><a class="btn btn-gold" href="{IG}" rel="noopener">Follow on Instagram</a><a class="btn btn-line" href="../index.html">All tables</a></div></div>')
    return (HEAD.format(title=e(title) + " · Hama the Gold Digger", desc=e(hk.get("on_screen", "")), css=CSS, cls="guide", home="../index.html", on="", ig=IG)
            + f'<div class="layout"><aside class="toc"><h4>In this guide</h4><ol>{toc}</ol><div class="extra"><ol>'
            + ('<li><a href="#why">Why it matters</a></li>' if w.get("line") else "") + '<li><a href="#src">Official sources</a></li></ol></div></aside>'
            + f'<article class="reader"><header class="head"><h1>{e(title)}</h1><div class="meta">{tags}<span>{mins} min read</span><span>STEP {len(st)}</span><span>{e(hk.get("made_on") or datetime.date.today().isoformat())}</span></div>'
            + f'<p class="pen" style="margin-top:10px;font-size:18px">{em(hk.get("on_screen",""))}</p>{callout}</header>'
            + f'<section class="inside"><div class="ih"><h2>What is inside</h2><span>STEP {len(st)} · {mins} MIN</span></div><ol>{inside}</ol></section>'
            + f'<div class="prose">{body}</div>{thanks}</article></div>'
            + f'<div class="stickybar"><div class="wrap"><span class="word">YOU COMMENTED <i>{e(word)}</i></span><a class="btn" href="{IG}" rel="noopener">Follow Hama</a></div></div>'
            + FOOT.format(ig=IG, home="../index.html"))

# ---------- 홈 (도서관) ----------
def build():
    (OUT / "p").mkdir(parents=True, exist_ok=True)
    posts = []
    for f in sorted(glob.glob(str(P / "콘텐츠" / "찾은" / "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if not (d.get("hooks") or {}).get("on_screen") or not (P / "엔진" / "out" / "릴스" / f'{d["key"]}-rail.mp4').exists(): continue   # 릴스 있는 편만
        (OUT / "p" / f'{d["key"]}.html').write_text(post_page(d), encoding="utf-8")
        posts.append(d)
    posts.sort(key=lambda d: (d.get("hooks", {}).get("made_on", ""), d.get("made_by", "")), reverse=True)
    cats = []
    for d in posts:
        if d.get("category") not in cats: cats.append(d.get("category"))
    chips = '<button class="chip on" data-c="">All<small>' + str(len(posts)) + "</small></button>" + "".join(
        f'<button class="chip" data-c="{e(c)}">{e(CAT.get(c, c))}<small>{sum(1 for d in posts if d.get("category") == c)}</small></button>' for c in cats)
    rows = ""
    for d in posts:
        word, thing = deliverable(d); w = d.get("why") or {}
        tag2 = e(w["ticker"]) if w.get("ticker") else e(d.get("series", ""))
        rows += (f'<a class="row" href="p/{e(d["key"])}.html" data-c="{e(d.get("category",""))}"><span class="rb"><span class="tags"><span class="tag tool">{e(CAT.get(d.get("category"), d.get("category","")))}</span><span class="tag">{tag2}</span></span>'
                 f'<span class="rt">{e(cap1(thing))}</span><span class="rd">{em(blurb(d))}</span><span class="rm">{minutes(d)} min read · STEP {len(steps(d))}</span></span><span class="arrow">→</span></a>')
    n_src = sum(len(d.get("sources", [])) for d in posts)
    stats = "".join(f'<div class="stat"><b>{s}</b><span>{t}</span></div>' for s, t in [
        (f"{len(posts)}", "free tables, one a day"), (f"{n_src}", "sources checked, letter for letter"), ("<i>0</i>", "numbers made up"), ("$1M", "the goal. every dollar logged")])
    home = (HEAD.format(title="Hama the Gold Digger — every table, free", desc="Every table Hama promised on a reel, free. Verified money facts for Canadians, from a Toronto chihuahua saving to $1M.", css=CSS, cls="", home="index.html", on="on", ig=IG)
            + '<section class="flood"><div class="wrap"><span class="kicker">The free library</span>'
            + '<h1 class="h1">I\'m Hama the Chihuahua<br>saving to <span class="u">$1M.</span></h1>'
            + '<p class="flood-body">I dig up the money leaks Canadians step over every day — and check every single number against the source before I bark. <b>No advice. Just verified facts.</b></p>'
            + '<span class="pen">Every table I promised on a reel, free below.</span></div></section>'
            + '<div class="lib-bar"><div class="wrap"><div class="lib-row"><label class="lib-search"><input id="q" type="search" placeholder="Find by name or keyword (SOXL, FHSA, bitcoin…)" autocomplete="off"></label></div>'
            + f'<div class="chips">{chips}</div></div></div>'
            + f'<main class="wrap"><div class="lib-count" id="n">{len(posts)} tables</div><div class="g-grid" id="g">{rows}</div></main>'
            + f'<section class="stats"><div class="wrap">{stats}</div></section>'
            + '<section class="letter"><div class="wrap"><div class="box"><h2>The Money Leak Letter</h2><p>Once a week, one leak in your money — the number, the source, and the one thing to check on your own account. Free, unsubscribe anytime.</p>'
            + '<form action="https://formsubmit.co/visual.climate.data@gmail.com" method="POST"><input type="hidden" name="_subject" value="[하마] 뉴스레터 가입"><input type="hidden" name="_next" value="https://hama-money.vercel.app/?joined=1">'
            + '<input type="email" name="email" required placeholder="you@example.com"><button class="btn btn-gold" type="submit">Join free →</button></form></div></div></section>'
            + """<script>
const q=document.getElementById('q'),rows=[...document.querySelectorAll('.row')],n=document.getElementById('n');let cat='';
function go(){const t=q.value.trim().toLowerCase();let k=0;rows.forEach(r=>{const ok=(!cat||r.dataset.c===cat)&&(!t||r.textContent.toLowerCase().includes(t));r.classList.toggle('hide',!ok);if(ok)k++});n.textContent=k+' table'+(k===1?'':'s')}
q.addEventListener('input',go);document.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>{document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));c.classList.add('on');cat=c.dataset.c;go()}));
</script>"""
            + FOOT.format(ig=IG, home="index.html"))
    (OUT / "index.html").write_text(home, encoding="utf-8")
    # 검색 노출: sitemap + robots (11/06 하림님 «릴스 말고 다른 노출» → 구글). Search Console 등록은 하림님 손.
    base = "https://hama-money.vercel.app"
    urls = [f"<url><loc>{base}/</loc><lastmod>{datetime.date.today()}</lastmod></url>"] + [f'<url><loc>{base}/p/{d["key"]}.html</loc><lastmod>{(d.get("hooks") or {}).get("made_on") or datetime.date.today()}</lastmod></url>' for d in posts]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>", encoding="utf-8")
    for sub, what in ((OUT, "사이트 빌드 산출물 (site.py 가 만든다, 손으로 고치지 않는다)"), (OUT / "p", "편 페이지 47")):   # validate.py: 폴더마다 _index.md
        (sub / "_index.md").write_text(f"---\nid: hama-site-{sub.name}\ntype: index\ntrack: invest\nstatus: active\nlast_review: {datetime.date.today()}\n---\n# {sub.name}\n{what}\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    print(f"사이트/  ·  홈 1 + 편 {len(posts)}  ·  {datetime.date.today()}")

if __name__ == "__main__":
    build()
