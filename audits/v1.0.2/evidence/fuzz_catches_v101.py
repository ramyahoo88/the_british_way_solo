"""Does the new fuzzer find a known error? It runs fuzz_v1.py with v1.0.1's bot (commit 33745a6), whose
Redeploy moved only one marker of a stack. Usage, from this folder inside a checkout that has fuzz_v1.py:

    git show 33745a6:force136_v1/code/force136_v1.py > /tmp/oldv/force136_v1.py
    F136_CODE=../../../force136_v1/code python3 fuzz_catches_v101.py /tmp/oldv

Note: run it on the v1.0.2 engine (commit 338cb0d). With the v1.0.3 engine the old bot also differs in the
J25 return, which the engine now decides, so more differences appear."""
import sys,os
sys.path.insert(0,sys.argv[1])                     # the old bot shadows the current one
import force136_v1 as V
assert os.path.abspath(V.__file__).startswith(os.path.abspath(sys.argv[1]))
sys.path.insert(1,os.environ['F136_CODE'])
import fuzz_v1 as Z
counts,kinds,found=Z.run(1500,700000)
print(dict(counts));[print(v,k) for k,v in kinds.most_common(5)]
print(found[0]['action'],found[0]['diff'][:3])
