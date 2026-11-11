# 영역 2 · 텍스트·음성 구현

## Foundry에서 텍스트 분석 고르기

- **Azure Language in Foundry Tools** — 언어 감지, 개체 인식, PII 감지 같은 자연어 처리 기능을 작업별 전용 분석기로 돌려 정해진 구조의 결과를 주는 Foundry Tool
  - 예전 이름: Azure Cognitive Service for Language, Text Analytics
  - Foundry 리소스 하나로 접근한다. Language 리소스를 따로 만들지 않아도 된다
- Q: Foundry가 텍스트 분석에 내놓는 두 가지 길 — 프롬프트로 여러 작업을 처리하는 범용 AI 모델, 작업마다 구조화된 일정한 결과를 주는 Azure Language
- Q: 같은 리뷰로 감정 분석을 두 번 요청했더니 범용 모델의 답 표현과 형식이 조금씩 달랐다. 이유는 — 모델이 확률적으로 글을 생성하기 때문
- Q: 언어 코드, 신뢰도, 가린 텍스트처럼 매번 같은 구조의 값이 필요한 자동화 파이프라인에 맞는 쪽 — Azure Language (SDK)
- Q: 새 Foundry 포털에서 언어 감지와 PII 가리기를 코드 없이 시험하는 곳 — Build 페이지의 AI 서비스 목록에서 여는 Language playground
  - Learn 단원은 Build, Models, AI services 탭 순서로, 실습 지침은 Build의 Services 페이지로 안내한다
- Q: Azure Language가 새 개발에 권하는 core 기능 — PII 감지, 언어 감지, NER(사전 구축, Custom), Text analytics for health
- Q: legacy로 분류된 핵심 구절 추출, 감정 분석, 요약의 퇴역일과 권하는 이전 대상 — 2029-03-31, Foundry 모델
  - 개체 연결은 2028-09-01 퇴역이고 NER이나 Foundry 모델로 옮기라고 안내한다

## Azure Language SDK로 앱 만들기

- Q: Azure Language의 Python 패키지와 클라이언트 클래스 — `azure-ai-textanalytics`, `TextAnalyticsClient`
- Q: 아래 코드에서 빈칸 ①에 들어갈 클래스 이름은?
  ```text
  from azure.core.credentials import ①
  from azure.ai.textanalytics import TextAnalyticsClient

  client = TextAnalyticsClient(
      endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
      credential=①(os.environ["API_KEY"]),
  )
  ```
  - 답: `AzureKeyCredential`
- Q: 결과 리스트에서 처리에 실패한 문서를 걸러 낼 때 보는 속성 — `is_error`
- Q: 아래 코드에서 빈칸 ①에 들어갈 속성 이름은? (출력 예: es)
  ```text
  result = client.detect_language(["¡Hola! Me llamo Josefina."])[0]
  print(result.primary_language.name)
  print(result.primary_language.①)
  print(result.primary_language.confidence_score)
  ```
  - 답: `iso6391_name`
- Q: 고객 메모에서 전화번호와 주소를 찾아 가리려 할 때 부르는 메서드 — `recognize_pii_entities`
- Q: 아래 코드에서 빈칸 ①에 들어갈 속성 이름은? (개인정보가 가려진 문장을 출력)
  ```text
  result = client.recognize_pii_entities([text])[0]
  print(result.①)
  for entity in result.entities:
      print(entity.text, entity.category, entity.confidence_score)
  ```
  - 답: `redacted_text`
- Q: 사람, 장소, 조직, 날짜를 범주별로 뽑을 때 부르는 메서드 — `recognize_entities`
- Q: 글에 나온 이름마다 Wikipedia 링크를 받을 때 부르는 메서드 — `recognize_linked_entities`
- Q: 기사마다 주요 화제를 낱말 목록으로 받을 때 부르는 메서드와 결과 속성 — `extract_key_phrases`, `key_phrases`
- Q: 아래 코드에서 빈칸 ①에 들어갈 매개변수 이름은? (측면별 평가까지 받기)
  ```text
  result = client.analyze_sentiment(reviews, ①=True)
  for doc in result:
      if not doc.is_error:
          print(doc.sentiment, doc.confidence_scores.positive)
  ```
  - 답: `show_opinion_mining`
- Q: 의료 문서 분석이나 여러 분석을 한 번에 돌리는 메서드 이름의 공통점 — `begin_`으로 시작하는 장기 실행 작업이라 poller를 받고 `result()`로 끝나기를 기다린다
  - 예: `begin_analyze_healthcare_entities`, `begin_analyze_actions`

## 에이전트에 Azure Language 붙이기

- **Azure Language MCP server** — 개체 인식, 감정 분석, 언어 감지 같은 Azure Language 기능을 MCP 표준 도구로 내놓아 에이전트가 불러 쓰게 하는 관리형 서버
- Q: Azure Language MCP server를 쓸 수 있는 두 형태 — Foundry Tool Catalog의 원격 서버, 직접 띄우는 로컬 서버
- Q: 에이전트에 언어 모델이 이미 있는데도 Azure Language 도구를 붙이는 이유 — 일관되고 구조화된 분석 결과가 필요해서 (예: 언어별 티켓 라우팅, PII 가리기)
- Q: playground에서 에이전트에 Azure Language 도구를 연결할 때 연결 설정에 넣는 값 — Foundry 리소스 이름

## 음성으로 묻고 멀티모달 모델이 답하기

- Q: chat completions로 오디오를 입력받아 텍스트와 음성으로 답하는 Foundry 모델 — `gpt-audio`, `gpt-audio-mini`
- Q: 아래 오디오 요청에서 빈칸 ①에 들어갈 content 파트 type은?
  ```text
  messages=[{"role": "user", "content": [
      {"type": "text", "text": "이 녹음의 요청 사항을 정리해 줘"},
      {"type": "①",
       "①": {"data": encoded_wav, "format": "wav"}},
  ]}]
  ```
  - 답: `input_audio`
  - 오디오 파일은 base64 문자열로 바꿔 `data`에 넣는다
- Q: 모델이 텍스트에 더해 음성으로도 답하게 하려고 요청에 넣는 두 매개변수 — `modalities=["text", "audio"]`, `audio={"voice": ..., "format": ...}`
- Q: 오디오 응답에서 모델이 말한 내용의 글과 음성 데이터가 있는 곳 — `message.audio.transcript`, `message.audio.data`(base64)
- Q: 사용자가 말하면 지연 없이 바로 말로 답하는 대화를 모델과 직접 주고받을 때 쓰는 API — GPT Realtime API (`gpt-realtime` 계열 모델)
- Q: Realtime API의 세 연결 방식과 쓰임 — 브라우저나 모바일 앱은 WebRTC, 서버 간 연결은 WebSocket, 전화 연동은 SIP
- Q: Realtime 세션을 연 뒤 보통 처음 보내 목소리, 지시, 턴 감지를 정하는 이벤트 — `session.update`
- Q: Realtime API `turn_detection`의 기본값과 동작 — `server_vad`, 침묵 구간으로 말이 끝났음을 감지하면 자동으로 응답을 만든다
- Q: `semantic_vad`가 `server_vad`와 다른 점 — 침묵 길이 대신 사용자가 한 말의 내용으로 발화 끝을 판단해 말을 덜 끊는다

## Azure Speech in Foundry Tools로 앱 만들기

- **Azure Speech in Foundry Tools** — 말소리를 글로 바꾸고, 글을 말소리로 읽고, 말을 번역하고, 실시간 음성 대화를 처리하는 기능을 Foundry 리소스로 제공하는 Foundry Tool
  - Speech SDK, Speech CLI, REST API로 쓴다
- Q: 코드 없이 음성 인식을 시험하는 Foundry playground 이름과 입력 방법 — Azure Speech - Speech to Text, 오디오 파일을 올리거나 직접 녹음한다
- Q: Speech SDK의 Python 패키지 이름 — `azure-cognitiveservices-speech`
  - 코드에서는 보통 `import azure.cognitiveservices.speech as speechsdk`로 불러온다
- Q: Speech SDK에서 키와 엔드포인트를 담는 설정 객체 — `SpeechConfig(subscription=키, endpoint=엔드포인트)`
- Q: 음성 인식 언어를 정하는 `SpeechConfig` 속성과 정하지 않았을 때 값 — `speech_recognition_language`, `en-US`
- Q: 마이크 대신 저장된 WAV 파일을 인식하려면 — `AudioConfig(filename="파일.wav")`로 오디오 입력을 바꾼다
  - 마이크는 `AudioConfig(use_default_microphone=True)`
- Q: `recognize_once_async()`가 한 번에 받아 적는 범위 — 발화 하나 (최대 30초, 또는 침묵이 나올 때까지)
- Q: 아래 코드에서 빈칸 ①에 들어갈 `ResultReason` 멤버는? (인식에 성공한 경우)
  ```text
  recognizer = speechsdk.SpeechRecognizer(
      speech_config=speech_config, audio_config=audio_config)
  result = recognizer.recognize_once_async().get()
  if result.reason == speechsdk.ResultReason.①:
      print("Recognized:", result.text)
  ```
  - 답: `RecognizedSpeech`
- Q: 인식 결과의 `reason`이 `NoMatch`일 때 뜻 — 말소리를 알아듣지 못했다 (`no_match_details`로 이유 확인)
- Q: 음성 메일처럼 긴 오디오를 계속 받아 적을 때 쓰는 메서드 짝 — `start_continuous_recognition()`, `stop_continuous_recognition()`
- Q: 연속 인식에서 중간 결과와 확정 결과를 받는 이벤트 — `recognizing`(중간), `recognized`(확정)
- Q: 텍스트를 말소리로 바꾸는 객체와 메서드 — `SpeechSynthesizer`, `speak_text_async(text).get()`
- Q: 아래 코드에서 빈칸 ①에 들어갈 매개변수 이름은? (합성 결과를 파일로 저장)
  ```text
  audio_config = speechsdk.audio.AudioOutputConfig(①="greeting.wav")
  synthesizer = speechsdk.SpeechSynthesizer(
      speech_config=speech_config, audio_config=audio_config)
  result = synthesizer.speak_text_async("안녕하세요").get()
  ```
  - 답: `filename`
- Q: 아래 코드에서 빈칸 ①에 들어갈 `SpeechConfig` 속성 이름은?
  ```text
  speech_config = speechsdk.SpeechConfig(
      subscription=os.environ["FOUNDRY_KEY"],
      endpoint=os.environ["ENDPOINT"])
  speech_config.① = "en-US-Ava:DragonHDLatestNeural"
  synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
  ```
  - 답: `speech_synthesis_voice_name`
- Q: `es-ES` 목소리로 영어 문장을 합성하면 — 영어로 말하되 스페인어 억양이 섞인다 (뉴럴 목소리는 모두 다국어)
  - 고른 목소리가 입력 언어를 아예 못 말하면 오디오가 만들어지지 않는다
- Q: `speech_synthesis_voice_name`과 `speech_synthesis_language`를 둘 다 정했을 때 말하는 목소리 — voice name으로 정한 목소리 (언어 설정은 무시된다)
  - SSML 안에 voice를 적으면 SSML이 둘 다보다 앞선다
- Q: SSML 문서를 합성할 때 쓰는 메서드 — `speak_ssml_async`
- Q: SSML 문서의 루트 요소와 목소리를 정하는 요소 — `<speak>`, `<voice name="...">`

## Voice Live와 음성 에이전트

- **Voice Live API** — 음성 인식, 생성형 모델의 추론, 음성 합성을 따로 잇지 않고 하나로 묶어 실시간 음성 대화를 처리하는 Azure Speech의 완전 관리형 API
- Q: Voice Live로 Python 앱을 만들 때 설치하는 패키지 — `azure-ai-voicelive`
  - `pyaudio`, `python-dotenv`, `azure-identity`도 함께 필요하다
- Q: Voice Live solution을 playground에서 새로 만들 때 반드시 고를 것 — 에이전트가 쓸 생성형 AI 모델
  - Voice Live는 이 모델을 자체 음향 모델과 함께 써서 대화한다
- Q: Foundry 에이전트 playground에서 음성 설정을 에이전트 정의 안에 넣어 클라이언트 코드를 줄이는 옵션 — Voice mode
- Q: 음성 에이전트가 갖추는 세 능력 — 듣기(말이 끝났는지 감지), 추론(모델, 지시, 도구), 말하기(고른 목소리로 전달)
- Q: 네이티브 speech-to-speech 모델과 텍스트 모델의 음성 처리 차이 — 앞은 오디오를 바로 다루고, 뒤는 음성 인식, 텍스트 응답 생성, 음성 합성을 차례로 거친다
- Q: 음성 에이전트 Advanced settings의 두 가지 turn detection — Azure semantic(말의 의미로 판단), Basic(소리 크기와 침묵 시간으로 판단)
- Q: Basic turn detection에서 Silence duration을 길게 잡으면 — 말 중간의 쉼에서 덜 끊기지만 말을 마친 뒤 응답이 늦어진다
- Q: 음성 에이전트의 답이 너무 길어 귀로 따라가기 어려울 때 고칠 곳 — Instructions의 응답 길이 지침 (목소리를 바꿔서는 해결되지 않는다)
- Q: 이미 만든 에이전트의 Interaction mode를 Text에서 Voice로 바꿀 수 있나 — 없다, 음성 에이전트를 새로 만든다
