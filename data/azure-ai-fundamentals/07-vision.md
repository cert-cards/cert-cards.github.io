# 영역 2 · 비전·이미지 생성 구현

## 이미지를 프롬프트에 넣기

- Q: 이미지를 따로 분석하는 비전 서비스 없이 사진에 대한 질문에 자연어로 답하게 하려면 배포할 모델 — 텍스트와 이미지를 한 요청에서 함께 받는 멀티모달 모델
- Q: Foundry 문서가 이미지 입력을 받는 OpenAI 모델로 꼽는 계열 — GPT-4o, GPT-4.1, GPT-4.5, GPT-5 시리즈, o-series 추론 모델
- Q: 코드를 쓰기 전에 비전 모델이 사진을 어떻게 해석하는지 확인해 볼 곳 — Foundry 포털의 playground (이미지를 올리고 프롬프트 입력)
- Q: 텍스트 지시와 이미지를 한 메시지로 보내려면 content를 어떤 모양으로 만드나 — 텍스트 파트와 이미지 파트를 담은 배열
  - 문자열 하나가 아니라 여러 파트로 된 multi-part 메시지
- Q: Chat Completions API에서 이미지 파트의 `type` 값 — `image_url`
- Q: Responses API에서 텍스트 파트와 이미지 파트의 `type` 값 — `input_text`, `input_image`
  - Learn 모듈은 에이전트형 앱에 맞는 Responses API로 이미지를 보내는 예를 쓴다
- Q: 이미지를 모델에 넘기는 두 방법 — 공개로 접근 가능한 HTTP(S) URL, 또는 base64로 인코딩한 이미지 데이터
- Q: 로컬 이미지 파일을 base64로 넘길 때 url 자리에 넣는 문자열 형식 — `data:<MIME 타입>;base64,<인코딩 데이터>`
  - 예: `data:image/jpeg;base64,...`
- Q: OpenAI 클라이언트의 `model` 인자에 넣는 값 — 내가 붙인 배포 이름(deployment name)
  - 원본 모델 이름(예: gpt-4.1-mini)과 다를 수 있다

## detail 설정과 입력 한도

- Q: 이미지 파트에서 모델이 그림을 얼마나 자세히 볼지 정하는 매개변수와 값 — `detail`, 값은 `low`, `high`, `auto`
- Q: `detail`을 지정하지 않았을 때 동작 — `auto`, 입력 이미지 크기를 보고 모델이 low와 high 중 고른다
- Q: `detail: low`일 때 모델이 보는 이미지 — 512x512로 줄인 저해상도 한 장
  - 응답이 빠르고 토큰을 덜 쓰지만 작은 글자나 물체 인식 정확도가 떨어질 수 있다
- Q: `detail: high`일 때 처리 방식 — 저해상도로 먼저 본 뒤 원본을 512x512 조각으로 나눠 자세히 본다
  - 조각마다 토큰을 더 써서 비용이 커진다
- Q: 영수증 사진의 작은 숫자까지 정확히 읽어야 할 때 고를 `detail` 값 — `high`
- Q: 수천 장의 사진을 실내/실외로만 빠르게 나누고 토큰을 아끼고 싶을 때 `detail` 값 — `low`
- Q: 채팅 요청 한 번에 올릴 수 있는 이미지 수 상한 — 10장
- Q: 비전 모델 입력 이미지 한 장의 최대 크기 — 20 MB

## 코드로 이미지 질문하기

- Q: 아래 Responses API 코드에서 빈칸 ①에 들어갈 파트 type은?
  ```text
  response = client.responses.create(
      model=os.environ["MODEL_NAME"],
      input=[{"role": "user", "content": [
          {"type": "input_text", "text": "사진 속 동물은?"},
          {"type": "①", "image_url": image_url},
      ]}],
  )
  print(response.output_text)
  ```
  - 답: `input_image`
  - Chat Completions라면 `image_url` 타입을 쓴다
- Q: 아래 Chat Completions 메시지에서 빈칸 ①에 들어갈 키 이름은?
  ```text
  {"type": "image_url",
   "image_url": {
       "url": image_url,
       "①": "high",
   }}
  ```
  - 답: `detail`
- Q: 아래 함수가 돌려주는 문자열에서 빈칸 ①에 들어갈 낱말은?
  ```text
  with open(path, "rb") as f:
      data = base64.b64encode(f.read()).decode("utf-8")
  return f"data:image/png;①,{data}"
  ```
  - 답: `base64`

## 이미지 생성 모델

- Q: Foundry에서 텍스트로 새 이미지를 만드는 OpenAI 모델 계열 — gpt-image 시리즈 (GPT-Image-1, GPT-Image-1-Mini, GPT-Image-1.5 등)
- Q: DALL-E 3의 현재 상태 — 2026-03-04에 퇴역, 새 배포 불가이고 기존 배포도 동작하지 않는다
  - 대신 gpt-image 시리즈를 쓴다
- Q: 품질보다 비용과 지연이 중요한 대량 이미지 생성에 맞는 모델 — GPT-Image-1-Mini
- Q: GPT-Image-1, GPT-Image-1.5를 쓰기 전에 필요한 절차 — 제한된 액세스(Limited access) 등록 신청과 승인

## 이미지 생성 매개변수

- Q: OpenAI Python SDK에서 이미지를 만드는 메서드 — `client.images.generate`
- Q: 요청 한 번에 만들 이미지 장수를 정하는 매개변수와 범위 — `n`, 1~10
- Q: GPT-Image-1 계열에서 고를 수 있는 `size` 세 가지 — `1024x1024`, `1024x1536`, `1536x1024`
- Q: GPT-Image-1과 1.5의 `quality` 값과 기본값 — `low`, `medium`, `high`, 기본 `high`
- Q: gpt-image 모델이 이미지를 돌려주는 방식 — 항상 base64(`b64_json`), URL로 받는 선택지는 없다
  - 그래서 `response_format` 매개변수를 지원하지 않는다
- Q: `output_format`으로 고를 수 있는 형식 — PNG(기본), JPEG
  - WEBP는 지원하지 않는다
- Q: 배경이 투명한 로고 이미지를 만들 때 설정 — `background="transparent"`와 `output_format="png"`
- Q: 아래 코드에서 빈칸 ①에 들어갈 응답 속성 이름은?
  ```text
  result = client.images.generate(
      model=deployment,
      prompt="수채화 풍의 등대",
      n=1,
      size="1024x1024",
  )
  png = base64.b64decode(result.data[0].①)
  ```
  - 답: `b64_json`
- Q: 아래 Responses API 코드에서 빈칸 ①에 들어갈 도구 type은?
  ```text
  response = client.responses.create(
      model=os.environ["MODEL_NAME"],
      input="파스텔 톤의 화분 든 로봇 일러스트",
      tools=[{"type": "①"}],
  )
  ```
  - 답: `image_generation`
  - 결과는 `type`이 `image_generation_call`인 출력 항목의 `result`에 base64로 들어 있다

## 이미지 편집과 안전장치

- Q: 기존 사진의 일부만 바꿀 때 호출하는 엔드포인트와 본문 형식 — `images/edits`, `multipart/form-data`
- Q: 편집 요청에서 마스크 PNG가 하는 일 — 입력과 같은 크기이고, 완전히 투명한(alpha 0) 픽셀이 수정할 영역이다
- Q: 프롬프트가 안전 시스템에 걸렸을 때 결과 — 이미지 없이 실패하고 오류 코드 `contentFilter`가 온다

## 비디오 생성

- Q: Foundry에서 직접 제공하는 비디오 생성 모델 — Sora (Sora 1, Sora 2)
  - 다른 멀티모달 모델은 영상 출력을 만들지 않는다
- Q: Sora 2가 지원하는 생성 방향 — 텍스트에서 영상, 이미지에서 영상, 영상에서 영상(remix)
  - 오디오 생성도 지원한다
- Q: 비디오 생성 REST 호출이 동기 응답이 아닌 이유와 순서 — 오래 걸리는 비동기 작업이라 작업 생성, 상태 폴링, 완료 후 MP4 다운로드 순으로 한다

## Azure Vision으로 이미지 분석

- **Azure Vision in Foundry Tools** — 미리 학습된 모델로 이미지에서 캡션, 태그, 물체 위치, 사람 위치, 글자 같은 시각 특징을 정해진 형식으로 뽑아 주는 Foundry Tool
  - 예전 이름: Azure AI Vision, Computer Vision
  - 이미지 분석 기능은 Image Analysis API로 쓴다
- Q: Image Analysis 4.0이 제공하는 기능 — Read(OCR), Caption, Dense captions, Tags, Objects, People, Smart crop
- Q: 3.2에만 있고 4.0에는 없는 기능의 예 — 브랜드 감지, 얼굴 감지, 유명인·랜드마크 인식, 성인 콘텐츠 감지, 색 구성, 이미지 유형
- Q: 사진 한 장을 완전한 문장 하나로 설명해 주는 기능 — Caption
- Q: 사진 속 여러 물체마다 따로 설명 문장과 위치 좌표를 받는 기능 — Dense captions
- Q: Tags와 Objects의 차이 — Objects는 찾은 항목마다 bounding box 좌표를 함께 준다
  - 같은 물체가 여러 개 있다는 사실도 Objects로 알 수 있다
- Q: 매장 카메라 사진에서 사람이 어디 몇 명 있는지 위치와 신뢰도만 알고 싶을 때 쓰는 4.0 기능 — People (사람 감지)
- Q: 썸네일을 정해진 가로세로 비율로 자를 때 중요한 부분의 좌표를 알려 주는 기능 — Smart crop
- Q: 캡션에 성별을 단정하는 낱말 대신 중립 표현을 쓰게 하는 옵션 — `gender_neutral_caption=True` (기본은 False)
- Q: Image Analysis API의 퇴역 예정일 — 2028-09-25 (v3.2와 v4.0 모두, 지금은 deprecated)
- Q: Image Analysis에서 옮겨 갈 곳 (OCR, 얼굴, 그 밖의 분석) — OCR은 Document Intelligence Read, 얼굴은 Face API, 나머지는 Foundry의 GPT 모델이나 Content Understanding
- Q: Python에서 Image Analysis를 쓰는 패키지와 클라이언트 클래스 — `azure-ai-vision-imageanalysis`, `ImageAnalysisClient`
- Q: 아래 코드에서 빈칸 ①에 들어갈 VisualFeatures 멤버는? (캡션과 OCR을 함께 요청)
  ```text
  client = ImageAnalysisClient(
      endpoint=os.environ["VISION_ENDPOINT"],
      credential=AzureKeyCredential(os.environ["VISION_KEY"]),
  )
  result = client.analyze_from_url(
      image_url=url,
      visual_features=[VisualFeatures.①, VisualFeatures.READ],
  )
  print(result.caption.text)
  ```
  - 답: `CAPTION`

## Face 서비스의 제한

- Q: Face 서비스를 쓸 수 있는 고객 — 자격 심사를 통과한 Microsoft 관리 고객과 파트너 (Face Recognition intake form으로 신청)
- Q: Microsoft가 Face에서 퇴역시킨 속성 추론 두 가지 — 감정(emotion), 성별(gender)
  - 나이, 미소, 수염, 머리카락, 화장은 제한된 속성이다
- Q: Face 검증(verification)과 식별(identification)의 차이 — 검증은 두 얼굴이 같은 사람인지 보는 1:1, 식별은 저장된 집합에서 찾는 1:N

## 시나리오에 맞는 선택

- Q: 고객이 올린 차량 파손 사진을 보고 보험사에 무엇을 알려야 할지 자연어로 조언해 주는 앱 — 비전을 지원하는 GPT 모델에 이미지와 질문을 함께 보낸다
- Q: 사진마다 물체 이름과 좌표, 신뢰도를 항상 같은 형식으로 받아 DB에 넣어야 할 때 — Azure Vision Image Analysis (Objects)
- Q: 제품 설명 문장만으로 광고용 새 이미지를 만들어야 할 때 — gpt-image 시리즈 이미지 생성 모델
- Q: 짧은 홍보용 영상 클립을 텍스트 프롬프트로 만들어야 할 때 — Sora 비디오 생성 모델
