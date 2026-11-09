#!/usr/bin/env python3
"""낯선 사람 읽기 (11/07 v2, 레드팀 3번: 경고만, 답 3개를 기록). 하림님 «무슨 말인지 모르겠다»를 숫자로 재는 관문.
투자 한 번 안 해 본 사람(싼 모델)이 대본만 한 번 읽고 «이게 뭐야 / 기억나는 숫자 하나 / 나는 뭘 해» 를 답한다.
엔진이 그 답을 subject · felt · plain.do(또는 cta 물건) 와 결정론으로 대조한다. 재작성은 없다 — 떨어뜨리면 «FAIL 넷» 위반.

  python3 엔진/reader.py <key>... | --all [--md] [--workers 4] [--model haiku]
결과: out/작업/reader.json · reader.md. post.json 은 쓰지 않는다 (감독이 나중에 made_by 에 붙이고 싶으면 reader.read(post) 를 부른다)."""
import argparse, concurrent.futures, json, pathlib, re, subprocess, sys, tempfile

P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P)); import hook   # subject · felt · felt_str · NUM · nval (읽기만)
POSTS = P.parent / "콘텐츠" / "찾은"; WORK = P / "out" / "작업"
STOP = set("the a an and or of to in on for your you it is are was be this that with what see get back want keep one two your own today now then into from at by as".split())

PROMPT = """You are a Canadian in your twenties who has never invested and finds money words hard. You just watched a 30-second reel once; its spoken script is below. Answer from the script alone, in your own plain words. JSON only:
{"what": "one sentence: what was this reel about? Name the thing it talked about, as you understood it",
 "number": "the one dollar amount you remember, as digits with $, then what it meant in 8 words or fewer",
 "do": "what the reel wants you to do or check, one sentence. If it never said, write exactly: unclear",
 "hard": ["every word or name you did not understand"]}

Script:
"""

def script_of(post):
    sc = (post.get("rail") or {}).get("scenes") or []
    lines = [ln for s in sc for ln in s.get("lines") or []] or [b.get("say", "") for b in (post.get("rail") or {}).get("beats") or []]
    return "\n".join(ln.replace("*", "") for ln in lines if ln)

def ask(text, model="haiku", timeout=120):
    with tempfile.TemporaryDirectory() as d:   # 바깥 CLAUDE.md 를 안 읽게 빈 폴더에서
        r = subprocess.run(["claude", "-p", "--model", model, "--output-format", "json"], input=PROMPT + text, cwd=d, capture_output=True, text=True, timeout=timeout)
    if r.returncode: raise RuntimeError(f"claude -p {r.returncode}: {(r.stderr or r.stdout)[:160]}")
    try: txt = json.loads(r.stdout).get("result", r.stdout)
    except json.JSONDecodeError: txt = r.stdout
    m = re.search(r"\{.*\}", txt, re.S)
    if not m: raise RuntimeError("응답에 JSON 없음: " + txt[:120])
    return json.loads(m.group(0))

def words(s): return {w for w in re.findall(r"[a-z][a-z'\-]{3,}", (s or "").lower()) if w not in STOP}

def judge(post, ans):
    """결정론 대조. 셋 다 맞으면 PASS. 아니면 틀린 칸과 낯선 사람의 말을 그대로 적는다."""
    subj = (hook.subject(post) or "").lower(); subj = re.sub(r"^(the|your|hama's)\s+", "", subj)
    what = (ans.get("what") or "").lower()
    plain_what = words((post.get("plain") or {}).get("what"))
    ok_what = (bool(subj) and (re.search(r"\b" + re.escape(subj) + r"\b", what) is not None or any(re.search(r"\b" + re.escape(w) + r"\b", what) for w in subj.split() if len(w) >= 3))) or len(words(what) & plain_what) >= 2   # 낱말 경계 (레드팀 9: cra ⊂ crash)   # 이름을 안 불러도 plain.what 과 뜻이 겹치면 알아들은 것 («a savings account for buying a first home» = FHSA)
    ft = hook.felt(post); nums = [hook.nval(m) for m in hook.NUM.findall((ans.get("number") or "").replace("K", "k"))]
    want_n = hook.nval(hook.felt_str(ft)) if ft else None
    if want_n is None:   # felt 없는 편은 fact.num 으로 (레드팀 8)
        try: want_n = float(str((post.get("fact") or {}).get("num", "")).replace(",", ""))
        except ValueError: want_n = None
    ok_num = want_n is not None and any(abs(x - want_n) <= max(1, x * .01) for x in nums)
    do = (ans.get("do") or "").strip(); dl = do.lower()
    want = words((post.get("plain") or {}).get("do")) | words((post.get("deliver") or {}).get("gift")) | words(post.get("object")) | {"comment", "save", "check", "write", "open", "look"}
    ok_do = bool(do) and "unclear" not in dl and bool(words(do) & want)
    hard = [h for h in (ans.get("hard") or []) if isinstance(h, str) and h.strip()]
    miss = [k for k, ok in (("what", ok_what), ("number", ok_num), ("do", ok_do)) if not ok]
    return {"ok": not miss, "miss": miss, "hard": hard[:6], "answers": {"what": ans.get("what"), "number": ans.get("number"), "do": do}}

def read(post, model="haiku"):
    txt = script_of(post)
    if not txt: return {"ok": False, "miss": ["script"], "hard": [], "answers": {}}
    for k in range(2):
        try: return judge(post, ask(txt, model))
        except Exception as x:
            if k: return {"ok": False, "miss": ["model"], "hard": [], "answers": {"error": str(x)[:120]}}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("keys", nargs="*"); ap.add_argument("--all", action="store_true"); ap.add_argument("--md", action="store_true"); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--model", default="haiku")
    a = ap.parse_args()
    keys = a.keys or ([pathlib.Path(p).stem for p in hook.posts_all()] if a.all else [])
    if not keys: ap.print_help(); return 1
    posts = {k: json.load(open(POSTS / f"{k}.json", encoding="utf-8")) for k in keys}
    with concurrent.futures.ThreadPoolExecutor(a.workers) as ex: res = dict(zip(keys, ex.map(lambda k: read(posts[k], a.model), keys)))
    WORK.mkdir(parents=True, exist_ok=True); jf = WORK / "reader.json"
    allr = json.load(open(jf, encoding="utf-8")) if jf.exists() else {}; allr.update(res); jf.write_text(json.dumps(allr, ensure_ascii=False, indent=1), encoding="utf-8")   # 부분 실행은 합친다
    n_ok = sum(1 for r in res.values() if r["ok"])
    for k in keys:
        r = res[k]; an = r["answers"]
        print(f"  {'✓' if r['ok'] else '~'} {k:36s} {'PASS' if r['ok'] else '놓침 ' + ','.join(r['miss']):16s} {str(an.get('number') or an.get('error') or '')[:50]:50s} 어려운 말 {len(r['hard'])}")
    print(f"\n  낯선 사람 읽기 {len(keys)}편 · 셋 다 맞음 {n_ok} · 놓침 what {sum('what' in r['miss'] for r in res.values())} · number {sum('number' in r['miss'] for r in res.values())} · do {sum('do' in r['miss'] for r in res.values())} → {WORK / 'reader.json'}")
    if a.md:
        keys, res = sorted(allr), allr; n_ok = sum(1 for r in res.values() if r["ok"])   # 표는 합쳐진 전체
        md = [f"# 낯선 사람 읽기 — {len(keys)}편 · 셋 다 맞음 {n_ok}", "", "haiku 가 대본만 읽고 «이게 뭐야 / 숫자 하나 / 나는 뭘 해» 를 답한 것을 subject · felt · plain.do 와 대조. 경고만 (재작성 없음, 레드팀 3번).", "",
              "| 편 | 판정 | 이게 뭐야 (낯선 사람 말) | 숫자 | 나는 뭘 해 | 어려운 말 |", "|---|---|---|---|---|---|"]
        for k in keys:
            r = res[k]; an = r["answers"]; cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")[:110]
            md.append(f"| {k} | {'PASS' if r['ok'] else '놓침 ' + ' '.join(r['miss'])} | {cell(an.get('what'))} | {cell(an.get('number'))} | {cell(an.get('do'))} | {cell(', '.join(r['hard']))} |")
        (WORK / "reader.md").write_text("\n".join(md) + "\n", encoding="utf-8"); print(f"  → {WORK / 'reader.md'}")
    return 0

if __name__ == "__main__":
    if "--selftest" in sys.argv:   # 모델 없이: 대조 규칙
        post = {"subject": "SOXL", "category": "fear", "fact": {"num": "81,000", "unit": "$", "sources": [], "felt": {"num": "71,000", "unit": "$", "a": "81,000", "b": "10,000"}}, "sources": [{"what": "81,000 and 10,000"}], "plain": {"do": "Write down what you would have done at the low."}, "object": "THE HOLDER'S LEDGER"}
        assert judge(post, {"what": "A fund called SOXL crashed and people who sold lost out", "number": "$71,000, what sellers missed", "do": "Write down what I would do at a low", "hard": []})["ok"]
        j = judge(post, {"what": "something about stocks", "number": "$10,000", "do": "unclear", "hard": ["ETF", "leveraged"]}); assert j["miss"] == ["what", "number", "do"], j
        post["plain"]["what"] = "SOXL is a fund that bets on chip companies three times harder. People who sold at the low missed the rebound."
        assert judge(post, {"what": "a fund betting on chip companies where sellers missed the rebound", "number": "$71,000 missed", "do": "write it down", "hard": []})["ok"]   # 이름 없이 뜻으로 통과
        print("reader selftest ok"); sys.exit(0)
    sys.exit(main())
