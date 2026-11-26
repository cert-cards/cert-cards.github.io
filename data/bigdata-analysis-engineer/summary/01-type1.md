# 작업형 1 · 데이터 처리

> 시험 버전 pandas 2.2 · numpy 1.26 기준. 아래 코드는 0절의 작은 df 하나로 모두 실행된다. 답은 print로 확인하고 제출 형식(정수, 소수 몇째 자리)에 맞춰 옮겨 적는다.

## 0. 공통

```python
import pandas as pd
import numpy as np
import math

df = pd.DataFrame({
    'id':    [1, 2, 3, 4, 5, 6, 7, 8],
    'grp':   ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B'],
    'x':     [30, 45, np.nan, 52, 38, 61, np.nan, 47],
    'y':     [3.2, 4.1, 2.8, 5.5, 3.9, 6.1, 4.4, 4.0],
    'date':  ['2024-01-05', '2024-01-06', '2024-02-10', '2024-02-11',
              '2024-03-01', '2024-03-02', '2024-03-15', '2024-04-20'],
    'name':  ['kim_a', 'lee_b', 'park_c', 'kim_d', 'choi_e', 'kim_f', 'lee_g', 'jung_h'],
})
print(df.shape, df.isna().sum().to_dict())
```

| 하고 싶은 것 | 코드 | 결과 |
|---|---|---|
| 소수 n째 자리 반올림 | `round(v, 2)` | 정확히 .5면 짝수 쪽 (`round(2.5)` → 2) |
| 소수점 아래 버림 (양수) | `int(v)` | 음수는 0 쪽 (`int(-3.9)` → −3) |
| 아래로 버림 (음수 포함) | `math.floor(v)` | `math.floor(-3.9)` → −4 |
| 올림 | `math.ceil(v)` | |
| 소수 둘째 자리 아래 버림 | `math.floor(v * 100) / 100` | |
| Series 한 칸만 꺼내기 | `s.iloc[0]` · `s.item()` | 출력에 인덱스가 섞이지 않게 |

## 1. 무엇을 하나 → 함수

| 하고 싶은 것 | 함수 | 핵심 |
|---|---|---|
| 조건으로 행 고르기 | `df[(조건1) & (조건2)]` | 조건마다 괄호, `and`·`or` 대신 `&` `\|` `~` |
| 여러 값 중 하나 | `df['grp'].isin(['A', 'C'])` | 아닌 것은 `~` |
| 구간 안 | `df['x'].between(30, 50)` | 양 끝 포함 |
| 정렬 (동률 규칙 포함) | `sort_values(['y', 'id'], ascending=[False, True])` | NaN은 맨 뒤 |
| 상위·하위 k개 | `nlargest(k, 'x')` · `nsmallest(k, 'x')` | 동점까지 모두는 `keep='all'` |
| k번째 행 | `정렬.iloc[k - 1]` | iloc은 0부터 |
| 순위 | `rank(method='dense', ascending=False)` | 동점 처리 방식은 2절 표 |
| 그룹 통계 | `df.groupby('grp')['x'].mean()` | 결과 길이 = 그룹 수 |
| 행마다 그룹 값 붙이기 | `groupby('grp')['x'].transform('mean')` | 결과 길이 = 원래 행 수 |
| 최댓값을 가진 그룹·행 | `g.idxmax()` · `df.loc[df['x'].idxmax()]` | 인덱스 이름을 돌려준다 |
| 결측 개수 | `df.isna().sum()` | 비율은 `.mean()` |
| 결측 채우기 | `fillna(평균·중앙값·최빈값)` | 최빈값은 `mode()[0]` |
| 결측 행 지우기 | `dropna(subset=['x'])` | |
| 중복 | `duplicated().sum()` · `drop_duplicates(subset=...)` | 처음 것은 중복으로 안 센다 |
| 분위수 | `df['x'].quantile(0.75)` | 선형 보간, NaN 건너뜀 |
| 표준편차·분산 | `std()` · `var()` | pandas 기본 ddof=1, numpy 기본 0 |
| 왜도·첨도 | `skew()` · `kurt()` | 첨도는 정규분포가 0인 값 |
| 상관계수 | `df['x'].corr(df['y'])` | 스피어만은 `method='spearman'` |
| 날짜로 바꾸기 | `pd.to_datetime(df['date'])` | 붙은 숫자는 `format='%Y%m%d'` |
| 연·월·요일 | `.dt.year` · `.dt.month` · `.dt.dayofweek` | 월요일 0, 토·일은 5·6 |
| 연-월 묶기 | `.dt.to_period('M')` | 연도가 다르면 다른 연-월 |
| 시간 차이(분) | `(end - start).dt.total_seconds() / 60` | `dt.seconds`는 하루 넘는 부분을 버린다 |
| 문자열 나누기 | `str.split('_').str[0]` | 공백 여럿은 `str.split()` |
| 포함 여부 | `str.contains('kim', na=False)` | 정규식이 기본, 기호는 `regex=False` |
| 글자 수·앞 n글자 | `str.len()` · `str[:3]` | |
| 표 모양 바꾸기 | `pivot_table` · `melt` · `crosstab` | pivot_table 기본 aggfunc는 mean |
| 표 합치기 | `pd.merge(a, b, on='id', how='left')` | 쌓기는 `pd.concat` |
| 구간 나누기 | `pd.cut` · `pd.qcut` | cut은 오른쪽 끝 포함 |
| 이전 행 값·누적 | `shift(1)` · `diff()` · `cumsum()` | |

## 2. 고르기 · 정렬 · k번째

```python
print(df[(df['x'] >= 40) & (df['grp'] != 'C')]['id'].tolist())   # 조건 둘 다
print(df[df['grp'].isin(['A', 'C'])].shape[0])                    # A 또는 C인 행 수
print(df.loc[df['y'] > 4, 'x'].mean())                            # 조건 + 열 + 계산

s = df.sort_values(['y', 'id'], ascending=[False, True])   # y 내림차순, 같으면 id 오름차순
print(s.iloc[2]['name'])                                   # 3번째 행의 다른 열
print(df['y'].nlargest(3).iloc[-1])                        # 3번째로 큰 값
```

```python
r = pd.Series([90, 85, 85, 70])
print(r.rank(ascending=False).tolist())                  # [1.0, 2.5, 2.5, 4.0]
print(r.rank(method='min', ascending=False).tolist())    # [1.0, 2.0, 2.0, 4.0]
print(r.rank(method='dense', ascending=False).tolist())  # [1.0, 2.0, 2.0, 3.0]
print(r.drop_duplicates().nlargest(2).iloc[-1])          # 같은 값을 하나로 칠 때 2번째 값: 85
```

| 동률 처리 | method | 90, 85, 85, 70 |
|---|---|---|
| 평균 순위 (기본) | `average` | 1, 2.5, 2.5, 4 |
| 가장 작은 순위, 다음은 건너뜀 | `min` | 1, 2, 2, 4 |
| 가장 작은 순위, 다음은 이어짐 | `dense` | 1, 2, 2, 3 |
| 먼저 나온 행이 앞 | `first` | 1, 2, 3, 4 |

- 조건마다 괄호를 친다. `&`가 비교보다 먼저 계산된다.
- NaN은 `>`, `<`, `==`에서 False라 빠지고, `!=`와 `~(조건)`에서는 True라 들어온다.

## 3. 그룹 집계

```python
g = df.groupby('grp')['y'].mean()
print(g.idxmax(), round(g.max(), 3))                  # 평균이 가장 큰 그룹과 값
print(g.sort_values(ascending=False).index[1])        # 두 번째 그룹
print(df.groupby('grp').agg(y_mean=('y', 'mean'), n=('id', 'count')).loc['B'].tolist())
df['y_grp'] = df.groupby('grp')['y'].transform('mean')   # 행마다 자기 그룹 평균
print(df[df['y'] > df['y_grp']]['id'].tolist())          # 그룹 평균보다 큰 행
print(df.loc[df.groupby('grp')['y'].idxmax(), 'name'].tolist())   # 그룹마다 y가 가장 큰 행
```

| 함수 | 결과 길이 | 쓰임 |
|---|---|---|
| `mean` · `sum` · `agg` | 그룹 수 | 그룹 요약 |
| `transform` | 원래 행 수 | 그룹 값 붙이기, 그룹별 결측 채우기 |
| `size()` · `count()` | 그룹 수 | size는 결측 포함 행 수, count는 결측 제외 |
| `filter` | 조건 맞는 그룹의 행 | `df.groupby('grp').filter(lambda t: len(t) >= 3)` |

- 문자열 열이 섞인 채 `df.groupby('grp').mean()`은 오류다. 열을 먼저 고른다.

## 4. 결측 · 중복

```python
d = df.copy()
print(d['x'].isna().sum(), round(d['x'].isna().mean(), 3))   # 개수, 비율
d['x1'] = d['x'].fillna(d['x'].mean())
d['x2'] = d['x'].fillna(d['x'].median())
d['x3'] = d['x'].fillna(d.groupby('grp')['x'].transform('median'))   # 그룹별 중앙값
d['x4'] = d['x'].ffill()                                              # 앞 행 값
print(d['grp'].mode()[0], d.dropna(subset=['x']).shape[0])
print(d.duplicated(subset=['grp']).sum())                 # grp 기준 중복 행 수
print(d.drop_duplicates(subset=['grp'], keep='last').shape[0])
```

- 채우기는 `d['x'] = d['x'].fillna(v)`로 쓴다. `inplace=True`는 2.2에서 경고가 나고 원본이 안 바뀔 수 있다.
- 채우기 전 통계(평균·표준편차)를 먼저 변수에 받아 두면 「채우기 전후 차이」 문제가 쉽다.
- 같은 그룹 안에서 앞 날짜 값으로 채우려면 먼저 날짜로 정렬한 뒤 `groupby('grp')['x'].ffill()`.

## 5. 이상치

```python
q1, q3 = df['y'].quantile([0.25, 0.75])
iqr = q3 - q1
out_iqr = df[(df['y'] < q1 - 1.5 * iqr) | (df['y'] > q3 + 1.5 * iqr)]
m, s = df['y'].mean(), df['y'].std()              # 표본표준편차 (ddof=1)
out_sd = df[(df['y'] - m).abs() > 1.5 * s]        # 평균 ± 1.5 표준편차 밖
z = (df['y'] - m) / s
print(len(out_iqr), len(out_sd), int((z.abs() > 2).sum()))
print(df['y'].clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr).max())   # 경계로 잘라 대체
```

| 기준 | 계산 | 주의 |
|---|---|---|
| IQR | Q1 − 1.5·IQR 미만, Q3 + 1.5·IQR 초과 | 분위수는 전체 기준인지 그룹 기준인지 지문대로 |
| 평균 ± k·SD | `(x − 평균).abs() > k * std` | SD가 표본(n−1)인지 모집단(n)인지 |
| Z 점수 | `(x − 평균) / std` | 거른 부분집합에서 다시 구하라면 그 안에서 평균·SD |
| 경계로 대체 | `clip(하한, 상한)` | 제거와 대체를 헷갈리지 않는다 |

## 6. 스케일링 · ddof

```python
x = df['y']
mm = (x - x.min()) / (x.max() - x.min())          # Min-Max, 0~1
zs = (x - x.mean()) / x.std()                     # 표준화 (ddof=1)
from sklearn.preprocessing import MinMaxScaler, StandardScaler
mm2 = MinMaxScaler().fit_transform(df[['y']]).ravel()     # 2차원으로 넣고 ravel로 편다
zs2 = StandardScaler().fit_transform(df[['y']]).ravel()   # ddof=0으로 나눈다
print(round(mm.max(), 3), round(zs.std(), 3), round(zs2.std(ddof=0), 3))
print(round(x.std(), 4), round(x.std(ddof=0), 4), round(np.std(x.values), 4))
```

| 코드 | 기본 ddof | 뜻 |
|---|---|---|
| `s.std()` · `s.var()` · `describe()` | 1 | 표본 (n−1로 나눔) |
| `np.std(arr)` · `np.var(arr)` | 0 | 모집단 (n으로 나눔) |
| `StandardScaler` · `scipy.stats.zscore` | 0 | 모집단 |

- 지문이 「표본표준편차」면 ddof=1, 「모표준편차」면 ddof=0. StandardScaler를 쓰라고 하면 ddof=0 값이다.

## 7. 날짜

```python
d = df.copy()
d['date'] = pd.to_datetime(d['date'])
d['month'] = d['date'].dt.month
d['weekend'] = d['date'].dt.dayofweek >= 5         # 토(5)·일(6)
d['ym'] = d['date'].dt.to_period('M')
print(d.groupby('ym')['y'].sum().idxmax())          # 합계가 가장 큰 연-월
print(int(d['weekend'].sum()), d['date'].dt.day_name().iloc[0])
t = pd.DataFrame({'s': ['2024-01-01 22:30', '2024-01-02 09:00'], 'e': ['2024-01-02 00:15', '2024-01-02 10:30']})
dur = pd.to_datetime(t['e']) - pd.to_datetime(t['s'])
print((dur.dt.total_seconds() / 60).tolist())      # 경과 분 [105.0, 90.0], 자정을 넘어도 맞다
print(pd.to_datetime(pd.Series(['20240105']), format='%Y%m%d').iloc[0].date())
```

- 같은 「월」이라도 연도가 다르면 다른 달이다. 연-월은 `to_period('M')`, 월만은 `dt.month`.
- 날짜 범위로 거를 때: `d[(d['date'] >= '2024-02-01') & (d['date'] < '2024-03-01')]`.
- 분기는 `dt.quarter`, 시는 `dt.hour`, 일 단위 차이는 `dt.days`.

## 8. 문자열

```python
n = df['name']
print(n.str.split('_').str[0].value_counts().idxmax())   # '_' 앞부분 중 가장 많은 값
print(int(n.str.contains('kim', na=False).sum()))         # 포함하는 행 수
print(n.str.len().mean(), n.str[:2].tolist()[:3])         # 글자 수 평균, 앞 2글자
print(n.str.upper().str.startswith('KIM').sum())          # 대소문자 무시하려면 한쪽으로 맞춘다
price = pd.Series(['1,200', '980', '15,000'])
print(price.str.replace(',', '').astype(int).sum())        # 쉼표 빼고 숫자로
words = pd.Series(['good  item', 'bad'])
print(words.str.split().str.len().tolist())               # 공백 여러 칸도 단어 수 [2, 1]
```

- `str.contains`는 정규식이 기본이라 `.`, `(`, `+` 같은 기호는 `regex=False`를 준다.
- 결측이 섞인 열은 `na=False`를 줘야 필터에 쓸 수 있다.
- 「포함」과 「같다」를 구분한다. `str.contains('빵')`은 「소금빵」과 「마늘빵」 둘 다 잡는다.

## 9. 모양 바꾸기 · 합치기 · 구간

```python
pv = pd.pivot_table(df, index='grp', values='y', aggfunc='sum')
print(pv.loc['A', 'y'])
long = df.melt(id_vars='id', value_vars=['x', 'y'], var_name='item', value_name='val')
print(long.shape)                                        # 행 수 × 2
a = pd.DataFrame({'id': [1, 2, 3], 'k': ['p', 'q', 'r']})
print(pd.merge(df, a, on='id', how='left')['k'].isna().sum())   # 짝이 없는 행은 NaN
print(pd.cut(df['y'], bins=[0, 4, 5, 10], labels=['저', '중', '고']).value_counts()['저'])
print(df['y'].diff().round(1).tolist()[:3])              # 이전 행과의 차이
```

- `pivot_table`의 `aggfunc` 기본값은 평균이다. 합계면 `'sum'`, 개수면 `'count'`.
- `pd.cut`은 (0, 4], (4, 5]처럼 오른쪽 끝을 포함한다. 왼쪽을 포함하려면 `right=False`.

## 10. 자주 나오는 문제 틀

파생변수 → 정렬 → k번째 행의 다른 열:

```python
d = df.dropna(subset=['x']).copy()
d['ratio'] = d['y'] / d['x']                                   # 1) 파생
d = d.sort_values(['ratio', 'id'], ascending=[False, True])    # 2) 정렬 + 동률 규칙
print(d.iloc[2]['name'])                                       # 3) 3번째 행의 다른 열
```

그룹 평균이 가장 큰 그룹 → 그 그룹 안에서 다시 계산:

```python
best = df.groupby('grp')['y'].mean().idxmax()
sub = df[df['grp'] == best]
print(best, round(sub['y'].std(), 3))
```

상위 k개를 k번째 값으로 바꾼 뒤 평균:

```python
s = df['y'].copy()
k = 3
v = s.nlargest(k).iloc[-1]
s[s.nlargest(k).index] = v
print(round(s.mean(), 3))
```

## 11. 시험장 체크리스트

- 반올림인지 버림인지, 몇째 자리인지 먼저 본다. 버림이면 음수인지 확인한다.
- 동률 규칙, 「이상」·「초과」, 처리 순서(채우고 거르기 vs 거르고 채우기)를 지문 그대로 따른다.
- 표준편차가 표본(n−1)인지 모집단(n)인지 확인한다.
- 비율의 평균과 합계의 비율(합 ÷ 합)은 다른 값이다. 지문이 어느 쪽인지 본다.
- 거른 부분집합에서 다시 통계를 구하라는지, 전체 기준인지 본다.
- 함수가 기억나지 않으면 `help(pd.Series.rank)`, `dir(pd.Series.str)`로 찾는다.
