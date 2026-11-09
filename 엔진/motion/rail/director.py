#!/usr/bin/env python3
"""레일 릴스 감독: post.json → 대본(claude -p, prompts/rail.md) → 장면마다 부품·전환 매핑 → rail{} → build_rail.
  python3 엔진/build.py <post.json> --direct [--dry] [--force] [--render]
  python3 엔진/motion/rail/director.py --stats          # 47편 분포 표 (꼴·끝맺음·첫 장면·부품·전환) + 관문
대본은 모델이 쓰고(역할만 고른다), 모션은 여기 규칙이 고른다. 규칙은 REF/fx-목록.md «지루하지 않게».
2단계 (11/06): 대본은 kallaway 9칸 위에 선다 (hooks.json playbook.skeleton). 꼴 4(shapes) · 끝맺음 4(endings) · 첫 장면 4 · 역할마다 부품 3+ · 전환 6 을
  최근 6편과 겹치지 않게 least_used 로 고른다. 막는 건 금지 표현·지어낸 숫자뿐, 나머지는 경고 (11/04 «만드는 게 우선»).
  --dry   post.json 에 쓰지 않고 out/<편>-auto-rail/ 로만 뽑는다
  --force 이미 rail{} 이 있어도 새로 쓴다 (예전 것은 rail_prev, 그 전 것은 rail_prev2)
연출 원장: 엔진/motion-ledger.json — 최근 6편과 꼴·끝맺음·첫 장면·부품·전환이 겹치지 않게."""
import json, re, sys, pathlib, datetime
R = pathlib.Path(__file__).parent; ENG = R.parent.parent
sys.path.insert(0, str(R)); sys.path.insert(0, str(ENG))
import build_rail
from hook import ask_claude

PROMPT = re.sub(r"\A---\n.*?\n---\n", "", (ENG / "prompts" / "rail.md").read_text(encoding="utf-8"), flags=re.S)   # 머리표는 떼고 보낸다
LEDGER = ENG / "motion-ledger.json"
BANNED = ["—", ";", "→", "here's why", "here is why", "the secret", "guaranteed", "buy this"]

# 역할 → 부품 후보 3개 이상 (11/06 레드팀 발견 13). 같은 데이터 꼴을 받는 부품끼리 묶는다. 새 부품이 생기면 여기에 한 줄 더한다
import hook as _hk0
G = _hk0.HK.get("grammar") or {}   # 감독 상수 한 소스 = hooks.json grammar (11/07 v2.1). 여기엔 기본값만
GRAMMAR = G.get("roles") or {"myth": ["strike", "wipe", "swap"], "catch": ["stamp", "stack", "strike"], "loss": ["shrink", "odometer", "stamp"], "rehook": ["swap", "wipe", "split"], "rehook_nodata": ["callout"],
                              "closing": ["odometer", "stamp"], "flow": ["receipt", "checkout", "amount", "funnel", "notify", "shrink"], "compare": ["wipe", "stack", "compare", "split", "donut", "table"],
                              "myrow": ["table", "wipe", "compare", "donut", "split"], "grow": ["coins", "counter", "odometer", "multiply", "clock", "split"], "step": ["toggle", "countdown", "swap", "stamp"], "check": ["checklist"], "cta": ["tiles"]}
TEXT_SWAP = G.get("text_swap", ["stamp", "swap", "strike"]); TEXT_SWAP_CAP = G.get("text_swap_cap", 2)
HEAVY_PARTS = G.get("heavy_parts", ["stack"]); HEAVY_MAX = G.get("heavy_max", 3)
CHART_LINES = G.get("chart_lines", r"zoom out|\bfell\b|dropped|crash|sits below|below (?:its|the) ")
CAPTIONS = ["blur", "karaoke"]   # T2 카라오케 자막 (build_rail 이 그린다). 편마다 교대
TEXT_ROLES = ("opener", "lockin")                      # 부품 없이 앞 장면을 잇는 역할 (자막만)
OPENERS = ["hooknum", "title2", "slam", "tease", "rollnum", "rise", "cover", "boil", "glass", "window"]   # 11/07 3라운드: rise(T4)·cover(K2)·boil(K3)·glass(K4)·window(K5)   # rollnum = 숫자가 돌아 멈추는 첫 장면 (11/06)
TRANS = ["pan", "dissolve", "fade", "zoom", "wipe", "iris"]
REACT_MIN = G.get("react_min", .6)   # «줄 반응» 기준 (hooks.json grammar)
STILL_MAX = G.get("still_max", 5.0)   # «정지» 기준 (hooks.json grammar)
RANGE_ORDER = ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]   # chart.py 창 길이 순 (줌아웃 짝 고르기, 11/07)   # 전환 6종 (build_rail 이 그린다)

def recent(n=6):   # 하루에 여러 편 만들 때도 겹치지 않게 (11/04 밤 6편 중 6편이 strike)
    import fcntl, time
    for k in range(5):   # 나란히 만들 때 다른 워커가 쓰는 중이면 반만 읽힌다 (11/07 밤 2008-crash JSONDecodeError) → 잠금 잡고, 깨지면 잠깐 뒤 다시
        try:
            with open(LEDGER.with_suffix(".lock"), "w") as lk:
                fcntl.flock(lk, fcntl.LOCK_SH); rows = json.load(open(LEDGER)) if LEDGER.exists() else []
            return rows[-n:]
        except json.JSONDecodeError:
            if k == 4: raise
            time.sleep(.3)

SALT = ""   # 편 이름. 동률일 때 편마다 다르게 고른다 (11/06: 3편 나란히 만들면 같은 원장을 읽어 셋이 같은 꼴을 골랐다)
def least_used(cands, used, avoid=()):
    """후보 중 최근에 덜 쓴 것. 동률이면 편 이름 해시로 (나란히 만들어도 안 겹치게). avoid 는 바로 앞 편 것 (연속 금지)."""
    import hashlib
    pool = [c for c in cands if c not in avoid] or cands
    return min(pool, key=lambda c: (used.count(c), hashlib.sha1((SALT + c).encode()).hexdigest()))

def anchor(lines, value, default=None):
    """value 가 들리는 단어. 못 찾으면 줄 번호(정수, build_rail 이 그 줄 첫 단어로 바꾼다)."""
    key = value.strip("*.,!?$").lower()
    for ln in lines:
        for t in ln.split():
            if t.strip("*.,!?$").lower() == key: return value
    return min(default if default is not None else len(lines) - 1, len(lines) - 1)

def kw(lines, i=0):
    """i번째 줄의 강조 단어(*별표*), 없으면 첫 단어."""
    ln = lines[min(i, len(lines) - 1)]
    m = re.search(r"\*([^*]+)\*", ln)
    return (m.group(1).split()[0] if m else ln.split()[0]).strip(".,!?")   # *starts over* 는 «starts» (11/06: 두 단어 별표로 Seg.w 가 죽었다)

def _ab(d):
    """a/b 데이터가 없는 역할(grow·rehook)을 compare 꼴로 (부품 후보 3개를 채우려고)."""
    fill = lambda x, tone: {"sub": "", "tone": tone, **{k: v for k, v in x.items() if v is not None}}   # 부품이 기대하는 키(h·v·sub·tone)를 항상 채운다 (11/07 KeyError 'sub')
    if "a" in d and "b" in d: return fill(d["a"], "loss"), fill(d["b"], "win")
    if "steps" in d:
        st = d["steps"]; return fill({"h": st[0]["label"], "v": st[0]["value"]}, "loss"), fill({"h": st[-1]["label"], "v": st[-1]["value"]}, "win")
    return fill({"h": d.get("old", ""), "v": d.get("old", "")}, "loss"), fill({"h": d.get("new", ""), "v": d.get("new", "")}, "win")

def _oldnew(d, sc):
    """old/new 가 없는 역할(step·데이터 없는 rehook)을 swap 꼴로."""
    if "old" in d and "new" in d: return d
    if "label" in d: return {"old": d["label"].upper(), "new": (d.get("sub") or "set it up").upper()[:18], **({"sub": d["sub"]} if d.get("sub") else {})}
    L = sc["lines"]; return {"old": kw(L, 0).upper(), "new": (L[-1].split()[-1] if L else "").strip(".,!?").upper()}

def data_for(part, sc, post):
    d, L = sc.get("data", {}), sc["lines"]
    if part == "chart":   # 단기+장기 짝이면 줌아웃. 그리기는 하락 % 를 말하는 줄에서, 줌은 «zoom» 을 말하는 줄에서 (11/06 하림님 «싱크 안 맞음»)
        zoom_at = next((i for i, ln in enumerate(L) if re.search(r"zoom|times your money|long run", ln, re.I)), None)
        short_at = next((i for i, ln in enumerate(L) if (zoom_at is None or i < zoom_at) and re.search(r"\d+(?:\.\d+)?%|\b(fell|dropped|down|crash|below|high|low)\b", ln, re.I)), 0)   # 11/07: 줌 줄보다 앞에서 그린다. 없으면 장면 첫 줄 (창이 비어 있지 않게)
        if not d.get("long"):
            out = {**d["chart"], "short_at": short_at}
            if d.get("second"):
                tk = re.sub(r"\..*$", "", d["second"].get("ticker", ""))
                out["second"] = d["second"]; out["second_at"] = next((i for i, ln in enumerate(L) if tk and re.search(r"\b" + re.escape(tk) + r"\b", ln)), min(short_at + 1, len(L) - 1))
            return out
        if zoom_at is None: zoom_at = min(short_at + 1, len(L) - 1)
        return {"chart": d["chart"], "long": d["long"], "at": zoom_at, "short_at": short_at}
    if part == "swap":
        d = _oldnew(d, sc)
        return {"old": d["old"], "new": d["new"], "at": kw(L, 0 if len(L) == 1 else 1) if not d.get("at") else d["at"],
                **({"sub": d["sub"], "sub_at": len(L) - 1} if d.get("sub") else {})}
    if part in ("stamp", "strike"):
        d = _oldnew(d, sc)
        return {"old": d["old"], "new": d["new"], "at": anchor(L, d["new"].split()[0], min(1, len(L) - 1)) if part == "stamp" else kw(L, min(1, len(L) - 1)), "k": sc.get("badge", ""),   # 순간은 둘째 줄까지 (11/06)
                **({"sub": d["sub"], "sub_at": len(L) - 1} if d.get("sub") else {})}
    if part == "receipt":
        rows = [[a, b, anchor(L, b, i)] for i, (a, b) in enumerate(d["rows"])]
        tn, tv = d["total"]
        return {"title": d["title"], "sub": d.get("sub", post.get("object", "").lower()), "rows": rows,
                "total": [tn, tv, anchor(L, tv)], "foot": " · ".join(s["label"].title() for s in post.get("sources", [])[:2])}
    if part == "stack":
        a, b = _ab(d)
        return {"layers": [{**a, "at": anchor(L, a["h"], 0)}, {**b, "at": anchor(L, b["h"], 1)}],
                "hi": 1 if d.get("win", "b") == "b" else 0, "hi_at": anchor(L, (b if d.get("win", "b") == "b" else a)["h"]),
                "stand_at": len(L) - 1}
    if part == "callout":   # T9/T10: 데이터 없는 rehook 의 별표 단어(없으면 마지막 낱말)가 큰 카드로
        w = kw(L, 0) if re.search(r"\*", L[0]) else L[0].rstrip(".,!?").split()[-1]
        return {"word": w, "line": L[0], "at": w}
    if part == "dumbbell": return data_for("compare", sc, post)
    if part == "waterfall":
        rr = data_for("receipt", sc, post); return {"title": rr["title"], "rows": rr["rows"], "total": rr["total"]}
    if part == "compare":
        a, b = _ab(d)
        out = {"a": {"k": a["h"], "big": a["v"], "ft": a.get("sub", "")},
               "b": {"k": b["h"], "big": b["v"], "ft": b.get("sub", ""), "at": anchor(L, b["v"], min(1, len(L) - 1))}}
        import hook as _hk; ft = _hk.felt(post)   # 11/07 하림님 «그래프가 뭘 말하는지 안 보여»: 장식 곡선 대신 두 금액 막대 + 차이 칩. 차이는 증명된 felt 만
        if ft and ft.get("a") and ft.get("b") and {_hk.nval(str(ft["a"])), _hk.nval(str(ft["b"]))} == {abs(_num(a["v"])), abs(_num(b["v"]))}:
            gs = _hk.felt_str(ft); out["gap"] = gs; out["gap_at"] = anchor(L, gs, len(L) - 1)
        return out
    if part in ("coins", "counter"):
        st = d["steps"]
        vals = [int(re.sub(r"[^\d]", "", x["value"]) or 0) for x in st]
        top = max(vals) or 1
        steps = [{"label": x["label"], "label_at": anchor(L, x["label"].split()[-1], i), "value": v,
                  "value_at": anchor(L, x["value"], i), "bar": round(v / top, 3),
                  **({} if x["value"].strip().lstrip("-+").startswith("$") else {"text": x["value"].strip()})} for i, (x, v) in enumerate(zip(st, vals))]   # 돈이 아닌 값은 글자 그대로
        v0 = st[0]["value"].strip()   # 값의 단위를 그대로 (11/05: «2 years» 가 «$2» 로 나오던 것)
        out = {"steps": steps, "ticks": ["0"] + [x["label"].split()[-1] for x in st],
               "pre": re.match(r"^[^\d]*", v0).group(0).replace("-", ""), "suf": re.search(r"[^\d,.]*$", v0).group(0)}
        if part == "coins": out["coins"] = [max(2, round(20 * v / top)) for v in vals]
        else: out["note"] = post.get("source_note", "").title()
        return out
    if part == "toggle":
        return {"k": sc.get("badge", ""), "label": d["label"], "sub": d.get("sub", ""), "on_at": kw(L), "app": "Hama Savings"}
    if part == "checklist":
        items = ["Start · your account"] + d["items"] + [sc.get("done", "Save this post")]
        return {"items": items, "from": 0, "to": len(L) - 1, "top": 420}
    if part == "tiles":
        return {"word": d["word"], "at": d["word"], "bar": "Add a comment…", "dm": ["Hama the Gold Digger", f"sent you {d['gift']} ✨"],
                "dm_at": "send", "disc": "General education, not financial advice."}
    if part == "checkout":     # flow 데이터(영수증과 같은 것)를 결제 화면으로
        rows = d["rows"]; tn, tv = d["total"]
        return {"title": d["title"], "tag": post.get("series", "").title() or "Secure", "icon": "🧾",
                "h": rows[0][0], "p": d.get("sub", post.get("object", "").lower()), "price": rows[0][1],
                "fields": [f"{a}   {b}" for a, b in rows[1:]], "btn": f"{tn}  {tv}", "seal": [tv, tn, anchor(L, tv)]}
    if part == "amount":       # flow 데이터를 앱 금액 선택 화면으로
        rows = d["rows"]; tn, tv = d["total"]; k = len(rows) - 1
        return {"app": d["title"].title(), "sub": d.get("sub", ""), "options": [b for _, b in rows],
                "pick": k, "pick_at": anchor(L, rows[k][1], 1), "big": tv, "big_sub": tn}
    if part == "split":        # compare 데이터(a/b)를 막대 쪼개기로
        a, b = _ab(d)
        va, vb = (int(re.sub(r"[^\d]", "", x["v"]) or 0) for x in (a, b))
        return {"k": f"{a['h']} vs {b['h']}", "total": b["v"] if vb >= va else a["v"],
                "a": {"v": a["v"], "l": a["h"], "w": max(.12, min(.88, va / ((va + vb) or 1))), "at": anchor(L, a["v"], 0)},
                "b": {"v": b["v"], "l": b["h"], "at": anchor(L, b["v"], 1), "label_at": anchor(L, b["v"], 1)}}
    if part == "wipe":         # D11: a 손해 판 → b 이득 판
        a, b = _ab(d)
        return {"a": {"h": a["h"], "v": a["v"], "sub": a.get("sub", "")}, "b": {"h": b["h"], "v": b["v"], "sub": b.get("sub", "")}, "at": anchor(L, b["v"], min(1, len(L) - 1))}
    if part == "table":        # H4: 편의 조회표(grid·table 장) 행 4개 + 내 행. 없으면 a/b 로 한 줄짜리
        sl = next((x for x in post.get("slides", []) if x.get("type") in ("grid", "table")), None)
        if sl and sl["type"] == "grid":
            rows = [{"lab": r["a"], "cells": [str(c) for c in r["cells"]]} for r in sl["rows"][:4]]; cols = [str(c) for c in sl["cols"]]
            hi = (sl.get("hi") or [0])[0] if isinstance(sl.get("hi"), list) else 0
        elif sl:
            rows = [{"lab": r["a"], "cells": [r["b"]] + ([r["c"]] if r.get("c") else [])} for r in sl["rows"][:4]]; cols = [c for c in (sl.get("h2"), sl.get("h3")) if c]
            hi = 0
        else:
            a, b = _ab(d); cols = [a["h"], b["h"]]; rows = [{"lab": "YOU", "cells": [a["v"], b["v"]]}]; hi = 0
        hi = min(hi, len(rows) - 1)
        return {"k": sc.get("badge") or post.get("object", ""), "cols": cols, "rows": rows, "hi": hi, "at": anchor(L, rows[hi]["cells"][-1], len(L) - 1)}
    if part == "odometer":     # N2: 0 → felt $ (loss·closing) 또는 첫 값 → 끝 값 (grow)
        import hook as _hk
        if "steps" in d:
            v0, v1 = d["steps"][0]["value"], d["steps"][-1]["value"]; lab = d["steps"][-1]["label"]
        else:
            dd = _oldnew(d, sc); ft = _hk.felt(post)
            v1 = next((m for m in re.findall(r"\$\d[\d,]*(?:\.\d+)?", dd.get("old", "") + " " + dd.get("new", "") + " " + " ".join(L))), _hk.felt_str(ft) if ft else "$0")
            v0 = "$0"; lab = dd.get("new", "") if not dd.get("new", "").startswith("$") else dd.get("old", "")
        digits = lambda v: re.sub(r"[^\d,.]", "", str(v))
        return {"from": digits(v0).replace(",", ""), "to": digits(v1), "pre": "$" if "$" in str(v1) else "", "suf": "%" if "%" in str(v1) else "", "label": lab, "at": anchor(L, v1, len(L) - 1)}
    if part == "multiply":     # D14: grow steps → 칸 수(≤16) 비례
        st = d["steps"]; vals = [int(re.sub(r"[^\d]", "", x["value"]) or 0) for x in st]; top = max(vals) or 1
        v0 = st[0]["value"].strip()
        return {"steps": [{"label": x["label"], "value": re.sub(r"^[^\d]*|[^\d,.]*$", "", x["value"]), "n": max(1, round(16 * v / top)), "at": anchor(L, x["value"], i)} for i, (x, v) in enumerate(zip(st, vals))],
                "pre": re.match(r"^[^\d]*", v0).group(0).replace("-", ""), "suf": re.search(r"[^\d,.]*$", v0).group(0)}
    if part == "shrink":       # N6: flow rows(넣은 돈 → 깎인 뒤) 또는 old/new 두 막대
        if "rows" in d:
            vals = [(a, b) for a, b in d["rows"]] + [tuple(d["total"])]
        else:
            dd = _oldnew(d, sc); vals = [(dd["old"], dd["old"]), (dd["new"], dd["new"])]
        nums = [abs(_num(v)) for _, v in vals]; top = max([n for n in nums if n] or [1])
        return {"k": sc.get("badge", ""), "bars": [{"l": l, "v": v, "w": (abs(_num(v)) / top if _num(v) else .2), "at": anchor(L, v, i)} for i, ((l, v), _) in enumerate(zip(vals, nums))]}
    if part == "funnel":       # P4: flow rows → in · leak · out
        rows = d["rows"]; tn, tv = d["total"]
        leak = next((b for a, b in rows[1:] if b.strip().startswith(("-", "−"))), rows[-1][1] if len(rows) > 1 else "")
        return {"in": rows[0][1], "leak": leak, "out": tv, "label": tn.lower(), "in_at": anchor(L, rows[0][1], 0), "leak_at": anchor(L, leak, min(1, len(L) - 1)), "out_at": anchor(L, tv, len(L) - 1)}
    if part == "clock":        # N4: grow steps 의 마지막 값/라벨 (연수) 또는 숫자 하나
        st = d.get("steps") or []
        if st:
            yrs = [int(re.sub(r"[^\d]", "", x["label"]) or 0) for x in st]; total = max(yrs) or 1
            return {"total": total, "filled": total, "unit": "years", "label": st[-1]["value"], "at": anchor(L, st[-1]["value"], len(L) - 1)}
        dd = _oldnew(d, sc); n = _num(dd.get("old", "")) or 1
        return {"total": n, "filled": n, "unit": dd.get("new", ""), "label": sc.get("badge", ""), "at": kw(L, len(L) - 1)}
    if part == "countdown":    # U13: 줄에서 날짜(April 30 · Dec 31 · March 1) 를 찾는다. 없으면 label
        m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}\b", " ".join(L))
        date = m.group(0) if m else d.get("sub") or d.get("label", "")
        return {"label": (d.get("label") or sc.get("badge") or "deadline").upper()[:18], "date": date, "at": anchor(L, date.split()[-1], len(L) - 1) if m else kw(L, len(L) - 1)}
    if part == "notify":       # U9: flow rows → 알림, total → 배지
        rows = d["rows"]; tn, tv = d["total"]
        return {"items": [{"app": a, "v": b, "at": anchor(L, b, i)} for i, (a, b) in enumerate(rows)], "total": tv, "total_at": anchor(L, tv, len(L) - 1)}
    if part == "donut":        # N8: a/b 비율 (이득 조각이 hi)
        a, b = _ab(d); va, vb = abs(_num(a["v"])), abs(_num(b["v"])); tot = (va + vb) or 1
        hi = 1 if d.get("win", "b") == "b" else 0
        return {"k": sc.get("badge", ""), "segs": [{"l": a["h"], "v": a["v"], "w": va / tot}, {"l": b["h"], "v": b["v"], "w": vb / tot}], "hi": hi, "at": anchor(L, (b if hi else a)["v"], len(L) - 1)}
    # ── 4라운드 (11/07 v2, claude-37): fan(D5) · hub(U7) · paid(U10) · tabs(U2) · tag(T9) · tail(T10) · badge(U14). 지금 대본의 데이터 꼴(items · label/sub · old/new)만 받는다 ──
    if part == "fan":          # D5: check 항목 = checklist 와 같은 목록 (≤5)
        items = ["Start · your account"] + list(d["items"]) + [sc.get("done", "Save this post")]
        return {"items": items[:5], "k": sc.get("badge") or post.get("object", ""), "from": 0, "to": len(L) - 1}
    if part == "hub":          # U7: 항목만 허브 둘레에 (2~4개)
        return {"items": list(d["items"])[:4], "k": sc.get("badge") or post.get("object", ""), "from": 0, "to": len(L) - 1}
    if part == "paid":         # U10: step {label, sub} + 줄의 첫 $ 금액이 영수증 줄로
        amt = next(iter(re.findall(r"\$\d[\d,]*(?:\.\d+)?", " ".join(L))), None)
        return {"k": sc.get("badge", ""), "label": d.get("label") or kw(L, 0).title(), "sub": d.get("sub", ""), "at": kw(L, min(1, len(L) - 1)), **({"amt": amt} if amt else {})}
    if part in ("tabs", "tag", "badge"):   # U2 · T9 · U14: old → new 뒤집기. 순간은 new 의 첫 낱말, 둘째 줄까지
        dd = _oldnew(d, sc)
        out = {"old": dd["old"], "new": dd["new"], "at": anchor(L, dd["new"].split()[0], min(1, len(L) - 1)), **({"sub": dd["sub"], "sub_at": len(L) - 1} if dd.get("sub") else {})}
        if part != "tag": out["k"] = sc.get("badge") or (post.get("object", "") if part == "badge" else "")
        return out
    if part == "tail":         # T10: 큰 글 = $·% 가 든 쪽(없으면 new), 꼬리 = 나머지(또는 sub). 조건: old/new 에 돈·% 가 있을 때만 (cands 에서 거른다)
        dd = _oldnew(d, sc); money = lambda x: bool(re.search(r"[$]\s?\d|\d\s?%", str(x)))
        if money(dd["old"]) and money(dd["new"]): big_old = abs(_num(dd["old"])) >= abs(_num(dd["new"]))   # 둘 다 돈이면 큰 쪽이 큰 글 (손해 −$150 vs $0 back → −$150)
        else: big_old = money(dd["old"]) and not money(dd["new"])
        big, tl_ = (dd["old"], dd.get("sub") or dd["new"]) if big_old else (dd["new"], dd.get("sub") or dd["old"])
        return {"k": sc.get("badge", ""), "big": big, "tail": tl_.lower() if tl_.isupper() else tl_, "at": anchor(L, big, len(L) - 1)}
    raise SystemExit(f"감독: {part} 데이터 짜는 법이 없다")

def _reconciles(dd):
    """영수증 데이터가 폭포 꼴인가: rows[0] 시작액, rows[1:] 부호 있는 단계, total 끝액. 시작 + Σ단계 = 끝 (1% 안)."""
    rows, tot = dd.get("rows") or [], dd.get("total")
    if len(rows) < 2 or not tot or not all(re.search(r"\$\d", str(x[1])) for x in rows) or not re.search(r"\$\d", str(tot[1])): return False
    start = abs(_num(rows[0][1])); run = start
    for _, v in rows[1:]: n = _num(v); run += -abs(n) if re.search(r"[-−]", str(v)) else n
    return abs(run - abs(_num(tot[1]))) <= max(1, abs(_num(tot[1])) * .01)

def _num(v):
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v).replace("−", "-"))
    return float(m.group(0).replace(",", "")) if m else 0.0

def opener_data(part, post, hk):
    f = post["fact"]; n = f"{int(f['num']):,}" if str(f["num"]).isdigit() else f["num"]   # 2372 → 2,372
    num = (f["unit"] + n) if f.get("unit") == "$" else (n + f.get("unit", ""))
    line = hk["on_screen"]; prom = hk.get("promise", "")
    import hook as _hk; subj = _hk.subject(post)
    bare = re.sub(re.escape(re.sub(r"^the ", "", subj, flags=re.I)), " ", line, flags=re.I) if subj else line   # «S&P 500» 의 500 은 숫자가 아니다
    hn = re.search(r"[-−]?\$\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s?(?:million|billion|M|B|k))?|[-−]?\d{1,3}(?:,\d{3})*(?:\.\d+)?%", bare) or re.search(r"[-−]?\d{1,3}(?:,\d{3})*(?:\.\d+)?", bare)
    if hn: num = hn.group(0)   # 큰 숫자 = 화면 훅의 숫자 (11/05). 꼬리 쉼표는 안 잡는다 (11/06 «$1,000,»)
    ft = _hk.felt(post)
    if ft:   # 큰 숫자 = 느끼는 숫자 (11/06). 훅에 $10,000 과 $1,483 이 같이 있으면 $1,483 이 주인공
        fs = _hk.felt_str(ft); m = re.search(re.escape(fs) + r"(?!\d)", line)
        if m: num = fs; hn = m
    subj_d = {"subj": re.sub(r"^the ", "", subj, flags=re.I).upper()} if subj else {}   # 숫자 위 큰 이름 한 줄 (SOXL / BITCOIN)
    if re.search(r"\b(fell|dropped|down|crashed|lost|below|sank)\b", line, re.I) and "%" in num: subj_d["drop"] = True   # 하락 % = 로즈, 부호 없어도. 달러 원금은 아니다
    pill = post.get("object", "").upper()
    st = hk.get("stamp") or stamp_word(line)   # 도장 = 포모 명령 (hooks.stamp). 없으면 훅의 손해 동사
    if st: subj_d["stamp"] = st   # 11/06 하림님 «한 장에 뭘 이야기하는지»
    if part == "title2":
        parts = re.split(r"(?<=[.,?])\s+", line, maxsplit=1)
        # 첫 줄이 96px 한 줄(18자쯤)을 넘으면 둘째 줄과 겹친다 → hooknum 으로 (11/04 코인 편)
        if len(parts) < 2 or len(parts[0]) > 26: part = "hooknum"   # 11/06: 18 → 26, parts.title2 가 글자를 줄인다
        else:
            l1 = (parts[0].replace(hn.group(0), "") if hn else parts[0].replace(f["num"] + f.get("unit", ""), "").replace("$" + f["num"], "")).strip()
            if subj: l1 = re.sub(re.escape(subj), "", l1, flags=re.I)
            l1 = re.sub(r"\s+([.,:?!])", r"\1", l1).strip(" :.,")
            if len(l1.split()) <= 2: return "hooknum", {"pill": pill, "num": num, "line": line, "promise": prom, **subj_d}   # 11/05 «SOXX.» 찌꺼기 줄
            return part, {"pill": pill, "num": num, "l1": l1, "l2": parts[1], "promise": prom, **subj_d}
    return part, {"pill": pill, "num": num, "line": line, "promise": prom, **subj_d}   # hooknum·slam 은 같은 data (title2 탈락도 여기로)

STAMP_PHRASES = ["want it back", "still waiting", "want the mix", "want yours", "want the gains", "don't miss"]
def stamp_word(line):
    """첫 장면 도장 글자(hooks.stamp 가 없을 때): 훅의 첫 손해 말(hooks.json cover.fomo_words) 없으면 욕망 구(want it back). 없으면 None."""
    import hook as _hk
    low = line.lower()
    for ph in STAMP_PHRASES:
        if ph in low and not any(re.search(r"(?<!\w)" + re.escape(f) + r"(?!\w)", low) for f in _hk.CF["fomo_words"]): return ph.upper()
    for w in re.findall(r"[a-z']+", low):
        if w in _hk.CF["fomo_words"] and w not in ("never", "every", "first", "late", "wrong", "less"): return w.upper()
    for ph in STAMP_PHRASES:
        if ph in low: return ph.upper()
    return None

def pick_opener(cands, used, post, hk):
    """덜 쓴 첫 장면부터 해 보고, 그 틀이 이 훅에 안 맞아 다른 틀로 떨어지면 다음 후보로 (11/05: title2 → hooknum 낙하로 12편 중 10편이 hooknum).
    slam(로즈 쾅)은 손해 훅에만: 훅에 fell/lose/gone/cut/miss 류가 없으면 뺀다 (11/05 «VFV beat VSP by $396»)."""
    loss = re.search(r"\b(fell|fall|drop|dropped|down|crash|lose|loses|lost|gone|missing|miss|missed|cut|cuts|leak|leaks|cost|costs|takes|took|pay|pays|paid|late|penalty|never)\b", hk.get("on_screen", ""), re.I)
    if not loss: cands = [c for c in cands if c != "slam"] or cands
    for c in sorted(cands, key=lambda c: (used.count(c), cands.index(c))):
        part, data = opener_data(c, post, hk)
        if part == c: return part, data
    return opener_data(cands[0], post, hk)

GAP_SHAPES = ["ledger", "zoom"]   # 차이($a−$b) 편은 body 1 이 compare 인 꼴만 (11/06 하림님 «왜 71,000 잃은 건데?»)
def pick_shape(pb, rec, gap=False):
    """꼴: 최근 6편에서 덜 쓴 것, 바로 앞 편과 다르게. 차이 편은 두 금액을 먼저 보여주는 꼴만."""
    names = [k for k in pb["shapes"] if k != "_" and (not gap or k in GAP_SHAPES)]
    used = [r.get("shape") for r in rec]
    return least_used(names, used, avoid=used[-1:])

def pick_ending(pb, shape, rec):
    names = [k for k in pb["endings"] if k != "_"]
    used = [r.get("ending") for r in rec]
    pref = pb["shapes"][shape].get("ending_pref")
    cands = ([pref] if pref in names else []) + [n for n in names if n != pref]
    return least_used(cands, used, avoid=used[-1:])

def what_ok(scenes, post):
    """몸통1 첫 줄이 plain.what 첫 문장의 낱말을 둘 이상 쓰나 (11/07 v2.1 칸 검사). direct 의 다시 쓰기와 review 경고가 같이 쓴다."""
    body1 = next((sc for sc in scenes if sc.get("role") not in ("opener", "lockin", "rehook")), None)
    what = ((post.get("plain") or {}).get("what") or "").split(".")[0]
    if not (body1 and body1.get("lines") and what): return True
    STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "is", "are", "that", "this", "with", "for", "its", "it", "one", "two", "at", "by", "from", "many", "your", "you"}
    W = lambda t: {w.strip(".,:;!?*").lower() for w in t.split() if len(w.strip(".,:;!?*")) > 3 and w.strip(".,:;!?*").lower() not in STOP}
    return len(W(body1["lines"][0]) & W(what)) >= min(2, len(W(what)))   # «BMO is a bank» 처럼 낱말이 하나뿐인 문장은 하나만

def direct(post, stem, reuse=False):
    global SALT; SALT = stem
    hk = post.get("hooks") or {}
    if not hk.get("spoken"): raise SystemExit("감독: hooks.spoken 이 없다. 먼저 python3 엔진/hook.py --make <post.json>")
    if not hk.get("promise"): raise SystemExit("감독: hooks.promise 가 없다. 먼저 python3 엔진/hook.py --make <post.json>")
    mode = hk.get("modes", ["숫자"])[hk.get("candidates", [hk.get("on_screen")]).index(hk["on_screen"])] if hk.get("on_screen") in hk.get("candidates", []) else "숫자"
    import hook as _hk
    pb = _hk.HK.get("playbook", {}); rec = recent()
    wins0 = [c for s_ in post.get("slides", []) if s_.get("type") == "chart" for c in s_.get("charts", [])]
    miss = [k for k, ok in (("plain", bool((post.get("plain") or {}).get("what"))), ("subject", bool(_hk.subject(post))), ("why", bool(post.get("why")) or not wins0), ("object", bool(post.get("object")))) if not ok]
    if miss: print(f"  ~ 입력 계약: {', '.join(miss)} 없음 — 경고, 기본값으로 간다 (11/07 v2.1 관문0: FAIL 은 넷뿐)")   # plain·felt 는 hook.rebuild 가 먼저 채운다
    post.setdefault("object", "the table")
    ft = _hk.felt(post); gap = bool(ft and ft.get("a") and ft.get("b"))
    m0 = (post.get("rail") or {}).get("made_by") or {}
    shape = m0["shape"] if reuse and m0.get("shape") else pick_shape(pb, rec, gap)
    ending = m0["ending"] if reuse and m0.get("ending") else pick_ending(pb, shape, rec)
    arc = list(pb["shapes"][shape]["arc"]) + list(pb["endings"][ending])
    cat = {k: v for k, v in pb.get(post.get("category", ""), {}).items() if k not in ("arc",)}
    payload = {k: post.get(k) for k in ("title", "category", "object", "subject", "fact", "slides", "caption", "unverified", "source_note", "why", "plain")}
    payload["felt"] = ft
    payload["playbook"] = {**pb.get("common", {}), **cat, "shape": pb["shapes"][shape].get("name", shape), "arc": arc, "ending": list(pb["endings"][ending])}
    payload["plain_words"] = _hk.HK.get("plain", {})
    payload["real_moves"] = _hk.real_moves(post)
    payload["recent_keywords"] = [r.get("keyword") for r in recent(12) if r.get("keyword")]
    payload["hook"] = {"spoken": hk["spoken"], "promise": hk["promise"], "on_screen": hk.get("on_screen"), "mode": mode}
    out = {"scenes": [dict(sc) for sc in post["rail"]["scenes"]], "why": m0.get("why", "")} if reuse else ask_claude(payload, prompt_text=PROMPT)   # reuse(--redirect): 대본 그대로, 쪼개기·주가 창·부품 매핑만 새 규칙으로 (11/07)
    if not reuse and not what_ok(out["scenes"], post):   # 11/07: 몸통1 첫 줄에 «그게 뭔지» 없으면 한 번만 다시 쓴다 (24편이 여기서 걸렸다)
        print("  ~ 몸통1 첫 줄에 그게 뭔지 없음 → 한 번 다시")
        what = ((post.get("plain") or {}).get("what") or "").split(".")[0]
        out = ask_claude({**payload, "fix": f"Your last script missed this rule. The FIRST line of the first body scene (right after lockin) must say what the thing is, reusing the words of this sentence: \"{what}\"."}, prompt_text=PROMPT)
    scenes = out["scenes"]
    # 관문: 첫마디 = 훅 · 금지 표현 · 뼈대 (결격은 금지 표현뿐. 나머지는 엔진이 맞추고 경고만, 11/04 «만드는 게 우선»)
    errs = []
    if scenes[0]["role"] != "opener": scenes.insert(0, {"role": "opener", "lines": []})
    scenes[0]["lines"] = [hk["spoken"], hk["promise"]]
    if len(scenes) < 2 or scenes[1]["role"] != "lockin": print("  ~ lock-in 장면이 없다"); scenes.insert(1, {"role": "lockin", "lines": [f"Keep watching and the {post.get('object', 'table').lower()} is yours."]})
    for sc in scenes:
        if sc["role"] not in TEXT_ROLES and sc["role"] not in GRAMMAR: print(f"  ~ 모르는 역할 {sc['role']} → step"); sc["role"] = "step"
        for ln in sc["lines"]:
            if len(ln.replace("*", "").split()) > 14: print(f"  ~ 긴 줄: {ln}")
            for b in BANNED:
                if b in ln.lower(): errs.append(f"금지 «{b}»: {ln}")
    roles = [sc["role"] for sc in scenes]
    if roles.count("rehook") < 2: print(f"  ~ rehook {roles.count('rehook')}개 (2개 이상이어야 kallaway 뼈대)")
    if not any(r in ("loss", "compare", "myrow", "flow") for r in roles): print("  ~ 손해를 눈으로 보는 장면이 없다")
    if "closing" not in roles: print("  ~ closing($ 다시) 이 없다")
    if gap:
        A, B = _hk.nval(str(ft["a"])), _hk.nval(str(ft["b"]))
        seen = any({A, B} <= {_hk.nval(m) for m in _hk.NUM.findall(json.dumps(sc.get("data") or {}))} for sc in scenes)
        if not seen: print(f"  ~ 차이 편인데 두 금액({ft['a']}·{ft['b']})이 한 장면에 같이 안 보인다 — 왜 잃었는지 화면이 말을 못 한다")
    if roles[-1] != "cta": print("  ~ 마지막이 cta 가 아니다")
    alltext = hk["on_screen"] + " " + hk["promise"] + " " + " ".join(ln for sc in scenes for ln in sc["lines"])
    hw = _hk.hard_words(alltext)   # 쉬운 말은 경고만 (11/05 밤 하림님 «미친 듯이 검열하면 만들 수 있는 게 없다»)
    if hw: print(f"  ~ 어려운 말 풀이 없음 {hw}")
    if errs: raise SystemExit("감독 관문:\n  " + "\n  ".join(errs))
    # cta 키워드 (발견 17): TABLE/MATH 거나 최근 12편과 같으면 물건의 주 명사로 (경고)
    cta = next((sc for sc in scenes if sc["role"] == "cta"), None)
    if cta:
        w = (cta.get("data") or {}).get("word", "").upper()
        if w in ("TABLE", "MATH", "") or w in [k.upper() for k in payload["recent_keywords"]]:
            noun = next((x for x in re.findall(r"[A-Za-z]{4,6}", post.get("object", "")) if x.upper() not in ("TABLE", "MATH", "THE", "YOUR", "SHEET", "CHECK")), "SAVE").upper()
            print(f"  ~ cta 키워드 «{w}» → «{noun}» (TABLE/MATH 거나 최근과 같다)")
            cta.setdefault("data", {})["word"] = noun
            cta["lines"] = [re.sub(r"\*[A-Z]+,?\*", f"*{noun},*", ln) for ln in cta["lines"]]
    # 말 4줄 이상인 장면은 둘로 (11/06 하림님 «말마다 모션이 있어야»): 같은 역할·데이터, 감독이 다른 부품을 고른다. 주가 창 장면은 그대로
    split = []
    for sc in scenes:
        if len(sc["lines"]) >= 3 and sc["role"] not in TEXT_ROLES and sc["role"] not in ("cta", "check"):   # 11/07 하림님 «말만 많고 모션 없음»: 3줄부터 쪼갠다 (장면당 1~2줄)
            k = 2 if len(sc["lines"]) <= 4 else 3
            split.append({**sc, "lines": sc["lines"][:k]}); split.append({**{k_: v for k_, v in sc.items() if k_ != "badge"}, "lines": sc["lines"][k:], "_cont": True})   # 배지 없음 = 키 없음 (None 이면 donut 의 k 가 깨진다, 11/07)
        else: split.append(sc)
    scenes = split; roles = [sc["role"] for sc in scenes]
    # 모션 매핑
    used_parts = [p for r in rec for p in r["parts"]]; used_open = [r["opener"] for r in rec]; used_tr = [t for r in rec for t in r["transitions"]]
    beats, parts, trans, dark_used, prev_part, prev_tr = [], [], [], False, None, None
    wins = [c for s_ in post.get("slides", []) if s_.get("type") == "chart" for c in s_.get("charts", [])]
    chart_tgt = (next((j for j, x in enumerate(scenes) if j > 0 and x["role"] not in TEXT_ROLES and any(re.search(CHART_LINES, ln, re.I) for ln in x["lines"])), None)
                 or next((j for j, x in enumerate(scenes) if x["role"] in ("compare", "myrow")), None)) if wins else None   # 11/06: 하락·줌을 말하는 장면에. 차이 장면은 두 금액 부품이 맡는다
    nodark = post.get("category") in _hk.HK["series"].get("no_dark", {}).get("list", [])
    for i, sc in enumerate(scenes):
        role, L = sc["role"], sc["lines"]
        if role == "opener":
            pref = pb["shapes"][shape].get("opener_pref", OPENERS)
            part, data = pick_opener(pref, used_open, post, hk)
            first = {"say": L[0], "part": part, "data": data, "nocap": True}
            beats.append(first); beats += [{"say": ln, "nocap": True} for ln in L[1:]]   # ② 도 화면에 찍혀 있어 자막을 안 띄운다
            parts.append(part); prev_part = part; continue
        if role == "lockin":   # lock-in 한 줄, 첫 장면 위 아래 띠 자막 (11/06 «첫 장에서 너무 오래 말만 해»)
            beats += [{"say": ln, "cap": "low"} for ln in L[:1]]; continue
        if role in TEXT_ROLES:
            beats += [{"say": ln} for ln in L]; continue
        rk = "rehook_nodata" if role == "rehook" and not sc.get("data") else role   # 데이터 없는 rehook 도 그림(callout) 을 받는다 (11/07 v2.1: 자막만인 장면 159/478 이 단조로움의 원인)
        cands = [c for c in GRAMMAR[rk] if c != prev_part] or GRAMMAR[rk]
        if sum(x in TEXT_SWAP for x in parts) >= TEXT_SWAP_CAP: cands = [c for c in cands if c not in TEXT_SWAP] or cands   # 글자교체 3종 편당 상한
        if "table" in cands and not any(x.get("type") in ("grid", "table") and len(x.get("rows") or []) >= 3 for x in post.get("slides", [])):
            cands = [c for c in cands if c != "table"] or cands   # 장표는 진짜 조회표(3행 이상)가 있을 때만. 한 줄짜리 장표는 화면이 빈다 (11/06)
        dd = sc.get("data") or {}
        if len(dd.get("rows") or []) < 2: cands = [c for c in cands if c not in ("funnel", "notify")] or cands
        if not _reconciles(dd): cands = [c for c in cands if c != "waterfall"] or cands   # 폭포는 «시작 ± 단계 = 끝» 이 숫자로 맞을 때만 (diagram-design 폭포 정직 규칙, 11/07)
        if not ("a" in dd and "b" in dd): cands = [c for c in cands if c not in G.get("pair_only", ["dumbbell"])] or cands   # 덤벨은 진짜 두 값 쌍에만 (11/07: old/new 를 쌍으로 꾸미면 헛그림)
        # 4라운드 쓸 조건 (11/07 v2): tail 은 old/new 에 $·% 가 있을 때만 · hub 는 항목 2~4개일 때만
        _dd = _oldnew(dd, sc) if role not in ("check", "cta", "flow", "compare", "myrow", "grow") else {}
        if not re.search(r"[$]\s?\d|\d\s?%", str(_dd.get("old", "")) + " " + str(_dd.get("new", ""))): cands = [c for c in cands if c != "tail"] or cands
        if not (2 <= len(dd.get("items") or []) <= 4): cands = [c for c in cands if c != "hub"] or cands
        if not dd.get("steps"): cands = [c for c in cands if c not in ("multiply", "clock")] or cands
        if not any(abs(_num(x)) >= 100 for x in re.findall(r"\$\d[\d,]*", " ".join(L) + json.dumps(dd))): cands = [c for c in cands if c != "odometer"] or cands   # $3 을 오도미터로 돌리면 우습다 (11/07)
        if not re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}\b", " ".join(L)): cands = [c for c in cands if c != "countdown"] or cands
        part = least_used(cands, used_parts + parts, avoid=parts)   # 같은 편 안에서 같은 부품 두 번은 피한다 (대안이 있을 때)
        if sc.get("_cont") and prev_part == "chart": part = "chart"   # 쪼갠 뒤 장면이 주가 창이면 창을 잇는다
        if i == chart_tgt and "chart" not in parts:   # 진짜 주가 창: compare 장면(줌아웃 대사)에 (11/05)
            part = "chart"; sc.setdefault("data", {})["chart"] = wins[0]
            same = sorted([w for w in wins if w.get("ticker") == wins[0].get("ticker")], key=lambda w: RANGE_ORDER.index(w.get("range", "1mo")) if w.get("range") in RANGE_ORDER else 0)
            if len(same) >= 2: sc["data"]["chart"], sc["data"]["long"] = same[0], same[-1]
            other = next((w for w in wins if w.get("ticker") != wins[0].get("ticker")), None)
            if other and len(same) < 2: sc["data"]["second"] = other   # 티커가 둘이면 둘째 창이 둘째 티커를 말할 때 아래로 들어온다 (11/07 XEQT vs VEQT)   # 줌아웃은 같은 티커의 짧은 창 → 긴 창일 때만 (11/07: XEQT 5y → VEQT 5y 로 «줌아웃»해 창이 빨갰다)
        first = {"say": L[0], "part": part, "data": data_for(part, sc, post)}
        if sc.get("badge") and role in ("flow", "compare", "grow", "step", "catch", "myrow") and part != "chart": first["badge"] = sc["badge"]   # 창은 자기 머리가 있다
        # 다크 컷: loss 장면 한 번 (11/05: 둘째 장면은 밝게 · no_dark 시리즈는 없음)
        if role == "loss" and not dark_used and not nodark and len(parts) >= 2: first["dark"] = True; dark_used = True
        # 전환: 6종 least_used, 같은 전환 연속 금지. cta 는 dissolve
        if role == "cta": tr = "dissolve"
        else: tr = least_used(TRANS, used_tr + trans, avoid=(prev_tr,))
        if tr != "fade": first["in"] = tr
        nxt = scenes[i + 1]["role"] if i + 1 < len(scenes) else None
        if role in ("flow", "myth") and nxt == "loss" and trans.count("tear") == 0: first["out"] = "tear"; trans.append("tear")
        trans.append(tr); prev_tr = tr
        beats.append(first); beats += [{"say": ln} for ln in L[1:]]
        parts.append(part); prev_part = part
    heavy = trans.count("tear") + dark_used + sum(p_ in HEAVY_PARTS for p_ in parts)   # 무거운 것: 찢김·다크·3D (fx-목록 규칙 2, 3개까지)
    if heavy > HEAVY_MAX: print(f"  ~ 무거운 것 {heavy}개")
    caption = least_used(CAPTIONS, [r.get("caption") for r in rec], avoid=[r.get("caption") for r in rec][-1:])
    rail = {"note_": f"엔진/motion/rail/director.py 가 {datetime.date.today()} 에 만들었다. 대본 prompts/rail.md (kallaway 9칸, 꼴 {shape}, 끝맺음 {ending}) · 모션 매핑 GRAMMAR. 훅 방식 {mode}.",
            "voice": "af_heart", "speed": 1.0, "hold": 3.5, "caption": caption, "beats": beats, "scenes": [{k: v for k, v in sc.items() if not k.startswith("_")} for sc in scenes],   # 클론 폐기, af_heart 복귀 (11/04 밤 하림님: «호불호 없는 여자 AI 목소리로»)
            "made_by": {"why": out.get("why", ""), "shape": shape, "ending": ending, "caption": caption, "opener": parts[0], "parts": parts, "transitions": trans, "heavy": heavy,
                        "roles": roles, "keyword": (cta or {}).get("data", {}).get("word")}}
    # 사이트·캐러셀이 쓰는 필드 (레드팀: 부품 이름에 기대지 않는다)
    post["deliver"] = {"word": (cta or {}).get("data", {}).get("word", ""), "gift": (cta or {}).get("data", {}).get("gift", post.get("object", "").lower())}
    ck = next((sc for sc in scenes if sc["role"] == "check"), None)
    post["check"] = list((ck or {}).get("data", {}).get("items") or [])
    return rail

def remap(post, stem):
    """대본은 그대로, 모션만 다시 매핑 (모델 없이). rail.scenes + 지금 부품 순서(made_by.parts)로 data_for 를 다시 돈다. 부품 규칙이 바뀌었을 때 47편에 한 번에."""
    rail = post["rail"]; scenes = rail.get("scenes"); m = rail.get("made_by") or {}
    if not scenes: raise SystemExit(f"{stem}: rail.scenes 가 없다 (11/06 이전 대본) — build.py --direct --force")
    hk = post["hooks"]; parts = list(m.get("parts") or []); beats = []; pi = 0; k = 0
    old = [b for b in rail["beats"] if b.get("part")]
    for sc in scenes:
        role, L = sc["role"], sc["lines"]
        if role == "opener":
            ob = old[0]; beats.append({"say": L[0], "part": ob["part"], "data": ob["data"], "nocap": True}); beats += [{"say": ln, "nocap": True} for ln in L[1:]]; pi += 1; continue
        if role == "lockin": beats += [{"say": ln, "cap": "low"} for ln in L[:1]]; continue
        if role in TEXT_ROLES or (role == "rehook" and not sc.get("data")): beats += [{"say": ln} for ln in L]; continue
        if pi >= len(old): break
        ob = old[pi]; part = ob["part"]; pi += 1
        if part == "chart": sc.setdefault("data", {}).update({k_: v for k_, v in ((ob["data"].get("chart") and {"chart": ob["data"]["chart"], "long": ob["data"].get("long")}) or {"chart": ob["data"]}).items() if v})
        first = {"say": L[0], "part": part, "data": data_for(part, sc, post)}
        for key in ("badge", "in", "out", "dark"):
            if ob.get(key): first[key] = ob[key]
        beats.append(first); beats += [{"say": ln} for ln in L[1:]]
    rail["beats"] = beats
    rail["note_"] = (rail.get("note_", "") + f" · {datetime.date.today()} remap").strip(" ·")
    return rail

def reopen(post, stem):
    """훅만 바뀐 편: 첫 두 비트 say(① 훅 · ② 약속) + 첫 장면 부품·데이터만 교체. 대본 나머지는 그대로 (11/06 레드팀 발견 16, scratchpad reopen.py 를 엔진으로)."""
    hk = post["hooks"]; rail = post["rail"]; b = rail["beats"]
    mode = hk.get("modes", ["숫자"])[hk["candidates"].index(hk["on_screen"])] if hk.get("on_screen") in hk.get("candidates", []) else "숫자"
    part, data = pick_opener(OPENERS, [r["opener"] for r in recent()], post, hk)
    b[0] = {"say": hk["spoken"], "part": part, "data": data, "nocap": True}
    if len(b) > 1 and not b[1].get("part"): b[1] = {"say": hk["promise"], "nocap": True}
    else: b.insert(1, {"say": hk["promise"], "nocap": True})
    for x in b[2:]: x.pop("t0", None); x.pop("t1", None); x.pop("toks", None)   # 시각은 build_rail 이 다시 잰다
    m = rail.setdefault("made_by", {}); m["opener"] = part; m["parts"] = [part] + (m.get("parts") or [None])[1:]
    rail["note_"] = (rail.get("note_", "") + f" · {datetime.date.today()} reopen (훅 방식 {mode}, 첫 장면 {part})").strip(" ·")
    log(stem, rail)
    return rail

def log(stem, rail):
    import fcntl   # 여러 편을 나란히 만들 때 원장이 서로 덮지 않게 (11/06)
    with open(LEDGER.with_suffix(".lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        rows = json.load(open(LEDGER)) if LEDGER.exists() else []
        rows = [r for r in rows if r["post"] != stem]
        m = rail["made_by"]
        rows.append({"date": str(datetime.date.today()), "post": stem, "shape": m.get("shape"), "ending": m.get("ending"), "caption": m.get("caption"), "opener": m["opener"], "parts": m["parts"], "transitions": m["transitions"], "keyword": m.get("keyword")})
        json.dump(rows, open(LEDGER, "w"), ensure_ascii=False, indent=1)

def stats(posts=None):
    """분포 표 + 관문: 같은 꼴 연속 3편 FAIL · 한 꼴 50% 넘으면 FAIL · 끝맺음 한 종류 60% 넘으면 FAIL. 첫 장면·부품·전환은 보여만 준다."""
    rows = json.load(open(LEDGER)) if LEDGER.exists() else []
    if posts: rows = [r for r in rows if r["post"] in posts]
    n = len(rows) or 1
    def dist(key, flat=False):
        c = {}
        for r in rows:
            for v in (r.get(key) or []) if flat else [r.get(key)]: c[v] = c.get(v, 0) + 1
        return dict(sorted(c.items(), key=lambda kv: -kv[1]))
    shapes, ends = dist("shape"), dist("ending")
    fam = dist("parts", True); tr = dist("transitions", True)
    per = [len(set(r.get("parts") or []) | set(r.get("transitions") or [])) for r in rows]
    bad = []
    if per and min(per) < 5: bad.append(f"한 편 가족 <5: {[r['post'] for r in rows if len(set(r.get('parts') or []) | set(r.get('transitions') or [])) < 5][:5]}")
    if len(fam) + len(tr) < 25: bad.append(f"전체 가족 {len(fam) + len(tr)} < 25")
    slots = [p for r in rows for p in (r.get("parts") or [])[1:] if p != "tiles"]
    if slots and max(slots.count(p) for p in set(slots)) / len(slots) > .5: bad.append(f"부품 {max(set(slots), key=slots.count)} 가 부품 칸의 50% 넘음")
    if shapes and max(shapes.values()) / n > .5: bad.append(f"꼴 {max(shapes, key=shapes.get)} 가 {max(shapes.values())}/{n}")
    if ends and max(ends.values()) / n > .6: bad.append(f"끝맺음 {max(ends, key=ends.get)} 가 {max(ends.values())}/{n}")
    run = 1; warn_run = ""
    for a, b in zip(rows, rows[1:]):
        run = run + 1 if a.get("shape") and a.get("shape") == b.get("shape") else 1
        if run >= 3: warn_run = f"~ 같은 꼴 연속 3편 (제작 원장 순서, {b['post']}) — 게시 순서는 4단계 find.py plan 이 정한다"; break
    md = [f"# 대본 분포 — {datetime.date.today()} · {n}편", "", "| 축 | 분포 |", "|---|---|",
          f"| 꼴 | {shapes} |", f"| 끝맺음 | {ends} |", f"| 자막 | {dist('caption')} |", f"| 첫 장면 | {dist('opener')} |", f"| 부품 | {fam} |", f"| 전환 | {tr} |",
          f"| 가족 | 전체 {len(fam) + len(tr)} · 편당 최소 {min(per) if per else 0} · 평균 {sum(per) / len(per) if per else 0:.1f} |", "",
          (("**FAIL** " + " · ".join(bad)) if bad else "관문 PASS (꼴 ≤50% · 끝맺음 ≤60% · 편당 가족 ≥5 · 전체 ≥25 · 한 부품 ≤50% 칸)") + (("\n" + warn_run) if warn_run else "")]
    out = ENG / "out" / "작업" / "shape-stats.md"; out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md)); print(f"  → {out}")
    return bad

CALL = re.compile(r"\b(you should|time to|go) (buy|sell)\b|\bbuy the dip\b|\b(load up on|go all in|all in on)\b|(?:^|[.!?]\s*)(?:just )?(buy|sell) (it|this|now|everything|more)( now| today)?[.!]?\s*$", re.I)   # 권유·명령 문장만. «Sell now and $X is gone»·«can't buy it directly»·«sell it in a regular box» 는 설명 (11/06)
def review(posts=None):
    """레드팀 관문 (영상 대신 대본·장면 데이터로, 11/06 하림님 «한 편씩 보지 않는다»). 편마다 FAIL/경고 → out/작업/review.md.
    FAIL 은 넷뿐(지어낸 숫자 · 매수콜 · 훅에 felt 없음 · 금지 표현). 나머지는 경고: lock-in 한 줄 · 말마다 캡션 · rehook ≥2 · closing · 차이 두 금액 한 장면 · 차트 줄 · 한 부품에 말 4줄+ · 가족 ≥5 · 어려운 말."""
    import hook as _hk
    paths = [p for p in _hk.posts_all() if not posts or pathlib.Path(p).stem in posts]
    rows = []; nfail = 0
    agg = {}
    for p in paths:
        post = json.load(open(p, encoding="utf-8")); stem = pathlib.Path(p).stem; rail = post.get("rail") or {}; b = rail.get("beats") or []
        m = rail.get("made_by") or {}; hk = post.get("hooks") or {}; ft = _hk.felt(post)
        fails, warns = [], []
        # FAIL
        g = _hk.gates(hk.get("on_screen", ""), post.get("category", ""), _hk.subject(post), ft, post.get("fact"))
        fails += [x for x in g if not x.startswith("~")]
        try: build_rail.gate(post)
        except SystemExit as x: fails.append(str(x)[:80])
        for x in b:
            if any(w in x["say"].lower() for w in BANNED): fails.append(f"금지 표현: {x['say'][:40]}")
            if CALL.search(x["say"]): fails.append(f"매수콜: {x['say'][:40]}")
        # 경고
        if not b or b[0].get("part") not in OPENERS: warns.append("첫 장면 부품 아님")
        if b and not (b[0].get("data") or {}).get("stamp"): warns.append("도장 없음")
        over = [x for x in b[2:] if not x.get("part")][:next((i for i, x in enumerate(b[2:]) if x.get("part")), 0)] if len(b) > 2 else []
        if len(over) != 1: warns.append(f"lock-in {len(over)}줄")
        if any(x.get("nocap") for x in b[2:]): warns.append("캡션 없는 말")
        roles = m.get("roles") or []
        if roles.count("rehook") < 2: warns.append(f"rehook {roles.count('rehook')}")
        if "closing" not in roles: warns.append("closing 없음")
        if roles and roles[-1] != "cta": warns.append("끝이 cta 아님")
        if ft and ft.get("a") and ft.get("b"):
            A, B = _hk.nval(str(ft["a"])), _hk.nval(str(ft["b"]))
            if not any({A, B} <= {_hk.nval(x) for x in _hk.NUM.findall(json.dumps(bt.get("data") or {}))} for bt in b): warns.append("차이 두 금액이 한 장면에 없음")
        segs = []
        for x in b:
            if x.get("part"): segs.append([x])
            elif segs: segs[-1].append(x)
        long_ = [sc["role"] for sc in (rail.get("scenes") or []) if len(sc.get("lines") or []) >= 3 and sc["role"] not in TEXT_ROLES] if rail.get("scenes") else [s[0]["part"] for s in segs[1:] if len(s) >= 4]
        if long_: warns.append(f"한 장면에 말 3줄+: {long_}")   # rehook 한 줄이 앞 장면에 붙는 건 정상 (자막이 있다)
        for s in segs:
            if s[0].get("part") == "chart" and not any(re.search(r"\d+(?:\.\d+)?%|zoom|fell", x["say"], re.I) for x in s): warns.append("차트 장면에 하락·줌 말 없음")
        fam = set(m.get("parts") or []) | set(m.get("transitions") or [])
        if len(fam) < 5: warns.append(f"가족 {len(fam)}")
        ih = ENG / "out" / "작업" / f"{stem}-rail" / "index.html"   # 11/07 하림님 «말만 많고 모션 없음»: 만든 타임라인에서 그림이 멈춘 구간을 잰다 (자막 제외)
        if ih.exists():
            js_ = ih.read_text(encoding="utf-8"); end = float(re.search(r'data-duration="([\d.]+)"', js_).group(1))
            iv = []   # 트윈이 덮는 구간 [시작, 시작+길이] (자막 제외). 덮이지 않은 구간이 STILL_MAX 넘으면 «정지»
            for call, t in re.findall(r'((?:tl\.(?:fromTo|to)\("(?!#c\d|#cap)[^"]*"|pop\("[^"]*")[^;]*?),\s*([\d.]+)\);', js_):
                dm = re.search(r"duration:([\d.]+)", call); d_ = float(dm.group(1)) if dm else .5
                if "repeat:" in call: d_ *= 2
                iv.append((float(t), float(t) + d_))
            gaps, cur = [], 0.0
            for x, y in sorted(iv):
                if x - cur > STILL_MAX: gaps.append((x - cur, cur))
                cur = max(cur, y)
            if end - 3.5 - cur > STILL_MAX: gaps.append((end - 3.5 - cur, cur))
            if gaps: warns.append("정지 " + " · ".join(f"{g:.0f}s@{t:.0f}s" for g, t in sorted(gaps, reverse=True)[:3]))
            cj_ = ih.with_name("check.json")   # hyperframes check 집계 (11/07): 코드별 수. 경고만
            if cj_.exists():
                codes = json.load(open(cj_)).get("codes") or {}
                keep = {k: v for k, v in codes.items() if not k.endswith(("line_unread", "text_below_floor"))}   # 자막 거짓양성은 뺀다
                if keep: warns.append("check " + " · ".join(f"{k.split(':')[1]} {v}" for k, v in sorted(keep.items(), key=lambda kv: -kv[1])[:4]))
            # 줄 반응 (11/07 레드팀 11번): 말한 줄의 첫 단어 ±0.4초 안에 자막 아닌 트윈이 시작하면 «반응». 비율이 REACT_MIN 아래면 «말만 많다»
            bj = ih.with_name("beats.json"); tb_ = json.load(open(bj, encoding="utf-8")) if bj.exists() else []
            starts = sorted(x for x, _ in iv); said = [x["t0"] for x in tb_[2:] if not x.get("nocap")]
            if said:
                hit = sum(1 for t0 in said if any(abs(t_ - t0) <= .4 for t_ in starts))
                if hit / len(said) < REACT_MIN: warns.append(f"줄 반응 {hit}/{len(said)}")
        hw = _hk.hard_words(" ".join(x["say"] for x in b))
        if hw: warns.append(f"어려운 말 {hw[:3]}")
        rj = ENG / "out" / "작업" / "reader.json"; dj = ENG / "out" / "작업" / "deliver.json"   # claude-37 의 낯선 사람 읽기·납품 실측을 같은 표에 (11/07 v2.1)
        try:
            rd = (json.load(open(rj, encoding="utf-8")) or {}).get(stem) if rj.exists() else None
            if rd and not rd.get("ok"): warns.append("낯선사람 " + ",".join(rd.get("miss") or []))
            dv = next((x for x in (json.load(open(dj, encoding="utf-8")) if dj.exists() else []) if x.get("key") == stem), None)
            if dv:
                if dv.get("lufs") is not None and abs(dv["lufs"] - (-14)) > 1 and not dv.get("normalized"): warns.append(f"소리 {dv['lufs']:.1f}LUFS")
                fz = [f for f in (dv.get("freezes") or []) if f[1] >= STILL_MAX]
                if fz: warns.append("정지(실측) " + " · ".join(f"{d_:.1f}s@{t:.0f}s" for t, d_ in fz[:3]))
                if dv.get("blacks"): warns.append(f"검은프레임 {len(dv['blacks'])}")
        except Exception as x: warns.append(f"reader/deliver 못 읽음 {str(x)[:40]}")
        scs = rail.get("scenes") or []   # 11/07 v2.1 칸 검사 (결정론, 경고): 몸통1 첫 줄에 «그게 뭔지» · closing 에 felt
        if not what_ok(scs, post): warns.append("몸통1 첫 줄에 그게 뭔지 없음")
        cl = next((sc for sc in scs if sc.get("role") == "closing"), None)
        if cl and ft and _hk.felt_str(ft) not in " ".join(cl.get("lines") or []): warns.append("closing 에 felt 없음")
        for w_ in warns: agg[w_.split(" ")[0]] = agg.get(w_.split(" ")[0], 0) + 1
        if fails: nfail += 1
        rows.append(f"| {stem} | {m.get('shape', '')}/{m.get('ending', '')} | {'**FAIL** ' + ' · '.join(fails) if fails else 'PASS'} | {' · '.join(warns)} |")
    tally = " · ".join(f"{k} {v}" for k, v in sorted(agg.items(), key=lambda kv: -kv[1]))   # 경고 집계 (11/07 v2.1: 한 표에서 본다)
    md = [f"# 레드팀 관문 — {datetime.date.today()} · {len(paths)}편 · FAIL {nfail}", "", "FAIL 넷(지어낸 숫자·매수콜·훅 felt 없음·금지 표현)만 막는다. 나머지는 경고.", "", f"경고 집계: {tally or '없음'}", "",
          "| 편 | 꼴/끝맺음 | 판정 | 경고 |", "|---|---|---|---|"] + rows
    out = ENG / "out" / "작업" / "review.md"; out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:1] + [md[4]] + rows)); print(f"  → {out}")
    return nfail

def main(path, dry=False, force=False, render=False, reuse=False):
    path = pathlib.Path(path); post = json.load(open(path, encoding="utf-8")); stem = path.stem
    if reuse and not (post.get("rail") or {}).get("scenes"): raise SystemExit(f"{stem}: rail.scenes 가 없다 — --direct --force")
    if post.get("rail") and not force and not dry and not reuse:
        raise SystemExit(f"{path.name} 에 rail{{}} 이 이미 있다. 새로 쓰려면 --force (예전 것은 rail_prev 로), 보기만 하려면 --dry")
    rail = direct(post, stem, reuse)
    trial = dict(post); trial["rail"] = rail
    build_rail.gate(trial)   # 숫자 관문: 대본 숫자가 이 편 json 에 없으면 멈춘다
    m = rail["made_by"]
    print(f"감독  꼴 {m['shape']} · 끝맺음 {m['ending']} · 첫 장면 {m['opener']} · 부품 {' → '.join(m['parts'])} · 전환 {m['transitions']} · 무거운 것 {m['heavy']}")
    for b in rail["beats"]: print(f"   {b.get('part','  ·'):>9}  {b['say']}")
    if dry:
        return build_rail.build(trial, stem + "-auto", render)
    if post.get("rail_prev"): post["rail_prev2"] = post["rail_prev"]   # 11/06: --force 가 옛것을 덮지 않게 두 벌 남긴다
    if post.get("rail"): post["rail_prev"] = post["rail"]
    post["rail"] = rail
    json.dump(post, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log(stem, rail)
    return build_rail.build(post, stem, render)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if "--stats" in sys.argv: sys.exit(1 if stats(a or None) else 0)
    if "--review" in sys.argv: sys.exit(1 if review(a or None) else 0)
    main(a[0], "--dry" in sys.argv, "--force" in sys.argv, "--render" in sys.argv, "--reuse" in sys.argv)
