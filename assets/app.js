// 자격증 페이지는 window.CERT = { deck: '<id>' } 만 준다. Markdown 읽기와 서식(parseDeck·fmt 등)은 deck.js.
// deck.json에 sections가 있으면 위쪽에 탭(예: 필기 · 카드 | 퀴즈 / 실기 · 카드 | 실습)을 그린다.
const DECK = window.CERT.deck;
const BASE = `../data/${DECK}/`;
let DATA = [];
let INFO = {};
let SECTIONS = [];      // [{ id, label, views, files, unitLabel, practice }]
let SEC = null;         // 지금 보는 구역
let VIEW = 'cards';     // cards | quiz | practice
const TEXTS = {};       // 파일 이름 → Markdown

// 화면 뼈대 — 모든 자격증이 같다
document.body.insertAdjacentHTML('afterbegin', `
<div class="bar"><div class="bar-in">
  <div class="row top">
    <button class="icon-btn" id="tocBtn" aria-label="목차 열기">☰</button>
    <h1 id="deckTitle"></h1>
    <nav class="tabs" id="tabs" hidden aria-label="구역"></nav>
    <span class="prog" id="prog">불러오는 중</span>
    <button class="icon-btn" id="themeBtn" aria-label="다크 모드 전환" title="다크 모드 전환">◐</button>
  </div>
  <div class="row ctl" id="ctl">
    <div class="seg" role="group" aria-label="가릴 쪽">
      <button data-mode="term" aria-pressed="true">용어 가리기</button>
      <button data-mode="desc" aria-pressed="false">설명 가리기</button>
    </div>
    <button class="btn" id="flagBtn" aria-pressed="false"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" aria-hidden="true" style="vertical-align:-1px"><path d="M6 3h12v18l-6-4-6 4z"/></svg> 다시 볼 것</button>
    <button class="btn quiz" id="quizBtn">퀴즈</button>
    <button class="btn" id="allBtn">전체 펼치기</button>
    <button class="btn" id="resetBtn">다시 가리기</button>
    <input class="search" id="q" type="search" placeholder="검색 (용어·설명)" autocomplete="off">
  </div>
  <div class="pbar" id="pbar"><i id="pfill"></i></div>
</div></div>

<div class="qz" id="qz" hidden role="dialog" aria-modal="true" aria-label="퀴즈">
  <div class="qz-top">
    <button class="btn" id="qzPrev" aria-label="이전 문제">← 이전</button>
    <span class="cnt" id="qzCnt"></span>
    <button class="icon-btn" id="qzFlag" aria-label="다시 볼 것 표시" title="다시 볼 것"></button>
    <button class="btn" id="qzClose">닫기</button>
  </div>
  <div class="qz-stage"><div class="qz-card" id="qzCard" tabindex="0"></div></div>
  <div class="qz-hint" id="qzHint">한 번 누르면 정답 · 한 번 더 누르면 다음 문제</div>
</div>
<div class="scrim" id="scrim"></div>
<div class="wrap" id="cardsView">
  <nav class="toc" id="toc" aria-label="목차"></nav>
  <main id="main"></main>
</div>
<div id="practiceView" hidden></div>
<footer>카드를 누르면 정답이 보이고, 다시 누르면 가려집니다 · 책갈피 표시는 이 브라우저에만 저장됩니다<span id="deckNotes"></span><br><a href="../">다른 자격증</a> · <a href="https://github.com/cert-cards/cert-cards.github.io/issues">틀린 내용 제보</a></footer>
`);

const getTexts = files => Promise.all(files.map(f => TEXTS[f] !== undefined ? TEXTS[f] : getText(BASE + f).then(t => (TEXTS[f] = t))));
async function loadInfo(){
  INFO = JSON.parse(await getText(BASE + 'deck.json'));
  KEY = INFO.storageKey || DECK;
  mode = store.get('mode', 'term');
  flags = new Set(store.get('flags', []));
  $('#deckTitle').textContent = INFO.title;
  $('#deckNotes').innerHTML = (INFO.notes || []).map(n => '<br>' + esc(n)).join('');
  SECTIONS = INFO.sections || [{ id: '', label: '', views: ['cards'], files: INFO.files, unitLabel: INFO.unitLabel }];
}
async function loadSection(sec){
  DATA = [];
  const texts = await getTexts(sec.files || []);
  texts.forEach((md, i) => {
    parseDeck(md).forEach(g => { g.ch = (i + 1) + '. ' + g.ch; DATA.push(g); });
  });
}
const $ = s => document.querySelector(s);
const store = {
  get(k, d){ try{ const v = localStorage.getItem(KEY + ':' + k); return v === null ? d : JSON.parse(v); }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem(KEY + ':' + k, JSON.stringify(v)); }catch(e){} }
};
let KEY = DECK;          // 책갈피·모드 저장 이름 (deck.json storageKey가 있으면 그것)
let mode = 'term';
let flags = new Set();
const revealed = new Set();
let total = 0;

const flagSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"/></svg>';
const VIEW_LABEL = { cards: '카드', quiz: '퀴즈', practice: '실습' };

function build(){
  const main = $('#main'), toc = $('#toc');
  main.innerHTML = '';
  toc.innerHTML = '<div class="toc-head">목차 <button class="icon-btn" id="tocClose" aria-label="목차 닫기">✕</button></div>';
  $('#tocClose').addEventListener('click', closeToc);
  total = 0; revealed.clear();
  const prefix = SEC.id ? SEC.id + ':' : '';
  if (!DATA.length){
    main.innerHTML = `<p class="empty">${esc(SEC.label || '')} 카드는 준비 중입니다.</p>`;
    return;
  }
  let lastCh = null;
  DATA.forEach((sec, si) => {
    if (sec.ch !== lastCh){
      lastCh = sec.ch;
      const m = sec.ch.match(/^(\d+)\.\s*(.*)$/);
      const h = document.createElement('div'); h.className = 'chapter'; h.id = 'c' + si;
      h.innerHTML = `<div class="no">${esc(SEC.unitLabel || INFO.unitLabel || '과목')} ${m ? m[1].padStart(2,'0') : ''}</div><h2>${esc(m ? m[2] : sec.ch)}</h2>`;
      main.appendChild(h);
      const ta = document.createElement('a'); ta.className = 'ch'; ta.href = '#c' + si; ta.textContent = sec.ch;
      ta.addEventListener('click', jumpTo); toc.appendChild(ta);
    }
    const el = document.createElement('section');
    el.id = 's' + si;
    el.innerHTML = `<h3>${fmt(sec.t)}</h3>`;
    const g = document.createElement('div'); g.className = 'grid';
    let cnt = 0;
    sec.items.forEach((it, ii) => {
      const id = prefix + si + '-' + ii;
      if (it.k === 'T' || it.k === 'Q'){
        cnt++; total++;
        const c = document.createElement('div');
        c.className = 'card hide' + (it.k === 'Q' ? ' q' : '') + ((it.a + it.b).includes('```') ? ' wide' : '');
        c.tabIndex = 0; c.dataset.id = id; c.dataset.k = it.k;
        c.dataset.text = (it.a + ' ' + it.b + ' ' + sec.t + ' ' + sec.ch).toLowerCase();
        c.innerHTML =
          `<div class="term"><span class="part" data-p="a"></span></div>` +
          `<div class="desc"><span class="part" data-p="b"></span></div>` +
          `<button class="flagbtn" aria-label="다시 볼 것 표시" title="다시 볼 것">${flagSvg}</button>`;
        c._it = it;
        if (flags.has(id)) c.classList.add('flag');
        g.appendChild(c);
      } else if (it.k === 'N'){
        const n = document.createElement('div'); n.className = 'note'; n.innerHTML = fmt(it.a); g.appendChild(n);
      }
    });
    el.appendChild(g); main.appendChild(el);
    const a = document.createElement('a');
    a.href = '#s' + si;
    a.innerHTML = `${fmt(sec.t)}<span class="cnt">${cnt || ''}</span>`;
    a.addEventListener('click', jumpTo);
    toc.appendChild(a);
  });
  const e = document.createElement('div'); e.className = 'empty hidden'; e.id = 'empty'; e.textContent = '조건에 맞는 카드가 없습니다.';
  main.appendChild(e);
}
// 목차 링크: 주소창의 # 탭 경로를 건드리지 않고 그 자리로 스크롤만
function jumpTo(e){
  e.preventDefault();
  const t = document.getElementById(e.currentTarget.getAttribute('href').slice(1));
  if (t) t.scrollIntoView({ block: 'start' });
  closeToc();
}

// 어느 쪽을 가릴지: Q 카드는 항상 답(b), T 카드는 모드에 따라
function hiddenPart(c){ return c.dataset.k === 'Q' ? 'b' : (mode === 'term' ? 'a' : 'b'); }
function paint(c){
  const it = c._it, hp = hiddenPart(c);
  c.querySelectorAll('.part').forEach(p => {
    const key = p.dataset.p, txt = fmt(it[key]);
    if (key === hp){
      const label = c.dataset.k === 'Q' ? '정답 보기' : (key === 'a' ? '용어 보기' : '설명 보기');
      p.className = 'part ans' + (key === 'b' ? ' blk' : '');
      p.innerHTML = `<span class="real">${txt}</span><span class="mask">${label}</span>`;
    } else { p.className = 'part'; p.innerHTML = txt; }
  });
}
function paintAll(){ document.querySelectorAll('.card').forEach(paint); }

function setRevealed(c, on){
  c.classList.toggle('hide', !on);
  if (on){ revealed.add(c.dataset.id); c.classList.add('reveal-anim'); }
  else { revealed.delete(c.dataset.id); c.classList.remove('reveal-anim'); }
  updateProg();
}
function updateProg(){
  if (VIEW === 'practice'){ $('#prog').textContent = ''; return; }
  $('#prog').textContent = total ? `${revealed.size} / ${total}` : '';
  $('#pfill').style.width = (total ? revealed.size / total * 100 : 0) + '%';
}

function applyFilter(){
  const q = $('#q').value.trim().toLowerCase();
  const onlyFlag = $('#flagBtn').getAttribute('aria-pressed') === 'true';
  const filtering = q || onlyFlag;
  let any = false;
  document.querySelectorAll('#main section').forEach(sec => {
    let shown = 0;
    sec.querySelectorAll('.card').forEach(c => {
      const ok = (!q || c.dataset.text.includes(q)) && (!onlyFlag || c.classList.contains('flag'));
      c.classList.toggle('hidden', !ok); if (ok) shown++;
    });
    sec.querySelectorAll('.note').forEach(n => n.classList.toggle('hidden', !!filtering));
    sec.classList.toggle('hidden', filtering && !shown);
    if (!filtering || shown) any = true;
  });
  document.querySelectorAll('.chapter').forEach(h => {
    let n = h.nextElementSibling, vis = false;
    while (n && !n.classList.contains('chapter')){ if (n.tagName === 'SECTION' && !n.classList.contains('hidden')) vis = true; n = n.nextElementSibling; }
    h.classList.toggle('hidden', !vis);
  });
  const em = $('#empty'); if (em) em.classList.toggle('hidden', any);
}

function closeToc(){ $('#toc').classList.remove('open'); $('#scrim').classList.remove('open'); }

// ── 구역·탭 (#<구역>/<보기>)
function drawTabs(){
  const nav = $('#tabs');
  if (!INFO.sections){ nav.hidden = true; return; }
  nav.hidden = false;
  nav.innerHTML = SECTIONS.map(s => `<div class="tabgrp"><span class="tablbl">${esc(s.label)}</span><div class="seg">` +
    s.views.map(v => `<button data-sec="${esc(s.id)}" data-view="${v}" aria-pressed="${s === SEC && v === VIEW}">${VIEW_LABEL[v] || v}</button>`).join('') +
    `</div></div>`).join('');
}
function parseHash(){
  const m = location.hash.match(/^#([\w-]+)\/(cards|quiz|practice)$/);
  const sec = m && SECTIONS.find(s => s.id === m[1] && s.views.includes(m[2]));
  if (sec) return [sec, m[2]];
  const saved = store.get('tab', null);
  const s2 = saved && SECTIONS.find(s => s.id === saved[0] && s.views.includes(saved[1]) && saved[1] !== 'quiz');
  if (s2) return [s2, saved[1]];
  const first = SECTIONS.find(s => (s.files || []).length) || SECTIONS[0];
  return [first, 'cards'];
}
async function route(){
  const [sec, view] = parseHash();
  const secChanged = sec !== SEC;
  SEC = sec; VIEW = view;
  if (INFO.sections) store.set('tab', [SEC.id, VIEW]);
  drawTabs();
  const practice = VIEW === 'practice', quiz = VIEW === 'quiz' && !!INFO.sections;
  // 머리 막대(제목·진행·탭)는 어느 보기에서나 그대로 둔다. 카드용 도구 줄만 카드 보기에서 보인다
  $('#cardsView').hidden = practice || quiz; $('#practiceView').hidden = !practice;
  $('#ctl').hidden = practice || quiz; $('#pbar').hidden = practice;
  $('#tocBtn').hidden = practice || quiz;
  document.body.classList.toggle('wide', !!INFO.sections);   // 구역 탭이 있는 덱은 모든 보기를 같은 폭(1440px)으로
  $('#quizBtn').hidden = !!INFO.sections;          // 구역이 있는 덱은 퀴즈가 탭이다
  if (secChanged){
    await loadSection(SEC);
    build(); paintAll(); applyFilter();
  }
  updateProg();
  if (practice){ if (!$('#qz').hidden) qzClose(true); await openPractice(); return; }
  if (VIEW === 'quiz') qzOpen(); else if (!$('#qz').hidden) qzClose(true);
}
function setTab(secId, view){
  const h = `#${secId}/${view}`;
  if (location.hash === h) route(); else location.hash = h;
}
$('#tabs').addEventListener('click', e => {
  const b = e.target.closest('button[data-view]');
  if (b) setTab(b.dataset.sec, b.dataset.view);
});
window.addEventListener('hashchange', () => { if (INFO.sections && /^#[\w-]+\/(cards|quiz|practice)$/.test(location.hash)) route(); });

// 실습 탭: 처음 열 때만 실습 화면 코드를 불러온다 (파이썬은 그 안에서 또 따로)
let practiceLoaded = null;
function openPractice(){
  if (!practiceLoaded){
    practiceLoaded = new Promise((ok, no) => {
      const s = document.createElement('script');
      s.src = '../assets/practice.js?v=10'; s.onload = ok; s.onerror = () => no(new Error('practice.js'));
      document.head.appendChild(s);
    }).then(() => window.Practice.mount($('#practiceView'), { base: BASE, deck: DECK, info: INFO, section: SEC }));
  }
  return practiceLoaded.catch(err => { $('#practiceView').innerHTML = `<p class="empty">실습 화면을 불러오지 못했습니다. (${esc(err.message)})</p>`; });
}

$('#main').addEventListener('click', e => {
  const fb = e.target.closest('.flagbtn');
  if (fb){
    const c = fb.closest('.card'); c.classList.toggle('flag');
    c.classList.contains('flag') ? flags.add(c.dataset.id) : flags.delete(c.dataset.id);
    store.set('flags', [...flags]); e.stopPropagation(); return;
  }
  const c = e.target.closest('.card');
  if (c && !window.getSelection().toString()) setRevealed(c, c.classList.contains('hide'));
});
$('#main').addEventListener('keydown', e => {
  const c = e.target.closest('.card');
  if (c && (e.key === 'Enter' || e.key === ' ')){ e.preventDefault(); setRevealed(c, c.classList.contains('hide')); }
});
document.querySelectorAll('#ctl .seg button').forEach(b => b.addEventListener('click', () => {
  mode = b.dataset.mode; store.set('mode', mode);
  document.querySelectorAll('#ctl .seg button').forEach(x => x.setAttribute('aria-pressed', x === b));
  paintAll();
}));
const vis = () => [...document.querySelectorAll('#main .card:not(.hidden)')].filter(c => !c.closest('section.hidden'));
$('#allBtn').addEventListener('click', () => { vis().forEach(c => setRevealed(c, true)); });
$('#resetBtn').addEventListener('click', () => { document.querySelectorAll('#main .card').forEach(c => setRevealed(c, false)); });
['flagBtn'].forEach(id => $('#'+id).addEventListener('click', e => {
  const b = e.currentTarget; b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true'); applyFilter();
}));
$('#q').addEventListener('input', applyFilter);
$('#tocBtn').addEventListener('click', () => { $('#toc').classList.add('open'); $('#scrim').classList.add('open'); });
$('#scrim').addEventListener('click', closeToc);
// ── 퀴즈: 지금 화면에 보이는(필터가 걸려 있으면 걸린) 카드에서 무작위로 끝없이
// hist: 지금까지 낸 카드 순서. pos: 지금 보는 위치. 이전으로 갔다가 다음을 누르면 기록을 따라 앞으로 가고, 끝에 닿으면 새로 뽑는다.
const qz = { pool: [], deck: [], cur: null, shown: false, last: null, hist: [], pos: -1, base: 0 };
const QZ_HIST_MAX = 300;
function qzShuffle(){
  const d = qz.pool.slice();
  for (let i = d.length - 1; i > 0; i--){ const j = Math.random() * (i + 1) | 0; [d[i], d[j]] = [d[j], d[i]]; }
  if (d.length > 1 && d[d.length - 1] === qz.last) [d[0], d[d.length - 1]] = [d[d.length - 1], d[0]];
  qz.deck = d;
}
function qzNext(){
  if (qz.pos < qz.hist.length - 1){
    qz.pos++;
  } else {
    if (!qz.deck.length) qzShuffle();
    qz.last = qz.deck.pop();
    qz.hist.push(qz.last);
    if (qz.hist.length > QZ_HIST_MAX){ qz.hist.shift(); qz.base++; }
    qz.pos = qz.hist.length - 1;
  }
  qz.cur = qz.hist[qz.pos]; qz.shown = false;
  qzRender();
}
function qzPrev(){
  if (qz.pos <= 0) return;
  qz.pos--; qz.cur = qz.hist[qz.pos]; qz.shown = false;
  qzRender();
}
function qzRender(){
  const c = qz.cur, it = c._it, hp = hiddenPart(c), box = $('#qzCard');
  const sec = c.closest('section');
  let chEl = sec; while (chEl && !chEl.classList.contains('chapter')) chEl = chEl.previousElementSibling;
  const where = (chEl ? chEl.querySelector('h2').textContent + ' › ' : '') + sec.querySelector('h3').textContent;
  const label = c.dataset.k === 'Q' ? '정답 보기' : (hp === 'a' ? '용어는?' : '설명은?');
  const part = key => key === hp && !qz.shown ? `<span class="qz-hole">${label}</span>` : `<span class="${key === hp ? 'qz-ans' : ''}">${fmt(it[key])}</span>`;
  box.className = 'qz-card' + (c.dataset.k === 'Q' ? ' q' : '') + (qz.shown ? ' shown' : '');
  box.innerHTML = `<div class="qz-where">${esc(where)}</div><div class="qz-a">${part('a')}</div><div class="qz-b">${part('b')}</div>`;
  $('#qzCnt').textContent = `${qz.base + qz.pos + 1}번째 · ${qz.pool.length}장 중에서`;
  $('#qzPrev').disabled = qz.pos <= 0;
  $('#qzHint').textContent = qz.shown ? '한 번 더 누르면 다음 문제' : '누르면 정답';
  const f = c.classList.contains('flag');
  $('#qzFlag').innerHTML = flagSvg; $('#qzFlag').style.color = f ? 'var(--flag)' : '';
  $('#qzFlag').setAttribute('aria-pressed', f);
}
function qzStep(){ if (!qz.shown){ qz.shown = true; qzRender(); } else qzNext(); }
function qzOpen(){
  qz.pool = vis();
  if (!qz.pool.length){
    alertEmpty();
    if (INFO.sections && VIEW === 'quiz') setTab(SEC.id, 'cards');
    return;
  }
  qz.deck = []; qz.last = null; qz.hist = []; qz.pos = -1; qz.base = 0;
  // 구역 탭이 있는 덱은 퀴즈를 머리 막대 아래 페이지 안 화면으로, 아니면 화면 전체를 덮는 창으로
  const inline = !!INFO.sections;
  $('#qz').classList.toggle('inline', inline);
  $('#qz').hidden = false; if (!inline) document.body.style.overflow = 'hidden';
  $('#qzClose').textContent = inline ? '카드로' : '닫기';
  qzNext(); $('#qzCard').focus();
}
// 퀴즈 탭에서 닫으면 그 구역의 카드 탭으로 돌아간다
function qzClose(silent){
  $('#qz').hidden = true; document.body.style.overflow = '';
  if (!silent && INFO.sections && VIEW === 'quiz') setTab(SEC.id, 'cards');
}
function alertEmpty(){
  const b = INFO.sections ? document.querySelector('#tabs button[data-view="quiz"]') : $('#quizBtn');
  if (!b) return;
  const t = b.textContent; b.textContent = '카드 없음'; setTimeout(() => b.textContent = t, 1500);
}
$('#quizBtn').addEventListener('click', qzOpen);
$('#qzClose').addEventListener('click', () => qzClose());
$('#qzPrev').addEventListener('click', () => { qzPrev(); $('#qzCard').focus(); });
// 글자를 드래그·더블클릭해 고르는 중이면 넘기지 않는다 (복사하려는 것)
const selectingIn = el => { const s = window.getSelection(); return s && !s.isCollapsed && el.contains(s.anchorNode); };
// 정답이 보이는 상태의 한 번 클릭은 0.25초 기다렸다가 넘긴다 — 그 사이 두 번째 클릭(더블클릭으로 단어 고르기)이 오면 취소
let qzTimer = null;
$('#qzCard').addEventListener('click', e => {
  const card = e.currentTarget;
  if (e.detail > 1){ clearTimeout(qzTimer); qzTimer = null; return; }
  if (selectingIn(card)) return;
  if (!qz.shown){ qzStep(); return; }
  clearTimeout(qzTimer);
  qzTimer = setTimeout(() => { qzTimer = null; if (!selectingIn(card)) qzStep(); }, 250);
});
$('#qzFlag').addEventListener('click', () => {
  const c = qz.cur; c.classList.toggle('flag');
  c.classList.contains('flag') ? flags.add(c.dataset.id) : flags.delete(c.dataset.id);
  store.set('flags', [...flags]); qzRender();
});
document.addEventListener('keydown', e => {
  if ($('#qz').hidden) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;   // ⌘C·Ctrl+C 같은 단축키는 건드리지 않는다
  if (e.key === 'Escape'){ qzClose(); }
  else if (e.key === 'ArrowLeft'){ e.preventDefault(); qzPrev(); }
  else if (e.key === ' ' || e.key === 'Enter' || e.key === 'ArrowRight'){ if (e.target.tagName !== 'BUTTON'){ e.preventDefault(); qzStep(); } }
});

const root = document.documentElement;
const themeStore = { get(){ try{ return localStorage.getItem('cert-cards:theme'); }catch(e){ return null; } }, set(v){ try{ localStorage.setItem('cert-cards:theme', v); }catch(e){} } };
const savedTheme = themeStore.get(); if (savedTheme) root.dataset.theme = savedTheme;
$('#themeBtn').addEventListener('click', () => {
  const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = dark ? 'light' : 'dark'; themeStore.set(root.dataset.theme);
});

loadInfo().then(async () => {
  document.querySelectorAll('#ctl .seg button').forEach(b => b.setAttribute('aria-pressed', b.dataset.mode === mode));
  await route();
}).catch(err => {
  $('#main').innerHTML = `<p class="empty">카드를 불러오지 못했습니다. (${esc(err.message)})</p>`;
});
