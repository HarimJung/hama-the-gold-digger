#!/usr/bin/env python3
"""관문. post.json 하나를 받아 훅·캡션·AI티·구조를 검사한다."""
import json,sys,subprocess,pathlib
import pathlib as _pl0,tempfile,re
P=pathlib.Path(__file__).parent
SK=P.parent/'하마-제작실/sources/instagram-agent/skills'
post=json.load(open(sys.argv[1],encoding='utf-8'))
fails=[];warns=[]
def run(cmd,**kw):
    return subprocess.run(cmd,capture_output=True,text=True,**kw).stdout

# 1 훅
hooks=post.get('hooks',{}).get('candidates',[])
if len(hooks)<3: fails.append(f"훅 후보 {len(hooks)}개 — 3개 이상 필요")
if len(set(h.strip().lower() for h in hooks))<len(hooks):
    fails.append("훅 후보에 같은 문장이 있다 — 서로 다른 방식으로 써야 한다")
# 헨리 방식: 후보는 10개, 서로 다른 방식, 화면 글자 10단어 이하
_modes=(post.get('hooks') or {}).get('modes') or []
if _modes:
    if len(_modes)!=len(hooks):
        fails.append(f"훅 {len(hooks)}개인데 방식 {len(_modes)}개 — 하나씩 짝이 맞아야 한다")
    if len(set(_modes))<len(_modes):
        fails.append("훅 방식이 겹친다 — 10가지 방식에서 서로 다르게 고른다")
_os=(post.get('hooks') or {}).get('on_screen','')
_HK=json.load(open(P/'hooks.json',encoding='utf-8'))
if _os and len(_os.split())>_HK['henry']['max_words']:
    fails.append(f"화면 글자 {len(_os.split())}단어 — {_HK['henry']['max_words']}단어 이하 (henry)")
else:
    f=tempfile.NamedTemporaryFile('w',suffix='.txt',delete=False,encoding='utf-8')
    f.write('\n'.join(hooks));f.close()
    out=run(['python3','hookscore.py',f.name],cwd=SK/'ig-reel')
    m=re.search(r'->\s+([\d.]+)',out)
    top=float(m.group(1)) if m else 0
    print(out.strip()[:400]);print()
    if top<50: fails.append(f"훅 최고점 {top} — 50 미만, 주제로 되돌아간다")
    elif top<80: warns.append(f"훅 최고점 {top} — 80 미만, 레버로 올릴 것")
    else: print(f"  훅 {top}  OK")

# 2 화면 훅 = 표지 소제목. 세 조각(대상+숫자+이득/함정)이 들어가야 해서 hooks.json cover.hook.max_words (10) 가 기준이다
#   (2026-11-03 3차 공식. 옛 6단어 기준은 숫자 하나짜리 표지용이었다)
_CFm=json.load(open(_pl0.Path(__file__).parent/'hooks.json',encoding='utf-8'))['cover']['hook']['max_words']
sh=post.get('hooks',{}).get('on_screen','')
if not sh: fails.append("화면 훅 없음")
elif len(sh.split())>_CFm: warns.append(f"화면 훅 {len(sh.split())}단어 — {_CFm}단어 이하")
# 2-1 ② 약속 줄 (hooks.json one_second, 2026-11-04). ① 훅 = 첫마디, ② 약속이 둘째 마디
#   단어 수·문구 모양은 경고만 (11/04 «너무 엄격하게 하지 마»). 답 노출은 막는다
_PR=_HK['promise']; _pr=(post.get('hooks') or {}).get('promise','')
if not _pr: fails.append("② 약속 줄 없음 — python3 엔진/hook.py --make 로 ① 과 짝으로 만든다")
else:
    if not _pr.startswith(_PR['starts']): warns.append(f"② 약속이 «{_PR['starts']}» 로 시작하지 않는다")
    if len(_pr.split())>_PR['max_words']: warns.append(f"② 약속 {len(_pr.split())}단어 — {_PR['max_words']}단어 이하")
    _hit=[a for a in _HK['cover']['answer_words'] if a in _pr.lower()]
    if _hit: fails.append(f"② 약속에 답이 있다 {_hit} — 방법은 숨긴다")
if sh and (post.get('hooks') or {}).get('spoken','').strip()!=sh.strip():
    warns.append("화면 훅과 첫마디가 다르다 — 같은 문장이어야 한다 (henry)")

# 3 캡션
cap=post.get('caption','')
if not cap: fails.append("캡션 없음")
else:
    f=tempfile.NamedTemporaryFile('w',suffix='.txt',delete=False,encoding='utf-8')
    f.write(cap);f.close()
    out=run(['python3','caption.py',f.name],cwd=SK/'ig-caption')
    print(out.strip()[-700:]);print()
    if 'FAIL' in out: fails.append("캡션 린터 FAIL 항목 있음")
    out2=run(['python3','detect.py',f.name],cwd=SK/'ig-human')
    m=re.search(r'HUMAN SCORE\s+\S+\s+([\d.]+)',out2)
    hs=float(m.group(1)) if m else 0
    print(f"  ig-human {hs}")
    if hs<70: fails.append(f"ig-human {hs} — 70 미만 (축약형 확인)")

# 4 구조
sl=post.get('slides',[])
types=[s['type'] for s in sl]
# 역할 표. 재현 장 6종(2026-11-03 승인)이 기존 장과 같은 자리를 메운다.
# 장 이름이 늘어도 «표지·스테이크·저장·CTA 가 있나» 라는 질문은 안 바뀐다.
ROLE={'cover':'cover','hero':'cover','table':'key','grid':'key',
      'stake':'stake','flow':'stake','two':'stake','idea':'body','decoder':'body','mini':'body',
      'key':'key','recap':'key',
      'cta':'cta','do':'cta'}
roles={ROLE.get(x) for x in types}
# 장 수는 내용이 정한다 (하림님 2026-11-03). 1~3장이라도 포모가 오고 다 알면 끝이다. 6장 틀은 없다.
if not (1<=len(sl)<=10): fails.append(f"{len(sl)}장 — 1~10장")
if 'cover' not in roles: fails.append("표지(hero) 없음 — 1장짜리라도 표지는 있어야 한다")
if len(sl)>=4:
    for need,label in (('stake','스테이크'),('key','저장 장'),('cta','CTA')):
        if need not in roles: warns.append(f"{len(sl)}장인데 {label} 역할이 없다 — 길게 갈 거면 있어야 한다")
import re as _re
strip=lambda t: _re.sub(r'\s+',' ', _re.sub(r'<[^>]+>',' ', t or '')).strip()
for i,s in enumerate(sl):
    if s['type']=='idea':
        w=len(strip(s.get('body','')).split())
        if w>25: fails.append(f"{i+1}장 본문 {w}단어 — 25단어 이하")
    if s['type']=='decoder':
        w=len(strip(s.get('meaning','')).split())+len(strip(s.get('example','')).split())
        if w>25: fails.append(f"{i+1}장 본문 {w}단어 — 25단어 이하")

# 4-0 build.py 가 쓰는 필수 필드. 없으면 READY 받고 빌드에서 죽는다
NEED={'cover':('promise',),'stake':('text',),'idea':('title','figure','figure_label','body'),
      'decoder':('title','base','suffix','meaning'),'key':('title','rows'),
      'recap':('title','rows'),'cta':('text','button','fine'),
      # 표지 언어 장. 필드 이름은 build.py 의 mk_inner 와 같아야 한다 (속장은 kicker + title 제목판)
      'hero':('kicker','hook'),
      'table':('kicker','title','h1','h2','rows','note'),
      'grid':('kicker','title','cols','rows','note'),
      'flow':('kicker','title','lead','steps','source_label'),
      'two':('kicker','title','boxes','source_label'),
      'mini':('kicker','title','lead','rows','source_label'),
      'do':('kicker','title','lead','checks','button','fine')}
for i,s_ in enumerate(sl):
    if s_['type']=='cover' and s_.get('variant')=='ticket':
        need=('kicker','promise','rows')
    else:
        need=NEED.get(s_['type'],())
    for k in need:
        if not s_.get(k): fails.append(f"{i+1}장 '{k}' 비어 있음 — build.py 가 요구한다")
for i,s_ in enumerate(sl):
    # 속장 제목판은 1초에 읽혀야 한다 — 표지 소제목과 같은 10단어 기준
    if s_.get('title') and s_['type']!='cover' and len(strip(s_['title']).split())>10:
        fails.append(f"{i+1}장 제목 {len(strip(s_['title']).split())}단어 — 10단어 이하 (제목판은 1초)")
    if s_['type']=='grid' and not (3<=len(s_.get('rows') or [])<=6 and 2<=len(s_.get('cols') or [])<=4):
        fails.append(f"{i+1}장 조회표 {len(s_.get('rows') or [])}행 × {len(s_.get('cols') or [])}열 — 3~6행 × 2~4열 (레퍼 밀도, 글자 24px 유지)")
    if s_['type']=='table' and not (2<=len(s_.get('rows') or [])<=6):
        fails.append(f"{i+1}장 표 {len(s_.get('rows') or [])}행 — 2~6행. 글자를 줄이지 말고 행을 줄인다")
    if s_['type']=='flow' and len(s_.get('steps') or [])!=3:
        fails.append(f"{i+1}장 흐름 칸 {len(s_.get('steps') or [])}개 — 3개여야 격자가 선다")
    if s_['type'] in ('two','do') and len(s_.get('boxes') or s_.get('checks') or [])!=2:
        fails.append(f"{i+1}장 두 칸 비교가 2칸이 아니다")
for k in ('title','series','source_note'):
    if not post.get(k): fails.append(f"post '{k}' 비어 있음")

# 4-1 물건 — 한 편은 독자가 가져가는 물건 하나를 만들어 준다 (plan.json save_card)
if not post.get('object'):
    fails.append("object 없음 — 이 편이 만들어 주는 물건의 이름이 있어야 한다 (plan.json save_card)")

# 4-2 칸 = 장 = 출처. 사실이 모자라면 장으로 때우지 않는다
kan=[s for s in sl if s['type'] in ('idea','decoder','flow','two','mini')]
srcs=post.get('sources') or []
ns=len({(x.get('url') or x.get('what')) for x in srcs})
if ns < len(kan):
    fails.append(f"칸 {len(kan)}개인데 서로 다른 출처 {ns}개 — 칸마다 다른 출처가 있어야 한다")

# 4-3 점수 매긴 훅이 실제로 화면에 찍히는지. 안 찍히면 그 점수는 의미가 없다
spoken=(post.get('hooks') or {}).get('spoken','').strip()
cov=next((s for s in sl if ROLE.get(s['type'])=='cover'), None)
def hook_text(c):
    h=c.get('hook') or {}
    return (h.get('pre','')+str(h.get('num') if h.get('num') is not None else '')+h.get('post','')).strip()
if cov and cov['type']=='hero':
    line=strip(hook_text(cov))
    if line and hooks and line not in [strip(h) for h in hooks]:
        fails.append(f"표지에 찍힌 줄 '{line}' 이 훅 후보에 없다 — 안 재고 올린 줄이다")
elif cov and cov['type']=='table':
    line=strip(cov.get('sub',''))
    if line and hooks and line not in [strip(h) for h in hooks]:
        fails.append(f"표지에 찍힌 줄 '{line}' 이 훅 후보에 없다 — 안 재고 올린 줄이다")
elif spoken and cov:
    shown=(strip(cov.get('figure','')) + ' ' + strip(cov.get('promise',''))).strip()
    if spoken not in shown:
        fails.append("점수 매긴 훅이 표지에 없다 — hooks.spoken 이 화면에 안 찍힌다")

# 4-4 1초 관문 — 표지는 1초 안에 «이득»이 보여야 한다 (하림님 2026-11-03)
if cov:
    hero=strip(cov.get('figure','')) if cov['type'] not in ('table','hero') else (
         f"{strip(cov.get('a',''))} → {strip(cov.get('b',''))}" if cov['type']=='table' else hook_text(cov))
    if cov['type']=='hero':
        # 표지 공식 2차 (hooks.json cover). 주제어가 제일 크고, 훅은 구체+숫자, 답은 없다
        CF=json.load(open(_pl0.Path(__file__).parent/'hooks.json',encoding='utf-8')).get('cover',{})
        pill=[w for w in strip(cov.get('kicker','')).replace('·',' ').split() if w]
        SER=json.load(open(_pl0.Path(__file__).parent/'hooks.json',encoding='utf-8'))['series']['title']
        want=SER.get(post.get('category',''),'')
        tp=strip(cov.get('topic') or want).split(); hk=hook_text(cov).split(); sub=strip(cov.get('sub','')).split()
        if len(pill)>CF['pill']['max_words']: fails.append(f"F-1 알약 {len(pill)}단어 — {CF['pill']['max_words']} 이하")
        if not want: fails.append(f"F-2 카테고리 '{post.get('category')}' 의 대제목이 hooks.json series 에 없다")
        elif ' '.join(tp)!=want: fails.append(f"F-2 대제목 '{' '.join(tp)}' ≠ series '{want}' — 대제목은 지어내지 않는다")
        if not _re.search(r'\b(you|your)\b', ' '.join(hk).lower()): fails.append("F-3 소제목에 대상(you/your)이 없다 — 세 조각 중 하나가 빠졌다")
        if len(hk)>CF['hook']['max_words']: fails.append(f"F-3 훅 {len(hk)}단어 — {CF['hook']['max_words']} 이하")
        if CF['hook']['needs_number'] and not _re.search(r'[0-9$€£%]', ' '.join(hk)): fails.append("F-3 훅에 숫자가 없다 — 내 돈이 얼마나 인지 1초에 안 보인다")
        both=(' '.join(tp+hk)).lower()
        if not any(f in both for f in CF['fomo_words']): fails.append("F-3 손해·이득 말이 없다 — 포모가 안 온다 (hooks.json cover.fomo_words)")
        if len(sub)>CF['sub']['max_words']: fails.append(f"F-4 부제 {len(sub)}단어 — {CF['sub']['max_words']} 이하")
        alltxt=(' '.join(tp+hk+sub)).lower()
        hitw=[a for a in CF['answer_words'] if a in alltxt]
        if hitw: fails.append(f"F-4 표지에 답이 있다 {hitw} — 이유·방법·결론은 속장으로 (henry)")
        if len(tp)+len(hk)+len(sub)>CF['total_max_words']: fails.append(f"F-5 표지 글 {len(tp)+len(hk)+len(sub)}단어 — {CF['total_max_words']} 이하")
    elif cov['type']=='table':
        rows=cov.get('rows') or []
        if len(rows)<3: fails.append(f"S-1 표 줄 {len(rows)}개 — 3개 이상이어야 화면이 선다")
        if not _re.search(r'[0-9$€£%]', hero):
            fails.append(f"S-1 표지 주인공이 '{hero}' — A→B 제목에 숫자나 금액이 있어야 한다")
    elif cov.get('variant')=='ticket':
        # 무대가 주인공인 표지. 줄이 3개 이상이고 금색 칸이 하나 있어야 «물음»이 생긴다
        rows=cov.get('rows') or []
        if len(rows)<3: fails.append(f"S-1 티켓 줄 {len(rows)}개 — 3개 이상이어야 화면이 선다")
        if not any(r.get('gold') for r in rows): fails.append("S-1 티켓에 금색 칸이 없다 — 눈이 멈출 자리가 없다")
    elif not _re.search(r'[0-9$€£%]', hero):
        fails.append(f"S-1 표지 주인공이 '{hero}' — 숫자나 금액이어야 한다. 코드·글자는 1초에 안 읽힌다")
    # S-2 이득 또는 손해가 말로 박혀 있어야 한다
    GAIN=('stop','save','keep','pay','cost','costs','lose','loses','wast','make','earn','skip','avoid','free','miss','wrong','disappear','vanish','gone','leak','charge','taxed')
    # 재현 표지에서 사람이 읽는 글은 sub 한 줄이다. note 는 발띠 위 참고라 1초에 안 읽는다
    body=(strip(cov.get('sub','')).lower() if cov['type']=='table'
          else (strip(cov.get('topic',''))+' '+hook_text(cov)+' '+strip(cov.get('sub',''))).lower() if cov['type']=='hero'
          else (strip(cov.get('promise',''))+' '+strip(cov.get('sub',''))).lower())
    if cov['type']=='hero': body+=' '+strip(cov.get('promise','')).lower()   # ② 약속이 이득 자리다 (one_second)
    if not any(g in body for g in GAIN+tuple(_HK['cover']['fomo_words'])):
        fails.append("S-2 표지에 이득·손해가 없다 — 주제만 말하고 있다")
    # S-4 저장 이유(물건)가 훅 위에
    if not post.get('object'):
        fails.append("S-4 표지에 물건 이름이 없다 — 왜 저장하는지가 1초에 안 보인다")
    # S-5 표지에서 읽는 글 15단어 이하
    w=len(body.split())-(len(strip(cov.get('promise','')).split()) if cov['type']=='hero' else 0)   # ② 는 따로 잰다
    if w>15: fails.append(f"S-5 표지 글 {w}단어 — 15단어 이하. 읽어야 아는 건 실패")
    # S-6 훅이 공식 라이브러리 안에 있어야 한다
    fid=(post.get('hooks') or {}).get('formula')
    import pathlib as _pl
    HK=json.load(open(_pl.Path(__file__).parent/'hooks.json',encoding='utf-8'))
    ids=[x['id'] for x in HK['formulas']]
    if fid not in ids:
        fails.append(f"S-6 훅 공식 '{fid}' 이 hooks.json 에 없다 — 공식 {ids} 중 하나를 써야 한다")

# 5 출처·금지어
_HK=json.load(open(_pl0.Path(__file__).parent/'hooks.json',encoding='utf-8'))
# 면책은 막으면 안 된다. "not guaranteed" 를 "guaranteed" 로 잡던 버그.
# 부정어가 앞에 있으면 면책이다. "Nothing here is guaranteed" 를 권유로 잡던 버그.
NEG=_re.compile(r"\b(not|no|nothing|never|n't|아님|아닙니다)\b[^.!?]{0,40}?(guaranteed|guarantee|promise|보장)")
def scan(label,text):
    t=(text or '').lower()
    t=NEG.sub(' ',t)
    for m in _HK.get('indirect',{}).get('map',[]):
        if m['direct'] in t:
            fails.append(f"{label}에 직접 표현 '{m['direct']}' — 간접으로: \"{m['indirect']}\"")
for i,s_ in enumerate(sl):
    scan(f"{i+1}장", json.dumps(s_,ensure_ascii=False))
scan("캡션", post.get('caption',''))          # 레드팀: 여기가 비어 있었다
scan("훅", json.dumps(post.get('hooks',{}),ensure_ascii=False))

if not post.get('sources'): fails.append("숫자 출처 없음 — 승인됨 불가")

# 5-1 AI 티는 캡션만이 아니라 사람이 보는 슬라이드 글에도 돌린다
slide_text=' '.join(strip(json.dumps(s,ensure_ascii=False)) for s in sl)

# 결격만 막는다 (하림님 11/04 «만드는 게 우선, 너무 촘촘하게 하지 마»). 나머지는 전부 경고로 보고 사람이 본다
HARD=('비어 있음','표지(hero) 없음','화면 훅 없음','캡션 없음','숫자 출처 없음','직접 표현')
warns+=[f_ for f_ in fails if not any(h in f_ for h in HARD)]; fails=[f_ for f_ in fails if any(h in f_ for h in HARD)]
print('\n'+'='*54)
for w in warns: print('  WARN ',w)
for f_ in fails: print('  FAIL ',f_)
print('  VERDICT', 'BLOCKED' if fails else ('REVIEW' if warns else 'READY'))
if not fails:
    print('  다음: python3 엔진/ink.py <표지 PNG>  — 채움·빈 띠·가로폭은 픽셀로 잰다')
sys.exit(1 if fails else 0)
