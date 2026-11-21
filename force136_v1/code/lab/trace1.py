import sys
from rulebot import RuleGame
from exp4 import variants
from engine import ORDER,gs,cubes
class G(RuleGame):P=variants['A']
G.quiet=False
g=G(int(sys.argv[1]));g.policy=sys.argv[2];g.run()
def brd(b):
    out=[]
    for s in ORDER:
        v=b[s];bits=[]
        if v['troops'] or v['police']:bits.append(f"T{v['troops']}P{v['police']}")
        if v['kempeitai']:bits.append(f"K{v['kempeitai']}")
        g_=f"r{v['red_u']}/{v['red_a']}b{v['blue_u']}/{v['blue_a']}" if gs(v) else ''
        if g_:bits.append(g_)
        if v['force136']:bits.append('F')
        if v['camp']:bits.append('camp')
        if v['cache']:bits.append('CACHE')
        if v['opposition']:bits.append('opp')
        if v['intel'] is not None:bits.append(f"i{v['intel']}")
        if bits:out.append(s[:4]+':'+','.join(bits))
    return ' '.join(out)
for x in g.log:
    d=x['detail']
    if x['kind'] in('British turn','Japanese turn'):
        d={k:v for k,v in d.items() if k in('op','sa','box','task','kind','timing')}
    elif 'scoring' in x['kind']:
        d={k:d[k] for k in ('net_change','intel','caches','majorities','resource_penalty','neutral_penalty','police_penalty','resistance_after')}
    else:d=''
    print(x['draw'],x['event'],x['kind'][:14],d,'R',x['resistance'],'res',x['resources'])
    if x['kind'] in('British turn','Japanese turn','Nonfinal scoring','Final scoring'):print('    ',brd(x['board']),'sab',[k[:9] for k,v in x['sabotage'].items() if v])
print(g.winner,g.resistance)
