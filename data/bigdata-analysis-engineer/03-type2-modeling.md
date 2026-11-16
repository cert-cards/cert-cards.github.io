# 작업형 2 · 모델링과 제출

> 작업형 2유형은 train으로 모델을 만들고 test 예측을 CSV로 내는 문제다. 제출 파일 이름, 열 이름, 형식은 문제 지시문을 그대로 따른다. 코드는 전부 직접 만든 작은 데이터이고, 답은 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다. 모델 점수는 버전마다 달라서 다루지 않는다.

## 읽기와 분리

- Q: train에서 입력 X를 만들 때 빼야 하는 두 종류의 열 — 타깃 열과 ID 열
  - ID는 예측에 쓰지 않지만 제출 파일에 들어가므로 test의 ID는 따로 보관한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'id': [1, 2, 3, 4], 'age': [20, 35, 41, 28],
                        'city': ['A', 'B', 'A', 'C'], 'target': [0, 1, 1, 0]})
  test = pd.DataFrame({'id': [5, 6], 'age': [33, 50], 'city': ['B', 'A']})
  y = train['target']
  X = train.drop(columns=['id', 'target'])
  test_id = test.pop('id')
  print(list(X.columns), list(test.columns), test_id.tolist())
  ```
  - 답: `['age', 'city'] ['age', 'city'] [5, 6]`
  - `pop`은 열을 꺼내 돌려주면서 원본에서 지운다. X와 test의 열이 같아야 predict가 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'age': [20, 35, 41], 'city': ['A', 'B', 'A'],
                     'score': [3.5, 4.0, 2.5], 'job': ['x', 'y', 'y']})
  print(df.select_dtypes(include='object').columns.tolist())
  print(df.select_dtypes(exclude='object').columns.tolist())
  ```
  - 답:
    ```text
    ['city', 'job']
    ['age', 'score']
    ```
  - 인코딩할 범주형 열과 그대로 둘 수치형 열을 나눌 때 쓴다.

- Q: 예측을 마친 뒤 가장 먼저 대조할 두 숫자 — 예측값 개수와 test 행 수
  - 둘이 다르면 test 행을 지웠거나 인덱스가 어긋난 것이다.

## 결측치

- Q: test의 결측을 채우는 기준값은 어디서 구하나 — train에서 구한 값(평균, 중앙값, 최빈값)
  - test 자신의 통계로 채우면 학습 때와 다른 기준이 섞인다. 결측 개수는 `isnull().sum()`으로 train과 test 둘 다 본다.
  - test 행은 `dropna`로 지우지 않는다. 제출 행 수가 모자라게 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'x': [10.0, None, 30.0, 20.0]})
  test = pd.DataFrame({'x': [None, 50.0, None]})
  m = train['x'].mean()
  train['x'] = train['x'].fillna(m)
  test['x'] = test['x'].fillna(m)
  print(m, test['x'].tolist())
  ```
  - 답: `20.0 [20.0, 50.0, 20.0]`
  - `mean()`은 NaN을 빼고 계산한다. test 평균(50)으로 채웠다면 기준이 달라진다.

## 인코딩

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'city': ['A', 'B', 'C', 'A']})
  test = pd.DataFrame({'city': ['A', 'B']})
  tr = pd.get_dummies(train)
  te = pd.get_dummies(test)
  print(tr.shape[1], te.shape[1])
  print(list(te.columns))
  ```
  - 답:
    ```text
    3 2
    ['city_A', 'city_B']
    ```
  - 따로 인코딩하면 test에 없는 범주(C)의 열이 빠져 predict에서 열 불일치 오류가 난다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'city': ['A', 'B', 'C', 'A'], 'x': [1, 2, 3, 4]})
  test = pd.DataFrame({'city': ['A', 'D'], 'x': [5, 6]})
  all_ = pd.get_dummies(pd.concat([train, test]))
  tr = all_.iloc[:len(train)]
  te = all_.iloc[len(train):]
  print(tr.shape, te.shape)
  print(list(te.columns))
  ```
  - 답:
    ```text
    (4, 5) (2, 5)
    ['x', 'city_A', 'city_B', 'city_C', 'city_D']
    ```
  - 합쳐서 인코딩한 뒤 train 길이로 잘라 되돌린다. 수치형 x는 그대로 남는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  tr = pd.get_dummies(pd.DataFrame({'c': ['a', 'b', 'c']}))
  te = pd.get_dummies(pd.DataFrame({'c': ['b', 'd']}))
  te = te.reindex(columns=tr.columns, fill_value=0)
  print(list(te.columns))
  print(te.astype(int).values.tolist())
  ```
  - 답:
    ```text
    ['c_a', 'c_b', 'c_c']
    [[0, 1, 0], [0, 0, 0]]
    ```
  - train 열 목록에 맞춰 없는 열은 0으로 만들고, train에 없던 열(c_d)은 버린다.

- Q: 빈칸에 들어갈 것은? (test 열을 train 열에 맞춘다)
  ```text
  import pandas as pd
  X_tr = pd.get_dummies(pd.DataFrame({'c': ['a', 'b', 'c']}))
  X_te = pd.get_dummies(pd.DataFrame({'c': ['a', 'd']}))
  X_tr, X_te = X_tr.align(X_te, join='①', axis=②, fill_value=0)
  print(list(X_te.columns))
  ```
  - 답: ① `left` ② `1`
  - 출력은 `['c_a', 'c_b', 'c_c']`. `axis=1`이 열 기준이고, `join='left'`면 왼쪽(train) 열 목록을 따른다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  d = pd.get_dummies(pd.Series(['x', 'y', 'x']))
  print(d['x'].dtype, d.sum().tolist())
  print(pd.get_dummies(pd.Series(['x', 'y', 'x']), dtype=int)['x'].dtype)
  ```
  - 답:
    ```text
    bool [2, 1]
    int64
    ```
  - 버전 주의: pandas 2.0부터 기본 dtype이 bool이다(그 전에는 uint8). 모델에는 bool도 그대로 들어간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import LabelEncoder
  train = pd.DataFrame({'grade': ['B', 'C', 'A', 'B']})
  test = pd.DataFrame({'grade': ['C', 'D']})
  le = LabelEncoder()
  le.fit(pd.concat([train['grade'], test['grade']]))
  print(le.classes_.tolist())
  print(le.transform(test['grade']).tolist())
  ```
  - 답:
    ```text
    ['A', 'B', 'C', 'D']
    [2, 3]
    ```
  - train과 test 값을 합쳐 fit해야 test에만 있는 값(D)도 번호를 받는다. train에만 fit하면 `transform(['D'])`가 ValueError를 낸다.

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  print(le.fit_transform(['low', 'mid', 'high', 'low']).tolist())
  ```
  - 답: `[1, 2, 0, 1]`
  - 번호는 등장 순서가 아니라 사전순이다(high < low < mid). 순서가 의미 있는 범주는 `map`으로 직접 매긴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['M', 'F', 'f', 'M'])
  r = s.map({'M': 0, 'F': 1})
  print(r.isna().sum(), r.tolist())
  ```
  - 답: `1 [0.0, 1.0, nan, 0.0]`
  - 사전에 없는 값은 NaN이 되고, NaN이 섞여 열이 실수형으로 바뀐다.

## 스케일링

- Q: 스케일러를 fit할 데이터 — train만. test에는 `transform`만 쓴다
  - test에 `fit_transform`을 하면 test가 자기 평균·표준편차로 변환돼 학습 때와 다른 눈금이 된다.
- Q: 랜덤포레스트에 스케일링이 꼭 필요한가 — 아니다
  - 트리는 값의 대소 순서로 나누므로 표준화 같은 단조 변환으로 분할 결과가 사실상 바뀌지 않는다. 거리 기반 모델(KNN, SVM)이나 선형 모델에서 필요하다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  train = pd.DataFrame({'x': [1.0, 2.0, 3.0, 4.0, 5.0]})
  test = pd.DataFrame({'x': [6.0]})
  sc = StandardScaler().fit(train)
  print(round(sc.scale_[0], 4), round(sc.transform(test)[0, 0], 2))
  print(round(train['x'].std(), 4))
  ```
  - 답:
    ```text
    1.4142 2.12
    1.5811
    ```
  - StandardScaler는 모표준편차(ddof=0)로 나누고, 판다스 `std()`는 표본표준편차(ddof=1)다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import MinMaxScaler
  train = pd.DataFrame({'x': [10, 20, 30]})
  test = pd.DataFrame({'x': [40, 5]})
  mm = MinMaxScaler().fit(train)
  print(mm.transform(test).ravel().round(2).tolist())
  ```
  - 답: `[1.5, -0.25]`
  - train의 최솟값·최댓값 기준이라 test 값은 0~1을 벗어날 수 있다. 정상이다.

## 검증 분할

- Q: `X_tr, X_val, y_tr, y_val = train_test_split(X, y)`에서 돌려주는 순서의 규칙 — 넣은 배열마다 학습용 다음 검증용
- Q: train_test_split에서 `test_size`를 주지 않으면 검증 비율 — 0.25
- **층화 분할 (stratify)** — 타깃의 클래스 비율이 학습용과 검증용에 똑같이 유지되도록 나누는 방식. 분류 문제에서 `stratify=y`로 준다
  - 회귀(연속 타깃)에는 쓰지 않는다. 값마다 클래스가 1개뿐이라 ValueError가 난다.
- **난수 시드 (random_state)** — 분할이나 부트스트랩처럼 무작위가 끼는 과정을 고정해 다시 돌려도 같은 결과가 나오게 하는 인자

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.model_selection import train_test_split
  X = pd.DataFrame({'v': range(11)})
  X_tr, X_val = train_test_split(X, test_size=0.2, random_state=0)
  print(len(X_tr), len(X_val))
  ```
  - 답: `8 3`
  - 11 × 0.2 = 2.2인데 검증 쪽은 올림해서 3개가 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.model_selection import train_test_split
  X = pd.DataFrame({'v': range(12)})
  y = pd.Series([0] * 8 + [1] * 4)
  X_tr, X_val, y_tr, y_val = train_test_split(
      X, y, test_size=0.25, stratify=y, random_state=1)
  print(len(y_val), y_val.sum(), y_tr.sum())
  ```
  - 답: `3 1 3`
  - 원래 비율 2:1(0이 8개, 1이 4개)이 검증 3개에도 2:1로 유지된다.

## 모델 고르기

- Q: 타깃이 0/1 같은 범주이면 쓰는 랜덤포레스트 — `RandomForestClassifier`
  - 연속값(가격, 수량)이면 `RandomForestRegressor`. 평가지표가 AUC, F1, 정확도면 분류이고 RMSE, MAE, R²면 회귀다.
- Q: 클래스가 3개 이상인 다중 분류에 RandomForestClassifier를 쓰려면 추가로 할 설정 — 없다
  - 타깃에 클래스가 여러 개 있으면 그대로 다중 분류로 학습한다. `predict_proba`는 (행 수, 클래스 수) 모양이 된다.
- Q: RandomForest의 `n_estimators` 기본값 — `100`
  - 나무 개수다. 늘리면 대체로 안정되지만 시간이 늘어난다.
- Q: RandomForest의 `max_depth` 기본값 — `None`
  - 잎이 순수해지거나 `min_samples_split`보다 작아질 때까지 끝까지 자란다. 과적합이 보이면 5~10 정도로 제한한다.
- Q: RandomForestClassifier의 `max_features` 기본값 — `'sqrt'`
  - 버전 주의: scikit-learn 1.1부터. RandomForestRegressor의 기본값은 `1.0`(모든 특성)이다.
- Q: 소수 클래스가 아주 적을 때 RandomForestClassifier에 줄 수 있는 인자 — `class_weight='balanced'`
  - 클래스 빈도의 역수로 가중치를 줘 소수 클래스를 더 무겁게 본다.
- **최소 잎 샘플 수 (min_samples_leaf)** — 잎 노드 하나에 남아야 하는 최소 샘플 수. 기본값 1이고 키우면 나무가 덜 세분돼 과적합이 줄어든다

- Q: 출력 결과는?
  ```text
  from sklearn.ensemble import RandomForestClassifier
  X = [[1], [2], [3], [4]]
  y = [1.5, 2.7, 3.1, 4.8]
  try:
      RandomForestClassifier(random_state=0).fit(X, y)
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 연속 타깃을 분류기에 넣으면 클래스를 정할 수 없어 학습이 거부된다. 회귀 문제는 Regressor로 푼다.

## predict와 predict_proba

- Q: 평가지표가 AUC일 때 제출할 값 — `predict_proba(X)[:, 1]`(양성 클래스 확률)
  - `predict`의 0/1을 내면 순위 정보가 사라져 AUC가 떨어진다.

- Q: 출력 결과는?
  ```text
  from sklearn.ensemble import RandomForestClassifier
  X = [[1], [2], [3], [4], [5], [6]]
  y = ['yes', 'no', 'yes', 'no', 'yes', 'no']
  clf = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
  print(clf.classes_.tolist(), clf.predict_proba([[3], [4]]).shape)
  ```
  - 답: `['no', 'yes'] (2, 2)`
  - 확률 열 순서는 `classes_` 순서(정렬순)다. 여기서는 `[:, 1]`이 'yes'의 확률이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  proba = np.array([[0.7, 0.3], [0.45, 0.55], [0.2, 0.8]])
  print(proba[:, 1].tolist())
  print((proba[:, 1] >= 0.5).astype(int).tolist())
  print(proba.sum(axis=1).tolist())
  ```
  - 답:
    ```text
    [0.3, 0.55, 0.8]
    [0, 1, 1]
    [1.0, 1.0, 1.0]
    ```
  - 행마다 확률의 합은 1이고, 이진 분류의 `predict`는 확률이 더 큰 쪽을 고른다.

## 분류 평가지표

- Q: sklearn 분류 지표 중 0/1 라벨이 아니라 확률(점수)을 받는 것 — `roc_auc_score`
  - 정확도, 정밀도, 재현율, F1, 혼동행렬 함수는 라벨을 받는다. `log_loss`도 확률을 받는다.
- Q: 다중 분류 AUC를 `roc_auc_score`로 구할 때 필요한 것 — 클래스별 확률 전체(n×k 배열)와 `multi_class='ovr'`
- **정밀도 (precision)** — 양성이라고 예측한 것 중 실제 양성의 비율, TP / (TP + FP)
- **재현율 (recall)** — 실제 양성 중 모델이 양성으로 맞힌 비율, TP / (TP + FN)
- Q: 클래스가 95:5로 치우친 데이터에서 정확도가 0.95라면 — 전부 다수 클래스로 찍어도 나오는 값이라 성능을 말해 주지 못한다
  - 이럴 때 문제는 보통 F1이나 AUC로 채점한다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import confusion_matrix
  y_true = [1, 0, 1, 1, 0, 0, 1, 0]
  y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
  tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
  print(tn, fp, fn, tp)
  ```
  - 답: `3 1 1 3`
  - 행이 실제, 열이 예측이고 라벨 순(0, 1)이라 펼치면 TN, FP, FN, TP 순이다.

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
  - TP 2, FN 2, FP 1, TN 5. F1은 정밀도와 재현율의 조화평균이다.

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
  - `average` 기본값은 `'binary'`라 다중 분류에서는 오류다. `'macro'`는 클래스별 F1의 단순 평균, `'weighted'`는 클래스 크기로 가중한 평균이다.

## 회귀 평가지표

- Q: RMSE를 버전과 상관없이 구하는 코드 — `np.sqrt(mean_squared_error(y_true, y_pred))`
  - 시험 환경(scikit-learn 1.5.2)에서 `mean_squared_error(..., squared=False)`는 폐기 경고와 함께 아직 동작한다. 1.6 이후 버전에서는 제거됐으니 `np.sqrt`나 `root_mean_squared_error`(1.4부터)를 쓰는 습관이 안전하다.
- Q: 시험 환경(scikit-learn 1.5.2)에서 `mean_squared_log_error`가 ValueError를 내는 경우 — 예측값이나 실젯값에 음수가 하나라도 있을 때
  - 1.6부터는 -1 이하일 때만 오류로 바뀌었다. 어느 버전이든 회귀 예측을 `np.clip(pred, 0, None)`으로 0 아래를 잘라 두면 안전하다.

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
  from sklearn.metrics import r2_score
  y_true = [1, 2, 3, 4]
  print(r2_score(y_true, [2.5, 2.5, 2.5, 2.5]), r2_score(y_true, [4, 3, 2, 1]))
  ```
  - 답: `0.0 -3.0`
  - 평균만 찍으면 0이고, 그보다 못하면 음수가 된다. R²는 0~1 사이로 묶여 있지 않다.

- Q: 출력 결과는?
  ```text
  from sklearn.metrics import r2_score
  y_true = [1, 2, 3, 4]
  y_pred = [1, 2, 3, 8]
  print(round(r2_score(y_true, y_pred), 2), round(r2_score(y_pred, y_true), 2))
  ```
  - 답: `-2.2 0.45`
  - R²는 정답 쪽 분산으로 나누므로 인자 순서를 바꾸면 값이 달라진다. MSE·MAE는 순서와 무관하다.

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

## 제출 파일

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
  - `index=False`를 빠뜨리면 이름 없는 인덱스 열이 첫 열로 들어가 열 개수가 달라진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  test_id = pd.Series([501, 502], index=[4, 5])
  pred = pd.Series([1, 0])
  sub = pd.DataFrame({'id': test_id, 'pred': pred})
  print(len(sub), sub['pred'].isna().sum())
  ```
  - 답: `4 2`
  - Series끼리는 인덱스로 맞춰 붙는다. concat 뒤 잘라낸 test처럼 인덱스가 0부터가 아니면 어긋난다. 예측은 배열 그대로(`model.predict` 결과) 넣거나 `test_id.values`를 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'x': [1, 2, 3]})
  test = pd.DataFrame({'x': [4, 5]})
  all_ = pd.concat([train, test])
  print(all_.index.tolist(), len(all_.loc[0]), all_.iloc[len(train):]['x'].tolist())
  ```
  - 답: `[0, 1, 2, 0, 1] 2 [4, 5]`
  - concat은 인덱스를 그대로 이어 붙여 0이 두 번 나오고, `loc[0]`은 두 행을 돌려준다. 되돌릴 때는 `loc`이 아니라 `iloc`으로 자른다.

## 점수를 깎는 실수

- **데이터 누수 (data leakage)** — 예측 시점에는 알 수 없는 정보(타깃 자체나 타깃에서 만든 열, test의 통계)가 학습에 섞여 검증 점수가 실제보다 좋게 나오는 것
- Q: 검증 점수를 확인한 뒤 test 예측 전에 해도 되는 일 — train 전체(학습용 + 검증용)로 모델을 다시 fit
  - 검증용으로 떼어 둔 행까지 학습에 쓰게 된다. 하이퍼파라미터는 바꾸지 않는다.
- Q: test에 get_dummies나 스케일러 fit을 따로 하면 생기는 일 — 열 구성이나 변환 기준이 train과 달라진다
  - 인코딩은 합쳐서 하거나 열을 맞추고, 스케일러는 train으로 fit한 것을 test에 transform만 한다.
