#!/usr/bin/env python3
"""레일 감독·빌드 래퍼. 실제 일은 motion/rail/director.py(대본·매핑) 와 motion/rail/build_rail.py(레일 HTML·TTS·렌더) 가 한다.
옛 캐러셀 덱 빌더(template.html·--reel·--motion)는 2026-11-07 대청소에서 뺐다. 캐러셀은 안 한다(11/07 하림님).

  python3 엔진/build.py <post.json> --direct [--dry|--force] [--render]   대본 새로 + 매핑 (모델 1회)
  python3 엔진/build.py <post.json> --redirect [--render]                 대본 그대로, 매핑만 새 규칙으로 (모델 없이)
  python3 엔진/build.py <post.json> --reopen [--render]                   훅만 바뀐 편: 첫 두 비트·첫 장면만 교체
  python3 엔진/build.py <post.json> --remap [--render]                    대본 그대로, 모션 데이터만 다시
  python3 엔진/build.py <post.json> --rail [--render]                     레일 HTML (+MP4) 만
일괄은 hook.py rebuild --all 이 이 네 단계를 편마다 부른다."""
import json,sys,pathlib
P=pathlib.Path(__file__).parent
if '--direct' in sys.argv:   # 레일 감독: 대본 쓰고 모션 매핑까지 (motion/rail/director.py)
    sys.path.insert(0,str(P/'motion'/'rail')); import director
    director.main([a for a in sys.argv[1:] if not a.startswith('--')][0],'--dry' in sys.argv,'--force' in sys.argv,'--render' in sys.argv); sys.exit()
if '--redirect' in sys.argv:   # 대본 그대로, 쪼개기·주가 창·부품 매핑만 새 규칙으로 다시 (모델 없이, 11/07)
    sys.path.insert(0,str(P/'motion'/'rail')); import director
    director.main([a for a in sys.argv[1:] if not a.startswith('--')][0],False,True,'--render' in sys.argv,True); sys.exit()
if '--reopen' in sys.argv:   # 훅만 바뀐 편: 첫 두 비트 + 첫 장면만 교체하고 레일 다시 (11/06). 대본 나머지는 그대로
    sys.path.insert(0,str(P/'motion'/'rail')); import director, build_rail
    _a=[a for a in sys.argv[1:] if not a.startswith('--')][0]; _d=json.load(open(_a,encoding='utf-8'))
    director.reopen(_d,pathlib.Path(_a).stem); json.dump(_d,open(_a,'w',encoding='utf-8'),ensure_ascii=False,indent=2); open(_a,'a',encoding='utf-8').write('\n')
    build_rail.build(_d,pathlib.Path(_a).stem,'--render' in sys.argv); sys.exit()
if '--remap' in sys.argv:   # 대본 그대로, 모션 데이터만 다시 (부품 규칙이 바뀌었을 때, 11/06)
    sys.path.insert(0,str(P/'motion'/'rail')); import director, build_rail
    _a=[a for a in sys.argv[1:] if not a.startswith('--')][0]; _d=json.load(open(_a,encoding='utf-8'))
    director.remap(_d,pathlib.Path(_a).stem); json.dump(_d,open(_a,'w',encoding='utf-8'),ensure_ascii=False,indent=2); open(_a,'a',encoding='utf-8').write('\n')
    build_rail.build(_d,pathlib.Path(_a).stem,'--render' in sys.argv); sys.exit()
if '--rail' in sys.argv:   # 레일 릴스는 motion/rail/build_rail.py 가 맡는다
    sys.path.insert(0,str(P/'motion'/'rail')); import build_rail
    _a=[a for a in sys.argv[1:] if not a.startswith('--')][0]
    build_rail.build(json.load(open(_a,encoding='utf-8')),pathlib.Path(_a).stem,'--render' in sys.argv); sys.exit()
raise SystemExit(__doc__)
