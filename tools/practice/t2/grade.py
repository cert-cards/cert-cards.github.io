
import sys, json, numpy as np, pandas as pd
from sklearn import metrics as M
res, truth_path, m, pos = sys.argv[1:5]
sub = pd.read_csv(res); truth = pd.read_csv(truth_path)["y"]
out = {"cols": list(sub.columns), "rows": len(sub), "nrows_truth": len(truth)}
p = sub["pred"]
out["na"] = int(p.isna().sum())
if m == "rmse": s = float(np.sqrt(M.mean_squared_error(truth, p)))
elif m == "rmsle":
    out["neg"] = int((p < 0).sum()); s = float(np.sqrt(M.mean_squared_log_error(truth, p)))
elif m == "mae": s = float(M.mean_absolute_error(truth, p))
elif m == "f1_macro": s = float(M.f1_score(truth.astype(str), p.astype(str), average="macro"))
elif m == "roc_auc": s = float(M.roc_auc_score(truth, p))
out["score"] = s
print(json.dumps(out))
