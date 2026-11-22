"""Verify source provenance and the shipped HTML without a browser."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
expected={'cards.json':'d1142551ab9e7c86f5e61c9f2765be314652f62cb61c0182447500eab4da3e1a','rules.md':'87aee2713a113d79b035ffb1466d637837bfff1132fbec5fcbc44de48645323e','turn_flow.svg':'e3fbc66a39efb01c70ce8f25e052ac5ab0b51b0c9868a1d37a8c42d2b9394e4b'}
for f,sha in expected.items():assert hashlib.sha256((ROOT/'source_data'/f).read_bytes()).hexdigest()==sha,f
printables=json.loads((ROOT/'source_data/printables.json').read_text())
for item in printables:
 source=(ROOT/'source_data'/item['file']).read_bytes()
 assert hashlib.sha256(source).hexdigest()==item['sha256'],item['file']
 assert (ROOT/'dist'/item['file']).read_bytes()==source,item['file']
page=(ROOT/'dist/index.html').read_bytes();assert page==(ROOT/'dist/Force_136_Digital_Deck.html').read_bytes()
assert b'github.com' not in page
assert (ROOT/'dist/printables.html').read_bytes()==(ROOT/'src/printables.html').read_bytes()
assert 'github.com' not in (ROOT/'dist/printables.html').read_text()
class Document(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.external_scripts=[];self.remote_styles=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='script' and a.get('src'):self.external_scripts.append(a['src'])
  if tag=='link' and a.get('rel')=='stylesheet':self.remote_styles.append(a.get('href'))
doc=Document();doc.feed(page.decode());assert len(doc.ids)==len(set(doc.ids));assert not doc.external_scripts and not doc.remote_styles
assert all('rule-'+str(i) in doc.ids for i in range(1,12))
source=json.loads((ROOT/'source_data/cards.json').read_text());data=json.loads(re.search(r'<script id="force136-data" type="application/json">(.*?)</script>',page.decode(),re.S).group(1))
assert data['cards']==source and len(source)==9 and data['rulesVersion']=='1.1'
assert set(data['goals'])=={'PLACE','AMBUSH','INTEL','SUPPLY','TRAIN','CONTACT'}
assert set(data['procedures'])=={'contact','train','ambush','sabotage','gather','supply','raid'}
before=page
subprocess.run([sys.executable,str(ROOT/'build.py')],check=True,capture_output=True)
assert (ROOT/'dist/index.html').read_bytes()==before,'Rebuild changed the HTML'
print(json.dumps({'source_inputs_verified':len(expected),'printable_pdfs_verified':len(printables),'cards_verified':9,'full_rule_sections':11,'html_ids_unique':len(doc.ids),'remote_runtime_dependencies':0,'byte_identical_html_rebuild':True},indent=2))
