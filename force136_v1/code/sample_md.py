"""Turn sample_<seed>_<policy>.json (from sample_game.py) into the readable sample-game Markdown."""
import json,sys
seed,pol,out=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(f'sample_{seed}_{pol}.json'))
def phr(c):
    s,rest=c.split(': ',1);items={}
    for part in rest.split(', '):
        k,v=part.rsplit(' ',1);a,b=v.split('->');items[k]=(a,b)
    o=[]
    for col in ('red','blue'):
        ku,ka=col+'_u',col+'_a';parts=[]
        if ku in items:parts.append(f"Underground {items[ku][0]}→{items[ku][1]}")
        if ka in items:parts.append(f"Active {items[ka][0]}→{items[ka][1]}")
        if parts:o.append(f"{col} "+', '.join(parts))
    for k,lab in (('troops','Troops'),('police','Police'),('kempeitai','Kempeitai')):
        if k in items:o.append(f"{lab} {items[k][0]}→{items[k][1]}")
    for k,lab in (('force136','Force 136'),('camp','Camp'),('cache','Cache'),('opposition','Opposition'),('new_village','New Village')):
        if k in items:
            a,b=items[k]
            up=(b=='True') if a in('True','False') else int(b)>int(a)
            o.append(('+' if up else '−')+lab)
    if 'terror' in items:o.append('+Terror' if int(items['terror'][1])>int(items['terror'][0]) else '−Terror')
    if 'intel' in items:
        a,b=items['intel'];o.append(f"Intel revealed ({b})" if a=='None' else 'Intel concealed' if b=='None' else f"Intel {a}→{b}")
    return f"{s}: "+'; '.join(o)
OPS={'DEPLOY':'Deploy','CONSTRUCT':'Construct','ASSAULT':'Assault','SWEEP':'Sweep','EVENT':'Japanese side','PASS':'Pass'}
L=["# Force 136 v1.1 — sample game","",
f"Seed {seed}, Agent level, against the simulation's *{pol}* Japan policy. The game was generated with `python3 sample_game.py {seed} {pol}` and `python3 sample_md.py {seed} {pol} <file>`. The Japanese moves come from one computer policy and are not advice. The log lists each card's MPAJA icon, each Force 136 turn (Directive card, the goal that qualified, the board changes; or the Event it played) and each Japanese move, then every Propaganda with the position after its Reset.","",
"## Starting position","","Standard setup. Resistance 2, Zipper at Delay, Japanese Resources 0. Force 136 is first eligible.",""]
L+=[f"- {x}" for x in d['start']]
L+=["","## Play",""]
for x in d['narr']:
    if x.get('prop'):
        t=x['terms'];card=f" (card {x['draw']})"
        L+=["",f"**{'Final ' if x['final'] else ''}Propaganda{card}.** Intel +{t['intel']}, Caches +{t['caches']}, majorities +{t['majorities']}, Resources −{t['resource_penalty']}, Neutral Population −{t['neutral_penalty']}, Police −{t['police_penalty']}: net {t['net_change']:+d}. Resistance {x['R'][0]} → {x['R'][1]}"+("." if x['final'] else f"; Zipper at {x['zipper'] or 'Delay'}."),""]
        if x.get('after'):
            L+=["Position after the Reset (all guerrillas Underground, Intel dealt again"+(f"; Sabotage on {', '.join(r.replace(' *','★') for r in x['sab'])}" if x['sab'] else "")+"):",""]
            L+=[f"- {y}" for y in x['after']]+[""]
        continue
    ch=' — '+' | '.join(phr(c) for c in x['changes']) if x['changes'] else ' — no board change'
    if x.get('icon'):
        L.append(f"- Card {x['draw']} (J{x['event']}) · icon: {x['icon']}{ch}");continue
    if x.get('mandatory'):
        L.append(f"- Card {x['draw']} (J{x['event']}) · Mandatory Event"+(": the game goes straight to the final Propaganda" if x['ends'] else ch));continue
    if x.get('who'):
        pl=x['plan'];what=OPS[pl['op']]+(f" + {pl['sa'].title()}" if pl.get('sa') else '')
        if pl.get('sa')=='REPRISAL' and pl.get('timing')=='before':what=f"Reprisal, then {OPS[pl['op']]}"
        res=f"; Resources {x['res'][0]}→{x['res'][1]}" if x['res'][0]!=x['res'][1] else ''
        cap=''.join(f"; capability J{c} now in play" for c in x.get('cap',[]))
        L.append(f"- *Card {x['draw']} (J{x['event']}) · Japan · {x['box']}: {what}* · R {x['R'][0]}→{x['R'][1]}{res}{cap}{ch}");continue
    if x['op']=='EVENT':
        what='Contact'+(f" + {x['sa'].title()}" if x['sa'] else '') if x['event']==25 else '+1 Resistance per space with Force 136 and a Camp'
        L.append(f"- **Card {x['draw']} (J{x['event']}) · Force 136 · Event box: British side ({what})** · R {x['R'][0]}→{x['R'][1]}{ch}");continue
    sa=f" + {x['sa'].title()}" if x['sa'] else ''
    card=x['card'].split(':')[0]
    L.append(f"- **Card {x['draw']} (J{x['event']}) · Force 136 · Directive {card} · {x['goal']} → {x['box']}: {x['op'].title()}{sa}** · R {x['R'][0]}→{x['R'][1]}{ch}")
L+=["",(f"**Result:** Force 136 wins at Resistance {d['R']}." if d['winner']=='Force 136' else f"**Result:** {d['winner']} wins (Resistance {d['R']})."),""]
open(out,'w').write('\n'.join(L))
