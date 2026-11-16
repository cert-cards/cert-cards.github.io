// 실습 탭 (deck.json sections[].practice가 가리키는 문제 목록을 푼다)
// 문제 목록 JSON:
//   sets:     [{ id, title }]
//   problems: [{ id, set, type: 1|2|3, no, title, points, statement(Markdown), files: ['<set>/<파일>.csv'],
//                starter, answers: [{ label, format, value }],          ← 작업형 1·3: 답 칸
//                submit: { file, column, rows }, metric, truth, reference: { baseline, solution }, ← 작업형 2: CSV 채점
//                solution, explain }]
// 내 코드·답·채점 결과는 이 브라우저(localStorage)에만 남는다.
window.Practice = (() => {
  const RUN_LIMIT = 60;   // 초. 시험도 한 번 실행은 1분까지다
  const TYPE_NAME = { 1: '작업형 1', 2: '작업형 2', 3: '작업형 3' };
  const METRIC = {
    rmse: ['RMSE', false], rmsle: ['RMSLE', false], mae: ['MAE', false], r2: ['R²', true], accuracy: ['Accuracy', true],
    f1: ['F1', true], f1_macro: ['macro F1', true], roc_auc: ['ROC-AUC', true]
  };
  let root, ctx, BANK = { sets: [], problems: [] }, cur = null, mode = 'set';
  let worker = null, ready = false, running = false, timer = null, filesSent = null, after = null;
  const FILES = {};      // 파일 경로 → 내용(텍스트)

  const key = k => `cert-cards:${ctx.deck}:practice:${k}`;
  const st = {
    get(k, d){ try{ const v = localStorage.getItem(key(k)); return v === null ? d : JSON.parse(v); }catch(e){ return d; } },
    set(k, v){ try{ v === undefined ? localStorage.removeItem(key(k)) : localStorage.setItem(key(k), JSON.stringify(v)); }catch(e){} }
  };
  const q = s => root.querySelector(s);

  // ── 아주 작은 Markdown: 문단 · 목록(- ) · 표(|) · 코드 블록
  function md(s){
    return (s || '').split(/\n{2,}/).map(b => {
      const lines = b.split('\n');
      if (/^```/.test(b)) return fmt(b);
      if (lines.every(l => /^\s*[-*] /.test(l))) return '<ul>' + lines.map(l => `<li>${inline(l.replace(/^\s*[-*] /, ''))}</li>`).join('') + '</ul>';
      if (lines.every(l => /^\s*\|/.test(l))){
        const rows = lines.filter(l => !/^\s*\|[\s:|-]+\|\s*$/.test(l)).map(l => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim()));
        return '<div class="pr-tbl"><table><thead><tr>' + rows[0].map(c => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>' +
          rows.slice(1).map(r => '<tr>' + r.map(c => `<td>${inline(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>';
      }
      return '<p>' + lines.map(inline).join('<br>') + '</p>';
    }).join('');
  }
  const base = p => p.split('/').pop();
  const status = p => st.get('s:' + p.id, null);   // { done: true|false, score }

  // ── 화면 뼈대
  function skeleton(){
    root.innerHTML = `
<div class="pr">
  <aside class="pr-side">
    <div class="seg pr-mode" role="group" aria-label="목록 묶음">
      <button data-mode="set">모의고사</button><button data-mode="type">유형별</button>
    </div>
    <nav class="pr-list" id="prList"></nav>
  </aside>
  <section class="pr-main">
    <div class="pr-head"><div class="pr-where" id="prWhere"></div><h2 id="prTitle"></h2></div>
    <div class="pr-stmt" id="prStmt"></div>
    <div class="pr-files" id="prFiles"></div>
    <div class="pr-tools">
      <button class="btn quiz" id="prRun" disabled>실행</button>
      <button class="btn" id="prStop" hidden>정지</button>
      <button class="btn" id="prReset">처음 코드로</button>
      <span class="pr-hint">⌘/Ctrl + Enter로 실행</span>
    </div>
    <textarea id="prEditor" class="pr-editor" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" aria-label="코드 편집기"></textarea>
    <div class="pr-status" id="prStatus">파이썬 준비 중 · 처음 한 번은 수십 MB를 받습니다. 그다음부터는 브라우저에 저장된 것을 씁니다.</div>
    <div class="pr-sub">실행 결과</div>
    <pre class="pr-out" id="prOut" aria-live="polite"></pre>
    <div class="pr-answer" id="prAnswer"></div>
    <div class="pr-sol-row"><button class="btn" id="prSolBtn" aria-expanded="false">풀이 보기</button></div>
    <div class="pr-sol" id="prSol" hidden></div>
    <div class="pr-nav"><button class="btn" id="prPrev">← 이전 문제</button><button class="btn" id="prNext">다음 문제 →</button></div>
    <p class="pr-foot">브라우저 안에서 도는 파이썬(Pyodide 0.26.4: pandas 2.2.0 · numpy 1.26.4 · scipy 1.12.0 · scikit-learn 1.4.2 · statsmodels 0.14.2)입니다. 시험 환경과 버전이 조금 다를 수 있습니다. 한 번 실행은 시험처럼 60초가 넘으면 멈춥니다. 데이터는 <code>data/</code> 폴더에 있습니다. 문제와 데이터는 기출 유형을 따라 새로 만든 것입니다.</p>
  </section>
</div>`;
  }

  function order(){
    const ps = BANK.problems.slice();
    if (mode === 'type') ps.sort((a, b) => a.type - b.type || BANK.problems.indexOf(a) - BANK.problems.indexOf(b));
    return ps;
  }
  function drawList(){
    root.querySelectorAll('.pr-mode button').forEach(b => b.setAttribute('aria-pressed', b.dataset.mode === mode));
    const groups = [];
    if (mode === 'set'){
      BANK.sets.forEach(s => groups.push([s.title, BANK.problems.filter(p => p.set === s.id)]));
    } else {
      [1, 2, 3].forEach(t => groups.push([TYPE_NAME[t], BANK.problems.filter(p => p.type === t)]));
    }
    q('#prList').innerHTML = groups.map(([t, ps]) => {
      const done = ps.filter(p => (status(p) || {}).done).length;
      return `<div class="pr-grp"><div class="pr-gt">${esc(t)}<span>${done}/${ps.length}</span></div>` +
        ps.map(p => {
          const s = status(p);
          const dot = s ? (s.done ? 'ok' : 'try') : '';
          const label = mode === 'set' ? `${esc(p.no)} ${esc(p.title)}` : `${esc((BANK.sets.find(x => x.id === p.set) || {}).title || '')} · ${esc(p.no)} ${esc(p.title)}`;
          return `<button class="pr-item${cur === p ? ' on' : ''}" data-id="${esc(p.id)}"><i class="pr-dot ${dot}"></i><span>${label}</span></button>`;
        }).join('') + '</div>';
    }).join('');
  }

  async function open(p){
    cur = p; st.set('last', p.id);
    drawList();
    const setT = (BANK.sets.find(s => s.id === p.set) || {}).title || '';
    q('#prWhere').textContent = `${setT} · ${p.no} · ${TYPE_NAME[p.type]}${p.points ? ' · ' + p.points + '점' : ''}`;
    q('#prTitle').textContent = p.title;
    q('#prStmt').innerHTML = md(p.statement);
    q('#prEditor').value = st.get('c:' + p.id, null) ?? (p.starter || '');
    q('#prOut').textContent = '';
    q('#prSol').hidden = true; q('#prSolBtn').setAttribute('aria-expanded', 'false'); q('#prSolBtn').textContent = '풀이 보기';
    q('#prSol').innerHTML = (p.solution ? fmt('```python\n' + p.solution.replace(/\n$/, '') + '\n```') : '') + md(p.explain);
    drawAnswer();
    const list = order(), i = list.indexOf(p);
    q('#prPrev').disabled = i <= 0; q('#prNext').disabled = i >= list.length - 1;
    q('#prFiles').innerHTML = (p.files || []).map(f => `<details class="pr-file" data-f="${esc(f)}"><summary><code>data/${esc(base(f))}</code> <span class="pr-meta">불러오는 중</span> <a href="${esc(ctx.base + practiceDir() + f)}" download>내려받기</a></summary><div class="pr-prev"></div></details>`).join('');
    await loadFiles(p);
    sendFiles();
  }
  const practiceDir = () => ctx.section.practice.replace(/[^/]*$/, '');
  async function loadFiles(p){
    for (const f of p.files || []){
      if (FILES[f] === undefined) FILES[f] = await getText(ctx.base + practiceDir() + f);
      const lines = FILES[f].replace(/\n$/, '').split('\n');
      const box = root.querySelector(`.pr-file[data-f="${CSS.escape(f)}"]`);
      if (!box) continue;
      const head = lines[0].split(',');
      box.querySelector('.pr-meta').textContent = `${lines.length - 1}행 × ${head.length}열`;
      box.querySelector('.pr-prev').innerHTML = '<div class="pr-tbl"><table><thead><tr>' + head.map(c => `<th>${esc(c)}</th>`).join('') + '</tr></thead><tbody>' +
        lines.slice(1, 6).map(l => '<tr>' + l.split(',').map(c => `<td>${esc(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>';
    }
  }
  function sendFiles(){
    if (!ready || !cur || filesSent === cur.id) return;
    filesSent = cur.id;
    worker.postMessage({ type: 'files', files: (cur.files || []).map(f => ({ name: base(f), text: FILES[f] })) });
  }

  // ── 답안
  function drawAnswer(){
    const p = cur, box = q('#prAnswer'), saved = st.get('a:' + p.id, {});
    if (p.type === 2){
      const [mname, higher] = METRIC[p.metric] || [p.metric, true];
      const r = p.reference || {};
      box.innerHTML = `<div class="pr-sub">답안 제출</div>
<p class="pr-rule">예측 결과를 <code>${esc(p.submit.file)}</code>로 저장하는 코드를 제출합니다. 칼럼은 <code>${esc(p.submit.column)}</code> 하나, 행은 ${p.submit.rows}개, <code>index=False</code>. 평가지표는 ${esc(mname)}(${higher ? '높을수록' : '낮을수록'} 좋음)입니다.</p>
<div class="pr-tools"><button class="btn quiz" id="prSubmit">제출하고 채점</button></div>
<div class="pr-result" id="prResult">${saved.msg ? saved.msg : ''}</div>
${r.baseline !== undefined ? `<p class="pr-rule">참고: 범주형만 인코딩하고 기본 RandomForest를 쓴 점수 ${fmtScore(r.baseline)} · 풀이 코드 점수 ${fmtScore(r.solution)} (시험 환경 기준. 브라우저에서는 소수 둘째·셋째 자리가 조금 다를 수 있습니다)</p>` : ''}`;
      q('#prSubmit').addEventListener('click', submit2);
      return;
    }
    box.innerHTML = `<div class="pr-sub">답안 입력</div>` + p.answers.map((a, i) =>
      `<label class="pr-ans"><span class="pr-al">${esc(a.label || '답')}</span><input data-i="${i}" value="${esc(saved['v' + i] || '')}" autocomplete="off" placeholder="${esc(a.format || '')}"><span class="pr-mark" id="prMark${i}"></span></label>
       <div class="pr-fmt">${esc(a.format || '')}</div>`).join('') +
      `<div class="pr-tools"><button class="btn quiz" id="prCheck">채점</button></div>`;
    box.querySelectorAll('input').forEach(inp => inp.addEventListener('input', () => {
      const s = st.get('a:' + p.id, {}); s['v' + inp.dataset.i] = inp.value; st.set('a:' + p.id, s);
    }));
    q('#prCheck').addEventListener('click', check13);
  }
  const fmtScore = v => v === undefined || v === null ? '-' : (Math.abs(v) >= 100 ? v.toFixed(1) : v.toFixed(4));
  function check13(){
    const p = cur; let all = true;
    p.answers.forEach((a, i) => {
      const got = q(`input[data-i="${i}"]`).value.trim(), want = String(a.value).trim(), mk = q('#prMark' + i);
      let cls = 'bad', txt = '오답';
      // 숫자는 값으로 견준다(0.120과 0.12는 같다). 문자 답(예: 채택/기각)은 그대로 견준다
      if (got === want || (got !== '' && want !== '' && !isNaN(+got) && !isNaN(+want) && +got === +want)){ cls = 'ok'; txt = '정답'; }
      if (cls !== 'ok') all = false;
      mk.className = 'pr-mark ' + cls; mk.textContent = txt;
    });
    st.set('s:' + p.id, { done: all });
    drawList();
  }
  function submit2(){
    if (!ready || running) return;
    after = 'grade';
    run();
  }
  async function grade(){
    const p = cur;
    q('#prResult').textContent = '채점 중 …';
    const truth = await getText(ctx.base + practiceDir() + p.truth);
    worker.postMessage({ type: 'grade', spec: Object.assign({ metric: p.metric, pos_label: p.pos_label }, p.submit), truth });
  }
  function graded(res){
    const p = cur, [mname, higher] = METRIC[p.metric] || [p.metric, true];
    let html;
    if (!res.ok) html = `<span class="pr-mark bad">채점 안 됨</span> ${esc(res.msg || '')}`;
    else {
      const r = p.reference || {};
      const beatBase = r.baseline === undefined || (higher ? res.score >= r.baseline : res.score <= r.baseline);
      html = `<span class="pr-mark ${beatBase ? 'ok' : 'warn'}">${esc(mname)} ${fmtScore(res.score)}</span> ` +
        (beatBase ? '형식이 맞고 기본 모델 점수 이상입니다.' : '형식은 맞습니다. 기본 모델 점수보다 낮습니다.');
    }
    q('#prResult').innerHTML = html;
    const prev = status(p) || {};
    const done = !!res.ok;
    st.set('s:' + p.id, { done: done || prev.done, score: res.ok ? res.score : prev.score });
    st.set('a:' + p.id, { msg: html });
    drawList();
  }

  // ── 파이썬 워커
  function setStatus(s, cls){ const el = q('#prStatus'); el.textContent = s; el.className = 'pr-status' + (cls ? ' ' + cls : ''); }
  function append(s, cls){ const sp = document.createElement('span'); if (cls) sp.className = cls; sp.textContent = s; q('#prOut').appendChild(sp); }
  function makeWorker(){
    ready = false; filesSent = null; q('#prRun').disabled = true;
    worker = new Worker('../assets/py-worker.js?v=4');
    worker.onmessage = e => {
      const m = e.data;
      if (m.type === 'status') setStatus(m.s + ' …');
      else if (m.type === 'ready'){ ready = true; q('#prRun').disabled = false; setStatus('준비됨 · ' + m.s, 'ok'); sendFiles(); }
      else if (m.type === 'fatal') setStatus('파이썬을 불러오지 못했습니다. 네트워크를 확인하고 새로고침해 주세요. (' + m.s + ')', 'bad');
      else if (m.type === 'out') append(m.s + '\n');
      else if (m.type === 'err') append(m.s + '\n', 'warn');
      else if (m.type === 'error'){ finish(); after = null; append(m.s + '\n', 'error'); setStatus('오류로 멈췄습니다', 'bad'); if (cur && cur.type === 2) q('#prResult').innerHTML = '<span class="pr-mark bad">채점 안 됨</span> 코드에서 오류가 났습니다.'; }
      else if (m.type === 'done'){ finish(); setStatus('실행을 마쳤습니다', 'ok'); if (after === 'grade'){ after = null; grade(); } }
      else if (m.type === 'graded') graded(m.res);
    };
    worker.onerror = e => setStatus('파이썬 워커 오류: ' + (e.message || e), 'bad');
  }
  function run(){
    if (!ready || running || !cur) return;
    sendFiles();
    running = true;
    q('#prOut').textContent = '';
    q('#prRun').disabled = true; q('#prStop').hidden = false;
    setStatus('실행 중 …');
    worker.postMessage({ type: 'run', code: q('#prEditor').value, clean: cur.submit ? cur.submit.file : 'result.csv' });
    timer = setTimeout(() => stop(`${RUN_LIMIT}초가 넘어 멈췄습니다 (시험도 한 번 실행은 1분까지입니다)`), RUN_LIMIT * 1000);
    if (!status(cur)) { st.set('s:' + cur.id, { done: false }); drawList(); }
  }
  function finish(){ running = false; clearTimeout(timer); q('#prRun').disabled = !ready; q('#prStop').hidden = true; }
  function stop(why){
    if (!running) return;
    worker.terminate(); finish(); after = null;
    append('\n' + (why || '멈췄습니다') + '\n', 'error');
    makeWorker(); setStatus('파이썬을 다시 불러오는 중 …');
  }

  function bind(){
    root.querySelectorAll('.pr-mode button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; st.set('mode', mode); drawList(); }));
    q('#prList').addEventListener('click', e => {
      const b = e.target.closest('.pr-item'); if (!b) return;
      const p = BANK.problems.find(x => x.id === b.dataset.id);
      if (p){ open(p); q('.pr-main').scrollIntoView({ block: 'start' }); }
    });
    q('#prRun').addEventListener('click', run);
    q('#prStop').addEventListener('click', () => stop());
    q('#prReset').addEventListener('click', () => { q('#prEditor').value = cur.starter || ''; st.set('c:' + cur.id, undefined); });
    q('#prSolBtn').addEventListener('click', () => {
      const open = q('#prSol').hidden;
      q('#prSol').hidden = !open; q('#prSolBtn').setAttribute('aria-expanded', open); q('#prSolBtn').textContent = open ? '풀이 가리기' : '풀이 보기';
    });
    const go = d => { const l = order(), i = l.indexOf(cur) + d; if (l[i]){ open(l[i]); window.scrollTo(0, 0); } };
    q('#prPrev').addEventListener('click', () => go(-1));
    q('#prNext').addEventListener('click', () => go(1));
    let saveT = null;
    q('#prEditor').addEventListener('input', () => {
      clearTimeout(saveT);
      saveT = setTimeout(() => { const v = q('#prEditor').value; st.set('c:' + cur.id, v === (cur.starter || '') ? undefined : v); }, 300);
    });
    q('#prEditor').addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter'){ e.preventDefault(); run(); return; }
      if (e.key === 'Tab' && !e.shiftKey && !e.metaKey && !e.ctrlKey && !e.altKey){
        e.preventDefault();
        const t = e.target; t.setRangeText('    ', t.selectionStart, t.selectionEnd, 'end');
        t.dispatchEvent(new Event('input'));
      }
    });
  }

  async function mount(el, c){
    root = el; ctx = c;
    if (!document.querySelector('link[data-practice-css]')){
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '../assets/practice.css?v=4'; l.dataset.practiceCss = '';
      document.head.appendChild(l);
    }
    mode = st.get('mode', 'set');
    skeleton(); bind();
    BANK = JSON.parse(await getText(ctx.base + ctx.section.practice));
    if (!BANK.problems.length){ q('.pr-main').innerHTML = '<p class="empty">실습 문제를 준비 중입니다.</p>'; drawList(); return; }
    makeWorker();
    const last = BANK.problems.find(p => p.id === st.get('last', null)) || BANK.problems[0];
    await open(last);
  }
  return { mount };
})();
