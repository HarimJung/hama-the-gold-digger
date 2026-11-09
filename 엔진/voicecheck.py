#!/usr/bin/env python3
"""목소리 대조 (11/07 밤, 하림님 «대본이랑 한 개도 안 맞잖아»): 편마다 모든 줄의 캐시된 목소리를 받아 적은 글과 대본 줄을 대조한다.
  python3 엔진/voicecheck.py [--all | <key>...] [--purge] [--md]
  --purge  대조가 .5 미만인 줄의 목소리·받아 적기 캐시를 지운다 (다음 빌드가 차례로 다시 만든다)
결과: out/작업/voice-check.json · voice-check.md. 받아 적기가 없는 줄은 «없음»으로 적는다(빌드 때 생긴다).
원인 기록: 3 워커가 공용 say.txt 를 같이 써서 남의 줄 소리가 저장됐다 → build_rail.tts 가 줄마다 고유 파일을 쓰고, times() 의 목소리 관문이 안 맞으면 다시 만든다."""
import argparse, json, pathlib, sys
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P / "motion" / "rail")); sys.path.insert(0, str(P))
import build_rail as br, hook
POSTS = P.parent / "콘텐츠" / "찾은"; WORK = P / "out" / "작업"

def check(key, purge=False):
    post = json.load(open(POSTS / f"{key}.json", encoding="utf-8")); reel = post["rail"]
    voice, speed = reel.get("voice", "af_heart"), reel.get("speed", 1.0)
    rows = []
    for i, b in enumerate(reel["beats"]):
        quick = bool(b.get("nocap")) and i == 0 or (i == 1 and bool(b.get("nocap")))
        text = br.spoken(b["say"], quick); f = br.vpath(text, voice, speed * (1.15 if quick else 1.0))
        j = f.with_suffix(".words.json")
        if not f.exists(): rows.append({"i": i, "say": b["say"], "ratio": None, "state": "소리 없음"}); continue
        if not j.exists(): rows.append({"i": i, "say": b["say"], "ratio": None, "state": "받아 적기 없음"}); continue
        vr = br.voice_ratio(b["say"].split(), f)
        bad = vr is not None and vr < .5
        if bad and purge: f.unlink(missing_ok=True); j.unlink(missing_ok=True)
        rows.append({"i": i, "say": b["say"], "ratio": None if vr is None else round(vr, 2), "state": ("불일치→지움" if purge else "불일치") if bad else "맞음",
                     "heard": " ".join(w["text"] for w in json.load(open(j))) if j.exists() and bad else ""})
    return {"key": key, "lines": len(rows), "bad": sum(1 for r in rows if r["state"].startswith("불일치")), "missing": sum(1 for r in rows if "없음" in r["state"]), "rows": rows}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("keys", nargs="*"); ap.add_argument("--all", action="store_true"); ap.add_argument("--purge", action="store_true"); ap.add_argument("--md", action="store_true")
    a = ap.parse_args(); keys = a.keys or ([pathlib.Path(p).stem for p in hook.posts_all()] if a.all else [])
    if not keys: ap.print_help(); return 1
    res = [check(k, a.purge) for k in keys]
    WORK.mkdir(parents=True, exist_ok=True); json.dump(res, open(WORK / "voice-check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nb = sum(r["bad"] for r in res); nm = sum(r["missing"] for r in res); nl = sum(r["lines"] for r in res)
    for r in res:
        if r["bad"] or r["missing"]: print(f"  {'✗' if r['bad'] else '·'} {r['key']:36s} 줄 {r['lines']:2d} · 불일치 {r['bad']} · 없음 {r['missing']}")
    print(f"\n  목소리 대조 {len(res)}편 · {nl}줄 · 불일치 {nb} · 받아 적기 없음 {nm}{' · 지움 ' + str(nb) if a.purge else ''} → {WORK / 'voice-check.json'}")
    if a.md:
        md = [f"# 목소리 대조 — {len(res)}편 · {nl}줄 · 불일치 {nb} · 받아 적기 없음 {nm}", "", "줄마다 캐시된 목소리를 받아 적은 글(whisper)과 대본 줄을 대조. .5 미만 = 남의 소리. 티커를 못 알아듣는 줄은 .5~.7 로 낮게 나올 수 있다.", "",
              "| 편 | 줄 | 불일치 | 없음 | 불일치 줄 (대본 → 들린 말) |", "|---|---|---|---|---|"]
        for r in res:
            bad = "<br>".join(f"{x['i']}: {x['say'][:40]} → {x.get('heard', '')[:50]}" for x in r["rows"] if x["state"].startswith("불일치"))
            md.append(f"| {r['key']} | {r['lines']} | {r['bad']} | {r['missing']} | {bad} |")
        (WORK / "voice-check.md").write_text("\n".join(md) + "\n", encoding="utf-8"); print(f"  → {WORK / 'voice-check.md'}")
    return 0

if __name__ == "__main__": sys.exit(main())
