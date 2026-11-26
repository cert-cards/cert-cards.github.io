"""problems.json의 풀이를 주어진 파이썬으로 돌려 답·점수를 확인한다.
사용: <python> verify_practice.py [problems.json 경로]"""
import json, subprocess, sys, tempfile, shutil, re, time
from pathlib import Path
import numpy as np, pandas as pd
from sklearn import metrics as M
P = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "data/bigdata-analysis-engineer/practice/problems.json"
bank = json.loads(P.read_text()); base = P.parent
bad = 0
for p in bank["problems"]:
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "data").mkdir()
        for f in p.get("files", []):
            shutil.copy(base / f, Path(d) / "data" / Path(f).name)
        (Path(d) / "s.py").write_text(p["solution"])
        t0 = time.time()
        r = subprocess.run([sys.executable, "-I", "-W", "ignore", "s.py"], cwd=d, capture_output=True, text=True, timeout=120)
        dt = time.time() - t0
        if r.returncode:
            bad += 1; print(p["id"], "실행 오류", r.stderr.strip().splitlines()[-1:]); continue
        if p["type"] in (1, 3):
            out = r.stdout.split() + [l.strip() for l in r.stdout.splitlines()]   # 공백이 든 답(「푸른 등대」)은 줄 단위로
            want = [str(a["value"]) for a in p["answers"]]
            def same(a, b):
                try: return float(a) == float(b)
                except ValueError: return a == b
            ok = len(out) >= len(want) and all(any(same(o, w) for o in out) for w in want)
            if not ok:
                bad += 1; print(p["id"], "답 불일치", want, "출력", r.stdout.strip()[:200])
        else:
            sub = pd.read_csv(Path(d) / p["submit"]["file"])
            truth = pd.read_csv(base / p["truth"])["y"]
            ok = list(sub.columns) == [p["submit"]["column"]] and len(sub) == len(truth) == p["submit"]["rows"]
            pr = sub[p["submit"]["column"]]; m = p["metric"]
            sc = {"rmse": lambda: np.sqrt(M.mean_squared_error(truth, pr)), "rmsle": lambda: np.sqrt(M.mean_squared_log_error(truth, pr)),
                  "mae": lambda: M.mean_absolute_error(truth, pr), "r2": lambda: M.r2_score(truth, pr),
                  "accuracy": lambda: M.accuracy_score(truth.astype(str), pr.astype(str)),
                  "f1": lambda: M.f1_score(truth.astype(str), pr.astype(str), pos_label=str(p.get("pos_label", 1))),
                  "f1_macro": lambda: M.f1_score(truth.astype(str), pr.astype(str), average="macro"),
                  "roc_auc": lambda: M.roc_auc_score(truth, pr)}[m]() if ok else None
            ref = p["reference"]["solution"]
            print(p["id"], m, "형식", "OK" if ok else "틀림", "점수", None if sc is None else round(float(sc), 4), "기록", ref, f"{dt:.1f}s")
            if not ok or abs(float(sc) - ref) > max(0.02 * abs(ref), 1e-3): bad += 1
print("문제", len(bank["problems"]), "· 불일치", bad)
sys.exit(1 if bad else 0)
