// 첫 화면: data/decks.json의 순서대로 자격증 카드를 그린다.
// 과목 수는 deck.json의 파일 수, 카드 수는 Markdown에서 센다 — 숫자를 손으로 적어 두지 않는다.
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const get = (url, as) => fetch(url).then(r => { if (!r.ok) throw new Error(url + ' ' + r.status); return as === 'json' ? r.json() : r.text(); });

async function deckCard(id){
  const info = await get(`data/${id}/deck.json`, 'json');
  const count = async files => (await Promise.all(files.map(f => get(`data/${id}/${f}`))))
    .reduce((n, md) => n + md.split('\n').filter(l => l.startsWith('- ')).length, 0);
  let parts;
  if (info.sections){
    // 구역이 있는 덱: 「필기 120장 · 실기 350장 · 실습 30문제」처럼
    parts = [];
    for (const s of info.sections){
      const n = await count(s.files || []);
      if (n) parts.push(`${s.label} ${n}장`);
      if (s.practice){
        const bank = await get(`data/${id}/${s.practice}`, 'json').catch(() => null);
        if (bank && bank.problems.length) parts.push(`${s.label} 실습 ${bank.problems.length}문제`);
      }
    }
  } else {
    parts = [`${info.files.length}${info.unitLabel || '과목'}`, `${await count(info.files)}장`];
  }
  const meta = [...parts, info.summary].filter(Boolean).join(' · ');
  return `<a class="deck" href="${esc(id)}/">
      <div>
        <div class="name">${esc(info.title)}</div>
        <div class="meta">${esc(meta)}</div>
      </div>
      <span class="go">열기 →</span>
    </a>`;
}

(async () => {
  const list = document.getElementById('decks');
  try {
    const ids = await get('data/decks.json', 'json');
    list.innerHTML = (await Promise.all(ids.map(deckCard))).join('');
  } catch (err) {
    list.innerHTML = `<p class="soon">목록을 불러오지 못했습니다. (${esc(err.message)})</p>`;
  }
})();
