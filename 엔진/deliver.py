#!/usr/bin/env python3
"""납품 층 (11/07 v2). 렌더된 MP4 를 실제 파일로 잰다: 라우드니스(−14 LUFS)·정지·검은 프레임·첫 프레임·릴스 스펙. 필요하면 소리만 맞춘다.
ffmpeg 만 쓴다 (ffmpeg-skill 설치 없이 돈다). 영상 스트림은 복사, 소리만 다시 쓴다.

  python3 엔진/deliver.py <key>... | --all [--norm] [--md] [--workers 3]
  --norm   라우드니스가 목표(−14 LUFS)에서 1 LU 넘게 벗어나면 loudnorm 2패스로 맞춰 같은 파일에 쓴다. 없으면 재기만
  --md     out/작업/deliver.md 표도 쓴다

결과: out/작업/deliver.json (편별). 경고만 — FAIL 은 넷뿐(하림님 11/05·11/06). «정지(실측)» 기준은 hooks.json grammar.still_max (없으면 5초).
정지는 자막까지 포함해 화면 전체가 안 바뀐 구간이다(review 의 «정지»는 자막을 뺀 트윈 기준이라 둘은 다른 자다). 끝 hold(3.5초, CTA 가 서 있는 설계)는 뺀다."""
import argparse, concurrent.futures, io, json, os, pathlib, re, subprocess, sys, tempfile

P = pathlib.Path(__file__).parent
REELS = P / "out" / "릴스"; WORK = P / "out" / "작업"; POSTS = P.parent / "콘텐츠" / "찾은"
TARGET_I, TARGET_TP, TARGET_LRA = -14.0, -1.0, 11.0
SPEC = {"w": 1080, "h": 1920, "fps": 30, "vcodec": "h264", "acodec": "aac", "max_dur": 90}
FREEZE_MIN = 1.5   # 이보다 긴 정지는 전부 적는다 (하림님 11/07 «정지 너무 싫어, 정지하면 넘긴다»)
try: STILL_MAX = float((json.load(open(P / "hooks.json", encoding="utf-8")).get("grammar") or {}).get("still_max", 5.0))
except Exception: STILL_MAX = 5.0

def run(args, timeout=600):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)

def probe(f):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate:format=duration", "-of", "json", str(f)])
    d = json.loads(r.stdout or "{}"); out = {"dur": round(float((d.get("format") or {}).get("duration") or 0), 2)}
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            a, b = (s.get("r_frame_rate") or "0/1").split("/"); out.update(w=s.get("width"), h=s.get("height"), fps=round(int(a) / max(int(b), 1), 2), vcodec=s.get("codec_name"))
        elif s.get("codec_type") == "audio": out.update(acodec=s.get("codec_name"), ar=int(s.get("sample_rate") or 0))
    return out

def loud(f):
    """1패스: 지금 라우드니스. loudnorm 이 찍는 JSON 을 읽는다."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af", f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m: return None
    j = json.loads(m.group(0))
    return {k: float(j[k]) for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")}

def normalize(f, m):
    """2패스: 1패스 측정값을 넣어 선형으로 맞춘다 (dynamic 보다 소리 모양을 덜 건드린다). 영상은 복사. 같은 이름으로 바꿔치기."""
    af = (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=summary")
    tmp = f.with_suffix(".norm.tmp.mp4")
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(f), "-af", af, "-ar", "48000", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp)])
    if r.returncode or not tmp.exists() or tmp.stat().st_size < 1000:
        tmp.unlink(missing_ok=True); raise RuntimeError("loudnorm 실패 " + r.stderr[-200:])
    os.replace(tmp, f)
    return loud(f)

def content(f, hold=3.5, dur=None):
    """정지·검은 구간 (freezedetect / blackdetect) + 첫 프레임 평탄도. 끝 hold 안에서 시작한 정지는 설계라 뺀다."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-an", "-vf", f"freezedetect=n=0.001:d={FREEZE_MIN},blackdetect=d=0.4:pic_th=0.98", "-f", "null", "-"])
    end = dur or 0; fr = []
    for ev in re.findall(r"freeze_(start|duration): ([\d.]+)", r.stderr):   # 끝까지 이어지는 정지는 duration 줄이 없다 (레드팀 2) → 끝 − 시작
        if ev[0] == "start": fr.append([float(ev[1]), None])
        elif fr and fr[-1][1] is None: fr[-1][1] = float(ev[1])
    freezes = [(round(a, 1), round((b if b is not None else max(0.0, end - a)), 1)) for a, b in fr if not (end and (a >= end - hold - .6 or (b is None and a >= end - hold - 1.5)))]   # 끝까지 이어지는 정지는 설계된 끝 hold(CTA 가 서 있는 3.5초)+1.5초 안에서 시작하면 뺀다
    blacks = [(round(float(a), 1), round(float(b), 1)) for a, b in re.findall(r"black_start:([\d.]+) black_end:[\d.]+ black_duration:([\d.]+)", r.stderr)]
    flat = None
    try:   # 첫 프레임: 알약·숫자·얼굴이 있어야 한다 (11/06 발견 15: 0초 빈 프레임). 밝기 표준편차가 작으면 빈 화면
        from PIL import Image, ImageStat
        im = Image.open(io.BytesIO(subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout)).convert("L")
        flat = round(ImageStat.Stat(im).stddev[0], 1)
    except Exception: pass
    return {"freezes": freezes, "blacks": blacks, "first_std": flat}

def hold_of(key):
    try: return float(((json.load(open(POSTS / f"{key}.json", encoding="utf-8")).get("rail") or {}).get("hold") or 3.5))
    except Exception: return 3.5

def check(key, norm=False):
    f = REELS / f"{key}-rail.mp4"
    if not f.exists(): return {"key": key, "error": "MP4 없음"}
    pr = probe(f); lm = loud(f); out = {"key": key, **pr, "lufs": lm and round(lm["input_i"], 1), "tp": lm and round(lm["input_tp"], 1), "normalized": False}
    if norm and lm and (abs(lm["input_i"] - TARGET_I) > 1.0 or lm["input_tp"] > TARGET_TP + .1):
        after = normalize(f, lm); out.update(normalized=True, lufs_after=after and round(after["input_i"], 1), tp_after=after and round(after["input_tp"], 1))
    ct = content(f, hold_of(key), pr.get("dur")); out.update(ct)
    warns = []
    if (pr.get("w"), pr.get("h")) != (SPEC["w"], SPEC["h"]): warns.append(f"크기 {pr.get('w')}×{pr.get('h')}")
    if pr.get("fps") and abs(pr["fps"] - SPEC["fps"]) > .5: warns.append(f"fps {pr['fps']}")
    if pr.get("vcodec") != SPEC["vcodec"] or pr.get("acodec") != SPEC["acodec"]: warns.append(f"코덱 {pr.get('vcodec')}/{pr.get('acodec')}")
    if pr.get("dur", 0) > SPEC["max_dur"]: warns.append(f"길이 {pr['dur']}s > {SPEC['max_dur']}")
    cur = out.get("lufs_after") if out["normalized"] else out["lufs"]
    if cur is not None and abs(cur - TARGET_I) > 1.0: warns.append(f"소리 {cur} LUFS (목표 {TARGET_I:.0f})")
    long_ = [x for x in ct["freezes"] if x[1] >= STILL_MAX]
    if long_: warns.append("정지(실측) " + " · ".join(f"{d}s@{t}s" for t, d in sorted(long_, key=lambda x: -x[1])[:3]))
    if ct["blacks"]: warns.append(f"검은 프레임 {len(ct['blacks'])}")
    if ct["first_std"] is not None and ct["first_std"] < 6: warns.append(f"첫 프레임 빔 (std {ct['first_std']})")
    out["warns"] = warns
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("keys", nargs="*"); ap.add_argument("--all", action="store_true"); ap.add_argument("--norm", action="store_true"); ap.add_argument("--md", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    keys = a.keys or ([p.name[:-9] for p in sorted(REELS.glob("*-rail.mp4"))] if a.all else [])
    if not keys: ap.print_help(); return 1
    WORK.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(a.workers) as ex: rows = list(ex.map(lambda k: check(k, a.norm), keys))
    jf = WORK / "deliver.json"; prev = {r["key"]: r for r in (json.load(open(jf, encoding="utf-8")) if jf.exists() else [])}
    prev.update({r["key"]: r for r in rows}); jf.write_text(json.dumps(list(prev.values()), ensure_ascii=False, indent=1), encoding="utf-8")   # 부분 실행은 합친다
    n_warn = sum(1 for r in rows if r.get("warns"))
    for r in rows:
        if r.get("error"): print(f"  ✗ {r['key']:36s} {r['error']}"); continue
        fz = " ".join(f"{d}s@{t}s" for t, d in r["freezes"]) or "—"
        print(f"  {'~' if r['warns'] else '✓'} {r['key']:36s} {r['dur']:5.1f}s  {r['lufs']!s:>6} LUFS{' → ' + str(r['lufs_after']) if r['normalized'] else ''}  정지 {fz}  {' · '.join(r['warns'])}")
    print(f"\n  납품 검사 {len(rows)}편 · 경고 {n_warn} · 소리 맞춤 {sum(1 for r in rows if r.get('normalized'))} → {WORK / 'deliver.json'}")
    if a.md:
        rows = sorted(prev.values(), key=lambda r: r["key"]); n_warn = sum(1 for r in rows if r.get("warns"))   # 표는 합쳐진 전체
        md = [f"# 납품 검사 (실제 MP4) — {len(rows)}편 · 경고 {n_warn}", "", f"소리 목표 {TARGET_I:.0f} LUFS / TP {TARGET_TP:.0f} dB · 정지(실측) = 자막까지 멈춘 구간 ≥{FREEZE_MIN:.0f}초, 경고는 ≥{STILL_MAX:.0f}초 (끝 hold 제외) · 경고만, FAIL 아님", "",
              "| 편 | 길이 | LUFS | 정지(실측) | 경고 |", "|---|---|---|---|---|"]
        md += [f"| {r['key']} | {r.get('dur', '')} | {r.get('lufs', '')}{' → ' + str(r['lufs_after']) if r.get('normalized') else ''} | {' '.join(f'{d}s@{t}s' for t, d in r.get('freezes', [])) or '—'} | {' · '.join(r.get('warns') or []) or ('' if not r.get('error') else r['error'])} |" for r in rows]
        (WORK / "deliver.md").write_text("\n".join(md) + "\n", encoding="utf-8"); print(f"  → {WORK / 'deliver.md'}")
    return 0

if __name__ == "__main__":
    if "--selftest" in sys.argv:   # 자가 검사: 측정 JSON 파싱과 끝 hold 제외
        import types
        fake = types.SimpleNamespace(stderr='[Parsed_loudnorm_0 @ 0x1] \n{\n\t"input_i" : "-19.51",\n\t"input_tp" : "-2.42",\n\t"input_lra" : "1.70",\n\t"input_thresh" : "-29.65",\n\t"output_i" : "-14.03",\n\t"output_tp" : "-1.00",\n\t"output_lra" : "1.70",\n\t"output_thresh" : "-24.16",\n\t"normalization_type" : "dynamic",\n\t"target_offset" : "0.03"\n}\n')
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", fake.stderr, re.S); j = json.loads(m.group(0)); assert float(j["input_i"]) == -19.51
        evs = re.findall(r"freeze_(start|duration): ([\d.]+)", "x freeze_start: 10.9\ny freeze_duration: 3.27\nz freeze_end: 14.2\nx freeze_start: 40.0\n"); fr = []
        for ev in evs:
            if ev[0] == "start": fr.append([float(ev[1]), None])
            elif fr and fr[-1][1] is None: fr[-1][1] = float(ev[1])
        fz = [(a, round(b if b is not None else 59.8 - a, 2)) for a, b in fr if not a >= 59.8 - 3.5 - .6]; assert fz == [(10.9, 3.27), (40.0, 19.8)], fz   # 끝까지 가는 정지도 잡는다
        print("deliver selftest ok"); sys.exit(0)
    sys.exit(main())
