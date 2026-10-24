# cert-cards

자격증 대비 정답 가리기 플래시카드입니다.

**사이트: https://cert-cards.github.io**

| 자격증 | 바로가기 | 데이터 |
|---|---|---|
| 정보처리기사 | [info-processing](https://cert-cards.github.io/info-processing/) | [data/info-processing](data/info-processing) |

## 쓰는 법

- 카드를 누르면 정답이 보이고, 다시 누르면 가려집니다.
- **용어 가리기 / 설명 가리기**로 어느 쪽을 맞힐지 고릅니다. 순서·명령어 같은 문답 카드는 항상 정답 쪽이 가려집니다.
- **퀴즈**: 지금 화면에 보이는 카드에서 무작위로 한 장씩 끝없이 냅니다. 한 번 누르면 정답, 한 번 더 누르면 다음 문제입니다. **← 이전**으로 앞서 푼 문제로 돌아갈 수 있습니다(최근 300문제까지). 키보드는 스페이스·엔터·→(다음), ←(이전), Esc(닫기).
- **다시 볼 것 · 검색**으로 범위를 좁힌 뒤 퀴즈를 켜면 그 카드만 나옵니다.
- 책갈피(다시 볼 것) 표시는 이 브라우저에만 저장됩니다.

## 카드 데이터

카드는 과목마다 Markdown 파일 하나입니다. GitHub에서 그대로 읽을 수 있고, 고치면 사이트에 바로 반영됩니다.

```markdown
# 과목 이름

## 그룹 이름

- **용어 (English)** — 정의
  - 보충 한 줄 (선택)
- Q: 질문 — 답

- Q: 다음 코드의 출력 결과는?
  ```c
  int main(void) { ... }
  ```
  - 답: `7`
  - 해설 한 줄 (선택)

> 가리지 않는 메모
```

- 용어와 정의 사이는 ` — `(앞뒤 공백이 있는 줄표)입니다.
- `- **…**` 줄은 용어 카드, `- Q:` 줄은 문답 카드가 됩니다.
- 코드는 백틱으로 감쌉니다. 코드 읽기 문제의 답은 실제로 실행한 출력과 같아야 합니다. 여러 줄 답은 `- 답:` 아래에 네 칸 들여쓴 ```` ```text ```` 블록으로 씁니다.

```
index.html                  첫 화면 (자격증 목록은 data/decks.json에서 자동으로)
<자격증>/index.html          자격증 페이지 (제목과 deck 이름만 있음)
assets/                     공용 화면 코드 (app.js · cards.css · home.js · home.css)
data/decks.json             첫 화면에 보일 자격증 순서
data/<자격증>/deck.json      제목 · 안내 문구 · 파일 목록
data/<자격증>/NN-*.md        카드 데이터 (파일 하나 = 과목 하나, 이름 순서가 과목 순서)
```

로컬에서 볼 때는 파일을 직접 열지 말고 서버를 띄웁니다: `python3 -m http.server`

### 검사

push·PR마다 GitHub Actions가 `tools/check.py`를 돌립니다. 고친 뒤 로컬에서 먼저 돌려 볼 수 있습니다.

```
python3 tools/check.py            # 전부 (C 컴파일러·JDK·Python 필요)
python3 tools/check.py --no-code  # 코드 실행 빼고 빠르게
```

- **형식**: 위 규칙에 맞지 않는 줄, 답이 없는 문제, 닫히지 않은 코드 블록, 정의에 용어가 그대로 들어간 카드
- **덱 일치**: `decks.json` · `deck.json` · 페이지 · 폴더 안 파일이 서로 맞는지
- **코드 답**: 코드 읽기 문제를 실제로 컴파일·실행한 출력이 「답」과 같은지 (C는 미정의 동작 검사를 켜고 경고 0개)

## 자격증 추가하는 법

예: 정보보안기사를 `security-engineer`라는 이름으로 추가할 때.

1. **카드 쓰기** — `data/security-engineer/`에 과목별 Markdown(`01-....md`, `02-....md` …)과 `deck.json`을 만든다.

   ```json
   {
     "title": "정보보안기사",
     "summary": "",
     "notes": ["비공식 학습 자료입니다."],
     "files": ["01-system.md", "02-network.md"]
   }
   ```

   `files` 순서가 과목 순서다. `summary`는 첫 화면에 짧게 붙는 설명(비워도 된다).

2. **페이지 만들기** — `info-processing/index.html`을 `security-engineer/index.html`로 복사하고 두 군데만 바꾼다.

   ```html
   <title>정보보안기사 플래시카드</title>
   <script>window.CERT = { deck: 'security-engineer' };</script>
   ```

3. **목록에 올리기** — `data/decks.json`에 `"security-engineer"`를 추가한다. 위 README 표에도 한 줄 넣는다.
4. **검사** — `python3 tools/check.py`가 통과하면 끝. 빠뜨린 단계가 있으면 어디가 빠졌는지 알려 준다.

화면(상단 바·퀴즈·목차)은 `assets/app.js`가 그리므로 자격증마다 따로 고칠 것이 없다. 과목 수·카드 수도 첫 화면이 파일에서 직접 센다.

## 알림

- 비공식 학습 자료입니다. 시험 시행 기관과 관련이 없습니다. 최신 출제기준과 일정은 Q-Net에서 확인하세요.
- 틀린 내용은 [Issues](https://github.com/cert-cards/cert-cards.github.io/issues)로 알려 주세요.

## 라이선스

[MIT](LICENSE)
