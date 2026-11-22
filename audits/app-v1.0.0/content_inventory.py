"""Inventory compiled cards/rules and compare inputs to the pinned GitHub tree."""
from pathlib import Path
import json, hashlib, re, html, sys
import fitz
root=Path(__file__).resolve().parent
app=Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/'force136_app'
page=(app/'dist/index.html').read_text()
data=json.loads(re.search(r'<script id="force136-data" type="application/json">(.*?)</script>',page,re.S)[1])
plain=lambda s:html.unescape(re.sub('<[^>]*>','',s)).strip()
result={'cardIds':[c['id'] for c in data['cards']],
 'fullGoals':{str(c['id']):['PLACE']+c['goals']+['CONTACT'] for c in data['cards']},
 'Limited':{str(c['id']):['PLACE',c['limited_first'],'TRAIN' if c['limited_first']=='AMBUSH' else 'AMBUSH','CONTACT'] for c in data['cards']},
 'sections':[plain(s) for s in re.findall(r'<summary>(.*?)</summary>',page,re.S)],
 'levelTable':[[plain(s) for s in re.findall(r'<t[dh]>(.*?)</t[dh]>',row,re.S)] for row in re.findall(r'<tr>(.*?)</tr>',page,re.S)],
 'goals':list(data['goals']),'procedures':list(data['procedures']),
 'runtimeScriptUrls':re.findall(r'<script[^>]*\bsrc=["\']([^"\']+)',page),
 'externalStyles':re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>',page)}
assert result['cardIds']==list(range(1,10))
assert len(result['sections'])==11 and len(result['levelTable'])==6
assert len(result['procedures'])==7
assert not result['runtimeScriptUrls'] and not result['externalStyles']
pdf=fitz.open(app/'dist/Force_136_Rules.pdf');result['rulesPDFPages']=len(pdf);assert len(pdf)==5
paper=json.loads((root/'evidence/source-release.json').read_text())['paperFiles']
mapping={'cards.json':'cards.json','Force_136_v1_Rules.md':'rules.md','Force_136_v1_Rules.pdf':'Force_136_Rules.pdf','turn_flow.svg':'turn_flow.svg'}
result['pinnedPaperBlobs']=[]
for entry in paper:
 p=app/'source_data'/mapping[Path(entry['path']).name];b=p.read_bytes()
 digest=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert digest==entry['sha']
 result['pinnedPaperBlobs'].append({'path':entry['path'],'sha':digest,'match':True})
(root/'evidence/content-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 9 card faces, 18 priority lists, 11 rule sections, 6 level-table rows, 7 procedures, 5 PDF pages and 4 pinned paper blobs.')
