# 영역 1 · 생성형 AI 모델과 구성

## 생성형 AI 모델의 작동 원리

- **생성형 AI (Generative AI)** — 자연어 대화를 비롯해 이미지·영상·코드 같은 새 콘텐츠를 만들어 내는 AI 분야
- Q: 언어 모델이 응답을 만드는 기본 방식 — 지금까지의 순서를 보고 다음에 올 확률이 가장 높은 토큰을 반복해서 예측
  - Learn은 휴대폰의 예측 입력 기능을 아주 강력하게 만든 것에 빗댄다
- **토큰 (Token)** — 모델이 처리하는 가장 작은 텍스트 단위. 단어뿐 아니라 단어 조각, 문장부호, 자주 쓰이는 문자열도 하나의 단위가 된다
- **임베딩 (Embedding)** — 텍스트나 토큰의 의미와 언어적 특징을 담은 다차원 숫자 벡터. 비슷한 맥락에서 쓰이는 것끼리 벡터 방향이 비슷해진다
  - 실제 모델의 벡터는 수천 개 요소를 가진다
- Q: 두 임베딩이 의미상 얼마나 가까운지 재는 대표적 방법 — 코사인 유사도 (cosine similarity)
  - 두 벡터 사이 각도의 코사인을 본다
- **트랜스포머 (Transformer)** — 어텐션으로 토큰 사이 관계를 계산해 의미 벡터를 만들고 이어질 토큰을 예측하는 신경망 구조. 오늘날 언어 모델의 바탕이다
- **어텐션 (Attention)** — 한 토큰의 의미를 계산할 때 주변 토큰이 얼마나 영향을 주는지 가중치를 매기는 기법
  - I heard a dog bark에서 bark를 볼 때 I나 a보다 heard와 dog에 큰 가중치가 실린다
- Q: 트랜스포머의 두 블록과 각각의 역할 — 인코더는 임베딩 생성, 디코더는 다음 토큰 예측
- Q: 토큰 벡터와 함께 넣어 문장 안의 순서를 알려 주는 정보 — 위치 인코딩 (positional encoding)
- Q: 학습(training)과 추론(inference)의 차이 — 학습은 정답과의 오차로 가중치를 고치는 과정, 추론은 학습된 모델로 새 입력에 응답을 만드는 과정

## 모델의 종류

- **대형 언어 모델 (LLM)** — 아주 많은 데이터와 변수로 학습해 범용 작업에 두루 강하지만 학습과 사용 비용이 큰 언어 모델
- **소형 언어 모델 (SLM)** — 데이터와 변수 수를 줄여 특정 주제에 집중하거나 기기·로컬 앱에 가볍게 배포하기 좋은 언어 모델
- Q: LLM과 SLM을 가르는 기준 — 학습 데이터의 양과 모델 변수(매개변수)의 수
- Q: 휴대폰 안에서 가볍게 돌아가야 하는 AI 기능에 알맞은 모델 종류 — SLM
- **파운데이션 모델 (Foundation model)** — GPT·Claude·Mistral처럼 대규모 사전 학습을 마쳐 언어·추론·멀티모달 능력을 바로 쓸 수 있고, 파인튜닝으로 맞춤화도 할 수 있는 모델
- **멀티모달 모델 (Multimodal model)** — 텍스트뿐 아니라 이미지·오디오·영상 같은 여러 형식의 입력을 함께 다루는 모델
  - 학습 자료의 예: Phi-4-multimodal-instruct
- **Reasoning model** — 답하기 전에 문제를 나누고 여러 접근을 따져 보는 사고 과정을 거치는 모델. 다단계 논리, 계획, 에이전트 작업에 강하다
  - 한국어로 추론 모델이라 부르면 inference(추론)와 헷갈리니 주의
- **Reasoning tokens** — 모델이 답을 내기 전 내부에서 생각하는 데 쓰는 토큰. 응답에는 보이지 않지만 컨텍스트 창을 차지하고 출력 토큰으로 과금된다
- Q: reasoning model이 얼마나 오래 생각할지 조절하는 매개변수 — `reasoning_effort`
- Q: reasoning model의 출력 상한을 Chat Completions API와 Responses API에서 각각 지정하는 매개변수 — `max_completion_tokens`, `max_output_tokens`
  - 두 상한 모두 reasoning tokens까지 포함해 센다
- Q: 문서 검색을 위해 텍스트를 의미 벡터로 바꿀 때 고를 모델 종류와 예 — 임베딩 모델, text-embedding-3-small
  - 임베딩 모델은 글을 생성하지 않고 벡터 검색, 추천, 분류, 군집에 쓰인다

## 능력으로 모델 고르기

- **Foundry model catalog** — 여러 공급자의 생성형 AI 모델을 출처·기능·추론 작업 등으로 걸러 찾고 비교한 뒤 배포까지 이어 가는 Foundry의 중앙 허브
- Q: 모델 카탈로그의 두 범주 — Foundry Models sold by Azure, Models from partners and community
- Q: Microsoft가 호스팅하고 Azure 구독으로 과금되며 Azure SLA와 Microsoft 지원을 받는 모델 범주 — Foundry Models sold by Azure
  - Azure OpenAI 모델은 모두 여기에 속한다
- Q: 카탈로그의 모델 항목에서 볼 수 있는 정보 — 설명과 기능, 벤치마크 결과, 지원 추론 작업과 파인튜닝 여부, 책임 있는 AI 문서
- Q: 카탈로그에서 모델의 용도, 제약, 책임 있는 AI 관련 주의점을 확인하는 곳 — 그 모델의 모델 카드
- Q: 용도가 분명하고 맞춤 모델링 없이 예측 가능한 성능과 빠른 도입이 필요할 때 카탈로그 모델 대신 고려할 것 — Foundry Tools (미리 만들어진 모델 기반)
- **Model leaderboards** — 카탈로그 모델을 품질·안전·비용·성능 같은 표준 벤치마크로 순위 매겨 나란히 비교하게 해 주는 Foundry portal 기능
- Q: leaderboard의 quality index가 높다는 뜻 — 추론·코딩·수학·지식 과제 전반의 정확도가 높다
  - 0에서 1 사이 값이고 클수록 좋다
- Q: 안전 벤치마크의 attack success rate는 높을수록 좋은가 낮을수록 좋은가 — 낮을수록 공격에 강한 모델
- Q: 코딩이나 수학처럼 특정 용도에 맞는 모델을 찾을 때 먼저 볼 leaderboard — scenario leaderboard
- Q: 공개 데이터셋이 아니라 내 데이터로 모델을 시험해 보는 카탈로그 경로 — Benchmarks에서 Try with your own data
- Q: accuracy·precision·recall·F1과 groundedness·relevance·coherence·fluency는 각각 어떤 지표 — 앞은 전통 NLP 지표, 뒤는 AI-assisted 품질 지표
- **Evaluator (Foundry)** — 모델이나 에이전트 출력의 품질·안전성·효과를 측정하는 구성 요소. 문제를 찾아 점수를 매길 뿐 직접 고치지는 않는다

## 배포 옵션

- Q: 모델을 배포한다는 것의 뜻 — 앱이 API로 호출할 수 있는 안정적이고 확장 가능한 엔드포인트로 모델을 서비스화하는 것
- **TPM (Tokens per minute)** — 배포에 할당하는 분당 처리 토큰 한도. 늘리면 처리 용량이 커지고 RPM 같은 요청 한도도 이에 따라 정해진다
- **스로틀링 (Throttling)** — 처리 한계에 가까워진 시스템이 안정성을 지키려고 처리량을 일부러 제한하는 것
- Q: 스로틀링 오류가 날 때 학습 자료가 권하는 조치 — 최대 출력 토큰을 낮추거나 동시 요청 수를 줄인다
- Q: Foundry의 세 가지 배포 옵션 — Serverless API, Managed compute (preview), Foundry Local on Azure Local (preview)
- Q: Foundry가 우선 권장하고 standard·provisioned·batch 같은 deployment type을 고를 수 있는 배포 옵션 — Serverless API
- Q: 오픈소스나 커스텀 가중치 모델을 Microsoft가 관리하는 전용 GPU에 올리는 배포 옵션 — Managed compute
  - 과금은 가속기 SKU별 시간 단위
- Q: 배포를 만들지 않고 모델 이름만으로 바로 추론을 호출하는 기능 — instant access (preview)
- Q: deployment type의 세 범주와 과금 방식 — standard는 토큰당 과금, provisioned는 예약 용량, batch는 할인된 비동기 처리
- **PTU (Provisioned throughput unit)** — provisioned 배포에서 미리 사 두는 처리 용량 단위. 처리량이 보장되고 지연 시간 편차가 작다
- Q: 특별한 이유가 없을 때 처음 고를 deployment type — Global Standard
  - 신규 모델이 가장 먼저 나오고 가격이 가장 낮으며 지원 지역이 가장 넓다
- Q: Global, Data Zone, Standard 유형의 추론 데이터 처리 범위 — 아무 Azure 지역, US·EU·APAC 데이터 구역 안, 지정한 Azure geography 안
- Q: 추론 데이터가 EU 안에서만 처리돼야 하고 트래픽이 들쭉날쭉하다. 알맞은 deployment type — Data Zone Standard
- Q: 대량 트래픽이 꾸준하고 지연 시간 편차를 작게 유지해야 한다. 알맞은 범주 — Provisioned (예: Global Provisioned)
- Q: 급하지 않은 대량 문서 요약을 적은 비용으로 돌리려 한다. 알맞은 deployment type — Global Batch
  - Global Standard보다 50% 저렴하고 24시간 안 처리를 목표로 하며 할당량이 따로 잡힌다
- Q: 파인튜닝한 모델을 평가용으로만 잠깐 띄우는 deployment type — Developer
  - SLA와 데이터 상주 보장이 없고 24시간 뒤 자동 삭제된다

## 구성 매개변수

- **Temperature** — 출력의 무작위성을 정하는 값. 낮추면 집중되고 일관된 답, 높이면 다양하고 창의적인 답이 나온다
  - Foundry 프롬프트 엔지니어링 문서 기준 0에서 2 사이로 설정한다
- Q: 법률 문서를 생성하는 앱과 소설을 쓰는 앱 중 temperature를 낮게 둘 쪽 — 법률 문서 앱
- Q: temperature와 비슷하게 응답의 무작위성을 조절하지만 방식이 다른 매개변수 — `top_p`
- Q: temperature와 top_p를 조정할 때의 일반 권장 — 한 번에 둘 중 하나만 바꾼다
- Q: playground에서 응답 길이 상한을 정해 토큰 소비와 스로틀링에 영향을 주는 설정 — max output tokens
- Q: 지정한 문자열이 나오면 생성을 멈추게 하는 매개변수와 최대 개수 — `stop`, 최대 4개
  - 반환된 텍스트에는 그 문자열이 들어가지 않는다
- Q: 같은 문장을 그대로 되풀이하는 경향을 줄이려면 올릴 매개변수 — `frequency_penalty`
- Q: 이미 나온 토큰에 불이익을 줘 새 주제로 넘어가게 하는 매개변수 — `presence_penalty`
- Q: frequency_penalty와 presence_penalty의 차이 — 앞은 등장 횟수에 비례해, 뒤는 한 번이라도 등장했는지로 불이익을 준다
  - 둘 다 -2.0에서 2.0 사이 값
