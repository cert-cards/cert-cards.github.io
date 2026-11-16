// 실습 페이지의 파이썬: Pyodide(브라우저에서 도는 CPython)를 웹 워커에서 돌린다.
// 화면이 멈추지 않고, 정지할 때는 워커를 통째로 끝내고 새로 만든다.
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
importScripts(PYODIDE + 'pyodide.js');

const say = (type, data) => postMessage(Object.assign({ type }, data));
let py = null;

const ready = (async () => {
  say('status', { s: '파이썬을 불러오는 중' });
  py = await loadPyodide({ indexURL: PYODIDE });
  say('status', { s: 'numpy · pandas를 불러오는 중' });
  await py.loadPackage(['numpy', 'pandas'], { messageCallback: () => {} });
  py.FS.mkdirTree('/home/pyodide/data');
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

onmessage = async e => {
  const m = e.data;
  try { await ready; } catch (_) { return; }
  if (!py) return;
  if (m.type === 'file'){
    py.FS.writeFile('/home/pyodide/data/' + m.name, new Uint8Array(m.buf));
    say('file', { name: m.name });
    return;
  }
  if (m.type !== 'run') return;
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
};
