// 실습 탭의 파이썬: Pyodide(브라우저에서 도는 CPython)를 웹 워커에서 돌린다.
// 화면이 멈추지 않고, 정지할 때는 워커를 통째로 끝내고 새로 만든다.
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
importScripts(PYODIDE + 'pyodide.js');

const HOME = '/home/pyodide';
const say = (type, data) => postMessage(Object.assign({ type }, data));
let py = null;

const ready = (async () => {
  say('status', { s: '파이썬을 불러오는 중' });
  py = await loadPyodide({ indexURL: PYODIDE });
  say('status', { s: 'numpy · pandas를 불러오는 중' });
  await py.loadPackage(['numpy', 'pandas'], { messageCallback: () => {} });
  py.FS.mkdirTree(HOME + '/data');
  const v = py.runPython(`
import sys, numpy, pandas
f"Python {sys.version.split()[0]} · pandas {pandas.__version__} · numpy {numpy.__version__}"`);
  say('ready', { s: v });
})().catch(err => say('fatal', { s: String(err && err.message || err) }));

// 파이썬 오류에서 Pyodide 내부 줄은 빼고 내 코드 부분만 남긴다
function trimTraceback(msg){
  const lines = msg.split('\n');
  const at = lines.findIndex(l => l.includes('File "<exec>"'));
  if (at < 0) return msg.trim();
  return [lines[0], ...lines.slice(at)].join('\n').trim();
}
function rmIfExists(p){ try { py.FS.unlink(p); } catch (_) {} }

// 작업형 2 채점: 내 코드가 만든 result.csv를 숨겨 둔 정답과 견준다
const GRADE = `
import io, json, numpy as np, pandas as pd
from sklearn import metrics as M
def _grade(spec, truth_text):
    out = {"ok": False}
    try:
        sub = pd.read_csv(spec["file"])
    except FileNotFoundError:
        out["msg"] = f"{spec['file']} 파일이 없습니다. to_csv('{spec['file']}', index=False)로 만들었는지 확인하세요."
        return json.dumps(out, ensure_ascii=False)
    except Exception as e:
        out["msg"] = f"{spec['file']}을 읽지 못했습니다: {e}"
        return json.dumps(out, ensure_ascii=False)
    cols = list(sub.columns)
    probs = []
    if cols != [spec["column"]]:
        probs.append(f"칼럼이 {cols}입니다. '{spec['column']}' 하나만 있어야 합니다" + (" (index=False를 빠뜨리면 이름 없는 칼럼이 생깁니다)" if any(str(c).startswith("Unnamed") for c in cols) else ""))
    truth = pd.read_csv(io.StringIO(truth_text))["y"]
    if len(sub) != len(truth):
        probs.append(f"행 수가 {len(sub)}입니다. 평가용 데이터와 같은 {len(truth)}개여야 합니다")
    if probs:
        out["msg"] = " / ".join(probs)
        return json.dumps(out, ensure_ascii=False)
    p = sub[spec["column"]]
    if p.isna().any():
        out["msg"] = f"예측값에 결측치가 {int(p.isna().sum())}개 있습니다"
        return json.dumps(out, ensure_ascii=False)
    m = spec["metric"]
    try:
        if m == "rmse": s = float(np.sqrt(M.mean_squared_error(truth, p)))
        elif m == "rmsle":
            if (p < 0).any():
                out["msg"] = f"RMSLE는 음수 예측을 받지 않습니다. 음수 예측이 {int((p < 0).sum())}개 있습니다 (np.clip 등으로 0 이상으로)"
                return json.dumps(out, ensure_ascii=False)
            s = float(np.sqrt(M.mean_squared_log_error(truth, p)))
        elif m == "mae": s = float(M.mean_absolute_error(truth, p))
        elif m == "r2": s = float(M.r2_score(truth, p))
        elif m == "accuracy": s = float(M.accuracy_score(truth.astype(str), p.astype(str)))
        elif m == "f1": s = float(M.f1_score(truth.astype(str), p.astype(str), pos_label=str(spec.get("pos_label", 1))))
        elif m == "f1_macro": s = float(M.f1_score(truth.astype(str), p.astype(str), average="macro"))
        elif m == "roc_auc": s = float(M.roc_auc_score(truth, p))
        else: raise ValueError("모르는 평가지표 " + m)
    except Exception as e:
        out["msg"] = f"점수를 계산하지 못했습니다: {e}"
        return json.dumps(out, ensure_ascii=False)
    out.update(ok=True, score=s)
    return json.dumps(out, ensure_ascii=False)
`;

onmessage = async e => {
  const m = e.data;
  try { await ready; } catch (_) { return; }
  if (!py) return;
  if (m.type === 'files'){
    // 문제를 열 때마다 data/ 폴더를 그 문제의 파일로 채운다
    for (const name of py.FS.readdir(HOME + '/data')) if (name !== '.' && name !== '..') rmIfExists(HOME + '/data/' + name);
    for (const f of m.files) py.FS.writeFile(HOME + '/data/' + f.name, f.text);
    say('files', {});
    return;
  }
  if (m.type === 'run'){
    rmIfExists(HOME + '/' + (m.clean || 'result.csv'));
    py.setStdout({ batched: s => say('out', { s }) });
    py.setStderr({ batched: s => say('err', { s }) });
    try {
      await py.loadPackagesFromImports(m.code, { messageCallback: s => say('status', { s: s.replace(/^Loading /, '불러오는 중: ').replace(/^Loaded /, '불러옴: ') }) });
      const ns = py.globals.get('dict')();
      try { await py.runPythonAsync(m.code, { globals: ns }); }
      finally { ns.destroy(); }
      say('done', {});
    } catch (err) {
      say('error', { s: trimTraceback(String(err && err.message || err)) });
    }
    return;
  }
  if (m.type === 'grade'){
    try {
      await py.loadPackage(['scikit-learn'], { messageCallback: () => {} });
      const ns = py.globals.get('dict')();
      py.runPython(GRADE, { globals: ns });
      const fn = ns.get('_grade');
      const res = fn(py.toPy(m.spec), m.truth);
      fn.destroy(); ns.destroy();
      say('graded', { res: JSON.parse(res) });
    } catch (err) {
      say('graded', { res: { ok: false, msg: '채점 중 오류: ' + trimTraceback(String(err && err.message || err)) } });
    }
  }
};
