# 영역 2 · 생성형 AI 앱

## Foundry의 구성

- **Microsoft Foundry** — 에이전트, 모델, 도구를 하나의 Azure 관리 단위에 모아 두고 추적, 평가, 권한, 네트워크까지 함께 다루게 해 주는 Microsoft의 AI 앱 개발 플랫폼
  - 예전 이름: Azure AI Studio, Azure AI Foundry
- **Foundry 리소스 (Foundry resource)** — 여러 작업 공간을 담는 최상위 Azure 리소스. 모델 배포, 접근 제어, 네트워크, 정책을 이 한 곳에서 관리한다
  - 예전 구조: 허브(hub) + Azure OpenAI 리소스 + Azure AI Services 리소스를 따로 묶어 쓰던 방식
- **프로젝트 (Project)** — 리소스 안에서 팀이 모델, 에이전트, 데이터를 모아 실제 개발을 하는 작업 공간. 코드는 이 단위의 엔드포인트 하나로 접속한다
  - 엔드포인트 형식: `https://<리소스이름>.services.ai.azure.com/api/projects/<이름>`
- **Foundry 포털 (Foundry portal)** — ai.azure.com에서 모델을 둘러보고 프롬프트를 시험하고 에이전트를 코드 없이 만드는 웹 화면
  - 지금은 새 포털과 Foundry (classic) 포털이 함께 있다. 새 포털을 쓰려면 New Foundry 토글을 켠다
- Q: 허브 기반 프로젝트(hub-based project)를 계속 써야 할 때 여는 포털 — Foundry (classic) 포털
  - 새 투자는 새 포털의 Foundry 프로젝트에 집중된다
- Q: 포털에서 프로젝트 엔드포인트를 복사할 수 있는 곳 — 프로젝트를 열었을 때 나오는 첫 화면(welcome screen)
- Q: 팀원이 프로젝트에서 모델을 써서 앱을 만들고 시험할 수 있게 주는 최소 권한 역할 — Foundry User
  - 예전 이름: Azure AI User. 역할 ID와 권한은 이름이 바뀌어도 같다

## 모델 카탈로그와 배포

- **모델 카탈로그 (Model catalog)** — 1만 개가 넘는 모델을 키워드와 필터로 찾고, 벤치마크를 비교하고, 바로 배포까지 시작하는 포털 화면
  - 필터 예: 컬렉션(제공사), 지역, 배포 옵션, 수명 주기(Preview, GA, Deprecated), 추론 작업 종류
- Q: 카탈로그가 모델을 나누는 두 큰 분류 — Foundry Models sold by Azure, Foundry Models from partners and community
- Q: Microsoft가 직접 지원하고 엔터프라이즈 SLA를 주는 쪽 — Foundry Models sold by Azure
  - 파트너, 커뮤니티 모델은 제공한 회사나 커뮤니티가 지원한다
- **모델 카드 (Model card)** — 카탈로그에서 모델 하나를 열면 보이는 상세 페이지. Quick facts와 Details, Deployments, Benchmarks, License 탭으로 모델을 설명한다
- Q: 카탈로그에서 여러 모델의 성능 지표를 나란히 보려고 고르는 기능 — View leaderboard 또는 Compare models
- Q: 새 포털에서 카탈로그의 모델을 프로젝트에 배포하는 순서 — Build, Catalog, Model Catalog에서 모델을 고른 뒤 Deploy, Default settings

## 플레이그라운드

- **플레이그라운드 (Playground)** — 설치나 코드 없이 배포된 모델이나 에이전트에 바로 말을 걸어 프롬프트, 설정, 도구를 빠르게 시험하는 포털 안 채팅 환경
  - Model playground와 Agents playground 두 가지가 있다
- Q: 포털에서 모델 배포를 마치면 곧바로 이동하는 화면 — 그 모델의 Model playground
- Q: Model playground에서 시스템 프롬프트 외에 조정할 수 있는 것 — temperature, top_p, max_tokens 같은 매개변수와 web search, file search, code interpreter 같은 도구
- Q: Model playground의 비교 모드로 한 번에 나란히 돌릴 수 있는 모델 수 — 최대 3개
  - 같은 프롬프트, 같은 시스템 메시지, 같은 설정이 세 모델에 동시에 들어간다
- Q: 플레이그라운드에서 시험한 내용을 앱 코드로 옮길 때 쓰는 탭 — 채팅 창의 Code 탭 (언어별 샘플 코드)
  - 같은 탭의 Open in VS Code for the Web을 누르면 엔드포인트와 키까지 들어간 작업 공간이 열린다
- Q: Model playground에서 다듬은 모델을 에이전트로 이어서 만들려면 누르는 버튼 — Save as agent

## 메시지 역할

- **시스템 메시지 (System message)** — 대화 배열 맨 앞에 두어 모델의 역할, 말투, 허용 범위, 출력 형식을 정하는 최상위 지시. 시스템 프롬프트, 메타프롬프트라고도 부른다
  - 넣지 않아도 되지만 기본적인 것 하나는 넣는 편이 결과가 좋다
- **사용자 메시지 (User message)** — 앱을 쓰는 사람이 실제로 보낸 질문이나 요청. 배열 마지막을 이 역할로 끝내야 모델이 답할 차례가 된다
- **어시스턴트 메시지 (Assistant message)** — 모델이 앞서 내놓은 답. 대화 기록을 다시 보낼 때나 원하는 답의 모범 예시로 넣는다
- Q: 고객이 무엇을 묻든 존댓말로만 답하고 환불 규정 밖 질문은 상담원 연결을 안내하게 하려면 그 규칙을 넣는 곳 — 시스템 메시지
- Q: 시스템 메시지에 규칙을 적어 두면 모델이 반드시 지키는가 — 아니다. 영향을 줄 뿐 보장하지 않는다
  - 콘텐츠 필터, 평가 같은 다른 완화책과 겹쳐 쓰고 실제 질문으로 시험해야 한다
- Q: Chat Completions로 만든 챗봇이 앞 대화를 기억하게 하려면 — 매 요청마다 이전 user, assistant 메시지를 messages 배열에 다시 담아 보낸다
- Q: 대화가 길어져 토큰 한도에 가까워질 때 오래된 메시지를 지우면서도 남겨 두는 것 — 맨 앞의 시스템 메시지
  - 오래된 user, assistant 메시지부터 지우면 앞부분 맥락은 점점 잃는다
- Q: 시스템 메시지에 "정보가 부족하면 되묻고, 그래도 모르면 모른다고 답하라"를 넣는 목적 — 모를 때의 대체 행동을 정해 지어낸 답을 막는다

## 프롬프트 엔지니어링 기법

- **퓨샷 학습 (Few-shot learning)** — 원하는 입력과 출력의 예시 몇 쌍을 프롬프트에 넣어, 그 요청 한 번 동안만 모델이 같은 방식으로 답하게 하는 방법
  - 예시가 없으면 제로샷(zero-shot), 하나면 원샷(one-shot)
- Q: Chat Completions에서 퓨샷 예시를 넣는 위치와 모양 — 시스템 메시지 뒤에 user, assistant 메시지 쌍으로 넣는다
- **그라운딩 (Grounding)** — 모델이 답을 끌어올 근거 데이터를 프롬프트에 직접 넣어 주는 것. 최신이고 믿을 만한 답이 필요한 경우 가장 효과적인 방법으로 꼽힌다
- Q: 사내 휴가 규정 문서 내용으로만 답하게 하고 싶을 때 쓰는 기법 — 규정 문서를 근거 데이터로 넣고 그 안에서만 답하라고 지시한다(그라운딩)
- Q: 근거 데이터가 너무 많아 시스템 메시지에 다 넣을 수 없을 때 — 임베딩이나 Azure AI Search로 질문 시점에 관련 부분만 찾아 넣는다
- **최근 편향 (Recency bias)** — 프롬프트 뒤쪽에 놓인 정보가 앞쪽 정보보다 출력에 더 크게 작용하는 경향
- Q: 최근 편향을 이용해 지시를 더 잘 따르게 하는 방법 — 같은 지시를 프롬프트 끝에 한 번 더 적는다
- **출력 유도 문구 (Cue)** — 프롬프트 끝에 붙여 모델 답의 첫머리를 정해 주는 짧은 말. 답의 형식과 초점을 원하는 쪽으로 끌고 간다
  - 예: 끝에 `Key Points:` 다음 글머리표를 붙이면 목록으로 답한다
- Q: 모델이 검색어를 여러 개 내놓는데 하나만 받고 싶을 때 프롬프트 끝에 "One possible search query is:"를 붙이는 기법 — 출력 유도(prime the output)
- Q: 지시와 원문 자료가 섞여 모델이 헷갈릴 때 쓰는 방법 — `---` 같은 구분자, 대문자 제목, Markdown이나 XML로 구획을 나눈다
- Q: 사실 확인을 "주장 추출, 그다음 검색어 만들기"처럼 여러 단계로 나눠 시키는 기법 — 작업 쪼개기(break the task down)
- **사고의 사슬 (Chain of thought)** — 모델에게 단계별로 풀이 과정을 보여 준 뒤 최종 답을 내게 하는 기법. 틀릴 가능성을 줄이고 답을 검토하기 쉽게 만든다
- Q: gpt-5나 o 시리즈 같은 추론 모델에 "생각 과정을 전부 보여 줘"라고 요구하는 것이 권장되는가 — 아니다. 이 기법은 비추론 모델용이다
  - 추론 내용은 reasoning summary 매개변수로만 받는다. 다른 방법으로 뽑으려 하면 정책 위반이 될 수 있다
- Q: 답에 출처 인용을 달게 하면 지어낸 내용이 줄어드는 이유 — 거짓 답에 맞는 그럴듯한 출처까지 만들어야 해서 두 번 틀려야 하기 때문이다
- Q: 앱이 정해진 키를 가진 JSON만 받아야 할 때 시스템 메시지에 할 일 — 출력 형식을 예시 스키마와 함께 분명히 적는다
- Q: "본문에 답이 없으면 not found라고 답하라"를 넣어 두는 이유 — 모델에게 빠져나갈 길을 줘서 지어낸 답을 막는다

## SDK로 채팅 클라이언트 만들기

- **AIProjectClient** — `azure-ai-projects` 패키지에서 엔드포인트와 자격 증명으로 만드는 진입 객체. 여기서 모델 호출용 OpenAI 클라이언트를 얻고 에이전트도 관리한다
- **DefaultAzureCredential** — `azure-identity` 패키지의 자격 증명 클래스. 코드에 키를 두지 않고 Microsoft Entra ID 토큰으로 인증하게 해 준다
  - 로컬에서 실행하기 전에 `az login`으로 로그인해 둔다
- Q: 현재 Foundry SDK quickstart가 설치하는 Python 패키지 — `azure-ai-projects` 2.x (인증용 `azure-identity`)
  - 2.x 코드는 1.x와 호환되지 않는다. 1.x 예제는 Foundry (classic) 문서에 있다
- Q: 현재 quickstart가 모델에 프롬프트를 보낼 때 쓰는 API — Responses API (`responses.create`)
- Q: 새 앱을 만들 때 Chat Completions와 Responses API 중 문서가 권하는 쪽 — Responses API
  - Chat Completions에 없는 최신 기능을 지원하고, 대화 기록 관리도 API에 맡길 수 있다
- Q: Chat Completions 응답에서 생성된 텍스트가 있는 경로 — `choices[0].message.content`
- Q: Entra ID 토큰을 받을 때 쓰는 범위(scope) — `https://ai.azure.com/.default`
- Q: Chat Completions 응답의 `finish_reason`이 `length`인 뜻 — 출력 토큰 한도에 걸려 답이 중간에 끊겼다
- Q: 아래 코드에서 빈칸 ①에 들어갈 자격 증명 클래스는?
  ```text
  from azure.ai.projects import AIProjectClient
  from azure.identity import ①

  project = AIProjectClient(
      endpoint=os.environ["PROJECT_ENDPOINT"],
      credential=①(),
  )
  ```
  - 답: `DefaultAzureCredential`
  - API 키 문자열을 넣지 않고 Entra ID로 인증한다
- Q: 아래 코드에서 빈칸 ①에 들어갈 메서드 이름은?
  ```text
  project = AIProjectClient(endpoint=endpoint,
                            credential=DefaultAzureCredential())
  client = project.①()
  reply = client.responses.create(model="gpt-5-mini",
                                  input="안녕?")
  ```
  - 답: `get_openai_client`
- Q: 아래 코드에서 빈칸 ①에 들어갈 속성 이름은?
  ```text
  reply = client.responses.create(
      model="gpt-5-mini",
      input="서울의 면적은?",
  )
  print(reply.①)
  ```
  - 답: `output_text`
- Q: 아래 Chat Completions 코드에서 빈칸 ①에 들어갈 역할 이름은?
  ```text
  messages = [
      {"role": "①", "content": "너는 여행 상담원이다. 한국어로만 답한다."},
      {"role": "user", "content": "제주도 3박 일정 추천해 줘"},
  ]
  reply = client.chat.completions.create(model=deployment,
                                         messages=messages)
  ```
  - 답: `system`
- Q: 아래 messages에서 두 번째와 세 번째 메시지는 어떤 프롬프트 기법인가?
  ```text
  messages = [
      {"role": "system", "content": "기사 제목의 분야를 한 단어로 답한다."},
      {"role": "user", "content": "류현진, 7이닝 무실점 호투"},
      {"role": "assistant", "content": "야구"},
      {"role": "user", "content": "손흥민, 시즌 10호 골"},
  ]
  ```
  - 답: 퓨샷 학습 (예시 user, assistant 쌍)
- Q: 아래 코드에서 빈칸 ①에 들어갈 매개변수 이름은?
  ```text
  first = client.responses.create(model="gpt-5-mini",
                                  input="파국적 망각이 뭐야?")
  second = client.responses.create(
      model="gpt-5-mini",
      ①=first.id,
      input="대학 신입생 눈높이로 다시 설명해 줘",
  )
  ```
  - 답: `previous_response_id`
- Q: 아래 코드에서 빈칸 ①에 들어갈 매개변수 이름은?
  ```text
  reply = client.responses.create(
      model="gpt-5-mini",
      ①="너는 수학 과외 선생님이다. 풀이를 짧게 보여 준다.",
      input="3x + 11 = 14를 풀어 줘",
  )
  ```
  - 답: `instructions`
- Q: 아래 코드는 API 키로 연결한다. 빈칸 ①에 들어갈 경로는?
  ```text
  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["AZURE_OPENAI_API_KEY"],
      base_url="https://my-resource.openai.azure.com①",
  )
  ```
  - 답: `/openai/v1/`
