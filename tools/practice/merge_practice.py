"""parts/t1·t2·t3.json → problems.json (세트 순서: 1-1,1-2,1-3,2,3-1,3-2). 합친 뒤 parts/는 지운다."""
import json, shutil, sys
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "data/bigdata-analysis-engineer/practice"
parts = {t: json.loads((P / f"parts/t{t}.json").read_text()) for t in (1, 2, 3)}
probs = [p for t in (1, 2, 3) for p in parts[t]]
sets = sorted({p["set"] for p in probs}, key=lambda s: int(s[1:]))
order = {"1-1": 0, "1-2": 1, "1-3": 2, "2": 3, "3-1": 4, "3-2": 5}
probs.sort(key=lambda p: (int(p["set"][1:]), order[p["no"]]))
bank = {"sets": [{"id": s, "title": f"모의고사 {s[1:]}회"} for s in sets], "problems": probs}
(P / "problems.json").write_text(json.dumps(bank, ensure_ascii=False, indent=1) + "\n")
print(len(sets), "세트", len(probs), "문제")
if "--keep" not in sys.argv:
    shutil.rmtree(P / "parts")
