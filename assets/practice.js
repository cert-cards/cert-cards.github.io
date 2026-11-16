// 실습 페이지: ?deck=<id>&file=<md 파일>&n=<그 파일의 몇 번째 코드 문제>
// 주소에 deck이 없으면 빈 편집기로 자유롭게 쓴다.
const $ = s => document.querySelector(s);
const P = new URLSearchParams(location.search);
const DECK = P.get('deck');
const RUN_LIMIT = 60;   // 초. 시험도 한 번 실행은 1분까지다
let INFO = {}, LIST = [], idx = -1;
let worker = null, ready = false, running = false, timer = null, stdout = '';
const uploads = [];     // 워커를 새로 만들 때 다시 넣는다

const store = {
  get(k){ try{ return localStorage.getItem('cert-cards:practice:' + k); }catch(e){ return null; } },
  set(k, v){ try{ v === null ? localStorage.removeItem('cert-cards:practice:' + k) : localStorage.setItem('cert-cards:practice:' + k, v); }catch(e){} }
};
const cur = () => LIST[idx];
const saveKey = () => cur() ? `${DECK}:${cur().file}:${cur().it.n}` : 'free';

// ── 문제 불러오기
async function load(){
  if (!DECK){ show(); return; }
  INFO = JSON.parse(await getText(`../data/${DECK}/deck.json`));
  const texts = await Promise.all(INFO.files.map(f => getText(`../data/${DECK}/${f}`)));
  texts.forEach((md, i) => parseDeck(md).forEach(g => g.items.forEach(it => {
    if (canPractice(it, INFO)) LIST.push({ it, file: INFO.files[i], ch: (i + 1) + '. ' + g.ch, t: g.t });
  })));
  const file = P.get('file'), n = +P.get('n');
  idx = LIST.findIndex(x => x.file === file && x.it.n === n);
  if (idx < 0 && LIST.length) idx = 0;
  $('#back').href = `../${DECK}/`;
  $('#back').textContent = '← ' + INFO.title + ' 카드';
  document.title = INFO.title + ' 코드 실습';
  $('#title').textContent = INFO.title + ' 코드 실습';
  show();
}

function show(){
  const x = cur();
  const free = !x;
  $('#blankNote').hidden = true;
  ['#where', '#question', '.px-nav', '#ansBtn'].forEach(s => $(s).hidden = free);
  $('#reset').hidden = free;
  $('#ans').hidden = true; $('#ansBtn').setAttribute('aria-expanded', 'false'); $('#ansBtn').textContent = '정답 보기';
  $('#out').textContent = ''; $('#verdict').textContent = ''; $('#verdict').className = 'px-verdict';
  if (free){
    $('#pos').textContent = '';
    $('#editor').value = store.get('free') || '';
    return;
  }
  $('#pos').textContent = `${idx + 1} / ${LIST.length}`;
  $('#where').textContent = x.ch + ' › ' + x.t;
  $('#question').innerHTML = fmt(x.it.a.split('\n```')[0]);
  $('#ans').innerHTML = fmt(x.it.b);
  $('#editor').value = store.get(saveKey()) ?? x.it.code;
  $('#blankNote').hidden = !/[①②③④⑤⑥⑦⑧⑨]/.test(x.it.code);
  $('#prev').disabled = idx <= 0;
  $('#next').disabled = idx >= LIST.length - 1;
  const u = new URL(location.href);
  u.searchParams.set('file', x.file); u.searchParams.set('n', x.it.n);
  history.replaceState(null, '', u);
}
function go(d){ const j = idx + d; if (j < 0 || j >= LIST.length) return; idx = j; show(); window.scrollTo(0, 0); }

// ── 파이썬 워커
function status(s, cls){ const el = $('#status'); el.textContent = s; el.className = 'px-status' + (cls ? ' ' + cls : ''); }
function append(s, cls){
  const span = document.createElement('span');
  if (cls) span.className = cls;
  span.textContent = s; $('#out').appendChild(span);
}
function makeWorker(){
  ready = false; $('#run').disabled = true;
  worker = new Worker('../assets/py-worker.js');
  worker.onmessage = e => {
    const m = e.data;
    if (m.type === 'status') status(m.s + ' …');
    else if (m.type === 'ready'){
      ready = true; $('#run').disabled = false; status('준비됨 · ' + m.s, 'ok');
      uploads.forEach(f => worker.postMessage({ type: 'file', name: f.name, buf: f.buf.slice(0) }));
    }
    else if (m.type === 'fatal') status('파이썬을 불러오지 못했습니다. 네트워크를 확인하고 새로고침해 주세요. (' + m.s + ')', 'bad');
    else if (m.type === 'file') status(`data/${m.name}에 올렸습니다 · pd.read_csv('data/${m.name}')로 읽습니다`, 'ok');
    else if (m.type === 'out'){ stdout += m.s + '\n'; append(m.s + '\n'); }
    else if (m.type === 'err') append(m.s + '\n', 'warn');
    else if (m.type === 'error'){ finish(); append(m.s + '\n', 'error'); status('오류로 멈췄습니다', 'bad'); }
    else if (m.type === 'done'){ finish(); status('실행을 마쳤습니다', 'ok'); judge(); }
  };
  worker.onerror = e => status('파이썬 워커 오류: ' + (e.message || e), 'bad');
}
function run(){
  if (!ready || running) return;
  running = true; stdout = '';
  $('#out').textContent = ''; $('#verdict').textContent = ''; $('#verdict').className = 'px-verdict';
  $('#run').disabled = true; $('#stop').hidden = false;
  status('실행 중 …');
  worker.postMessage({ type: 'run', code: $('#editor').value });
  timer = setTimeout(() => stop(`${RUN_LIMIT}초가 넘어 멈췄습니다 (시험도 한 번 실행은 1분까지입니다)`), RUN_LIMIT * 1000);
}
function finish(){
  running = false; clearTimeout(timer);
  $('#run').disabled = !ready; $('#stop').hidden = true;
}
function stop(why){
  if (!running) return;
  worker.terminate(); finish();
  append('\n' + (why || '멈췄습니다') + '\n', 'error');
  makeWorker();
  status('파이썬을 다시 불러오는 중 …');
}
// 출력이 카드의 정답과 같은지 (빈칸 문제·정답이 출력이 아닌 문제는 견주지 않는다)
function judge(){
  const want = expectedOutput(cur() && cur().it);
  if (want === null) return;
  const got = stdout.replace(/\s+$/, ''), exp = want.replace(/\s+$/, '');
  // 브라우저 파이썬은 32비트라 기본 정수형이 int32로 찍힌다. 시험 환경(64비트)은 int64
  const only32 = got !== exp && got.replace(/int32/g, 'int64') === exp;
  const same = got === exp || only32;
  $('#verdict').textContent = only32 ? '정답과 같은 출력 (int32는 브라우저 차이, 시험 환경은 int64)' : same ? '정답과 같은 출력' : '정답과 다른 출력';
  $('#verdict').className = 'px-verdict ' + (same ? 'ok' : 'bad');
}

// ── 버튼과 키
$('#run').addEventListener('click', run);
$('#stop').addEventListener('click', () => stop());
$('#reset').addEventListener('click', () => { if (cur()){ $('#editor').value = cur().it.code; store.set(saveKey(), null); } });
$('#clear').addEventListener('click', () => { $('#editor').value = ''; store.set(saveKey(), ''); $('#editor').focus(); });
$('#prev').addEventListener('click', () => go(-1));
$('#next').addEventListener('click', () => go(1));
$('#ansBtn').addEventListener('click', () => {
  const open = $('#ans').hidden;
  $('#ans').hidden = !open; $('#ansBtn').setAttribute('aria-expanded', open); $('#ansBtn').textContent = open ? '정답 가리기' : '정답 보기';
});
let saveT = null;
$('#editor').addEventListener('input', () => {
  clearTimeout(saveT);
  saveT = setTimeout(() => {
    const v = $('#editor').value;
    store.set(saveKey(), cur() && v === cur().it.code ? null : v);
  }, 300);
});
$('#editor').addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter'){ e.preventDefault(); run(); return; }
  if (e.key === 'Tab' && !e.shiftKey && !e.metaKey && !e.ctrlKey && !e.altKey){
    e.preventDefault();
    const t = e.target, a = t.selectionStart;
    t.setRangeText('    ', a, t.selectionEnd, 'end');
    t.dispatchEvent(new Event('input'));
  }
});
$('#upload').addEventListener('change', async e => {
  for (const f of e.target.files){
    const buf = await f.arrayBuffer();
    const i = uploads.findIndex(u => u.name === f.name);
    if (i >= 0) uploads.splice(i, 1);
    uploads.push({ name: f.name, buf });
    if (ready) worker.postMessage({ type: 'file', name: f.name, buf: buf.slice(0) });
  }
  e.target.value = '';
  if (!ready) status('파이썬이 준비되면 파일을 넣습니다 …');
});

// 다크 모드 (카드 페이지와 같은 저장 이름)
const root = document.documentElement;
const themeStore = { get(){ try{ return localStorage.getItem('cert-cards:theme'); }catch(e){ return null; } }, set(v){ try{ localStorage.setItem('cert-cards:theme', v); }catch(e){} } };
const savedTheme = themeStore.get(); if (savedTheme) root.dataset.theme = savedTheme;
$('#themeBtn').addEventListener('click', () => {
  const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = dark ? 'light' : 'dark'; themeStore.set(root.dataset.theme);
});

makeWorker();
load().catch(err => { $('#question').hidden = false; $('#question').innerHTML = `<p class="empty">문제를 불러오지 못했습니다. (${esc(err.message)})</p>`; });
