# 작업형 1 · pandas로 데이터 다루기

> 할 일 → 함수 → 핵심 인자 순서로 정리했다. 코드는 시험 환경 버전(pandas 2.2.2, numpy 1.26.4, scikit-learn 1.5.2)에서 실행해 확인했다.
> 예시 열 이름: grp(범주), city(범주), x와 y(숫자, x에 결측 있음), score(숫자), date(날짜 문자열), name(문자열).

## 시작과 답 확인

```python
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')   # 경로는 문제에 적힌 그대로 쓴다
print(df.shape)
print(df.head())
```

| 할 일 | 코드 | 메모 |
|---|---|---|
| 행 수, 열 수 | `df.shape` | 행 수만은 `len(df)` |
| 자료형과 결측 아닌 개수 | `df.info()` | 출력만 하고 None을 돌려준다 |
| 숫자 열 요약 | `df.describe()` | std는 ddof=1 |
| 문자열 열 요약 | `df.describe(include='object')` | count, unique, top, freq |
| 고유값 개수 | `df['grp'].nunique()` | NaN은 세지 않는다 |
| 값별 빈도 | `df['grp'].value_counts()` | 많은 순, NaN 제외(`dropna=False`면 포함) |
| 값별 비율 | `df['grp'].value_counts(normalize=True)` | 합이 1 |
| 가장 흔한 값 | `df['grp'].value_counts().idxmax()` | `df['grp'].mode()[0]`도 같다 |

- 작업형 1은 print로 값을 확인한 뒤 답안 칸에 옮겨 적는다. 문제가 정한 형식(정수, 소수 몇째 자리)에 맞춘다.
- 답이 Series 한 칸이면 `.iloc[0]`이나 `.item()`으로 값만 꺼내 출력한다.

## 반올림과 버림

```python
import math

print(round(2.5), round(3.5))      # 2 4   짝수 쪽으로 간다(은행가 반올림)
print(round(2.675, 2))             # 2.67  2.675를 정확히 저장하지 못해서
print(int(3.9), int(-3.9))         # 3 -3  0 쪽으로 버림
print(math.floor(-3.9), math.ceil(3.1))  # -4 4
print(math.floor(3.14159 * 100) / 100)   # 3.14  소수 둘째 자리 아래 버림
print(pd.Series([0.5, 1.5, 2.5]).round().tolist())  # [0.0, 2.0, 2.0]  pandas도 짝수 쪽
```

| 하고 싶은 것 | 코드 | 결과 자료형 |
|---|---|---|
| 소수 n째 자리까지 반올림 | `round(v, 2)` | float |
| 정수로 반올림 | `round(v)` | int |
| 소수점 아래 버림 | `int(v)` | int |
| 음수까지 아래로 버림 | `math.floor(v)` | int |
| Series 전체 반올림 | `s.round(2)` | Series |

> 정확히 .5로 끝나는 값에서만 round가 사사오입과 달라진다. 평균처럼 계산된 값은 대개 .5로 딱 떨어지지 않으므로 round로 충분하다. 정수 값을 반올림해야 할 때만 조심한다.

## 조건으로 행 고르기

```python
df[(df['x'] >= 30) & (df['grp'] == 'B')]     # 그리고
df[(df['x'] < 20) | (df['y'] > 5)]           # 또는
df[~(df['grp'] == 'A')]                      # 아니다
df[df['grp'].isin(['A', 'C'])]               # 여러 값 중 하나
df[~df['grp'].isin(['A', 'C'])]              # 여러 값이 아닌 것
df[df['x'].between(20, 50)]                  # 20 이상 50 이하
df.query("x >= 30 and grp == 'B'")           # 문자열로 쓰는 조건
df.loc[df['x'] > 30, 'y'].mean()             # 조건 + 열 선택 + 계산
print(((df['x'] > 30) & (df['y'] < 5)).sum())  # 조건을 만족하는 행 수
```

- 조건마다 괄호를 친다. `&`가 `>=`보다 먼저 계산되기 때문이다.
- `and`, `or`를 쓰면 ValueError가 난다. Series끼리는 `&`, `|`, `~`.
- `between`은 양 끝을 포함한다. 바꾸려면 `inclusive='left'`, `'right'`, `'neither'`.
- NaN은 `>`, `<`, `==` 비교에서 False라 조건에서 빠진다. 반대로 `!=`와 `~(조건)`에서는 True가 되어 들어온다.

## 정렬, 상위 k개, k번째 값

```python
df.sort_values('x', ascending=False)                    # 내림차순, NaN은 맨 뒤
df.sort_values(['x', 'y'], ascending=[False, True])     # x 내림차순, 같으면 y 오름차순
df.nlargest(3, 'x')                                     # x 상위 3행
df.nsmallest(3, 'x')                                    # x 하위 3행
df.nlargest(3, 'score', keep='all')                     # 3등과 동점인 행까지 모두
df.sort_values('x', ascending=False).iloc[2]            # 3번째 행 (iloc은 0부터)
df['x'].sort_values(ascending=False).iloc[2]            # 3번째로 큰 값
df.sort_values('x').reset_index(drop=True)              # 정렬 후 인덱스 새로 매기기
```

상위 k개 값을 k번째 값으로 바꾸기 (자주 나오는 유형):

```python
k = 3
v = df['x'].sort_values(ascending=False).iloc[k - 1]   # k번째로 큰 값
idx = df['x'].nlargest(k).index
df.loc[idx, 'x'] = v
print(df['x'].mean())
```

순위 매기기 `rank`:

```python
s = pd.Series([90, 85, 85, 70])
print(s.rank(ascending=False).tolist())                  # [1.0, 2.5, 2.5, 4.0]  average
print(s.rank(method='min', ascending=False).tolist())    # [1.0, 2.0, 2.0, 4.0]
print(s.rank(method='dense', ascending=False).tolist())  # [1.0, 2.0, 2.0, 3.0]
print(s.rank(method='first', ascending=False).tolist())  # [1.0, 2.0, 3.0, 4.0]
```

| method | 동점 처리 | 다음 순위 |
|---|---|---|
| `average` (기본) | 평균 순위 | 건너뜀 |
| `min` | 가장 작은 순위 | 건너뜀 (1, 2, 2, 4) |
| `dense` | 가장 작은 순위 | 이어짐 (1, 2, 2, 3) |
| `first` | 먼저 나온 행이 앞 | 동점 없음 |

- rank 결과는 float다. 정수로 쓰려면 `.astype(int)`.
- 큰 값이 1등이려면 `ascending=False`.

## 그룹별 집계

```python
df.groupby('grp')['x'].mean()                              # 그룹별 평균 (Series)
df.groupby('grp')['x'].agg(['mean', 'sum', 'count'])       # 여러 통계
df.groupby('grp').agg(x_mean=('x', 'mean'), y_max=('y', 'max'))  # 열 이름 직접 지정
df.groupby(['grp', 'city'])['x'].sum().reset_index()       # 두 기준, 결과를 표로
df.groupby('grp').size()                                   # 그룹별 행 수 (NaN 행 포함)
df.groupby('grp')['x'].count()                             # 그룹별 x 결측 아닌 개수
```

```python
g = df.groupby('grp')['x'].mean()
print(g.idxmax(), g.max())                       # 평균이 가장 큰 그룹과 그 값
print(g.sort_values(ascending=False).index[1])   # 두 번째로 큰 그룹
print(df.loc[df['x'].idxmax(), 'name'])          # x가 가장 큰 행의 name
print(df.loc[df.groupby('grp')['x'].idxmax()])   # 그룹마다 x가 가장 큰 행
```

```python
df['x_grp_mean'] = df.groupby('grp')['x'].transform('mean')   # 행마다 자기 그룹 평균
df['x_diff'] = df['x'] - df['x_grp_mean']
df[df['x'] > df['x_grp_mean']]                                # 그룹 평균보다 큰 행
```

| 함수 | 결과 길이 | 쓰임 |
|---|---|---|
| `agg`, `mean` 등 | 그룹 수 | 그룹 요약표 |
| `transform` | 원래 행 수 | 행마다 그룹 값 붙이기, 그룹별 결측 채우기 |
| `filter` | 조건을 만족한 그룹의 행 | `df.groupby('grp').filter(lambda t: len(t) >= 3)` |

- pandas 2에서는 문자열 열이 섞인 채로 `df.groupby('grp').mean()`을 하면 TypeError가 난다. 열을 먼저 고르거나 `numeric_only=True`를 준다.
- `idxmax`는 위치가 아니라 인덱스 이름을 돌려준다. 그래서 `loc`과 짝을 맞춘다.

## 피벗, 녹이기, 합치기

```python
pd.pivot_table(df, index='grp', columns='city', values='x', aggfunc='mean', fill_value=0)
pd.crosstab(df['grp'], df['city'])        # 빈도표
long = df.melt(id_vars=['id'], value_vars=['x', 'y'], var_name='item', value_name='val')
print(long.shape)                          # (행 수 x 2, 3)
```

```python
a = pd.DataFrame({'id': [1, 2, 3], 'grp': ['A', 'B', 'C']})
b = pd.DataFrame({'id': [1, 2, 4], 'amt': [10, 20, 40]})
print(pd.merge(a, b, on='id', how='inner').shape)   # (2, 3)  양쪽에 다 있는 id
print(pd.merge(a, b, on='id', how='left').shape)    # (3, 3)  a 기준, 없는 amt는 NaN
print(pd.merge(a, b, on='id', how='outer').shape)   # (4, 3)
print(pd.concat([a, a], ignore_index=True).shape)   # (6, 2)  위아래로 쌓기
print(pd.concat([a, b], axis=1).shape)              # (3, 4)  옆으로 붙이기 (인덱스 기준)
```

- pivot_table의 aggfunc 기본값은 mean이다. 개수가 필요하면 `aggfunc='count'`나 crosstab.
- 열 이름이 다르면 `left_on='id', right_on='cust_id'`.

## 결측값

```python
print(df.isna().sum())             # 열별 결측 수
print(df.isna().sum().sum())       # 전체 결측 수
print(df['x'].isna().mean())       # x 결측 비율
print(df[df['x'].isna()])          # x가 결측인 행
```

```python
df['x'] = df['x'].fillna(df['x'].mean())       # 평균
df['x'] = df['x'].fillna(df['x'].median())     # 중앙값
df['city'] = df['city'].fillna(df['city'].mode()[0])   # 최빈값
df['x'] = df['x'].fillna(df.groupby('grp')['x'].transform('median'))  # 그룹별 중앙값
df['x'] = df['x'].ffill()                      # 앞 값으로 (fillna(method='ffill')는 경고)
df['x'] = df['x'].fillna(0)
```

```python
df2 = df.dropna()                  # 결측이 하나라도 있는 행 제거
df2 = df.dropna(subset=['x'])      # x가 결측인 행만 제거
df2 = df.dropna(axis=1)            # 결측이 있는 열 제거
df2 = df.dropna(thresh=5)          # 값이 5개 이상 있는 행만 남김
```

- `df['x'].fillna(v, inplace=True)`는 2.2에서 FutureWarning이 나고 앞으로 원본을 안 바꾸게 된다. 항상 `df['x'] = df['x'].fillna(v)`로 쓴다.
- `mode()`는 Series를 돌려준다. 최빈값이 여럿이면 정렬되어 나오고 `[0]`은 그중 가장 작은 값이다.
- 채우기 전 값(평균, 중앙값)을 먼저 변수에 받아 두면 전후 비교 문제에서 헷갈리지 않는다.

## 중복

```python
print(df.duplicated().sum())                         # 모든 열이 같은 행 수 (처음 것은 제외)
print(df.duplicated(subset=['grp', 'city']).sum())   # 특정 열 기준
df2 = df.drop_duplicates()                           # keep='first' 기본
df2 = df.drop_duplicates(subset=['grp'], keep='last')
df2 = df.drop_duplicates(subset=['grp'], keep=False) # 중복된 행은 모두 제거
```

## 이상치

IQR 기준:

```python
q1 = df['x'].quantile(0.25)
q3 = df['x'].quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
out = df[(df['x'] < lower) | (df['x'] > upper)]
print(len(out))
```

평균 ± k 표준편차, z-score 기준:

```python
m, s = df['x'].mean(), df['x'].std()
out2 = df[(df['x'] < m - 1.5 * s) | (df['x'] > m + 1.5 * s)]
z = (df['x'] - m) / s
out3 = df[z.abs() > 3]
```

- quantile은 기본이 선형 보간(`interpolation='linear'`)이고 NaN을 건너뛴다. `np.percentile`도 보간 방식은 같지만 NaN이 있으면 nan이 나온다(`np.nanpercentile`을 쓴다).
- 범위 밖 값을 경계값으로 자를 때는 `df['x'].clip(lower, upper)`.
- `scipy.stats.zscore`는 ddof=0이라 pandas로 직접 계산한 z와 조금 다르다.

## 스케일링

```python
mn, mx = df['x'].min(), df['x'].max()
df['x_mm'] = (df['x'] - mn) / (mx - mn)                  # 0~1 (Min-Max)
df['x_z'] = (df['x'] - df['x'].mean()) / df['x'].std()   # 표준화, ddof=1
```

```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler

df['x_mm2'] = MinMaxScaler().fit_transform(df[['x']]).ravel()   # 손 계산과 같다
df['x_z2'] = StandardScaler().fit_transform(df[['x']]).ravel()  # ddof=0 기준
print(df['x_z2'].std(ddof=0))                                   # 1.0
```

- sklearn 스케일러에는 2차원을 넣는다. `df[['x']]`(대괄호 두 겹)이고 결과는 2차원 배열이라 `.ravel()`로 편다.
- StandardScaler는 모집단 표준편차(ddof=0)로 나눈다. pandas `std()`로 손 계산하면 값이 조금 다르다. 문제가 StandardScaler를 말하면 sklearn을 쓰거나 `std(ddof=0)`로 맞춘다.
- 두 스케일러 모두 NaN은 무시하고 학습하고, 결과에서도 NaN으로 남긴다.

## 표준편차와 분산의 ddof

| 코드 | 기본 ddof | 의미 |
|---|---|---|
| `df['x'].std()`, `df['x'].var()`, `describe()` | 1 | 표본 (n-1로 나눔) |
| `np.std(arr)`, `np.var(arr)` | 0 | 모집단 (n으로 나눔) |
| `StandardScaler` | 0 | 모집단 |
| `scipy.stats.zscore` | 0 | 모집단 |

```python
s = pd.Series([2, 4, 4, 4, 5, 5, 7, 9])
print(s.std(), s.std(ddof=0))     # 2.138... 2.0
print(np.std(s.values), np.std(s.values, ddof=1))   # 2.0 2.138...
print(np.std(pd.Series([1.0, np.nan, 3.0])))        # 1.0  Series를 넣으면 NaN은 건너뛴다
print(np.std(np.array([1.0, np.nan, 3.0])))         # nan  배열이면 nan
```

## 왜도, 첨도, 상관계수

```python
print(df['y'].skew())      # 왜도, 표본 보정값
print(df['y'].kurt())      # 첨도, 정규분포가 0인 초과첨도, 표본 보정값
print(df[['x', 'y']].corr())                       # 피어슨 상관행렬
print(df['x'].corr(df['y']))                       # 두 열 상관계수 (NaN 행은 빼고)
print(df['x'].corr(df['y'], method='spearman'))    # 스피어만
c = df.corr(numeric_only=True)['y'].drop('y')      # y와 다른 숫자 열의 상관
print(c.abs().idxmax(), c.abs().max())             # 절댓값이 가장 큰 열
```

- 문자열 열이 있으면 `df.corr()`는 pandas 2에서 ValueError다. `numeric_only=True`를 준다.
- `scipy.stats.skew`, `kurtosis`는 기본이 편향 보정 없음(`bias=True`)이라 pandas 값과 다르다. 문제에 따로 말이 없으면 pandas 값을 쓴다.

## 날짜

```python
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['dow'] = df['date'].dt.dayofweek              # 월요일 0 ... 일요일 6
df['weekend'] = df['date'].dt.dayofweek >= 5     # 토, 일
df['ym'] = df['date'].dt.to_period('M')          # 2024-01 형태의 월 단위
print(df.groupby('ym')['x'].sum())               # 월별 합계
print(df['date'].dt.day_name().head(2))          # 'Friday' 같은 요일 이름
print(df.groupby(df['date'].dt.quarter)['x'].mean())   # 분기별 평균
```

```python
d = pd.Series(['20240105', '20240212'])
print(pd.to_datetime(d, format='%Y%m%d'))       # 숫자처럼 붙은 날짜는 format 지정
n = pd.Series([20240105, 20240212])
print(pd.to_datetime(n.astype(str), format='%Y%m%d'))   # 정수면 문자열로 바꿔서
print(pd.to_datetime(pd.Series(['2024-01-05', 'bad']), errors='coerce'))  # 못 읽으면 NaT
```

기간 계산:

```python
t = pd.DataFrame({'start': ['2024-01-01 09:00', '2024-01-01 22:30'],
                  'end':   ['2024-01-01 10:30', '2024-01-03 01:00']})
t['start'] = pd.to_datetime(t['start'])
t['end'] = pd.to_datetime(t['end'])
dur = t['end'] - t['start']                     # Timedelta
print((dur.dt.total_seconds() / 60).tolist())   # [90.0, 1590.0]  전체 분
print(dur.dt.days.tolist())                     # [0, 1]  일 단위 (남는 시간은 버림)
print(dur.dt.seconds.tolist())                  # [5400, 9000]  일을 뺀 나머지 초만
print(t['start'] + pd.Timedelta(days=7))        # 7일 뒤
```

- 분이나 시간으로 바꿀 때는 `dt.total_seconds()`다. `dt.seconds`는 하루를 넘는 부분을 버린다.
- 시간 단위는 `dt.total_seconds() / 3600`, 일 단위 소수는 `/ 86400`.
- 날짜끼리 비교는 문자열 그대로도 된다: `df[df['date'] >= '2024-02-01']` (to_datetime 후).

## 문자열

```python
df['name'].str.split('_').str[0]              # '_' 앞부분
df['name'].str.split('_', expand=True)        # 나눈 조각을 열로
df['name'].str.contains('kim')                # 포함 여부, 정규식이 기본
df['name'].str.contains('KIM', case=False)    # 대소문자 무시
df['name'].str.contains('.', regex=False)     # 점, 괄호 같은 기호는 regex=False
df['name'].str.len()                          # 글자 수
df['name'].str.lower()                        # 소문자, upper()는 대문자
df['name'].str.strip()                        # 앞뒤 공백 제거
df['name'].str[:3]                            # 앞 3글자 (str.slice(0, 3)과 같다)
df['name'].str[-2:]                           # 뒤 2글자
df['name'].str.startswith('kim')              # endswith도 있다
df['price'].str.replace(',', '').astype(int)  # '1,000' -> 1000
pd.to_numeric(df['price'].str.replace(',', ''), errors='coerce')   # 숫자가 아니면 NaN
```

- 결측이 섞인 열에 `str.contains`를 쓰면 NaN이 섞여 필터에 쓸 수 없다. `na=False`를 준다.
- pandas 2에서 `str.replace`는 정규식이 기본 꺼짐(`regex=False`)이다. 패턴을 쓰려면 `regex=True`.
- 조건으로 셀 때: `df['name'].str.contains('kim', na=False).sum()`.

## 구간 나누기와 누적 계산

```python
pd.cut(df['score'], bins=[0, 60, 80, 100], labels=['low', 'mid', 'high'])  # (0, 60] 식으로 오른쪽 포함
pd.qcut(df['score'], q=4, labels=False)      # 개수가 같도록 4구간, 번호 0~3
df['x'].shift(1)                             # 한 칸 아래로 (이전 행 값)
df['x'].diff()                               # 이전 행과의 차이
df['x'].cumsum()                             # 누적 합
df['y'].rolling(3).mean()                    # 3행 이동평균
```

- 증가율은 `(s - s.shift(1)) / s.shift(1)`로 직접 계산한다. `pct_change()`는 결측이 있으면 2.2에서 경고가 난다.

## 시험장에서 함수가 기억 안 날 때

```python
help(pd.Series.rank)              # 인자 설명
print([m for m in dir(pd.Series.str) if not m.startswith('_')])   # str 메서드 목록
```
