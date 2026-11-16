# pandas · 집계·결합·모양 바꾸기

> 그룹별 집계, 표 합치기, 넓은 표와 긴 표 바꾸기, 순위·누적·이전 행 비교에 쓰는 pandas 함수.

## groupby 기본

- Q: `df.groupby('g')['v'].mean()`이 돌려주는 것 — g 값이 인덱스인 Series
  - 열을 두 개 이상 고르면(`[['v', 'w']]`) DataFrame이 된다.
- Q: groupby 결과의 그룹 순서 기본값 — 키 오름차순으로 정렬된다 (`sort=True`)
  - 처음 나온 순서를 유지하려면 `sort=False`.
- Q: groupby 결과에서 그룹 키를 인덱스가 아닌 일반 열로 남기는 인자 — `as_index=False`
  - 이미 집계한 뒤라면 `.reset_index()`로 같은 효과를 낸다.
- Q: 그룹 키가 결측인 행을 groupby가 다루는 기본 방식 — 빼고 묶는다 (`dropna=True`)

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['b', 'a', 'b', 'a'], 'v': [1, 2, 3, 4]})
  r = df.groupby('g', as_index=False)['v'].sum()
  print(r.columns.tolist(), r['g'].tolist(), r['v'].tolist())
  ```
  - 답: `['g', 'v'] ['a', 'b'] [6, 4]`
  - 키가 열로 남고, 키 순서(a, b)로 정렬된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', None, 'a', None],
                     'v': [1, 2, 3, 4, 5]})
  print(len(df.groupby('g')['v'].sum()), len(df.groupby('g', dropna=False)['v'].sum()))
  ```
  - 답: `2 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'sido': ['서울', '서울', '부산', '서울', '부산'],
                     'gender': ['M', 'F', 'M', 'M', 'F'],
                     'cnt': [5, 3, 4, 2, 6]})
  s = df.groupby(['sido', 'gender'])['cnt'].sum()
  print(s.loc[('서울', 'M')], s.loc['부산'].max())
  ```
  - 답: `7 6`
  - 두 열로 묶으면 MultiIndex가 된다. 튜플로 한 칸을, 바깥 키 하나로 그 아래 묶음을 꺼낸다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'region': ['N', 'S', 'N', 'E', 'S', 'N'],
                     'amt': [50, 30, 70, 20, 10, 20]})
  share = df.groupby('region')['amt'].sum() / df['amt'].sum()
  print(round(share['N'], 2), share.idxmin())
  ```
  - 답: `0.7 E`
  - 그룹 합을 전체 합으로 나누면 그룹별 비율이다.

## groupby · agg

- Q: 한 열에 여러 집계를 한 번에 거는 코드 — `agg(['mean', 'count'])`
  - 결과는 함수 이름이 열 이름인 DataFrame이다.
- Q: 열마다 다른 집계를 거는 `agg` 인자 모양 — 딕셔너리 `{'a': 'sum', 'b': 'mean'}`
- Q: 결과 열 이름을 직접 정하는 named aggregation 모양 — `agg(새이름=('열', '함수'))`
  - 예: `agg(total=('v', 'sum'), n=('v', 'count'))`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'dept': ['A', 'B', 'A', 'B', 'B'],
                     'sal': [300, 250, 340, 270, 290]})
  g = df.groupby('dept')['sal'].agg(['mean', 'count'])
  print(g.loc['B', 'mean'], g.loc['B', 'count'])
  ```
  - 답: `270.0 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['x', 'y', 'x', 'y'],
                     'a': [1, 2, 3, 4], 'b': [10, 20, 30, 50]})
  r = df.groupby('g').agg({'a': 'sum', 'b': 'max'})
  print(r.loc['y'].tolist(), r.columns.tolist())
  ```
  - 답: `[6, 50] ['a', 'b']`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['x', 'y', 'x', 'x'], 'v': [5, 1, 7, 3]})
  r = df.groupby('g').agg(total=('v', 'sum'), top=('v', 'max'))
  print(r.columns.tolist(), r.loc['x', 'total'], r.loc['x', 'top'])
  ```
  - 답: `['total', 'top'] 15 7`

## groupby · size와 count

- Q: groupby의 `size()`와 `count()`의 차이 — size는 결측 포함 행 수, count는 결측이 아닌 값의 개수
  - size는 열을 고르지 않아도 그룹마다 숫자 하나를 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'g': ['a', 'a', 'a', 'b', 'b'],
                     'v': [1, np.nan, 3, np.nan, 5]})
  print(df.groupby('g')['v'].count().tolist(), df.groupby('g').size().tolist())
  ```
  - 답: `[2, 1] [3, 2]`

## groupby · transform

- Q: 그룹 평균을 원래 행 수 그대로 붙이고 싶을 때 쓰는 메서드 — `transform('mean')`
  - `agg('mean')`은 그룹 수만큼으로 줄어들어 원래 행에 바로 붙일 수 없다.
- Q: 그룹별 평균과의 차이를 새 열로 만드는 코드 — `df['v'] - df.groupby('g')['v'].transform('mean')`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'dept': ['A', 'A', 'A', 'B', 'B'],
                     'sal': [300, 400, 500, 200, 600]})
  g_mean = df.groupby('dept')['sal'].transform('mean')
  print(g_mean.tolist(), (df['sal'] > g_mean).sum())
  ```
  - 답: `[400.0, 400.0, 400.0, 400.0, 400.0] 2`
  - 두 부서 평균이 같은 400이지만, 비교는 행마다 자기 부서 평균과 한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', 'a', 'b', 'a'], 'v': [2, 10, 4, 30, 6]})
  print(len(df.groupby('g')['v'].agg('sum')), df.groupby('g')['v'].transform('sum').tolist())
  ```
  - 답: `2 [12, 40, 12, 40, 12]`

## groupby · filter

- Q: 조건을 만족하는 그룹의 행만 남기는 메서드 — `groupby(...).filter(함수)`
  - 함수는 그룹 하나(DataFrame)를 받아 True/False를 돌려준다. 결과는 원래 행들이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', 'a', 'c', 'a', 'b'],
                     'v': [1, 5, 2, 9, 3, 6]})
  r = df.groupby('g').filter(lambda x: len(x) >= 2)
  print(len(r), r['v'].sum())
  ```
  - 답: `5 17`
  - 행이 하나뿐인 c 그룹만 빠진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', 'a', 'c', 'a', 'b'],
                     'v': [1, 5, 2, 9, 3, 6]})
  r = df.groupby('g').filter(lambda x: x['v'].mean() > 4)
  print(sorted(r['g'].unique().tolist()))
  ```
  - 답: `['b', 'c']`
  - 평균은 a 2, b 5.5, c 9다.

## pivot_table

- Q: `pivot_table`의 `aggfunc` 기본값 — `'mean'`
  - 합계가 필요하면 `aggfunc='sum'`, 개수는 `'count'`.
- Q: 조합이 없어 생긴 빈 칸을 채우는 `pivot_table` 인자 — `fill_value`
- Q: 행·열 합계(또는 평균) 줄을 덧붙이는 인자 — `margins=True`
  - 덧붙는 줄과 열의 이름은 `'All'`이고, 값은 aggfunc로 계산한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'store': ['A', 'A', 'B', 'B', 'A'],
                     'month': [1, 1, 1, 2, 2],
                     'sales': [10, 30, 50, 70, 40]})
  pt = pd.pivot_table(df, index='store', columns='month', values='sales')
  print(pt.loc['A', 1], pt.isna().sum().sum())
  ```
  - 답: `20.0 0`
  - 기본 집계가 평균이라 A의 1월은 (10 + 30) / 2다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'store': ['A', 'A', 'B', 'C'],
                     'month': [1, 2, 1, 2],
                     'sales': [10, 20, 30, 40]})
  pt = pd.pivot_table(df, index='store', columns='month', values='sales',
                      aggfunc='sum', fill_value=0, margins=True)
  print(pt.loc['C', 1], pt.loc['All', 'All'], pt.loc['A', 'All'])
  ```
  - 답: `0 100 30`

## crosstab

- Q: `pd.crosstab(a, b)`가 기본으로 세는 것 — 두 범주 조합의 빈도
  - 카이제곱 독립성 검정의 분할표를 만들 때 바로 쓴다.
- Q: `crosstab`의 `normalize` 값별 뜻 — `'index'`는 행 합이 1, `'columns'`는 열 합이 1, `True`는 전체 합이 1

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'gender': ['M', 'F', 'M', 'F', 'M', 'M'],
                     'buy': ['Y', 'Y', 'N', 'N', 'Y', 'Y']})
  ct = pd.crosstab(df['gender'], df['buy'], normalize='index')
  print(ct.loc['M', 'Y'], ct.loc['F', 'Y'])
  ```
  - 답: `0.75 0.5`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'gender': ['M', 'F', 'M', 'F', 'M', 'M'],
                     'buy': ['Y', 'Y', 'N', 'N', 'Y', 'Y']})
  ct = pd.crosstab(df['gender'], df['buy'])
  print(ct.shape, ct.loc['M', 'Y'], round(pd.crosstab(df['gender'], df['buy'], normalize=True).loc['F', 'N'], 4))
  ```
  - 답: `(2, 2) 3 0.1667`
  - 전체 6명 중 F이면서 N은 1명이다.

## pd.merge

- Q: `pd.merge`의 `how` 기본값 — `'inner'`
  - 왼쪽 행을 모두 남기려면 `how='left'`, 양쪽 모두는 `'outer'`. 짝이 없는 칸은 NaN이 된다.
- Q: 두 표의 키 열 이름이 서로 다를 때 쓰는 merge 인자 — `left_on`, `right_on`
- Q: 키가 아닌 열 이름이 양쪽에 같을 때 merge가 붙이는 기본 접미사 — `_x`, `_y`
  - `suffixes=('_l', '_r')`처럼 바꿀 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'id': [1, 2, 3, 4], 'x': [10, 20, 30, 40]})
  b = pd.DataFrame({'id': [2, 4, 5], 'y': ['p', 'q', 'r']})
  inner = pd.merge(a, b, on='id')
  left = pd.merge(a, b, on='id', how='left')
  outer = pd.merge(a, b, on='id', how='outer')
  print(len(inner), len(left), len(outer), left['y'].isna().sum())
  ```
  - 답: `2 4 5 2`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'k': ['A', 'A', 'B'], 'v1': [1, 2, 3]})
  b = pd.DataFrame({'k': ['A', 'A', 'B', 'C'], 'v2': [7, 8, 9, 0]})
  print(len(pd.merge(a, b, on='k')))
  ```
  - 답: `5`
  - 키가 양쪽에서 중복되면 짝을 모두 만든다. A는 2 × 2 = 4행, B는 1행.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'id': [1, 2], 'score': [70, 80]})
  b = pd.DataFrame({'id': [1, 2], 'score': [90, 60]})
  m1 = pd.merge(a, b, on='id')
  m2 = pd.merge(a, b, on='id', suffixes=('_mid', '_fin'))
  print(m1.columns.tolist(), m2.columns.tolist())
  ```
  - 답: `['id', 'score_x', 'score_y'] ['id', 'score_mid', 'score_fin']`

- Q: 빈칸을 채우면?
  ```text
  import pandas as pd
  users = pd.read_csv('users.csv')    # 키 열: user_id
  orders = pd.read_csv('orders.csv')  # 키 열: uid
  # 모든 사용자를 남기고 주문 정보를 붙인다
  m = pd.merge(users, orders, ①='user_id', ②='uid', how=③)
  ```
  - 답: `① left_on ② right_on ③ 'left'`

## pd.concat

- Q: `pd.concat([a, b])`의 기본 방향 — 위아래로 붙인다 (`axis=0`)
  - 옆으로 붙이려면 `axis=1`. 이때는 인덱스가 같은 행끼리 맞춰진다.
- Q: 위아래로 붙인 뒤 인덱스를 0부터 다시 매기는 인자 — `ignore_index=True`
  - 안 주면 원래 인덱스가 겹친 채 남아 `loc[0]`이 여러 행을 돌려준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'v': [1, 2]})
  b = pd.DataFrame({'v': [3, 4, 5]})
  c1 = pd.concat([a, b])
  c2 = pd.concat([a, b], ignore_index=True)
  print(c1.index.tolist(), len(c1.loc[0]), c2.index.tolist())
  ```
  - 답: `[0, 1, 0, 1, 2] 2 [0, 1, 2, 3, 4]`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'x': [1, 2]})
  b = pd.DataFrame({'y': [3, 4], 'z': [5, 6]})
  c = pd.concat([a, b], axis=1)
  print(c.shape, c.columns.tolist())
  ```
  - 답: `(2, 3) ['x', 'y', 'z']`

## pd.melt

- Q: 넓은 표의 여러 열을 (변수 이름, 값) 두 열로 세워 긴 표로 만드는 함수 — `pd.melt`
  - 남길 열은 `id_vars`, 녹일 열은 `value_vars`, 새 열 이름은 `var_name`, `value_name`.
- Q: `var_name`과 `value_name`을 주지 않을 때 새 열 이름 — `variable`과 `value`
- Q: melt와 반대로 긴 표를 넓은 표로 펼치는 함수 — `pivot` 또는 `pivot_table`
  - 같은 (행, 열) 조합이 여러 번 나오면 pivot은 오류가 나고 pivot_table은 집계한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'id': [1, 2, 3], 'kor': [80, 90, 70], 'eng': [60, 85, 95]})
  m = pd.melt(df, id_vars='id', var_name='subject', value_name='score')
  print(m.shape, m.groupby('subject')['score'].mean()['eng'])
  ```
  - 답: `(6, 3) 80.0`
  - 학생 3명 × 과목 2개 = 6행이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'id': [1, 2], 'q1': [5, 6], 'q2': [7, 8], 'q3': [9, 1]})
  m = pd.melt(df, id_vars='id', value_vars=['q1', 'q3'])
  print(m.columns.tolist(), len(m), m['value'].sum())
  ```
  - 답: `['id', 'variable', 'value'] 4 21`
  - value_vars에 없는 q2는 결과에서 빠진다.

## rank

- Q: `rank()`의 기본 `method`와 동점 처리 — `'average'`, 동점이면 차지하는 순위들의 평균을 준다
  - 결과는 실수(float)다.
- Q: `rank`의 method 값 `'min'`·`'dense'`·`'first'`의 차이 — min은 동점에 가장 작은 순위, dense는 min처럼 주되 다음 순위를 건너뛰지 않음, first는 나온 순서대로
- Q: 가장 큰 값을 1등으로 매기는 인자 — `ascending=False`
  - 기본은 가장 작은 값이 1이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([90, 80, 90, 70])
  print(s.rank().tolist(), s.rank(ascending=False, method='min').tolist())
  ```
  - 답: `[3.5, 2.0, 3.5, 1.0] [1.0, 3.0, 1.0, 4.0]`
  - 내림차순 min에서는 90 둘이 1등, 80은 3등이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([90, 80, 90, 70])
  print(s.rank(ascending=False, method='dense').tolist(), s.rank(ascending=False, method='first').tolist())
  ```
  - 답: `[1.0, 2.0, 1.0, 3.0] [1.0, 3.0, 2.0, 4.0]`
  - dense는 다음 순위를 건너뛰지 않고, first는 먼저 나온 90을 1등으로 둔다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'a', 'b', 'b', 'b'], 'v': [5, 9, 1, 7, 3]})
  df['r'] = df.groupby('g')['v'].rank(ascending=False)
  print(df['r'].tolist())
  ```
  - 답: `[2.0, 1.0, 3.0, 1.0, 2.0]`
  - 그룹마다 따로 순위를 매긴다.

## cumsum · cumcount

- Q: 그룹마다 따로 누적합을 구하는 코드 — `df.groupby('g')['v'].cumsum()`
  - 결과는 원래 행 순서·길이 그대로 나온다.
- Q: 그룹 안에서 몇 번째 행인지를 0부터 매기는 메서드 — `groupby(...).cumcount()`
  - 1부터 세려면 `+ 1`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([30, 25, 20, 40, 10], index=['d1', 'd2', 'd3', 'd4', 'd5'])
  cum = s.cumsum()
  print(cum.tolist(), (cum >= 70).idxmax())
  ```
  - 답: `[30, 55, 75, 115, 125] d3`
  - 불리언 Series에서 `idxmax`는 처음 True가 나오는 라벨이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', 'a', 'a', 'b'], 'v': [1, 2, 3, 4, 5]})
  print(df.groupby('g')['v'].cumsum().tolist(), df.groupby('g').cumcount().tolist())
  ```
  - 답: `[1, 2, 4, 8, 7] [0, 0, 1, 2, 1]`

## shift · diff · pct_change

- Q: 직전 행의 값을 옆에 붙여 lag 피처를 만드는 메서드 — `shift(1)`
  - 첫 행은 앞 값이 없어 NaN. `shift(-1)`은 다음 행 값을 끌어온다.
- Q: `s.diff()`와 같은 계산 — `s - s.shift(1)`
- Q: `pct_change()`가 계산하는 값 — (이번 값 - 이전 값) / 이전 값
  - 첫 행은 NaN이다. 백분율이 필요하면 100을 곱한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([100, 120, 90, 150, 140])
  diff = s.diff()
  print(diff.isna().sum(), diff.max(), diff.idxmax())
  ```
  - 답: `1 60.0 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'a', 'b', 'a', 'b'],
                     'v': [1, 2, 10, 3, 20]})
  df['lag'] = df.groupby('g')['v'].shift(1)
  print(df['lag'].tolist())
  ```
  - 답: `[nan, 1.0, nan, 2.0, 10.0]`
  - 그룹이 바뀌면 이전 그룹 값을 끌어오지 않는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([200, 250, 225, 300], index=['1월', '2월', '3월', '4월'])
  rate = s.pct_change()
  print(rate.round(3).tolist(), rate.idxmax())
  ```
  - 답: `[nan, 0.25, -0.1, 0.333] 4월`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([5, 8, 6])
  print(s.shift(-1).tolist(), s.diff(2).tolist())
  ```
  - 답: `[8.0, 6.0, nan] [nan, nan, 1.0]`
  - `diff(2)`는 두 행 앞 값과의 차이다.

## apply · map

- Q: Series의 각 값에 함수를 하나씩 적용하는 메서드 — `s.apply(함수)` 또는 `s.map(함수)`
  - 딕셔너리로 값을 바꿀 때는 `map`을 쓴다.
- Q: `df.apply(함수)`의 기본 방향 — 열마다 적용한다 (`axis=0`)
  - 행마다 여러 열 값을 함께 쓰려면 `axis=1`.
- Q: `map(딕셔너리)`에서 딕셔너리에 없는 값의 결과 — NaN
  - 없는 값을 그대로 두려면 `replace`를 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 2, 3], 'b': [10, 20, 30]})
  print(df.apply(sum).tolist(), df.apply(lambda r: r['a'] * r['b'], axis=1).tolist())
  ```
  - 답: `[6, 60] [10, 40, 90]`
  - 기본은 열마다 sum을 해서 열 수만큼, axis=1이면 행 수만큼 나온다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([72, 45, 88, 60])
  print(s.apply(lambda x: 'P' if x >= 60 else 'F').tolist())
  ```
  - 답: `['P', 'F', 'P', 'P']`
