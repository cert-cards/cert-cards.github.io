"""parts/x3.json(작업형3 검정별 연습)의 solution을 두 파이썬으로 돌려 answers와 비교한다 (시스템 python3로 실행).

EXAM_PY · BROWSER_PY 환경변수가 가리키는 두 파이썬에서 출력이 정답과 같아야 하고,
두 버전의 원값(반올림 전)도 함께 보여 준다. 그 밖에 문제 객체 형식, CSV 행 수·쉼표·따옴표,
지문에 라이브러리·함수·인자 이름이 없는지를 본다.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PYS = {'exam': os.environ.get('EXAM_PY', 'python3'), 'pyo26': os.environ.get('BROWSER_PY', 'python3')}
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))
KEYS = ["a1", "a2", "a3"]
FIELDS = ["id", "set", "type", "no", "points", "title", "statement", "files", "starter", "answers", "solution", "explain"]
# 지문에 나오면 안 되는 라이브러리·함수·인자 이름 (대소문자 구분: 검정 이름 Levene·Shapiro–Wilk 등은 허용)
BANNED = ["scipy", "statsmodels", "pandas", "numpy", "sklearn", "smf.", "pd.", "np.", "stats.",
          "ttest", "chi2_contingency", "chisquare", "levene", "bartlett", "shapiro", "mannwhitneyu",
          "wilcoxon", "kruskal", "pearsonr", "spearmanr", "tukey", "anova_lm", "f_oneway", "ols(",
          "equal_var", "alternative=", "correction=", "center=", "typ=", "zero_method", "use_continuity",
          "crosstab", "groupby", "dropna", "to_datetime", "dayofweek", "value_counts", "reindex", "pivot"]

probs = json.load(open(os.path.join(REPO, "parts", "x3.json"), encoding="utf-8"))
bad = 0

ids = [p["id"] for p in probs]
if ids != [f"x3-{i:02d}" for i in range(1, 16)]:
    print("BAD ids", ids)
    bad += 1

for p in probs:
    # 형식
    probs_fmt = []
    if list(p.keys()) != FIELDS:
        probs_fmt.append(f"fields {list(p.keys())}")
    if (p["set"], p["type"], p["points"]) != ("x3", 3, 15) or p["id"] != f"x3-{p['no']}":
        probs_fmt.append("set/type/points/no")
    if " — " not in p["title"]:
        probs_fmt.append("title")
    if not 2 <= len(p["answers"]) <= 3 or [a["label"] for a in p["answers"]] != ["①", "②", "③"][:len(p["answers"])]:
        probs_fmt.append("answers")
    if "【제출 형식】" not in p["statement"] or f"`{os.path.basename(p['files'][0])}`" not in p["statement"]:
        probs_fmt.append("statement 형식")
    hit = [b for b in BANNED if b in p["statement"]]
    if hit:
        probs_fmt.append(f"지문에 이름 {hit}")
    for f in p["files"]:
        path = os.path.join(REPO, f)
        raw = open(path, encoding="utf-8").read()
        rows = list(csv.reader(raw.splitlines()))
        if not 60 <= len(rows) - 1 <= 400:
            probs_fmt.append(f"rows {len(rows) - 1}")
        if any(len(r) != len(rows[0]) for r in rows) or '"' in raw:
            probs_fmt.append("csv 쉼표·따옴표")
    if probs_fmt:
        bad += 1
        print(f"{p['id']:8s} FORMAT BAD {probs_fmt}")

    # 두 파이썬 실행
    k = len(p["answers"])
    raws = {}
    for name, py in PYS.items():
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "data"))
        for f in p["files"]:
            shutil.copy(os.path.join(REPO, f), os.path.join(tmp, "data", os.path.basename(f)))
        code = p["solution"] + "\nprint('RAW', " + ", ".join(
            f"({key} if isinstance({key}, str) else repr(float({key})))" for key in KEYS[:k]) + ")\n"
        res = subprocess.run([py, "-I", "-c", code], cwd=tmp, capture_output=True, text=True, timeout=60)
        shutil.rmtree(tmp)
        lines = res.stdout.strip().splitlines()
        raw = [l for l in lines if l.startswith("RAW")]
        outs = [l for l in lines if not l.startswith("RAW")]
        raws[name] = raw[0] if raw else None
        ok = len(outs) == k
        if ok:
            for o, a in zip(outs, p["answers"]):
                try:
                    ok &= float(o) == float(a["value"])
                except ValueError:
                    ok &= o.strip() == a["value"]
        if not ok or res.returncode:
            bad += 1
        print(f"{p['id']:8s} {name:6s} {'OK ' if ok and not res.returncode else 'BAD'} out={outs} ans={[a['value'] for a in p['answers']]} {res.stderr[-300:] if res.returncode else ''}")
    print(f"{'':8s} raw exam ={raws['exam']}\n{'':8s} raw pyo26={raws['pyo26']}")
print("FAILURES", bad)
sys.exit(1 if bad else 0)
