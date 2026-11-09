#!/usr/bin/env python
"""클론 목소리(Chatterbox): jobs.json {"ref": 참조녹음.wav, "lines": [{"text","out"}]} → out 마다 wav.
엔진/.voice 의 파이썬으로 돈다 (build_rail.py 가 부른다). 모델은 한 번만 올린다."""
import json, sys
import torch, torchaudio

jobs = json.load(open(sys.argv[1]))
dev = "mps" if torch.backends.mps.is_available() else "cpu"
_load = torch.load  # 체크포인트가 cuda 로 저장돼 있어 맥에선 자리만 바꿔 읽는다
torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": torch.device(dev)})
from chatterbox.tts import ChatterboxTTS
model = ChatterboxTTS.from_pretrained(device=dev)
exg = jobs.get("exaggeration", 0.5)   # 과장 다듬은 판(0.25~0.4)은 뉴스 같거나 엉망 (11/04 하림님)
cfg = jobs.get("cfg_weight", 0.6)     # F판 채택 (11/04 하림님): 빠름(0.5)과 늘어짐(0.7)의 중간 템포
spd = jobs.get("speed", 1.0)          # 첫 판이 살짝 느리다 → 피치 그대로 템포만 (ffmpeg atempo)
import subprocess
for L in jobs["lines"]:
    wav = model.generate(L["text"], audio_prompt_path=jobs["ref"], exaggeration=exg, cfg_weight=cfg)
    torchaudio.save(L["out"], wav, model.sr)
    if spd != 1.0:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", L["out"], "-af", f"atempo={spd}", L["out"] + ".t.wav"], check=True)
        subprocess.run(["mv", L["out"] + ".t.wav", L["out"]], check=True)
    print("·", L["out"])
