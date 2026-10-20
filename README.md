# cert-cards

자격증 실기 대비 정답 가리기 플래시카드입니다.

**사이트: https://cert-cards.github.io**

| 자격증 | 카드 | 바로가기 | 데이터 |
|---|---|---|---|
| 정보처리기사 실기 | 10과목 · 764장 | [info-processing](https://cert-cards.github.io/info-processing/) | [data/info-processing](data/info-processing) |

## 쓰는 법

- 카드를 누르면 정답이 보이고, 다시 누르면 가려집니다.
- **용어 가리기 / 설명 가리기**로 어느 쪽을 맞힐지 고릅니다. 순서·명령어 같은 문답 카드는 항상 정답 쪽이 가려집니다.
- **퀴즈**: 지금 화면에 보이는 카드에서 무작위로 한 장씩 끝없이 냅니다. 한 번 누르면 정답, 한 번 더 누르면 다음 문제입니다. 키보드는 스페이스·엔터·→, 닫기는 Esc.
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

> 가리지 않는 메모
```

- 용어와 정의 사이는 ` — `(앞뒤 공백이 있는 줄표)입니다.
- `- **…**` 줄은 용어 카드, `- Q:` 줄은 문답 카드가 됩니다.
- 코드는 백틱으로 감쌉니다.

```
index.html                 첫 화면
info-processing/index.html 자격증 페이지 (불러올 파일 목록만 있음)
assets/                    공용 화면 코드 (app.js · cards.css · home.css)
data/<자격증>/NN-*.md      카드 데이터
```

로컬에서 볼 때는 파일을 직접 열지 말고 서버를 띄웁니다: `python3 -m http.server`

## 알림

- 비공식 학습 자료입니다. 시험 시행 기관과 관련이 없습니다. 최신 출제기준과 일정은 Q-Net에서 확인하세요.
- 틀린 내용은 [Issues](https://github.com/cert-cards/cert-cards.github.io/issues)로 알려 주세요.

## 라이선스

[MIT](LICENSE)
