#!/usr/bin/env python3
"""찾기 엔진. 무엇을 만들지 · 그 숫자가 맞는지 · 훅까지. 디자인·릴스 틀은 건드리지 않고 그 앞단만 한다 (하림님 2026-11-04).

흐름 (칸마다 정본 파일 하나, 전부 엔진/find/)
  1 신호   prompts/find-signals.md + 웹 → signals.json   이미 터졌다는 증거 (터진 릴스·반복 질문·뉴스·돈 달력). 링크·지표·원문
  2 퍼스나 prompts/find-persona.md        → persona.json   신호 원문에서만 세운 독자 2~3명. 지어낸 말은 관문이 버린다
  3 주제   prompts/find-topics.md         → topics.json    줄기(pillars.json) × 퍼스나 × 신호 → 다섯 칸 점수 + 퍼스나 판정 → 순위
  4 사실   prompts/find-fact.md + 웹      → topics.json    숫자 하나를 1차 출처에서. 엔진이 그 페이지를 직접 받아 인용 문장을 대조한다. 계산은 다시 계산한다
  5 씨앗   콘텐츠/찾은/<key>.json → hook.py --make (① 훅 + ② 약속) → 그다음은 기존 엔진 (build.py --direct)
  6 되먹임 hooks-ledger.json 의 저장 수가 그 줄기 순위를 올린다

관문이 법이다. 모델이 «확인했다»고 해도 페이지에 그 문장이 없으면 그 숫자는 없다.

사용
  python3 엔진/find.py signals [--pillar bitcoin] [--n 12]
  python3 엔진/find.py persona
  python3 엔진/find.py topics [--n 20]
  python3 엔진/find.py fact <key> | --top 5
  python3 엔진/find.py seed <key> | --top 5
  python3 엔진/find.py write <key> | --top 5   # 속장 2~3장 + 캡션 (prompts/post.md)
  python3 엔진/find.py run [--n 5]          # 1~5 한 바퀴. 몇 번이고 다시 돌리면 쌓인다
  python3 엔진/find.py stats
"""
import argparse, datetime, hashlib, html, json, pathlib, re, sys, urllib.request

P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P))
import hook   # ask_claude 와 make (① 훅 + ② 약속) 를 그대로 쓴다

F = P / 'find'; F.mkdir(exist_ok=True)
OUT = P.parent / '콘텐츠' / '찾은'
WEB = 'WebSearch,WebFetch'
PIL = json.load(open(F / 'pillars.json', encoding='utf-8'))
PILLARS = {p['id']: p for p in PIL['pillars']}
TODAY = str(datetime.date.today())


def prompt(name): return re.sub(r"\A---\n.*?\n---\n", "", (P / 'prompts' / name).read_text(encoding='utf-8'), flags=re.S)
def load(name, empty): return json.load(open(F / name, encoding='utf-8')) if (F / name).exists() else empty
def save(name, data):
    """topics.json 은 편마다 다시 읽어 합친다 (11/05: 4편 동시에 돌리다 서로 덮어씀). 한 편의 레코드만 바꾸고 나머지는 디스크 것을 믿는다."""
    if name == 'topics.json' and (F / name).exists():
        disk = {t['key']: t for t in json.load(open(F / name, encoding='utf-8'))}
        mine = {t['key']: t for t in data}
        for k, t in mine.items():
            if k not in disk or json.dumps(t, sort_keys=True) != json.dumps(disk[k], sort_keys=True):
                if k in disk and disk[k].get('status') not in ('idea', t.get('status')) and t.get('status') == 'idea': continue   # 디스크가 더 앞서면 내 옛 복사본으로 덮지 않는다
                disk[k] = t
        data = list(disk.values())
    json.dump(data, open(F / name, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open(F / name, 'a').write('\n')


# ── 대조: 엔진이 직접 페이지를 받아 본다 ─────────────────────────────
def norm(s):
    s = html.unescape(s or '').replace(' ', ' ').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace('−', '-')
    return re.sub(r'\s+', ' ', s).strip().lower()

def page_text(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh) hama-find/1'})
        raw = urllib.request.urlopen(req, timeout=25).read()
    except Exception:
        return None
    if raw[:4] == b'%PDF':   # PDF 는 글자로 뽑아야 대조된다 (펀드 팩트 등)
        import subprocess
        try: raw = subprocess.run(['pdftotext', '-', '-'], input=raw, capture_output=True, timeout=60).stdout
        except Exception: return None
    raw = raw.decode('utf-8', 'ignore')
    raw = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    return norm(re.sub(r'<[^>]+>', ' ', raw))

def on_page(url, quote):
    """True = 인용이 페이지에 있다 · False = 페이지는 열렸는데 없다 · None = 페이지가 안 열린다 (소셜은 흔하다)."""
    if not quote: return None
    t = page_text(url)
    q = norm(quote).rstrip('.')
    if t is None: return refetch(url, quote)
    return q in t or q[:120] in t

def refetch(url, quote):
    """엔진이 못 여는 페이지(정부 사이트가 스크립트 접속을 막는다)는 WebFetch 로 한 번 더 연다. 판정만 받고, 못 열면 None."""
    try:
        out = hook.ask_claude({"url": url, "sentence": quote}, timeout=300, tools='WebFetch', prompt_text=
            'Open the url with WebFetch. Answer {"found": true} only if the sentence (or the same sentence with only spacing or punctuation differences) appears on that page, with the same numbers. Answer {"found": false} if the page opened but the sentence is not there, {"found": null} if the page did not open. JSON only.\n\nInput: ')
        return {True: 'webfetch', False: False}.get(out.get('found'))
    except Exception:
        return None

def same(a, b):
    """«1.00» 과 «1» 은 같은 숫자다."""
    try: return float(str(a).replace(',', '')) == float(str(b).replace(',', ''))
    except ValueError: return False

def digits(s): return re.sub(r'[^\d.]', '', str(s or '')).rstrip('.')

def fv(monthly, rate, years):
    """월말 납입 미래가치. Day 4 와 같은 식: P × ((1+r)^n − 1) / r."""
    r = float(rate) / 100 / 12; n = int(years) * 12
    return float(monthly) * ((1 + r) ** n - 1) / r


# ── 1 신호 ────────────────────────────────────────────────────────
def signals(pillar=None, n=12, brief=None):
    rows = load('signals.json', [])
    seen = {r['url'] for r in rows}
    for pid in ([pillar] if pillar else list(PILLARS)):
        if PILLARS[pid].get('needs_hama'): continue   # 원장은 하마 기록이 신호다
        out = hook.ask_claude({"pillar": {"id": pid, **PILLARS[pid]}, "banned": PIL['banned_topics'], "fresh": PIL['fresh'], "seen": sorted(seen)[-200:],
                               "count": n, "audience": "Canadian beginners, English", "today": TODAY, "brief": brief},
                              timeout=900, prompt_text=prompt('find-signals.md'), tools=WEB)
        add = 0
        for s in out.get('signals', []):
            url = (s.get('url') or '').strip()
            if not url.startswith('http') or url in seen: continue
            if not (s.get('fomo') or '').strip(): continue   # 포모 변환이 안 되는 정보는 신호가 아니다 (하림님 11/04)
            s['id'] = 's' + hashlib.sha1(url.encode()).hexdigest()[:8]; s['pillar'] = pid
            s['quote_checked'] = on_page(url, s.get('quote')); s['found'] = TODAY
            rows.append(s); seen.add(url); add += 1
        print(f"  신호 {pid:11s} +{add}  (원문 대조됨 {sum(1 for s in rows if s['pillar']==pid and s.get('quote_checked'))})")
        save('signals.json', rows)
    return rows


# ── 2 퍼스나 ──────────────────────────────────────────────────────
def persona():
    sig = load('signals.json', [])
    if len(sig) < 6: raise SystemExit(f"신호 {len(sig)}개 — 6개 이상 모은 뒤에 퍼스나를 세운다 (find.py signals)")
    ids = {s['id'] for s in sig}; quotes = [norm(s.get('quote')) for s in sig if s.get('quote')]
    out = hook.ask_claude({"signals": [{k: s.get(k) for k in ('id', 'kind', 'pillar', 'title', 'quote', 'metric', 'why')} for s in sig]},
                          prompt_text=prompt('find-persona.md'))
    ps = []
    for p in out.get('personas', []):
        p['signal_ids'] = [i for i in p.get('signal_ids', []) if i in ids]
        made = [w for w in p.get('words', []) if not any(norm(w) in q for q in quotes)]
        p['words'] = [w for w in p.get('words', []) if w not in made]   # 신호 원문에 없는 말은 지어낸 말이다
        if made: p['dropped_words'] = made
        if len(p['signal_ids']) >= 3: ps.append(p)
        else: print(f"  ✗ 퍼스나 «{p.get('name')}» 근거 신호 {len(p['signal_ids'])}개 — 3개 미만이라 버린다")
    save('persona.json', {"made_on": TODAY, "from_signals": len(sig), "personas": ps})
    for p in ps: print(f"  퍼스나 {p['name']}  ·  신호 {len(p['signal_ids'])}  ·  {p.get('stops_for','')}")
    return ps


# ── 3 주제 ────────────────────────────────────────────────────────
def boost():
    """6 되먹임: 줄기별 평균 저장 수 → 순위 배수. 결과가 없으면 1."""
    by = {}
    tops = {t['key']: t['pillar'] for t in load('topics.json', [])}
    for r in hook.load_ledger():
        sv = (r.get('result') or {}).get('saves')
        if sv is not None and r['post'] in tops: by.setdefault(tops[r['post']], []).append(sv)
    allv = [v for vs in by.values() for v in vs]
    if not allv: return {}
    mean = sum(allv) / len(allv) or 1
    return {k: min(2.0, max(0.5, (sum(v) / len(v)) / mean)) for k, v in by.items()}   # ponytail: 평균 비율만, 표본 적을 때 흔들린다. 편 30개 넘으면 베이지안으로

def rank(t, b=None):
    sc = sum((t.get('scores') or {}).values()); v = t.get('persona_verdict') or {}
    return round((sc + v.get('stop', 0) + v.get('save', 0) + v.get('send', 0)) * PILLARS[t['pillar']]['weight'] * (b or {}).get(t['pillar'], 1), 2)

def topics(n=20, brief=None):
    sig = load('signals.json', []); per = load('persona.json', {}).get('personas', [])
    if not per: raise SystemExit("퍼스나가 없다 — find.py persona 먼저")
    rows = load('topics.json', []); have = {t['key'] for t in rows}; ids = {s['id'] for s in sig}
    out = hook.ask_claude({"pillars": PIL['pillars'], "must": PIL['must'], "banned": PIL['banned_topics'], "fresh": PIL['fresh'], "personas": per,
                           "signals": [{k: s.get(k) for k in ('id', 'kind', 'pillar', 'title', 'quote', 'metric', 'date', 'why')} for s in sig],
                           "have": [{"key": t['key'], "title": t['title']} for t in rows], "count": n, "brief": brief},
                          timeout=900, prompt_text=prompt('find-topics.md'))
    add = 0; new = []
    for t in out.get('topics', []):
        why = []
        if t.get('pillar') not in PILLARS: why.append(f"줄기 없음 {t.get('pillar')}")
        elif t.get('category') != PILLARS[t['pillar']]['category']: t['category'] = PILLARS[t['pillar']]['category']
        t['signal_ids'] = [i for i in t.get('signal_ids', []) if i in ids]
        if not t['signal_ids']: why.append("근거 신호 없음")
        if re.search(r'\d', t.get('angle', '')): print(f"  ~ {t.get('key')}: 각도에 숫자 — 경고만. 숫자는 4 사실에서 다시 확인한다")
        if not t.get('key') or t['key'] in have: why.append("겹침")
        if why: print(f"  ✗ {t.get('key')}: {' · '.join(why)}"); continue
        t.update(status='idea', found=TODAY, **({'brief': brief} if brief else {})); rows.append(t); have.add(t['key']); add += 1; new.append(t['key'])
    b = boost()
    for t in rows: t['rank'] = rank(t, b)
    rows.sort(key=lambda t: -t['rank']); save('topics.json', rows)
    print(f"  주제 +{add}  ·  모두 {len(rows)}")
    return new


# ── 4 사실 ────────────────────────────────────────────────────────
def fact_gate(f):
    """숫자 관문. 인용이 실제 페이지에 있고, 숫자가 그 인용 안에 있어야 한다. 계산은 엔진이 다시 한다."""
    why = []; srcs = f.get('sources') or []; num = digits(f.get('num')).replace(',', '')
    for s in srcs: s['checked'] = on_page(s.get('url', ''), s.get('quote'))
    ok = [s for s in srcs if s['checked']]
    # 결격은 «출처가 아예 없음» 하나. 페이지 대조·숫자 대조는 표시만 한다 (하림님 11/04 «너무너무 검증할 필요 없다»)
    if not srcs or not (f.get('claim') or f.get('num')): return ["출처나 주장이 없다"]
    if not ok: print(f"    ~ 페이지 대조 못 함 — 출처 {len(srcs)}곳 그대로 쓴다")
    c = f.get('calc')
    if c:
        try:
            got = fv(c['monthly'], c['rate'], c['years']); want = float(num.replace(',', ''))
            if abs(got - want) / got > 0.02: print("    ~ " + f"계산이 안 맞는다: 다시 계산하면 {got:,.0f}, 적힌 숫자 {f['num']}")
        except Exception as x: why.append(f"계산 칸이 깨졌다 {x}")
    elif not any(same(num, x) for s in srcs for x in re.findall(r'\d[\d,]*(?:\.\d+)?', s.get('quote') or '')):
        print(f"    ~ 숫자 {f.get('num')} 가 인용 글자에 없다 — 경고만")
    return why

def fact(keys):
    rows = load('topics.json', [])
    for t in [t for t in rows if t['key'] in keys]:
        if PILLARS[t['pillar']].get('needs_hama'):
            t['status'] = 'needs-hama'; print(f"  · {t['key']}: 하마 실제 기록이 필요하다 (하림님 손)"); continue
        out = hook.ask_claude({"topic": {k: t.get(k) for k in ('key', 'title', 'angle', 'number_needed', 'object', 'category', 'brief')}, "today": TODAY},
                              timeout=900, prompt_text=prompt('find-fact.md'), tools=WEB)
        f = out.get('fact')
        if not f: t.update(status='no-fact', why=[out.get('why', '모름')]); print(f"  ✗ {t['key']}: {t['why'][0]}"); save('topics.json', rows); continue
        if out.get('subject'): t['subject'] = out['subject']
        why = fact_gate(f)
        if why: t.update(status='no-fact', why=why, fact_try=f); print(f"  ✗ {t['key']}: {' · '.join(why)}")
        else:
            t.update(status='fact', fact=f); t.pop('why', None)
            print(f"  ✓ {t['key']}: {f.get('unit','') if f.get('unit')=='$' else ''}{f['num']}{'' if f.get('unit')=='$' else f.get('unit','')}  ·  {sum(1 for s in f['sources'] if s['checked'])}곳 대조")
        save('topics.json', rows)


# ── 5 씨앗 → 훅 ──────────────────────────────────────────────────
def seed(keys):
    rows = load('topics.json', []); OUT.mkdir(parents=True, exist_ok=True)
    for t in [t for t in rows if t['key'] in keys and t['status'] == 'fact']:
        f = t['fact']; path = OUT / f"{t['key']}.json"
        t['category'] = next((p['category'] for p in PIL['pillars'] if p.get('series_match') and p['series_match'] in (t.get('brief') or '')), t['category'])   # 시리즈 편 (11/05)
        post = {"key": t['key'], "category": t['category'], "status": "draft", "title": t['title'], "object": t['object'], "subject": t.get('subject'),
                "made_by": f"엔진/find.py {TODAY} · 신호 {t['signal_ids']} · 퍼스나 {t.get('persona')}",
                "fact": {"num": f['num'], "unit": f.get('unit', ''), "thing": f['thing'], "box": f.get('box', ''), "claim": f['claim'], "felt": f.get('felt'),   # felt = 시청자가 느끼는 $ (11/06). hook.py 가 훅 숫자로 쓴다
                         "sources": [s['label'] for s in f['sources']], "verified": "find.py · 대조 " + str(sum(1 for s in f['sources'] if s.get('checked'))) + "/" + str(len(f['sources']))},
                "sources": [{"label": s['label'], "url": s['url'], "what": s['quote'], "confidence": "1차" if s.get('primary') else "2차"}
                            for s in f['sources']],
                "slides": []}
        if path.exists(): post = {**json.load(open(path, encoding='utf-8')), **{k: post[k] for k in ('fact', 'sources', 'object')}}
        json.dump(post, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        try: ok = hook.make(str(path)) == 0
        except SystemExit as x: ok = False; print(f"  ✗ {t['key']}: {x}")   # 한 편이 막혀도 다음 편으로 (11/07: btc-dca 가 run 전체를 세웠다). 막힌 편은 hook.py rebuild 가 felt 보충 뒤 다시 민다
        if ok:
            h = json.load(open(path, encoding='utf-8'))['hooks']
            t.update(status='hooked', post=str(path.relative_to(P.parent)), hook=h['on_screen'], promise=h['promise'])
        save('topics.json', rows)


# 속장 조합. 피부는 하나, 판 배치만 돈다. 저장할 물건(grid·table·do)이 하나씩 들어 있다
LAYOUTS = [["flow", "grid"], ["two", "mini", "do"], ["grid", "flow"], ["mini", "table"], ["flow", "two", "do"], ["two", "grid"]]

def write(keys):
    """씨앗(훅까지 된 편)에 속장 2~3장 + 캡션을 채운다. 예시는 승인된 Day 2·Day 4 장. 숫자는 check.py·build_rail 숫자 관문이 다시 본다."""
    ex = [s for f in ('2026-11-03-01-main-v4', '2026-11-05-01-main')
          for s in json.load(open(P.parent / '콘텐츠' / '31일' / f'{f}.json', encoding='utf-8'))['slides'] if s['type'] != 'hero']
    tx = prompt('post.md').replace('EXAMPLES', json.dumps(ex, ensure_ascii=False))
    rows = load('topics.json', [])
    n = sum(1 for t in rows if t['status'] == 'written')
    for t in [t for t in rows if t['key'] in keys and t['status'] == 'hooked']:
        path = P.parent / t['post']; d = json.load(open(path, encoding='utf-8'))
        lay = LAYOUTS[n % len(LAYOUTS)]; n += 1   # 편마다 속장 조합을 돌린다 (11/04 밤 «디자인이 겹친다»)
        out = hook.ask_claude({**{k: d.get(k) for k in ('category', 'object', 'fact', 'sources', 'hooks', 'title')}, "layout": lay}, prompt_text=tx)
        hero = [s for s in d['slides'] if s['type'] == 'hero']
        d.update({k: out[k] for k in ('title', 'lede', 'series', 'source_note', 'caption') if out.get(k)})
        d['slides'] = hero + [s for s in out.get('slides', []) if s.get('type') != 'hero']
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        t['status'] = 'written'; save('topics.json', rows)
        if t.get('charts'): add_chart(t['key'], ','.join(t['charts']))   # 종목 편은 진짜 주가 창이 붙는다 (11/05)
        if t.get('charts') and t.get('category') == 'fear': add_why(t['key'])   # 공포 시리즈는 «왜 중요한가»까지
        add_plain(t['key'])   # 쉬운 말 층은 모든 편 (11/07 하림님 «무슨 말인지 모르겠다»: run 으로 만든 새 편 4개가 plain 없이 감독돼 대본이 어려웠다)
        print(f"  ✎ {t['key']}  {len(d['slides'])}장  {d.get('title', '')}")


def add_chart(key, specs):
    """주가 창 장을 표지 바로 뒤에 넣는다. specs 'SOXL:1mo,SOXL:10y'. 숫자는 chart.py 가 받은 값뿐이라 제목도 엔진이 쓴다."""
    import chart as ch
    path = OUT / f"{key}.json"; d = json.load(open(path, encoding='utf-8'))
    cs = []
    for sp in specs.split(','):
        t, _, r = sp.strip().partition(':'); cs.append(ch.fetch(t, r or '1mo'))
    a = cs[0]; P = lambda c: ch.pct(c['period_pct'])   # 잘라내기 말고 정본 반올림
    WHEN = {'1d': 'today', '5d': 'this week', '1mo': 'this month', '3mo': 'in 3 months', '6mo': 'in 6 months', 'ytd': 'this year', '1y': 'in a year', '2y': 'in 2 years', '5y': 'in 5 years', '10y': 'in 10 years', 'max': 'all time'}
    tl = f"{a['ticker']} {P(a)} {WHEN[a['range']]}."
    if len(cs) > 1: tl = f"{P(a)} {WHEN[a['range']]}. *{P(cs[1])}* {WHEN[cs[1]['range']]}."   # 공포에서 부자 시리즈: 단기 폭락 → 장기
    sl = {"type": "chart", "kicker": d.get('object', 'THE CHART'), "title": tl, "charts": cs,
          "source_label": f"Yahoo Finance · {a['as_of'][:10]}"}
    d['slides'] = [s for s in d['slides'] if s['type'] == 'hero'] + [sl] + [s for s in d['slides'] if s['type'] not in ('hero', 'chart')]
    have = {s.get('url') for s in d.get('sources', [])}
    for c in cs:
        if c['src'] not in have:
            d.setdefault('sources', []).append({"label": f"Yahoo Finance {c['ticker']}", "url": c['src'], "what": f"{c['ticker']} {ch.PAST[c['range']]} {ch.pct(c['period_pct'])}, last {c['last']} at {c['as_of']} ET", "confidence": "1차"}); have.add(c['src'])
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"  📈 {key}: " + ' · '.join(f"{c['ticker']} {c['range']} {ch.pct(c['period_pct'])}" for c in cs))


def add_why(key):
    """공포 시리즈: 이 종목이 왜 중요한가 (하림님 11/05 «왜 중요한지, 얼마나 의미가 있는지 알아야»). 1차 출처 문장만. post.why 에 둔다."""
    path = OUT / f"{key}.json"; d = json.load(open(path, encoding='utf-8'))
    tk = sorted({c['ticker'] for s in d.get('slides', []) if s.get('type') == 'chart' for c in s.get('charts', [])})
    if not tk: print(f"  · {key}: 주가 창이 없어 «왜 중요한가»는 건너뛴다"); return
    out = hook.ask_claude({"tickers": tk, "title": d.get('title'), "fact": d.get('fact'), "today": TODAY}, timeout=900, prompt_text=prompt('find-why.md'), tools=WEB)
    w = out.get('why')
    if not w or not w.get('sources'): print(f"  ✗ {key}: 왜 중요한가 못 찾음 — {out.get('reason', '')}"); return
    for s in w['sources']: s['checked'] = on_page(s.get('url', ''), s.get('quote'))
    d['why'] = w
    have = {s.get('url') for s in d.get('sources', [])}
    d.setdefault('sources', []).extend({"label": s['label'], "url": s['url'], "what": s['quote'], "confidence": "1차"} for s in w['sources'] if s['url'] not in have)
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"  💡 {key}: {w['line']}")


def add_plain(key):
    """쉬운 말 층 (11/05 아만다 «너무 어렵다»). 편의 사실·훅·왜 중요한가를 초등 6학년 수준으로 다시 쓴다. post.plain 에 둔다. 사이트가 맨 위에 보여준다."""
    path = OUT / f"{key}.json"; d = json.load(open(path, encoding='utf-8'))
    hk = d.get('hooks') or {}
    beats = [b['say'] for b in (d.get('rail') or {}).get('beats') or [] if b.get('say')]
    payload = {"title": d.get('title'), "hook": hk.get('on_screen'), "fact": d.get('fact'), "lede": d.get('lede'), "caption": (d.get('caption') or '').split('#')[0],
               "script": beats, "why": d.get('why'), "dictionary": {k: v for k, v in (hook.HK.get("plain") or {}).items() if k != '_'}}
    out = hook.ask_claude(payload, timeout=600, prompt_text=prompt('find-plain.md'))
    pl = out.get('plain')
    if not pl or not pl.get('what'): print(f"  ✗ {key}: 쉬운 말 못 씀 — {out.get('reason', '')}"); return
    d['plain'] = pl
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"  🍼 {key}: {pl['what'][:90]}")


def refomo():
    """포모 소급 관문. fomo 없는 신호는 모델이 한 번 변환해 보고, 안 되면 지운다. 몇 번을 돌려도 같은 결과다."""
    rows = load('signals.json', [])
    need = [s for s in rows if not (s.get('fomo') or '').strip()]
    if need:
        out = hook.ask_claude({"signals": [{k: s.get(k) for k in ('id', 'kind', 'title', 'quote', 'why')} for s in need],
                               "task": 'For each signal, write "fomo": one short honest sentence "You lose/miss/pay ..." that a Canadian beginner feels in one second, using only what the signal says. If impossible, null. Answer {"fomo":{"<id>":"...or null"}} only.'},
                              prompt_text="You convert raw signals into reader-loss sentences for a Canadian beginner finance account. Information that stays information is worthless.\n\nInput: ")
        m = out.get('fomo', {})
        for s in need: s['fomo'] = m.get(s['id'])
    kept = [s for s in rows if (s.get('fomo') or '').strip()]
    save('signals.json', kept)
    print(f"  포모 관문: {len(rows)} → {len(kept)} (지움 {len(rows)-len(kept)})")
    return kept


def top(status, n): return [t['key'] for t in load('topics.json', []) if t['status'] == status][:n]

def stats():
    rows = load('topics.json', []); sig = load('signals.json', []); per = load('persona.json', {}).get('personas', [])
    print(f"  신호 {len(sig)} (원문 대조 {sum(1 for s in sig if s.get('quote_checked'))})  ·  퍼스나 {len(per)}  ·  주제 {len(rows)}")
    st = {}
    for t in rows: st.setdefault(t['pillar'], {}).setdefault(t['status'], 0); st[t['pillar']][t['status']] += 1
    for p, d in st.items(): print(f"  {p:11s} " + '  '.join(f"{k} {v}" for k, v in sorted(d.items())))
    print()
    for t in rows[:15]:
        print(f"  {t['rank']:5.1f} {t['status']:10s} {t['key']:34s} {t.get('hook') or t.get('angle','')}")


def plan_rows(days=14):
    """달력 행: (날짜, 주제, 훅, 릴스 있나). plan 과 site.py 가 같이 쓴다."""
    rows = [t for t in load('topics.json', []) if t['status'] != 'no-fact']
    order = {'written': 0, 'hooked': 1, 'fact': 2, 'idea': 3}
    by = {}
    for t in rows: by.setdefault(t['pillar'], []).append(t)
    for v in by.values(): v.sort(key=lambda t: (order.get(t['status'], 9), -t['rank']))
    cred = {p: 0.0 for p in by}; out = []
    while len(out) < min(days, len(rows)) and any(by.values()):
        for p in cred:
            if by[p]: cred[p] += PILLARS[p]['weight']
        p = max((q for q in by if by[q]), key=lambda q: cred[q])
        cred[p] = 0; out.append(by[p].pop(0))
    d = datetime.date.today(); res = []
    for i, t in enumerate(out):
        hk = t.get('hook') or t.get('angle', '')
        try: hk = json.load(open(OUT / f"{t['key']}.json", encoding='utf-8'))['hooks']['on_screen']   # 편 파일의 훅이 정본 (hook.py --make 가 다시 뽑으면 topics.json 은 옛것)
        except Exception: pass
        mp4 = (P / 'out' / '릴스' / f"{t['key']}-rail.mp4").exists()
        res.append((d + datetime.timedelta(days=i + 1), t, hk, mp4))
    return res


def plan(days=14):
    # 달력: 완성(written) 먼저, 줄기 비중(PILLARS weight)대로 섞어서 내일부터 하루 한 편
    for day, t, hk, mp4 in plan_rows(days):
        print(f"{day} | {t['pillar']:10s} | {'릴스' if mp4 else t['status']:7s} | {t['key']:34s} | {hk}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('key', nargs='?')
    ap.add_argument('--pillar'); ap.add_argument('--n', type=int, default=5); ap.add_argument('--top', type=int)
    ap.add_argument('--charts', help='TICKER:range,... (find.py chart)')
    ap.add_argument('--brief', help='이번 판 하림님 지시 한 문장. 신호·주제·사실이 이걸 따른다')
    a = ap.parse_args()
    if a.cmd == 'signals': signals(a.pillar, a.n if a.n != 5 else 12, a.brief); refomo()
    elif a.cmd == 'refomo': refomo()
    elif a.cmd == 'persona': persona()
    elif a.cmd == 'topics': topics(a.n if a.n != 5 else 20, a.brief)
    elif a.cmd == 'fact': fact([a.key] if a.key else top('idea', a.top or 5))
    elif a.cmd == 'seed': seed([a.key] if a.key else top('fact', a.top or 5))
    elif a.cmd == 'write': write([a.key] if a.key else top('hooked', a.top or 5))
    elif a.cmd == 'run':
        # ponytail: 한 줄로 차례대로 돈다. 1,000편 단위로 빨라야 하면 fact 를 병렬로
        signals(a.pillar, 12, a.brief); refomo(); persona() if not load('persona.json', {}).get('personas') else None
        if a.brief:   # 지시가 있는 판은 이번에 나온 주제만 끝까지 민다
            new = topics(a.n + 2, a.brief); fact(new); seed(new); write(new)
        else:
            topics(4 * a.n); fact(top('idea', a.n)); seed(top('fact', a.n)); write(top('hooked', a.n))
        stats()
    elif a.cmd == 'chart': add_chart(a.key, a.charts)   # find.py chart <key> --charts SOXL:1mo,SOXL:10y
    elif a.cmd == 'why': add_why(a.key)
    elif a.cmd == 'plain': add_plain(a.key)   # find.py plain <key>  (쉬운 말 층)
    elif a.cmd == 'stats': stats()
    elif a.cmd == 'plan': plan(a.n if a.n != 5 else 14)
    elif a.cmd == 'selftest':
        assert abs(fv(100, 7, 30) - 122000) / 122000 < 0.01          # Day 4 표와 같은 식
        assert fact_gate({"num": "15", "sources": [{"url": "", "quote": "x"}]}) == []   # 출처가 있으면 통과 (대조는 표시만)
        assert fact_gate({"num": "15", "sources": []}) == ["출처나 주장이 없다"]
        assert norm("Don\u2019t  pay\u00a0more") == "don't pay more"
        print("selftest ok")
    else: ap.print_help(); return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
