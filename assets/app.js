// 카드 데이터는 data/<자격증>/*.md 에 있다. 페이지가 window.CERT = { files: [...] } 로 목록을 준다.
let DATA = [];

// Markdown 한 파일 → 과목 1개의 그룹 목록
//   # 과목   ## 그룹   > 메모
//   - **용어** — 정의          - Q: 질문 — 답        (들여쓴 "  - " 줄은 보충)
//   - Q: 질문                  코드 읽기 문제: 아래에 들여쓴 ```코드```, 그다음 "  - 답: …"
//     ```c                     여러 줄 답은 "  - 답:" 아래에 네 칸 들여쓴 ```text``` 블록
//     ...
//     ```
//     - 답: `7`
function parseDeck(md){
  const out = []; let ch = '', g = null, last = null, fence = null;
  for (const raw of md.split('\n')){
    const line = raw.replace(/\s+$/, '');
    if (fence){
      if (line.trim() === '```'){ last[fence.key] += '\n```'; fence = null; }
      else last[fence.key] += '\n' + line.slice(Math.min(fence.indent, line.length - line.trimStart().length));
      continue;
    }
    if (!line.trim()) continue;
    let m;
    if ((m = line.match(/^# (.+)/))){ ch = m[1].trim(); continue; }
    if ((m = line.match(/^## (.+)/))){ g = { ch, t: m[1].trim(), items: [] }; out.push(g); last = null; continue; }
    if (!g){ g = { ch, t: '', items: [] }; out.push(g); }
    if ((m = line.match(/^> ?(.*)/))){ g.items.push({ k: 'N', a: m[1] }); last = null; continue; }
    if (last && (m = line.match(/^( {2,})```(\w*)$/))){
      const key = last.ans ? 'b' : 'a';
      last[key] += '\n```' + m[2]; fence = { indent: m[1].length, key }; continue;
    }
    if (last && last.k === 'Q' && !last.ans && (m = line.match(/^ {2,}- 답:\s*(.*)/))){ last.b = m[1]; last.ans = true; continue; }
    if (last && (m = line.match(/^ {2,}- (.*)/))){ last.b += '\n' + m[1]; continue; }
    if ((m = line.match(/^- \*\*(.+?)\*\* — (.*)/))){ last = { k: 'T', a: m[1], b: m[2], ans: true }; g.items.push(last); continue; }
    if ((m = line.match(/^- Q: (.+?) — (.*)/))){ last = { k: 'Q', a: m[1], b: m[2], ans: true }; g.items.push(last); continue; }
    if ((m = line.match(/^- Q: (.+)/))){ last = { k: 'Q', a: m[1], b: '', ans: false }; g.items.push(last); continue; }
    console.warn('읽지 못한 줄:', line);
  }
  out.forEach(g => g.items.forEach(it => {
    if (it.k !== 'N' && !it.ans) console.warn('답이 없는 문제:', it.a);
    if (it.b) it.b = it.b.replace(/^\n+/, '');
  }));
  return out;
}
async function loadDecks(){
  const texts = await Promise.all(window.CERT.files.map(f => fetch(f).then(r => { if (!r.ok) throw new Error(f + ' ' + r.status); return r.text(); })));
  texts.forEach((md, i) => {
    parseDeck(md).forEach(g => { g.ch = (i + 1) + '. ' + g.ch; DATA.push(g); });
  });
}
const $ = s => document.querySelector(s);
const store = {
  get(k, d){ try{ const v = localStorage.getItem((window.CERT.key || 'cards') + ':' + k); return v === null ? d : JSON.parse(v); }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem((window.CERT.key || 'cards') + ':' + k, JSON.stringify(v)); }catch(e){} }
};
let mode = store.get('mode', 'term');
let flags = new Set(store.get('flags', []));
const revealed = new Set();
let total = 0;

const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const inline = s => esc(s).replace(/`([^`]+)`/g, '<code>$1</code>');
// ```lang ... ``` 블록은 <pre>, 나머지는 인라인 서식
const fmt = s => s.split(/(```\w*\n[\s\S]*?\n```)/).map(part => {
  const m = part.match(/^```(\w*)\n([\s\S]*?)\n```$/);
  return m ? `<pre class="code"><code>${esc(m[2])}</code></pre>` : inline(part.replace(/^\n|\n$/g, ''));
}).join('');
const flagSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"/></svg>';

function build(){
  const main = $('#main'), toc = $('#toc');
  let lastCh = null;
  DATA.forEach((sec, si) => {
    if (sec.ch !== lastCh){
      lastCh = sec.ch;
      const m = sec.ch.match(/^(\d+)\.\s*(.*)$/);
      const h = document.createElement('div'); h.className = 'chapter'; h.id = 'c' + si;
      h.innerHTML = `<div class="no">과목 ${m ? m[1].padStart(2,'0') : ''}</div><h2>${esc(m ? m[2] : sec.ch)}</h2>`;
      main.appendChild(h);
      const ta = document.createElement('a'); ta.className = 'ch'; ta.href = '#c' + si; ta.textContent = sec.ch;
      ta.addEventListener('click', closeToc); toc.appendChild(ta);
    }
    const el = document.createElement('section');
    el.id = 's' + si;
    el.innerHTML = `<h3>${fmt(sec.t)}</h3>`;
    const g = document.createElement('div'); g.className = 'grid';
    let cnt = 0;
    sec.items.forEach((it, ii) => {
      const id = si + '-' + ii;
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
    a.addEventListener('click', closeToc);
    toc.appendChild(a);
  });
  const e = document.createElement('div'); e.className = 'empty hidden'; e.id = 'empty'; e.textContent = '조건에 맞는 카드가 없습니다.';
  main.appendChild(e);
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
  $('#prog').textContent = `${revealed.size} / ${total}`;
  $('#pfill').style.width = (revealed.size / total * 100) + '%';
}

function applyFilter(){
  const q = $('#q').value.trim().toLowerCase();
  const onlyFlag = $('#flagBtn').getAttribute('aria-pressed') === 'true';
  const filtering = q || onlyFlag;
  let any = false;
  document.querySelectorAll('section').forEach(sec => {
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
  $('#empty').classList.toggle('hidden', any);
}

function closeToc(){ $('#toc').classList.remove('open'); $('#scrim').classList.remove('open'); }


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
document.querySelectorAll('.seg button').forEach(b => b.addEventListener('click', () => {
  mode = b.dataset.mode; store.set('mode', mode);
  document.querySelectorAll('.seg button').forEach(x => x.setAttribute('aria-pressed', x === b));
  paintAll();
}));
const vis = () => [...document.querySelectorAll('.card:not(.hidden)')].filter(c => !c.closest('section.hidden'));
$('#allBtn').addEventListener('click', () => { vis().forEach(c => setRevealed(c, true)); });
$('#resetBtn').addEventListener('click', () => { document.querySelectorAll('.card').forEach(c => setRevealed(c, false)); });
['flagBtn'].forEach(id => $('#'+id).addEventListener('click', e => {
  const b = e.currentTarget; b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true'); applyFilter();
}));
$('#q').addEventListener('input', applyFilter);
$('#tocBtn').addEventListener('click', () => { $('#toc').classList.add('open'); $('#scrim').classList.add('open'); });
$('#tocClose').addEventListener('click', closeToc);
$('#scrim').addEventListener('click', closeToc);
// ── 퀴즈: 지금 화면에 보이는(필터가 걸려 있으면 걸린) 카드에서 무작위로 끝없이
const qz = { pool: [], deck: [], cur: null, shown: false, n: 0, last: null };
function qzShuffle(){
  const d = qz.pool.slice();
  for (let i = d.length - 1; i > 0; i--){ const j = Math.random() * (i + 1) | 0; [d[i], d[j]] = [d[j], d[i]]; }
  if (d.length > 1 && d[d.length - 1] === qz.last) [d[0], d[d.length - 1]] = [d[d.length - 1], d[0]];
  qz.deck = d;
}
function qzNext(){
  if (!qz.deck.length) qzShuffle();
  qz.cur = qz.deck.pop(); qz.last = qz.cur; qz.shown = false; qz.n++;
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
  $('#qzCnt').textContent = `${qz.n}번째 · ${qz.pool.length}장 중에서`;
  $('#qzHint').textContent = qz.shown ? '한 번 더 누르면 다음 문제' : '누르면 정답';
  const f = c.classList.contains('flag');
  $('#qzFlag').innerHTML = flagSvg; $('#qzFlag').style.color = f ? 'var(--flag)' : '';
  $('#qzFlag').setAttribute('aria-pressed', f);
}
function qzStep(){ if (!qz.shown){ qz.shown = true; qzRender(); } else qzNext(); }
function qzOpen(){
  qz.pool = vis();
  if (!qz.pool.length){ alertEmpty(); return; }
  qz.deck = []; qz.n = 0; qz.last = null;
  $('#qz').hidden = false; document.body.style.overflow = 'hidden';
  qzNext(); $('#qzCard').focus();
}
function qzClose(){ $('#qz').hidden = true; document.body.style.overflow = ''; }
function alertEmpty(){ const b = $('#quizBtn'); b.textContent = '카드 없음'; setTimeout(() => b.textContent = '퀴즈', 1500); }
$('#quizBtn').addEventListener('click', qzOpen);
$('#qzClose').addEventListener('click', qzClose);
$('#qzCard').addEventListener('click', qzStep);
$('#qzFlag').addEventListener('click', () => {
  const c = qz.cur; c.classList.toggle('flag');
  c.classList.contains('flag') ? flags.add(c.dataset.id) : flags.delete(c.dataset.id);
  store.set('flags', [...flags]); qzRender();
});
document.addEventListener('keydown', e => {
  if ($('#qz').hidden) return;
  if (e.key === 'Escape'){ qzClose(); }
  else if (e.key === ' ' || e.key === 'Enter' || e.key === 'ArrowRight'){ if (e.target.tagName !== 'BUTTON'){ e.preventDefault(); qzStep(); } }
});

const root = document.documentElement;
const savedTheme = store.get('theme', null); if (savedTheme) root.dataset.theme = savedTheme;
$('#themeBtn').addEventListener('click', () => {
  const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = dark ? 'light' : 'dark'; store.set('theme', root.dataset.theme);
});

loadDecks().then(() => {
  build(); paintAll(); updateProg();
  document.querySelectorAll('.seg button').forEach(b => b.setAttribute('aria-pressed', b.dataset.mode === mode));
}).catch(err => {
  $('#main').innerHTML = `<p class="empty">카드를 불러오지 못했습니다. (${esc(err.message)})</p>`;
});
