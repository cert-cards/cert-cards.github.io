# scikit-learn · 모델

> scikit-learn의 분류·회귀 모델(랜덤포레스트, 결정트리, 로지스틱·선형회귀, KNN, 그레이디언트 부스팅)과 lightgbm, xgboost 모델의 사용법과 주요 인자, fit과 predict, predict_proba, feature_importances_를 다룬다.

## 분류기와 회귀기 고르기

- Q: 타깃이 0/1이나 문자열 범주일 때 쓰는 모델 종류 — 분류기(`...Classifier`)
  - 연속값(가격, 수량)이면 회귀기(`...Regressor`). 평가지표가 AUC, F1, 정확도면 분류이고 RMSE, MAE, R²면 회귀다.
- Q: 클래스가 3개 이상인 다중 분류에 sklearn 분류기를 쓰려면 추가로 할 설정 — 없다
  - 타깃에 클래스가 여러 개 있으면 그대로 다중 분류로 학습한다. `predict_proba`는 (행 수, 클래스 수) 모양이 된다.

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

- Q: 출력 결과는?
  ```text
  from sklearn.ensemble import RandomForestClassifier
  X = [[0], [1], [2], [3], [4], [5]]
  y = [0.0, 1.0, 2.0, 0.0, 1.0, 2.0]
  clf = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, y)
  print(clf.classes_.tolist())
  ```
  - 답: `[0.0, 1.0, 2.0]`
  - 실수형이어도 값이 정수 꼴이면 클래스로 받아들인다. 오류가 나는 것은 1.5처럼 소수가 섞인 값이다.

## fit · predict 공통 규칙

- Q: `model.fit(X, y)`에 넣는 모양 — X는 2차원(행 × 특성), y는 1차원(행 수 길이)
  - `fit`은 학습된 모델 자신을 돌려주므로 `model = RandomForestClassifier().fit(X, y)`처럼 한 줄로 쓸 수 있다.
- Q: 모델 객체를 만들 때와 fit할 때 각각 넣는 것 — 만들 때는 하이퍼파라미터, fit할 때는 데이터
  - 예: `RandomForestClassifier(n_estimators=200, random_state=0).fit(X_train, y_train)`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.ensemble import RandomForestClassifier
  X = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [0, 1, 0, 1]})
  m = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, [0, 1, 0, 1])
  print(m.n_features_in_, m.feature_names_in_.tolist())
  ```
  - 답: `2 ['a', 'b']`
  - DataFrame으로 학습하면 열 이름을 기억한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.ensemble import RandomForestClassifier
  X = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [0, 1, 0, 1]})
  m = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, [0, 1, 0, 1])
  try:
      m.predict(X[['b', 'a']])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 열 이름이 같아도 순서가 다르면 거부한다. test는 `X_test[X_train.columns]`로 열 순서를 맞춘다.

- Q: 빈칸에 들어갈 것은? (test 열 순서를 train과 같게 맞춘다)
  ```text
  model.fit(X_train, y_train)
  X_test = X_test[①]
  pred = model.predict(X_test)
  ```
  - 답: ① `X_train.columns`

## predict · predict_proba

- Q: 분류기에서 `predict`와 `predict_proba`가 돌려주는 것 — 예측 라벨 1차원 배열 / 클래스별 확률 2차원 배열(행 수 × 클래스 수)
- Q: predict_proba의 열 순서를 정하는 속성 — `classes_`(정렬된 순서)
- Q: 이진 분류에서 양성 클래스(1) 확률을 꺼내는 코드 — `model.predict_proba(X)[:, 1]`
  - 평가지표가 AUC면 이 확률을 제출한다. `predict`의 0/1을 내면 순위 정보가 사라진다.
- Q: 회귀기에 predict_proba가 있나 — 없다(AttributeError)
  - 회귀기는 `predict`만 쓰고 연속값을 돌려준다.

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

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.ensemble import RandomForestClassifier
  X = np.arange(18).reshape(9, 2)
  y = np.array(['c', 'a', 'b'] * 3)
  clf = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, y)
  print(clf.classes_.tolist(), clf.predict_proba(X[:2]).shape)
  ```
  - 답: `['a', 'b', 'c'] (2, 3)`
  - 다중 분류면 열이 클래스 수만큼 생긴다. 'c'의 확률은 `[:, 2]`다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  classes = np.array(['a', 'b', 'c'])
  proba = np.array([[0.2, 0.5, 0.3], [0.6, 0.1, 0.3]])
  print(classes[proba.argmax(axis=1)].tolist())
  ```
  - 답: `['b', 'a']`
  - 다중 분류의 `predict`는 행마다 확률이 가장 큰 열의 클래스를 고른 것과 같다.

## RandomForestClassifier · RandomForestRegressor

- Q: RandomForest의 `n_estimators` 기본값 — `100`
  - 나무 개수다. 늘리면 대체로 안정되지만 시간이 늘어난다.
- Q: RandomForest의 `max_depth` 기본값 — `None`
  - 잎이 순수해지거나 `min_samples_split`(기본 2)보다 작아질 때까지 끝까지 자란다. 과적합이 보이면 5~10 정도로 제한한다.
- Q: RandomForestClassifier의 `max_features` 기본값 — `'sqrt'`
  - RandomForestRegressor의 기본값은 `1.0`(모든 특성)이다.
- Q: RandomForest에서 `random_state`를 고정하는 이유 — 부트스트랩 표본과 특성 선택이 무작위라 고정하지 않으면 돌릴 때마다 결과가 달라진다
- Q: 소수 클래스가 아주 적을 때 RandomForestClassifier에 줄 수 있는 인자 — `class_weight='balanced'`
  - 클래스 빈도의 역수로 가중치를 줘 소수 클래스를 더 무겁게 본다.
- Q: RandomForest의 `min_samples_leaf` 기본값과 키우면 생기는 일 — `1` / 잎이 덜 잘게 나뉘어 과적합이 줄어든다
- Q: RandomForest에서 `n_jobs=-1`의 뜻 — CPU 코어를 모두 써서 나무를 병렬로 학습

- Q: 출력 결과는?
  ```text
  from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
  c = RandomForestClassifier().get_params()
  r = RandomForestRegressor().get_params()
  print(c['criterion'], r['criterion'])
  print(c['max_features'], r['max_features'])
  ```
  - 답:
    ```text
    gini squared_error
    sqrt 1.0
    ```

- Q: 빈칸에 들어갈 것은? (나무 300개, 깊이 10, 결과 고정)
  ```text
  from sklearn.ensemble import RandomForestRegressor
  rf = RandomForestRegressor(①=300, ②=10, ③=0)
  rf.fit(X_train, y_train)
  pred = rf.predict(X_test)
  ```
  - 답: ① `n_estimators` ② `max_depth` ③ `random_state`

## DecisionTreeClassifier · DecisionTreeRegressor

- Q: DecisionTreeClassifier의 `criterion` 기본값 — `'gini'`
  - `'entropy'`로 바꿀 수 있다. 회귀 나무의 기본값은 `'squared_error'`다.
- Q: 결정트리를 단독으로 쓸 때 가장 먼저 제한하는 인자 — `max_depth`
  - 기본값 None이면 훈련 데이터를 다 외울 때까지 자라 과적합되기 쉽다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.tree import DecisionTreeClassifier
  X = np.array([[0, 0], [1, 1], [2, 2], [3, 0], [4, 1], [5, 2], [6, 0], [7, 1], [8, 2]])
  y = [0, 0, 0, 1, 1, 1, 2, 2, 2]
  t = DecisionTreeClassifier(max_depth=1, random_state=0).fit(X, y)
  print(t.get_depth(), t.get_n_leaves())
  ```
  - 답: `1 2`
  - 깊이 1이면 한 번만 나눠 잎이 2개다. 클래스가 3개여도 잎 2개로는 두 클래스만 예측된다.

## LogisticRegression

- Q: LogisticRegression의 규제 기본값 — `penalty='l2'`, `C=1.0`
  - 아무것도 안 줘도 L2 규제가 걸려 있다.
- Q: LogisticRegression의 `C`를 줄이면 — 규제가 강해진다(C는 규제 강도의 역수)
- Q: LogisticRegression의 `max_iter` 기본값 — `100`
  - 수렴하지 못하면 ConvergenceWarning을 내고 그 상태로 학습을 끝낸다. 스케일링을 하거나 `max_iter=1000`으로 늘린다.
- Q: 이름은 회귀지만 LogisticRegression이 푸는 문제 — 분류
  - `predict_proba`를 갖고 있다. 연속값 예측에는 LinearRegression을 쓴다.

- Q: 출력 결과는?
  ```text
  import warnings
  import numpy as np
  from sklearn.linear_model import LogisticRegression
  X = np.array([[0, 0], [1, 1], [2, 2], [3, 0], [4, 1], [5, 2], [6, 0], [7, 1], [8, 2]])
  y = [0, 0, 0, 1, 1, 1, 2, 2, 2]
  with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter('always')
      LogisticRegression(max_iter=2).fit(X, y)
  print(type(w[0].message).__name__)
  ```
  - 답: `ConvergenceWarning`
  - 오류가 아니라 경고라 코드는 계속 돈다. 경고가 보이면 `max_iter`를 늘린다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.linear_model import LogisticRegression
  X = np.array([[0, 0], [1, 1], [2, 2], [3, 0], [4, 1], [5, 2], [6, 0], [7, 1], [8, 2]])
  y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
  m3 = LogisticRegression(max_iter=1000).fit(X, y)
  m2 = LogisticRegression(max_iter=1000).fit(X, (y > 0).astype(int))
  print(m3.coef_.shape, m2.coef_.shape)
  ```
  - 답: `(3, 2) (1, 2)`
  - 다중 분류는 클래스마다 계수 한 줄, 이진 분류는 한 줄만 있다. 열 수는 특성 수다.

## LinearRegression

- Q: LinearRegression에서 학습된 기울기와 절편이 들어 있는 속성 — `coef_`, `intercept_`
- Q: LinearRegression에 규제 인자가 있나 — 없다
  - 규제가 필요하면 `Ridge`(L2), `Lasso`(L1)를 쓰고 세기는 `alpha`로 준다.

- Q: 출력 결과는?
  ```text
  from sklearn.linear_model import LinearRegression
  lr = LinearRegression().fit([[0], [1], [2], [3]], [1, 3, 5, 7])
  print(lr.coef_.round(4).tolist(), round(lr.intercept_, 4))
  print(lr.predict([[10]]).round(4).tolist())
  ```
  - 답:
    ```text
    [2.0] 1.0
    [21.0]
    ```
  - y = 2x + 1에 정확히 맞는 데이터다. `coef_`는 특성마다 하나라 배열이고, `intercept_`는 스칼라다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.linear_model import LinearRegression
  X = pd.DataFrame({'x1': [0, 1, 2, 3], 'x2': [5, 3, 8, 1]})
  y = 3 * X['x1'] - 2 * X['x2'] + 4
  lr = LinearRegression().fit(X, y)
  print(dict(zip(X.columns, lr.coef_.round(4))), round(lr.intercept_, 4))
  ```
  - 답: `{'x1': 3.0, 'x2': -2.0} 4.0`
  - 계수는 열 순서대로 나오므로 `zip(X.columns, coef_)`로 이름을 붙여 읽는다.

## KNeighborsClassifier · KNeighborsRegressor

- Q: KNeighbors 모델의 `n_neighbors` 기본값 — `5`
- Q: KNeighbors의 `weights` 기본값과 `'distance'`의 뜻 — `'uniform'`(이웃을 똑같이) / `'distance'`면 가까운 이웃일수록 더 크게 반영
- Q: KNN 앞에 스케일링이 필요한 이유 — 거리로 이웃을 고르므로 단위가 큰 열이 거리를 좌우한다

- Q: 출력 결과는?
  ```text
  from sklearn.neighbors import KNeighborsRegressor
  m = KNeighborsRegressor(n_neighbors=2).fit([[1], [2], [3], [10]], [1, 2, 3, 10])
  print(m.predict([[2.4]]).tolist())
  ```
  - 답: `[2.5]`
  - 가장 가까운 두 점(2, 3)의 y 평균이다.

- Q: 출력 결과는?
  ```text
  from sklearn.neighbors import KNeighborsClassifier
  m = KNeighborsClassifier(n_neighbors=3)
  m.fit([[1], [2], [3], [10], [11]], ['a', 'a', 'b', 'b', 'b'])
  print(m.predict([[1.5], [10.5]]).tolist())
  ```
  - 답: `['a', 'b']`
  - 1.5의 이웃 셋은 1, 2, 3(a, a, b)이라 다수결로 a다.

- Q: 출력 결과는?
  ```text
  from sklearn.neighbors import KNeighborsClassifier
  m = KNeighborsClassifier().fit([[1], [2], [3]], [0, 1, 0])
  try:
      m.predict([[2]])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 기본 이웃 수 5가 학습 행 수 3보다 많다. fit은 되고 predict에서 오류가 난다.

## GradientBoostingClassifier · GradientBoostingRegressor

- Q: GradientBoosting의 `n_estimators`, `learning_rate`, `max_depth` 기본값 — `100`, `0.1`, `3`
- Q: 부스팅에서 `learning_rate`를 줄일 때 같이 하는 일 — `n_estimators`를 늘린다
  - 나무 하나가 고치는 양이 작아지므로 나무가 더 많이 필요하다.
- Q: 랜덤포레스트와 그레이디언트 부스팅이 나무를 만드는 방식의 차이 — 랜덤포레스트는 나무들을 독립적으로 만들어 평균, 부스팅은 앞 나무의 오차를 다음 나무가 고치도록 차례로 만든다

## LGBMClassifier · LGBMRegressor (lightgbm)

- Q: lightgbm 분류기를 불러오는 줄 — `from lightgbm import LGBMClassifier`
  - sklearn과 같은 `fit`, `predict`, `predict_proba`를 쓴다.
- Q: LGBMClassifier의 `n_estimators`, `learning_rate`, `max_depth` 기본값 — `100`, `0.1`, `-1`(깊이 제한 없음)
- Q: LightGBM에서 나무의 복잡도를 정하는 주 인자와 기본값 — `num_leaves`, `31`
  - 나무가 잎 단위로 자라므로 깊이보다 잎 개수로 크기를 조절한다.
- Q: LightGBM이 학습 중 찍는 `[LightGBM] [Info]` 로그를 끄는 인자 — `verbose=-1`
- Q: LightGBM에 문자열 범주 열을 그대로 넣는 방법 — 열을 `astype('category')`로 바꾼다
  - category dtype 열은 자동으로 범주형 특성으로 다룬다. object 열은 ValueError다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from lightgbm import LGBMClassifier
  X = pd.DataFrame({'a': [1.0, 2, 3, 4, 5, 6], 'c': ['x', 'y', 'x', 'y', 'x', 'y']})
  y = ['n', 'y', 'n', 'y', 'n', 'y']
  try:
      LGBMClassifier(n_estimators=3, verbose=-1).fit(X, y)
  except Exception as e:
      print(type(e).__name__)
  X['c'] = X['c'].astype('category')
  m = LGBMClassifier(n_estimators=3, verbose=-1).fit(X, y)
  print(m.classes_.tolist(), m.predict_proba(X).shape)
  ```
  - 답:
    ```text
    ValueError
    ['n', 'y'] (6, 2)
    ```
  - object 열은 거부하고 category 열은 받는다. 문자열 라벨 y는 그대로 받는다.

- Q: 출력 결과는?
  ```text
  from lightgbm import LGBMClassifier, LGBMRegressor
  p = LGBMClassifier().get_params()
  print(p['n_estimators'], p['learning_rate'], p['max_depth'], p['num_leaves'])
  print(LGBMRegressor().get_params()['objective'])
  ```
  - 답:
    ```text
    100 0.1 -1 31
    None
    ```
  - objective를 비워 두면 분류기는 binary 또는 multiclass, 회귀기는 regression(L2)이 쓰인다.

- Q: 빈칸에 들어갈 것은? (로그 없이 학습하고 양성 확률을 낸다)
  ```text
  from lightgbm import LGBMClassifier
  m = LGBMClassifier(n_estimators=300, learning_rate=0.05, ①=-1, random_state=0)
  m.fit(X_train, y_train)
  pred = m.②(X_test)[:, 1]
  ```
  - 답: ① `verbose` ② `predict_proba`

## XGBClassifier · XGBRegressor (xgboost)

- Q: xgboost 회귀기를 불러오는 줄 — `from xgboost import XGBRegressor`
- Q: XGBoost의 `n_estimators`, `learning_rate`, `max_depth` 실제 기본값 — `100`, `0.3`, `6`
  - `get_params()`로 보면 None으로 나온다. 값을 주지 않으면 xgboost 내부 기본값이 쓰인다는 뜻이다.
- Q: XGBClassifier가 받는 y의 조건 — 0부터 k-1까지의 정수 라벨
  - 문자열 라벨이나 1, 2처럼 0에서 시작하지 않는 라벨은 ValueError다. LabelEncoder로 바꾼 뒤 넣는다.
- Q: XGBoost에 범주 열을 그대로 넣는 조건 — 열을 category dtype으로 바꾸고 `enable_categorical=True`를 준다
  - 둘 중 하나라도 빠지면 ValueError다. 아니면 원핫이나 LabelEncoder로 숫자로 만든다.
- Q: XGBoost의 로그 양을 정하는 인자 — `verbosity`(0이면 조용히)

- Q: 출력 결과는?
  ```text
  from xgboost import XGBClassifier
  X = [[1], [2], [3], [4], [5], [6]]
  try:
      XGBClassifier(n_estimators=3).fit(X, ['n', 'y', 'n', 'y', 'n', 'y'])
  except Exception as e:
      print(type(e).__name__)
  try:
      XGBClassifier(n_estimators=3).fit(X, [1, 2, 1, 2, 1, 2])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답:
    ```text
    ValueError
    ValueError
    ```
  - 둘 다 0, 1이 아니라서 거부된다. lightgbm과 sklearn 분류기는 둘 다 받는다.

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import LabelEncoder
  from xgboost import XGBClassifier
  X = [[1], [2], [3], [4], [5], [6]]
  le = LabelEncoder()
  y = le.fit_transform(['n', 'y', 'n', 'y', 'n', 'y'])
  m = XGBClassifier(n_estimators=3).fit(X, y)
  print(m.classes_.tolist(), le.inverse_transform(m.classes_).tolist())
  ```
  - 답: `[0, 1] ['n', 'y']`
  - 예측 결과를 원래 라벨로 제출해야 하면 `le.inverse_transform(m.predict(X_test))`로 되돌린다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from xgboost import XGBClassifier
  X = pd.DataFrame({'a': [1.0, 2, 3, 4, 5, 6], 'c': ['x', 'y'] * 3})
  X['c'] = X['c'].astype('category')
  try:
      XGBClassifier(n_estimators=3).fit(X, [0, 1] * 3)
  except Exception as e:
      print(type(e).__name__)
  m = XGBClassifier(n_estimators=3, enable_categorical=True).fit(X, [0, 1] * 3)
  print(m.predict_proba(X).shape)
  ```
  - 답:
    ```text
    ValueError
    (6, 2)
    ```

- Q: 출력 결과는?
  ```text
  from xgboost import XGBClassifier
  X = [[1], [2], [3], [4], [5], [6]]
  m = XGBClassifier(n_estimators=3).fit(X, [0, 1, 2, 0, 1, 2])
  print(m.objective, m.predict_proba(X).shape)
  ```
  - 답: `multi:softprob (6, 3)`
  - 이진이면 `binary:logistic`, 다중이면 `multi:softprob`를 라벨을 보고 자동으로 고른다.

## feature_importances_

- Q: 트리 모델에서 특성 중요도가 들어 있는 속성 — `feature_importances_`
  - 학습에 쓴 열 순서대로 값이 하나씩 있다. LogisticRegression, LinearRegression에는 없고 대신 `coef_`를 본다.
- Q: sklearn 랜덤포레스트와 LightGBM의 feature_importances_ 차이 — sklearn은 합이 1인 비율, LightGBM은 기본 `importance_type='split'`이라 분할에 쓰인 횟수(정수)

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.ensemble import RandomForestClassifier
  X = np.arange(30).reshape(10, 3)
  y = [0, 1] * 5
  m = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
  print(len(m.feature_importances_), round(m.feature_importances_.sum(), 6))
  ```
  - 답: `3 1.0`

- Q: 빈칸에 들어갈 것은? (중요도가 큰 특성부터 열 이름과 함께 본다)
  ```text
  import pandas as pd
  imp = pd.Series(model.feature_importances_, index=①)
  print(imp.sort_values(ascending=②).head(5))
  ```
  - 답: ① `X_train.columns` ② `False`
