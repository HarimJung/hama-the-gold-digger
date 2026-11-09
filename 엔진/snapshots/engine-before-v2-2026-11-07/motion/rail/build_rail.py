#!/usr/bin/env python3
"""레일 릴스: post.json 의 reel{} → 목소리(장면별 TTS) → 단어 자막 → HyperFrames 프로젝트 → (--render) MP4.
  python3 엔진/build.py <post.json> --rail [--render]
피부는 skin.css, 부품은 parts.py 한 곳. 여기는 시간과 배선만 한다.
reel{}: voice · speed · hold · beats[{say, part?, badge?, data?}]
  say 는 자막 그대로(숫자는 $122,000 처럼 숫자로, 강조 단어는 *별표*). 읽을 때만 말로 바꾼다.
  part 가 없는 장면은 앞 장면의 부품을 이어 간다.
숫자 관문: say·data 의 $·% 숫자는 전부 같은 post.json(reel 밖)에 있어야 한다. 없으면 멈춘다."""
import json, re, sys, hashlib, pathlib, shutil, subprocess, os
from html import escape as e
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from parts import PARTS

R = pathlib.Path(__file__).parent
ENG = R.parent.parent
TTS_PY = os.environ.get("HYPERFRAMES_PYTHON", os.path.expanduser("~/.local/share/hama-tts/bin/python"))  # 저장소 밖에 둔다(validate.py 가 훑지 않게)
CACHE = ENG / "out" / ".tts-cache"
RAIL_END = ("checklist", "compare", "tiles")
OPENERS = ("hooknum", "title2", "slam", "tease", "rollnum", "rise", "cover", "boil", "glass", "window")   # 11/07 3라운드: rise(T4)·cover(K2)·boil(K3)·glass(K4)·window(K5)   # 0초부터 보이는 첫 장면 (11/06 발견 15: tease·slam 의 0초 프레임이 비었다)

# ── 숫자 관문 ──────────────────────────────────────────────
NUM = re.compile(r"\$\d[\d,]*(?:\.\d+)?k?|\d+(?:\.\d+)?%")
def nval(t):
    k = t.endswith("k"); t = t.strip("$%k").replace(",", "")
    v = float(t) * (1000 if k else 1)
    return v
def script_key(post):
    """레일 대본 칸. 새 편은 rail{}, 11/04 Day 4 는 reel{} (beats 가 있는 쪽)."""
    for k in ("rail", "reel"):
        if isinstance(post.get(k), dict) and post[k].get("beats"): return k
    raise SystemExit("post.json 에 rail{beats} 이 없다")
def gate(post):
    """대본의 $·% 는 전부 편이 증명한 숫자(hook.numset: fact·slides·sources·why)여야 한다. 아니면 멈춘다 (11/06 레드팀 발견 10: print 만 하던 관문, 대조 집합에 모델 산출물이 섞여 순환)."""
    sys.path.insert(0, str(ENG)); import hook as _hk
    key = script_key(post); ok = _hk.numset(post)
    bad = sorted({m for m in NUM.findall(json.dumps(post[key], ensure_ascii=False)) if not any(abs(nval(m) - v) <= max(1, nval(m) * .01) for v in ok)})
    if bad: raise SystemExit(f"숫자 관문: 대본의 {bad} 가 fact·slides·sources·why 에 없다 — 지어낸 숫자는 못 나간다")

# ── 읽기용 문장: 숫자를 말로 ─────────────────────────────────
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def words(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " and " + words(n % 100))
    for big, name in ((10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= big: return (words(n // big) + " " + name
                             + ("" if n % big == 0 else (" and " if n % big < 100 else " ") + words(n % big)))

SAY = json.load(open(ENG / "hooks.json", encoding="utf-8")).get("say", {})   # 티커·약어 발음표 (11/05)
try: WORDS = set(open("/usr/share/dict/words").read().split())   # 맥 사전. 없으면 전부 약어 취급
except OSError: WORDS = set()
UNIT = {"k": "thousand", "K": "thousand", "M": "million", "B": "billion", "T": "trillion", "million": "million", "billion": "billion", "trillion": "trillion"}
NUMTOK = re.compile(r"(?<![\w.])([+\-−])?(\$)?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s?(million|billion|trillion)\b|(k|K|M|B|T)\b)?(%)?")

def say_num(m):
    """숫자 하나를 말로. 부호·달러·소수·단위·퍼센트·연도·센트를 한 번에 (11/05 레드팀: «four dollars billion», «75.five»)."""
    sign, dol, whole, dec, unit = m.group(1), m.group(2), m.group(3).replace(",", ""), m.group(4), m.group(5) or m.group(6)
    pct = m.group(7)
    if not (sign or dol or dec or unit or pct) and len(whole) == 4 and 1900 <= int(whole) <= 2099 and "," not in m.group(3):
        y = int(whole); return words(y) if 2000 <= y <= 2009 else words(y // 100) + " " + ("hundred" if y % 100 == 0 else words(y % 100))
    out = {"+": "plus ", "-": "minus ", "−": "minus "}.get(sign or "", "")
    if dol and dec and len(dec) == 3 and not unit and not pct:   # $44.11 · $0.38
        c = int(dec[1:]); d = int(whole)
        return out + (f"{words(d)} dollars" if d else "") + (" and " if d and c else "") + (f"{words(c)} cents" if c else "")
    out += words(whole) + ("" if not dec else " point " + " ".join(ONES[int(x)] for x in dec[1:]))
    if unit: out += " " + UNIT[unit]
    if pct: out += " percent"
    if dol: out += " dollars"
    return out

def spoken(s, quick=False):
    s = s.replace("*", "")
    if quick: s = re.sub(r"(\d+)\.\d+(%)", lambda m: str(round(float(m.group(0)[:-1]))) + "%", s)   # 첫 장면: 72.8% → 73% 로 읽는다 (화면은 그대로)
    for k, v in SAY.items():   # 기호가 든 약어(S&P)는 글자 그대로 먼저 · 소문자 낱말(vs)은 단어 경계로, 대소문자 무시 (11/06 «브이에스가 아니라 버서스»)
        if k == "_": continue
        if not k.isalnum(): s = s.replace(k, v)
        elif k.islower(): s = re.sub(r"(?<![\w])" + re.escape(k) + r"(?![\w])", v, s, flags=re.I)
    s = re.sub(r"(\d)([A-Z]{2,3})\b", r"\1 \2", s)   # 480MW → 480 MW
    s = re.sub(r"\bUS\$(\d(?:[\d,]*\d)?)(?:\.\d+)?", r"\1 US dollars", s)   # US$87,249.05 → «eighty-seven thousand … U.S. dollars» (11/07 하림님 «어스 에스»)
    s = NUMTOK.sub(say_num, s)
    s = re.sub(r"\b(fell|fall|falls|dropped|drops|down|lost|loses|lose|crashed|sank|slid|cut|hit|at|is|was)\s+minus\s", r"\1 ", s, flags=re.I)
    s = re.sub(r"\b(\w+) dollars (gap|fee|cut|bill|hole|loss|difference|charge|cost)\b", r"\1-dollar \2", s)   # «a three dollars gap» → «a three-dollar gap» (11/07 레드팀)   # «fell -72%» 는 «fell minus» 로 읽지 않는다 (11/05)
    def caps(m):
        w = m.group(1)
        if w in SAY: return SAY[w]
        if len(w) == 2: return " ".join(w)   # 두 글자 대문자는 항상 글자로 (TD·RY·AI). 사전에 td 가 있어 «Td» 로 읽던 것 (11/07 레드팀)
        if w.lower() in WORDS or w.title() in WORDS: return w.title()   # 영어 낱말(SHEET·ROOM·NVIDIA 류)은 낱말로 읽는다 (11/06 하림님 «엔비디아지 엔 브이 아이…»)
        return " ".join(w)   # 표에 없는 진짜 약어만 글자로 (T S L U). 발음은 hooks.json say
    return re.sub(r"\b([A-Z][A-Z0-9]{1,5})\b", caps, s)

# ── 목소리: 장면별로 뽑아 이어 붙인다(장면 길이를 정확히 안다) ──────────
VOICES = R / "voices"                           # <이름>.wav 가 있으면 그 목소리를 클론해 읽는다 (Chatterbox, 엔진/.voice)
def vpath(text, voice, speed):
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / (hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16] + ".wav")

def clone_batch(says, voice, speed):
    """클론 목소리: 캐시에 없는 장면만 모아 모델 한 번으로 뽑는다."""
    lines = [{"text": s, "out": str(vpath(s, voice, speed))} for s in dict.fromkeys(says) if not vpath(s, voice, speed).exists()]
    if not lines: return
    j = CACHE / "clone-jobs.json"
    j.write_text(json.dumps({"ref": str(VOICES / f"{voice}.wav"), "lines": lines, "speed": speed}, ensure_ascii=False))
    subprocess.run([os.path.expanduser("~/.local/share/hama-voice/bin/python"), str(R / "clone_tts.py"), str(j)], check=True)   # 클론은 쉬는 중 (voices/<이름>.wav 를 rail.voice 로 불러야만 돈다)

def tts(text, voice, speed):
    f = vpath(text, voice, speed)
    if not f.exists():
        if (VOICES / f"{voice}.wav").exists():
            clone_batch([text], voice, speed)
        else:
            tmp = CACHE / "say.txt"; tmp.write_text(text)
            subprocess.run(["npx", "hyperframes", "tts", str(tmp), "-v", voice, "-s", str(speed), "-o", str(f)],
                           check=True, capture_output=True, env={**os.environ, "HYPERFRAMES_PYTHON": TTS_PY})
    return f
def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)
def speech(f):
    """소리가 나는 구간 [처음, 끝] (앞뒤 무음 제외)."""
    out = subprocess.run(["ffmpeg", "-i", str(f), "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = dur(f); a, b = 0.0, d
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    if st and st[0] < .05 and en: a = en[0]
    if st and st[-1] > d - 1.5 and (not en or en[-1] < st[-1] or en[-1] >= d - .01): b = st[-1]
    return a, b

def heard(f):
    """장면 wav 의 단어 시각 (hyperframes transcribe, whisper small.en). wav 옆에 캐시. 실패하면 None."""
    j = f.with_suffix(".words.json")
    if not j.exists():
        tmp = CACHE / "tr"; tmp.mkdir(exist_ok=True)
        r = subprocess.run(["npx", "hyperframes", "transcribe", str(f), "--json", "-m", "small.en", "-d", str(tmp)], capture_output=True, text=True)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1]); assert out.get("ok")
            shutil.copy(out["transcriptPath"], j)
        except Exception:
            return None
    try:
        ws = json.load(open(j))
        if not (isinstance(ws, list) and ws and isinstance(ws[0], dict) and "start" in ws[0]): raise ValueError   # 깨진 캐시(11/05: 3편 TypeError)
        return ws
    except Exception:
        j.unlink(missing_ok=True); return None

def align(toks, f):
    """자막 단어마다 들린 시각(장면 안 초). 말로 바꾼 단어끼리 맞춰서, 숫자가 여러 말이 되어도 첫 말에 붙인다. 못 맞추면 None."""
    import difflib
    ws = heard(f)
    if not ws: return None
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    A = [(i, norm(w)) for i, t in enumerate(toks) for w in spoken(t).split() if norm(w)]
    B = [(w["start"], norm(x)) for w in ws for x in spoken(w["text"]).split() if norm(x)]
    sm = difflib.SequenceMatcher(None, [a for _, a in A], [b for _, b in B], autojunk=False)
    at = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i = A[blk.a + k][0]
            at.setdefault(i, B[blk.b + k][0])
    if len(at) < max(1, len(toks) // 2): return None   # 반도 못 맞추면 믿지 않는다
    out, known = [None] * len(toks), sorted(at)
    for i in range(len(toks)):
        if i in at: out[i] = at[i]; continue
        lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
        if lo is not None and hi is not None: out[i] = at[lo] + (at[hi] - at[lo]) * (i - lo) / (hi - lo)
        elif lo is not None: out[i] = at[lo] + .25 * (i - lo)
        else: out[i] = max(0, at[hi] - .25 * (hi - i))
    return out

class Seg:
    def __init__(s, part, beats): s.part, s.beats, s.t0, s.t1 = part, beats, beats[0]["t0"], beats[-1]["t1"]
    def w(s, word, n=1):
        if isinstance(word, int):   # 감독이 단어를 못 찾으면 장면 안 n번째 줄의 첫 단어
            return round(s.beats[min(word, len(s.beats) - 1)]["toks"][0][0], 2)
        key = word.strip("*.,!?$").lower(); k = 0
        for b in s.beats:
            for t, txt, _ in b["toks"]:
                if txt.strip("*.,!?$").lower() == key:
                    k += 1
                    if k == n: return round(t, 2)
        print(f"  ~ «{word}» 가 {s.part} 장면 자막에 없다 → 장면 첫 단어 시각 (11/06: 한 단어로 배치를 멈추지 않는다)"); return round(s.beats[0]["toks"][0][0], 2)

def times(reel):
    """1 목소리와 장면 시각: 비트마다 TTS(캐시) → t0·t1·toks(단어 시각). 파일은 캐시에만 쓴다. cards.py 도 이걸로 장면 시각을 얻는다 (11/06)."""
    voice, speed = reel.get("voice", "af_heart"), reel.get("speed", 1.0)
    if (VOICES / f"{voice}.wav").exists():      # 클론 목소리는 한 번에 모아 뽑는다(모델 로드 1회)
        clone_batch([spoken(b["say"]) for b in reel["beats"]], voice, speed)
    t, wavs = 0.0, []
    # lock-in 은 director 가 한 줄 + cap:"low" 로 준다 (11/06). 임시 다리는 4단계에서 지웠다
    for b in reel["beats"]:
        quick = bool(b.get("nocap")) and b is reel["beats"][0] or (len(wavs) == 1 and bool(b.get("nocap")))   # 훅·약속 두 줄
        f = tts(spoken(b["say"], quick), voice, speed * (1.15 if quick else 1.0)); wavs.append(f)
        d = dur(f); a, z = speech(f)
        b["t0"], b["t1"] = t, t + d
        toks = b["say"].split()
        wt = [len(spoken(x)) + (8 if x.rstrip("*").endswith((".", "!", "?")) else 5 if x.rstrip("*").endswith(",") else 1) for x in toks]
        tot, c, b["toks"] = sum(wt), 0, []
        got = align(toks, f)   # 들린 시각이 있으면 그걸로, 없으면 글자 수 비례 (예전 방식)
        for k, (x, wgt) in enumerate(zip(toks, wt)):
            b["toks"].append((t + (got[k] if got else a + (z - a) * c / tot), x, x.startswith("*")))
            c += wgt
        t += d
    return wavs, t

def build(post, stem, render=False):
    reel = post[script_key(post)]; gate(post)
    hold = reel.get("hold", 3.5)
    md = ENG / "out" / "작업" / f"{stem}-rail"; (md / "assets").mkdir(parents=True, exist_ok=True)   # 중간물은 작업/, 발행 MP4 는 릴스/ (11/04 정리)
    wavs, t = times(reel)
    END = round(t + hold, 2)
    lst = md / "assets" / "vo.txt"; lst.write_text("".join(f"file '{w}'\n" for w in wavs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "48000", str(md / "assets" / "vo.wav")], check=True)
    lst.unlink()
    # 2 장면 → 부품 구간
    segs = []
    for b in reel["beats"]:
        if b.get("part"): segs.append(Seg(b["part"], [b]))
        else: segs[-1].beats.append(b); segs[-1].t1 = b["t1"]
    # 3 부품
    body, js, ticks = [], [], []
    dark = False
    nodark = post.get("category") in json.load(open(ENG / "hooks.json", encoding="utf-8"))["series"].get("no_dark", {}).get("list", [])
    if nodark:
        for b_ in reel["beats"]: b_.pop("dark", None)   # 시리즈 설정: 검정 장면 없음
    for i, s in enumerate(segs):
        p = f"b{i}"; b0 = s.beats[0]; d = b0.get("data", {})
        r = PARTS[s.part](p, s, d)
        html, pjs = r[0], r[1]
        if b0.get("out") == "tear":   # 찢김: 같은 장면을 두 벌 그려 왼쪽·오른쪽 반만 보이게 한다
            r2 = PARTS[s.part](p + "r", s, d)
            html = f'<div class="half hl" id="{p}-tL">{r[0]}</div><div class="half hr" id="{p}-tR">{r2[0]}</div>'
            pjs = r[1] + r2[1]
        body.append(f'<div class="layer p-{s.part}{" dk" if b0.get("dark") else ""}" id="{p}">{html}</div>')
        nxt = segs[i + 1].t0 if i + 1 < len(segs) else None
        nin = segs[i + 1].beats[0].get("in", "fade") if nxt else None
        inn = b0.get("in", "fade")
        if i == 0 and s.part in OPENERS:   # 1초 훅: 0초 프레임에 이미 보인다
            enter = f'tl.set("#{p}",{{opacity:1}},0);'
        elif inn == "pan":
            enter = f'tl.set("#{p}",{{opacity:1}},{s.t0-.2});tl.fromTo("#{p}",{{y:1920}},{{y:0,duration:.5,ease:"power3.inOut"}},{s.t0-.2});'
        elif inn == "dissolve":
            enter = f'tl.fromTo("#{p}",{{opacity:0,filter:"blur(14px)"}},{{opacity:1,filter:"blur(0px)",duration:.35,ease:"sine.inOut"}},{s.t0-.15});'
        elif inn == "zoom":     # D7 줌 관통: 앞 장면은 커지며 사라지고 새 장면은 작게서 커진다
            enter = f'tl.fromTo("#{p}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.45,ease:"expo.out"}},{s.t0-.1});'
        elif inn == "wipe":     # D11 와이프: 왼쪽에서 오른쪽으로 닦아 들어온다
            enter = f'tl.set("#{p}",{{opacity:1}},{s.t0-.2});tl.fromTo("#{p}",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.5,ease:"power3.inOut"}},{s.t0-.2});'
        elif inn == "iris":     # D8 아이리스: 가운데 원이 열린다
            enter = f'tl.set("#{p}",{{opacity:1}},{s.t0-.15});tl.fromTo("#{p}",{{clipPath:"circle(0% at 50% 50%)"}},{{clipPath:"circle(90% at 50% 50%)",duration:.5,ease:"power2.out"}},{s.t0-.15});'
        else:
            enter = f'tl.fromTo("#{p}",{{opacity:0}},{{opacity:1,duration:.35,ease:"power3.out"}},{s.t0});'
        leave = ""
        if nxt and b0.get("out") == "tear":
            k = nxt - .55
            body.append(f'<svg class="spark" id="{p}-sp" viewBox="0 0 40 40"><path d="M20 0 L24 16 L40 20 L24 24 L20 40 L16 24 L0 20 L16 16Z"/></svg>')
            leave = (f'tl.fromTo("#{p}-sp",{{opacity:0,scale:0,rotation:0}},{{opacity:1,scale:1.4,rotation:45,duration:.12,ease:"power2.out"}},{k:.2f});tl.to("#{p}-sp",{{opacity:0,scale:.2,duration:.12}},{k+.12:.2f});'
                     f'tl.to("#{p}-tL",{{x:-50,rotation:-6,duration:.15,ease:"power2.out"}},{k+.1:.2f});tl.to("#{p}-tR",{{x:50,rotation:8,duration:.15,ease:"power2.out"}},{k+.1:.2f});'
                     f'tl.to("#{p}-tL",{{x:-180,y:1500,rotation:-22,duration:.4,ease:"power2.in"}},{k+.25:.2f});tl.to("#{p}-tR",{{x:200,y:1550,rotation:24,duration:.4,ease:"power2.in"}},{k+.25:.2f});'
                     f'tl.set("#{p}",{{opacity:0}},{nxt+.1:.2f});')
            ticks.append(round(k + .1, 2))
        elif nxt and nin == "pan":
            leave = f'tl.to("#{p}",{{y:-1920,duration:.5,ease:"power3.inOut"}},{nxt-.2});tl.set("#{p}",{{opacity:0}},{nxt+.3});'
        elif nxt and nin == "dissolve":
            leave = f'tl.to("#{p}",{{opacity:0,filter:"blur(14px)",duration:.3,ease:"sine.inOut"}},{nxt-.15});'
        elif nxt and nin == "zoom":
            leave = f'tl.to("#{p}",{{opacity:0,scale:1.5,duration:.4,ease:"power2.in"}},{nxt-.3});'
        elif nxt and nin in ("wipe", "iris"):   # 새 장면이 위에서 덮는다: 앞 장면은 덮인 뒤에 끈다
            leave = f'tl.set("#{p}",{{opacity:0}},{nxt+.4});'
        elif nxt:
            leave = f'tl.to("#{p}",{{opacity:0,duration:.25,ease:"power2.in"}},{nxt-.25});'
        js.append(enter + leave + pjs)   # 11/07 저녁: «느린 푸시인 + 줄마다 범프» 는 뺐다 — 레드팀: hyperframes motion.md 의 «생성 티» 안티패턴 + 정지 관문을 가림 + 줌 전환 scale 과 충돌(lint 4개). 줄마다 반응은 review 의 «줄 반응» 지표로 잰다
        if b0.get("dark"):   # 손해 장면만 검정 바탕. 자막 색도 같이 뒤집는다
            dark = True; z = (nxt or END) - .2
            js.append(f'tl.set("#dark",{{opacity:0}},0);tl.set("#dark",{{opacity:1}},{s.t0});tl.set(".cap",{{color:"#FFFFFF"}},{s.t0});'   # 11/05 컷 (페이드는 회색 빈 프레임)
                      f'tl.set("#dark",{{opacity:0}},{z});tl.set(".cap",{{color:"#16140F"}},{z});')
        if len(r) > 2: ticks += r[2]
        for j, b_ in enumerate(s.beats[1:], 1):   # 줄 칩 (11/07): 이어지는 줄이 새 숫자를 말하면 숫자 칩이 아래 띠에 팝. 부품 데이터에 이미 있는 숫자는 건너뛴다
            if b_.get("nocap") or b_.get("cap") == "low": continue
            nums = [m for m in NUM.findall(b_["say"]) if m not in json.dumps(d, ensure_ascii=False)]
            if not nums: continue
            cid = f"{p}-lc{j}"; at = next((t_ for t_, x, _ in b_["toks"] if nums[0] in x), b_["t0"])
            body.append(f'<div class="lchip" id="{cid}">{e(nums[0])}</div>')
            js.append(f'tl.fromTo("#{cid}",{{opacity:0,scale:1.5,y:20}},{{opacity:1,scale:1,y:0,duration:.3,ease:"back.out(2)"}},{at:.2f});tl.to("#{cid}",{{opacity:0,duration:.2}},{b_["t1"]-.1:.2f});')
            ticks.append(round(at, 2))
    # 4 레일·배지·아바타
    bb = [b for b in reel["beats"] if b.get("badge")]
    if bb:
        r0 = bb[0]["t0"]; r1 = next((s.t0 for s in segs if s.part in RAIL_END and s.t0 > bb[-1]["t0"]), END)   # 11/05: 끝까지 남던 배지
        js.append(f'tl.fromTo("#rail",{{opacity:0}},{{opacity:1,duration:.3}},{r0-.2});tl.fromTo("#railfill",{{scaleY:0}},{{scaleY:1,duration:{r1-r0:.2f},ease:"none"}},{r0});'
                  f'tl.to(["#rail","#ava"],{{opacity:0,duration:.25}},{r1-.2});')
        for j, b in enumerate(bb):
            a = b["t0"]; z = bb[j + 1]["t0"] if j + 1 < len(bb) else r1
            body.append(f'<div class="badge" id="bd{j}"><b>{j+1:02d}</b>{e(b["badge"])}</div>')
            js.append(f'tl.fromTo("#bd{j}",{{opacity:0,x:-16}},{{opacity:1,x:0,duration:.3,ease:"power3.out"}},{a});tl.to("#bd{j}",{{opacity:0,duration:.2}},{z-.2});')
    if segs[0].part == "hook" and len(segs) > 1:
        m = segs[1].t0
        js.append(f'tl.to("#ava",{{x:-476,y:-442,scale:.12,duration:.6,ease:"power3.inOut"}},{m-.3});tl.to("#b0-chip",{{opacity:0,duration:.2}},{m-.3});')
    else:
        js.append('tl.set("#ava",{opacity:0},0);')
    # 5 위쪽 한 줄 자막: 문장부호에서 끊고 5단어 넘기지 않는다
    phrases, cur, low = [], [], set()
    for b in reel["beats"]:
        if b.get("nocap"): continue   # 화면 글 = 첫마디인 장면은 위 자막을 안 띄운다
        for tok in b["toks"]:
            cur.append(tok)
            if re.search(r"[.,!?]\*?$", tok[1]) or len(cur) == 5:
                if b.get("cap") == "low": low.add(len(phrases))
                phrases.append(cur); cur = []
        if cur:
            if b.get("cap") == "low": low.add(len(phrases))
            phrases.append(cur); cur = []
    caps = []
    for k, ph in enumerate(phrases):
        sp = []
        for j, (tt, x, em) in enumerate(ph):
            x = x.strip("*") if em else x
            if em and x.endswith("*"): x = x[:-1]
            x = x.replace("*", "")
            sp.append(f'<span id="c{k}_{j}" class="{"w em" if em else "w"}">' + (f"<i>{e(x)}</i>" if em else e(x)) + "</span>")
            if reel.get("caption") == "blur":
                js.append(f'tl.fromTo("#c{k}_{j}",{{opacity:0,y:8,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.2,ease:"power2.out"}},{tt:.2f});')
            elif reel.get("caption") == "karaoke":   # T2: 구절 전체가 흐리게 먼저 보이고, 읽는 단어만 골드로 켜진다 (11/06)
                js.append(f'tl.set("#c{k}_{j}",{{opacity:.3}},{ph[0][0]:.2f});tl.to("#c{k}_{j}",{{opacity:1,color:"#9A7414",duration:.12}},{tt:.2f});tl.to("#c{k}_{j}",{{color:"#16140F",duration:.3}},{tt+.5:.2f});')
            else:
                js.append(f'tl.fromTo("#c{k}_{j}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:.22,ease:"power3.out"}},{tt:.2f});')
            if em: js.append(f'tl.fromTo("#c{k}_{j}",{{"--box":0}},{{"--box":1,duration:.3,ease:"expo.out"}},{tt+.08:.2f});')
        n_ = sum(len(x) + 1 for _, x, _ in ph)   # 62px 한 줄에 34자쯤 들어간다 (Day 4 32자 그대로). 넘으면 글자를 줄인다 (끝 장면 «...checkli» 잘림, 11/04)
        fs = f' style="font-size:{62 * 34 // n_}px"' if n_ > 34 else ''
        caps.append(f'<div id="cap{k}" class="cap{" low" if k in low else ""}"{fs}>{" ".join(sp)}</div>')   # .cap.low = 첫 장면 위 lock-in 자막 띠 (skin.css)
        js.append(f'tl.set("#cap{k}",{{opacity:1}},{ph[0][0]:.2f});')
        if k + 1 < len(phrases): js.append(f'tl.set("#cap{k}",{{opacity:0}},{phrases[k+1][0][0]-.001:.3f});')
    # 6 틱 소리
    sfx = ""
    if ticks:
        args = ["ffmpeg", "-v", "error", "-y"]
        for _ in ticks: args += ["-i", str(R / "tick.wav")]
        mix = "".join(f"[{i}]adelay={int(x*1000)}:all=1[a{i}];" for i, x in enumerate(ticks))
        mix += "".join(f"[a{i}]" for i in range(len(ticks))) + f"amix=inputs={len(ticks)}:normalize=0,apad=whole_dur={END}[o]"
        subprocess.run(args + ["-filter_complex", mix, "-map", "[o]", "-ar", "48000", str(md / "assets" / "sfx.wav")], check=True)
        sfx = f'<audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="{END}" data-track-index="11" data-volume="0.5"></audio>'
    shutil.copy(ENG / "assets" / "hama-face.png", md / "assets")
    html = f'''<!doctype html>
<!-- 생성물. 고치지 말 것: 피부 엔진/motion/rail/skin.css · 부품 parts.py · 배선 build_rail.py · 글과 숫자 {e(stem)}.json reel{{}} -->
<html data-composition-variables='[]'>
<head><meta charset="utf-8"><title>{e(post.get("title", stem))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
{(R / "skin.css").read_text()}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
<div id="grid"></div><div id="glow"></div>{'<div id="dark"></div>' if dark else ''}<div id="rail"><div id="railfill"></div></div>
{chr(10).join(body)}
<div id="ava"></div>
<div id="caps" data-track-kind="captions">
{chr(10).join(caps)}
</div>
<audio id="vo" class="clip" src="assets/vo.wav" data-start="0" data-duration="{round(t, 2)}" data-track-index="10"></audio>
{sfx}
</div>
<script>
const tl=gsap.timeline({{paused:true}});
function pop(id,t,o){{tl.fromTo(id,{{opacity:0,scale:.96,y:30}},{{opacity:1,scale:1,y:0,duration:.55,ease:"expo.out",...o}},t);}}
{chr(10).join(js)}
tl.set({{}},{{}},{END});
window.__timelines["main"]=tl;
</script>
</body></html>'''
    (md / "index.html").write_text(html)
    (md / "beats.json").write_text(json.dumps([{"t0": round(b_["t0"], 2), "say": b_["say"], "nocap": bool(b_.get("nocap"))} for b_ in reel["beats"]], ensure_ascii=False))   # 장면 시각 (review 의 «줄 반응» 이 읽는다, 11/07)
    try:   # hyperframes check: 경고 집계만 (11/07 레드팀 4번: 하드 게이트는 «FAIL 은 넷뿐» 위반). review 가 check.json 을 읽는다
        ck = subprocess.run(["npx", "hyperframes", "check", "--json"], cwd=md, capture_output=True, text=True, timeout=180)
        cj = json.loads(ck.stdout); codes = {}
        for sec in ("lint", "runtime", "layout", "contrast", "craft", "motion"):
            for x in ((cj.get(sec) or {}).get("findings") or []):
                c = f'{sec}:{x.get("code", "?")}'; codes[c] = codes.get(c, 0) + 1
        (md / "check.json").write_text(json.dumps({"ok": cj.get("ok"), "codes": codes}, ensure_ascii=False))
        print("  check:", " · ".join(f"{k} {v}" for k, v in sorted(codes.items(), key=lambda kv: -kv[1])[:8]) or "깨끗")
    except Exception as x: print(f"  ~ check 못 돌림: {str(x)[:80]}")
    print(f"{md}  ·  레일 릴스 {END}s · 장면 {len(reel['beats'])} · 부품 {len(segs)}")
    if render:
        mp4 = ENG / "out" / "릴스" / f"{stem}-rail.mp4"; mp4.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npx", "hyperframes", "render", "-o", str(mp4)], cwd=md, check=True)
        print(mp4)
    return md

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    build(json.load(open(a[0], encoding="utf-8")), pathlib.Path(a[0]).stem, "--render" in sys.argv)
