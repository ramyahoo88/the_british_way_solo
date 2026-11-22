"""Package the self-contained app alongside the retained Solo Table assets.
Pages' function upload is used because the connection cannot authorize asset-store uploads.
Refresh the production manifest and catalog before a later site-wide deployment.
"""
from pathlib import Path
import json,base64
ROOT=Path(__file__).resolve().parent.parent
template=(ROOT/'deployment/worker-template.mjs').read_text()
pdfs={'/games/force136/'+p['file']:base64.b64encode((ROOT/'dist'/p['file']).read_bytes()).decode() for p in json.loads((ROOT/'source_data/printables.json').read_text())}
values={'APP':(ROOT/'dist/index.html').read_text(),'HOME':(ROOT/'deployment/home_after.html').read_text(),'PRINTABLES':(ROOT/'dist/printables.html').read_text(),'PDFS':pdfs}
for key,value in values.items():template=template.replace('/*__'+key+'__*/',json.dumps(value,ensure_ascii=False))
(ROOT/'deployment/pages-worker.mjs').write_text(template)
print('Built Pages function bundle:',len(template.encode()),'bytes.')
