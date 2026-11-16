"""parts/t3.json 의 solution을 두 파이썬으로 돌려 answers와 비교한다 (시스템 python3로 실행)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

PYS = {'exam': os.environ.get('EXAM_PY', 'python3'), 'pyo26': os.environ.get('BROWSER_PY', 'python3')}
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))

probs = json.load(open(os.path.join(REPO, "parts", "t3.json"), encoding="utf-8"))
bad = 0
for p in probs:
    raws = {}
    for name, py in PYS.items():
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "data"))
        for f in p["files"]:
            shutil.copy(os.path.join(REPO, f), os.path.join(tmp, "data", os.path.basename(f)))
        code = p["solution"] + "\nprint('RAW', repr(float(a1)) if not isinstance(a1, str) else a1, repr(float(a2)), repr(float(a3)) if not isinstance(a3, str) else a3)\n"
        r = subprocess.run([py, "-I", "-c", code], cwd=tmp, capture_output=True, text=True, timeout=60)
        shutil.rmtree(tmp)
        lines = [l for l in r.stdout.strip().splitlines()]
        raw = [l for l in lines if l.startswith("RAW")]
        outs = [l for l in lines if not l.startswith("RAW")]
        raws[name] = raw[0] if raw else None
        ok = len(outs) == len(p["answers"])
        if ok:
            for o, a in zip(outs, p["answers"]):
                try:
                    ok &= float(o) == float(a["value"])
                except ValueError:
                    ok &= o.strip() == a["value"]
        if not ok or r.returncode:
            bad += 1
        print(f"{p['id']:8s} {name:6s} {'OK ' if ok and not r.returncode else 'BAD'} out={outs} ans={[a['value'] for a in p['answers']]} {r.stderr[-300:] if r.returncode else ''}")
    print(f"{'':8s} raw exam ={raws['exam']}\n{'':8s} raw pyo26={raws['pyo26']}")
print("FAILURES", bad)
sys.exit(1 if bad else 0)
