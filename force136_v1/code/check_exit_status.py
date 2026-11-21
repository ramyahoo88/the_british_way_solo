"""The checker's exit status must fail when it finds a problem (GPT re-audit, finding R2).

1. A clean run of verify_v1.py exits 0.
2. The same command with an error injected into the shared engine's scoring (Caches count double,
   in memory only) exits 1.
3. Mutation mode with a 'mutant' that changes nothing (so it cannot be caught) exits 1.
"""
import subprocess,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
def run(code):
    return subprocess.run([sys.executable,'-c',code],cwd=HERE,capture_output=True,text=True).returncode
clean=run("import sys,verify_v1 as T;sys.exit(T.main(['2']))")
inject=run("import sys,engine,verify_v1 as T\n"
           "st=engine.score_terms\n"
           "def f(b,r):\n t=st(b,r);t['caches']*=2;return t\n"
           "engine.score_terms=f\nsys.exit(T.main(['2']))")
missed=run("import sys,verify_v1 as T\n"
           "class Same(T.V.Force136):pass\n"
           "T.mutants=lambda:[('no change',Same,('agent',),None,'P')]\n"
           "T.shared_mutants=lambda:[];T.zipper_mutants=lambda:[]\n"
           "sys.exit(T.main(['--mutants','1']))")
print('clean run exit',clean,'| injected scoring error exit',inject,'| uncaught mutant exit',missed)
assert clean==0 and inject==1 and missed==1
print('exit status checks passed')
