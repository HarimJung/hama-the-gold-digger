#!/usr/bin/env python3
"""post.json -> 덱 HTML. 디자인 토큰은 template.html 한 곳에만 있다.

한 편은 plan.json 의 save_card = «독자가 가져가는 물건» 을 만들어 주는 과정이다.
칸 하나 = 장 하나 = 출처 하나. 그 규칙은 check.py 가 강제한다.

장 종류는 두 묶음이다.
  표지 언어 장 (hero two table flow mini do) — 2026-11-03 밤, 속장을 표지 언어로 통일했다.
    정본 CSS 는 template.html 의 .sl.hero / .sl.inner 한 곳. 레퍼 재현본 deck.html 은 기록으로 동결.
    장 수는 내용이 정한다. 표지 1장 + 필요한 속장만. 6장 틀 없음.
  기존 장 (cover stake idea decoder key recap cta) — cqw 무대. 그대로 둔다.

릴스: python3 엔진/build.py <post.json> --reel  →  out/<stem>-reel/  (HyperFrames 프로젝트, 9:16, 장당 6초)
     그 뒤  cd out/<stem>-reel && npx hyperframes check --json && npx hyperframes render --quality looks -o ../<stem>.mp4
레일 감독: python3 엔진/build.py <post.json> --direct [--dry|--force] [--render]  →  대본·모션 매핑을 엔진이 짠다
레일 릴스: python3 엔진/build.py <post.json> --rail [--render]  →  out/<stem>-rail/ (mrcreates 문법, reel{} 대본, 틀은 motion/rail/)
"""
import json,sys,pathlib,html,shutil,re
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
post=json.load(open([a for a in sys.argv[1:] if not a.startswith('--')][0],encoding='utf-8'))
if post.get('category') in json.load(open(P/'hooks.json',encoding='utf-8'))['series'].get('reel_only',{}).get('list',[]):
    print(f"  · {post.get('category')} 시리즈는 릴스만 (hooks.json series.reel_only) — 캐러셀 건너뜀"); sys.exit(0)
ARGS=[a for a in sys.argv[1:] if not a.startswith('--')]   # --reel 같은 깃발은 경로가 아니다
out=ARGS[1] if len(ARGS)>1 else str((P/'out'/'캐러셀').mkdir(parents=True,exist_ok=True) or P/'out'/'캐러셀'/(pathlib.Path(ARGS[0]).stem+'.html'))
outdir=pathlib.Path(out).parent
outdir.mkdir(parents=True,exist_ok=True)
# 사진을 산출물 옆에 둔다. 상대경로가 서버 루트 위로 올라가면 안 열린다.
shutil.copytree(P/'assets', outdir/'assets', dirs_exist_ok=True)
e=lambda s: html.escape(str(s))
N=len(post['slides']); tag=post['series']; src=post['source_note']
OBJ=post.get('object','')   # 이 편이 만들어 주는 물건. plan.json 의 save_card 와 같다
PLACE=post.get('place','TORONTO')
HK=json.load(open(P/'hooks.json',encoding='utf-8'))
SPINE=HK['spine']           # 축. 매 장 같은 자리, 안 바뀐다

PHOTOS=['hama-stand.jpg','hama-straw.jpg','hama-trench.jpg']

def photo(s,i):
    # i%3 이면 모든 편의 표지가 i=0 으로 같은 사진이 된다. 날짜를 섞는다.
    return s.get('photo') or PHOTOS[(i+sum(map(ord,post['date'])))%len(PHOTOS)]

def hama(s,i):
    """하마 자리. 보유 사진을 프레임 안에서 자르기만 한다. 누끼·리터칭·생성 없음."""
    say=s.get('say','')
    bub=f'<div class="bub">{e(say)}</div>' if say else ''
    return f'<div class="hmrow"><div class="hm"><img src="assets/{e(photo(s,i))}" alt=""></div>{bub}</div>'

def frame(s,i,inner):
    return f'''<section class="sl{' on' if i==0 else ''}">
  <div class="top">
    <span class="spine">
      <span class="nm"><span class="mk"></span>{e(SPINE['name'])}</span>
      <span class="jr">{e(SPINE['line'])}</span>
    </span>
    <span class="pg">{i+1}/{N}</span>
  </div>
  <div class="hr"></div>
  {inner}
  {hama(s,i)}
  <div class="foot"><span>@hamathegolddigger</span><span class="src">{e(src)}</span></div>
</section>'''

# ── 표지 언어 부품 ─────────────────────────────────────────────────────────
def pill(text):
    """알약 글자. 한 글자씩 떨어진다 (표지와 같은 모션)."""
    return ''.join(f'<span class="c" style="animation-delay:{0.06+n*0.012:.3f}s">{"&nbsp;" if ch==" " else e(ch)}</span>'
                   for n,ch in enumerate(text))

def hookline(words,t0):
    """제목 한 줄. 단어마다 .w 로 들어온다. words 는 이미 이스케이프된 조각 목록.
    *단어* 는 로즈(손해), _단어_ 는 골드잉크(이득). 색은 글자에만 — 판·막대 없음 (2026-11-03 밤)."""
    out=[]; open_=None   # *March 1* 처럼 여러 단어 강조도 받는다
    for n,w in enumerate(words):
        cls='w'
        if re.match(r'^[-−]\$?\d',re.sub(r'<[^>]+>','',w)) and not open_: cls='w hi'   # 마이너스 숫자 = 손해 = 로즈 (11/05)
        elif len(w)>2 and w[0]=='*' and w.rstrip('.,!?')[-1:]=='*': cls='w hi'; w=w.replace('*','',2)
        elif len(w)>2 and w[0]=='_' and w.rstrip('.,!?')[-1:]=='_': cls='w ok'; w=w.replace('_','',2)
        elif len(w)>1 and w[0] in '*_' and not open_: open_=w[0]; cls='w '+('hi' if open_=='*' else 'ok'); w=w[1:]
        elif open_:
            cls='w '+('hi' if open_=='*' else 'ok')
            if w.rstrip('.,!?')[-1:]==open_: w=w.replace(open_,'',1); open_=None
        out.append(f'<span class="{cls}" style="animation-delay:{t0+n*0.08:.3f}s">{w}</span>')
    return ' '.join(out)

STAGE_ALIAS = {"stocks": "etf", "fear": "etf"}   # 그림이 없는 카테고리는 승인된 그림을 빌린다 (주식 = 차트 보는 하마)
def stage_pic():
    c = post.get('category', 'tax'); c = c if (P / 'assets' / 'stage' / f'{c}.png').exists() else STAGE_ALIAS.get(c, 'basics')
    return f"stage/{c}.png"

def hama_say(s):
    """moa_sudal 자리. 카테고리 일러를 둥글게 자른 것 + 한마디. 사진은 안 쓴다 (하림님 2026-11-03)."""
    if not s.get('say'): return ''
    return (f'<div class="hama"><div class="pic"><img src="assets/{e(stage_pic())}" alt=""></div>'
            f'<span class="say">{e(s["say"]).replace("|","<br>")}</span></div>')   # | 는 줄바꿈 자리

def frame_inner(s,i,body):
    """속장 틀 = 알약 + 블러시 제목판 + 몸통 + 발띠. 표지(hero)와 같은 부품. 매 장 같은 자리."""
    title=hookline([e(w) for w in s['title'].split()],0.5)
    return f'''<section class="sl inner{' on' if i==0 else ''}">
  <span class="pill"><i></i>{pill(s['kicker'])}<i></i></span>
  <div class="hook">{title}</div>
  {body}
  {srcchip(s)}
  <div class="foot"><span>{e(SPINE['name'])} · {e(PLACE)}</span><span>{i+1}/{N}</span></div>
</section>'''

def srcchip(s):
    """출처 칩 (v2). source_label 이 있는 장에만."""
    lb=s.get('source_label')
    return f'<span class="srcchip">{e(lb)}</span>' if lb else ''

def hero(s,i):
    """주인공 표지. 그림은 category 로 자동, 글만 post.json 에서 온다.
    ① 훅이 제일 크고 ② 약속이 그 아래 작은 줄 (hooks.json one_second, 2026-11-04). 시리즈 이름은 작게 위로."""
    pic=s.get('photo') or stage_pic()
    topic=s.get('topic') or HK['series']['title'].get(post.get('category',''),'')
    long_=' long' if len(topic)>13 else ''
    hk=s['hook']
    words=[]
    # 훅을 단어로 쪼개되 숫자 자리는 .num 으로 남긴다
    pre_raw=hk.get('pre',''); pre=pre_raw.split(); post_=hk.get('post','')
    for w in pre: words.append(e(w))
    if hk.get('num') is not None:
        head=post_.split(' ',1); first=head[0]; rest=head[1] if len(head)>1 else ''
        # "$" 처럼 앞말이 공백 없이 숫자에 붙어 있으면 한 단어로 묶는다 — 아니면 "$ 100" 이 된다
        glue=words.pop() if (pre and not pre_raw.endswith(' ')) else ''
        w_=f'{glue}<span class="num" data-to="{e(hk["num"])}">{e(hk["num"])}</span>{e(first)}'
        words.append('*'+w_+'*' if glue.endswith(('-','−')) else w_)   # -72% 는 부호째 로즈
        for w in rest.split(): words.append(e(w))
    else:
        for w in post_.split(): words.append(e(w))
    sub=f'<div class="q">{e(s["sub"])}</div>' if s.get('sub') else ''
    prom=f'<div class="prom">{e(s["promise"])}</div>' if s.get('promise') else ''
    return f'''<section class="sl hero{' on' if i==0 else ''}">
  <span class="pill"><i></i>{pill(s['kicker'])}<i></i></span>
  <div class="topic{long_}">{e(topic)}</div>
  <div class="hook">{hookline(words,0.9)}</div>{prom}{sub}
  <div class="pic"><img src="assets/{e(pic)}" alt=""></div>
  <span class="keep"><i></i>{e(OBJ)}<span class="shine"></span></span>
  <div class="foot"><span>{e(SPINE['name'])} · {e(PLACE)}</span><span>{i+1}/{N}</span></div>
</section>'''

def mk_inner(s,i):
    """표지 언어 장이면 HTML 을, 아니면 None 을 돌려준다 (기존 cqw 장은 mk 로 넘어간다)."""
    t=s['type']
    if t=='hero':
        return hero(s,i)
    if t=='two':
        # 두 칸 비교. 왼쪽이 손해(블러시), 오른쪽이 이득(버터). 숫자 160px 가 주인공
        # 주인공 하나 + 위성 하나 (Stageshow). lead:true 인 칸이 주인공, 없으면 win 칸, 그것도 없으면 둘째 칸
        boxes=s['boxes']; li=next((k for k,b in enumerate(boxes) if b.get('lead')),None)
        if li is None: li=next((k for k,b in enumerate(boxes) if b.get('win') or b.get('tone')=='win'),1)
        def box(k,b):
            d2='<span class="d2">'+e(b['d2'])+'</span>' if b.get('d2') else ''
            d3='<span class="d3">'+e(b['d3'])+'</span>' if b.get('d3') else ''
            tone=b.get('tone') or ('win' if b.get('win') else 'loss')   # loss 로즈 · win 골드 밑줄 · flat 검정
            role='is-lead' if k==li else 'is-sat'   # .lead 는 옛 cqw 장과 겹친다
            n_=len(b['v'])   # 승인 판은 4자 이하. 더 긴 값($1.52M)은 칸 안에 들게 줄인다
            fs=(f' style="font-size:{min(200, 900//n_) if k==li else min(132, 720//n_)}px"' if n_>4 else '')
            return ('<div class="bx '+tone+' '+role+'"><span class="h">'+e(b['h'])+'</span><span class="v"'+fs+'>'+e(b['v'])
                    +'</span><span class="d">'+e(b['d'])+'</span>'+d2+d3+'</div>')
        bx=''.join(box(k,b) for k,b in enumerate(boxes))
        cls='two lead-first' if li==0 else 'two'
        return frame_inner(s,i,f'<div class="{cls}">{bx}</div>\n  {hama_say(s)}')
    if t=='table':
        # 저장되는 표. 2열(금액 | 도착) 또는 3열 밀도표(v2 01-table 구조: 금액+막대 | 도착 TFSA | 비교 RRSP). 머리글은 한 번. 빠진 돈은 도착 열 안에
        dense=any(r.get('c') for r in s['rows'])
        def row(r):
            gone='<span class="gone">'+e(r['gone'])+'</span>' if r.get('gone') else ''
            bars=('<span class="bars"><span class="bar a"><i style="width:'+str(r.get('bar',85))+'%"></i></span><span class="bar b"><i></i></span></span>') if dense else ''
            c3=('<div class="c3"><span class="c3v">'+e(r['c'])+'</span><span class="csub">'+e(r.get('csub',''))+'</span></div>') if dense else ''   # 머리글은 표 위에 한 번
            lb2=''   # 머리글은 표 위에 한 번뿐 (Stageshow «say it once»)
            return ('<div class="row'+(' c3' if dense else '')+'"><div class="c1"><span class="amt">'+e(r['a'])+'</span><span class="asub">'+e(r.get('asub',''))
                    +'</span>'+bars+'</div><div class="c2">'+lb2+'<span class="big">'+e(r['b'])+'</span>'+gone+'</div>'+c3+'</div>')
        rows=''.join(row(r) for r in s['rows'])
        head=(('<div class="th c3"><span>'+e(s.get('h1',''))+'</span><span>'+e(s.get('h2',''))+'</span><span>'+e(s.get('h3',''))+'</span></div>') if dense
              else ('<div class="th"><span>'+e(s.get('h1',''))+'</span><span>'+e(s.get('h2',''))+'</span></div>'))
        return frame_inner(s,i,'<div class="tbl'+(' dense' if dense else '')+'">'+head+rows+'</div>\n  <div class="note">'+s.get('note','')+'</div>')
    if t=='grid':
        # 조회표. cols = 값 칸 머리글, rows[].cells = 값, hi = 강조할 [행,열] (골드 밑줄은 한 칸만)
        n=len(s['cols']); hi=s.get('hi') or [-1,-1]
        tmpl='grid-template-columns:'+str(s.get('labw',22))+'% repeat('+str(n)+',1fr)'
        head='<div class="gh" style="'+tmpl+'"><span>'+e(s.get('rowlabel',''))+'</span>'+''.join('<span>'+e(c)+'</span>' for c in s['cols'])+'</div>'
        def gr(ri,r):
            acc=s.get('acc',n-1)   # 결과 열(기본 마지막)은 골드 칩
            cells=''.join('<span class="cell'+(' hi' if [ri,ci]==hi else (' acc' if ci==acc else ''))+'">'+e(v)+'</span>' for ci,v in enumerate(r['cells']))
            return ('<div class="gr" style="'+tmpl+'"><span class="lab"><b>'+e(r['a'])+'</b><span>'+e(r.get('asub',''))+'</span></span>'+cells+'</div>')
        rows=''.join(gr(i_,r) for i_,r in enumerate(s['rows']))
        return frame_inner(s,i,'<div class="grid">'+head+rows+'</div>\n  <div class="note">'+s.get('note','')+'</div>')
    if t=='flow':
        # 세 칸 흐름. 가운데가 «잘리는» 칸. 화살표는 뺐다 (금색 화살표 대비 1.68)
        st=''.join(f'<span class="st{" cut" if x.get("cut") else ""}"><span class="n">{e(x["n"])}</span><b>{e(x["t"])}</b><span>{e(x.get("s",""))}</span></span>' for x in s['steps'])
        return frame_inner(s,i,f'<div class="stage"><div class="card"><div class="m">{s["lead"]}</div><div class="flow">{st}</div><div class="x">{s.get("tail","")}</div></div></div>\n  {hama_say(s)}')
    if t=='mini':
        rows=''.join(f'<span class="mr {"ok" if r.get("ok") else "no"}"><b>{e(r["t"])}</b><span class="tagv">{e(r["v"])}</span></span>' for r in s['rows'])
        return frame_inner(s,i,f'<div class="stage"><div class="card"><div class="m">{s["lead"]}</div><div class="mini">{rows}</div><div class="x">{s.get("tail","")}</div></div></div>\n  {hama_say(s)}')
    if t=='chart':
        # 주가 창 (chart.py 정본, 하림님 11/05 캡처 레퍼). charts[] 는 find.py chart 가 받아 둔 스냅숏. 2개면 작게 위아래
        import chart as _ch
        cs=s['charts'][:2]; sm=' two' if len(cs)>1 else ''
        win=''.join(_ch.window(c,f'c{i}{k}') for k,c in enumerate(cs))
        return frame_inner(s,i,f'<style>{_ch.CSS}</style><div class="chstage{sm}">{win}</div>\n  {hama_say(s)}')
    if t=='do':
        ck=''.join(f'<div class="ck"><span class="h">{e(c["h"])}</span><span class="d">{c["d"]}</span></div>' for c in s['checks'])
        return frame_inner(s,i,f'<div class="stage"><div class="card"><div class="checks">{ck}</div><div class="m">{s["lead"]}</div></div><div class="btn">{e(s["button"])}</div></div>\n  {hama_say(s)}\n  <div class="fine">{e(s.get("fine",""))}</div>')
    return None

def mk(s,i):
    r=mk_inner(s,i)
    if r is not None: return r
    t=s['type']
    if t=='cover' and s.get('variant')=='ticket':
        rows=''.join(
          f'''<div class="tr"><span class="k">{e(r['k'])}</span><span class="ar">&#9656;</span>'''
          f'''<span class="v">{'<span class="blk" style="width:'+str(r['blk'])+'cqw"></span>' if r.get('blk') else ''}'''
          f'''{'<span class="gd'+(' warn' if r.get('warn') else '')+'">'+e(r['gold'])+'</span>' if r.get('gold') else ''}{e(r.get('v',''))}</span>'''
          f'''{'<span class="st'+(' hit' if r.get('hit') else '')+'">'+e(r['st'])+'</span>' if r.get('st') else ''}</div>'''
          for r in s['rows'])
        return frame(s,i,f'''<div class="mid"><div class="cvt">
      <span class="chips"><span class="kick">{e(s['kicker'])}</span>{'<span class="kick alt">'+e(s['kicker2'])+'</span>' if s.get('kicker2') else ''}</span>
      <div class="hk">{s['promise']}</div>
      <div class="tkt"><div class="bar"><span>{e(s.get('bar','ORDER'))}</span><span>{e(s.get('bar2',''))}</span></div>{rows}</div>
      <span class="save"><span class="lf"><i></i>{e(OBJ)}</span></span>
    </div></div>''')
    if t=='cover':
        obj=f'<span class="obj"><i></i>{e(OBJ)}</span>' if OBJ else ''
        return frame(s,i,f'''<div class="mid"><div class="cover">
      {obj}
      <span class="big d">{e(s['figure'])}</span>
      <span class="pr">{s['promise']}</span>
      <span class="sub">{e(s.get('sub',''))}</span></div></div>''')
    if t=='stake':
        return frame(s,i,f'''<div class="mid"><div class="stake">
      <p>{s['text']}</p><span class="u">{e(s.get('under',''))}</span></div></div>''')
    if t=='decoder':
        # 티커 목업 하나가 주인공. 1장 = 1규칙.
        ex=f'''<div class="ex">{e(s['example'])}</div>''' if s.get('example') else ''
        badge=f'''<span class="src1">{e(s['source_label'])}</span>''' if s.get('source_label') else ''
        return frame(s,i,f'''<div class="hd"><span class="d lead w">{e(s['title'])}</span></div>
    <div class="mid"><div class="deco">
      <div class="tick">
        <div class="lb">{e(s.get('chip','ON THE TICKER'))}</div>
        <div class="sym d"><span class="base">{e(s['base'])}</span><span class="suf">{e(s['suffix'])}</span></div>
        <div class="mean">{s['meaning']}</div>{ex}
      </div>{badge}
    </div></div>''')
    if t=='idea':
        eg=f'''<div class="eg"><span class="lb">{e(s['eg_label'])}</span><span class="tx">{e(s['eg'])}</span></div>''' if s.get('eg') else ''
        return frame(s,i,f'''<div class="hd"><span class="d lead w">{e(s['title'])}</span></div>
    <div class="mid"><div class="idea">
      <span class="fig"><span class="n d">{e(s['figure'])}</span><span class="u">{e(s['figure_label'])}</span></span>
      <p class="body25">{e(s['body'])}</p>{eg}</div></div>''')
    if t=='key':
        # 저장되는 물건 그 자체. 맥락 없이 혼자 읽혀야 한다.
        rows=''.join(f'''<div class="kr"><span class="c d">{e(r['c'])}</span><span class="m">{r['m']}</span></div>''' for r in s['rows'])
        return frame(s,i,f'''<div class="hd"><span class="d lead w">{e(s['title'])}</span>
      <span class="obj"><i></i>{e(OBJ)}</span></div>
    <div class="mid"><div class="key">{rows}</div></div>''')
    if t=='recap':
        rows=''.join(f'''<div class="rw"><span class="v d">{e(r['v'])}</span><span class="t"><b>{e(r['t'])}</b>{e(r['s'])}</span></div>''' for r in s['rows'])
        return frame(s,i,f'''<div class="hd"><span class="d lead w">{e(s['title'])}</span><span class="rest">{e(s.get('sub','Screenshot this one.'))}</span></div>
    <div class="mid"><div class="recap">{rows}</div></div>''')
    if t=='cta':
        return frame(s,i,f'''<div class="mid"><div class="cta">
      <p class="q">{s['text']}</p>
      <div class="btn">{e(s['button'])}</div>
      <span class="sm">{e(s['fine'])}</span></div></div>''')
    raise SystemExit(f'unknown slide type {t}')

base=open(P/'template.html',encoding='utf-8').read()
doc=base.replace('{{TITLE}}',e(post['title'])).replace('{{LEDE}}',e(post.get('lede','')))
doc=doc.replace('{{SLIDES}}','\n'.join(mk(s,i) for i,s in enumerate(post['slides'])))
open(out,'w',encoding='utf-8').write(doc)
print(f'{out}  ·  {N}장  ·  물건: {OBJ or "없음"}')

# ── 릴스 = 같은 장을 9:16 으로 6초씩 (하림님 2026-11-03: 릴스는 캐러셀 장을 쓴다. 별도 기획 없음) ──
# HyperFrames 프로젝트를 쓴다. 장마다 한 장면(compositions/sN.html). CSS 키프레임은 HyperFrames 가 시간을 시킹한다.
# 그래서 속장 모션은 transition 이 아니라 animation 이어야 한다 (template.html 참고).
if '--reel' in sys.argv:
    import re as _re
    SEC=6.0
    rd=outdir/(pathlib.Path(ARGS[0]).stem+'-reel'); (rd/'compositions').mkdir(parents=True,exist_ok=True)
    shutil.copytree(P/'assets', rd/'assets', dirs_exist_ok=True)
    css=_re.search(r'<style>(.*?)</style>',base,_re.S).group(1)
    css=_re.sub(r'/\*VIEWER\*/.*?/\*/VIEWER\*/','',css,flags=_re.S)          # 보기 껍데기(body zoom 등)는 장면에 못 들어간다
    css=_re.sub(r'transition(?:-delay)?\s*:[^;}]*;?','',css)                   # 옛 cqw 장의 transition 은 시킹이 안 된다 — 릴스에선 뺀다
    css=('@font-face{font-family:"Fredoka";src:url("assets/fonts/Fredoka.woff2") format("woff2");font-weight:300 700;font-style:normal}\n'
         '@font-face{font-family:"Bricolage Grotesque";src:url("assets/fonts/BricolageGrotesque.woff2") format("woff2");font-weight:200 800;font-style:normal}\n'
         '@font-face{font-family:"Figtree";src:url("assets/fonts/Figtree.woff2") format("woff2");font-weight:300 900;font-style:normal}\n'
         +css+
         '\n#root{position:absolute;inset:0;background:var(--cream)}\n.deck{box-shadow:none;border-radius:0}\n'
         '.sl *{animation-iteration-count:1!important}\n')                     # 무한 반복(beat·shine)은 렌더에서 한 번만
    hosts=[]
    for i,s in enumerate(post['slides']):
        sid=f's{i+1}'
        html_=mk(s,i).replace('class="sl hero"','class="sl hero on"').replace('class="sl inner"','class="sl inner on"')
        scene=('<template>\n<style>'+css+'</style>\n'
               f'<div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">\n<div class="deck v916">\n'
               +html_+'\n</div></div>\n'
               f'<script>window.__timelines["{sid}"]=gsap.timeline({{paused:true}});</script>\n</template>\n')
        (rd/'compositions'/f'{sid}.html').write_text(scene,encoding='utf-8')
        hosts.append(f'    <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{i*SEC:g}" data-duration="{SEC:g}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>')
    index=('<!doctype html>\n<html><head><meta charset="utf-8"><title>'+e(post['title'])+'</title>\n'
           '<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script></head>\n'   # hyperframes init 이 넣는 것과 같다

           '<body style="margin:0;background:#FDF8EC">\n'
           f'  <div id="root" data-composition-id="main" data-start="0" data-duration="{N*SEC:g}" data-width="1080" data-height="1920" data-fps="30">\n'
           +'\n'.join(hosts)+'\n  </div>\n'
           '  <script>window.__timelines["main"]=gsap.timeline({paused:true});</script>\n</body></html>\n')
    (rd/'index.html').write_text(index,encoding='utf-8')
    print(f'{rd}  ·  릴스 {N}장 × {SEC:g}s = {N*SEC:g}s  ·  다음: cd "{rd}" && npx hyperframes check --json')

# ── 모션 릴스 (--motion): 캐러셀 장이 아니라 «한 줄 + 물건 하나가 비트마다 바뀌는» 이야기. 틀은 엔진/motion/number-story.html 한 곳.
#    post.json 의 motion{} 이 글·숫자·타이밍을 준다. 하림님 2026-11-03 밤: «이런 모션그래픽을 왜 못 해».
if '--motion' in sys.argv:
    import re as _re
    M=post.get('motion')
    if not M: raise SystemExit('post.json 에 motion{} 이 없다')
    md=outdir/(pathlib.Path(ARGS[0]).stem+'-motion'); md.mkdir(parents=True,exist_ok=True)
    shutil.copytree(P/'assets', md/'assets', dirs_exist_ok=True)
    tpl=open(P/'motion'/(M.get('template','number-story')+'.html'),encoding='utf-8').read()
    T=M['t']  # t1 · stage · t3 · t4 · end
    sub={'TITLE':post['title'],'DUR':T['end'],'SHOW':M.get('show',''),
         'T1':T['t1'],'T2L':round(T['t3']-T['t1'],3),'T3':T['t3'],'T3L':round(T['t4']-T['t3'],3),'T4':T['t4'],'T4L':round(T['end']-T['t4'],3),
         'HOOK_NUM':M['hook']['num'],'HOOK_TAG':M['hook'].get('tag',''),'GROW_CAP':M.get('grow_cap',''),
         'IN_V':M['split']['in'][0],'IN_L':M['split']['in'][1],'ADD_V':M['split']['add'][0],'ADD_L':M['split']['add'][1],'SPLIT_FINE':M['split'].get('fine',''),
         'PIC':M.get('pic') or stage_pic(),'PILL':M['payoff'].get('pill',OBJ),'PAYOFF_FINE':M['payoff'].get('fine',''),
         'FOOT_L':f"{SPINE['name']} · {PLACE}",'FOOT_R':src}
    for k,v in sub.items(): tpl=tpl.replace('{{'+k+'}}',e(v) if isinstance(v,str) else str(v))
    tpl=tpl.replace('/*STORY*/{}/*/STORY*/',json.dumps(M,ensure_ascii=False))
    (md/'index.html').write_text(tpl,encoding='utf-8')
    print(f'{md}  ·  모션 릴스 {T["end"]}s  ·  다음: cd "{md}" && npx hyperframes check --json && npx hyperframes render --quality looks -o ../<stem>-motion.mp4')
