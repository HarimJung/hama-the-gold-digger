"""레일 릴스 부품. 부품 하나 = 함수 하나 → (html, js).
p: 이 장면의 id 앞머리(b3 …). 모든 id 는 p 로 시작해서 같은 부품을 두 번 써도 안 겹친다.
s: 장면 시각. s.t0 시작 · s.t1 끝 · s.w("단어", n) 그 장면 자막에서 n번째 단어가 들리는 시각.
d: post.json reel.beats[].data. 숫자는 여기서만 들어온다(build 가 fact 와 대조한다).
CSS 는 skin.css 의 .p-<부품> 아래에. 안무는 2026-11-04 동결본 그대로."""
import json, re
from html import escape as e

def J(x): return json.dumps(x, ensure_ascii=False)
NEG = ' class="neg"'
def subj(d): return f'<div class="osubj"{fit(d["subj"], 130, 980) if len(d["subj"]) > 12 else ""}>{e(d["subj"])}</div>' if d.get("subj") else ''   # 첫 장면 대상 이름 (11/05). 긴 이름은 폭에 맞춘다 (11/06 «YOUR $3.7 MILLIO»)
def ols(t): return f' style="font-size:{68 if len(t) <= 36 else 58 if len(t) <= 48 else 52}px"'   # 긴 훅이 약속 줄에 닿지 않게 (11/05)
def fit(t, px, w):   # 글자 길이에 맞춘 크기 (11/05 레드팀: 상자 밖 넘침 6곳). w = 상자 폭 px
    return f' style="font-size:{min(px, int(w / (max(len(str(t)), 1) * .58)))}px;white-space:nowrap"'
def numpx(n): return min(NUM_MAX, 1500 // max(len(str(n)), 1))   # 첫 장면 큰 숫자 크기. 한 곳 (11/06 하림님 «숫자가 너무 크다» → 캡 400→250)
def numst(n, base=840): return f' style="font-size:{numpx(n)}px;top:{base - numpx(n)}px"'   # 숫자는 금색 줄 바로 위에 붙는다 (아래 기준). base = 줄 top
NUM_MAX = 250
def negc(v, d=None): return ' neg' if (str(v)[:1] in '-−' or (d or {}).get("drop")) else ''   # 하락 숫자 = 로즈, 부호 없어도 (11/05)

def hook(p, s, d):
    html = f'<div class="chip" id="{p}-chip"><i></i><small>LIVE</small>{e(d["chip"])}<em>{e(d.get("chip_note",""))}</em></div>'
    js = f'tl.fromTo("#{p}-chip",{{opacity:0,y:-10}},{{opacity:1,y:0,duration:.4,ease:"power3.out"}},{s.t0+.15});'
    return html, js

def checkout(p, s, d):
    fields = "".join(f'<div class="field">{e(f)}</div>' for f in d.get("fields", []))
    html = (f'<div class="card" id="{p}-c"><div class="top">{e(d["title"])}<span class="lock">🔒 {e(d["tag"])}</span></div>'
            f'<div class="row"><div class="ic">{d["icon"]}</div><div><h3>{e(d["h"])}</h3><p>{e(d["p"])}</p>'
            f'<div class="price">{e(d["price"])}<s id="{p}-s"></s></div></div></div>{fields}<div class="btn">{e(d["btn"])}</div></div>')
    js = f'pop("#{p}-c",{s.t0});tl.set("#{p}-s",{{scaleX:0}},0);'
    if d.get("strike_at"):
        js += f'tl.to("#{p}-s",{{scaleX:1,duration:.3,ease:"power3.out"}},{s.w(d["strike_at"])});'
    if d.get("seal"):
        n, lab, at = d["seal"]
        html += f'<div class="sec" id="{p}-sec"{fit(n, 84, 170)}>{e(n)}<small>{e(lab)}</small></div>'
        js += f'tl.fromTo("#{p}-sec",{{opacity:0,scale:.4,rotation:-12}},{{opacity:1,scale:1,rotation:0,duration:.5,ease:"back.out(2)"}},{s.w(at)});'
    return html, js

def amount(p, s, d):
    opts = "".join(f'<span id="{p}-o{i}"{fit(o, 44, 1000 // max(len(d["options"]), 1) - 30)}>{e(o)}</span>' for i, o in enumerate(d["options"]))
    html = (f'<div class="card" id="{p}-c"><div class="app"><div class="appic"></div><div><h3>{e(d["app"])}</h3><p>{e(d["sub"])}</p></div></div>'
            f'<div class="seg">{opts}</div><div class="big" id="{p}-big">{e(d["big"])}<small> {e(d.get("big_sub",""))}</small></div></div>')
    t, o = s.w(d["pick_at"]), f'#{p}-o{d["pick"]}'
    js = (f'pop("#{p}-c",{s.t0});'
          f'tl.to("{o}",{{borderColor:"#9A7414",backgroundColor:"rgba(227,190,90,.24)",color:"#16140F",duration:.2}},{t});'
          f'tl.fromTo("{o}",{{scale:1}},{{scale:1.06,duration:.12,yoyo:true,repeat:1}},{t});'
          f'tl.fromTo("#{p}-big",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{t+.1});')
    return html, js, [t]

def toggle(p, s, d):
    html = (f'<div class="card main" id="{p}-c"><div class="k">{e(d.get("k",""))}</div>'
            f'<div class="tg"><div><b>{e(d["label"])}</b><p>{e(d["sub"])}</p></div><div class="track" id="{p}-trk"><div class="knob" id="{p}-knob"></div></div></div></div>')
    t = s.w(d["on_at"])
    js = (f'pop("#{p}-c",{s.t0});tl.to("#{p}-knob",{{x:74,duration:.3,ease:"power3.inOut"}},{t});'
          f'tl.to("#{p}-trk",{{backgroundColor:"#E3BE5A",duration:.3}},{t});')
    if d.get("term"):
        lines = "".join(f'<div class="l" id="{p}-l{i}">&gt; {e(x)}</div>' for i, (x, _) in enumerate(d["term"]))
        html += f'<div class="card term" id="{p}-term"><div class="t"><i class="face"></i>{e(d["app"])}</div>{lines}</div>'
        js += f'pop("#{p}-term",{t+.4});'
        js += "".join(f'tl.to("#{p}-l{i}",{{opacity:1,duration:.1}},{max(s.w(at), t+.6)});' for i, (_, at) in enumerate(d["term"]))
    return html, js, [t]

def counter(p, s, d):
    labs = "".join(f'<span id="{p}-y{i}">{e(x["label"])}</span>' for i, x in enumerate(d["steps"]))
    ticks = "".join(f"<span>{e(x)}</span>" for x in d["ticks"])
    html = (f'<div class="card" id="{p}-c"><div class="k yr">{labs}</div><div class="num" id="{p}-n">{e(d.get("pre", "$"))}0{e(d.get("suf", ""))}</div>'
            f'<div class="bar"><div class="barf" id="{p}-bf"></div></div><div class="ticks">{ticks}</div></div>')
    js = f'pop("#{p}-c",{s.t0});tl.set("#{p}-bf",{{scaleX:0}},0);const {p}v={{v:0}},{p}f=()=>document.getElementById("{p}-n").textContent={J(d.get("pre", "$"))}+Math.round({p}v.v).toLocaleString("en-US")+{J(d.get("suf", ""))};'
    st = d["steps"]
    for i, x in enumerate(st):
        a = s.w(x["label_at"])
        js += f'tl.fromTo("#{p}-y{i}",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.25}},{a});'
        if i + 1 < len(st): js += f'tl.to("#{p}-y{i}",{{opacity:0,duration:.15}},{s.w(st[i+1]["label_at"])-.15});'
        v = s.w(x["value_at"]) - .4
        js += ((f'tl.call(()=>{{document.getElementById("{p}-n").textContent={J(x["text"])}}},null,{v+.4:.2f});' if x.get("text")   # 돈이 아닌 값 (11/05)
                else f'tl.to({p}v,{{v:{x["value"]},duration:.9,ease:"power3.out",onUpdate:{p}f}},{v});')
               + f'tl.to("#{p}-bf",{{scaleX:{x["bar"]},duration:.9,ease:"power3.out"}},{v});')
    if d.get("note"):
        html += f'<div class="note" id="{p}-note">{e(d["note"])}</div>'
        js += f'pop("#{p}-note",{s.w(st[0]["label_at"])});'
    return html, js

def split(p, s, d):
    a, b = d["a"], d["b"]
    html = (f'<div class="card" id="{p}-c"><div class="k">{e(d["k"])}</div><h3>{e(d["total"])}</h3>'
            f'<div class="sb"><div class="sa" id="{p}-a" style="width:{a["w"]*100:.1f}%"></div><div class="sbb" id="{p}-b" style="width:{100-a["w"]*100:.1f}%"></div></div>'
            f'<div class="sl"><div id="{p}-la" style="width:{max(a["w"],.38)*100:.0f}%"><b>{e(a["v"])}</b><span>{e(a["l"])}</span></div>'
            f'<div id="{p}-lb"><b>{e(b["v"])}</b><span>{e(b["l"])}</span></div></div></div>')
    js = (f'pop("#{p}-c",{s.t0});'
          f'tl.fromTo("#{p}-a",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},{s.w(a["at"])});tl.to("#{p}-la",{{opacity:1,duration:.3}},{s.w(a["at"])});'
          f'tl.fromTo("#{p}-b",{{scaleX:0}},{{scaleX:1,duration:1.2,ease:"power2.out"}},{s.w(b["at"])});tl.to("#{p}-lb",{{opacity:1,duration:.3}},{s.w(b["label_at"])-.3});')
    return html, js

def checklist(p, s, d):
    it = d["items"]; n = len(it)
    c0, c1 = s.w(d["from"]) + .3, s.w(d["to"]) + .5
    ts = [round(c0 + i * (c1 - c0) / (n - 1), 2) for i in range(n)]
    li = "".join(f'<div class="li{" b" if i in (0, n-1) else ""}" id="{p}-li{i}" style="top:{i*112}px"><span class="dot" id="{p}-d{i}">'
                 f'<svg viewBox="0 0 24 24"><path d="M6 12.5l4 4 8-9"/></svg></span>{e(x)}</div>' for i, x in enumerate(it))
    top = f' style="top:{d["top"]}px"' if d.get("top") else ''   # 레일 배지가 남아 있는 편은 목록을 내린다 (감독 편만)
    html = f'<div class="list"{top}><div class="lline" id="{p}-ll" style="height:{(n-1)*112}px"></div>{li}</div>'
    js = f'tl.fromTo("#{p}-ll",{{scaleY:0}},{{scaleY:1,duration:{c1-c0:.2f},ease:"none"}},{c0});'
    js += "".join(f'tl.to("#{p}-d{i}",{{backgroundColor:"#E3BE5A",borderColor:"#E3BE5A",duration:.15}},{t});'
                  f'tl.fromTo("#{p}-d{i} path",{{strokeDashoffset:24}},{{strokeDashoffset:0,duration:.2,ease:"power2.out"}},{t});'
                  f'tl.to("#{p}-li{i}",{{color:"#16140F",duration:.15}},{t});' for i, t in enumerate(ts))
    return html, js, ts

def compare(p, s, d):
    """두 금액 나란히. 숫자 아래 막대가 크기 비율을 보여주고, 차이(d.gap, 증명된 felt)가 두 카드 사이에 칩으로 뜬다.
    11/07 하림님 «이런 그래프 많이 봤는데 뭘 말하는지 안 보여»: 장식 곡선(비용 아래 올라가는 선) 폐기. 그림은 말하는 숫자 하나만 말한다."""
    a, b = d["a"], d["b"]
    va, vb = abs(_n(a["big"])), abs(_n(b["big"])); top = max(va, vb) or 1
    dots = '<div class="dots">' + "<i></i>" * a.get("dots", 0) + "</div>" if a.get("dots") else ""
    html = (f'<div class="card ca" id="{p}-a"><div class="k">{e(a["k"])}</div><b class="big"{fit(a["big"], 130, 400)}>{e(a["big"])}</b>{dots}<div class="bar"><i id="{p}-ba"></i></div><div class="ft">{e(a["ft"])}</div></div>'
            f'<div class="card cb" id="{p}-b"><div class="k">{e(b["k"])}</div><b class="big"{fit(b["big"], 130, 400)}>{e(b["big"])}</b><div class="bar"><i id="{p}-bb"></i></div><div class="ft">{e(b["ft"])}</div></div>'
            f'<div class="mid face" id="{p}-m"></div>')
    tb = s.w(b["at"])
    js = (f'pop("#{p}-a",{s.t0});pop("#{p}-b",{tb-.2});'
          f'tl.fromTo("#{p}-ba",{{scaleX:0}},{{scaleX:{va / top:.3f},duration:.6,ease:"expo.out"}},{s.t0+.4});'
          f'tl.fromTo("#{p}-bb",{{scaleX:0}},{{scaleX:{vb / top:.3f},duration:.6,ease:"expo.out"}},{tb+.2});'
          f'tl.fromTo("#{p}-m",{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.4,ease:"back.out(1.8)"}},{tb});'
          f'tl.fromTo("#{p}-a .dots i",{{scale:0}},{{scale:1,duration:.25,stagger:.05,ease:"back.out(2)"}},{s.t0+.3});')
    ticks = []
    if d.get("gap"):   # 차이 칩: 두 카드 사이, 차이를 말하는 순간 쾅
        tg = max(s.w(d.get("gap_at", 1)), tb + .4)
        html += f'<div class="gap" id="{p}-g"{fit(d["gap"] + " gap", 56, 520)}>{e(d["gap"])} <small>gap</small></div>'
        js += f'tl.fromTo("#{p}-g",{{opacity:0,scale:1.6,rotation:-6}},{{opacity:1,scale:1,rotation:-3,duration:.3,ease:"power4.in"}},{tg:.2f});'
        ticks.append(round(tg + .3, 2))
    return html, js, ticks

def _n(v):
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v).replace("−", "-"))
    return float(m.group(0).replace(",", "")) if m else 0.0

def tiles(p, s, d):
    word = d["word"]
    t0 = s.w(d["at"])
    ts = [round(t0 + i * .12, 2) for i in range(len(word))]
    html = (f'<div class="cava face" id="{p}-av"></div><div class="card cbar" id="{p}-bar">{e(d["bar"])}</div>'
            f'<div class="tiles">' + "".join(f'<span class="tile" id="{p}-t{i}">{e(c)}</span>' for i, c in enumerate(word)) + '</div>'
            f'<div class="card dm" id="{p}-dm"><i class="face"></i><div><b>{e(d["dm"][0])}</b><p>{e(d["dm"][1])}</p></div></div>'
            f'<div class="note" id="{p}-disc">{e(d["disc"])}</div>')
    rot = (-8, 6, -4, 7, -6, 5, -7, 4)
    tsend = s.w(d["dm_at"])
    js = (f'tl.to("#glow",{{opacity:1,duration:.6,ease:"power2.inOut"}},{s.t0});pop("#{p}-av",{s.t0});pop("#{p}-bar",{s.t0+.15});'
          + "".join(f'tl.fromTo("#{p}-t{i}",{{y:-260,opacity:0,rotation:{rot[i%8]}}},{{y:0,opacity:1,rotation:0,duration:.5,ease:"back.out(1.6)"}},{t});' for i, t in enumerate(ts))
          + f'pop("#{p}-dm",{tsend});pop("#{p}-disc",{tsend+.5});')
    return html, js, ts + [tsend]

def coins(p, s, d):
    """counter 와 같은 data + coins[해마다 동전 수]. 동전이 위에서 떨어져 쌓인다."""
    st = d["steps"]
    labs = "".join(f'<span id="{p}-y{i}">{e(x["label"])}</span>' for i, x in enumerate(st))
    cols = ""
    for i, (x, n) in enumerate(zip(st, d["coins"])):
        cols += f'<div class="col">' + "".join(f'<i class="coin" id="{p}-c{i}-{k}" style="bottom:{k*20}px"></i>' for k in range(n)) + f'<div class="lab">{e(x["label"])}</div></div>'
    html = (f'<div class="card" id="{p}-c"><div class="k yr">{labs}</div><div class="num" id="{p}-n">{e(d.get("pre", "$"))}0{e(d.get("suf", ""))}</div>'
            f'<div class="stacks">{cols}</div></div>')
    js = f'pop("#{p}-c",{s.t0});const {p}v={{v:0}},{p}f=()=>document.getElementById("{p}-n").textContent={J(d.get("pre", "$"))}+Math.round({p}v.v).toLocaleString("en-US")+{J(d.get("suf", ""))};'
    ticks = []
    for i, (x, n) in enumerate(zip(st, d["coins"])):
        a = s.w(x["label_at"])
        js += f'tl.fromTo("#{p}-y{i}",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.25}},{a});'
        if i + 1 < len(st): js += f'tl.to("#{p}-y{i}",{{opacity:0,duration:.15}},{s.w(st[i+1]["label_at"])-.15});'
        v = s.w(x["value_at"]) - .4
        js += (f'tl.call(()=>{{document.getElementById("{p}-n").textContent={J(x["text"])}}},null,{v+.4:.2f});' if x.get("text")   # 돈이 아닌 값 (4 months)
               else f'tl.to({p}v,{{v:{x["value"]},duration:.9,ease:"power3.out",onUpdate:{p}f}},{v});')
        gap = min(.06, .9 / n)
        for k in range(n):
            js += f'tl.fromTo("#{p}-c{i}-{k}",{{opacity:0,y:-420}},{{opacity:1,y:0,duration:.32,ease:"power2.in"}},{v+k*gap:.2f});'
        ticks += [round(v + .32 + k * gap, 2) for k in range(0, n, 3)]
    return html, js, ticks

def receipt(p, s, d):
    """영수증이 프린터 틈에서 내려온다. rows[[이름, 값, 나올 단어]], total[이름, 값, 나올 단어]."""
    rows = "".join(f'<div class="r" id="{p}-r{i}"><span>{e(a)}</span><b>{e(b)}</b></div>' for i, (a, b, _) in enumerate(d["rows"]))
    tn, tv, tat = d["total"]
    html = (f'<div class="slot"></div><div class="win"><div class="paper" id="{p}-pp"><div class="hd">{e(d["title"])}</div><div class="sub">{e(d["sub"])}</div><hr>{rows}<hr>'
            f'<div class="tot" id="{p}-tot"><span>{e(tn)}</span><b{fit(tv, 76, 360)}><i id="{p}-hl"></i><span>{e(tv)}</span></b></div><div class="ft" id="{p}-ft">{e(d.get("foot",""))}</div></div></div>')
    js = (f'tl.fromTo("#{p}-pp",{{yPercent:-100}},{{yPercent:0,duration:1.6,ease:"steps(16)"}},{s.t0});'
          + "".join(f'tl.fromTo("#{p}-r{i}",{{opacity:0,x:-12}},{{opacity:1,x:0,duration:.3,ease:"power3.out"}},{s.w(at)});' for i, (_, _, at) in enumerate(d["rows"]))
          + f'tl.fromTo("#{p}-tot",{{opacity:0}},{{opacity:1,duration:.3}},{s.w(tat)});tl.fromTo("#{p}-hl",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"expo.out"}},{s.w(tat)+.15});'
          + f'tl.to("#{p}-ft",{{opacity:1,duration:.3}},{s.w(tat)+.4});')
    return html, js, [s.t0 + .1 * k for k in range(0, 16, 2)] + [s.w(tat)]

def swap(p, s, d):
    """큰 단어 교체. old 가 흐려지며 사라지고 new 가 글자마다 올라온다. sub 는 아래 이탤릭 한 줄."""
    t = s.w(d["at"])
    letters = "".join(f'<span id="{p}-n{i}">{e(c) if c != " " else "&nbsp;"}</span>' for i, c in enumerate(d["new"]))
    html = f'<div class="old" id="{p}-o"{fit(d["old"], 150, 1000)}>{e(d["old"])}</div><div class="new"{fit(d["new"], 150, 1000)}>{letters}</div>'   # 긴 말은 폭에 맞춘다 (11/06 «the cost of waiti…»)
    js = (f'tl.fromTo("#{p}-o",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.4,ease:"power3.out"}},{s.t0+.1});'
          f'tl.to("#{p}-o",{{opacity:0,y:-40,filter:"blur(12px)",duration:.35,ease:"power2.in"}},{t-.2});'
          + "".join(f'tl.fromTo("#{p}-n{i}",{{opacity:0,y:90}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{t+.1+i*.035:.2f});' for i in range(len(d["new"]))))
    if d.get("sub"):
        html += f'<div class="sub" id="{p}-sb">{e(d["sub"])}</div>'
        js += f'tl.fromTo("#{p}-sb",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"power3.out"}},{s.w(d["sub_at"]) if d.get("sub_at") else t+.6});'
    return html, js, [t + .1]

def stack(p, s, d):
    """아이소 판이 오른쪽 위에서 날아와 층층이 쌓인다 → hi 판을 골드로 → stand_at 에 바로 서며 위아래로 나란해진다."""
    L = d["layers"]; n = len(L)
    plates = "".join(f'<div class="plate {x.get("tone","")}" id="{p}-p{i}"><b>{e(x["h"])}</b><em>{e(x["v"])}</em><span>{e(x["sub"])}</span></div>' for i, x in enumerate(L))
    html = f'<div class="stage"><div class="iso" id="{p}-iso">{plates}</div></div>'
    js = f'tl.set("#{p}-iso",{{rotationX:56,rotationZ:-38}},0);'
    ticks = []
    for i, x in enumerate(L):
        a = s.w(x["at"])
        js += f'tl.fromTo("#{p}-p{i}",{{opacity:0,x:260,y:-260,z:{i*130+300}}},{{opacity:1,x:0,y:0,z:{i*130},duration:.5,ease:"power3.out"}},{a});'
        ticks.append(round(a + .45, 2))
    if d.get("hi_at") is not None:
        h = s.w(d["hi_at"]); hi = d["hi"]
        js += f'tl.to("#{p}-p{hi}",{{borderColor:"#9A7414",backgroundColor:"#FFF6DD",duration:.25}},{h});'
        # 판은 불투명하게 두고 글자만 낮춘다 (반투명이면 뒤 판 글자가 비친다, 11/04)
        js += "".join(f'tl.to("#{p}-p{i} b,#{p}-p{i} em,#{p}-p{i} span",{{color:"#B8B1A3",duration:.25}},{h});' for i in range(n) if i != hi)
    if d.get("stand_at"):
        t = s.w(d["stand_at"])
        js += f'tl.to("#{p}-iso",{{rotationX:0,rotationZ:0,duration:.6,ease:"power3.inOut"}},{t});'
        js += "".join(f'tl.to("#{p}-p{i}",{{z:0,y:{(i-(n-1)/2)*430 - 0:.0f},opacity:1,duration:.6,ease:"power3.inOut"}},{t});' for i in range(n))
        ticks.append(round(t + .55, 2))
    return html, js, ticks

def _karaoke(p, s, words, tag, at=0, wrap=False):
    """화면 문장 = 첫마디. 처음부터 다 보이고, 말하는 순간 단어가 골드로 바뀐다. at = 앞서 말한 단어 수. wrap = 단어마다 클립 마스크(.mk, rise 가 올린다)."""
    toks = [t for b in s.beats for t in b["toks"]]
    neg = [bool(re.match(r"^[-−]\$?\d", w)) for w in words]   # 마이너스 숫자는 처음부터 로즈 (11/05)
    W = (lambda x: f'<span class="mk">{x}</span>') if wrap else (lambda x: x)
    spans = "".join(W(f'<span id="{p}-{tag}{i}"{NEG if n else ""}>{e(w)}</span>') + " " for i, (w, n) in enumerate(zip(words, neg)))
    js = "".join(f'tl.to("#{p}-{tag}{i}",{{color:"#9A7414",duration:.12}},{toks[min(at+i, len(toks)-1)][0]:.2f});' for i in range(len(words)) if not neg[i])
    return spans, js

def _promise(p, s, d, at):
    """② 약속 줄 (hooks.json one_second). 0초부터 흐리게 있고, 말할 때 단어가 켜진다."""
    if not d.get("promise"): return "", ""
    toks = [t for b in s.beats for t in b["toks"]]; w = d["promise"].split()
    spans = "".join(f'<span id="{p}-p{i}">{e(x)}</span> ' for i, x in enumerate(w))
    js = "".join(f'tl.fromTo("#{p}-p{i}",{{opacity:.35}},{{opacity:1,duration:.15}},{toks[min(at+i, len(toks)-1)][0]:.2f});' for i in range(len(w)))
    return f'<div class="oprom">{spans}</div>', js

def ostamp(p, s, d, base=840, top=None):
    """첫 장면 도장: 포모 명령(d.stamp)이 숫자 위 오른쪽에 로즈 도장으로 0.1초에 쾅, 한 번 흔들린다 (11/06). top 을 주면 그 자리에 (title2 는 숫자가 글줄 안에 있어 둘째 줄 아래)."""
    if not d.get("stamp"): return "", ""
    t = s.t0 + .6   # 도장은 말하지 않는다. 훅 첫 숫자쯤에 한 번 흔들린다
    px = min(48, int(420 / (len(d["stamp"]) * .58)))
    html = f'<div class="ostamp" id="{p}-os" style="top:{top if top is not None else base - numpx(d["num"]) - 104}px;font-size:{px}px">{e(d["stamp"])}</div>'
    js = (f'tl.fromTo("#{p}-os",{{opacity:0,scale:2,rotation:-24}},{{opacity:1,scale:1,rotation:-12,duration:.22,ease:"power4.in"}},.1);'
          f'tl.fromTo("#{p}-os",{{x:0}},{{x:10,duration:.05,yoyo:true,repeat:3,ease:"none"}},{t:.2f});')
    return html, js

def hooknum(p, s, d):
    """첫 장면 A: 물건 알약 → 아주 큰 숫자 + 골드 밑줄 → 훅 한 줄 → 하마 얼굴."""
    spans, kj = _karaoke(p, s, d["line"].split(), "w")
    ph, pj = _promise(p, s, d, len(d["line"].split()))
    sh, sj = ostamp(p, s, d, 840)
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div><div class="num{negc(d["num"], d)}"{numst(d["num"])}>{e(d["num"])}</div><div class="ul" id="{p}-ul"></div>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    js = (f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.15);'
          f'tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + kj + pj)
    return html, js + sj

def title2(p, s, d):
    """첫 장면 B: 물건 알약 → 숫자가 든 첫 줄(숫자 가장 크게) → 세리프 이탤릭 둘째 줄 → 하마 얼굴."""
    w1, w2 = d["l1"].split(), d["l2"].split()
    s1, k1 = _karaoke(p, s, w1, "a")
    toks = [t for b in s.beats for t in b["toks"]]
    s2 = "".join(f'<span id="{p}-b{i}">{e(w)}</span> ' for i, w in enumerate(w2))
    k2 = "".join(f'tl.fromTo("#{p}-b{i}",{{opacity:.35}},{{opacity:1,duration:.15}},{toks[min(len(w1)+i, len(toks)-1)][0]:.2f});' for i in range(len(w2)))
    ph, pj = _promise(p, s, d, len(w1) + len(w2))
    sh, sj = ostamp(p, s, d, 840, top=1010)   # title2: 숫자가 첫 줄 안에 있어 둘째 줄 아래, 약속 위
    l1s = f' style="font-size:{min(96, int(920 / (max(len(d["l1"]), 1) * .58)))}px"' if len(d["l1"]) > 17 else ""   # 긴 첫 줄은 줄인다 (11/06: 18자 규칙으로 title2 가 0편)
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div><div class="oline l1"{l1s}><b class="{negc(d["num"], d).strip()}">{e(d["num"])}</b>{s1}</div>'
            f'<div class="oline l2">{s2}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    js = f'tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + k1 + k2 + pj
    return html, js + sj

def slam(p, s, d):
    """첫 장면 C: 손해 숫자(로즈)가 위에서 쾅 떨어지고 화면이 흔들린다. 1초 안에 «얼마»가 때리게 (11/04 하림님)."""
    spans, kj = _karaoke(p, s, d["line"].split(), "w")
    ph, pj = _promise(p, s, d, len(d["line"].split()))
    sh, sj = ostamp(p, s, d, 840)
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div>'
            f'<div class="num{negc(d["num"], d)}" id="{p}-n"{numst(d["num"])}>{e(d["num"])}</div>'
            f'<div class="ul" id="{p}-ul"></div><div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    js = (f'tl.fromTo("#{p}-n",{{opacity:1,scale:1.35,rotation:-4,y:-40}},{{opacity:1,scale:1,rotation:0,y:0,duration:.22,ease:"power4.in"}},0);'
          f'tl.fromTo("#{p}",{{x:0}},{{x:11,duration:.045,yoyo:true,repeat:5,ease:"none"}},.34);'
          f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"expo.out"}},.4);'
          f'tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + kj + pj)
    return html, js + sj, [.34]

def tease(p, s, d):
    """첫 장면 D: 공식 그대로 + ② 이득 2~4단어가 골드 칩으로 쾅 + 저장할 물건 카드가 아래서 삐죽(흐린 줄). 이득이 보이게 (11/04 하림님)."""
    spans, kj = _karaoke(p, s, d["line"].split(), "w")
    pw = (d.get("promise") or "").split()
    pre, gain = (pw[:4], pw[4:]) if len(pw) > 4 else (pw, pw[-2:])
    toks = [t for b in s.beats for t in b["toks"]]; at = len(d["line"].split())
    pres = "".join(f'<span id="{p}-p{i}">{e(x)}</span> ' for i, x in enumerate(pre))
    pj = "".join(f'tl.fromTo("#{p}-p{i}",{{opacity:.35}},{{opacity:1,duration:.15}},{toks[min(at+i,len(toks)-1)][0]:.2f});' for i in range(len(pre)))
    gt = toks[min(at + len(pre), len(toks) - 1)][0]
    sh, sj = ostamp(p, s, d, 820)
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div>'
            f'<div class="num{negc(d["num"], d)}"{numst(d["num"], 820)}>{e(d["num"])}</div><div class="ul" id="{p}-ul"></div>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div><div class="oprom">{pres}</div>'
            f'<div class="gchip" id="{p}-g"{fit(" ".join(gain), 66, 960)}>{e(" ".join(gain).upper().rstrip("."))}</div>'
            f'<div class="tcard" id="{p}-t"><b>{e(d["pill"])}</b><i></i><i></i><i></i></div>')
    js = (f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.15);'
          f'tl.fromTo("#{p}-t",{{y:150}},{{y:0,duration:.8,ease:"power3.out"}},.3);'
          f'tl.fromTo("#{p}-g",{{opacity:0,scale:2,rotation:6}},{{opacity:1,scale:1,rotation:-3,duration:.3,ease:"power4.in"}},{gt:.2f});' + kj + pj)
    return html, js + sj, [round(gt + .3, 2)]

def stamp(p, s, d):
    """손해: 금액 카드가 서고, at 에 빨간 도장이 비스듬히 쾅 (기울며 내려앉고 카드가 한 번 흔들린다)."""
    t = s.w(d["at"])
    html = (f'<div class="card" id="{p}-c"><div class="k">{e(d.get("k") or "")}</div><div class="amt"{fit(d["old"], 190, 580)}>{e(d["old"])}</div></div>'
            f'<div class="st" id="{p}-st"{fit(d["new"], 92, 520)}>{e(d["new"])}</div>')
    js = (f'pop("#{p}-c",{s.t0});'
          f'tl.fromTo("#{p}-st",{{opacity:0,scale:2.2,rotation:-24}},{{opacity:1,scale:1,rotation:-9,duration:.22,ease:"power4.in"}},{t-.1:.2f});'
          f'tl.fromTo("#{p}-c",{{x:0}},{{x:12,duration:.05,yoyo:true,repeat:3,ease:"none"}},{t+.12:.2f});')
    return html, js, [round(t + .12, 2)]

def strike(p, s, d):
    """믿음·예외: ✓ 붙은 말 → 빨간 취소선 + X → 아래에서 진짜 말(로즈) + 이탤릭 한 줄."""
    t = s.w(d["at"])
    html = (f'<div class="chip" id="{p}-c"><i>✓</i>{e(d["old"])}<span class="line" id="{p}-l"></span><span class="x" id="{p}-x">✕</span></div>'
            f'<div class="tru" id="{p}-t">{e(d["new"])}</div>')
    js = (f'pop("#{p}-c",{s.t0});tl.set("#{p}-l",{{scaleX:0}},0);'
          f'tl.to("#{p}-l",{{scaleX:1,duration:.25,ease:"power2.out"}},{t:.2f});'
          f'tl.fromTo("#{p}-x",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.2,ease:"back.out(2.5)"}},{t+.2:.2f});'
          f'tl.fromTo("#{p}-t",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{t+.35:.2f});')
    if d.get("sub"):
        html += f'<div class="sub" id="{p}-sb">{e(d["sub"])}</div>'
        js += f'tl.fromTo("#{p}-sb",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},{s.w(d["sub_at"]) if d.get("sub_at") is not None else t+.8});'
    return html, js, [round(t + .2, 2)]

def chart(p, s, d):
    """주가 창: 카드가 서고 선이 왼쪽에서 그려지며 떨어진다. 끝에 등락률이 한 번 튄다. d = chart.py 스냅숏."""
    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parents[2])); import chart as ch
    if d.get("long"):   # 공포에서 부자 (11/05): 한 달 폭락이 그려지고 → 줌아웃 → 10년 선이 오른다. 끝에 이번 달 구간이 로즈로
        a, b = d["chart"], d["long"]; ts0 = s.w(d.get("short_at", 0)); tz = max(s.w(d.get("at", 1)), ts0 + 2.2)   # 11/06: 하락 줄에서 그리고, zoom 줄에서 줌
        html = (f'<style>{ch.CSS}</style><div class="zz">' + ch.window(a, f"{p}-s-")
                + ch.window(b, f"{p}-l-", mark=a["ts"][0]) + f'<div class="zbadge" id="{p}-zb">ZOOM OUT</div></div>')
        js = (f'pop("#{p}-s-w",{s.t0});tl.set("#{p}-l-w",{{opacity:0}},0);tl.set("#{p}-s-pc",{{opacity:0}},0);'
              f'tl.fromTo("#{p}-s-a .cl",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.6,ease:"power2.out"}},{ts0+.1:.2f});'
              f'tl.fromTo("#{p}-s-a .cf",{{opacity:0}},{{opacity:1,duration:.6}},{ts0+1.1:.2f});'
              f'tl.fromTo("#{p}-s-pc",{{opacity:0,scale:1}},{{opacity:1,scale:1.35,duration:.14,yoyo:true,repeat:1,transformOrigin:"right center"}},{ts0+1.6:.2f});tl.set("#{p}-s-pc",{{opacity:1}},{ts0+1.9:.2f});'
              # 줌아웃: 한 달 그림이 오른쪽 끝으로 쪼그라들며 사라지고, 같은 자리에 10년 창
              f'tl.fromTo("#{p}-zb",{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.25,ease:"back.out(2)"}},{tz-.35:.2f});'
              f'tl.to("#{p}-s-a",{{scaleX:.08,scaleY:.5,transformOrigin:"100% 100%",duration:.6,ease:"power3.in"}},{tz:.2f});'
              f'tl.to("#{p}-s-w",{{opacity:0,duration:.25}},{tz+.45:.2f});tl.to("#{p}-zb",{{opacity:0,duration:.25}},{tz+.6:.2f});'
              f'tl.to("#{p}-l-w",{{opacity:1,duration:.2}},{tz+.2:.2f});'
              f'tl.set("#{p}-l-a .cm, #{p}-l-a .cmr",{{opacity:0}},0);'
              f'tl.fromTo("#{p}-l-a .cl",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.4,ease:"power2.out"}},{tz+.2:.2f});'
              f'tl.fromTo("#{p}-l-a .cf",{{opacity:0}},{{opacity:1,duration:.6}},{tz+1.0:.2f});'
              f'tl.to("#{p}-l-a .cm, #{p}-l-a .cmr",{{opacity:1,duration:.35}},{tz+1.6:.2f});'
              f'tl.fromTo("#{p}-l-pc",{{scale:1}},{{scale:1.4,duration:.16,yoyo:true,repeat:1,transformOrigin:"right center"}},{tz+1.5:.2f});')
        return html, js, [round(ts0 + 1.6, 2), round(tz, 2), round(tz + 1.5, 2)]
    html = f'<style>{ch.CSS}</style>' + ch.window(d, f"{p}-")
    t1 = s.t0 + 2.0
    js = (f'pop("#{p}-w",{s.t0});'
          f'tl.fromTo("#{p}-a .cl",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.8,ease:"power1.in"}},{s.t0+.2:.2f});'
          f'tl.fromTo("#{p}-a .cf",{{opacity:0}},{{opacity:1,duration:.8}},{s.t0+1.2:.2f});'
          f'tl.fromTo("#{p}-pc",{{scale:1}},{{scale:1.35,duration:.14,yoyo:true,repeat:1,transformOrigin:"right center"}},{t1:.2f});')
    ticks = [round(t1, 2)]
    if d.get("second"):   # 둘째 티커 창 (11/07): 첫 창이 위로 줄고, 둘째 창이 아래서 올라와 선을 그린다
        t2 = max(s.w(d.get("second_at", 1)), t1 + .3)
        html += f'<div class="w2">{ch.window(d["second"], f"{p}-2-")}</div>'
        js += (f'tl.set("#{p}-2-w",{{opacity:0}},0);tl.to("#{p}-w",{{scale:.74,transformOrigin:"top center",duration:.5,ease:"power3.inOut"}},{t2:.2f});'
               f'tl.fromTo("#{p}-2-w",{{opacity:0,y:120,scale:.74}},{{opacity:1,y:0,scale:.74,duration:.5,ease:"power3.out",transformOrigin:"top center"}},{t2+.1:.2f});'
               f'tl.fromTo("#{p}-2-a .cl",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.4,ease:"power1.in"}},{t2+.4:.2f});'
               f'tl.fromTo("#{p}-2-a .cf",{{opacity:0}},{{opacity:1,duration:.6}},{t2+1.2:.2f});'
               f'tl.fromTo("#{p}-2-pc",{{scale:1}},{{scale:1.35,duration:.14,yoyo:true,repeat:1,transformOrigin:"right center"}},{t2+1.8:.2f});')
        ticks.append(round(t2 + 1.8, 2))
    return html, js, ticks


# ── 3단계 1라운드 (11/06): REF fx-목록 H4 · D11 · N2 ─────────────────────
def table(p, s, d):
    """H4 장표 «내 행»: 조회표 행이 하나씩 채워지고, hi 행이 at 에 골드 형광으로 켜진다. d = {cols, rows:[{lab, cells}], hi, at}."""
    cols = d["cols"]; rows = d["rows"]; n = len(rows); w = max(1, len(cols))
    head = f'<div class="th"><span></span>' + "".join(f'<span>{e(c)}</span>' for c in cols) + '</div>'
    body = "".join(f'<div class="tr" id="{p}-r{i}"><span class="lab">{e(r["lab"])}</span>' + "".join(f'<span{fit(c, 44, 760 // w - 20)}>{e(c)}</span>' for c in r["cells"]) + '</div>' for i, r in enumerate(rows))
    html = f'<div class="card" id="{p}-c" style="--cols:{w}"><div class="k">{e(d.get("k") or "")}</div>{head}{body}<div class="hl" id="{p}-hl" style="top:{150 + 40 + d["hi"] * 104}px"></div></div>'
    t0 = s.t0 + .3; gap = min(.35, 1.2 / n)
    js = f'pop("#{p}-c",{s.t0});' + "".join(f'tl.fromTo("#{p}-r{i}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.3,ease:"power3.out"}},{t0 + i * gap:.2f});' for i in range(n))
    th = s.w(d["at"]) if d.get("at") is not None else t0 + n * gap + .3
    js += (f'tl.fromTo("#{p}-hl",{{opacity:0,scaleX:0}},{{opacity:1,scaleX:1,duration:.4,ease:"expo.out"}},{th:.2f});'
           f'tl.to("#{p}-r{d["hi"]} span",{{color:"#16140F",fontWeight:800,duration:.2}},{th:.2f});'
           f'tl.fromTo("#{p}-r{d["hi"]}",{{scale:1}},{{scale:1.04,duration:.15,yoyo:true,repeat:1}},{th:.2f});')
    return html, js, [round(th, 2)]

def wipe(p, s, d):
    """D11 세로 와이프 전 → 후: 손해 판(로즈) 위를 골드 선이 쓸고 지나가며 이득 판이 드러난다. d = {a:{h,v,sub}, b:{h,v,sub}, at}."""
    a, b = d["a"], d["b"]
    def pane(k, x, cls): return (f'<div class="pane {cls}" id="{p}-{k}"><div class="k">{e(x["h"])}</div><b{fit(x["v"], 170, 760)}>{e(x["v"])}</b><span>{e(x.get("sub", ""))}</span></div>')
    html = pane("a", a, "la") + pane("b", b, "wb") + f'<div class="wline" id="{p}-wl"></div>'
    t = s.w(d["at"]) if d.get("at") is not None else s.t0 + 1.4
    js = (f'pop("#{p}-a",{s.t0});tl.set("#{p}-b",{{opacity:1,clipPath:"inset(0 100% 0 0)"}},0);tl.set("#{p}-wl",{{opacity:0,x:0}},0);'
          f'tl.to("#{p}-wl",{{opacity:1,duration:.1}},{t - .05:.2f});'
          f'tl.to("#{p}-b",{{clipPath:"inset(0 0% 0 0)",duration:.7,ease:"power3.inOut"}},{t:.2f});'
          f'tl.to("#{p}-wl",{{x:960,duration:.7,ease:"power3.inOut"}},{t:.2f});tl.to("#{p}-wl",{{opacity:0,duration:.15}},{t + .7:.2f});'
          f'tl.fromTo("#{p}-b b",{{scale:.9}},{{scale:1,duration:.35,ease:"back.out(2)"}},{t + .45:.2f});')
    return html, js, [round(t + .7, 2)]

def odometer(p, s, d):
    """N2 자릿수 오도미터: 끝자리부터 빠르게, 앞자리는 느리게 돌아 to 에 멈춘다. d = {from, to, pre, suf, label, at}. to 는 «71,000» 꼴."""
    to = str(d["to"]); frm = str(d.get("from", "0")).rjust(len(to), "0")
    cols = ""
    for i, ch in enumerate(to):
        if ch.isdigit():
            cols += f'<span class="dg"><i id="{p}-d{i}">' + "".join(f'<b>{k}</b>' for k in range(10)) + '</i></span>'
        else: cols += f'<span class="sep">{e(ch)}</span>'
    html = (f'<div class="card" id="{p}-c"><div class="k">{e(d.get("label", ""))}</div><div class="od" style="font-size:{min(190, 1300 // max(len(to) + len(d.get("pre", "")), 1))}px">'
            f'<span class="sep">{e(d.get("pre", ""))}</span>{cols}<span class="sep">{e(d.get("suf", ""))}</span></div></div>')
    t = s.w(d["at"]) if d.get("at") is not None else s.t0 + .6
    nd = sum(ch.isdigit() for ch in to); k = 0
    js = f'pop("#{p}-c",{s.t0});'
    for i, ch in enumerate(to):
        if not ch.isdigit(): continue
        f0 = int(frm[i]) if frm[i].isdigit() else 0
        dur = .5 + (nd - 1 - k) * .22   # 앞자리가 더 오래 돈다
        js += f'tl.fromTo("#{p}-d{i}",{{yPercent:{-f0 * 10}}},{{yPercent:{-int(ch) * 10},duration:{dur:.2f},ease:"power3.out"}},{t:.2f});'
        k += 1
    js += f'tl.fromTo("#{p}-c",{{x:0}},{{x:6,duration:.04,yoyo:true,repeat:3,ease:"none"}},{t + .5 + (nd - 1) * .22:.2f});'
    return html, js, [round(t + .5 + (nd - 1) * .22, 2)]


# ── 3단계 2라운드 (11/06): D14 multiply · N6 shrink · P4 funnel · N4 clock · U13 countdown · U9 notify · N8 donut · 첫 장면 rollnum ──
def multiply(p, s, d):
    """D14 복붙 증식: 칸이 1 → 2 → 4 → … 로 불어나고 위 숫자가 따라 오른다. d = {steps:[{label, value, n, at}], pre, suf}. n = 칸 수(≤16)."""
    st = d["steps"]; top = max(x["n"] for x in st) or 1
    cells = "".join(f'<i id="{p}-c{k}"></i>' for k in range(top))
    html = (f'<div class="card" id="{p}-c"><div class="k" id="{p}-k">{e(st[0]["label"])}</div><div class="num" id="{p}-n">{e(d.get("pre", "$"))}0{e(d.get("suf", ""))}</div>'
            f'<div class="grid">{cells}</div></div>')
    js = f'pop("#{p}-c",{s.t0});'
    ticks = []; shown = 0
    for i, x in enumerate(st):
        t = s.w(x["at"]); n = max(1, x["n"])
        js += f'tl.call(()=>{{document.getElementById("{p}-k").textContent={J(x["label"])};document.getElementById("{p}-n").textContent={J(d.get("pre", "$") + x["value"] + d.get("suf", ""))}}},null,{t:.2f});'
        for k in range(shown, n):
            js += f'tl.fromTo("#{p}-c{k}",{{opacity:0,scale:.3}},{{opacity:1,scale:1,duration:.25,ease:"back.out(2)"}},{t + (k - shown) * (.6 / max(1, n - shown)):.2f});'
        shown = n; ticks.append(round(t, 2))
    return html, js, ticks

def shrink(p, s, d):
    """N6 줄어드는 막대: 넣은 돈 막대가 수수료·세금에 깎여 줄고 색이 골드 → 로즈로. d = {bars:[{l, v, w, at}]} (w 0~1)."""
    bars = "".join(f'<div class="row"><span class="l">{e(b["l"])}</span><div class="bar"><div class="f" id="{p}-f{i}" style="width:100%"></div></div><b id="{p}-v{i}"{fit(b["v"], 44, 220)}>{e(b["v"])}</b></div>' for i, b in enumerate(d["bars"]))
    html = f'<div class="card" id="{p}-c"><div class="k">{e(d.get("k") or "")}</div>{bars}</div>'
    js = f'pop("#{p}-c",{s.t0});'; ticks = []
    for i, b in enumerate(d["bars"]):
        t = s.w(b["at"]); w = max(.06, min(1, b["w"]))
        col = "#E3BE5A" if w > .66 else "#E08A3C" if w > .33 else "#D8415C"
        js += (f'tl.set("#{p}-v{i}",{{opacity:0}},0);tl.to("#{p}-f{i}",{{width:"{w*100:.0f}%",backgroundColor:"{col}",duration:.8,ease:"power3.inOut"}},{t:.2f});'
               f'tl.to("#{p}-v{i}",{{opacity:1,duration:.2}},{t + .5:.2f});')
        ticks.append(round(t + .8, 2))
    return html, js, ticks

def funnel(p, s, d):
    """P4 깔때기: 위에서 돈이 들어가고 옆으로 새고(로즈) 아래로 남은 돈이 쌓인다. d = {in, leak, out, label, in_at, leak_at, out_at}."""
    dots = "".join(f'<i class="dot" id="{p}-d{k}" style="left:{300 + (k * 37) % 480}px"></i>' for k in range(14))
    html = (f'<div class="fun" id="{p}-c"><div class="top" id="{p}-in"><span>IN</span><b{fit(d["in"], 70, 400)}>{e(d["in"])}</b></div>'
            f'<svg class="shape" viewBox="0 0 600 420"><path d="M40 0 L560 0 L340 300 L340 420 L260 420 L260 300 Z"/></svg>{dots}'
            f'<div class="leak" id="{p}-lk"><b{fit(d["leak"], 60, 330)}>{e(d["leak"])}</b><span>{e(d.get("label", "leaks out"))}</span></div>'
            f'<div class="out" id="{p}-out"><span>LEFT</span><b{fit(d["out"], 96, 520)}>{e(d["out"])}</b></div></div>')
    ti, tl_, to = s.w(d["in_at"]), s.w(d["leak_at"]), s.w(d["out_at"])
    js = (f'pop("#{p}-c",{s.t0});tl.fromTo("#{p}-in",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.4}},{ti:.2f});'
          + "".join(f'tl.fromTo("#{p}-d{k}",{{opacity:0,y:-60}},{{opacity:1,y:{330 + (k % 3) * 20},duration:.9,ease:"power1.in"}},{ti + .1 + k * .08:.2f});tl.to("#{p}-d{k}",{{opacity:0,duration:.2}},{ti + 1.1 + k * .08:.2f});' for k in range(14))
          + f'tl.fromTo("#{p}-lk",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.4,ease:"power3.out"}},{tl_:.2f});'
          + f'tl.fromTo("#{p}-out",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5,ease:"expo.out"}},{to:.2f});')
    return html, js, [round(tl_, 2), round(to, 2)]

def clock(p, s, d):
    """N4 시계 부채꼴: 부채꼴이 차오르며 가운데 카운터가 오른다. d = {total, filled, unit, label, at}. filled/total = 채우는 비율."""
    r = 300; C = 2 * 3.14159 * r
    html = (f'<div class="card" id="{p}-c"><div class="k">{e(d.get("label", ""))}</div><svg class="ring" viewBox="0 0 700 700"><circle class="bg" cx="350" cy="350" r="{r}"/>'
            f'<circle class="fg" id="{p}-arc" cx="350" cy="350" r="{r}" style="stroke-dasharray:{C:.0f};stroke-dashoffset:{C:.0f}"/></svg>'
            f'<div class="mid"><b id="{p}-n">0</b><span>{e(d.get("unit", ""))}</span></div></div>')
    t = s.w(d["at"]); frac = max(.02, min(1, float(d["filled"]) / max(float(d["total"]), 1)))
    js = (f'pop("#{p}-c",{s.t0});const {p}v={{v:0}};tl.to("#{p}-arc",{{strokeDashoffset:{C * (1 - frac):.0f},duration:1.4,ease:"power2.inOut"}},{t:.2f});'
          f'tl.to({p}v,{{v:{float(d["filled"])},duration:1.4,ease:"power2.inOut",onUpdate:()=>document.getElementById("{p}-n").textContent=Math.round({p}v.v).toLocaleString("en-US")}},{t:.2f});')
    return html, js, [round(t + 1.4, 2)]

def countdown(p, s, d):
    """U13 다이내믹 아일랜드 3·2·1 → 마감 날짜 LIVE. d = {label, date, at}."""
    html = (f'<div class="isl" id="{p}-c"><span class="cnt" id="{p}-n">3</span><span class="lab" id="{p}-l">{e(d["label"])}</span></div>'
            f'<div class="dl" id="{p}-d"><span>DEADLINE</span><b{fit(d["date"], 150, 900)}>{e(d["date"])}</b><i class="live"><u></u>LIVE</i></div>')
    t = s.w(d["at"])
    js = (f'tl.fromTo("#{p}-c",{{opacity:0,scaleX:.4}},{{opacity:1,scaleX:1,duration:.4,ease:"back.out(1.6)"}},{s.t0 + .1:.2f});'
          + "".join(f'tl.call(()=>document.getElementById("{p}-n").textContent="{3 - k}",null,{s.t0 + .5 + k * .5:.2f});tl.fromTo("#{p}-n",{{scale:1.5}},{{scale:1,duration:.3}},{s.t0 + .5 + k * .5:.2f});' for k in range(3))
          + f'tl.to("#{p}-c",{{width:900,duration:.4,ease:"power3.inOut"}},{t - .2:.2f});tl.fromTo("#{p}-d",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{t:.2f});')
    return html, js, [round(s.t0 + .5, 2), round(s.t0 + 1.0, 2), round(s.t0 + 1.5, 2), round(t, 2)]

def notify(p, s, d):
    """U9 알림 쌓임: 폰 알림이 위에서 하나씩 떨어져 쌓이고 배지 합계가 오른다. d = {items:[{app, v, at}], total}."""
    items = "".join(f'<div class="nt" id="{p}-n{i}" style="top:{120 + i * 150}px"><i class="face"></i><div><b>{e(x["app"])}</b><span>{e(x["v"])}</span></div></div>' for i, x in enumerate(d["items"]))
    html = f'<div class="phone" id="{p}-c"><div class="badge2" id="{p}-b">0</div>{items}<div class="tot" id="{p}-t"><span>TOTAL</span><b{fit(d["total"], 90, 520)}>{e(d["total"])}</b></div></div>'
    js = f'pop("#{p}-c",{s.t0});'; ticks = []
    for i, x in enumerate(d["items"]):
        t = s.w(x["at"])
        js += f'tl.fromTo("#{p}-n{i}",{{opacity:0,y:-120}},{{opacity:1,y:0,duration:.45,ease:"back.out(1.4)"}},{t:.2f});tl.call(()=>document.getElementById("{p}-b").textContent="{i + 1}",null,{t + .2:.2f});tl.fromTo("#{p}-b",{{scale:1.5}},{{scale:1,duration:.25}},{t + .2:.2f});'
        ticks.append(round(t, 2))
    tt = s.w(d.get("total_at", d["items"][-1]["at"])) + .5
    js += f'tl.fromTo("#{p}-t",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{tt:.2f});'
    return html, js, ticks

def donut(p, s, d):
    """N8 도넛: 조각이 차례로 그려지고 hi 조각만 골드로 튄다. d = {segs:[{l, v, w}], hi, at}. w 는 0~1 비율."""
    r = 240; C = 2 * 3.14159 * r; segs = d["segs"]; off = 0; circ = ""; leg = ""
    for i, sg in enumerate(segs):
        w = max(.02, min(1, sg["w"])); dash = C * w
        circ += f'<circle id="{p}-s{i}" class="{"hi" if i == d["hi"] else "sg"}" cx="350" cy="350" r="{r}" style="stroke-dasharray:{dash:.0f} {C:.0f};stroke-dashoffset:{-off:.0f}"/>'
        leg += f'<div class="lg{" hi" if i == d["hi"] else ""}" id="{p}-l{i}"><i></i><b>{e(sg["v"])}</b><span>{e(sg["l"])}</span></div>'
        off += dash
    html = f'<div class="card" id="{p}-c"><div class="k">{e(d.get("k") or "")}</div><svg class="ring" viewBox="0 0 700 700">{circ}</svg><div class="legend">{leg}</div></div>'
    t0 = s.t0 + .4; th = s.w(d["at"])
    js = f'pop("#{p}-c",{s.t0});' + "".join(f'tl.fromTo("#{p}-s{i}",{{opacity:0}},{{opacity:1,duration:.35}},{t0 + i * .3:.2f});tl.fromTo("#{p}-l{i}",{{opacity:0,x:-10}},{{opacity:1,x:0,duration:.3}},{t0 + i * .3:.2f});' for i in range(len(segs)))
    js += f'tl.fromTo("#{p}-s{d["hi"]}",{{scale:1}},{{scale:1.08,duration:.25,yoyo:true,repeat:1,transformOrigin:"center"}},{th:.2f});tl.to("#{p}-l{d["hi"]} b",{{color:"#9A7414",duration:.2}},{th:.2f});'
    return html, js, [round(th, 2)]

def rollnum(p, s, d):
    """첫 장면 E: hooknum 과 같되 큰 숫자가 0.7초 동안 자릿수별로 돌아 멈춘다 (N2 를 첫 장면에)."""
    spans, kj = _karaoke(p, s, d["line"].split(), "w")
    ph, pj = _promise(p, s, d, len(d["line"].split()))
    sh, sj = ostamp(p, s, d, 840)
    num = d["num"]; cols = ""
    for i, ch in enumerate(num):
        if ch.isdigit(): cols += f'<span class="dg"><i id="{p}-d{i}">' + "".join(f'<b>{k}</b>' for k in range(10)) + '</i></span>'
        else: cols += f'<span class="sep">{e(ch)}</span>'
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div><div class="num od{negc(num, d)}"{numst(num)}>{cols}</div><div class="ul" id="{p}-ul"></div>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    nd = sum(ch.isdigit() for ch in num); k = 0; js = ""
    for i, ch in enumerate(num):
        if not ch.isdigit(): continue
        js += f'tl.fromTo("#{p}-d{i}",{{yPercent:{-((int(ch) + 7) % 10) * 10}}},{{yPercent:{-int(ch) * 10},duration:{.35 + (nd - 1 - k) * .12:.2f},ease:"power3.out"}},0);'; k += 1
    js += (f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.15);'
           f'tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + kj + pj)
    return html, js + sj

# ── 3단계 3라운드 (11/07): 첫 장면 5종 — rise(T4 마스크 상승) · cover(K2 잡지 표지) · boil(K3 선 떨림) · glass(K4 유리 글자) · window(K5 당겨 나오는 창) ──
def _opener_bits(p, s, d, base=840):
    """첫 장면 공통: 훅 줄 카라오케 · 약속 줄 · 도장. (spans, kj, ph, pj, sh, sj)"""
    spans, kj = _karaoke(p, s, d["line"].split(), "w")
    ph, pj = _promise(p, s, d, len(d["line"].split()))
    sh, sj = ostamp(p, s, d, base)
    return spans, kj, ph, pj, sh, sj

def _key(subj, n):
    """긴 대상 이름은 핵심 낱말 하나 (YOUR BMO NOTE → BMO, YOUR ADVISOR'S FUND → ADVISOR'S). 없으면 HAMA. cover 마스트헤드·glass 유리 글자가 쓴다 (11/07)."""
    g = subj or "HAMA"
    if len(g) > n: g = next((w for w in g.split() if w not in ("YOUR", "THE", "MY", "A", "AN", "OUR", "VS")), g.split()[0])
    return g

def rise(p, s, d):
    """첫 장면 F (T4): 숫자·훅 단어가 클립 마스크 아래에서 솟는다. 0초엔 알약·이름이 있고 0.45초면 다 서 있다."""
    spans, kj = _karaoke(p, s, d["line"].split(), "w", wrap=True)
    ph, pj = _promise(p, s, d, len(d["line"].split()))
    sh, sj = ostamp(p, s, d, 840)
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div>'
            f'<div class="mask"{numst(d["num"])}><div class="num{negc(d["num"], d)}" id="{p}-n" style="font-size:inherit">{e(d["num"])}</div></div>'
            f'<div class="ul" id="{p}-ul"></div><div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    n = len(d["line"].split())
    js = (f'tl.fromTo("#{p}-n",{{yPercent:105}},{{yPercent:0,duration:.5,ease:"expo.out"}},0);'
          f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.25);'
          + "".join(f'tl.fromTo("#{p}-w{i}",{{yPercent:110}},{{yPercent:0,duration:.4,ease:"power3.out"}},{.12 + i * .04:.2f});' for i in range(n))
          + f'tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + kj + pj)
    return html, js + sj

def cover(p, s, d):
    """첫 장면 G (K2): 잡지 표지. 마스트헤드 = 대상 이름(없으면 HAMA), 하마 얼굴이 마스트헤드 아래를 가리고, 숫자는 커버라인."""
    spans, kj, ph, pj, sh, sj = _opener_bits(p, s, d)
    head = _key(d.get("subj"), 9)
    sh, sj = ostamp(p, s, d, 840, top=240)   # 카드 위 오른쪽 모서리 (얼굴·숫자를 가리지 않게, 11/07)
    html = (f'<div class="mag" id="{p}-m"><div class="head" id="{p}-h"{fit(head, 190, 760)}>{e(head)}</div>'
            f'<div class="kick">{e(d["pill"])}</div><div class="oav face big" id="{p}-av"></div>'
            f'<div class="num{negc(d["num"], d)}" id="{p}-n"{fit(d["num"], 150, 520)}>{e(d["num"])}</div>'
            f'<div class="bar"></div></div>' + sh +
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}')
    js = (f'tl.fromTo("#{p}-m",{{scale:.94,y:24}},{{scale:1,y:0,duration:.55,ease:"expo.out"}},0);'
          f'tl.fromTo("#{p}-h",{{y:30,opacity:.5}},{{y:0,opacity:1,duration:.45,ease:"power3.out"}},.05);'
          f'tl.fromTo("#{p}-av",{{y:60}},{{y:0,duration:.6,ease:"power3.out"}},.1);'
          f'tl.fromTo("#{p}-n",{{scale:1.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power4.in"}},.2);' + kj + pj)
    return html, js + sj, [.5]

def _rough(x, y, w, h, seed, amp=7, step=36):
    """손그림 사각형 점 목록 (시드 고정, 떨림 변형용)."""
    import random; r = random.Random(seed); pts = []
    for ax, ay, bx, by in ((x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)):
        n = max(2, int(((bx - ax) ** 2 + (by - ay) ** 2) ** .5 / step))
        for k in range(n): t = k / n; pts.append((ax + (bx - ax) * t + r.uniform(-amp, amp), ay + (by - ay) * t + r.uniform(-amp, amp)))
    return "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + " Z"

def boil(p, s, d):
    """첫 장면 H (K3): hooknum 그대로 + 숫자와 얼굴 둘레에 손그림 선이 부들부들 떨린다 (sketch boil, 3벌을 0.1초씩 돌린다)."""
    spans, kj, ph, pj, sh, sj = _opener_bits(p, s, d)
    npx_ = numpx(d["num"]); nw = min(960, int(len(d["num"]) * npx_ * .62) + 80); top = 840 - npx_
    av_top = 1290 if d.get("promise") else 1130
    paths = "".join(f'<path id="{p}-r{k}" d="{_rough(540 - nw // 2, top - 10, nw, npx_ + 10, k + len(d["num"]))}"/><path id="{p}-c{k}" d="{_rough(440, av_top - 10, 200, 200, 10 + k, 5, 22)}"/>' for k in range(3))
    html = (subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div><div class="num{negc(d["num"], d)}"{numst(d["num"])}>{e(d["num"])}</div><div class="ul" id="{p}-ul"></div>'
            f'<svg class="sk" viewBox="0 0 1080 1920">{paths}</svg>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    js = f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.15);tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);'
    t = 0.0; k = 0
    while t < s.t1 - s.t0:   # 떨림: 0.1초마다 다음 벌
        js += f'tl.set(["#{p}-r{k % 3}","#{p}-c{k % 3}"],{{opacity:1}},{t:.2f});tl.set(["#{p}-r{(k + 2) % 3}","#{p}-c{(k + 2) % 3}"],{{opacity:0}},{t:.2f});'
        t += .1; k += 1
    return html, js + kj + pj + sj

def glass(p, s, d):
    """첫 장면 I (K4): 대상 이름이 유리 글자로 뒤에 크게, 앞에 숫자와 얼굴. 유리는 느리게 흐른다."""
    spans, kj, ph, pj, sh, sj = _opener_bits(p, s, d)
    g = _key(d.get("subj"), 8)
    html = (f'<div class="gl" id="{p}-g"{fit(g, 360, 1400)}>{e(g)}</div>' + subj(d) + sh + f'<div class="opill"><i></i>{e(d["pill"])}</div>'
            f'<div class="num{negc(d["num"], d)}" id="{p}-n"{numst(d["num"])}>{e(d["num"])}</div><div class="ul" id="{p}-ul"></div>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div>')
    js = (f'tl.fromTo("#{p}-g",{{x:-40,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power2.out"}},0);tl.to("#{p}-g",{{x:40,duration:{max(1.0, s.t1 - s.t0):.2f},ease:"none"}},.5);'
          f'tl.fromTo("#{p}-n",{{scale:1.15}},{{scale:1,duration:.4,ease:"power3.out"}},0);'
          f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.15);tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},0);' + kj + pj)
    return html, js + sj

def window(p, s, d):
    """첫 장면 J (K5): 데스크톱 창이 오른쪽에서 당겨져 나온다. 창 제목 = 물건, 안에 숫자·훅·얼굴."""
    spans, kj, ph, pj, sh, sj = _opener_bits(p, s, d)
    sh, sj = ostamp(p, s, d, 840, top=330)
    html = (f'<div class="win" id="{p}-w"><div class="tb"><i></i><i></i><i></i><span>{e(d["pill"])}</span></div>'
            + (f'<div class="wsubj"{fit(d["subj"], 60, 760)}>{e(d["subj"])}</div>' if d.get("subj") else "")
            + f'<div class="num{negc(d["num"], d)}" id="{p}-n"{fit(d["num"], 220, 760)}>{e(d["num"])}</div><div class="ul" id="{p}-ul"></div>'
            f'<div class="oline"{ols(d["line"])}>{spans}</div>{ph}<div class="oav face" id="{p}-av"></div><div class="tab" id="{p}-t"></div></div>' + sh)
    js = (f'tl.fromTo("#{p}-w",{{x:300,scale:.86,rotation:2}},{{x:0,scale:1,rotation:0,duration:.55,ease:"expo.out"}},0);'
          f'tl.to("#{p}-t",{{opacity:0,duration:.2}},.5);'
          f'tl.fromTo("#{p}-ul",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"expo.out"}},.3);tl.fromTo("#{p}-av",{{y:40}},{{y:0,duration:.6,ease:"power3.out"}},.1);' + kj + pj)
    return html, js + sj, [.45]

def callout(p, s, d):
    """T9/T10 (11/07 v2.1): 데이터 없는 rehook 한 줄이 통째로 세리프 이탤릭 카드로 쾅, 별표 낱말만 골드. 자막만인 장면을 없앤다."""
    words = d["line"].split(); star = re.search(r"\*([^*]+)\*", d["line"])
    inner = " ".join(f'<b>{e(w.strip("*"))}</b>' if w.startswith("*") or w.endswith("*") else e(w) for w in words)
    html = (f'<div class="card word" id="{p}-w"{fit(d["line"].replace("*", ""), 92, 820)}>{inner}</div><div class="oav face small" id="{p}-av"></div>')
    t = s.t0 + .15
    js = (f'tl.fromTo("#{p}-w",{{opacity:0,scale:1.4,rotation:-4}},{{opacity:1,scale:1,rotation:-1.5,duration:.32,ease:"power4.in"}},{t:.2f});'
          f'tl.fromTo("#{p}-av",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"power3.out"}},{t + .25:.2f});')
    if star: js += f'tl.fromTo("#{p}-w b",{{color:"#16140F"}},{{color:"#9A7414",duration:.2}},{s.w(d["at"]):.2f});'
    return html, js, [round(t + .3, 2)]

from charts import dumbbell, waterfall   # 차트 층 (11/07): 두 값+차이 → 덤벨 · 시작−단계=끝 → 폭포

# 셋째 값을 돌려주는 부품은 그 시각에 틱 소리가 난다
PARTS = dict(hook=hook, checkout=checkout, amount=amount, toggle=toggle, counter=counter,
             split=split, checklist=checklist, compare=compare, tiles=tiles,
             coins=coins, receipt=receipt, swap=swap, stack=stack,
             hooknum=hooknum, title2=title2, slam=slam, tease=tease, stamp=stamp, strike=strike, chart=chart,
             table=table, wipe=wipe, odometer=odometer,
             multiply=multiply, shrink=shrink, funnel=funnel, clock=clock, countdown=countdown, notify=notify, donut=donut, rollnum=rollnum,
             rise=rise, cover=cover, boil=boil, glass=glass, window=window,
             callout=callout, dumbbell=dumbbell, waterfall=waterfall)
