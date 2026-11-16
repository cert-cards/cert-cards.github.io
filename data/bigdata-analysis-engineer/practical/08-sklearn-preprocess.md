# scikit-learn · 전처리·분할

> sklearn.preprocessing의 인코더, 스케일러, 거듭제곱 변환과 sklearn.impute의 SimpleImputer, pandas get_dummies 열 맞추기, sklearn.model_selection의 분할, 교차검증, 그리드서치를 다룬다.

## fit · transform · fit_transform

- Q: 전처리 객체에서 `fit`이 하는 일 — 변환 기준(평균, 최솟값, 범주 목록 등)을 데이터에서 구해 객체 안에 저장
  - `transform`은 저장된 기준으로 값을 바꾸고, `fit_transform`은 둘을 한 번에 한다.

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import StandardScaler
  sc = StandardScaler()
  try:
      sc.transform([[1.0], [2.0]])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `NotFittedError`
  - fit 전에는 기준값이 없어 transform을 할 수 없다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  df = pd.DataFrame({'x': [1.0, 2.0, 3.0]})
  out = StandardScaler().fit_transform(df)
  print(type(out).__name__, out.shape)
  ```
  - 답: `ndarray (3, 1)`
  - DataFrame을 넣어도 numpy 배열이 나온다. 열 이름이 필요하면 `df[cols] = ...`로 다시 넣는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  df = pd.DataFrame({'x': [1.0, 2.0, 3.0]})
  out = StandardScaler().set_output(transform='pandas').fit_transform(df)
  print(type(out).__name__, out.columns.tolist())
  ```
  - 답: `DataFrame ['x']`
  - `set_output(transform='pandas')`를 걸면 열 이름이 붙은 DataFrame으로 돌려준다.

## LabelEncoder

- Q: `LabelEncoder().fit_transform(s)`가 돌려주는 것 — 0부터 매긴 정수 numpy 배열
  - 번호는 `classes_` 안의 위치이고, `classes_`는 값을 정렬한 순서다.
- Q: LabelEncoder가 원래 만들어진 용도 — 타깃 y의 범주를 0~k-1 정수로 바꾸는 것
  - 특성 열에 쓰면 사전순 번호가 크기처럼 읽힌다. 트리 모델은 대체로 괜찮고, 선형·거리 기반 모델에는 원핫 인코딩이 맞다.

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
  - train과 test 값을 합쳐 fit해야 test에만 있는 값(D)도 번호를 받는다.

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  y = le.fit_transform(['no', 'yes', 'no'])
  print(le.inverse_transform([1, 0]).tolist())
  ```
  - 답: `['yes', 'no']`
  - 숫자로 예측한 결과를 원래 라벨로 되돌려 제출할 때 쓴다.

- Q: 빈칸에 들어갈 것은? (범주형 열마다 따로 인코딩한다)
  ```text
  import pandas as pd
  from sklearn.preprocessing import LabelEncoder
  df = pd.read_csv('data.csv')
  for col in ['city', 'job']:
      df[col] = LabelEncoder().①(df[col])
  ```
  - 답: ① `fit_transform`
  - 열마다 새 객체를 만든다. 객체 하나를 돌려 쓰면 `classes_`에는 마지막 열 것만 남는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  print(le.fit_transform(pd.Series(['a', None, 'b'])).tolist())
  print(le.classes_.tolist())
  ```
  - 답:
    ```text
    [0, 2, 1]
    ['a', 'b', None]
    ```
  - 결측도 오류 없이 하나의 범주로 번호를 받는다. 결측을 먼저 채우지 않으면 모르는 사이에 '결측' 범주가 생긴다.

## OneHotEncoder

- Q: OneHotEncoder의 `handle_unknown` 기본값과 `'ignore'`의 뜻 — `'error'` / `'ignore'`면 fit 때 없던 범주를 전부 0인 행으로 바꾼다
- Q: OneHotEncoder의 `sparse_output` 기본값 — `True`(희소행렬을 돌려준다)
  - DataFrame으로 붙이려면 `sparse_output=False`를 주거나 결과에 `.toarray()`를 한다. 1.2에서 `sparse`가 `sparse_output`으로 이름이 바뀌었고, 이 버전(1.5)에서 `sparse=False`를 쓰면 TypeError다.
- Q: 범주 목록을 train에서 기억해 test에 같은 열을 만들어 주는 쪽 — OneHotEncoder
  - `pd.get_dummies`는 부를 때마다 그 데이터의 범주로 열을 새로 만들어 train과 test 열이 어긋날 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import OneHotEncoder
  train = pd.DataFrame({'city': ['A', 'B', 'C', 'A']})
  test = pd.DataFrame({'city': ['B', 'D']})
  ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
  ohe.fit(train[['city']])
  print(ohe.get_feature_names_out().tolist())
  print(ohe.transform(test[['city']]).tolist())
  ```
  - 답:
    ```text
    ['city_A', 'city_B', 'city_C']
    [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
    ```
  - test에만 있는 D는 세 열이 모두 0인 행이 된다. 열 개수는 train과 같다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import OneHotEncoder
  ohe = OneHotEncoder().fit(pd.DataFrame({'city': ['A', 'B']}))
  try:
      ohe.transform(pd.DataFrame({'city': ['C']}))
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 기본값 `handle_unknown='error'`라 처음 보는 범주에서 멈춘다.

- Q: 빈칸에 들어갈 것은? (원핫 결과를 열 이름이 있는 DataFrame으로 만든다)
  ```text
  import pandas as pd
  from sklearn.preprocessing import OneHotEncoder
  train = pd.read_csv('train.csv')
  ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
  arr = ohe.fit_transform(train[['city']])
  enc = pd.DataFrame(arr, columns=ohe.①(), index=train.index)
  ```
  - 답: ① `get_feature_names_out`
  - `index=train.index`를 줘야 원래 데이터와 concat할 때 행이 맞는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import OneHotEncoder
  ohe = OneHotEncoder(drop='first', sparse_output=False)
  ohe.fit(pd.DataFrame({'c': ['x', 'y', 'z']}))
  print(ohe.get_feature_names_out().tolist())
  ```
  - 답: `['c_y', 'c_z']`
  - `drop='first'`는 첫 범주 열을 빼서 k개 범주를 k-1개 열로 만든다. 선형회귀의 다중공선성을 피할 때 쓴다.

## pd.get_dummies와 열 맞추기

- Q: `pd.get_dummies(df)`가 바꾸는 열 — object(문자열)·category 열만
  - 수치형 열은 그대로 남는다. 특정 열만 바꾸려면 `columns=['city']`를 준다.

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

## StandardScaler

- Q: StandardScaler가 하는 변환 — 열마다 (x - 평균) / 표준편차
  - 결과 열은 평균 0, 표준편차 1이 된다. 평균은 `mean_`, 표준편차는 `scale_`에 저장된다.
- Q: StandardScaler가 쓰는 표준편차 — 모표준편차(ddof=0)
  - pandas `std()`는 표본표준편차(ddof=1)라 손 계산과 값이 조금 다르다.
- Q: 스케일링이 필요한 모델과 거의 필요 없는 모델 — 거리·계수 기반(KNN, SVM, 로지스틱·선형회귀)은 필요 / 트리 기반(결정트리, 랜덤포레스트, LightGBM, XGBoost)은 거의 필요 없다
  - 트리는 값의 대소 순서로 나누므로 단조 변환을 해도 분할 결과가 사실상 같다.

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
  - 평균 3, 모표준편차 √2로 나눈다. test는 train의 기준으로 변환되므로 (6 - 3) / 1.4142다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  df = pd.DataFrame({'x': [2, 4, 6, 8]})
  by_hand = (df['x'] - df['x'].mean()) / df['x'].std()
  by_sk = StandardScaler().fit_transform(df[['x']])
  print(round(by_hand.max(), 3), round(by_sk.max(), 3))
  ```
  - 답: `1.162 1.342`
  - 손 계산은 표본표준편차(2.582), 스케일러는 모표준편차(2.236)로 나눈다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  df = pd.DataFrame({'x': [1.0, 2.0, 3.0]})
  try:
      StandardScaler().fit_transform(df['x'])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 스케일러는 2차원 입력(행 × 열)을 받는다. 열 하나는 `df[['x']]`처럼 대괄호 두 겹으로 넣는다.

- Q: 빈칸에 들어갈 것은? (수치형 열을 train 기준으로 표준화한다)
  ```text
  from sklearn.preprocessing import StandardScaler
  num = ['age', 'income']
  sc = StandardScaler()
  X_train[num] = sc.①(X_train[num])
  X_test[num] = sc.②(X_test[num])
  ```
  - 답: ① `fit_transform` ② `transform`

## MinMaxScaler

- Q: MinMaxScaler의 변환식과 `feature_range` 기본값 — (x - min) / (max - min), `(0, 1)`
  - min과 max는 fit한 데이터에서 구한 값이다.

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

- Q: 빈칸에 들어갈 것은? (열 하나를 0~1로 바꾼다)
  ```text
  import pandas as pd
  from sklearn.preprocessing import MinMaxScaler
  df = pd.read_csv('data.csv')
  df['x_mm'] = MinMaxScaler().fit_transform(①)
  ```
  - 답: ① `df[['x']]`
  - `df['x']`(1차원 Series)를 넣으면 오류가 난다. 결과는 (n, 1) 배열이고 열 하나에 그대로 들어간다.

## RobustScaler

- Q: RobustScaler가 빼는 값과 나누는 값 — 중앙값을 빼고 IQR(Q3 - Q1)로 나눈다
  - 평균과 표준편차 대신 순위 기반 값을 쓰므로 이상치 한두 개에 기준이 끌려가지 않는다.
- Q: StandardScaler 대신 RobustScaler를 고르는 상황 — 열에 극단적인 이상치가 있을 때
  - 이상치 자체는 그대로 크게 남는다. 이상치를 없애는 것이 아니라 나머지 값의 눈금을 지키는 것이다.

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import RobustScaler
  X = [[1], [2], [3], [4], [100]]
  print(RobustScaler().fit_transform(X).ravel().tolist())
  ```
  - 답: `[-1.0, -0.5, 0.0, 0.5, 48.5]`
  - 중앙값 3, Q1 2, Q3 4라 IQR이 2다. 100은 (100 - 3) / 2 = 48.5로 여전히 크다.

## PowerTransformer

- Q: `PowerTransformer()`의 기본 방법과 표준화 여부 — `method='yeo-johnson'`, `standardize=True`
  - 그래서 결과는 평균 0, 표준편차 1로 맞춰져 나온다. 변환값 자체가 필요하면 `standardize=False`.
- Q: `method='box-cox'`와 `'yeo-johnson'`의 차이 — box-cox는 양수만, yeo-johnson은 0과 음수도 받는다

- Q: 출력 결과는?
  ```text
  from sklearn.preprocessing import PowerTransformer
  try:
      PowerTransformer(method='box-cox').fit_transform([[0.0], [1.0], [2.0]])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 0이 있어 box-cox를 쓸 수 없다. 기본값 yeo-johnson이면 그대로 된다.

## SimpleImputer

- Q: SimpleImputer의 `strategy` 기본값 — `'mean'`
  - 고를 수 있는 값은 `'mean'`, `'median'`, `'most_frequent'`, `'constant'`(값은 `fill_value`로 준다).
- Q: 문자열 열의 결측을 SimpleImputer로 채울 때 쓸 strategy — `'most_frequent'` 또는 `'constant'`
  - `'mean'`, `'median'`은 숫자에서만 계산된다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  from sklearn.impute import SimpleImputer
  train = pd.DataFrame({'x': [1.0, 2.0, np.nan, 100.0]})
  test = pd.DataFrame({'x': [np.nan, 5.0]})
  imp = SimpleImputer(strategy='median').fit(train)
  print(imp.statistics_.tolist(), imp.transform(test).ravel().tolist())
  ```
  - 답: `[2.0] [2.0, 5.0]`
  - 중앙값은 결측을 뺀 [1, 2, 100]에서 2다. test도 train의 중앙값으로 채운다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  from sklearn.impute import SimpleImputer
  df = pd.DataFrame({'c': ['b', 'a', np.nan, 'b']})
  print(SimpleImputer(strategy='most_frequent').fit_transform(df).ravel().tolist())
  ```
  - 답: `['b', 'a', 'b', 'b']`

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  from sklearn.impute import SimpleImputer
  df = pd.DataFrame({'c': ['a', np.nan, 'b']})
  try:
      SimpleImputer().fit(df)
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 기본 strategy가 `'mean'`이라 문자열 열에서 평균을 못 구한다.

- Q: 빈칸에 들어갈 것은? (결측을 'missing'이라는 범주로 채운다)
  ```text
  from sklearn.impute import SimpleImputer
  imp = SimpleImputer(strategy='①', fill_value='missing')
  X_train[['job']] = imp.fit_transform(X_train[['job']])
  ```
  - 답: ① `constant`

## train_test_split

- Q: `X_tr, X_val, y_tr, y_val = train_test_split(X, y)`에서 돌려주는 순서의 규칙 — 넣은 배열마다 학습용 다음 검증용
- Q: train_test_split에서 `test_size`를 주지 않으면 검증 비율 — 0.25
- Q: 분류 문제에서 학습용과 검증용의 클래스 비율을 같게 나누는 인자 — `stratify=y`
  - 회귀(연속 타깃)에는 쓰지 않는다. 값마다 클래스가 1개뿐이라 ValueError가 난다.

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

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.model_selection import train_test_split
  X = pd.DataFrame({'v': range(10)})
  X_tr, X_val = train_test_split(X, test_size=3, random_state=0)
  print(len(X_tr), len(X_val))
  ```
  - 답: `7 3`
  - `test_size`에 정수를 주면 비율이 아니라 행 개수다.

## KFold · StratifiedKFold

- Q: KFold의 `n_splits`와 `shuffle` 기본값 — `5`, `False`
  - 섞지 않으면 앞에서부터 순서대로 잘라 검증 폴드를 만든다.
- Q: StratifiedKFold를 쓰는 상황 — 분류에서 각 폴드의 클래스 비율을 전체와 같게 유지할 때
  - `split(X, y)`에 y가 꼭 필요하다. 회귀에는 KFold를 쓴다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.model_selection import KFold
  folds = list(KFold(n_splits=3).split(np.arange(10)))
  print([len(te) for tr, te in folds])
  print(folds[0][1].tolist())
  ```
  - 답:
    ```text
    [4, 3, 3]
    [0, 1, 2, 3]
    ```
  - 10행을 3등분하면 나머지 1행이 앞 폴드에 붙는다. 섞지 않았으므로 첫 검증 폴드는 0~3번 행이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.model_selection import KFold, StratifiedKFold
  y = np.array([0] * 6 + [1] * 3)
  X = np.zeros((9, 1))
  print([int(y[te].sum()) for tr, te in KFold(n_splits=3).split(X, y)])
  print([int(y[te].sum()) for tr, te in StratifiedKFold(n_splits=3).split(X, y)])
  ```
  - 답:
    ```text
    [0, 0, 3]
    [1, 1, 1]
    ```
  - 정렬된 데이터를 KFold로 섞지 않고 자르면 마지막 폴드에 1이 몰린다. StratifiedKFold는 폴드마다 1을 하나씩 넣는다.

- Q: 출력 결과는?
  ```text
  from sklearn.model_selection import KFold
  try:
      KFold(n_splits=3, random_state=0)
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - `shuffle=False`인데 `random_state`를 주면 효과가 없다며 거부한다. `KFold(n_splits=3, shuffle=True, random_state=0)`으로 쓴다.

## cross_val_score

- Q: `cross_val_score(model, X, y, cv=5)`가 돌려주는 것 — 폴드별 점수 5개가 든 numpy 배열
  - 보통 `.mean()`으로 평균을 본다. 모델을 폴드마다 새로 학습하므로 원래 model 객체는 학습되지 않은 채 남는다.
- Q: cross_val_score에서 `scoring`을 주지 않으면 쓰는 점수 — 모델의 `score` 메서드(분류기는 정확도, 회귀기는 R²)
- Q: `cv=5`처럼 정수를 줄 때 분류기에 쓰이는 분할 방식 — StratifiedKFold(섞지 않음)
  - 회귀기면 KFold다. 섞으려면 `cv=KFold(5, shuffle=True, random_state=0)`처럼 객체를 넘긴다.
- Q: scoring 문자열로 RMSE를 쓰는 이름 — `'neg_root_mean_squared_error'`
  - 이 밖에 자주 쓰는 이름: `'accuracy'`, `'f1'`, `'f1_macro'`, `'roc_auc'`, `'r2'`, `'neg_mean_squared_error'`, `'neg_mean_absolute_error'`.
- Q: 오차 지표 scoring 이름에 `neg_`가 붙는 이유 — sklearn은 점수가 클수록 좋다고 보기 때문에 오차에 음수를 붙여 돌려준다
  - 실제 RMSE는 `-scores.mean()`이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from sklearn.linear_model import LinearRegression
  from sklearn.model_selection import cross_val_score
  X = np.arange(20).reshape(-1, 1)
  y = np.arange(20) * 2.0 + np.array([0.5, -0.5] * 10)
  s = cross_val_score(LinearRegression(), X, y, cv=4,
                      scoring='neg_root_mean_squared_error')
  print(len(s), bool((s <= 0).all()))
  ```
  - 답: `4 True`
  - 폴드 수만큼 점수가 나오고, `neg_` 지표는 모두 0 이하다.

- Q: 빈칸에 들어갈 것은? (5겹 교차검증 AUC 평균)
  ```text
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import cross_val_score
  rf = RandomForestClassifier(random_state=0)
  scores = cross_val_score(rf, X, y, cv=5, scoring='①')
  print(scores.②())
  ```
  - 답: ① `roc_auc` ② `mean`

## GridSearchCV

- Q: GridSearchCV가 하는 일 — `param_grid`의 모든 조합을 교차검증으로 평가해 가장 좋은 조합을 고른다
  - 결과는 `best_params_`(조합), `best_score_`(그 교차검증 평균), `best_estimator_`(그 조합으로 다시 학습한 모델)에 있다.
- Q: GridSearchCV의 `refit` 기본값과 그 덕분에 할 수 있는 것 — `True` / 최적 조합으로 전체 데이터를 다시 학습하므로 `gs.predict(X_test)`를 바로 쓸 수 있다
- Q: 그리드서치의 학습 횟수 — 조합 수 × cv 폴드 수 (+ refit 1번)
  - 코드 실행 시간에 제한이 있으면 후보를 2~4개, cv를 3 정도로 작게 잡거나 그리드서치 없이 기본값 모델로 낸다.

- Q: 출력 결과는?
  ```text
  from sklearn.model_selection import ParameterGrid
  grid = {'max_depth': [3, 5, None], 'n_estimators': [50, 100]}
  n = len(ParameterGrid(grid))
  print(n, n * 3)
  ```
  - 답: `6 18`
  - 조합 3 × 2 = 6개를 cv=3으로 돌리면 학습이 18번(그리고 refit 1번) 일어난다.

- Q: 출력 결과는?
  ```text
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import GridSearchCV
  X = [[i] for i in range(10)]
  y = [0, 1] * 5
  try:
      GridSearchCV(RandomForestClassifier(), {'depth': [3, 5]}, cv=2).fit(X, y)
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - `param_grid`의 키는 모델 인자 이름과 정확히 같아야 한다(`max_depth`).

- Q: 빈칸에 들어갈 것은? (찾은 조합을 보고 그 모델로 예측한다)
  ```text
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import GridSearchCV
  gs = GridSearchCV(RandomForestClassifier(random_state=0),
                    param_grid={'max_depth': [5, 10]}, cv=3, scoring='roc_auc')
  gs.fit(X_train, y_train)
  print(gs.①)
  pred = gs.②.predict_proba(X_test)[:, 1]
  ```
  - 답: ① `best_params_` ② `best_estimator_`
  - refit 기본값이 True라 `gs.predict_proba(X_test)`라고 써도 같다.
