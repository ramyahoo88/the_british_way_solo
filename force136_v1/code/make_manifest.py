"""Regenerate the repository's FILE_MANIFEST_SHA256.json: SHA-256 of every tracked file except the
manifest itself. Run from anywhere inside the repository after the final edits and `git add`."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip())
files=subprocess.check_output(['git','ls-files'],cwd=root,text=True).split('\n')
out={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in sorted(files) if f and f!='FILE_MANIFEST_SHA256.json' and (root/f).is_file()}
(root/'FILE_MANIFEST_SHA256.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(out),'files')
