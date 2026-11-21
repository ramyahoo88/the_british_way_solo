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
L=["# Force 136 v1.0.1 — sample game","",
f"Seed {seed}, Agent level, against the simulation's *{pol}* Japan policy. The game was generated with `python3 sample_game.py {seed} {pol}` and `python3 sample_md.py {seed} {pol} <file>`. The Japanese moves come from one computer policy and are not advice. For each turn the log lists the bot's Directive card, the goal that qualified and the board changes. MPAJA icons are applied before the first entry of each card and are not listed.","",
"## Starting position","","Standard setup. Resistance 2, Zipper at Delay, Japanese Resources 0. Force 136 is first eligible.",""]
L+=[f"- {x}" for x in d['start']]
L+=["","## Play",""]
for x in d['narr']:
    if x.get('prop'):
        t=x['terms'];L+=["",f"**{'Final ' if x['final'] else ''}Propaganda.** Intel +{t['intel']}, Caches +{t['caches']}, majorities +{t['majorities']}, Resources −{t['resource_penalty']}, Neutral Population −{t['neutral_penalty']}, Police −{t['police_penalty']}: net {t['net_change']:+d}. Resistance {x['R'][0]} → {x['R'][1]}.",""];continue
    ch=' — '+' | '.join(phr(c) for c in x['changes']) if x['changes'] else ' — no board change'
    if x.get('who'):
        L.append(f"- *Card {x['draw']} (J{x['event']}) · Japan · {x['box']}* · R {x['R'][0]}→{x['R'][1]}{ch}");continue
    sa=f" + {x['sa'].title()}" if x['sa'] else ''
    card=x['card'].split(':')[0]
    L.append(f"- **Card {x['draw']} (J{x['event']}) · Force 136 · Directive {card} · {x['goal']} → {x['box']}: {x['op'].title()}{sa}** · R {x['R'][0]}→{x['R'][1]}{ch}")
L+=["",(f"**Result:** Force 136 wins at Resistance {d['R']}." if d['winner']=='Force 136' else f"**Result:** {d['winner']} wins (Resistance {d['R']})."),""]
open(out,'w').write('\n'.join(L))
