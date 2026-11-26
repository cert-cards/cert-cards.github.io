"""작업형2: 데이터 생성 → solution/baseline을 두 파이썬으로 실행·채점 → parts/t2.json 작성."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = {'exam': os.environ.get('EXAM_PY', 'python3'), 'pyo': os.environ.get('BROWSER_PY', 'python3')}
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))
sys.path.insert(0, HERE)
from problems_t2 import P, STARTER

# 작업형2 채점 — assets/py-worker.js의 _grade와 같은 계산
GRADE = r'''
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
'''

GEN = '--gen' in sys.argv
if GEN:
    subprocess.run([PY['exam'], os.path.join(HERE, 'gen.py'), REPO], check=True)

gpath = os.path.join(HERE, 'grade.py')
open(gpath, 'w').write(GRADE)


def run(code, setid, py):
    d = tempfile.mkdtemp(dir=os.path.join(HERE, 'runs'))
    os.makedirs(os.path.join(d, 'data'))
    for f in ('train.csv', 'test.csv'):
        shutil.copy(os.path.join(REPO, setid, f), os.path.join(d, 'data', f))
    open(os.path.join(d, 'main.py'), 'w').write(code)
    t = time.time()
    r = subprocess.run([PY[py], 'main.py'], cwd=d, capture_output=True, text=True, timeout=300)
    el = time.time() - t
    if r.returncode != 0:
        raise SystemExit(f'{setid} {py} failed:\n{r.stderr}')
    return d, el, r.stdout


def grade(d, setid, metric, py, pos=1):
    r = subprocess.run([PY[py], gpath, os.path.join(d, 'result.csv'),
                        os.path.join(REPO, setid, 't2_truth.csv'), metric, str(pos)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout.strip().splitlines()[-1])


os.makedirs(os.path.join(HERE, 'runs'), exist_ok=True)

# 해설에 쓰는 보조 수치 (시험 버전으로 계산)
EXTRA = {
    'm3': """import pandas as pd
from sklearn.linear_model import LinearRegression
train = pd.read_csv('data/train.csv'); test = pd.read_csv('data/test.csv')
X_all = pd.get_dummies(pd.concat([train.drop(columns=['id', 'sessions']), test.drop(columns=['id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
p = LinearRegression().fit(X, train['sessions']).predict(X_test)
print((p < 0).sum())
pd.DataFrame({'pred': p}).to_csv('result.csv', index=False)
""",
    'm4': """import pandas as pd
from sklearn.ensemble import RandomForestClassifier
train = pd.read_csv('data/train.csv'); test = pd.read_csv('data/test.csv')
y = train['re_register']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['member_id', 're_register']), test.drop(columns=['member_id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestClassifier(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
print('hard')
""",
    'm5': """import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
train = pd.read_csv('data/train.csv'); test = pd.read_csv('data/test.csv')
for col in ['station_min', 'built_year']:
    train[col] = train[col].fillna(train[col].median())
y = train['rent']
X = train.drop(columns=['room_id', 'rent']); X_test = test.drop(columns=['room_id'])
for col in ['gu', 'room_type', 'parking', 'full_option']:
    X[col] = LabelEncoder().fit_transform(X[col])
    X_test[col] = LabelEncoder().fit_transform(X_test[col])   # 잘못: 따로 fit
m = RandomForestRegressor(n_estimators=300, random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
print('misenc')
""",
    'm6': """import pandas as pd
from sklearn.ensemble import RandomForestClassifier
train = pd.read_csv('data/train.csv'); test = pd.read_csv('data/test.csv')
y = train['result']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['booking_id', 'result']), test.drop(columns=['booking_id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestClassifier(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict_proba(X_test)[:, list(m.classes_).index('노쇼')]}).to_csv('result.csv', index=False)
print('right')
""",
    'm7': """import pandas as pd
from sklearn.ensemble import RandomForestRegressor
train = pd.read_csv('data/train.csv'); test = pd.read_csv('data/test.csv')
y = train['loans']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['date', 'loans']), test.drop(columns=['date'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestRegressor(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
print('nodate')
""",
}
EXTRA_KEY = {'m4': 'hard', 'm5': 'misenc', 'm6': 'right', 'm7': 'nodate'}

out_objs, report = [], []
for p in P:
    s = p['set']
    rec = {'id': p['id'], 'metric': p['metric']}
    for kind in ('solution', 'baseline'):
        for py in ('exam', 'pyo'):
            d, el, stdout = run(p[kind], s, py)
            g = grade(d, s, p['metric'], py, p.get('pos_label', 1))
            assert g['cols'] == ['pred'], g
            assert g['rows'] == g['nrows_truth'] == p['rows'], g
            assert g['na'] == 0 and g.get('neg', 0) == 0, g
            rec[f'{kind}_{py}'] = round(g['score'], 4)
            rec[f'{kind}_{py}_sec'] = round(el, 1)
            if kind == 'solution' and py == 'exam':
                rec['stdout'] = stdout[-600:]
    fmt = {'base': rec['baseline_exam'], 'sol': rec['solution_exam']}
    if s in EXTRA:
        d, el, stdout = run(EXTRA[s], s, 'exam')
        if s == 'm3':
            fmt['neg'] = int(stdout.strip().splitlines()[-1])
        else:
            g = grade(d, s, p['metric'], 'exam')
            fmt[EXTRA_KEY[s]] = g['score']
            rec['extra'] = round(g['score'], 4)
    if s == 'm3':
        rec['extra_linreg_neg'] = fmt['neg']
    obj = {
        'id': p['id'], 'set': s, 'type': 2, 'no': '2', 'points': 40,
        'title': p['title'],
        'statement': p['statement'],
        'files': [f'{s}/train.csv', f'{s}/test.csv'],
        'starter': STARTER,
        'submit': {'file': 'result.csv', 'column': 'pred', 'rows': p['rows']},
        'metric': p['metric'],
    }
    if 'pos_label' in p:
        obj['pos_label'] = p['pos_label']
    obj.update({
        'truth': f'{s}/t2_truth.csv',
        'reference': {'baseline': rec['baseline_exam'], 'solution': rec['solution_exam']},
        'solution': p['solution'],
        'explain': p['explain'].format(**fmt),
    })
    out_objs.append(obj)
    report.append(rec)
    print(json.dumps({k: v for k, v in rec.items() if k != 'stdout'}, ensure_ascii=False))

os.makedirs(os.path.join(REPO, 'parts'), exist_ok=True)
with open(os.path.join(REPO, 'parts', 't2.json'), 'w', encoding='utf-8') as f:
    json.dump(out_objs, f, ensure_ascii=False, indent=1)
    f.write('\n')
json.dump(report, open(os.path.join(HERE, 'report.json'), 'w'), ensure_ascii=False, indent=1)
shutil.rmtree(os.path.join(HERE, 'runs'))
print('wrote parts/t2.json')
