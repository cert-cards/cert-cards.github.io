# scikit-learn · 평가지표

> sklearn.metrics의 분류 지표(정확도, 정밀도, 재현율, F1, AUC, 혼동행렬)와 회귀 지표(MSE, RMSE, MAE, R², MSLE, MAPE), 그리고 예측을 제출 CSV로 만드는 마지막 단계를 다룬다.

## 지표 함수 공통

- Q: sklearn 지표 함수의 인자 순서 — 정답 먼저, 예측 나중 (`f(y_true, y_pred)`)
  - MSE, MAE처럼 대칭인 지표는 바꿔도 같지만 R², AUC, 정밀도, 재현율은 값이 달라지거나 오류가 난다.
- Q: 분류 지표 중 0/1 라벨이 아니라 확률(점수)을 받는 것 — `roc_auc_score`(그리고 `log_loss`)
  - 정확도, 정밀도, 재현율, F1, 혼동행렬 함수는 라벨을 받는다.
- Q: 평가지표 이름으로 분류인지 회귀인지 가르는 법 — AUC, F1, 정확도, 정밀도, 재현율이면 분류 / RMSE, MAE, MSE, R², MAPE면 회귀

## accuracy_score

- Q: `accuracy_score(y_true, y_pred)`가 돌려주는 것 — 맞힌 비율(0~1 실수)
  - `normalize=False`를 주면 비율 대신 맞힌 개수를 돌려준다.
- Q: 클래스가 95:5로 치우친 데이터에서 정확도가 0.95라면 — 전부 다수 클래스로 찍어도 나오는 값이라 성능을 말해 주지 못한다
  - 이럴 때 문제는 보통 F1이나 AUC로 채점한다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import accuracy_score
  y_true = ['a', 'b', 'a', 'c']
  y_pred = ['a', 'a', 'a', 'c']
  print(accuracy_score(y_true, y_pred), accuracy_score(y_true, y_pred, normalize=False))
  ```
  - 답: `0.75 3.0`
  - 문자열 라벨도 그대로 비교한다. `normalize=False`의 개수도 실수로 나온다.

## confusion_matrix

- Q: `confusion_matrix(y_true, y_pred)`의 행과 열 — 행이 실제, 열이 예측
  - 순서는 라벨을 정렬한 순서다. 이진 0/1이면 [[TN, FP], [FN, TP]]다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import confusion_matrix
  y_true = [1, 0, 1, 1, 0, 0, 1, 0]
  y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
  tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
  print(tn, fp, fn, tp)
  ```
  - 답: `3 1 1 3`
  - 라벨 순(0, 1)이라 펼치면 TN, FP, FN, TP 순이다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import confusion_matrix
  y_true = [1, 0, 1, 1, 0, 0, 1, 0]
  y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
  print(confusion_matrix(y_true, y_pred, labels=[1, 0]).tolist())
  ```
  - 답: `[[3, 1], [1, 3]]`
  - `labels`로 순서를 바꾸면 첫 행·첫 열이 1이 된다. 이때 ravel 순서는 TP, FN, FP, TN이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.metrics import confusion_matrix
  y_true = [0, 1, 2, 2, 1, 0]
  y_pred = [0, 2, 2, 2, 1, 1]
  cm = confusion_matrix(y_true, y_pred)
  print(cm.shape, np.trace(cm), cm[1].tolist())
  ```
  - 답: `(3, 3) 4 [0, 1, 1]`
  - 대각선 합이 맞힌 개수다. `cm[1]`은 실제 1인 행들이 어떻게 예측됐는지다.

## precision_score · recall_score

- Q: `precision_score`가 계산하는 것 — 양성이라고 예측한 것 중 실제 양성의 비율, TP / (TP + FP)
- Q: `recall_score`가 계산하는 것 — 실제 양성 중 모델이 양성으로 맞힌 비율, TP / (TP + FN)
- Q: precision_score, recall_score, f1_score의 `pos_label` 기본값 — `1`
  - 라벨이 문자열이면 `pos_label='yes'`처럼 양성을 직접 지정해야 한다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
  y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
  y_pred = [1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
  print(accuracy_score(y_true, y_pred), round(precision_score(y_true, y_pred), 2))
  print(recall_score(y_true, y_pred), round(f1_score(y_true, y_pred), 2))
  ```
  - 답:
    ```text
    0.7 0.67
    0.5 0.57
    ```
  - TP 2, FN 2, FP 1, TN 5. 정밀도 2/3, 재현율 2/4다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import precision_score
  y_true = ['y', 'n', 'y', 'n']
  y_pred = ['y', 'y', 'n', 'n']
  try:
      precision_score(y_true, y_pred)
  except Exception as e:
      print(type(e).__name__)
  print(precision_score(y_true, y_pred, pos_label='y'))
  ```
  - 답:
    ```text
    ValueError
    0.5
    ```
  - 기본 `pos_label=1`이 라벨 안에 없어서 오류다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import precision_score
  print(precision_score([0, 1, 0], [0, 0, 0], zero_division=0))
  ```
  - 답: `0.0`
  - 양성 예측이 하나도 없으면 분모가 0이다. `zero_division`으로 그때 돌려줄 값을 정한다(기본은 경고와 함께 0).

## f1_score와 average

- Q: F1 점수의 식 — 2 × 정밀도 × 재현율 / (정밀도 + 재현율)
  - 정밀도와 재현율의 조화평균이라 둘 중 낮은 쪽에 끌려간다.
- Q: f1_score, precision_score, recall_score의 `average` 기본값 — `'binary'`
  - 이진 분류에서 pos_label 클래스 하나의 점수만 낸다. 다중 분류에서는 오류가 난다.
- Q: `average='macro'`와 `'weighted'`의 차이 — macro는 클래스별 점수의 단순 평균, weighted는 클래스별 실제 개수(support)로 가중한 평균
- Q: 다중 분류에서 `average='micro'`인 F1이 같아지는 값 — 정확도
  - 전체 TP, FP, FN을 모아서 한 번에 계산하기 때문이다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import f1_score
  y_true = [0, 1, 2, 2, 1, 0]
  y_pred = [0, 2, 2, 2, 1, 1]
  try:
      f1_score(y_true, y_pred)
  except Exception as e:
      print(type(e).__name__)
  print(round(f1_score(y_true, y_pred, average='macro'), 2))
  ```
  - 답:
    ```text
    ValueError
    0.66
    ```
  - 기본 `'binary'`는 다중 분류에서 쓸 수 없다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import f1_score
  y_true = [0, 1, 2, 2, 1, 0]
  y_pred = [0, 2, 2, 2, 1, 1]
  print(f1_score(y_true, y_pred, average=None).round(2).tolist())
  ```
  - 답: `[0.67, 0.5, 0.8]`
  - `average=None`이면 클래스별 F1을 배열로 준다. 이 셋의 단순 평균이 macro(0.66)다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import f1_score, accuracy_score
  y_true = [0, 1, 2, 2, 1, 0]
  y_pred = [0, 2, 2, 2, 1, 1]
  print(round(f1_score(y_true, y_pred, average='micro'), 4), round(accuracy_score(y_true, y_pred), 4))
  ```
  - 답: `0.6667 0.6667`

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import f1_score
  y_true = [0, 0, 0, 0, 1, 1, 2]
  y_pred = [0, 0, 0, 1, 1, 2, 2]
  print(round(f1_score(y_true, y_pred, average='macro'), 3))
  print(round(f1_score(y_true, y_pred, average='weighted'), 3))
  ```
  - 답:
    ```text
    0.675
    0.728
    ```
  - 개수가 많은 클래스 0의 F1이 높아 weighted가 macro보다 크다.

## classification_report

- Q: `classification_report(y_true, y_pred)`가 돌려주는 것 — 클래스별 precision, recall, f1-score, support를 담은 문자열
  - `print`로 본다. 값을 꺼내 쓰려면 `output_dict=True`로 사전을 받는다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import classification_report
  r = classification_report([0, 1, 1, 0], [0, 1, 0, 0], output_dict=True)
  print(list(r.keys()))
  print(r['1']['recall'], r['accuracy'])
  ```
  - 답:
    ```text
    ['0', '1', 'accuracy', 'macro avg', 'weighted avg']
    0.5 0.75
    ```
  - 클래스 키는 문자열이다(`r[1]`이 아니라 `r['1']`).

## roc_auc_score

- Q: roc_auc_score의 두 번째 인자로 넣는 것 — 양성 클래스의 확률이나 점수(`predict_proba(X)[:, 1]`)
  - `predict`의 0/1을 넣으면 순위 정보가 사라져 AUC가 대개 낮아진다.
- Q: AUC 값 0.5의 뜻 — 무작위로 찍는 수준
  - 1에 가까울수록 양성에 더 높은 점수를 매긴 것이다.
- Q: 다중 분류 AUC를 roc_auc_score로 구할 때 필요한 것 — 클래스별 확률 전체(n × k 배열)와 `multi_class='ovr'`(또는 `'ovo'`)

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import roc_auc_score
  y_true = [0, 0, 1, 1, 0, 1]
  score = [0.2, 0.6, 0.55, 0.9, 0.1, 0.4]
  label = [1 if s >= 0.5 else 0 for s in score]
  print(round(roc_auc_score(y_true, score), 2), round(roc_auc_score(y_true, label), 2))
  ```
  - 답: `0.78 0.67`
  - 같은 예측이어도 확률을 넣느냐 0/1을 넣느냐에 따라 AUC가 다르다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import roc_auc_score
  try:
      roc_auc_score([0.2, 0.6, 0.55], [0, 0, 1])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 인자 순서가 바뀌어 정답 자리에 실수가 들어갔다. `roc_auc_score(y_true, y_score)` 순이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.metrics import roc_auc_score
  y = [0, 1, 2, 0, 1, 2]
  p = np.array([[.6, .3, .1], [.2, .5, .3], [.1, .2, .7],
                [.3, .4, .3], [.5, .3, .2], [.2, .2, .6]])
  try:
      roc_auc_score(y, p)
  except Exception as e:
      print(type(e).__name__)
  print(round(roc_auc_score(y, p, multi_class='ovr'), 4))
  ```
  - 답:
    ```text
    ValueError
    0.8958
    ```
  - 다중 분류 확률을 넘길 때는 `multi_class`를 꼭 지정한다. 행마다 확률의 합은 1이어야 한다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import roc_auc_score
  try:
      roc_auc_score([1, 1, 1], [0.2, 0.3, 0.4])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 정답에 클래스가 하나뿐이면 AUC가 정의되지 않는다. 검증 폴드가 너무 작을 때 생긴다.

## mean_squared_error · root_mean_squared_error

- Q: RMSE를 버전과 상관없이 구하는 코드 — `np.sqrt(mean_squared_error(y_true, y_pred))`
  - `root_mean_squared_error`는 scikit-learn 1.4부터 있다.
- Q: `mean_squared_error(y_true, y_pred, squared=False)`의 상태 — 1.4부터 폐기 예정 경고가 나지만 1.5에서는 RMSE를 돌려준다. 1.6에서 없어졌다
  - 버전에 기대지 않으려면 `np.sqrt`나 `root_mean_squared_error`를 쓴다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.metrics import mean_squared_error, mean_absolute_error
  y_true = [3, 5, 2, 7]
  y_pred = [2, 5, 4, 8]
  mse = mean_squared_error(y_true, y_pred)
  print(mse, round(np.sqrt(mse), 2), mean_absolute_error(y_true, y_pred))
  ```
  - 답: `1.5 1.22 1.0`
  - 오차 -1, 0, 2, 1. 제곱 평균이 1.5, 절댓값 평균이 1.0이다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import root_mean_squared_error, mean_squared_error
  y_true = [3, 5, 2, 7]
  y_pred = [2, 5, 4, 8]
  print(round(root_mean_squared_error(y_true, y_pred), 4))
  print(round(mean_squared_error(y_true, y_pred, squared=False), 4))
  ```
  - 답:
    ```text
    1.2247
    1.2247
    ```
  - 둘째 줄은 이 버전(1.5)에서 경고만 내고 같은 값을 준다.

- Q: 빈칸에 들어갈 것은? (검증 RMSE를 출력한다)
  ```text
  import numpy as np
  from sklearn.metrics import mean_squared_error
  pred = model.predict(X_val)
  print(np.①(mean_squared_error(②, pred)))
  ```
  - 답: ① `sqrt` ② `y_val`

## mean_absolute_error

- Q: `mean_absolute_error`가 계산하는 것 — 오차 절댓값의 평균
- Q: MAE와 RMSE 중 큰 오차 하나에 더 크게 반응하는 쪽 — RMSE
  - 오차를 제곱해서 평균하므로 큰 오차가 더 무겁게 들어간다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import mean_absolute_error, root_mean_squared_error
  y_true = [10, 10, 10, 10]
  y_pred = [11, 9, 11, 17]
  print(mean_absolute_error(y_true, y_pred), round(root_mean_squared_error(y_true, y_pred), 2))
  ```
  - 답: `2.5 3.61`
  - 오차 7 하나가 RMSE를 MAE보다 훨씬 크게 끌어올린다.

## r2_score

- Q: r2_score가 1, 0, 음수일 때의 뜻 — 1은 완벽, 0은 평균만 찍은 수준, 음수는 평균보다 못함

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import r2_score
  y_true = [1, 2, 3, 4]
  print(r2_score(y_true, [2.5, 2.5, 2.5, 2.5]), r2_score(y_true, [4, 3, 2, 1]))
  ```
  - 답: `0.0 -3.0`
  - R²는 0~1 사이로 묶여 있지 않다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import r2_score
  y_true = [1, 2, 3, 4]
  y_pred = [1, 2, 3, 8]
  print(round(r2_score(y_true, y_pred), 2), round(r2_score(y_pred, y_true), 2))
  ```
  - 답: `-2.2 0.45`
  - R²는 정답 쪽 분산으로 나누므로 인자 순서를 바꾸면 값이 달라진다.

## mean_squared_log_error

- Q: mean_squared_log_error가 계산하는 것 — log(1 + 정답)과 log(1 + 예측)의 차이를 제곱해 평균
  - 제곱근을 씌운 RMSLE는 `np.sqrt(...)`나 `root_mean_squared_log_error`(1.4부터)로 구한다.
- Q: 이 버전(1.5)에서 `mean_squared_log_error`가 ValueError를 내는 경우 — 예측값이나 정답에 음수가 하나라도 있을 때
  - 1.6부터는 -1 이하일 때만 오류다. 회귀 예측을 `np.clip(pred, 0, None)`으로 0 아래를 잘라 두면 안전하다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.metrics import mean_squared_log_error
  y_true = [9, 99, 999]
  y_pred = [19, 99, 499]
  print(round(np.sqrt(mean_squared_log_error(y_true, y_pred)), 3))
  ```
  - 답: `0.566`
  - log(1 + x) 차이가 각각 log 2, 0, log 2라 큰 값과 작은 값의 오차를 같은 비율로 본다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.metrics import mean_squared_log_error
  y_true = [1, 2, 3]
  pred = np.array([-0.5, 2.0, 3.0])
  try:
      mean_squared_log_error(y_true, pred)
  except Exception as e:
      print(type(e).__name__)
  print(round(mean_squared_log_error(y_true, np.clip(pred, 0, None)), 4))
  ```
  - 답:
    ```text
    ValueError
    0.1602
    ```
  - 음수 예측을 0으로 잘라 내면 계산된다.

## mean_absolute_percentage_error

- Q: `mean_absolute_percentage_error`가 돌려주는 값의 단위 — 비율(0.1이 10%)
  - 100을 곱한 퍼센트가 아니다.
- Q: MAPE를 쓰면 안 되는 정답 값 — 0(또는 0에 아주 가까운 값)
  - 정답으로 나누므로 0이 있으면 값이 터무니없이 커진다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import mean_absolute_percentage_error
  print(round(mean_absolute_percentage_error([100, 200], [110, 180]), 4))
  ```
  - 답: `0.1`
  - 각 오차율 10/100 = 0.1, 20/200 = 0.1의 평균이다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import mean_absolute_percentage_error
  print(mean_absolute_percentage_error([0, 200], [10, 180]) > 1e10)
  ```
  - 답: `True`
  - 정답 0은 아주 작은 수로 바꿔 나누므로 오류 대신 거대한 값이 나온다.

## 제출 파일 만들기

- Q: 예측을 마친 뒤 가장 먼저 대조할 두 숫자 — 예측값 개수와 test 행 수
  - 둘이 다르면 test 행을 지웠거나 인덱스가 어긋난 것이다.
- Q: 제출 CSV를 저장할 때 빠뜨리면 안 되는 인자 — `index=False`
  - 빠뜨리면 이름 없는 인덱스 열이 첫 열로 들어가 열 개수가 달라진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  sub = pd.DataFrame({'id': [101, 102, 103], 'pred': [0, 1, 1]})
  print(sub.to_csv(index=False))
  ```
  - 답:
    ```text
    id,pred
    101,0
    102,1
    103,1
    ```
  - 경로를 주지 않으면 파일 대신 CSV 문자열을 돌려준다. 저장 전에 모양을 보는 데 쓸 수 있다.

- Q: 출력 결과는?
  ```text
  import io
  import pandas as pd
  sub = pd.DataFrame({'pred': [0.2, 0.9]})
  print(sub.to_csv().splitlines()[0])
  print(pd.read_csv(io.StringIO(sub.to_csv())).columns.tolist())
  ```
  - 답:
    ```text
    ,pred
    ['Unnamed: 0', 'pred']
    ```
  - 인덱스가 저장되면 다시 읽을 때 `Unnamed: 0` 열이 생긴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  test_id = pd.Series([501, 502], index=[4, 5])
  pred = pd.Series([1, 0])
  sub = pd.DataFrame({'id': test_id, 'pred': pred})
  print(len(sub), sub['pred'].isna().sum())
  ```
  - 답: `4 2`
  - Series끼리는 인덱스로 맞춰 붙는다. 예측은 배열 그대로(`model.predict` 결과) 넣거나 `test_id.values`를 쓴다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  test_id = pd.Series([501, 502, 503], index=[4, 5, 6])
  proba = np.array([[0.7, 0.3], [0.2, 0.8], [0.5, 0.5]])
  sub = pd.DataFrame({'id': test_id.values, 'prob': proba[:, 1]})
  print(sub.shape, sub['prob'].tolist())
  ```
  - 답: `(3, 2) [0.3, 0.8, 0.5]`
  - `.values`로 인덱스를 떼고 넣으면 행 순서대로 붙는다. AUC 채점이면 이렇게 양성 확률을 낸다.

- Q: 빈칸에 들어갈 것은? (예측을 지정한 이름으로 저장한다)
  ```text
  import pandas as pd
  pred = model.predict(X_test)
  sub = pd.DataFrame({'pred': pred})
  sub.①('result.csv', ②=False)
  ```
  - 답: ① `to_csv` ② `index`
  - 파일 이름과 열 이름은 문제 지시문을 그대로 따른다.
