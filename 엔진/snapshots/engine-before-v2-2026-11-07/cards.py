#!/usr/bin/env python3
"""캐러셀 엔진 (11/06 정본 공식): 릴스의 모션그래픽 UI 장면을 더 잘 보이게 4:5 정지 카드로.
한 장 = 릴스 장면 하나의 마지막 상태 (알약·숫자·장표·영수증·와이프·주가 창 그대로). 검정 바탕·한 단어 카드는 안 찍는다 (dark 비트 제외).
표지 = 첫 장면(알약 + 훅 + 약속 + 도장) · 마지막 = CTA(Comment WORD). reel_only 카테고리(fear)는 캐러셀 없음.

  python3 엔진/cards.py <key> | --all      → out/캐러셀/<key>/NN.png + contact.png
레일 HTML(out/작업/<key>-rail/)이 있어야 한다 (build.py --rail 또는 hook.py rebuild). 찍는 건 hyperframes snapshot, 자르는 건 PIL."""
import json, sys, pathlib, subprocess, argparse
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P))
import hook, shoot

W, H = 1080, 1350          # 4:5
CROP_TOP = 150             # 9:16 프레임에서 자르는 위 기준 (위 자막 205px 부터 들어온다)
MAX_CARDS = 10

def moments(post):
    """장면마다 마지막 상태 시각 = 다음 부품 비트 시작 − 0.25초 (전환 전). 첫 장면은 1.2초(도장 찍힌 뒤), 마지막은 끝 − 0.3초. dark 비트는 뺀다."""
    beats = post["rail"]["beats"]
    segs = []
    for b in beats:
        if b.get("part"): segs.append(b)
    out = []
    for i, b in enumerate(segs):
        nxt = segs[i + 1]["t0"] if i + 1 < len(segs) else None
        if b.get("dark"): continue
        t = 1.2 if i == 0 else (nxt - .25 if nxt else b["t1"] + 2.5)
        out.append((round(max(t, b["t0"] + .4), 2), b["part"]))
    return out[:MAX_CARDS]

def shoot_cards(key):
    path = P.parent / "콘텐츠" / "찾은" / f"{key}.json"; post = json.load(open(path, encoding="utf-8"))
    if post.get("category") in hook.HK["series"].get("reel_only", {}).get("list", []): print(f"  · {key}: 릴스만 (reel_only)"); return []
    md = P / "out" / "작업" / f"{key}-rail"
    if not (md / "index.html").exists(): print(f"  ✗ {key}: 레일 없음"); return []
    sys.path.insert(0, str(P / "motion" / "rail")); import build_rail
    build_rail.times(post["rail"])   # 비트 시각 (TTS 캐시라 빠르다)
    ms = moments(post)
    r = subprocess.run(["npx", "hyperframes", "snapshot", "--at", ",".join(str(t) for t, _ in ms), "--json"], cwd=md, capture_output=True, text=True)
    snaps = sorted((md / ".hyperframes" / "artifacts" / "snapshots").glob("*/"), key=lambda p: p.stat().st_mtime)
    if not snaps: print(f"  ✗ {key}: 스냅숏 실패 {r.stderr[:80]}"); return []
    frames = sorted(snaps[-1].glob("frame-*.png"))[:len(ms)]
    from PIL import Image
    out = P / "out" / "캐러셀" / key; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    pngs = []
    for i, (f, (t, part)) in enumerate(zip(frames, ms)):
        im = Image.open(f).crop((0, CROP_TOP, W, CROP_TOP + H))
        dst = out / f"{i + 1:02d}-{part}.png"; im.save(dst); pngs.append(dst)
    if len(pngs) > 1: shoot.contact(pngs, out / "contact.png", cols=5)
    print(f"  {key}: {len(pngs)}장 ({' → '.join(p for _, p in ms)}) → {out}")
    return pngs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("key", nargs="?"); ap.add_argument("--all", action="store_true"); a = ap.parse_args()
    keys = [pathlib.Path(p).stem for p in hook.posts_all()] if a.all or not a.key else [a.key]
    n = 0
    for k in keys:
        try: n += bool(shoot_cards(k))
        except Exception as x: print(f"  ✗ {k}: {str(x)[:120]}")
    print(f"  캐러셀 {n}/{len(keys)}")

if __name__ == "__main__":
    main()
