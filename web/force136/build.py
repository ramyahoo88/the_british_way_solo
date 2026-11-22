"""Build one self-contained HTML companion. Python-Markdown is the only build dependency."""
from pathlib import Path
import json,re,html,base64,hashlib
import markdown
ROOT=Path(__file__).resolve().parent
SOURCE='370ae906270464be64a304d95e6ee7a509c9fc1c'
def md(s):return markdown.markdown(s.strip(),extensions=['tables'])
rules=(ROOT/'source_data/rules.md').read_text()
parts=re.split(r'^## (\d+)\. (.+)$',rules,flags=re.M)
sections={parts[i]:{'title':parts[i+1],'body':parts[i+2]} for i in range(1,len(parts),3)}
svg='data:image/svg+xml;base64,'+base64.b64encode((ROOT/'source_data/turn_flow.svg').read_bytes()).decode()
rule_html=''.join('<details class="rule-section" id="rule-'+n+'"><summary>'+n+'. '+html.escape(s['title'])+'</summary><div>'+md(s['body']).replace('src="turn_flow.svg"','src="'+svg+'"')+'</div></details>' for n,s in sections.items())
g=re.split(r'^\*\*(PLACE|AMBUSH|INTEL|SUPPLY|TRAIN|CONTACT)\*\*',sections['5']['body'],flags=re.M)
goals={g[i]:md('**'+g[i]+'**'+g[i+1]) for i in range(1,len(g),2)}
p=re.split(r'^### 6\.\d+ (.+)$',sections['6']['body'],flags=re.M)
procedures={p[i].lower():md(p[i+1]) for i in range(1,len(p),2)}
orders=md('\n'.join(l for l in sections['3']['body'].splitlines() if l.startswith(('- **Map order:','- **Railway list**'))))
term_lines=[l for l in sections['3']['body'].splitlines() if l.startswith(('- **Majority:**','- **Good shot:**','- **Exposed:**'))]
assert len(term_lines)==3
data={'appVersion':'1.0.1','rulesVersion':'1.1','sourceCommit':SOURCE,'cards':json.loads((ROOT/'source_data/cards.json').read_text()),'goals':goals,'procedures':procedures,'terms':md('\n'.join(term_lines))}
page=(ROOT/'src/template.html').read_text()
replacements={'CSS':(ROOT/'src/styles.css').read_text(),'ORDERS':orders,'BETWEEN':md(sections['7']['body']),'RULES':rule_html,'DATA':json.dumps(data,ensure_ascii=False).replace('</',r'<\/'),'CORE':(ROOT/'src/core.js').read_text(),'UI':(ROOT/'src/ui.js').read_text()}
for k,v in replacements.items():page=page.replace('/*__'+k+'__*/',v)
assert not re.search(r'/\*__\w+__\*/',page)
out=ROOT/'dist';out.mkdir(exist_ok=True)
for name in ('index.html','Force_136_Digital_Deck.html'):(out/name).write_text(page)
if (ROOT/'source_data/Force_136_Rules.pdf').exists():(out/'Force_136_Rules.pdf').write_bytes((ROOT/'source_data/Force_136_Rules.pdf').read_bytes())
(ROOT/'source_data/provenance.json').write_text(json.dumps({'repository':'ramyahoo88/the_british_way_solo','sourceCommit':SOURCE,'rulesVersion':'1.1','inputs':{f:hashlib.sha256((ROOT/'source_data'/f).read_bytes()).hexdigest() for f in ('cards.json','rules.md','turn_flow.svg')}},indent=2)+'\n')
print('Built',len(page.encode()),'bytes; 9 Directives; 11 rule sections.')
