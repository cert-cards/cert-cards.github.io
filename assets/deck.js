// 카드 페이지(app.js)와 실습 페이지(practice.js)가 같이 쓰는 부분: Markdown 읽기와 서식.

// Markdown 한 파일 → 과목 1개의 그룹 목록
//   # 과목   ## 그룹   > 메모
//   - **용어** — 정의          - Q: 질문 — 답        (들여쓴 "  - " 줄은 보충)
//   - Q: 질문                  코드 읽기 문제: 아래에 들여쓴 ```코드```, 그다음 "  - 답: …"
//     ```c                     여러 줄 답은 "  - 답:" 아래에 네 칸 들여쓴 ```text``` 블록
//     ...
//     ```
//     - 답: `7`
// 코드 문제에는 실습 페이지가 쓰는 값이 더 붙는다:
//   lang(코드 블록 언어) · code(문제 코드) · answer(「답:」 줄) · ansblock(답 아래 여러 줄 블록) · n(파일 안에서 몇 번째 코드 문제인지)
function parseDeck(md){
  const out = []; let ch = '', g = null, last = null, fence = null, codeNo = 0;
  for (const raw of md.split('\n')){
    const line = raw.replace(/\s+$/, '');
    if (fence){
      if (line.trim() === '```'){ last[fence.key] += '\n```'; fence = null; }
      else {
        const body = line.slice(Math.min(fence.indent, line.length - line.trimStart().length));
        last[fence.key] += '\n' + body;
        if (fence.into) last[fence.into] = last[fence.into] === null ? body : last[fence.into] + '\n' + body;
      }
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
      let into = null;
      if (key === 'a' && last.k === 'Q' && last.code === undefined){ last.lang = m[2]; last.code = null; last.n = codeNo++; into = 'code'; }
      else if (key === 'b' && last.answer === '' && last.ansblock === undefined){ last.ansblock = null; into = 'ansblock'; }
      last[key] += '\n```' + m[2]; fence = { indent: m[1].length, key, into }; continue;
    }
    if (last && last.k === 'Q' && !last.ans && (m = line.match(/^ {2,}- 답:\s*(.*)/))){ last.b = m[1]; last.answer = m[1].trim(); last.ans = true; continue; }
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

// 실습 페이지에서 돌릴 수 있는 코드 문제인가: python 블록은 언제나, text 블록은 deck.json에 "practice": true가 있을 때
const canPractice = (it, info) => !!(it && it.code && (it.lang === 'python' || (it.lang === 'text' && info && info.practice)));
// 실행 결과와 견줄 정답: 빈칸(①②…) 문제는 견주지 않는다
function expectedOutput(it){
  if (!it || !it.code || /[①②③④⑤⑥⑦⑧⑨]/.test(it.code)) return null;
  if (it.ansblock) return it.ansblock;
  const a = it.answer || '';
  if (!a) return null;
  return (a.startsWith('`') && a.endsWith('`') && (a.match(/`/g) || []).length === 2) ? a.slice(1, -1) : a;
}

const getText = f => fetch(f).then(r => { if (!r.ok) throw new Error(f + ' ' + r.status); return r.text(); });
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const inline = s => esc(s).replace(/`([^`]+)`/g, '<code>$1</code>');
// ```lang ... ``` 블록은 <pre>, 나머지는 인라인 서식
const fmt = s => s.split(/(```\w*\n[\s\S]*?\n```)/).map(part => {
  const m = part.match(/^```(\w*)\n([\s\S]*?)\n```$/);
  return m ? `<pre class="code"><code>${esc(m[2])}</code></pre>` : inline(part.replace(/^\n|\n$/g, ''));
}).join('');
