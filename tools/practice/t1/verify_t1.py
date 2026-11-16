# parts/t1.json의 solution을 두 파이썬에서 실행해 answers와 비교한다.
import json, os, shutil, subprocess, tempfile, time

PYS = {'exam': os.environ.get('EXAM_PY', 'python3'), 'pyo26': os.environ.get('BROWSER_PY', 'python3')}
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))


def same(a, b):
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


probs = json.load(open(f'{ROOT}/parts/t1.json', encoding='utf-8'))
bad = 0
for p in probs:
    line = [p['id']]
    for name, py in PYS.items():
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(f'{tmp}/data')
            for f in p['files']:
                shutil.copy(f'{ROOT}/{f}', f'{tmp}/data/')
            open(f'{tmp}/sol.py', 'w', encoding='utf-8').write(p['solution'])
            t = time.time()
            r = subprocess.run([py, '-W', 'ignore', 'sol.py'], cwd=tmp, capture_output=True, text=True)
            dt = time.time() - t
        out = r.stdout.strip().splitlines()
        exp = [a['value'] for a in p['answers']]
        ok = r.returncode == 0 and len(out) == len(exp) and all(same(o, e) for o, e in zip(out, exp))
        bad += not ok
        line.append(f"{name}:{'OK' if ok else 'FAIL'} {out} ({dt:.1f}s)")
        if not ok:
            line.append(r.stderr[-500:])
    line.append(f"expected {[a['value'] for a in p['answers']]}")
    print(' | '.join(line))
print('FAILED', bad)
