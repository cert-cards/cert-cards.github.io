# 작업형 2 · scikit-learn으로 모델 만들고 제출하기

> 코드는 시험 환경 버전(pandas 2.2.2, numpy 1.26.4, scikit-learn 1.5.2)에서 실행해 확인했다.
> 예시 이름: 파일 train.csv와 test.csv, 타깃 열 target, ID 열 ID. 실제 이름은 문제에 맞게 바꾼다.

## 흐름 한눈에

| 단계 | 할 일 | 핵심 코드 |
|---|---|---|
| 1 | 읽기 | `pd.read_csv` |
| 2 | 타깃과 ID 떼기 | `train.pop('target')`, `drop(columns=['ID'])` |
| 3 | 결측 채우기 | train의 중앙값으로 train과 test 모두 |
| 4 | 범주 열 원핫 | concat → `get_dummies` → `iloc`로 다시 나누기 |
| 5 | 검증 | `train_test_split`, 분류면 `stratify=y` |
| 6 | 학습과 점수 확인 | `RandomForestClassifier` 또는 `RandomForestRegressor` |
| 7 | 전체 train으로 다시 학습 | `model.fit(X, y)` |
| 8 | 예측과 저장 | `predict` 또는 `predict_proba[:, 1]` → `to_csv('result.csv', index=False)` |
| 9 | 확인 | 행 수, 열 이름, 결측 |

## 분류 기본 템플릿

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
print(train.shape, test.shape)
print(train.isna().sum().sum(), test.isna().sum().sum())

# 1. 타깃과 ID 떼기
y = train.pop('target')
train = train.drop(columns=['ID'])
test = test.drop(columns=['ID'])

# 2. 결측 채우기 (기준값은 train에서 구한다)
num_cols = train.select_dtypes(include='number').columns
cat_cols = train.select_dtypes(exclude='number').columns
med = train[num_cols].median()
train[num_cols] = train[num_cols].fillna(med)
test[num_cols] = test[num_cols].fillna(med)
train[cat_cols] = train[cat_cols].fillna('missing')
test[cat_cols] = test[cat_cols].fillna('missing')

# 3. 합쳐서 원핫 인코딩 후 다시 나누기
X_all = pd.get_dummies(pd.concat([train, test]), columns=cat_cols)
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 4. 검증용 분할과 점수 확인
X_tr, X_val, y_tr, y_val = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y)
model = RandomForestClassifier(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
print('AUC', roc_auc_score(y_val, model.predict_proba(X_val)[:, 1]))

# 5. 전체 train으로 다시 학습하고 test 예측
model.fit(X, y)
pred = model.predict_proba(X_test)[:, 1]

# 6. 저장
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
```

제출 전 확인:

```python
r = pd.read_csv('result.csv')
print(r.shape, len(test))       # 행 수가 test와 같은가
print(r.columns.tolist())       # ['pred'] 한 열인가
print(r.isna().sum().sum())     # 0인가
print(r.head())
```

- concat 후 `iloc`로 자르면 train이 앞, test가 뒤라서 순서가 그대로 유지된다.
- 원핫을 train과 test에 따로 하면 열이 달라져 predict에서 에러가 난다. 따로 했다면 `X_test = X_test.reindex(columns=X.columns, fill_value=0)`로 맞춘다.
- 결측은 train에서 구한 값으로 test까지 채운다. test 행은 절대 지우지 않는다.

## 회귀로 바꿀 때

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0)  # stratify 없음
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
print('RMSE', root_mean_squared_error(y_val, model.predict(X_val)))

model.fit(X, y)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
```

- 연속값 타깃에 `stratify=y`를 주면 ValueError가 난다.
- RMSE는 `root_mean_squared_error`(1.4부터 있음)나 `np.sqrt(mean_squared_error(...))`. `mean_squared_error(..., squared=False)`는 1.5.2에서 FutureWarning이 난다.

## 타깃이 한쪽으로 치우친 회귀 (가격, 금액)

```python
print(y.skew())                                 # 크게 양수면 오른쪽 꼬리가 길다
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, np.log1p(y_tr))                 # log(1 + y)로 학습
pred_val = np.expm1(model.predict(X_val))       # 원래 단위로 되돌린다
print('RMSE', root_mean_squared_error(y_val, pred_val))
```

- 점수는 항상 원래 단위로 되돌린 값으로 계산하고, 제출도 expm1을 한 값으로 한다.
- log1p는 y가 -1보다 커야 한다. 0이 있어도 된다.

## RMSLE가 평가지표일 때

```python
from sklearn.metrics import root_mean_squared_log_error

pred_val = np.clip(model.predict(X_val), 0, None)   # 음수 예측을 0으로
print('RMSLE', root_mean_squared_log_error(y_val, pred_val))
```

- 예측에 음수가 하나라도 있으면 `mean_squared_log_error`와 `root_mean_squared_log_error`는 ValueError다. 선형회귀 계열은 음수가 나올 수 있어 clip을 먼저 한다.

## 클래스 불균형

```python
print(y.value_counts(normalize=True))            # 비율 확인
model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=0)
model.fit(X_tr, y_tr)
print('AUC', roc_auc_score(y_val, model.predict_proba(X_val)[:, 1]))
```

- 분할할 때 `stratify=y`로 검증셋의 비율을 train과 맞춘다.
- 지표가 AUC면 불균형이어도 확률을 내면 된다. F1이나 재현율이면 `class_weight='balanced'`가 효과가 크다.

## 예측값 종류: 라벨인가 확률인가

| 지표 | 제출할 값 | 코드 |
|---|---|---|
| 정확도, F1, 정밀도, 재현율 | 라벨 | `model.predict(X_test)` |
| ROC AUC (이진) | 양성 클래스 확률 | `model.predict_proba(X_test)[:, 1]` |
| 다중분류 macro F1 | 라벨 | `model.predict(X_test)` |
| 회귀 지표 전부 | 예측값 | `model.predict(X_test)` |

```python
print(model.classes_)                          # predict_proba 열 순서
pos = list(model.classes_).index(1)            # 양성 클래스가 몇 번째 열인지
proba = model.predict_proba(X_val)[:, pos]
```

- `predict_proba` 열은 `classes_` 순서(정렬 순)다. 타깃이 'No', 'Yes' 같은 문자열이면 `[:, 1]`은 'Yes'다. 문제가 묻는 클래스가 몇 번째인지 `classes_`로 확인한다.
- AUC 문제에 `predict`로 0과 1을 내면 점수가 크게 떨어진다.

## 평가지표 표

| 지표 | 함수 (sklearn.metrics) | 넣는 값 | 좋은 방향 |
|---|---|---|---|
| 정확도 | `accuracy_score(y_true, y_pred)` | 라벨 | 높을수록 |
| F1 (이진) | `f1_score(y_true, y_pred)` | 라벨 | 높을수록 |
| F1 (다중) | `f1_score(y_true, y_pred, average='macro')` | 라벨 | 높을수록 |
| 정밀도 | `precision_score(y_true, y_pred)` | 라벨 | 높을수록 |
| 재현율 | `recall_score(y_true, y_pred)` | 라벨 | 높을수록 |
| ROC AUC (이진) | `roc_auc_score(y_true, proba[:, 1])` | 양성 확률 | 높을수록 |
| ROC AUC (다중) | `roc_auc_score(y_true, proba, multi_class='ovr')` | 확률 전체 행렬 | 높을수록 |
| 로그 손실 | `log_loss(y_true, proba)` | 확률 | 낮을수록 |
| MAE | `mean_absolute_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| MSE | `mean_squared_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| RMSE | `root_mean_squared_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| RMSLE | `root_mean_squared_log_error(y_true, y_pred)` | 음수 없는 예측값 | 낮을수록 |
| MAPE | `mean_absolute_percentage_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| R2 | `r2_score(y_true, y_pred)` | 예측값 | 높을수록 (최대 1) |

```python
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             mean_absolute_error, mean_absolute_percentage_error, r2_score)

print(f1_score(['N', 'Y', 'Y'], ['N', 'Y', 'N'], pos_label='Y'))   # 0.666...
print(mean_absolute_percentage_error([100], [110]))               # 0.1  (10%가 아니라 0.1)
print(r2_score([1, 2, 3], [1, 2, 4]), r2_score([1, 2, 4], [1, 2, 3]))  # 순서를 바꾸면 값이 다르다
```

- 인자 순서는 항상 정답 먼저, 예측 다음이다.
- 이진 F1, 정밀도, 재현율은 양성을 1로 본다. 라벨이 문자열이면 `pos_label='Y'`처럼 주지 않으면 ValueError다.
- MAPE는 비율로 나온다. 퍼센트로 쓰려면 100을 곱한다.

## 1분 실행 제한

- 실행 한 번이 1분을 넘으면 중단된다. 랜덤포레스트는 `n_estimators=100~300` 안에서 쓴다.
- GridSearchCV나 큰 cross_val_score는 시간을 크게 잡아먹는다. 시험에서는 검증 분할 한 번으로 충분하다.
- 고유값이 수백 개인 문자열 열(주소, 이름, 날짜 문자열)을 그대로 원핫하면 열이 폭발해 느려진다. 먼저 `nunique()`로 보고 빼거나 줄인다.
- 시간이 걱정되면 학습 시간을 재 본다.

```python
import time

t0 = time.time()
RandomForestClassifier(n_estimators=200, random_state=0).fit(X_tr, y_tr)
print(round(time.time() - t0, 1), '초')
```

```python
print(train[cat_cols].nunique().sort_values(ascending=False))   # 고유값이 많은 범주 열 찾기
```

## 결측과 모델

| 모델 | NaN을 그대로 넣으면 (1.5.2) |
|---|---|
| `RandomForestClassifier`, `RandomForestRegressor` | 학습된다 |
| `HistGradientBoostingClassifier`, `HistGradientBoostingRegressor` | 학습된다 |
| `GradientBoostingClassifier`, `LogisticRegression`, `LinearRegression` | ValueError |

- 모델을 바꿔도 같은 코드가 돌게 결측은 미리 채워 두는 편이 안전하다.
- 제12회 체험환경에는 lightgbm 4.5.0과 xgboost 2.1.2도 설치돼 있다. 둘 다 결측을 그대로 받지만, 회차마다 패키지가 바뀔 수 있으니 시험장에서 버전부터 확인하고 쓴다. lightgbm은 `verbose=-1`을 줘야 학습 로그가 실행 결과에 쏟아지지 않는다.
- LogisticRegression은 스케일링이 필요하고 `max_iter`를 늘려야 경고가 사라지는 경우가 많다. 시험에서는 랜덤포레스트가 손이 덜 간다.

## 점수 잃는 실수

- `to_csv`에 `index=False`를 빼서 열이 두 개가 된다.
- 열 이름이 `pred`가 아니다. 문제에 적힌 파일 이름, 열 이름, 경로를 그대로 쓴다.
- AUC 문제에 확률 대신 0과 1을 낸다.
- test 행을 dropna로 지우거나 정렬해서 행 수나 순서가 바뀐다.
- train과 test를 따로 원핫해서 열이 맞지 않는다.
- ID 열을 특성으로 넣는다. 타깃 열을 test 쪽 concat에 같이 넣는다.
- 스케일러나 인코더를 test로 fit한다. fit은 train, test는 transform만.
- 검증 점수가 1.0처럼 지나치게 높다. 타깃에서 나온 열(누수)이 특성에 들어갔는지 본다.
- 회귀 문제에 stratify를 주거나, log1p로 학습하고 expm1 없이 제출한다.
- 저장 코드를 마지막에 실행하지 않았거나 실행이 1분을 넘어 저장 전에 멈췄다. 저장 후 `pd.read_csv('result.csv')`로 다시 읽어 확인한다.
