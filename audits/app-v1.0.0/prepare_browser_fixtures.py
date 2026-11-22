"""Create disposable browser fault fixtures using the unmodified release HTML.
Usage: python prepare_browser_fixtures.py /path/to/web/force136
Serve browser-fixtures/dist/ with an ordinary static host (or sites-preview).
"""
from pathlib import Path
import sys,json
app=Path(sys.argv[1]) if len(sys.argv)>1 else Path('../force136_app')
root=Path(__file__).resolve().parent
out=root/'browser-fixtures'/'dist';out.mkdir(parents=True,exist_ok=True)
save=json.loads((root/'fixtures/seed-2200001.json').read_text())
html=(app/'dist/index.html').read_text()
inject="""<script>
// AUDIT FIXTURE ONLY: deliberate faults before loading the unchanged released UI.
const auditCase=new URLSearchParams(location.search).get('case')||'damaged';
const auditKey='force136.deck.v1',auditBackup='force136.deck.backup.v1';
let auditQuota=auditCase==='quota';
const auditInitial=__SAVE__;
localStorage.removeItem(auditKey);localStorage.removeItem(auditBackup);
if(auditCase==='damaged'){localStorage.setItem(auditKey,'broken');localStorage.setItem(auditBackup,'broken');}
if(auditCase==='backup'){localStorage.setItem(auditKey,'broken');localStorage.setItem(auditBackup,JSON.stringify(auditInitial));}
if(auditCase==='quota'){localStorage.setItem(auditKey,JSON.stringify(auditInitial));}
const auditNativeSet=Storage.prototype.setItem;
Storage.prototype.setItem=function(k,v){if(auditQuota&&k.startsWith('force136.deck'))throw new DOMException('Audit quota fault','QuotaExceededError');return auditNativeSet.call(this,k,v);};
document.addEventListener('DOMContentLoaded',()=>{
 const bar=document.createElement('aside');bar.style.cssText='padding:10px;background:#ffe8ca';
 bar.innerHTML='<strong>AUDIT FIXTURE: '+auditCase+'</strong> <button id="audit-enable-storage">Restore storage writes</button><button id="audit-storage-state">Inspect storage state</button><pre id="audit-state"></pre>';
 document.body.prepend(bar);
 document.getElementById('audit-enable-storage').onclick=()=>{auditQuota=false;document.getElementById('audit-state').textContent='Storage writes enabled';};
 document.getElementById('audit-storage-state').onclick=()=>{let s;try{s=JSON.parse(localStorage.getItem(auditKey));}catch(e){s=null;}document.getElementById('audit-state').textContent=JSON.stringify({primaryIsValidJSON:!!s,draws:s?.game?.draws,level:s?.game?.level});};
});
</script>""".replace('__SAVE__',json.dumps(save).replace('</','<\\/'))
(out/'production.html').write_text(html)
(out/'app.html').write_text(html.replace('<body>','<body>'+inject,1))
(out/'index.html').write_text('''<!doctype html><html><head><meta name="viewport" content="width=device-width"></head><body><h1>Force 136 audit fixtures</h1><p>Disposable tests. Never load into a player\'s production origin.</p><ul><li><a href="app.html?case=damaged">Both autosaves damaged</a></li><li><a href="app.html?case=quota">Temporary quota failure</a></li><li><a href="app.html?case=backup">Primary damaged, valid backup</a></li><li><a href="mobile.html">390px mobile reference</a></li></ul></body></html>''')
(out/'mobile.html').write_text('''<!doctype html><html><body><h1>390px mobile audit frame</h1><iframe title="Phone app" src="production.html" style="width:390px;height:844px;border:1px solid black"></iframe></body></html>''')
config=root/'browser-fixtures'/'.openai';config.mkdir(exist_ok=True)
(config/'hosting.json').write_text(json.dumps({'static':{'directory':'dist'}}))
print(out)
