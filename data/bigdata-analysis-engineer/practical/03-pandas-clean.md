# pandas · 결측·이상치·변환

> 결측치와 중복을 처리하고, 분위수로 이상치를 찾고, 구간화·값 바꾸기·기술통계·스케일링에 쓰는 pandas 함수.

## isna · isnull

- Q: 열마다 결측치 개수를 세는 코드 — `df.isna().sum()`
  - `isnull()`은 `isna()`와 같은 함수다. 전체 개수는 `.sum().sum()`.
- Q: 열별 결측 비율을 구하는 코드 — `df.isna().mean()`
  - True를 1로 보고 평균을 내므로 비율이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, np.nan, 3, np.nan],
                     'b': [np.nan, 2, 3, 4],
                     'c': [1, 2, np.nan, np.nan]})
  print(df.isna().sum().tolist(), df.isna().sum().sum(), df.isna().any(axis=1).sum())
  ```
  - 답: `[2, 1, 2] 5 4`
  - 네 행 모두 어느 열인가에 결측이 하나씩 있다.

## fillna

- Q: `fillna`에 넣을 수 있는 값의 모양 — 스칼라 하나, 또는 열 이름을 키로 한 딕셔너리
  - `df.fillna({'a': 0, 'b': df['b'].mean()})`처럼 열마다 다르게 채운다.
- Q: 범주형 열의 결측을 최빈값으로 채울 때 `mode()` 뒤에 붙이는 것 — `[0]`
  - `mode()`는 최빈값이 여러 개일 수 있어 Series를 돌려준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([4, np.nan, 8, 100, np.nan, 6])
  a = s.fillna(s.mean()).mean()
  b = s.fillna(s.median()).mean()
  print(round(a, 2), round(b, 2))
  ```
  - 답: `29.5 22.0`
  - 평균 대체는 평균을 그대로 두고, 중앙값 대체(7)는 이상치(100)에 흔들리지 않아 평균이 낮아진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['red', 'blue', np.nan, 'red', np.nan, 'green'])
  s = s.fillna(s.mode()[0])
  print(s.value_counts()['red'])
  ```
  - 답: `4`
  - 최빈값 red로 결측 2개를 채운다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, np.nan, 5], 'b': [np.nan, 'x', np.nan]})
  df = df.fillna({'a': df['a'].median(), 'b': 'none'})
  print(df['a'].tolist(), df['b'].tolist())
  ```
  - 답: `[1.0, 3.0, 5.0] ['none', 'x', 'none']`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'g': ['a', 'a', 'a', 'b', 'b', 'b'],
                     'v': [10, np.nan, 30, 100, 200, np.nan]})
  df['v'] = df['v'].fillna(df.groupby('g')['v'].transform('median'))
  print(df['v'].tolist())
  ```
  - 답: `[10.0, 20.0, 30.0, 100.0, 200.0, 150.0]`
  - `transform`이 그룹 중앙값을 원래 행 위치에 펼쳐 주므로 `fillna`에 바로 넣을 수 있다.

- Q: 빈칸을 채우면?
  ```text
  import pandas as pd
  df = pd.read_csv('data.csv')
  # 'price' 결측치를 'brand'별 평균으로 채운다
  df['price'] = df['price'].fillna(df.groupby('brand')['price'].①('mean'))
  ```
  - 답: `① transform`
  - `agg('mean')`은 그룹 수만큼으로 줄어든 결과라 행 위치가 맞지 않는다.

## dropna

- Q: `dropna`의 `how` 기본값 — `'any'`
  - 하나라도 결측이면 행을 지운다. 모든 값이 결측인 행만 지우려면 `how='all'`.
- Q: 특정 열에 결측이 있는 행만 지우는 인자 — `subset=['열']`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, np.nan, np.nan, 4, 5],
                     'b': [np.nan, np.nan, 3, 4, np.nan]})
  print(len(df.dropna()), len(df.dropna(how='all')), len(df.dropna(subset=['a'])))
  ```
  - 답: `1 4 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, 2, 3], 'b': [np.nan, 2, 3], 'c': [1, np.nan, np.nan]})
  print(df.dropna(axis=1).columns.tolist(), df.dropna(thresh=2).index.tolist())
  ```
  - 답: `['a'] [0, 1, 2]`
  - `thresh=2`는 결측이 아닌 값이 2개 이상인 행을 남긴다. 세 행 모두 2개씩이다.

## ffill · bfill

- Q: 앞 행의 값으로 결측을 채우는 메서드 — `ffill()`
  - 뒤 행 값은 `bfill()`. `fillna(method='ffill')`은 pandas 2.1부터 deprecated다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([np.nan, 5, np.nan, np.nan, 8])
  print(s.ffill().isna().sum(), s.bfill().tolist())
  ```
  - 답: `1 [5.0, 5.0, 8.0, 8.0, 8.0]`
  - 첫 값이 결측이면 ffill로는 채울 앞 값이 없다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'g': ['a', 'a', 'b', 'b'], 'v': [1, np.nan, np.nan, 4]})
  print(df.groupby('g')['v'].ffill().tolist(), df['v'].ffill().tolist())
  ```
  - 답: `[1.0, 1.0, nan, 4.0] [1.0, 1.0, 1.0, 4.0]`
  - 그룹으로 나누면 b의 첫 결측은 a 값을 끌어오지 않는다.

## interpolate

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

## duplicated · drop_duplicates

- Q: `drop_duplicates`의 `keep` 기본값 — `'first'`
  - `keep='last'`는 마지막 것을 남기고, `keep=False`는 중복된 행을 전부 지운다.
- Q: 특정 열만 보고 중복을 판단하는 인자 — `subset`
  - `drop_duplicates(subset=['id'])` 또는 첫 인자로 `drop_duplicates('id')`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'id': [1, 2, 2, 3, 3, 3],
                     'v': [5, 6, 6, 7, 8, 7]})
  print(df.duplicated().sum(), len(df.drop_duplicates('id')), len(df.drop_duplicates('id', keep=False)))
  ```
  - 답: `2 3 1`
  - 행 전체가 같은 것은 (2, 6)과 (3, 7)의 두 번째 등장뿐이다. id 기준으로 중복이 아예 없는 것은 1뿐이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'id': [1, 1, 2, 2], 'v': [10, 20, 30, 40]})
  print(df.drop_duplicates('id', keep='last')['v'].tolist())
  ```
  - 답: `[20, 40]`

## quantile

- Q: pandas `quantile`의 기본 보간 방식 — `'linear'`
  - 위치 `(n-1)*q`가 정수가 아니면 양옆 값을 선형으로 잇는다. `np.percentile`도 기본은 linear다.
- Q: `quantile`에 리스트를 주면 돌려주는 것 — 분위수가 인덱스인 Series
  - 그래서 `q1, q3 = s.quantile([0.25, 0.75])`로 바로 풀어 받을 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([1, 2, 3, 4])
  print(s.quantile(0.25), s.quantile(0.5), s.quantile(0.75))
  ```
  - 답: `1.75 2.5 3.25`
  - 0.25 위치는 `3 * 0.25 = 0.75`라 1과 2 사이 75% 지점이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
  print(s.quantile(0.9), len(s[s >= s.quantile(0.9)]))
  ```
  - 답: `91.0 1`
  - 위치 `9 * 0.9 = 8.1`이라 90과 100 사이 10% 지점이다.

## IQR 이상치

- Q: IQR 방식의 이상치 기준 — `Q1 - 1.5*IQR` 미만 또는 `Q3 + 1.5*IQR` 초과
  - IQR은 `Q3 - Q1`, 가운데 50% 데이터가 퍼진 폭이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([12, 15, 14, 10, 13, 50, 11, 16, -8])
  q1, q3 = s.quantile([0.25, 0.75])
  iqr = q3 - q1
  out = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
  print(q1, q3, out.tolist())
  ```
  - 답: `11.0 15.0 [50, -8]`
  - 경계는 5와 21이다.

## clip

- Q: 하한보다 작은 값은 하한으로, 상한보다 큰 값은 상한으로 바꾸는 메서드 — `clip(lower, upper)`
  - 한쪽만 자를 때는 `clip(upper=100)`처럼 키워드로 준다. 이상치를 지우지 않고 눌러 둘 때 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([-5, 3, 12, 7, 30])
  print(s.clip(0, 10).tolist(), s.clip(upper=10).sum())
  ```
  - 답: `[0, 3, 10, 7, 10] 25`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([12, 15, 14, 10, 13, 50, 11, 16, -8])
  q1, q3 = s.quantile([0.25, 0.75])
  iqr = q3 - q1
  c = s.clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
  print(c.min(), c.max())
  ```
  - 답: `5 21`
  - IQR 경계 밖의 50과 -8이 경계값(5, 21)으로 눌린다. 경계가 정수 값이라 정수형 열이 그대로 유지된다.

## pd.cut

- Q: `pd.cut`의 기본 구간 모양 — 왼쪽 열림·오른쪽 닫힘 `(a, b]` (`right=True`)
  - 첫 경계값과 같은 값은 NaN이 되므로 `include_lowest=True`를 준다.
- Q: `bins`에 정수 하나를 주면 — 최솟값부터 최댓값까지를 같은 폭으로 그 개수만큼 나눈다

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
  s = pd.Series([10, 15, 20, 25, 30])
  a = pd.cut(s, bins=[10, 20, 30], labels=['low', 'high'], include_lowest=True)
  b = pd.cut(s, bins=[10, 20, 30], labels=['low', 'high'], right=False)
  print((a == 'low').sum(), (b == 'low').sum(), b.isna().sum())
  ```
  - 답: `3 2 1`
  - `right=False`면 `[10, 20)`·`[20, 30)`이라 20은 high, 30은 어디에도 안 들어간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  age = pd.Series([7, 19, 20, 35, 64, 65])
  g = pd.cut(age, bins=[0, 19, 64, 120], labels=['미성년', '성인', '노인'])
  print(g.value_counts()['성인'], g.tolist()[-1])
  ```
  - 답: `3 노인`
  - 19는 `(0, 19]`, 64는 `(19, 64]`에 든다.

## pd.qcut

- Q: `pd.cut`과 `pd.qcut`의 차이 — cut은 구간 폭을, qcut은 각 구간에 들어가는 개수를 같게 나눈다
  - qcut은 분위수로 경계를 정한다.
- Q: 구간 이름 대신 0부터 매긴 구간 번호를 받는 인자 — `labels=False`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 8, 1, 9, 5, 7, 2, 6])
  print(pd.qcut(s, 4, labels=False).tolist())
  ```
  - 답: `[1, 3, 0, 3, 1, 2, 0, 2]`
  - 8개를 4구간으로 나눠 구간마다 2개씩 들어간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 8, 1, 9, 5, 7, 2, 6])
  q = pd.qcut(s, 2, labels=['하', '상'])
  print(q.value_counts().tolist(), q[s == 5].tolist())
  ```
  - 답: `[4, 4] ['하']`
  - 중앙값 5.5를 경계로 둘로 나뉜다.

## replace · map

- Q: `replace`와 `map(딕셔너리)`의 차이 — replace는 딕셔너리에 없는 값을 그대로 두고, map은 NaN으로 만든다

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['M', 'F', 'U', 'M'])
  print(s.map({'M': 0, 'F': 1}).tolist(), s.replace({'M': 0, 'F': 1}).tolist())
  ```
  - 답: `[0.0, 1.0, nan, 0.0] [0, 1, 'U', 0]`
  - map은 결과에 NaN이 섞여 실수형이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([1, -999, 3, -999])
  r = s.replace(-999, np.nan)
  print(r.isna().sum(), r.mean())
  ```
  - 답: `2 2.0`
  - 결측을 숫자 코드로 적은 데이터는 replace로 결측으로 되돌린 뒤 계산한다.

## where · np.where

- Q: `s.where(조건, 값)`이 하는 일 — 조건이 True인 자리는 그대로 두고 False인 자리를 값으로 바꾼다
  - 값을 안 주면 NaN이 된다. 반대 동작은 `mask`.
- Q: 조건에 따라 두 값 중 하나를 고르는 numpy 함수 — `np.where(조건, 참일 때, 거짓일 때)`
  - 파생 변수(예: 고객 등급 0/1)를 만들 때 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([5, -2, 8, -1])
  print(s.where(s > 0, 0).tolist(), s.where(s > 0).isna().sum())
  ```
  - 답: `[5, 0, 8, 0] 2`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'amt': [120, 80, 300, 50]})
  df['vip'] = np.where(df['amt'] >= 100, 1, 0)
  print(df['vip'].tolist(), df.loc[df['vip'] == 1, 'amt'].mean())
  ```
  - 답: `[1, 0, 1, 0] 210.0`

## mean · median · std · var

- Q: pandas `std()`·`var()`의 기본 ddof — `1` (표본)
  - numpy `np.std`·`np.var`는 기본 `ddof=0` (모집단).
- Q: 문제가 모표준편차를 요구할 때 pandas에서 쓰는 코드 — `s.std(ddof=0)`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([2, 4, 4, 4, 5, 5, 7, 9])
  print(round(s.std(), 2), round(np.std(s.values), 2), round(s.std(ddof=0), 2))
  ```
  - 답: `2.14 2.0 2.0`
  - 같은 데이터라도 ddof에 따라 답이 달라진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([1, 2, 3, 4, 100])
  print(s.mean(), s.median(), s.var(ddof=0))
  ```
  - 답: `22.0 3.0 1522.0`
  - 이상치 하나가 평균을 크게 끌어올리지만 중앙값은 그대로다.

## skew · kurt

- Q: pandas `kurt()`가 정규분포에 주는 값 — 0
  - 정규분포를 3이 아니라 0으로 맞춘 초과 첨도다.
- Q: `scipy.stats.skew`·`kurtosis`의 값이 pandas `skew()`·`kurt()`와 다르게 나오는 이유 — scipy 기본이 `bias=True`라 표본 보정을 하지 않는다
  - `bias=False`를 주면 pandas와 같은 값이 나온다.
- Q: 0이 들어 있는 양수 데이터를 로그 변환할 때 쓰는 함수 — `np.log1p`
  - `log(1 + x)`라 0에서도 정의된다. 되돌릴 때는 `np.expm1`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  s = pd.Series([1, 2, 3, 4, 10])
  print(round(s.skew(), 3), round(stats.skew(s), 3), round(s.kurt(), 3))
  ```
  - 답: `1.697 1.138 3.152`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([0, 1, 2, 3, 50, 200])
  before = s.skew()
  after = np.log1p(s).skew()
  print(round(before, 2), round(after, 2), round(abs(before) - abs(after), 2))
  ```
  - 답: `2.16 0.93 1.23`
  - 오른쪽 꼬리가 긴 데이터는 로그 변환으로 왜도가 크게 줄어든다.

## corr

- Q: pandas `corr()`의 기본 방법 — `'pearson'`
  - 순위 상관은 `method='spearman'` 또는 `'kendall'`.
- Q: pandas 2.x에서 문자열 열이 섞인 DataFrame에 `df.corr()`를 하면 — ValueError가 난다
  - `numeric_only` 기본값이 False라서다. `df.corr(numeric_only=True)`로 숫자 열만 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 2, 3, 4, 5],
                     'b': [1, 4, 9, 16, 100]})
  print(round(df['a'].corr(df['b']), 3), round(df['a'].corr(df['b'], method='spearman'), 3))
  ```
  - 답: `0.795 1.0`
  - 순서가 완전히 같으면 스피어만은 1이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'x1': [1, 2, 3, 4, 5],
                     'x2': [5, 3, 4, 1, 2],
                     'x3': [2, 2, 3, 3, 9],
                     'y': [10, 12, 15, 17, 21]})
  c = df.corr()['y'].drop('y')
  print(c.abs().idxmax(), round(c.min(), 3))
  ```
  - 답: `x1 -0.735`
  - 절댓값으로 비교하라는 문제인지 부호까지 보라는 문제인지 먼저 확인한다.

## describe · percentiles

- Q: `describe`에 10%·90% 분위수를 보이게 하는 인자 — `percentiles=[0.1, 0.9]`
  - 50%는 따로 안 넣어도 항상 들어간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(range(1, 11))
  d = s.describe(percentiles=[0.1, 0.9])
  print(d.index.tolist()[4:7], d['90%'])
  ```
  - 답: `['10%', '50%', '90%'] 9.1`

## min-max 정규화 · z-score 표준화

- Q: min-max 정규화 식 — `(x - min) / (max - min)`
  - 결과 범위는 0~1.
- Q: scikit-learn `StandardScaler`가 쓰는 표준편차 — 모표준편차 (ddof=0)
  - 손으로 `(x - x.mean()) / x.std()`를 하면 pandas가 ddof=1을 써서 값이 조금 다르다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([10, 20, 25, 40, 60])
  mm = (s - s.min()) / (s.max() - s.min())
  print(mm.tolist(), (mm > 0.5).sum())
  ```
  - 답: `[0.0, 0.2, 0.3, 0.6, 1.0] 2`

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
  - 손 계산은 표본 표준편차(2.582), 스케일러는 모표준편차(2.236)로 나눈다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([50, 60, 70, 80, 90])
  z = (s - s.mean()) / s.std(ddof=0)
  print(round(z.iloc[-1], 3), int((z.abs() > 1).sum()))
  ```
  - 답: `1.414 2`
  - 모표준편차는 14.142다. 50과 90만 평균에서 1 표준편차보다 멀다.

## round

- Q: 출력 결과는?
  ```text
  print(round(0.125, 2), round(0.375, 2), round(2.675, 2))
  ```
  - 답: `0.12 0.38 2.67`
  - 0.125와 0.375는 이진수로 정확히 표현돼 짝수 쪽으로 간다. 2.675는 실제 저장값이 2.67499…라 내려간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 4, 4])
  print(int(s.mean()), round(s.mean()), round(s.mean(), 0))
  ```
  - 답: `3 4 4.0`
  - `int()`는 버림(3.67 → 3)이고, `round(x)`는 정수, `round(x, 0)`은 실수를 돌려준다.
