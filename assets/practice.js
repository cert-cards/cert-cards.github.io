// 실습 탭 (deck.json sections[].practice가 가리키는 문제 목록을 푼다)
// 문제 목록 JSON:
//   sets:     [{ id, title }]
//   problems: [{ id, set, type: 1|2|3, no, title, points, statement(Markdown), files: ['<set>/<파일>.csv'],
//                starter, answers: [{ label, format, value }],          ← 작업형 1·3: 답 칸
//                submit: { file, column, rows }, metric, truth, reference: { baseline, solution }, ← 작업형 2: CSV 채점
//                solution, explain }]
// 화면: 넓으면 문제(왼쪽) | 코드·결과·답안(오른쪽), 좁으면 위아래. 문제 목록은 「문제 목록」 버튼 바로 아래에 펼치는 판.
// 시험 모드: 한 세트를 180분 안에 풀고 끝낼 때 한꺼번에 채점한다(그전에는 정답·풀이를 가린다).
// 내 코드·답·채점 결과·시험 기록은 이 브라우저(localStorage)에만 남는다.
window.Practice = (() => {
  const RUN_LIMIT = 60;          // 초. 시험도 한 번 실행은 1분까지다
  const EXAM_MIN = 180;          // 분. 실기 시험 시간
  const PASS = 60;
  const TYPE_NAME = { 1: '작업형 1', 2: '작업형 2', 3: '작업형 3' };
  const METRIC = {
    rmse: ['RMSE', false], rmsle: ['RMSLE', false], mae: ['MAE', false], r2: ['R²', true], accuracy: ['Accuracy', true],
    f1: ['F1', true], f1_macro: ['macro F1', true], roc_auc: ['ROC-AUC', true]
  };
  let root, ctx, BANK = { sets: [], problems: [] }, cur = null, mode = 'set', exam = null, clock = null;
  let worker = null, ready = false, running = false, timer = null, filesSent = null, after = null;
  const FILES = {};      // 파일 경로 → 내용(텍스트)

  const key = k => `cert-cards:${ctx.deck}:practice:${k}`;
  const st = {
    get(k, d){ try{ const v = localStorage.getItem(key(k)); return v === null ? d : JSON.parse(v); }catch(e){ return d; } },
    set(k, v){ try{ v === undefined ? localStorage.removeItem(key(k)) : localStorage.setItem(key(k), JSON.stringify(v)); }catch(e){} }
  };
  const q = s => root.querySelector(s);
  const setOf = p => BANK.sets.find(s => s.id === p.set) || {};
  const inExam = () => !!(exam && !exam.done);

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
  const fmtScore = v => v === undefined || v === null ? '-' : (Math.abs(v) >= 100 ? v.toFixed(1) : v.toFixed(4));
  const sameAns = (got, want) => got === want || (got !== '' && want !== '' && !isNaN(+got) && !isNaN(+want) && +got === +want);

  // ── 화면 뼈대
  function skeleton(){
    root.innerHTML = `
<div class="pr">
  <div class="pr-bar">
    <button class="btn" id="prListBtn" aria-expanded="false">☰ 문제 목록</button>
    <span class="pr-where" id="prWhere"></span>
    <span class="pr-exam" id="prExam" hidden><span class="pr-clock" id="prClock"></span><button class="btn" id="prExamEnd">시험 끝내기</button></span>
    <span class="pr-step"><button class="btn" id="prPrev" aria-label="이전 문제">←</button><button class="btn" id="prNext" aria-label="다음 문제">→</button></span>
    <div class="pr-scrim" id="prScrim" hidden></div>
    <aside class="pr-drawer" id="prDrawer" hidden aria-label="문제 목록">
      <div class="pr-drawer-head">
        <div class="seg pr-mode" role="group" aria-label="목록 묶음"><button data-mode="set">모의고사</button><button data-mode="type">유형별</button></div>
        <button class="icon-btn" id="prDrawerClose" aria-label="목록 닫기">✕</button>
      </div>
      <nav class="pr-list" id="prList"></nav>
    </aside>
  </div>
  <div class="pr-report" id="prReport" hidden></div>
  <div class="pr-split">
    <section class="pr-left">
      <h2 class="pr-title" id="prTitle"></h2>
      <div class="pr-stmt" id="prStmt"></div>
      <div class="pr-files" id="prFiles"></div>
    </section>
    <section class="pr-right">
      <div class="pr-ide">
        <div class="pr-ide-head"><span class="pr-ide-title">코드 작성</span><span class="pr-ide-meta">Python 3 · 데이터는 <code>data/</code> 폴더</span></div>
        <div class="pr-ide-body">
          <pre class="pr-gutter" id="prGutter" aria-hidden="true">1</pre>
          <textarea id="prEditor" class="pr-editor" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" aria-label="코드 편집기"></textarea>
        </div>
        <div class="pr-ide-bar">
          <button class="btn run" id="prRun" disabled>▶ 실행</button>
          <button class="btn stop" id="prStop" hidden>■ 정지</button>
          <button class="btn ghost" id="prReset">처음 코드로</button>
          <span class="pr-hint">⌘/Ctrl + Enter로 실행 · 한 번 실행은 60초까지</span>
        </div>
      </div>
      <div class="pr-console">
        <div class="pr-console-head"><span>실행 결과</span><span class="pr-status" id="prStatus">파이썬 준비 중 · 처음 한 번은 수십 MB를 받습니다</span></div>
        <pre class="pr-out" id="prOut" aria-live="polite"></pre>
      </div>
      <div class="pr-answer" id="prAnswer"></div>
      <div class="pr-sol-row"><button class="btn" id="prSolBtn" aria-expanded="false">풀이 보기</button></div>
      <div class="pr-sol" id="prSol" hidden></div>
      <p class="pr-foot">브라우저 안에서 도는 파이썬(Pyodide 0.26.4: pandas 2.2.0 · numpy 1.26.4 · scipy 1.12.0 · scikit-learn 1.4.2 · statsmodels 0.14.2)입니다. 시험 환경과 버전이 조금 다를 수 있습니다. 문제와 데이터는 기출 유형을 따라 새로 만든 것입니다.</p>
    </section>
  </div>
</div>`;
  }

  // ── 문제 목록 (서랍)
  function order(){
    let ps = BANK.problems.slice();
    if (inExam()) return ps.filter(p => p.set === exam.set);
    if (mode === 'type') ps.sort((a, b) => a.type - b.type || BANK.problems.indexOf(a) - BANK.problems.indexOf(b));
    return ps;
  }
  function drawList(){
    root.querySelectorAll('.pr-mode button').forEach(b => { b.setAttribute('aria-pressed', b.dataset.mode === mode); b.disabled = inExam(); });
    const groups = [];
    if (inExam()) groups.push([setOf({ set: exam.set }).title + ' · 시험 중', BANK.problems.filter(p => p.set === exam.set), null]);
    else if (mode === 'set') BANK.sets.forEach(s => groups.push([s.title, BANK.problems.filter(p => p.set === s.id), s.id]));
    else [1, 2, 3].forEach(t => groups.push([TYPE_NAME[t], BANK.problems.filter(p => p.type === t), null]));
    const hist = st.get('examHist', {});
    q('#prList').innerHTML = groups.map(([t, ps, setId]) => {
      const done = ps.filter(p => (status(p) || {}).done).length;
      const last = setId && hist[setId] ? `<span class="pr-last">최근 시험 ${hist[setId].total}점</span>` : '';
      const head = `<div class="pr-gt"><span>${esc(t)}</span>${inExam() ? '' : `<span>${done}/${ps.length}</span>`}</div>` +
        (setId ? `<div class="pr-gx"><button class="btn pr-start" data-set="${esc(setId)}">시험 모드로 풀기 (180분)</button>${last}</div>` : '');
      return `<div class="pr-grp">${head}` + ps.map(p => {
        const s = inExam() ? null : status(p);
        const dot = inExam() ? ((exam.ans[p.id] || exam.sub[p.id]) ? 'try' : '') : (s ? (s.done ? 'ok' : 'try') : '');
        const label = mode === 'type' && !inExam() ? `${esc(setOf(p).title || '')} · ${esc(p.no)} ${esc(p.title)}` : `${esc(p.no)} ${esc(p.title)}`;
        return `<button class="pr-item${cur === p ? ' on' : ''}" data-id="${esc(p.id)}"><i class="pr-dot ${dot}"></i><span>${label}</span></button>`;
      }).join('') + '</div>';
    }).join('');
  }
  function drawer(open){
    q('#prDrawer').hidden = !open; q('#prScrim').hidden = !open;
    q('#prListBtn').setAttribute('aria-expanded', open);
    if (open){ drawList(); const on = q('.pr-item.on'); if (on) on.scrollIntoView({ block: 'center' }); }
  }

  // ── 문제 열기
  async function open(p){
    cur = p; st.set('last', p.id);
    drawList();
    q('#prWhere').textContent = `${setOf(p).title || ''} · ${p.no} · ${TYPE_NAME[p.type]}${p.points ? ' · ' + p.points + '점' : ''}`;
    q('#prTitle').textContent = p.title;
    q('#prStmt').innerHTML = md(p.statement);
    q('#prEditor').value = st.get('c:' + p.id, null) ?? (p.starter || '');
    gutter();
    q('#prOut').textContent = '';
    q('#prSol').hidden = true; q('#prSolBtn').setAttribute('aria-expanded', 'false'); q('#prSolBtn').textContent = '풀이 보기';
    q('#prSol').innerHTML = (p.solution ? fmt('```python\n' + p.solution.replace(/\n$/, '') + '\n```') : '') + md(p.explain);
    q('.pr-sol-row').hidden = inExam();
    drawAnswer();
    const list = order(), i = list.indexOf(p);
    q('#prPrev').disabled = i <= 0; q('#prNext').disabled = i >= list.length - 1;
    q('#prFiles').innerHTML = (p.files || []).map((f, k) =>
      `<details class="pr-file" data-f="${esc(f)}"${k === 0 ? ' open' : ''}><summary><code>data/${esc(base(f))}</code> <span class="pr-meta">불러오는 중</span> <a href="${esc(ctx.base + practiceDir() + f)}" download>내려받기</a></summary><div class="pr-prev"></div></details>`).join('');
    await loadFiles(p);
    sendFiles();
  }
  const practiceDir = () => ctx.section.practice.replace(/[^/]*$/, '');

  // 데이터 미리보기: 앞 5행 + 칼럼마다 타입(숫자/문자)과 결측 개수
  function profile(text){
    const lines = text.replace(/\n$/, '').split('\n');
    const head = lines[0].split(','), rows = lines.slice(1).map(l => l.split(','));
    const cols = head.map((h, j) => {
      let miss = 0, num = 0, seen = 0;
      for (const r of rows){
        const v = (r[j] ?? '').trim();
        if (v === '' || v === 'NA' || v === 'NaN') { miss++; continue; }
        seen++; if (!isNaN(+v)) num++;
      }
      return { name: h, type: seen && num === seen ? '숫자' : '문자', miss };
    });
    return { n: rows.length, cols, top: rows.slice(0, 5) };
  }
  async function loadFiles(p){
    for (const f of p.files || []){
      if (FILES[f] === undefined) FILES[f] = await getText(ctx.base + practiceDir() + f);
      const box = root.querySelector(`.pr-file[data-f="${CSS.escape(f)}"]`);
      if (!box) continue;
      const pf = profile(FILES[f]);
      const missCols = pf.cols.filter(c => c.miss).length;
      box.querySelector('.pr-meta').textContent = `${pf.n}행 × ${pf.cols.length}열` + (missCols ? ` · 결측 있는 칼럼 ${missCols}개` : ' · 결측 없음');
      box.querySelector('.pr-prev').innerHTML = '<div class="pr-tbl"><table><thead><tr>' + pf.cols.map(c => `<th>${esc(c.name)}</th>`).join('') + '</tr>' +
        '<tr class="pr-colinfo">' + pf.cols.map(c => `<th>${c.type}${c.miss ? ` · <b>결측 ${c.miss}</b>` : ''}</th>`).join('') + '</tr></thead><tbody>' +
        pf.top.map(r => '<tr>' + pf.cols.map((_, j) => `<td>${esc(r[j] ?? '')}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>';
    }
  }
  function sendFiles(){
    if (!ready || !cur || filesSent === cur.id) return;
    filesSent = cur.id;
    worker.postMessage({ type: 'files', files: (cur.files || []).map(f => ({ name: base(f), text: FILES[f] })) });
  }

  // ── 답안
  function drawAnswer(){
    const p = cur, box = q('#prAnswer');
    if (p.type === 2){
      const [mname, higher] = METRIC[p.metric] || [p.metric, true];
      const r = p.reference || {};
      const saved = inExam() ? (exam.sub[p.id] ? { msg: subMsg(exam.sub[p.id]) } : {}) : st.get('a:' + p.id, {});
      box.innerHTML = `<div class="pr-ans-head">답안 제출 <span>${inExam() ? '시험 중 · 점수는 끝낼 때 공개' : '작업형 2 · result.csv로 채점'}</span></div>
<p class="pr-rule">예측 결과를 <code>${esc(p.submit.file)}</code>로 저장하는 코드를 제출합니다. 칼럼은 <code>${esc(p.submit.column)}</code> 하나, 행은 ${p.submit.rows}개, <code>index=False</code>. 평가지표는 ${esc(mname)}(${higher ? '높을수록' : '낮을수록'} 좋음)입니다.</p>
<div class="pr-tools"><button class="btn run" id="prSubmit">${inExam() ? '제출' : '제출하고 채점'}</button></div>
<div class="pr-result" id="prResult">${saved.msg || ''}</div>
${!inExam() && r.baseline !== undefined ? `<p class="pr-rule">참고: 범주형만 인코딩하고 기본 RandomForest를 쓴 점수 ${fmtScore(r.baseline)} · 풀이 코드 점수 ${fmtScore(r.solution)} (시험 환경 기준. 브라우저에서는 소수 둘째·셋째 자리가 조금 다를 수 있습니다)</p>` : ''}`;
      q('#prSubmit').addEventListener('click', submit2);
      return;
    }
    const saved = inExam() ? (exam.ans[p.id] || []) : (() => { const s = st.get('a:' + p.id, {}); return p.answers.map((_, i) => s['v' + i] || ''); })();
    box.innerHTML = `<div class="pr-ans-head">답안 입력 <span>${inExam() ? '시험 중 · 입력하면 저장되고 끝낼 때 채점' : '값을 넣고 채점'}</span></div>` + p.answers.map((a, i) =>
      `<label class="pr-ans"><span class="pr-al">${esc(a.label || '답')}</span><input data-i="${i}" value="${esc(saved[i] || '')}" autocomplete="off" placeholder="${esc(a.format || '')}"><span class="pr-mark" id="prMark${i}"></span></label>`).join('') +
      `<div class="pr-tools"><button class="btn run" id="prCheck">${inExam() ? '답 저장' : '채점'}</button><span class="pr-saved" id="prSaved"></span></div>`;
    box.querySelectorAll('input').forEach(inp => inp.addEventListener('input', () => {
      if (inExam()){ (exam.ans[p.id] = exam.ans[p.id] || p.answers.map(() => ''))[+inp.dataset.i] = inp.value.trim(); saveExam(); return; }
      const s = st.get('a:' + p.id, {}); s['v' + inp.dataset.i] = inp.value; st.set('a:' + p.id, s);
    }));
    q('#prCheck').addEventListener('click', () => inExam() ? saveExamAnswer() : check13());
  }
  function check13(){
    const p = cur; let all = true;
    p.answers.forEach((a, i) => {
      const got = q(`input[data-i="${i}"]`).value.trim(), want = String(a.value).trim(), mk = q('#prMark' + i);
      // 숫자는 값으로 견준다(0.120과 0.12는 같다). 문자 답(예: 채택/기각)은 그대로 견준다
      const ok = sameAns(got, want);
      if (!ok) all = false;
      mk.className = 'pr-mark ' + (ok ? 'ok' : 'bad'); mk.textContent = ok ? '정답' : '오답';
    });
    st.set('s:' + p.id, { done: all });
    drawList();
  }
  function saveExamAnswer(){
    exam.ans[cur.id] = cur.answers.map((_, i) => q(`input[data-i="${i}"]`).value.trim());
    saveExam();
    q('#prSaved').textContent = '저장했습니다 · ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    drawList();
  }
  function submit2(){
    if (!ready || running) return;
    after = 'grade';
    run();
  }
  async function grade(){
    const p = cur;
    q('#prResult').textContent = inExam() ? '제출 중 …' : '채점 중 …';
    const truth = await getText(ctx.base + practiceDir() + p.truth);
    worker.postMessage({ type: 'grade', spec: Object.assign({ metric: p.metric, pos_label: p.pos_label }, p.submit), truth });
  }
  const subMsg = r => r.ok ? '<span class="pr-mark ok">제출됨</span> 형식이 맞습니다. 점수는 시험을 끝낼 때 공개합니다.' : `<span class="pr-mark bad">형식 오류</span> ${esc(r.msg || '')}`;
  function graded(res){
    const p = cur, [mname, higher] = METRIC[p.metric] || [p.metric, true];
    if (inExam()){
      exam.sub[p.id] = res; saveExam();
      q('#prResult').innerHTML = subMsg(res) + ' · ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
      drawList(); return;
    }
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
    st.set('s:' + p.id, { done: !!res.ok || prev.done, score: res.ok ? res.score : prev.score });
    st.set('a:' + p.id, { msg: html });
    drawList();
  }

  // ── 시험 모드
  function saveExam(){ st.set('exam', exam); }
  function startExam(setId){
    const s = BANK.sets.find(x => x.id === setId);
    if (!confirm(`${s.title}를 시험 모드로 시작할까요?\n\n${EXAM_MIN}분 타이머가 돌고, 끝낼 때까지 정답 확인과 풀이 보기는 가려집니다. 작업형 1·3은 「답 저장」, 작업형 2는 「제출」로 답을 냅니다.`)) return;
    exam = { set: setId, start: Date.now(), ans: {}, sub: {}, done: false };
    saveExam();
    drawer(false);
    q('#prReport').hidden = true;
    examUI();
    open(BANK.problems.find(p => p.set === setId));
  }
  function examUI(){
    q('#prExam').hidden = !inExam();
    clearInterval(clock);
    if (!inExam()) return;
    const tick = () => {
      const left = exam.start + EXAM_MIN * 60000 - Date.now();
      if (left <= 0){ endExam(true); return; }
      const s = Math.floor(left / 1000), hh = Math.floor(s / 3600), mm = Math.floor(s / 60) % 60, ss = s % 60;
      q('#prClock').textContent = `남은 시간 ${hh}:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
      q('#prClock').classList.toggle('low', left < 10 * 60000);
    };
    tick(); clock = setInterval(tick, 1000);
  }
  // 작업형2 점수(추정): 형식 오류·미제출 0, 기본 모델보다 낮으면 20, 기본~풀이 사이 30~40, 풀이 이상 40
  function score2(p, r){
    if (!r || !r.ok) return 0;
    const [, higher] = METRIC[p.metric] || [p.metric, true];
    const b = p.reference.baseline, s = p.reference.solution;
    const t = higher ? (r.score - b) / (s - b) : (b - r.score) / (b - s);
    if (t < 0) return 20;
    return Math.min(40, Math.round(30 + 10 * t));
  }
  function endExam(timeUp){
    if (!inExam()) return;
    if (!timeUp && !confirm('시험을 끝내고 채점할까요?')) return;
    const rows = BANK.problems.filter(p => p.set === exam.set).map(p => {
      if (p.type === 2){
        const r = exam.sub[p.id], pts = score2(p, r);
        const [mname] = METRIC[p.metric] || [p.metric];
        return { p, pts, mine: r ? (r.ok ? `${mname} ${fmtScore(r.score)}` : '형식 오류') : '미제출', want: `기본 ${fmtScore(p.reference.baseline)} · 풀이 ${fmtScore(p.reference.solution)}` };
      }
      const got = exam.ans[p.id] || [], k = p.answers.length;
      const right = p.answers.filter((a, i) => sameAns((got[i] || '').trim(), String(a.value).trim())).length;
      return { p, pts: Math.round(p.points * right / k * 10) / 10, mine: p.answers.map((a, i) => (a.label ? a.label + ' ' : '') + (got[i] || '·')).join('  '), want: p.answers.map(a => (a.label ? a.label + ' ' : '') + a.value).join('  ') };
    });
    const total = Math.round(rows.reduce((n, r) => n + r.pts, 0) * 10) / 10;
    const used = Math.min(EXAM_MIN, Math.round((Date.now() - exam.start) / 60000));
    exam.done = true; exam.total = total; saveExam();
    const hist = st.get('examHist', {}); hist[exam.set] = { total, date: new Date().toISOString().slice(0, 10) }; st.set('examHist', hist);
    rows.forEach(r => { if (r.p.type !== 2 && r.pts === r.p.points) st.set('s:' + r.p.id, { done: true }); });
    examUI();
    const s = setOf({ set: exam.set });
    q('#prReport').innerHTML = `<div class="pr-rep-head"><div><div class="pr-rep-t">${esc(s.title)} 결과${timeUp ? ' · 시간 종료' : ''}</div>
<div class="pr-rep-score ${total >= PASS ? 'ok' : 'bad'}">${total}점 <span>${total >= PASS ? '합격선(60점) 이상' : '합격선(60점) 미만'} · ${used}분 사용</span></div></div>
<button class="btn" id="prRepClose">닫기</button></div>
<div class="pr-tbl"><table><thead><tr><th>문항</th><th>배점</th><th>득점</th><th>내 답</th><th>정답</th></tr></thead><tbody>` +
      rows.map(r => `<tr><td><button class="pr-replink" data-id="${esc(r.p.id)}">${esc(r.p.no)} ${esc(r.p.title)}</button></td><td>${r.p.points}</td><td><b>${r.pts}</b></td><td>${esc(r.mine)}</td><td>${esc(r.want)}</td></tr>`).join('') +
      `</tbody></table></div><p class="pr-rule">작업형 1·3은 소문항 수로 배점을 나눴습니다. 작업형 2는 실제 채점 구간이 공개되지 않아 기본 모델·풀이 점수로 나눈 추정치입니다(형식 오류 0점, 기본 모델 미만 20점, 기본~풀이 30~40점). 이제 풀이를 볼 수 있습니다.</p>`;
    q('#prReport').hidden = false;
    q('#prRepClose').addEventListener('click', () => { q('#prReport').hidden = true; });
    q('#prReport').querySelectorAll('.pr-replink').forEach(b => b.addEventListener('click', () => { open(BANK.problems.find(p => p.id === b.dataset.id)); q('.pr-split').scrollIntoView({ block: 'start' }); }));
    q('#prReport').scrollIntoView({ block: 'start' });
    if (cur) open(cur);
  }

  // ── 파이썬 워커
  function setStatus(s, cls){ const el = q('#prStatus'); el.textContent = s; el.className = 'pr-status' + (cls ? ' ' + cls : ''); }
  function append(s, cls){ const sp = document.createElement('span'); if (cls) sp.className = cls; sp.textContent = s; q('#prOut').appendChild(sp); }
  function makeWorker(){
    ready = false; filesSent = null; q('#prRun').disabled = true;
    worker = new Worker('../assets/py-worker.js?v=6');
    worker.onmessage = e => {
      const m = e.data;
      if (m.type === 'status') setStatus(m.s + ' …');
      else if (m.type === 'ready'){ ready = true; q('#prRun').disabled = false; setStatus('준비됨 · ' + m.s.replace(/ · numpy.*/, ''), 'ok'); sendFiles(); }
      else if (m.type === 'fatal') setStatus('파이썬을 불러오지 못했습니다. 네트워크를 확인하고 새로고침해 주세요. (' + m.s + ')', 'bad');
      else if (m.type === 'out') append(m.s + '\n');
      else if (m.type === 'err') append(m.s + '\n', 'warn');
      else if (m.type === 'error'){
        finish(); append(m.s + '\n', 'error'); setStatus('오류로 멈췄습니다', 'bad');
        if (after === 'grade'){ after = null; graded({ ok: false, msg: '코드에서 오류가 나 파일을 만들지 못했습니다.' }); }
      }
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
    if (!inExam() && !status(cur)) { st.set('s:' + cur.id, { done: false }); drawList(); }
  }
  function finish(){ running = false; clearTimeout(timer); q('#prRun').disabled = !ready; q('#prStop').hidden = true; }
  function stop(why){
    if (!running) return;
    worker.terminate(); finish(); after = null;
    append('\n' + (why || '멈췄습니다') + '\n', 'error');
    makeWorker(); setStatus('파이썬을 다시 불러오는 중 …');
  }

  // 줄 번호: 편집기의 줄 수만큼 숫자를 세우고 스크롤을 같이 움직인다
  function gutter(){
    const n = q('#prEditor').value.split('\n').length;
    const g = q('#prGutter');
    if (g._n !== n){ g._n = n; g.textContent = Array.from({ length: n }, (_, i) => i + 1).join('\n'); }
    g.scrollTop = q('#prEditor').scrollTop;
  }
  // 문제 칸이 상단 바 바로 아래에 붙도록 높이를 잰다
  function measure(){
    const bar = document.querySelector('.bar'), pb = q('.pr-bar');
    const top = (bar ? bar.getBoundingClientRect().height : 0);
    root.style.setProperty('--pr-top', top + 'px');
    root.style.setProperty('--pr-top2', (top + (pb ? pb.getBoundingClientRect().height : 0) + 12) + 'px');
  }
  function bind(){
    root.querySelectorAll('.pr-mode button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; st.set('mode', mode); drawList(); }));
    q('#prListBtn').addEventListener('click', () => drawer(q('#prDrawer').hidden));
    q('#prDrawerClose').addEventListener('click', () => drawer(false));
    q('#prScrim').addEventListener('click', () => drawer(false));
    q('#prList').addEventListener('click', e => {
      const sb = e.target.closest('.pr-start');
      if (sb){ startExam(sb.dataset.set); return; }
      const b = e.target.closest('.pr-item'); if (!b) return;
      const p = BANK.problems.find(x => x.id === b.dataset.id);
      if (p){ drawer(false); open(p); window.scrollTo(0, 0); }
    });
    q('#prExamEnd').addEventListener('click', () => endExam(false));
    q('#prRun').addEventListener('click', run);
    q('#prStop').addEventListener('click', () => stop());
    q('#prReset').addEventListener('click', () => { q('#prEditor').value = cur.starter || ''; st.set('c:' + cur.id, undefined); gutter(); });
    q('#prSolBtn').addEventListener('click', () => {
      const open = q('#prSol').hidden;
      q('#prSol').hidden = !open; q('#prSolBtn').setAttribute('aria-expanded', open); q('#prSolBtn').textContent = open ? '풀이 가리기' : '풀이 보기';
    });
    const go = d => { const l = order(), i = l.indexOf(cur) + d; if (l[i]){ open(l[i]); window.scrollTo(0, 0); } };
    q('#prPrev').addEventListener('click', () => go(-1));
    q('#prNext').addEventListener('click', () => go(1));
    let saveT = null;
    const ed = q('#prEditor'), gut = q('#prGutter');
    ed.addEventListener('input', () => {
      gutter();
      clearTimeout(saveT);
      saveT = setTimeout(() => { const v = ed.value; st.set('c:' + cur.id, v === (cur.starter || '') ? undefined : v); }, 300);
    });
    ed.addEventListener('scroll', () => { gut.scrollTop = ed.scrollTop; });
    ed.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter'){ e.preventDefault(); run(); return; }
      if (e.key === 'Tab' && !e.shiftKey && !e.metaKey && !e.ctrlKey && !e.altKey){
        e.preventDefault();
        ed.setRangeText('    ', ed.selectionStart, ed.selectionEnd, 'end');
        ed.dispatchEvent(new Event('input'));
      }
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !q('#prDrawer').hidden) drawer(false); });
    window.addEventListener('resize', measure);
  }

  async function mount(el, c){
    root = el; ctx = c;
    if (!document.querySelector('link[data-practice-css]')){
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '../assets/practice.css?v=8'; l.dataset.practiceCss = '';
      document.head.appendChild(l);
    }
    mode = st.get('mode', 'set');
    exam = st.get('exam', null);
    skeleton(); bind(); measure();
    BANK = JSON.parse(await getText(ctx.base + ctx.section.practice));
    if (!BANK.problems.length){ q('.pr-split').innerHTML = '<p class="empty">실습 문제를 준비 중입니다.</p>'; return; }
    makeWorker();
    examUI();
    let first = BANK.problems.find(p => p.id === st.get('last', null)) || BANK.problems[0];
    if (inExam() && first.set !== exam.set) first = BANK.problems.find(p => p.set === exam.set);
    await open(first);
    measure();
  }
  return { mount };
})();
