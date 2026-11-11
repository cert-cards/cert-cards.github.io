# 영역 2 · Content Understanding

## 무엇이고 어디서 쓰나

- **Azure Content Understanding in Foundry Tools** — 생성형 AI로 문서, 이미지, 오디오, 비디오를 분석해 사용자가 정한 구조의 결과로 바꿔 주는 Foundry Tool
  - 비정형 데이터를 자동화 흐름과 분석에 바로 넣을 수 있는 형태로 만든다
- Q: Content Understanding을 쓰려면 Azure에서 먼저 만들 리소스 — Microsoft Foundry 리소스
- Q: Content Understanding이 받는 입력 형식 네 가지 — 문서, 이미지, 오디오, 비디오
- Q: Content Understanding 결과의 두 출력 형태와 용도 — Markdown은 검색과 RAG용, 스키마에 맞춘 JSON은 자동화와 분석용
- Q: 운영 환경에 쓰라고 권하는 GA API 버전 — `2025-11-01`
  - 새 기능 평가용 미리 보기는 `2026-06-01-preview`
- Q: 코드 없이 Content Understanding을 시험해 보는 두 웹 포털 — 새 Foundry 포털, Content Understanding Studio

## 분석기와 스키마

- **분석기 (Analyzer)** — 콘텐츠 추출 설정, 필드 스키마, 사용할 모델 배포를 하나로 묶어 두고 들어오는 모든 입력에 같은 처리 로직을 적용하는 Content Understanding의 핵심 단위
  - 같은 설정을 반복 적용하므로 결과 JSON 모양이 예측 가능하다
- **필드 스키마 (Field schema)** — 무엇을 뽑을지와 결과를 어떤 구조로 담을지를 필드 이름, 타입, 설명으로 정의한 것
  - 분석기 정의 안의 `fieldSchema` 속성
- **콘텐츠 추출 (Content extraction)** — 입력을 정규화된 텍스트와 메타데이터로 바꾸는 첫 단계. 문서는 OCR, 선택 표시, 바코드, 수식, 단락, 표 같은 레이아웃을 읽고 오디오와 비디오는 음성을 받아 적는다
- **필드 추출 (Field extraction)** — 정의한 스키마에 따라 키와 값 쌍의 구조화된 결과를 만드는 단계
- Q: 필드 값을 만드는 세 가지 `method` — `extract`, `classify`, `generate`
- Q: `extract` 방식의 뜻과 지원 범위 — 입력에 적힌 값을 그대로 뽑는다, 문서에서만 지원
- Q: 통화 녹음의 감정을 긍정, 부정, 중립 중 하나로 고르게 할 때 `method`와 함께 쓰는 속성 — `classify`, 후보 목록은 `enum`
- Q: 회의 녹화 영상의 장면 설명이나 통화 요약처럼 입력에 그대로 없는 값을 만들 때 `method` — `generate`
- Q: 송장의 품목 목록처럼 여러 하위 값을 가진 반복 항목을 스키마로 표현하는 방법 — `type: array`의 `items`에 `type: object`와 `properties`를 둔다
- **신뢰도 점수 (Confidence score)** — 추출한 필드 값이 얼마나 믿을 만한지를 0에서 1 사이 숫자로 나타낸 값. 높으면 사람 검토 없이 바로 자동 처리로 넘길 수 있다
- **Content Understanding의 그라운딩 (Grounding)** — 각 필드 값이 원본 콘텐츠의 어느 위치에서 나왔는지 표시해 사람이 출처를 따라가 확인할 수 있게 하는 기능
- Q: 문서 분석기에서 신뢰도 점수와 값의 출처 위치를 함께 켜는 설정 — `estimateFieldSourceAndConfidence`
- Q: 문서를 종류별로 나누거나 영상을 장면별로 쪼개 따로 처리하게 하는 분석기 설정 — `enableSegment` (분할, segmentation)

## OCR, Document Intelligence와의 차이

- Q: 기본 OCR만으로는 못 하고 Content Understanding은 하는 것 — 스키마로 정한 필드에 값의 의미를 맞춰 넣고 값 사이 관계(중첩 구조)까지 잡는다
  - OCR은 글자를 읽을 뿐 의미나 문맥을 이해하지 않는다
- Q: 송장마다 "Invoice No.", "Invoice #"로 다르게 적혀 있거나 레이블이 아예 없을 때 Content Understanding의 동작 — 의미가 같다고 판단하면 같은 필드(예: InvoiceNumber)로 뽑는다
- Q: 정해진 양식이 반복되는 정형 서식에서 일관성과 낮은 지연을 우선할 때 맞는 서비스 — Azure Document Intelligence in Foundry Tools의 prebuilt 모델
- Q: 레이아웃이 제각각인 비정형 문서에서 추론이 필요한 필드까지 뽑을 때 맞는 서비스 — Content Understanding 분석기
- Q: 레이블 데이터 없이 필드 설명만 적어서 사용자 지정 추출을 시작하려 할 때 — Content Understanding 사용자 지정 분석기 (zero-shot)
- Q: 레이블을 단 샘플로 매우 정형적인 문서용 사용자 지정 모델을 학습시키려 할 때 — Document Intelligence 사용자 지정 모델 (변형마다 최소 5개 샘플)
- Q: Foundry 모델에 직접 프롬프트를 짜서 추출하는 방식 대비 Content Understanding이 기본으로 주는 것 — 필드별 신뢰도 점수와 그라운딩, 관리형 확장과 후처리

## 미리 만든 분석기의 종류

- Q: 직접 정의하는 사용자 지정 분석기와 대비되는, 흔한 시나리오용으로 이미 준비된 분석기 — 미리 만든 분석기(prebuilt analyzer)
- Q: 언어 모델 없이 OCR만으로 글자, 단락, 수식, 바코드를 뽑는 분석기 — `prebuilt-read`
- Q: 글자에 더해 표, 그림, 섹션 구조까지 뽑지만 언어 모델이나 임베딩 모델이 필요 없는 분석기 — `prebuilt-layout`
- Q: 사용자 지정 분석기를 만들 때 부모로 지정할 수 있는 기본 분석기 네 가지 — `prebuilt-document`, `prebuilt-image`, `prebuilt-audio`, `prebuilt-video`
  - 분석기 정의의 `baseAnalyzerId` 속성에 넣는다
- Q: RAG 수집용으로 최적화된 분석기 네 가지 — `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch`
- Q: 사내 PDF 보고서를 검색 인덱스에 넣으면서 차트와 다이어그램 설명, 문서 요약, 청크 단위 출력까지 받고 싶을 때 — `prebuilt-documentSearch`
  - 차트는 chart.js 문법, 다이어그램은 mermaid.js 문법으로도 설명한다
- Q: 업체마다 양식이 다른 송장에서 공급자, 금액, 품목을 뽑을 때 — `prebuilt-invoice`
- Q: 여권과 운전면허증에서 신원 정보를 뽑을 때 — `prebuilt-idDocument`
- Q: 계약서에서 당사자와 의무 같은 정보를 뽑을 때 — `prebuilt-contract`
- Q: 콜센터 통화 녹음에서 요약, 감정, 주제, 언급된 회사와 사람을 한 번에 뽑을 때 — `prebuilt-callCenter`

## 이미지, 오디오, 비디오

- Q: Content Understanding 이미지 분석이 맞는 시나리오의 예 — 실적 차트 분석, 생산 라인 결함 탐지, 매장 진열대 상품 집계
- Q: 이미지에서 주로 글자를 뽑아 분석하려 할 때 권하는 방법 — 이미지 분석기 대신 문서 필드 추출 스키마를 쓴다
- Q: 오디오와 비디오 전사 결과의 형식 — WebVTT
- Q: 통화 녹음에서 누가 말했는지 화자별로 대사를 나누는 기능 — 화자 분리(Diarization)
- Q: 콜센터 통화에서 화자를 상담원과 고객 역할로 나누는 기능 — 화자 역할 감지(speaker role detection)
- Q: 오디오 `locales`를 비우거나 `auto`로 두면 켜지는 기능 — 다국어 전사 (구절마다 언어를 따로 적용)
- Q: `prebuilt-audioSearch`가 내 주는 것 — 대화 전사와 대화 요약
- Q: 비디오 콘텐츠 추출이 만드는 기초 메타데이터 — 전사, 키 프레임, 샷(컷) 경계
  - 샷 경계 타임스탬프는 `returnDetails: true`일 때 `cameraShotTimesMs`로 온다
- Q: 뉴스 방송을 기사 단위로 나누려 할 때 비디오 분석기 설정 — `enableSegment: true`와 나눌 기준을 자연어로 적은 `contentCategories`
- Q: 결과 `contents`의 `kind` 값 — 문서와 이미지는 `document`, 오디오와 비디오는 `audioVisual`

## 모델 배포와 안전장치

- Q: 필드 추출 같은 생성형 기능에 Content Understanding이 쓰는 모델 — 내 Foundry 리소스의 chat completion 모델 배포와 embeddings 모델 배포
  - 연결된 배포에서 처리한 토큰은 그 배포로 과금된다
- Q: 유해 콘텐츠 처리를 막는 Content Understanding의 guardrail은 어디서 오나 — 연결된 Foundry 모델 배포에 지정된 guardrail을 물려받는다
  - 막혀도 원문 추출은 남고 일부 필드만 빠진 채 경고와 함께 성공할 수 있다

## 앱에서 호출하기

- Q: 문서 분석을 시작하는 REST 호출 — `POST {endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze?api-version=2025-11-01`
  - 본문은 `{"inputs": [{"url": "..."}]}`
- Q: 키로 인증할 때 REST 요청에 넣는 헤더 — `Ocp-Apim-Subscription-Key`
- Q: analyze 요청에 대한 즉시 응답과 결과 위치를 알려 주는 헤더 — `202 Accepted`, `Operation-Location`
- Q: `Operation-Location`이 가리키는 결과 조회 경로 — `GET {endpoint}/contentunderstanding/analyzerResults/{request-id}`
- Q: 결과를 폴링하다 멈추는 조건 — `status`가 `Succeeded`가 될 때 (진행 중에는 `NotStarted`나 `Running`)
- Q: Python에서 Content Understanding을 쓰는 패키지와 클라이언트 클래스 — `azure-ai-contentunderstanding`, `ContentUnderstandingClient`
- Q: 아래 코드에서 빈칸 ①에 들어갈 메서드 이름은?
  ```text
  client = ContentUnderstandingClient(
      endpoint=os.environ["FOUNDRY_ENDPOINT"],
      credential=AzureKeyCredential(os.environ["FOUNDRY_KEY"]),
  )
  poller = client.①(
      analyzer_id="prebuilt-invoice",
      inputs=[{"url": invoice_url}],
  )
  ```
  - 답: `begin_analyze`
  - begin_ 접두어는 오래 걸리는 작업(LRO)을 시작한다는 뜻
- Q: 아래 코드에서 빈칸 ①에 들어갈 호출은? (분석이 끝날 때까지 기다려 결과 받기)
  ```text
  poller = client.begin_analyze(analyzer_id=analyzer_id, inputs=inputs)
  result = poller.①
  for content in result.contents:
      print(content.markdown)
      print(content.fields)
  ```
  - 답: `result()`
  - 폴링은 SDK가 대신 해 준다
- Q: 아래 curl에서 빈칸 ①에 들어갈 경로 끝부분은?
  ```text
  curl -i -X POST "{endpoint}/contentunderstanding/analyzers/prebuilt-audioSearch①?api-version=2025-11-01" \
    -H "Ocp-Apim-Subscription-Key: {key}" \
    -H "Content-Type: application/json" \
    -d '{"inputs":[{"url": "https://.../call.wav"}]}'
  ```
  - 답: `:analyze`
- Q: 아래 분석기 정의에서 빈칸 ①에 들어갈 `method` 값은?
  ```text
  "fieldSchema": {
    "fields": {
      "Sentiment": {
        "type": "string",
        "method": "①",
        "enum": ["Positive", "Neutral", "Negative"]
      }
    }
  }
  ```
  - 답: `classify`
- Q: 아래 사용자 지정 분석기 정의에서 빈칸 ①에 들어갈 속성 이름은?
  ```text
  {
    "description": "Sample receipt analyzer",
    "①": "prebuilt-document",
    "config": { "estimateFieldSourceAndConfidence": true },
    "fieldSchema": { "fields": { ... } }
  }
  ```
  - 답: `baseAnalyzerId`
