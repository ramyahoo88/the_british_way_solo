"""Build the audit PDF with the same pipeline as the print package (Python-Markdown + headless Chrome).
Usage, from this folder: python3 build_audit_pdf.py"""
import sys,importlib.util,markdown
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.argv=[sys.argv[0],'/tmp/f136_build_unused']          # build.py reads its output folder from argv
spec=importlib.util.spec_from_file_location('build',HERE.parents[1]/'force136_v1'/'print'/'build.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
name='Force_136_v1.0.2_Audit_338cb0d'
body=markdown.markdown((HERE/(name+'.md')).read_text(encoding='utf-8'),extensions=['tables','fenced_code'])
B.chrome_pdf(B.page(B.DOC_CSS,body,'Force 136 v1.0.2 audit'),HERE/(name+'.pdf'))
(HERE/(name+'.html')).unlink()
from pypdf import PdfReader
print(name+'.pdf',len(PdfReader(str(HERE/(name+'.pdf'))).pages),'pages')
