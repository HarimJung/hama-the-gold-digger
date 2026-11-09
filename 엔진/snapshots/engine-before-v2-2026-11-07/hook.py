#!/usr/bin/env python3
"""훅 엔진. 손으로 쓰지 않는다 — 사실 하나를 넣으면 대제목·소제목·훅이 나오고, 고른 것은 원장에 쌓인다.

흐름 (SDG hook_review.py 방식)
  1 대제목  hooks.json series.title[category]. 고정. 지어내지 않는다
  2 생성    prompts/hook.md + 사실 → claude -p → 후보 10 (헨리 10방식) + 모델 자체 점수 + 추천
  3 관문    F-관문 (숫자·대상·이득/손해 말·답 노출·단어 수·금지 기호) + P-관문 (② 약속 줄) — 결정론. 모델 점수와 별개
  4 점수    hookscore (하한선이지 합격증이 아니다)
  5 기록    post.json 의 hooks 블록과 hero 장에 써 넣고, hooks-ledger.json 에 쌓는다
  6 한 바퀴 이 엔진이 쓴 소제목을 그대로 쓰면 통과다. 검사기가 자기 제안을 또 고치라고 하면 끝이 없다

훅 공식 (11/06 하림님 확정): 한 문장 12단어 = [이름, 앞 3단어] + [잃은 것 $ = fact.felt] + [얻는 것 질문]. 정본 hooks.json one_second.
FAIL 은 넷뿐: 지어낸 숫자 · 매수/매도 콜 · 이름 없음 · 훅에 felt $ 없음. 나머지는 «~» 경고.

사용
  python3 엔진/hook.py --make 콘텐츠/찾은/<post>.json        # 사실 → 후보 → 관문 → post.json 에 써 넣고 원장
  python3 엔진/hook.py --make <post>.json --dry              # 써 넣지 않고 보기만
  python3 엔진/hook.py felt <post>.json | --all [--force]    # subject + fact.felt 채우기 (모델 한 번, 관문은 결정론). 새 편은 find.py 가 채운다
  python3 엔진/hook.py stamp --all                          # hooks.stamp (포모 명령 도장) 한 번의 호출로 채우기
  python3 엔진/hook.py audit [--all | <post>...]              # 47편 관문 표 → out/작업/hook-audit.md
  python3 엔진/hook.py rehook --all [--render]               # FAIL 편만: 훅 새로 → 첫 두 비트·첫 장면만 교체 → 레일 다시 (대본 나머지는 그대로)
  python3 엔진/hook.py rebuild --all [--direct] [--no-render]  # 4단계 한 명령: felt → 훅 관문 → (대본 새로) → remap → 레일 → MP4 out/릴스/
  python3 엔진/hook.py sheet [--all]                         # 첫 장면 1.2초 프레임 47장 대지 → out/작업/hook-sheet.png
  python3 엔진/hook.py --result <post-stem> saves=120 shares=40
  python3 엔진/hook.py --stats

post.json 에 필요한 것: category, object, subject, fact{num, unit, thing, box, claim, felt{num, unit, a?, b?, how}}
"""
import argparse, datetime, json, pathlib, re, subprocess, sys, tempfile

P = pathlib.Path(__file__).parent
HK = json.load(open(P / 'hooks.json', encoding='utf-8'))
CF = HK['cover']; PR = HK['promise']; SERIES = HK['series']['title']; MODES = HK['henry']['modes']
LEDGER = P / 'hooks-ledger.json'
PROMPT = (P / 'prompts/hook.md').read_text(encoding='utf-8')
SCORER = P.parent / '하마-제작실/sources/instagram-agent/skills/ig-reel'
BANNED = ['—', ';', '→', '←', '➡', 'not just', "here's why", 'here is why', 'the secret']

# 결정론 씨앗 — claude -p 가 없을 때의 뼈대. 완성품이 아니다
SEEDS = {
    "숫자":      "{N}{U} of your {thing}, gone every time.",
    "질문":      "Which of your boxes keeps all {N}{U}?",
    "흔한 실수": "Your {thing} in the wrong box costs {N}{U}.",
    "반전":      "Your safest box loses {N}{U}.",
    "경험":      "Hama lost {N}{U} of your-kind {thing} here.",
    "손해":      "You lose {N}{U} of {thing} at the border.",
    "이름":      "One list. Your box is not on it. {N}{U} gone.",
    "비교":      "Same {thing}, two boxes, {N}{U} apart.",
    "시간":      "Your {thing} lose {N}{U} since day one.",
    "금지":      "Never park {thing} where you lose {N}{U}.",
}


def words(s): return [w for w in re.sub(r'[^\w$%€£.\-\' ]', ' ', s or '').split() if w]


def subject(d):
    """첫 화면 대상 이름. post.subject (find.py · hook.py felt 가 채운다) → why.ticker → 주가 창 티커. hooks.json names 로 초보 말로.
    11/06: 이전 훅에서 거꾸로 뽑던 줄은 지웠다 (레드팀 발견 9: 첫 편은 검사가 없고 흐린 이름이 통과했다)."""
    nm = HK.get('names', {})
    t = d.get('subject') or (d.get('why') or {}).get('ticker') or next((c['ticker'] for s in d.get('slides', []) if s.get('type') == 'chart' for c in s.get('charts', [])), None)
    if t: t = re.sub(r"\.(TO|V|NE|CN)$", "", t)   # Yahoo 접미사는 화면에 안 쓴다 (11/05 XEQT.TO)
    if d.get('category') in ('etf', 'stocks'): return t   # ETF·주식 편은 티커 그대로 (VFV 를 «the S&P 500» 으로 바꾸지 않는다)
    return nm.get(t, t) if t else None


# ── 숫자의 정본 (11/06 레드팀 발견 2·3·10) ──────────────────────────
NUM = re.compile(r"[-−]?\$\d[\d,]*(?:\.\d+)?k?|[-−]?\d+(?:\.\d+)?%")
def nval(t):
    k = t.endswith('k'); t = t.replace('−', '-').strip('-$%k').replace(',', '')
    return float(t) * (1000 if k else 1)

def numset(d, with_felt=True):
    """편이 증명한 숫자 집합: fact·slides·sources·why 의 $·% 토큰 + fact.num + 출처 인용의 맨 숫자 + 증명된 felt(a−b 계산값). 모델 산출물(hooks·rail·caption·plain)은 안 센다 — 순환."""
    core = {k: (d.get(k) if k != 'fact' else {x: v for x, v in (d.get('fact') or {}).items() if x != 'felt'}) for k in ('fact', 'slides', 'sources', 'why')}
    s = {nval(m) for m in NUM.findall(json.dumps(core, ensure_ascii=False))}
    f = d.get('fact') or {}
    for x in [f.get('num')] + [v for v in (f.get('calc') or {}).values()]:
        try: s.add(abs(float(str(x).replace(',', ''))))
        except (TypeError, ValueError): pass
    for src in d.get('sources') or []:
        for m in re.findall(r'\d[\d,]*(?:\.\d+)?', src.get('what') or ''): s.add(nval(m))
    for sl in d.get('slides') or []:   # 주가 창의 값(last·hi·등락률)은 real_moves 로 대본에 간다
        for c in sl.get('charts') or []:
            for k in ('last', 'hi', 'period_pct'):
                if c.get(k) is not None: s.add(abs(float(c[k]))); s.add(abs(round(float(c[k]), 1)))
    s.add(0.0)   # $0 · 0% 는 지어낸 숫자가 아니다 (11/06)
    if with_felt:
        f = felt(d)
        if f: s.add(nval(felt_str(f)))   # 계산으로 증명된 차이 금액($1,000 − $423.50)도 대본에 쓸 수 있다
        if f and f.get('from') == 'calc_pct': s.add(float(f['base']))   # 예시 금액($10,000)도 대본에 쓸 수 있다
    return s

RATE = re.compile(r'\b(return|rate|yield|gross.?up|coupon|annualized|per year|a year|inclusion|share of|cap\b)', re.I)

def felt(d):
    """시청자가 느끼는 숫자 = fact.felt. 결정론 관문: num 이 numset 에 있거나, a·b 가 numset 에 있고 |a−b| 가 num 이다. 아니면 None (= 훅 못 만든다)."""
    f = (d.get('fact') or {}).get('felt')
    if not f or not f.get('num'): return None
    try: n = nval(str(f['num']))
    except ValueError: return None
    ok = numset(d, with_felt=False)
    if any(abs(n - v) <= max(1, n * .01) for v in ok): return f
    try:
        a, b = nval(str(f['a'])), nval(str(f['b']))
        if all(any(abs(x - v) <= max(1, x * .01) for v in ok) for x in (a, b)) and abs(abs(a - b) - n) <= max(1, n * .02): return f
    except (KeyError, TypeError, ValueError): pass
    if f.get('from') == 'calc_pct':   # % × 예시 금액 (11/06 «진행해»): pct 가 증명된 숫자고 base 가 예시($1,000·$10,000)면 그 곱도 증명된 숫자다
        try:
            pct, base = nval(str(f['pct'])), float(f['base'])
            if any(abs(pct - v) <= .01 for v in ok) and base in EXAMPLE_BASES and abs(pct * base / 100 - n) <= max(1, n * .02): return f
        except (KeyError, TypeError, ValueError): pass
    return None

EXAMPLE_BASES = (1000.0, 10000.0)   # 예시 금액: 수수료·세금 편 $1,000, 투자 편 $10,000
def felt_from_pct(d):
    """편에 $ 가 없고 fact 가 % 면: felt = fact.num% × 예시 금액. 결정론. hook.py felt 가 모델이 못 찾을 때 쓴다."""
    f = d.get('fact') or {}
    if f.get('unit') != '%': return None
    try: pct = float(str(f['num']).replace(',', ''))
    except (TypeError, ValueError): return None
    base = 10000.0 if d.get('category') in ('fear', 'stocks', 'etf', 'crypto', 'compound') else 1000.0
    n = pct * base / 100
    return {"num": f"{n:,.0f}" if n >= 10 else f"{n:,.2f}", "unit": "$", "pct": f['num'], "base": int(base), "how": f"{f['num']}% of a ${int(base):,} example", "from": "calc_pct"}

def felt_str(f):
    """«156,700» + «$» → «$156,700» · «37» + «%» → «37%»."""
    n = str(f['num']).lstrip('$').rstrip('%')
    try: n = f"{float(n.replace(',', '')):,.0f}" if float(n.replace(',', '')) >= 1000 and '.' not in n else n
    except ValueError: pass
    return ('$' + n) if f.get('unit', '$') == '$' else (n + f.get('unit', ''))

FELT_PROMPT = """You read one post of "Hama the Gold Digger" (Canadian beginners) and extract two fields. Answer JSON only.
- "subject": the name a beginner says in the first 3 words of the hook: the ticker, coin, fund, account or rule exactly as the post calls it (SOXL, Bitcoin, Your TFSA, World stocks, the CRA, Hama's 3-ETF mix). Never a vague word like "stocks" alone.
- "felt": the ONE dollar number the viewer feels: the money a person lost, missed or paid, or the gap between two choices (sold vs held, start at 25 vs 35, box A vs box B), on the example amount the post uses. Prefer a dollar gap or loss over an input rate (7.31%), an input ratio (138%) or a limit. Use only numbers that appear in fact, slides, sources or why. If the number is a gap, give "a" and "b" (both from the input) and num = the larger minus the smaller. Only when no dollar loss exists and the story is a pure price drop, felt may be that drop with unit "%". If the post has no dollar amount at all but has a %, make the viewer's dollars from an example: {"num":"200","unit":"$","pct":"2","base":10000,"how":"2% still owed on a $10,000 example","from":"calc_pct"} where pct is a % that appears in the input (the LOSS side: what is still owed, lost, or extra, never the % that is fine) and base is 10000 for investing posts or 1000 for fee and tax posts. If nothing fits, "felt": null and say why.
{"subject":"...","felt":{"num":"156,700","unit":"$","a":"286,500","b":"129,700","how":"start at 25 vs start at 35, at 65","from":"slides"},"why":"one line"}

Input: """

def backfill_felt(paths, force=False):
    """기존 편에 subject + fact.felt 를 채운다 (모델 한 번). 관문 felt() 가 결정론으로 거른다. 새 편은 find.py 가 처음부터 채운다."""
    n_ok = 0
    for path in paths:
        d = json.load(open(path, encoding='utf-8')); stem = pathlib.Path(path).stem
        if not force and d.get('subject') and felt(d): n_ok += 1; continue
        slim = [{k: v for k, v in s.items() if k not in ('charts', 'ts')} for s in d.get('slides', [])]
        try:
            out = ask_claude({"title": d.get('title'), "category": d.get('category'), "object": d.get('object'), "fact": d.get('fact'), "slides": slim,
                              "sources": [s.get('what') for s in d.get('sources') or []], "why": d.get('why'), "plain": d.get('plain'), "real_moves": real_moves(d)},
                             prompt_text=FELT_PROMPT)
        except Exception as x:
            print(f"  ✗ {stem}: 모델 실패 {str(x)[:80]}"); continue
        if out.get('subject'): d['subject'] = out['subject']
        d.setdefault('fact', {})['felt'] = out.get('felt')
        ok = felt(d)
        if not ok and out.get('felt'): print(f"  ~ {stem}: felt {out['felt'].get('num')} 가 fact·slides·sources·why 에 없다 — 버린다 ({out.get('why', '')[:60]})"); d['fact']['felt'] = None
        if not ok and felt_from_pct(d): d['fact']['felt'] = felt_from_pct(d); ok = felt(d); print(f"  · {stem}: % × 예시 금액 → {felt_str(ok) if ok else '—'}")
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(path, 'a', encoding='utf-8').write('\n')
        n_ok += bool(ok)
        print(f"  {'✓' if ok else '✗'} {stem:34s} {d.get('subject')!s:22s} {felt_str(ok) if ok else '—':>12s}  {(ok or {}).get('how', out.get('why', ''))[:60]}")
    print(f"  felt 있음 {n_ok}/{len(paths)}")

def real_moves(d):
    import chart as ch
    return [f"{c['ticker']} {c['range']} {ch.pct(c['period_pct'])}" + (f" (about {round(1 + c['period_pct'] / 100)} times your money)" if c['period_pct'] >= 1000 else "") + f", last ${c['last']:,.2f}, high in window ${c['hi']:,.2f}" for s in d.get('slides', []) if s.get('type') == 'chart' for c in s.get('charts', [])]

def hard_words(s):
    """쉬운 말 사전 왼쪽 말이 풀이 없이 나오면 그 말 목록 (11/05)."""
    low = (s or '').lower(); out = []
    for k, v in HK.get('plain', {}).items():
        if k == '_': continue
        ok = [v.lower()] + HK.get('plain_ok', {}).get(k, [])
        if re.search(r'(?<![\w-])' + re.escape(k.lower()) + r'(?![\w-])', low) and not any(o in low for o in ok): out.append(k)
    return out

def gates(sub, cat, subj=None, ft=None, fact=None, recent_tails=()):
    """훅 관문 (11/06 공식). 결정론이라 모델 점수와 섞이지 않는다.
    FAIL 은 넷뿐 (hooks.json one_second.fail): 지어낸 숫자 · 매수/매도 콜 · 이름 없음 · felt $ 없음. «~» 는 경고 — 후보를 떨어뜨리지 않는다."""
    bad = []; w = words(sub); low = (sub or '').lower()
    # ① 이름: 앞 3단어 안에 subject
    if subj:
        head = ' '.join(low.replace("’", "'").split()[:2 + len(subj.split())])
        if re.sub(r'^the ', '', subj.lower()) not in head: bad.append(f"F-1 이름 없음 ({subj} 가 앞 3단어에 없다)")
    else: bad.append("F-1 이름 없음 (post.subject 비어 있음 — hook.py felt)")
    # ② 잃은 것 $: felt 가 훅 안에
    nums = [nval(m) for m in NUM.findall(sub or '')]
    if ft:
        n = nval(str(ft['num']))
        if not any(abs(x - n) <= max(1, n * .01) for x in nums): bad.append(f"F-2 느끼는 숫자 없음 (felt {felt_str(ft)})")
    else: bad.append("F-2 felt 없음 (fact.felt 비어 있음 — hook.py felt)")
    if fact and nums and not ft:
        try:
            if any(abs(x - abs(float(str(fact.get('num')).replace(',', '')))) < 1e-6 for x in nums) and RATE.search(fact.get('thing', '')): bad.append("F-2 입력 수익률·비율이 훅 숫자다")
        except (TypeError, ValueError): pass
    if not nums: bad.append("F-2 $ 없음")
    # ③ 매수·매도 콜
    hitc = [c for c in CF.get('call_words', []) if re.search(r'(?<!\w)' + re.escape(c) + r'(?!\w)', low)]
    if hitc: bad.append(f"F-3 매수·매도 콜 {hitc}")
    hit = [a for a in CF['answer_words'] if a in low]
    if hit: bad.append(f"F-4 답 노출 {hit}")
    hitb = [b for b in BANNED if b in (sub or '')]
    if hitb: bad.append(f"F-4 금지 기호 {hitb}")
    if cat not in SERIES: bad.append(f"F-2 series 없음: {cat}")
    # 경고
    if len(w) > CF['hook']['max_words']: bad.append(f"~{len(w)}단어")
    if '?' not in (sub or ''): bad.append("~얻는 것 질문 없음")
    if not any(f in low for f in CF['fomo_words']): bad.append("~손해 말 없음")
    if not any(x in low for x in CF.get('desire_words', [])): bad.append("~욕망 방아쇠 없음")
    hw = hard_words(sub)
    if hw: bad.append(f"~어려운 말 {hw}")
    if tail(sub) in recent_tails: bad.append(f"~최근 6편과 같은 뒷문장 «{tail(sub)}»")
    return bad

def stamp_ok(st):
    """도장 관문: 2~3단어 대문자, 콜 금지. 아니면 None (감독이 훅 동사로 대신한다)."""
    if not st: return None
    st = re.sub(r'[^A-Z0-9\' ]', '', str(st).upper()).strip()
    low = st.lower()
    if any(re.search(r'(?<!\w)' + re.escape(c) + r'(?!\w)', low) for c in CF.get('call_words', [])): return None
    return st if 1 <= len(st.split()) <= 3 else None

STAMP_PROMPT = """For each reel of "Hama the Gold Digger" (Canadian beginners) write "stamp": the FOMO order the reel gives, 2 to 3 words in capitals, stamped next to the big number so one frame says what to feel and do. An imperative, never a fact: "DON'T MISS THIS", "GET IT BACK", "DON'T LOSE IT", "CLAIM YOURS", "KEEP IT", "DON'T SELL", "FILE IT", "STOP THE LEAK". A halving-crash post is "DON'T MISS THIS"; a refund post "GET IT BACK"; a fee post "STOP THE LEAK". Never "BUY" or "SELL NOW". Vary them; no more than a third of the posts may share one stamp.
Answer {"stamps": {"<key>": "..."}} only.

Input: """

def backfill_stamp(paths):
    """기존 편의 hooks.stamp 를 한 번의 호출로 채운다. 새 편은 --make 가 훅과 같이 뽑는다."""
    ds = {pathlib.Path(x).stem: json.load(open(x, encoding='utf-8')) for x in paths}
    out = ask_claude({"posts": [{"key": k, "hook": (d.get('hooks') or {}).get('on_screen'), "promise": (d.get('hooks') or {}).get('promise'), "object": d.get('object'),
                                 "so_what": (d.get('plain') or {}).get('so_what')} for k, d in ds.items()]}, timeout=900, prompt_text=STAMP_PROMPT)
    got = out.get('stamps', {}); n = 0
    for x in paths:
        k = pathlib.Path(x).stem; st = stamp_ok(got.get(k))
        ds[k].setdefault('hooks', {})['stamp'] = st; n += bool(st)
        json.dump(ds[k], open(x, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(x, 'a', encoding='utf-8').write('\n')
        print(f"  {'✓' if st else '✗'} {k:36s} {st or got.get(k)}")
    print(f"  도장 {n}/{len(paths)}")

def tail(s): return re.split(r'(?<=[.?!])\s+', (s or '').strip())[-1].lower().rstrip('.?!')

def promise_gates(pr, sub=''):
    """② 약속 줄 (hooks.json promise). 시간 약속으로 시작하고, 짧고, 방법은 없다. 심리 규칙: 훅과 반대 극 (경고)."""
    bad = []; low = (pr or '').lower(); hl = (sub or '').lower()
    if not (pr or '').startswith(PR['starts']): bad.append(f"~P-1 «{PR['starts']}» 로 시작하지 않는다")
    if len(words(pr)) > PR['max_words']: bad.append(f"~P-2 약속 {len(words(pr))}단어")
    loss_in_hook = any(f in hl for f in CF['fomo_words']); loss_in_prom = any(f in low for f in CF['fomo_words'])
    if not loss_in_hook and not loss_in_prom: bad.append("~P-5 훅이 얻는 것인데 약속에 손해가 없다 (한 편에 둘 다)")
    hit = [a for a in CF['answer_words'] if a in low]
    if hit: bad.append(f"P-3 답 노출 {hit}")
    hitb = [b for b in BANNED + ['guarantee'] if b in low]
    if hitb: bad.append(f"P-4 금지 {hitb}")
    return bad


def hard(c): return [g for g in c['gates'] if not g.startswith('~')]


def split_num(sub):
    """소제목에서 첫 숫자를 .num 자리로 뗀다. 롤업은 그 숫자만 한다."""
    m = re.search(r'(\$?\d[\d,]*(?:\.\d+)?)', sub or '')   # «122,000.» 의 마침표는 숫자가 아니다
    if not m: return {"pre": sub or '', "num": None, "post": ""}
    return {"pre": sub[:m.start()], "num": m.group(1).lstrip('$'), "post": sub[m.end():]} if not m.group(1).startswith('$') \
        else {"pre": sub[:m.start()] + '$', "num": m.group(1)[1:], "post": sub[m.end():]}


def hookscore(lines):
    if not (SCORER / 'hookscore.py').exists(): return {}
    f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8'); f.write('\n'.join(lines)); f.close()
    out = subprocess.run([sys.executable, 'hookscore.py', f.name], cwd=SCORER, capture_output=True, text=True).stdout
    return {m.group(2).strip(): float(m.group(1)) for m in re.finditer(r'^\s*(?:->)?\s*([\d.]+)\s+[A-Z]+\s+(.+?)\s*$', out, re.M)}


def ask_claude(payload, timeout=600, prompt_text=None, tools=None, tries=2):
    """claude -p. 응답 JSON 이 깨지면 한 번 더 (11/05 ETF 찾기가 글자 하나로 통째로 죽었다)."""
    for k in range(tries):
        try: return _ask(payload, timeout, prompt_text, tools)
        except (json.JSONDecodeError, RuntimeError) as x:
            if k + 1 == tries: raise
            print(f"  ~ 모델 응답 깨짐, 다시: {str(x)[:80]}")

def _ask(payload, timeout=600, prompt_text=None, tools=None):
    """claude -p 한 번. 프롬프트 파일 + 입력 JSON. 바깥 CLAUDE.md 를 안 읽게 빈 폴더에서 돌린다.
    prompt_text 를 주면 그 프롬프트로 (레일 감독 prompts/rail.md). tools 를 주면 그 도구만 연다 (찾기 엔진의 WebSearch,WebFetch)."""
    prompt = (prompt_text or PROMPT) + json.dumps(payload, ensure_ascii=False, indent=1)
    with tempfile.TemporaryDirectory() as d:
        cmd = ['claude', '-p', '--output-format', 'json'] + (['--allowedTools', tools] if tools else [])
        r = subprocess.run(cmd, input=prompt, cwd=d,
                           capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"claude -p exited {r.returncode}: {(r.stderr or r.stdout).strip()[:300]}")
    try:
        env = json.loads(r.stdout); text = env.get('result', r.stdout) if isinstance(env, dict) else r.stdout
    except json.JSONDecodeError:
        text = r.stdout
    m = re.search(r'\{.*\}', text, re.S)
    if not m: raise RuntimeError('응답에 JSON 이 없다: ' + text[:200])
    return json.loads(m.group(0))


def load_ledger(): return json.load(open(LEDGER, encoding='utf-8')) if LEDGER.exists() else []
def save_ledger(rows):
    json.dump(rows, open(LEDGER, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open(LEDGER, 'a', encoding='utf-8').write('\n')


def report(series, cands, pick):
    print(f"  대제목  {series}")
    print(f"  {'방식':6s} {'모델':>4s} {'점수':>5s}  {'관문':14s} ① 훅  ·  ② 약속")
    for i, c in enumerate(cands):
        g = 'PASS' if not hard(c) else '·'.join(x.split()[0] for x in hard(c))
        mt = sum(c.get('tests', {}).values()) if c.get('tests') else 0
        print(f"{'→' if i == pick else ' '} {c['mode']:6s} {mt:4d} {c.get('score', 0):5.1f}  {g:14s} {c['subtitle']}  ·  {c.get('promise', '')}")


def make(path, dry=False, seeds_only=False):
    d = json.load(open(path, encoding='utf-8'))
    cat = d.get('category', ''); fact = d.get('fact')
    if not fact: raise SystemExit("post.json 에 fact{num,unit,thing,box,claim} 이 없다 — 사실 없이는 훅도 없다")
    series = SERIES.get(cat)
    if not series: raise SystemExit(f"hooks.json series 에 '{cat}' 대제목이 없다")
    if seeds_only:
        cands = [{"mode": m, "subtitle": s.format(N=fact['num'], U=fact.get('unit', ''), thing=fact['thing'], box=fact.get('box', 'box')),
                  "promise": PR['starts'] + " Keep all of it.", "tests": {}, "why": "seed"} for m, s in SEEDS.items()]
        pick = 0; pick_why = '씨앗 — 모델 없이 뼈대만'
    else:
        ft = felt(d)
        if not ft: raise SystemExit(f"{pathlib.Path(path).stem}: fact.felt 가 없거나 증명 안 됨 — 훅 숫자가 없다. 먼저 python3 엔진/hook.py felt {path}")
        out = ask_claude({"category": cat, "series": series, "angle": HK['series'].get('angle', {}).get(cat), "object": d.get('object', ''),
                          "subject": subject(d), "felt": {**ft, "as_written": felt_str(ft)}, "fact": {k: v for k, v in fact.items() if k != 'felt'},
                          "real_moves": real_moves(d), "why": d.get('why'),
                          "story": {"title": d.get('title'), "so_what": (d.get('plain') or {}).get('so_what'), "script": [b.get('say') for b in (d.get('rail') or {}).get('beats') or [] if b.get('say')]},
                          "playbook": {**HK.get('playbook', {}).get('common', {}), **HK.get('playbook', {}).get(cat, {})}, "plain": HK.get('plain', {}),
                          "modes": MODES, "audience": "Canadian beginners saving toward their first $100k"})
        cands = out.get('candidates', []); pick = int(out.get('pick', 0)); pick_why = out.get('pick_why', '')
    sc = hookscore([c['subtitle'] for c in cands])
    rec = [r for r in load_ledger() if r['post'] != pathlib.Path(path).stem][-6:]; used_t = [tail(r.get('chosen')) for r in rec]
    for c in cands:
        c['gates'] = gates(c['subtitle'], cat, subject(d), felt(d), fact, used_t) + promise_gates(c.get('promise', ''), c['subtitle']); c['score'] = sc.get(c['subtitle'], 0.0)
    # 추천이 관문에 걸리면 관문 통과 중 모델 점수 최고로 바꾼다. 모델 점수는 제안, 관문은 법이다. 통과 후보 안에서 후보를 더 바꾸지는 않는다 (11/05 밤)
    if cands and hard(cands[pick]):
        ok = [i for i, c in enumerate(cands) if not hard(c)]
        if ok: pick = max(ok, key=lambda i: (sum(cands[i].get('tests', {}).values()), cands[i]['score']))
    report(series, cands, pick)
    print(f"\n  왜  {pick_why}")
    if dry or not cands: return 0
    best = cands[pick]
    if hard(best): print(f"  ⚠ 관문 통과 후보가 없다 {hard(best)} — post.json 에 쓰지 않는다"); return 1
    d['hooks'] = {"formula": d.get('hooks', {}).get('formula', 'H2-stop-wasting'),
                  "candidates": [c['subtitle'] for c in cands], "modes": [c['mode'] for c in cands],
                  "on_screen": best['subtitle'], "spoken": best['subtitle'], "promise": best['promise'], "stamp": stamp_ok(best.get('stamp')),
                  "pick_why": pick_why, "made_by": "엔진/hook.py --make (prompts/hook.md via claude -p)",
                  "made_on": str(datetime.date.today())}
    hero = next((s for s in d['slides'] if s['type'] == 'hero'), None)
    if hero is None:
        hero = {"type": "hero"}; d['slides'].insert(0, hero)
    hero['kicker'] = hero.get('kicker') or f"{cat.upper()} · CANADA"
    hero['topic'] = series; hero['hook'] = split_num(best['subtitle']); hero['promise'] = best['promise']; hero.pop('sub', None)
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(path, 'a', encoding='utf-8').write('\n')
    rows = [r for r in load_ledger() if r['post'] != pathlib.Path(path).stem]
    rows.append({"date": str(datetime.date.today()), "post": pathlib.Path(path).stem, "category": cat, "series": series,
                 "fact": fact, "candidates": cands, "chosen": best['subtitle'], "chosen_mode": best['mode'],
                 "result": {"saves": None, "shares": None, "comments": None}})
    save_ledger(rows)
    print(f"  썼다  {path}  ·  원장 {len(rows)}편")
    return 0


# ── 47편 일괄: felt → audit → rehook → sheet (11/06 계획 1단계) ────────────
OUT = P.parent / '콘텐츠' / '찾은'; WORK = P / 'out' / '작업'

def posts_all():
    """릴스(MP4)가 있는 편 전부. 폐기 편(MP4 없음)은 자동으로 빠진다."""
    return [str(p) for p in sorted(OUT.glob('*.json')) if (P / 'out' / '릴스' / f"{p.stem}-rail.mp4").exists()]

def audit(paths):
    """관문 표. 편 · 이름 · felt · 훅 · FAIL/경고. 모델 없이 결정론. 표는 out/작업/hook-audit.md."""
    rows = []; fails = []
    for path in paths:
        d = json.load(open(path, encoding='utf-8')); stem = pathlib.Path(path).stem
        hk = (d.get('hooks') or {}).get('on_screen', ''); ft = felt(d)
        g = gates(hk, d.get('category', ''), subject(d), ft, d.get('fact'))
        pill = ((d.get('rail') or {}).get('beats') or [{}])[0].get('data', {}).get('pill')
        if not pill: g.append("F-2 첫 장면에 물건 알약 없음")
        h = hard({'gates': g}); w = [x[1:] for x in g if x.startswith('~')]
        if h: fails.append(path)
        rows.append(f"| {stem} | {subject(d) or '—'} | {felt_str(ft) if ft else '—'} | {hk} | {'**FAIL** ' + ' · '.join(h) if h else 'PASS'} | {' · '.join(w)} |")
    WORK.mkdir(parents=True, exist_ok=True)
    md = (f"# 훅 관문 표 — {datetime.date.today()} · {len(paths)}편 · FAIL {len(fails)}\n\n공식: [이름] + [잃은 것 $ = felt] + [얻는 것 질문]. FAIL 은 넷뿐, 나머지는 경고.\n\n"
          "| 편 | 이름 | felt | 훅 | 판정 | 경고 |\n|---|---|---|---|---|---|\n" + '\n'.join(rows) + '\n')
    (WORK / 'hook-audit.md').write_text(md, encoding='utf-8')
    print(md); print(f"  → {WORK / 'hook-audit.md'}")
    return fails

def rehook(paths, render=False):
    """FAIL 편만: 훅 새로(--make) → 첫 두 비트 say + 첫 장면 데이터만 교체(director.reopen) → 레일 다시. 편마다 실패를 격리한다."""
    sys.path.insert(0, str(P / 'motion' / 'rail')); import director, build_rail
    done, failed = [], []
    for path in paths:
        stem = pathlib.Path(path).stem
        try:
            print(f"\n■ {stem}")
            if make(path) != 0: raise RuntimeError("관문 통과 훅 없음")
            d = json.load(open(path, encoding='utf-8'))
            if not d.get('rail'): raise RuntimeError("rail 없음 — build.py --direct 가 먼저")
            director.reopen(d, stem)
            json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(path, 'a', encoding='utf-8').write('\n')
            build_rail.build(d, stem, render); done.append(stem)
        except BaseException as x:   # SystemExit 도 잡는다: 한 편이 배치를 멈추지 않는다
            if isinstance(x, KeyboardInterrupt): raise
            failed.append((stem, str(x)[:120])); print(f"  ✗ {stem}: {str(x)[:120]}")
    print(f"\n  다시 만든 편 {len(done)} · 실패 {len(failed)}")
    for s, why in failed: print(f"   ✗ {s}: {why}")
    return failed

def rebuild(paths, direct=False, render=True):
    """4단계 한 명령 (11/06): 편마다 felt(없으면) → 훅 관문(FAIL 이면 --make) → (--direct 면 대본 새로) → remap(모션 다시) → 레일 → MP4. 편마다 실패 격리, 폐기 편은 posts_all 이 거른다."""
    sys.path.insert(0, str(P / 'motion' / 'rail')); import director, build_rail
    done, failed = [], []
    for path in paths:
        stem = pathlib.Path(path).stem
        try:
            print(f"\n■ {stem}")
            d = json.load(open(path, encoding='utf-8'))
            if not felt(d): backfill_felt([path])
            d = json.load(open(path, encoding='utf-8'))
            if not d.get('plain'):   # 쉬운 말 층이 없으면 감독 전에 채운다 (11/07). 대본 body 2 와 낱말 풀이가 여기서 나온다
                import find as _fd; _fd.add_plain(stem); d = json.load(open(path, encoding='utf-8'))
            if hard({'gates': gates((d.get('hooks') or {}).get('on_screen', ''), d.get('category', ''), subject(d), felt(d), d.get('fact'))}):
                if make(path) != 0: raise RuntimeError("훅 관문 통과 후보 없음")
                d = json.load(open(path, encoding='utf-8'))
            if direct or not d.get('rail'):
                director.main(path, False, True, False); d = json.load(open(path, encoding='utf-8'))
            else:
                director.remap(d, stem); json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(path, 'a', encoding='utf-8').write('\n')
                build_rail.build(d, stem, False)
            if render:
                md = WORK / f"{stem}-rail"; mp4 = P / 'out' / '릴스' / f"{stem}-rail.mp4"
                r = subprocess.run(['npx', 'hyperframes', 'render', '--quality', 'looks', '-o', str(mp4)], cwd=md, capture_output=True, text=True)
                if r.returncode: raise RuntimeError("렌더 실패 " + (r.stdout + r.stderr)[-160:])
            done.append(stem)
        except BaseException as x:
            if isinstance(x, KeyboardInterrupt): raise
            failed.append((stem, str(x)[:140])); print(f"  ✗ {stem}: {str(x)[:140]}")
    print(f"\n  다시 만든 편 {len(done)} · 실패 {len(failed)}")
    for s_, why in failed: print(f"   ✗ {s_}: {why}")
    return failed

def sheet(paths, at=1.2):
    """첫 장면 프레임(1.2초) 대지 한 장. hyperframes snapshot → PIL. 레일 프로젝트가 없는 편은 빈 칸."""
    import shoot
    pngs = []
    for path in paths:
        stem = pathlib.Path(path).stem; md = WORK / f"{stem}-rail"
        if not (md / 'index.html').exists(): print(f"  · {stem}: 레일 없음"); continue
        r = subprocess.run(['npx', 'hyperframes', 'snapshot', '--at', str(at), '--json'], cwd=md, capture_output=True, text=True)
        cands = sorted((md / '.hyperframes' / 'artifacts' / 'snapshots').glob(f'*/frame-00-at-{at}s.png'), key=lambda p: p.stat().st_mtime)   # 최신 스냅숏
        if cands: pngs.append(cands[-1])
        else: print(f"  ✗ {stem}: 프레임 못 찍음 {r.stderr[:80]}")
    out = WORK / 'hook-sheet.png'; shoot.contact(pngs, out, cols=6)
    print(f"  대지 {len(pngs)}장 → {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?', choices=['felt', 'stamp', 'audit', 'rehook', 'rebuild', 'sheet', 'selftest']); ap.add_argument('posts', nargs='*')
    ap.add_argument('--all', action='store_true'); ap.add_argument('--force', action='store_true'); ap.add_argument('--render', action='store_true'); ap.add_argument('--direct', action='store_true'); ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--make'); ap.add_argument('--seeds'); ap.add_argument('--dry', action='store_true')
    ap.add_argument('--result', nargs='+'); ap.add_argument('--stats', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'selftest':   # 공식의 다섯 예시가 관문을 지나고, 입력 수익률·콜·이름 없음은 떨어진다
        F = lambda n: {"num": n, "unit": "$"}
        for sub, sj, n in [("SOXL sellers missed $71,000. Want it back?", "SOXL", "71,000"), ("Bitcoin sellers in 2022 missed $4,100. Scared of the next dip?", "Bitcoin", "4,100"),
                           ("Waiting 10 years cost $156,700. Still waiting?", "Waiting 10 years", "156,700"), ("Your TFSA lost $850 to US tax. Want it back?", "Your TFSA", "850"),
                           ("Hama's 2-ETF mix: $100 a month became $286,500. Want the mix?", "Hama's 2-ETF mix", "286,500")]:
            assert not hard({'gates': gates(sub, 'fear', sj, F(n))}), (sub, gates(sub, 'fear', sj, F(n)))
        assert any(g.startswith('F-2') for g in gates("SOXL fell 72.8%. Want it back?", 'fear', "SOXL", F("71,000")))
        assert any(g.startswith('F-1') for g in gates("Sellers missed $71,000. Want it back?", 'fear', "SOXL", F("71,000")))
        assert any(g.startswith('F-3') for g in gates("SOXL: buy the dip, $71,000. Want it?", 'fear', "SOXL", F("71,000")))
        assert felt_str(F("156,700")) == "$156,700" and felt_str({"num": "37", "unit": "%"}) == "37%"
        print("selftest ok"); return 0
    if a.cmd:
        paths = posts_all() if (a.all or not a.posts) else a.posts
        if a.cmd == 'felt': backfill_felt(paths, a.force); return 0
        if a.cmd == 'stamp': backfill_stamp(paths); return 0
        if a.cmd == 'audit': return 1 if audit(paths) else 0
        if a.cmd == 'rehook': return 1 if rehook(audit(paths) if a.all or not a.posts else paths, a.render) else 0
        if a.cmd == 'rebuild': return 1 if rebuild(paths, a.direct, not a.no_render) else 0
        if a.cmd == 'sheet': sheet(paths); return 0
    if a.stats:
        by = {}
        for r in load_ledger():
            for c in r['candidates']:
                x = by.setdefault(c['mode'], {"n": 0, "score": 0.0, "chosen": 0, "saves": []})
                x['n'] += 1; x['score'] += c.get('score', 0)
                if c['subtitle'] == r['chosen']:
                    x['chosen'] += 1
                    if r['result'].get('saves') is not None: x['saves'].append(r['result']['saves'])
        print(f"  {'방식':6s} {'후보':>4s} {'평균점수':>8s} {'선택':>4s} {'평균저장':>8s}")
        for m, x in sorted(by.items(), key=lambda kv: -kv[1]['score'] / max(1, kv[1]['n'])):
            sv = sum(x['saves']) / len(x['saves']) if x['saves'] else float('nan')
            print(f"  {m:6s} {x['n']:4d} {x['score']/max(1,x['n']):8.1f} {x['chosen']:4d} {sv:8.0f}")
        return 0
    if a.result:
        pid, kv = a.result[0], dict(x.split('=') for x in a.result[1:]); rows = load_ledger()
        for r in rows:
            if r['post'] == pid:
                r['result'].update({k: int(v) for k, v in kv.items()}); save_ledger(rows); print(f"  {pid} {r['result']}"); return 0
        raise SystemExit(f"{pid} 가 원장에 없다")
    if a.seeds: return make(a.seeds, dry=True, seeds_only=True)
    if a.make: return make(a.make, dry=a.dry)
    ap.print_help(); return 1


if __name__ == '__main__':
    sys.exit(main())
