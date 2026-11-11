# 영역 2 · 에이전트

## 에이전트란

- **AI 에이전트 (AI agent)** — 모델에 지시와 도구를 짝지어, 요청을 따져 보고 필요하면 도구를 불러 실제 작업까지 해내는 AI 구성
- Q: Foundry 문서가 말하는 에이전트의 세 요소 — 모델, 지시(instructions), 도구(tools)
- **Foundry Agent Service** — 에이전트를 만들고 배포하고 확장하는 Foundry의 관리형 서비스. 런타임이 대화 상태, 도구 호출, 에이전트 수명 주기를 맡는다
- **지시문 (Instructions)** — 에이전트가 늘 따를 역할, 목표, 규칙을 적은 글. 에이전트에 저장해 두므로 요청할 때마다 다시 보내지 않아도 된다
- **프롬프트 에이전트 (Prompt agent)** — 모델, 지시, 도구를 설정하는 것만으로 선언적으로 정의하고 실행은 Foundry가 맡는 에이전트. 관리할 앱 코드나 컨테이너가 없다
- **호스티드 에이전트 (Hosted agent)** — Agent Framework, LangGraph 같은 프레임워크나 직접 짠 코드를 컨테이너로 올리면 Foundry가 엔드포인트, 확장, ID를 관리해 주는 에이전트
- Q: 인프라와 코드 관리 없이 가장 빨리 업무용 에이전트를 만들려는 팀이 고를 유형 — 프롬프트 에이전트
- Q: 직접 만든 오케스트레이션 로직과 멀티 에이전트 코드를 그대로 Foundry에서 실행하려는 팀이 고를 유형 — 호스티드 에이전트
- Q: 음성 처리 파이프라인을 직접 운영하지 않고 실시간 음성 대화 에이전트를 만들 때 고를 유형 — 음성 기반 프롬프트 에이전트(voice-based prompt agent)
  - Voice Live로 연결하며 현재 미리보기 기능이다
- Q: Foundry에 에이전트 리소스를 만들지 않고 앱 코드 안에 지시와 도구를 두고 매번 Responses API를 직접 호출하는 방식 — 임시 에이전트(ephemeral agent)

## 대화, 응답, 버전

- **대화 (Conversation)** — 에이전트와 여러 턴 주고받은 기록을 서버에 보관하는 객체. 같은 id로 요청하면 앞 내용을 기억한 채 답한다
  - 예전 이름: 스레드(Thread)
- **항목 (Item)** — conversation 안에 쌓이는 낱개 요소. 사용자 메시지, 모델 메시지, 도구 호출과 그 결과가 각각 하나씩 된다
  - 예전 이름: 메시지(Message)
- **응답 (Response)** — 에이전트나 모델을 한 번 실행해 출력을 받는 호출 단위. `responses.create`가 만든다
  - 예전 이름: 런(Run)
- **에이전트 버전 (Agent version)** — 에이전트의 모델, 지시, 도구 설정을 저장할 때마다 남는 스냅숏. 이전 것으로 되돌리거나 서로 비교할 수 있다
  - 예전 이름: 어시스턴트(Assistant)
- Q: 지금 Foundry 에이전트(Agents v2)가 쓰는 API — Responses API
  - 예전 Agents v0.5와 v1은 Assistants API를 썼다
- Q: 에이전트에게 "프랑스 면적은?"에 이어 "수도는?"을 물었을 때 앞 질문을 이해하게 하려면 — 두 요청에 같은 conversation id를 넘긴다

## 포털에서 만들고 시험하기

- Q: 새 Foundry 포털에서 에이전트를 만드는 메뉴 순서 — Build, 왼쪽 Agents, Create agent
- Q: Agents playground에서 할 수 있는 일 — 지시와 페르소나 설정, 도구와 지식 원본 연결, 대화 시험, 추적과 평가 확인
- Q: Agents playground에서 기본으로 켜져 있어 사용량 요금이 붙는 기능 — 평가(evaluations)
  - 끄려면 오른쪽 위 metrics에서 평가기를 모두 해제한다
- Q: 함수 호출 도구를 포털에서 추가하거나 수정할 수 있는가 — 아니다. SDK나 REST API로 설정한다
  - 포털은 함수를 대신 실행하지도 않는다
- Q: 포털에서 만든 에이전트를 앱 코드에서 부르려면 필요한 두 값 — 프로젝트 엔드포인트, 에이전트 이름
- Q: 에이전트의 모델 호출과 도구 호출 과정을 추적(trace)으로 남기려면 프로젝트에 연결하는 리소스 — Application Insights
- Q: 게시한 에이전트를 사용자에게 나눠 줄 수 있는 곳 — Microsoft Teams, Microsoft Copilot, Entra Agent Registry

## 에이전트 도구

- **도구 (Tool)** — 에이전트가 모델의 학습 지식 밖에서 정보를 찾아오거나 실제 행동을 할 수 있게 붙이는 기능. 내장형과 사용자 정의형이 있다
- **파일 검색 (File search)** — 올린 문서를 자동으로 나누고 임베딩해 벡터 저장소에 넣은 뒤, 키워드와 의미 검색을 섞어 관련 대목을 찾아 답에 쓰는 내장 도구
  - 기본 청크 크기 800토큰, 겹침 400토큰
- Q: 사용자가 올린 제품 설명서 PDF 내용으로 답하는 에이전트에 붙일 도구 — 파일 검색
- Q: 파일 검색 도구가 문서를 담아 검색하는 저장 단위 — 벡터 저장소(vector store)
- Q: 에이전트 하나에 붙일 수 있는 벡터 저장소 수 — 1개
  - 대화 하나에도 1개까지 붙일 수 있다
- Q: 이미 운영 중인 Azure AI Search 인덱스를 에이전트가 검색하게 하려면 고르는 도구 — Azure AI Search 도구
- **코드 인터프리터 (Code interpreter)** — 모델이 파이썬 코드를 직접 써서 격리된 샌드박스에서 실행하게 하는 내장 도구. 계산, 데이터 분석, 차트 파일 생성에 쓴다
  - 토큰 요금과 별도로 과금된다
- Q: 올린 CSV로 부서별 매출 막대그래프 PNG를 만들어 달라는 요청에 필요한 도구 — 코드 인터프리터
- Q: 코드 인터프리터 세션이 유지되는 시간 — 최대 1시간, 30분 동안 쓰지 않으면 종료
- Q: 코드 인터프리터 샌드박스 안의 코드가 외부 인터넷을 호출할 수 있는가 — 없다
- **웹 검색 (Web search)** — 공개 인터넷에서 최신 정보를 가져와 인라인 인용과 함께 답하게 하는 내장 도구. 내부적으로 Grounding with Bing을 쓴다
- Q: 오늘 날씨나 어제 발표된 소식처럼 모델 학습 이후 정보가 필요한 질문에 붙일 도구 — 웹 검색
- Q: 웹 검색 도구를 쓸 때 데이터 처리에서 주의할 점 — 질의가 Azure 규정 준수, 지리적 경계 밖으로 전송되고 Microsoft DPA가 적용되지 않는다
- Q: 에이전트의 웹 검색 결과를 회사가 지정한 공개 도메인으로만 제한하려면 — Grounding with Bing Custom Search 구성을 쓴다
- **함수 호출 (Function calling)** — 내 함수의 이름, 설명, 매개변수 스키마를 에이전트에 알려 두면 모델이 실행을 요청하고, 실제 실행은 내 앱이 맡아 결과를 돌려주는 방식
- Q: 함수 호출에서 함수를 실제로 실행하는 쪽 — 클라이언트 앱 (에이전트 서비스가 아니다)
- Q: 내 앱 안의 파이썬 함수로 사내 재고 DB를 조회해 답하게 하려면 쓰는 도구 — 함수 호출
- Q: 함수 실행 결과를 제출해야 하는 시간 제한 — 실행이 만들어지고 10분 안
  - 오래 걸리는 작업은 상태를 먼저 돌려주고 따로 확인하게 만든다
- Q: OpenAPI 명세가 이미 있는 외부 REST 서비스를 에이전트에 연결할 때 쓰는 도구 — OpenAPI 도구
- **MCP (Model Context Protocol)** — 애플리케이션이 LLM에 도구와 맥락 데이터를 제공하는 방식을 정한 개방형 표준. 에이전트는 원격 서버에 붙어 그 서버가 내놓은 도구를 쓴다
- Q: 원격 MCP 서버의 도구를 호출하기 전에 사람이 확인하게 하는 설정 — `require_approval`을 `always`로
- Q: MCP 서버가 내놓은 도구 중 일부만 허용하려면 — `allowed_tools`에 도구 이름 목록을 준다
  - 빈 목록 `[]`는 아무것도 막지 않고 전부 허용한다
- Q: 원격 MCP 서버가 보낸 도구 설명과 결과를 다루는 원칙 — 신뢰할 수 없는 입력으로 본다. 간접 프롬프트 주입이 숨어 있을 수 있다
- **툴박스 (Toolbox)** — 여러 도구를 한 번 골라 묶어 MCP 호환 엔드포인트 하나로 여러 에이전트에 제공하는 관리 단위. 인증, 거버넌스, 버전을 한곳에서 다룬다
- Q: 툴박스에 넣지 못하고 에이전트에 직접 붙여야 하는 도구 예 — 함수 호출 (클라이언트 쪽에서 실행되므로)
- **Foundry IQ** — 여러 데이터 원본을 묶은 지식 베이스를 만들어 사용자 권한을 지키며 인용과 함께 근거를 돌려주는 관리형 지식 계층. 색인과 검색은 Azure AI Search가 맡는다
- Q: 여러 에이전트가 함께 쓸 사내 정리 문서(SharePoint, Blob 등)로 답의 근거를 삼게 하려면 — Foundry IQ 지식 베이스를 연결한다
- Q: 지난 세션에서 말한 "유제품 알레르기"를 다음 세션에서도 기억하게 하려면 쓰는 기능 — 메모리(Memory, 미리보기)
  - 대화 기록은 한 세션 안의 단기 기억이고 메모리는 세션을 넘는 장기 기억이다

## SDK로 에이전트 클라이언트 만들기

- Q: 코드로 프롬프트 에이전트를 만들거나 새 버전을 저장하는 메서드 — `project.agents.create_version`
- Q: 프롬프트 에이전트의 모델, 지시, 도구를 담는 정의 클래스 — `PromptAgentDefinition`
- Q: 특정 에이전트에 미리 묶인 OpenAI 클라이언트를 얻는 호출 — `project.get_openai_client(agent_name=...)`
- Q: 다 쓴 에이전트 버전을 정리하는 메서드 — `project.agents.delete_version`
- Q: 아래 코드에서 빈칸 ①에 들어갈 매개변수 이름은?
  ```text
  agent = project.agents.create_version(
      agent_name="HelpDesk",
      definition=PromptAgentDefinition(
          model="gpt-5-mini",
          ①="너는 사내 IT 헬프데스크 담당이다.",
      ),
  )
  ```
  - 답: `instructions`
- Q: 아래 코드에서 빈칸 ①에 들어갈 값은?
  ```text
  openai = project.get_openai_client(agent_name="HelpDesk")
  conv = openai.conversations.create()
  r1 = openai.responses.create(conversation=①,
                               input="VPN이 안 붙어요")
  r2 = openai.responses.create(conversation=①,
                               input="재부팅도 해 봤어요")
  ```
  - 답: `conv.id`
  - 같은 대화 id를 넘겨야 두 번째 질문이 앞 맥락을 이어받는다
- Q: 아래 코드에서 빈칸 ①에 들어갈 도구 클래스는?
  ```text
  store = openai.vector_stores.create(name="Manuals")
  definition = PromptAgentDefinition(
      model="gpt-5-mini",
      instructions="올린 설명서에서 찾아 답한다.",
      tools=[①(vector_store_ids=[store.id])],
  )
  ```
  - 답: `FileSearchTool`
- Q: 함수를 실행한 뒤 결과를 돌려보내는 코드다. 빈칸 ①에 들어갈 type 값은?
  ```text
  for item in response.output:
      if item.type == "function_call":
          result = get_stock(**json.loads(item.arguments))
          outputs.append({"type": "①",
                          "call_id": item.call_id,
                          "output": json.dumps(result)})
  ```
  - 답: `function_call_output`
  - `call_id`로 어느 호출에 대한 결과인지 짝을 맞춘다
- Q: MCP 도구를 `require_approval="always"`로 붙였다. 빈칸 ①에 들어갈 항목 type은?
  ```text
  for item in response.output:
      if item.type == "①":
          ok = input("이 호출을 허용할까요? (y/N) ") == "y"
          approvals.append({"type": "mcp_approval_response",
                            "approve": ok,
                            "approval_request_id": item.id})
  ```
  - 답: `mcp_approval_request`
