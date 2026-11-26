# 작업형 2 · 모델링과 제출

> 시험 버전 pandas 2.2 · numpy 1.26 · scikit-learn 1.5 기준. 아래 코드는 0절의 train, test로 위에서부터 차례로 모두 실행된다. 시험에서는 0절 대신 `pd.read_csv`로 읽고, 파일 이름과 열 이름은 문제에 맞게 바꾼다.

## 0. 공통

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score, f1_score, root_mean_squared_error

# 연습용 데이터. 시험에서는 train = pd.read_csv('data/...train.csv'), test도 같은 식
rng = np.random.default_rng(0)
def make(n):
    d = pd.DataFrame({
        'ID':     np.arange(n),
        'age':    rng.integers(20, 70, n).astype(float),
        'income': rng.lognormal(8, 0.6, n).round(),
        'region': rng.choice(['서울', '부산', '대구', '광주'], n).astype(object),
        'grade':  rng.choice(['A', 'B', 'C'], n, p=[0.5, 0.3, 0.2]),
    })
    d.loc[rng.random(n) < 0.1, 'age'] = np.nan
    d.loc[rng.random(n) < 0.05, 'region'] = np.nan
    return d

train, test = make(400), make(100)
test.loc[:2, 'grade'] = 'D'                                        # test에만 있는 범주
z = (train['age'].fillna(45) - 45) / 10 + (train['grade'] == 'A') - 1.2
train['target'] = (rng.random(400) < 1 / (1 + np.exp(-z))).astype(int)   # 분류 타깃
price = (train['income'] * rng.lognormal(0, 0.3, 400)).round()     # 3절 회귀 예시용 타깃
print(train.shape, test.shape, round(train['target'].mean(), 2))
```

| 제출 규칙 | 내용 |
|---|---|
| 파일 | `result.csv`. 문제에 적힌 경로와 이름 그대로 |
| 열 | `pred` 한 열. 문제가 다른 이름을 주면 그 이름 |
| 행 | test 행 수와 같고 순서도 test 그대로 |
| 인덱스 | `to_csv(..., index=False)` |
| 값 | AUC면 양성 확률, 정확도와 F1이면 라벨, 회귀면 예측값 |
| 실행 시간 | 실행 한 번이 1분 안 |

## 1. 무엇을 하나 → 코드

| 하고 싶은 것 | 코드 | 핵심 |
|---|---|---|
| 타깃 떼기 | `y = train.pop('target')` | train에서 빠지고 y에 담긴다 |
| ID 빼기 | `drop(columns=['ID'])` | train과 test 둘 다 |
| 숫자 열, 문자 열 | `select_dtypes(include='number')` | 문자는 `exclude='number'` |
| 숫자 결측 | `fillna(train[num_cols].median())` | 기준값은 train에서 구해 test에도 |
| 범주 결측 | `fillna('missing')` | 결측도 범주 하나로 |
| 원핫 인코딩 | `pd.get_dummies(pd.concat([train, test]), columns=cat_cols)` | `iloc`로 다시 나눈다 |
| 따로 원핫한 열 맞추기 | `X_test.reindex(columns=X.columns, fill_value=0)` | 열 이름과 순서를 train에 맞춘다 |
| 검증 분할 | `train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)` | 회귀는 stratify를 빼야 한다 |
| 분류 모델 | `RandomForestClassifier(n_estimators=200, random_state=0)` | 결측과 스케일에 덜 민감 |
| 회귀 모델 | `RandomForestRegressor(n_estimators=200, random_state=0)` | |
| 양성 확률 | `predict_proba(X_test)[:, 1]` | 열 순서는 `model.classes_` |
| 라벨 | `predict(X_test)` | |
| 불균형 | `class_weight='balanced'` | 분할은 `stratify=y` |
| 치우친 타깃 | `np.log1p(y)`로 학습, `np.expm1(pred)`로 제출 | 점수도 되돌린 값으로 |
| 음수 예측 막기 | `np.clip(pred, 0, None)` | RMSLE는 음수에서 에러 |
| 날짜 열 | `.dt.year` · `.dt.month` 뽑고 원래 열 삭제 | 문자열 그대로 원핫하지 않는다 |
| 고유값 많은 열 | `nunique()` 보고 빼기 | 원핫하면 열이 폭발한다 |
| 저장 | `pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)` | |
| 다시 읽어 확인 | `pd.read_csv('result.csv')` | 행 수, 열 이름, 결측 |

## 2. 분류 기본 템플릿

```python
print(train.shape, test.shape)
print(train.isna().sum().sum(), test.isna().sum().sum())

# 1. 타깃과 ID 떼기
y = train.pop('target')
train = train.drop(columns=['ID'])
test = test.drop(columns=['ID'])

# 2. 결측 채우기 (기준값은 train에서)
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

# 4. 검증 분할과 점수 확인
X_tr, X_val, y_tr, y_val = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y)
model = RandomForestClassifier(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
print('AUC', round(roc_auc_score(y_val, model.predict_proba(X_val)[:, 1]), 4))

# 5. 전체 train으로 다시 학습하고 test 예측
model.fit(X, y)
pred = model.predict_proba(X_test)[:, 1]

# 6. 저장
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
```

- concat하면 train이 앞, test가 뒤라서 `iloc`로 자른 순서가 원래 그대로다.
- 결측은 train에서 구한 값으로 test까지 채운다. test 행은 지우지도 정렬하지도 않는다.
- 4단계 점수는 모델을 고르는 데만 쓴다. 제출 예측은 5단계처럼 전체 train으로 다시 학습한 모델로 한다.

## 3. 회귀로 바꿀 때

2절의 1~3단계(X, X_test 만들기)는 같다. 타깃과 모델, 지표만 바꾼다.

```python
yr = price                                    # 시험에서는 train.pop('타깃열')

X_tr, X_val, yr_tr, yr_val = train_test_split(X, yr, test_size=0.2, random_state=0)   # stratify 없음
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, yr_tr)
print('RMSE', round(root_mean_squared_error(yr_val, model.predict(X_val)), 1))

model.fit(X, yr)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
```

| 분류 | 회귀 |
|---|---|
| `RandomForestClassifier` | `RandomForestRegressor` |
| `stratify=y` | 넣지 않는다. 연속값에 주면 ValueError |
| `predict_proba(...)[:, 1]` 또는 `predict` | `predict` |
| `roc_auc_score`, `f1_score` | `root_mean_squared_error`, `mean_absolute_error`, `r2_score` |

- RMSE는 `root_mean_squared_error`(1.4부터) 또는 `np.sqrt(mean_squared_error(...))`. `mean_squared_error(..., squared=False)`는 1.5에서 FutureWarning이 난다.

## 4. 전처리 · 인코딩

| 방법 | 코드 | 언제 |
|---|---|---|
| 합쳐서 원핫 | concat → `get_dummies` → `iloc` | 기본. test에만 있는 범주도 열이 생긴다 |
| 따로 원핫 후 맞추기 | `get_dummies` 두 번 → `reindex(columns=..., fill_value=0)` | test에만 있는 범주는 버려진다 |
| 정수 코드 | concat → `astype('category').cat.codes` | 범주가 많을 때, 트리 모델에만 |
| 스케일링 | `StandardScaler().fit(X_tr)` 후 `transform` | 선형 모델, KNN, SVM일 때. 트리는 필요 없다 |

```python
# 따로 원핫하고 열 맞추기
Xa = pd.get_dummies(train, columns=cat_cols)
Xb = pd.get_dummies(test, columns=cat_cols).reindex(columns=Xa.columns, fill_value=0)
print(Xa.shape, Xb.shape)
print('grade_D' in X_test.columns, 'grade_D' in Xb.columns)   # concat 쪽에만 D 열이 있다
```

```python
# 범주를 정수 코드로 (원핫 대신)
all_ = pd.concat([train, test])
for c in cat_cols:
    all_[c] = all_[c].astype('category').cat.codes
X2, X2_test = all_.iloc[:len(train)], all_.iloc[len(train):]
print(X2.dtypes.to_dict())
```

- 인코더와 스케일러는 train으로 fit하고 test는 transform만 한다. concat 방식은 범주 목록만 함께 쓰는 것이라 괜찮다.
- 타깃 열이 concat에 섞이지 않게 pop을 먼저 한다.

## 5. 평가지표

| 지표 | 함수 (sklearn.metrics) | 넣는 값 | 좋은 쪽 |
|---|---|---|---|
| 정확도 | `accuracy_score(y_true, y_pred)` | 라벨 | 높을수록 |
| F1 (이진) | `f1_score(y_true, y_pred)` | 라벨 | 높을수록 |
| F1 (다중) | `f1_score(y_true, y_pred, average='macro')` | 라벨 | 높을수록 |
| 정밀도 | `precision_score(y_true, y_pred)` | 라벨 | 높을수록 |
| 재현율 | `recall_score(y_true, y_pred)` | 라벨 | 높을수록 |
| ROC AUC (이진) | `roc_auc_score(y_true, proba[:, 1])` | 양성 확률 | 높을수록 |
| ROC AUC (다중) | `roc_auc_score(y_true, proba, multi_class='ovr')` | 확률 행렬 전체 | 높을수록 |
| 로그 손실 | `log_loss(y_true, proba)` | 확률 | 낮을수록 |
| MAE | `mean_absolute_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| MSE | `mean_squared_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| RMSE | `root_mean_squared_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| RMSLE | `root_mean_squared_log_error(y_true, y_pred)` | 음수 없는 예측값 | 낮을수록 |
| MAPE | `mean_absolute_percentage_error(y_true, y_pred)` | 예측값 | 낮을수록 |
| R2 | `r2_score(y_true, y_pred)` | 예측값 | 높을수록, 최대 1 |

```python
from sklearn.metrics import mean_absolute_percentage_error, r2_score

print(f1_score(['N', 'Y', 'Y'], ['N', 'Y', 'N'], pos_label='Y'))      # 0.666...
print(mean_absolute_percentage_error([100], [110]))                  # 0.1 (10이 아니다)
print(r2_score([1, 2, 3], [1, 2, 4]), r2_score([1, 2, 4], [1, 2, 3]))   # 순서를 바꾸면 값이 다르다
```

- 인자 순서는 언제나 정답 먼저, 예측 다음.
- 이진 F1, 정밀도, 재현율은 1을 양성으로 본다. 라벨이 문자열이면 `pos_label`을 주지 않으면 ValueError.
- MAPE는 비율로 나온다. 퍼센트는 100을 곱한다.
- AUC 문제에 `predict`로 0과 1을 내면 점수가 크게 떨어진다. 확률을 낸다.

## 6. 함정별 대처

| 보이는 것 | 할 일 |
|---|---|
| 타깃 `skew()`가 1보다 크다 (가격, 금액) | `log1p`로 학습, `expm1`로 되돌려 점수와 제출 |
| 지표가 RMSLE | 예측을 `clip(0)` 한 뒤 계산하고 제출 |
| 양성이 10~20%뿐 | `stratify=y`, F1이나 재현율이면 `class_weight='balanced'` |
| 타깃이 'Yes', 'No' 문자열 | `classes_`로 양성 열 위치 확인, F1은 `pos_label` |
| 날짜 문자열 열 | 연, 월, 요일, 경과 일수로 바꾸고 원래 열은 뺀다 |
| 검증 점수가 1.0에 가깝다 | 타깃에서 나온 열(누수)이 특성에 있는지 본다 |

치우친 타깃:

```python
print(round(yr.skew(), 2))                       # 크게 양수면 오른쪽 꼬리가 길다
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, np.log1p(yr_tr))                 # log(1 + y)로 학습
pred_val = np.expm1(model.predict(X_val))        # 원래 단위로 되돌린다
print('RMSE', round(root_mean_squared_error(yr_val, pred_val), 1))
```

- log1p는 y가 −1보다 크면 된다. 0이 있어도 괜찮다.

RMSLE:

```python
from sklearn.metrics import root_mean_squared_log_error

pred_val = np.clip(pred_val, 0, None)            # 음수 예측을 0으로
print('RMSLE', round(root_mean_squared_log_error(yr_val, pred_val), 4))
```

- 예측에 음수가 하나라도 있으면 `root_mean_squared_log_error`와 `mean_squared_log_error`는 ValueError. 선형회귀 계열은 음수가 나올 수 있다.

클래스 불균형:

```python
print(y.value_counts(normalize=True).round(2))
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=0)
model.fit(X_tr, y_tr)
print('F1', round(f1_score(y_val, model.predict(X_val)), 4))
```

문자열 타깃과 `classes_`:

```python
to_yn = {0: 'No', 1: 'Yes'}
m = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_tr, y_tr.map(to_yn))
print(m.classes_)                                # ['No' 'Yes'] 정렬 순서가 predict_proba 열 순서
pos = list(m.classes_).index('Yes')
proba = m.predict_proba(X_val)[:, pos]
print('AUC', round(roc_auc_score(y_val.map(to_yn) == 'Yes', proba), 4))
print('F1', round(f1_score(y_val.map(to_yn), m.predict(X_val), pos_label='Yes'), 4))
```

날짜 열:

```python
d = pd.DataFrame({'joined': ['2023-01-15', '2023-07-02', '2024-03-30']})
d['joined'] = pd.to_datetime(d['joined'])
d['year'], d['month'], d['dow'] = d['joined'].dt.year, d['joined'].dt.month, d['joined'].dt.dayofweek
d['days'] = (pd.Timestamp('2024-12-31') - d['joined']).dt.days     # 기준일까지 일수
d = d.drop(columns='joined')                                       # 원래 열은 모델에 넣지 않는다
print(d)
```

## 7. 제출과 확인

```python
r = pd.read_csv('result.csv')
print(r.shape, len(test))       # 행 수가 test와 같은가
print(r.columns.tolist())       # ['pred'] 한 열인가
print(r.isna().sum().sum())     # 0인가
print(r.head(3))
```

| 이렇게 나오면 | 원인 |
|---|---|
| 열이 `['Unnamed: 0', 'pred']` | `index=False`를 뺐다 |
| 행 수가 test보다 적다 | test에 `dropna`를 했다 |
| 값이 0과 1뿐인데 지표가 AUC | `predict_proba` 대신 `predict`를 썼다 |
| 값이 한 자릿수인데 타깃은 수천 단위 | log1p로 학습하고 `expm1`을 빼먹었다 |
| 결측이 있다 | test 쪽 결측을 안 채운 열이 있다 |

## 8. 1분 실행 제한

- 랜덤포레스트는 `n_estimators=100~300`이면 충분하다.
- GridSearchCV나 큰 cross_val_score는 시간을 크게 잡아먹는다. 검증 분할 한 번으로 충분하다.
- 고유값이 수백 개인 문자열 열(주소, 이름, 날짜 문자열)을 그대로 원핫하면 열이 폭발해 느려진다.

```python
import time

t0 = time.time()
RandomForestClassifier(n_estimators=200, random_state=0).fit(X_tr, y_tr)
print(round(time.time() - t0, 1), '초')

print(train[cat_cols].nunique().sort_values(ascending=False))   # 고유값이 많은 범주 열 찾기
```

## 9. 모델과 결측

| 모델 | NaN을 그대로 넣으면 (1.5) |
|---|---|
| `RandomForestClassifier`, `RandomForestRegressor` | 학습된다 |
| `HistGradientBoostingClassifier`, `HistGradientBoostingRegressor` | 학습된다 |
| `GradientBoostingClassifier`, `LogisticRegression`, `LinearRegression` | ValueError |

- 모델을 바꿔도 같은 코드가 돌게 결측은 미리 채워 두는 편이 안전하다.
- 제12회 체험환경에는 lightgbm 4.5.0과 xgboost 2.1.2도 있다. 회차마다 바뀔 수 있으니 시험장에서 버전부터 확인한다. lightgbm은 `verbose=-1`을 줘야 학습 로그가 쏟아지지 않는다.
- LogisticRegression은 스케일링을 해야 수렴이 잘 되고 `max_iter`를 늘려야 경고가 사라지는 경우가 많다. 랜덤포레스트가 손이 덜 간다.

## 10. 시험장 체크리스트

- 분류인지 회귀인지, 평가지표가 무엇인지, 제출 값이 확률인지 라벨인지 먼저 본다.
- 제출 파일 이름, 열 이름, 경로를 문제에 적힌 그대로 쓴다.
- ID 열을 특성에서 뺐는지, 타깃 열이 test 쪽 concat에 섞이지 않았는지 본다.
- train과 test를 같은 열로 맞췄는지 본다. 따로 원핫했다면 reindex.
- 회귀에 stratify를 주지 않았는지, log1p로 학습했다면 expm1으로 되돌렸는지 본다.
- 저장 코드가 마지막에 실제로 실행됐는지 `pd.read_csv('result.csv')`로 다시 읽어 확인한다.
