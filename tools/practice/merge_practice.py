"""parts/*.json → problems.json. 합친 뒤 parts/는 지운다(--keep이면 남긴다).

parts/t1.json · t2.json · t3.json : 모의고사 세트(m1, m2, …)의 문제. 세트마다 1-1, 1-2, 1-3, 2, 3-1, 3-2
parts/x3.json                      : 작업형3 검정별 연습(세트 x3). 시험 모드 없이 유형 연습용
"""
import json, shutil, sys
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "data/bigdata-analysis-engineer/practice"
probs = []
for f in sorted((P / "parts").glob("*.json")):
    probs += json.loads(f.read_text())
order = {"1-1": 0, "1-2": 1, "1-3": 2, "2": 3, "3-1": 4, "3-2": 5}
mock = sorted({p["set"] for p in probs if p["set"].startswith("m")}, key=lambda s: int(s[1:]))
extra = [s for s in ("x3",) if any(p["set"] == s for p in probs)]
rank = {s: i for i, s in enumerate(mock + extra)}
probs.sort(key=lambda p: (rank[p["set"]], order.get(p["no"], 10), p["id"]))
sets = [{"id": s, "title": f"모의고사 {s[1:]}회"} for s in mock]
if "x3" in extra:
    sets.append({"id": "x3", "title": "작업형 3 검정별 연습", "exam": False})
bank = {"sets": sets, "problems": probs}
(P / "problems.json").write_text(json.dumps(bank, ensure_ascii=False, indent=1) + "\n")
print(len(sets), "세트", len(probs), "문제")
if "--keep" not in sys.argv:
    shutil.rmtree(P / "parts")
