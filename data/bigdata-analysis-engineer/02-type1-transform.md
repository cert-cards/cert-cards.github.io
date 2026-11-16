# 작업형 1 · 시계열·문자열·변형

> 날짜·문자열·모양 바꾸기 문제. 코드는 전부 직접 만든 작은 데이터이고, 답은 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다.

## 날짜 변환과 dt 접근자

- Q: 문자열 날짜 열을 날짜형으로 바꾸는 함수 — `pd.to_datetime`
  - 바꾸지 않은 문자열 열에 `.dt`를 쓰면 AttributeError가 난다.
- Q: `dt.dayofweek`에서 월요일과 일요일의 값 — 월요일 0, 일요일 6
  - 그래서 주말은 `dt.dayofweek >= 5`. 요일 이름이 필요하면 `dt.day_name()`.
- Q: 날짜로 바꿀 수 없는 값을 오류 대신 NaT로 두는 `to_datetime` 인자 — `errors='coerce'`
  - NaT가 섞인 열에서 `dt.month`를 꺼내면 결과가 실수형(float)이 된다.
- Q: 날짜형 열에서 시각(0~23)과 분기(1~4)를 꺼내는 속성 — `dt.hour`, `dt.quarter`
- Q: 날짜형 열을 `'2026-03'` 같은 연-월 문자열로 바꾸는 코드 — `dt.strftime('%Y-%m')`
  - 집계 키로만 쓸 거면 `dt.to_period('M')`도 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': ['2025-12-30', '2026-01-03', '2026-02-14', '2026-03-01', '2025-07-07']})
  df['date'] = pd.to_datetime(df['date'])
  print((df['date'].dt.year == 2026).sum(), df['date'].dt.month.max())
  ```
  - 답: `3 12`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  d = pd.to_datetime(pd.Series(['2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16', '2026-11-28']))
  wk = d.dt.dayofweek
  print(wk.tolist(), (wk >= 5).sum())
  ```
  - 답: `[4, 5, 6, 0, 5] 3`
  - 2026-11-14와 11-28은 토요일, 11-15는 일요일이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  print(pd.Timestamp('2026-11-28').day_name(), pd.to_datetime('05/03/2026').month)
  ```
  - 답: `Saturday 5`
  - 슬래시 날짜는 기본이 월/일/연이다. 일이 앞이면 `dayfirst=True`나 `format='%d/%m/%Y'`을 준다.

## 월별·주별 집계

- Q: `resample`을 쓰기 위한 조건 — 인덱스가 DatetimeIndex여야 한다
  - 날짜가 열에 있으면 `set_index('date')`를 먼저 하거나 `resample('MS', on='date')`처럼 `on`을 준다.
- Q: `resample('W')`의 기본 주 경계 — 일요일에 끝나는 주 (`'W-SUN'`)
  - 결과 라벨도 그 주의 일요일 날짜다. 월요일에 끝나게 하려면 `'W-MON'`.
- Q: pandas 2.2부터 월말 기준 resample에 권장하는 별칭 — `'ME'`
  - 예전 `'M'`은 FutureWarning을 낸다. 월초 라벨은 `'MS'`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': pd.to_datetime(['2026-01-05', '2026-01-20', '2026-02-03',
                                             '2026-02-25', '2026-02-27', '2026-04-10']),
                     'sales': [10, 20, 5, 15, 30, 40]})
  m = df.set_index('date').resample('MS')['sales'].sum()
  print(m.tolist())
  ```
  - 답: `[30, 50, 0, 40]`
  - 거래가 없는 3월도 0으로 한 칸 생긴다. groupby로 월을 묶으면 3월은 아예 나오지 않는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': pd.to_datetime(['2026-01-05', '2026-01-20', '2026-02-03',
                                             '2026-02-25', '2026-02-27', '2026-04-10']),
                     'sales': [10, 20, 5, 15, 30, 40]})
  m = df.groupby(df['date'].dt.to_period('M'))['sales'].sum()
  print(len(m), str(m.idxmax()))
  ```
  - 답: `3 2026-02`
  - `to_period('M')`은 연-월 단위로 묶어 서로 다른 해의 같은 달이 섞이지 않는다. `dt.month`로 묶으면 섞인다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': pd.to_datetime(['2026-11-09', '2026-11-12', '2026-11-15',
                                             '2026-11-16', '2026-11-20']),
                     'n': [1, 2, 3, 4, 5]})
  w = df.resample('W', on='date')['n'].sum()
  print(str(w.index[0].date()), w.tolist())
  ```
  - 답: `2026-11-15 [6, 9]`
  - 11-09(월)부터 11-15(일)까지가 첫 주이고, 라벨은 끝나는 일요일이다.

## 날짜 차이와 Timedelta

- Q: 두 날짜 열의 차이(Timedelta)를 일 수 정수로 바꾸는 코드 — `(d2 - d1).dt.days`
  - 시간 단위가 필요하면 `.dt.total_seconds() / 3600`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'order': pd.to_datetime(['2026-03-01', '2026-03-05', '2026-03-28']),
                     'ship': pd.to_datetime(['2026-03-04', '2026-03-05', '2026-04-02'])})
  gap = (df['ship'] - df['order']).dt.days
  print(gap.tolist(), round(gap.mean(), 2))
  ```
  - 답: `[3, 0, 5] 2.67`
  - 3월은 31일까지라 03-28에서 04-02는 5일이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  td = pd.Timedelta('1 days 02:30:00')
  print(td.days, td.seconds, td.total_seconds())
  ```
  - 답: `1 9000 95400.0`
  - `seconds`는 일 단위를 뺀 나머지 초만 준다. 전체 길이는 `total_seconds()`로 구한다.

## 문자열 처리

- Q: `str.contains`의 `regex` 기본값 — `True`
  - 마침표·괄호·`+` 같은 문자를 글자 그대로 찾으려면 `regex=False`를 준다.
- Q: 문자열 앞뒤 공백을 지우는 메서드 — `str.strip()`
- Q: 문자열이 특정 글자로 시작하는 행만 고르는 메서드 — `str.startswith`
  - 끝 글자는 `str.endswith`. 둘 다 정규식이 아니라 글자 그대로 비교한다.
- Q: `str.contains`를 결측이 있는 열에 써서 불리언 인덱싱할 때 주는 인자 — `na=False`
  - 결측 자리가 NaN으로 남으면 인덱싱에서 오류가 난다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['AB-101', 'CD-205', 'AB-330', 'EF-112', 'AB-090'])
  print(s.str[:2].value_counts().idxmax(), s.str[-3:].astype(int).max())
  ```
  - 답: `AB 330`
  - `str[:2]`는 각 문자열의 앞 두 글자, `str[-3:]`은 뒤 세 글자다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['data.csv', 'report', 'img.png', 'notes'])
  print(s.str.contains('.').sum(), s.str.contains('.', regex=False).sum())
  ```
  - 답: `4 2`
  - 정규식에서 `.`은 아무 글자 하나라 모든 값에 걸린다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['Seoul', 'seoul ', 'Busan', ' SEOUL', 'busan', 'Incheon'])
  print(s.nunique(), s.str.strip().str.lower().nunique())
  ```
  - 답: `6 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['1,200원', '850원', '3,000원'])
  v = s.str.replace(',', '').str.replace('원', '').astype(int)
  print(v.sum())
  ```
  - 답: `5050`
  - 숫자로 바꾸기 전에 쉼표와 단위를 모두 지워야 `astype(int)`가 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['kim-서울-30', 'lee-부산-41', 'park-서울-25'])
  parts = s.str.split('-')
  print(parts.str[1].tolist(), parts.str[2].astype(int).sum())
  ```
  - 답: `['서울', '부산', '서울'] 96`
  - 바로 여러 열로 펼치려면 `s.str.split('-', expand=True)`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['apple', np.nan, 'banana', 'kiwi', 'Apricot'])
  print(s.str.len().max(), s.str.contains('ap', case=False, na=False).sum())
  ```
  - 답: `7.0 2`
  - 결측이 섞이면 `str.len()` 결과가 실수형이라 `7.0`이 찍힌다. `case=False`로 Apricot도 걸린다.

## 병합과 결합

- Q: `pd.merge`의 `how` 기본값 — `'inner'`
  - 왼쪽 행을 모두 남기려면 `how='left'`. 짝이 없는 칸은 NaN이 된다.
- Q: 두 표의 키 열 이름이 서로 다를 때 쓰는 merge 인자 — `left_on`, `right_on`
- Q: `pd.concat`으로 위아래로 붙인 뒤 인덱스를 0부터 다시 매기는 인자 — `ignore_index=True`
  - 안 주면 원래 인덱스가 겹친 채 남아 `loc[0]`이 여러 행을 돌려준다.
- Q: 키가 아닌 열 이름이 양쪽에 같을 때 merge가 붙이는 기본 접미사 — `_x`, `_y`
  - `suffixes=('_left', '_right')`처럼 바꿀 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'id': [1, 2, 3, 4], 'x': [10, 20, 30, 40]})
  b = pd.DataFrame({'id': [2, 4, 5], 'y': ['p', 'q', 'r']})
  inner = pd.merge(a, b, on='id')
  left = pd.merge(a, b, on='id', how='left')
  print(len(inner), len(left), left['y'].isna().sum())
  ```
  - 답: `2 4 2`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  a = pd.DataFrame({'k': ['A', 'A', 'B'], 'v1': [1, 2, 3]})
  b = pd.DataFrame({'k': ['A', 'A', 'B', 'C'], 'v2': [7, 8, 9, 0]})
  print(len(pd.merge(a, b, on='k')))
  ```
  - 답: `5`
  - 키가 양쪽에서 중복되면 짝을 모두 만든다. A는 2 × 2 = 4행, B는 1행.

## pivot_table과 melt

- Q: `pivot_table`의 `aggfunc` 기본값 — `'mean'`
  - 합계가 필요하면 `aggfunc='sum'`, 빈 칸은 `fill_value=0`으로 채운다.
- Q: 넓은 표의 여러 열을 (변수 이름, 값) 두 열로 세워 긴 표로 만드는 함수 — `pd.melt`
  - 남길 열은 `id_vars`, 녹일 열은 `value_vars`, 새 열 이름은 `var_name`, `value_name`.

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
  df = pd.DataFrame({'id': [1, 2, 3], 'kor': [80, 90, 70], 'eng': [60, 85, 95]})
  m = pd.melt(df, id_vars='id', var_name='subject', value_name='score')
  print(m.shape, m.groupby('subject')['score'].mean()['eng'])
  ```
  - 답: `(6, 3) 80.0`
  - 학생 3명 × 과목 2개 = 6행이 된다.

## 구간화 (cut·qcut)

- Q: `pd.cut`과 `pd.qcut`의 차이 — cut은 구간 경계(폭)를, qcut은 각 구간에 들어가는 개수를 같게 나눈다
  - qcut은 분위수로 경계를 정한다.
- Q: `pd.cut`의 기본 구간 모양 — 왼쪽 열림·오른쪽 닫힘 `(a, b]` (`right=True`)
  - 첫 경계값과 같은 값은 NaN이 되므로 `include_lowest=True`를 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([10, 15, 20, 25, 30])
  c = pd.cut(s, bins=[10, 20, 30], labels=['low', 'high'])
  print(c.isna().sum(), (c == 'low').sum())
  ```
  - 답: `1 2`
  - 10은 `(10, 20]`에 들지 않아 NaN이고, 20은 low에 들어간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 8, 1, 9, 5, 7, 2, 6])
  print(pd.qcut(s, 4, labels=False).tolist())
  ```
  - 답: `[1, 3, 0, 3, 1, 2, 0, 2]`
  - 8개를 4구간으로 나눠 구간마다 2개씩 들어간다. `labels=False`는 구간 번호(0부터)를 준다.

## shift·누적합·transform

- Q: 직전 행의 값을 옆에 붙여 lag 피처를 만드는 메서드 — `shift(1)`
  - 첫 행은 앞 값이 없어 NaN. 그룹마다 따로 하려면 `groupby(...)['v'].shift(1)`.
- Q: groupby 집계 결과를 원래 행 수 그대로 펼쳐 돌려주는 메서드 — `transform`
  - `df['g_mean'] = df.groupby('g')['v'].transform('mean')`처럼 새 열로 바로 붙인다.
- Q: 그룹마다 따로 누적합을 구하는 코드 — `df.groupby('g')['v'].cumsum()`
  - 결과는 원래 행 순서·길이 그대로 나온다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([100, 120, 90, 150, 140])
  diff = s - s.shift(1)
  print(diff.isna().sum(), diff.max(), diff.idxmax())
  ```
  - 답: `1 60.0 3`
  - 같은 계산을 `s.diff()`로도 할 수 있다.

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
  s = pd.Series([30, 25, 20, 40, 10], index=['d1', 'd2', 'd3', 'd4', 'd5'])
  cum = s.cumsum()
  print(cum.tolist(), (cum >= 70).idxmax())
  ```
  - 답: `[30, 55, 75, 115, 125] d3`
  - 불리언 Series에서 `idxmax`는 처음 True가 나오는 라벨이다.

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

## 보간과 앞뒤 채우기

- Q: 앞 행의 값으로 결측을 채우는 메서드 — `ffill()`
  - 뒤 행 값은 `bfill()`. `fillna(method='ffill')`은 pandas 2.1부터 deprecated다.
- Q: `interpolate()`의 기본 방법 — `'linear'`
  - 인덱스 간격을 무시하고 행이 같은 간격이라고 보고 잇는다. 날짜 간격을 반영하려면 `method='time'`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([1, np.nan, np.nan, 4, np.nan])
  print(s.interpolate().tolist())
  ```
  - 답: `[1.0, 2.0, 3.0, 4.0, 4.0]`
  - 마지막 결측은 뒤에 값이 없어 앞 값(4)을 그대로 이어 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([np.nan, 5, np.nan, np.nan, 8])
  print(s.ffill().isna().sum(), s.bfill().tolist())
  ```
  - 답: `1 [5.0, 5.0, 8.0, 8.0, 8.0]`
  - 첫 값이 결측이면 ffill로는 채울 앞 값이 없다.

## 비율 계산

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'region': ['N', 'S', 'N', 'E', 'S', 'N'],
                     'amt': [50, 30, 70, 20, 10, 20]})
  share = df.groupby('region')['amt'].sum() / df['amt'].sum()
  print(round(share['N'], 2), share.idxmin())
  ```
  - 답: `0.7 E`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'gender': ['M', 'F', 'M', 'F', 'M', 'M'],
                     'buy': ['Y', 'Y', 'N', 'N', 'Y', 'Y']})
  ct = pd.crosstab(df['gender'], df['buy'], normalize='index')
  print(ct.loc['M', 'Y'], ct.loc['F', 'Y'])
  ```
  - 답: `0.75 0.5`
  - `normalize='index'`는 행마다 합이 1이 되게 나눈다. 열 기준은 `'columns'`, 전체 기준은 `True`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([200, 250, 225, 300], index=['1월', '2월', '3월', '4월'])
  rate = s.pct_change()
  print(rate.round(3).tolist(), rate.idxmax())
  ```
  - 답: `[nan, 0.25, -0.1, 0.333] 4월`
  - 증감률은 (이번 값 - 이전 값) / 이전 값이다.
