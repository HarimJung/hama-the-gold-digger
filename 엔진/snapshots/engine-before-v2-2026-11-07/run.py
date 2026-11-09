#!/usr/bin/env python3
"""오늘(또는 지정일) 브리프를 plan.json에서 꺼낸다. 엔진 1단계."""
import json,sys,datetime,pathlib
P=pathlib.Path(__file__).parent
plan=json.load(open(P/'plan.json',encoding='utf-8'))
want=sys.argv[1] if len(sys.argv)>1 else str(datetime.date.today())
d=next((x for x in plan['days'] if x['date']==want),None)
if not d:
    print(f"{want}: 31일 목록에 없음. 범위 {plan['days'][0]['date']} ~ {plan['days'][-1]['date']}");sys.exit(1)
c=plan['cadence']
print(f"""DAY {d['day']}/31  ·  {d['date']} ({d['dow']})
한 주 단계: {c['phase1'] if d['date']<='2026-11-15' else c['phase2']}
하루 블록 4개 = 아침 스토리 / 점심 미니 / 저녁 메인 릴스 / 밤 스토리

  메인 릴스  [{d['main']['category']}]  {d['main']['topic']}
  미니 피드  [{d['mini']['category']}]  {d['mini']['topic']}
  저장 카드  {d['save_card']}
  스토리     {d['story']}

다음: hama-post 스킬 단계 0(독자 레벨) → 1(사실) → 2(훅 4개, hookscore 80+)
빈칸은 [Taylor가 채움]으로 둔다. 숫자 출처 없으면 상태는 승인됨이 될 수 없다.""")

# --- 각도 엔진 (2026-11-03) ---------------------------------------------
import json as _j
_A=_j.load(open(pathlib.Path(__file__).parent/'angles.json',encoding='utf-8'))
def _angles(cat):
    return [a for a in _A['angles'] if a['category']==cat]

def brief_angle(day):
    out=[]
    for slot in ('main','mini'):
        b=day.get(slot)
        if not b: continue
        cand=_angles(b['category'])
        out.append(f"\n  [{slot}] {b['category']} · {b['topic']}")
        if not cand:
            out.append(f"      각도 없음 — angles.json 에 {b['category']} 각도를 먼저 만든다")
        for a in cand:
            st=_A['stages'].get(a['stage'],{}).get('status','?')
            out.append(f"      {a['id']:18s} {a['shape']}")
            out.append(f"      {'':18s} 물건: {a['object']} · 무대: {a['stage']}({st}) · 훅: {a['hook']}")
            out.append(f"      {'':18s} 필요: {a['needs']}")
    return '\n'.join(out)

print('\n  — 각도 후보 (angles.json) —' + brief_angle(d))
