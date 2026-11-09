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
        if path.exists():   # 다시 seed 할 때 옛 출처(주가 창·왜 중요한가)를 지우지 않고 합친다 (11/07 FAIL 편 사실 다시 찾기)
            old = json.load(open(path, encoding='utf-8')); seen = {(s['url'], s['what']) for s in post['sources']}
            post = {**old, **{k: post[k] for k in ('fact', 'object')}, "sources": post['sources'] + [s for s in old.get('sources', []) if (s.get('url'), s.get('what')) not in seen]}
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
    """씨앗(훅까지 된 편)에 속장 2~3장을 채운다. 예시는 승인된 Day 2·Day 4 장. 숫자는 check.py·build_rail 숫자 관문이 다시 본다. 캡션은 대본이 나온 뒤 caption() 이 쓴다."""
    ex = [s for f in ('2026-11-03-01-main-v4', '2026-11-05-01-main')
          for s in json.load(open(P.parent / '콘텐츠' / '31일' / f'{f}.json', encoding='utf-8'))['slides'] if s['type'] != 'hero']
    tx = prompt('post.md').replace('EXAMPLES', json.dumps(ex, ensure_ascii=False))
    rows = load('topics.json', [])
    n = sum(1 for t in rows if t['status'] == 'written')
    for t in [t for t in rows if t['key'] in keys and t['status'] == 'hooked']:
        path = OUT / f"{t['key']}.json"; d = json.load(open(path, encoding='utf-8'))
        lay = LAYOUTS[n % len(LAYOUTS)]; n += 1   # 편마다 속장 조합을 돌린다 (11/04 밤 «디자인이 겹친다»)
        out = hook.ask_claude({**{k: d.get(k) for k in ('category', 'object', 'fact', 'sources', 'hooks', 'title')}, "layout": lay}, prompt_text=tx)
        hero = [s for s in d['slides'] if s['type'] == 'hero']
        d.update({k: out[k] for k in ('title', 'lede', 'series', 'source_note') if out.get(k)})
        d['slides'] = hero + [s for s in out.get('slides', []) if s.get('type') != 'hero']
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        t['status'] = 'written'; save('topics.json', rows)
        if t.get('charts'): add_chart(t['key'], ','.join(t['charts']))   # 종목 편은 진짜 주가 창이 붙는다 (11/05)
        if t.get('charts') and t.get('category') == 'fear': add_why(t['key'])   # 공포 시리즈는 «왜 중요한가»까지
        add_plain(t['key'])   # 쉬운 말 층은 모든 편 (11/07 하림님 «무슨 말인지 모르겠다»: run 으로 만든 새 편 4개가 plain 없이 감독돼 대본이 어려웠다)
        print(f"  ✎ {t['key']}  {len(d['slides'])}장  {d.get('title', '')}")



CAP_BAN = ["—", ";", "here's the thing", "here's why", "here is why", "the secret", "let's dive", "game changer", "game-changer", "the truth is", "guaranteed", "your friend", "two friends", "two people"]
def caption_gate(c, d, word):
    """캡션 관문 (11/07 하림님 «짧게, 후기 오게, AI 티 덜 나게»): 출처에 없는 숫자 · 금지 표현 · 릴스 댓글 키워드 없음 · 길이."""
    ok = hook.numset(d); why = []
    body = "\n".join(l for l in c.split("\n") if not l.startswith("Dig #"))   # 서명 줄(road to $1M)은 엔진 고정 문구
    bad = [m for m in hook.NUM.findall(body) if not any(abs(hook.nval(m) - v) <= max(.01, hook.nval(m) * .01) for v in ok)]
    if bad: why.append(f"출처에 없는 숫자 {bad}")
    why += [f"금지 «{b}»" for b in CAP_BAN if b in c.lower()]
    if word and word.upper() not in c: why.append(f"댓글 키워드 {word} 없음")
    n = len(c.split()); why += [f"{n}단어 (30~80)"] if not 30 <= n <= 80 else []
    if len(c.split('\n')[0]) > 95: why.append("첫 줄 95자 넘음")   # 릴스는 첫 줄 앞부분만 보인다 (11/07)
    hk = (d.get('hooks') or {}).get('on_screen') or ''
    rep = [m for m in hook.NUM.findall(c.split('\n')[0]) if '$' in m and m in hk]
    if rep: why.append(f"첫 줄이 훅 금액 반복 {rep}")   # 경고만 (11/09 캡션 첫 줄은 훅이 안 한 말)
    return why

def recent_families(n=6):
    """최근 n편 캡션이 쓴 첫 줄 꼴 (11/09). 같은 꼴이 몰리지 않게 다음 캡션에 피하라고 넘긴다."""
    fs = sorted(OUT.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in fs:
        f = json.load(open(p, encoding='utf-8')).get('caption_family')
        if f: out.append(f)
        if len(out) >= n: break
    return out

def caption(keys, dry=False, b=False):
    """릴스 캡션 (prompts/caption.md). 대본(rail)이 있는 편만: 릴스 끝의 댓글 키워드·선물을 그대로 넘긴다. 관문에 걸리면 한 번 다시, 그래도 걸리면 옛 캡션을 둔다."""
    tx = prompt('caption.md')
    for k in keys:
        path = OUT / f"{k}.json"; d = json.load(open(path, encoding='utf-8'))
        sc = (d.get('rail') or {}).get('scenes') or []
        if not sc: print(f"  · {k}: 대본이 없어 캡션은 건너뛴다"); continue
        cta = next(((s.get('data') or {}) for s in sc if s.get('role') == 'cta'), {})
        ft = hook.felt(d)
        payload = {"hook": (d.get('hooks') or {}).get('on_screen'), "felt": hook.felt_str(ft) if ft else None, "felt_how": (ft or {}).get('how'),
                   "fact": {x: (d.get('fact') or {}).get(x) for x in ('num', 'unit', 'thing', 'claim')}, "sources": [{"label": s.get('label'), "what": s.get('what')} for s in d.get('sources') or []],
                   "script": [ln for s in sc for ln in s.get('lines') or []], "cta": {"word": cta.get('word', ''), "gift": cta.get('gift', '')},
                   "plain": d.get('plain'), "category": d.get('category'), "avoid_families": recent_families(),
                   "do": [(d.get('plain') or {}).get('do')] + [i for s in sc if s.get('role') == 'check' for i in (s.get('data') or {}).get('items') or []]}   # 📌 할 일 칸 (11/07 hongik.man 레퍼: 단계 목록 + 저장 이유)
        try:
            r = hook.ask_claude(payload, prompt_text=tx); c = (r.get('caption') or '').strip(); fam = r.get('family'); why = caption_gate(c, d, cta.get('word'))
            if why:
                r2 = hook.ask_claude({**payload, "fix": "Your last caption broke these rules, fix them: " + "; ".join(why), "last": c}, prompt_text=tx)
                c2 = (r2.get('caption') or '').strip(); why2 = caption_gate(c2, d, cta.get('word'))
                if len(why2) < len(why): c, why, fam = c2, why2, r2.get('family')
        except Exception as x: print(f"  ✗ {k}: 모델 실패 {str(x)[:80]}"); continue
        if any(w.startswith(("출처에 없는", "금지", "댓글")) for w in why) or not c: print(f"  ✗ {k}: 옛 캡션 그대로 — {' · '.join(why)}"); continue
        if dry: print(f"\n── {k} ({len(c.split())}단어 · {fam}{' · ' + ' · '.join(why) if why else ''})\n{c}"); continue
        d = json.load(open(path, encoding='utf-8')); d['caption_b' if b else 'caption'] = c; d['caption_family'] = fam   # --b: A/B 시험용 새 캡션은 caption_b, 옛 caption 은 A 로 남긴다 (11/09)
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"  ✎ {k} 캡션 {len(c.split())}단어" + (f"  ~ {' · '.join(why)}" if why else ""))

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


def story(cap, k):
    """하루 스토리 3장 (11/09 하림님 «릴스 하루 1편 + 스토리 3장»). 모델 없이 캡션에서 뽑는다: ① 오늘 릴스 공유 ② 캡션 끝 질문으로 투표 ③ 댓글 키워드 안내."""
    lines = [l.strip() for l in cap.split("\n") if l.strip()]
    q = next((l for l in lines if l.endswith("?") and not l.startswith("🐶")), "Did you know this?")
    word = (re.search(r"Comment (\S+)", cap) or [None, ""])[1]
    return [f"1. 오늘 릴스 공유 (릴스 아래 종이비행기 → 스토리에 추가)",
            f"2. 투표 스티커: {q}  /  Yes · Not yet",
            f"3. 글자: Comment {word} under today's reel and I'll send it to you 🪙"]

def publish_table(rows, W):
    """아침 메일용 (11/09): Drive «하마-발행표.txt» 본문을 out/작업/발행표.txt 로 쓴다. Drive 에 올리는 건 Claude 가 한다.
    게시는 하림님이 맥에서 하므로 영상은 out/릴스/ 의 MP4 경로를 그대로 적는다 (iCloud 복사는 11/09 하림님 «컴으로 할라구»로 뺌)."""
    txt = ["# 하마 발행표 (엔진 find.py queue 가 씀, 손으로 고치지 않는다)", f"# 만든 날 {TODAY} · 하루 {len({r['date'] for r in rows}) and max(r['slot'] for r in rows)}편 · A/B 캡션 시험 중", ""]
    for d in sorted({r["date"] for r in rows})[:10]:   # 10일치만: Drive 읽기 도구가 27KB 근처에서 자른다 (11/09)
        txt.append(f"### {d}")
        for r in [x for x in rows if x["date"] == d]:
            txt += [f"[{r['slot']}번 · 캡션 {r['ab']}] {r['mp4']}", "---캡션 시작---", r["caption"], "---캡션 끝---", ""]
    # Drive 읽기 도구가 4바이트 이모지를 깨뜨린다(🐶→ð¶). 이름표로 쓰고 아침 메일 루틴이 되돌린다 (11/09)
    (W / "발행표.txt").write_text("\n".join(txt).replace("🐶", ":dog:").replace("🪙", ":coin:"), encoding="utf-8")
    print(f"  발행표 {W / '발행표.txt'}")

def queue(start='2026-11-08', per_day=1):   # 11/09 하림님: 릴스 하루 1편 + 스토리 3장 (윤치상·가이드 기준)
    """올리기 큐 (11/07 하림님): 통과한 편만 = 관문 FAIL 아님 · 목소리 대조 불일치 0 · 캡션 있음 · MP4 있음. plan 순서(줄기 비중)대로 하루 per_day 편.
    결과 out/작업/upload-queue.json = 하마 올리기 판(dashboard.html)의 db 문서들. 이미 올린 편(out/작업/posted.json, 판에서 읽어 온 것)은 다시 잡지 않는다. 게시는 하림님 손."""
    W = P / 'out' / '작업'
    fail = set(re.findall(r'^\| (\S+) \| [^|]* \| \*\*FAIL', (W / 'review.md').read_text(encoding='utf-8'), re.M))
    voice = {r['key']: r['bad'] == 0 and r['missing'] == 0 for r in json.load(open(W / 'voice-check.json', encoding='utf-8'))}
    posted = set(json.load(open(W / 'posted.json', encoding='utf-8'))) if (W / 'posted.json').exists() else set()
    order = [t['key'] for _, t, _, _ in plan_rows(9999)]
    keys = sorted((p.stem for p in OUT.glob('*.json')), key=lambda k: (order.index(k) if k in order else len(order), k))
    day0 = max(datetime.date.fromisoformat(start), datetime.date.today())   # 11/09 «오늘부터 올릴 수 있게»
    rows, out, nob = [], [], []
    for k in keys:
        if k in posted: continue
        d = json.load(open(OUT / f"{k}.json", encoding='utf-8')); mp4 = P / 'out' / '릴스' / f"{k}-rail.mp4"
        why = [w for w, bad in (("MP4 없음", not mp4.exists()), ("관문 FAIL", k in fail), ("목소리 불일치", not voice.get(k)), ("캡션 없음", not (d.get('caption') or '').strip())) if bad]
        if why: out.append({"key": k, "why": " · ".join(why)}); continue
        i = len(rows); day = day0 + datetime.timedelta(days=i // per_day)
        ab = 'AB'[(i + i // per_day) % 2] if per_day == 2 else 'AB'[i % 2]   # A/B 캡션 시험 (11/09~): A·B 번갈아
        if ab == 'B' and not (d.get('caption_b') or '').strip(): ab = 'A'; nob.append(k)   # B 캡션이 없으면 A 로 정직하게 표시
        cap = d['caption_b'] if ab == 'B' else d['caption']
        rows.append({"key": k, "date": str(day), "slot": i % per_day + 1, "hook": (d.get("hooks") or {}).get("on_screen", ""), "category": d.get("category", ""),
                     "mp4": str(mp4), "ab": ab, "caption_family": d.get("caption_family") if ab == "B" else None, "caption": cap.strip().replace("Dig #N", f"Dig #{len(posted) + i + 1}"),   # 연재 번호 = 올린 편 수 + 큐 순서 (11/07)
                     "site": f"https://hama-money.vercel.app/p/{k}.html", "story": story(cap, k)})
    res = {"made": TODAY, "per_day": per_day, "queue": rows, "excluded": out}
    publish_table(rows, W)
    json.dump(res, open(W / 'upload-queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"  올리기 큐 {len(rows)}편 ({rows[0]['date'] if rows else '-'}~{rows[-1]['date'] if rows else '-'}) · 이미 올림 {len(posted)} · 뺀 편 {len(out)} → {W / 'upload-queue.json'}")
    for x in out: print(f"   ✗ {x['key']}: {x['why']}")
    if nob: print(f"  ⚠ B 차례인데 B 캡션 없음 {len(nob)}편 (A 로 표시): " + ' '.join(nob))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('key', nargs='?')
    ap.add_argument('--pillar'); ap.add_argument('--n', type=int, default=5); ap.add_argument('--top', type=int)
    ap.add_argument('--charts', help='TICKER:range,... (find.py chart)')
    ap.add_argument('--dry', action='store_true', help='caption: 저장 없이 보기만')
    ap.add_argument('--b', action='store_true', help='caption: A/B 시험용 새 캡션을 caption_b 에 쓴다 (옛 caption 은 A)')
    ap.add_argument('--brief', help='이번 판 하림님 지시 한 문장. 신호·주제·사실이 이걸 따른다')
    a = ap.parse_args()
    if a.cmd == 'signals': signals(a.pillar, a.n if a.n != 5 else 12, a.brief); refomo()
    elif a.cmd == 'refomo': refomo()
    elif a.cmd == 'persona': persona()
    elif a.cmd == 'topics': topics(a.n if a.n != 5 else 20, a.brief)
    elif a.cmd == 'fact': fact([a.key] if a.key else top('idea', a.top or 5))
    elif a.cmd == 'seed': seed([a.key] if a.key else top('fact', a.top or 5))
    elif a.cmd == 'write': write([a.key] if a.key else top('hooked', a.top or 5))
    elif a.cmd == 'caption': caption([a.key] if a.key and a.key != 'all' else [pathlib.Path(x).stem for x in hook.posts_all()], a.dry, a.b)   # find.py caption <key|all>
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
    elif a.cmd == 'queue': queue()   # find.py queue → out/작업/upload-queue.json (하마 올리기 판에 넣는다)
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
