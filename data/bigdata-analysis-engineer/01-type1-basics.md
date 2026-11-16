# 작업형 1 · 기본 처리

> 작업형 1유형은 값 하나를 구해 내는 문제다. 코드는 전부 직접 만든 작은 데이터이고, 답은 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다.

## 선택·필터·정렬

- Q: 조건 두 개를 동시에 거는 불리언 인덱싱에서 `and` 대신 쓰는 연산자 — `&` (또는 `|`), 조건마다 괄호로 감싼다
  - `&`가 비교 연산자보다 먼저 묶이므로 괄호가 없으면 오류가 나거나 엉뚱한 결과가 나온다.
- Q: 열 값이 주어진 목록 중 하나인 행만 고르는 메서드 — `isin`
  - 반대(목록에 없는 행)는 `~df['c'].isin([...])`.
- Q: `df.loc`과 `df.iloc`의 차이 — loc은 라벨로, iloc은 정수 위치로 고른다
  - 슬라이스에서 loc은 끝 라벨을 포함하고 iloc은 끝 위치를 뺀다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'name': list('ABCDEF'),
                     'score': [70, 95, 88, 95, 60, 81]})
  top3 = df.sort_values('score', ascending=False).head(3)
  print(top3['score'].sum())
  ```
  - 답: `278`
  - 상위 3개는 95, 95, 88이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'score': [90, 85, 85, 70, 60]})
  print(len(df.nlargest(2, 'score')), len(df.nlargest(2, 'score', keep='all')))
  ```
  - 답: `2 3`
  - `keep='all'`은 마지막 순위의 동점을 모두 남긴다. 기본값은 `'first'`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'age': [25, 34, 41, 29, 52, 38],
                     'city': ['서울', '부산', '서울', '서울', '부산', '서울'],
                     'income': [300, 420, 510, 280, 600, 450]})
  cond = (df['age'] >= 30) & (df['city'] == '서울')
  print(df.loc[cond, 'income'].mean())
  ```
  - 답: `480.0`
  - 조건을 만족하는 행은 41세(510)와 38세(450)다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'score': [45, 72, 58, 90, 30]})
  df.loc[df['score'] < 60, 'score'] = 60
  print(df['score'].mean())
  ```
  - 답: `68.4`
  - 60 미만인 45, 58, 30이 60으로 바뀐다. 값 변경은 `df.loc[조건, 열] = 값` 한 줄로 한다.

## groupby 집계

- Q: groupby 결과에서 그룹 키를 인덱스가 아닌 일반 열로 남기는 인자 — `as_index=False`
  - 이미 집계한 뒤라면 `.reset_index()`로 같은 효과를 낸다.
- Q: 그룹별 평균이 가장 큰 그룹의 이름을 바로 꺼내는 메서드 — `idxmax()`
  - 값 자체가 필요하면 `max()`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'team': ['x', 'y', 'x', 'z', 'y', 'z'],
                     'pts': [10, 25, 30, 18, 15, 20]})
  print(df.groupby('team')['pts'].mean().idxmax())
  ```
  - 답: `x`
  - 평균은 x 20, y 20, z 19로 x와 y가 같다. groupby 결과는 키 순서로 정렬되고, `idxmax`는 동점이면 먼저 나온 라벨을 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'dept': ['A', 'B', 'A', 'B', 'B'],
                     'sal': [300, 250, 340, 270, 290]})
  g = df.groupby('dept')['sal'].agg(['mean', 'count'])
  print(g.loc['B', 'mean'], g.loc['B', 'count'])
  ```
  - 답: `270.0 3`
  - `agg`에 함수 이름 리스트를 주면 열이 함수별로 생긴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'g': ['a', 'b', None, 'a', None],
                     'v': [1, 2, 3, 4, 5]})
  print(len(df.groupby('g')['v'].sum()), len(df.groupby('g', dropna=False)['v'].sum()))
  ```
  - 답: `2 3`
  - 그룹 키가 결측인 행은 기본(`dropna=True`)으로 빠진다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'g': ['a', 'a', 'a', 'b', 'b'],
                     'v': [1, np.nan, 3, np.nan, 5]})
  print(df.groupby('g')['v'].count().tolist(), df.groupby('g').size().tolist())
  ```
  - 답: `[2, 1] [3, 2]`
  - `count`는 결측이 아닌 값만 세고 `size`는 행 수를 센다.

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

## value_counts·nunique

- Q: `value_counts()`의 기본 정렬 — 빈도 내림차순
  - 그래서 최빈값은 `.index[0]` 또는 `.idxmax()`로 꺼낸다.
- Q: `value_counts`가 개수 대신 비율을 돌려주게 하는 인자 — `normalize=True`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['x', 'y', np.nan, 'x', np.nan])
  print(s.value_counts().sum(), s.nunique(), s.nunique(dropna=False))
  ```
  - 답: `3 2 3`
  - `value_counts`와 `nunique` 둘 다 기본으로 결측을 뺀다.

## 결측치

- Q: 열마다 결측치 개수를 세는 코드 — `df.isna().sum()`
  - 전체 개수는 `.sum().sum()`, 열별 결측 비율은 `df.isna().mean()`.
- Q: 판다스 `mean()`이 결측치를 다루는 기본 방식 — 빼고 계산한다 (`skipna=True`)
- Q: `mode()`의 반환 형태 — Series
  - 최빈값이 여러 개일 수 있어서다. 하나만 쓰려면 `mode()[0]`.
- Q: 모든 값이 결측인 행만 지우는 `dropna` 인자 — `how='all'`
  - 기본값 `how='any'`는 하나라도 결측이면 지운다. 특정 열만 보려면 `subset=[...]`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, np.nan, 3, np.nan],
                     'b': [np.nan, 2, 3, 4],
                     'c': [1, 2, np.nan, np.nan]})
  print(df.isna().sum().sum(), df.isna().mean().idxmax())
  ```
  - 답: `5 a`
  - a와 c가 50%로 같고, `idxmax`는 먼저 나온 a를 준다.

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
  df = pd.DataFrame({'a': [1, np.nan, np.nan, 4, 5],
                     'b': [np.nan, np.nan, 3, 4, np.nan]})
  print(len(df.dropna()), len(df.dropna(how='all')), len(df.dropna(subset=['a'])))
  ```
  - 답: `1 4 3`

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
  - `agg('mean')`은 그룹 수만큼만 줄어든 결과라 행 위치가 맞지 않는다.

## 중복

- Q: `drop_duplicates`의 `keep` 기본값 — `'first'`
  - `keep='last'`는 마지막 것을 남기고, `keep=False`는 중복된 행을 전부 지운다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'id': [1, 2, 2, 3, 3, 3],
                     'v': [5, 6, 6, 7, 8, 7]})
  print(df.duplicated().sum(), len(df.drop_duplicates('id')), len(df.drop_duplicates('id', keep=False)))
  ```
  - 답: `2 3 1`
  - 행 전체가 같은 것은 (2, 6)과 (3, 7)의 두 번째 등장뿐이다. id 기준으로 중복이 아예 없는 것은 1뿐이다.

## 분위수와 IQR 이상치

- **IQR (Interquartile Range)** — 3사분위수에서 1사분위수를 뺀 값. 가운데 50% 데이터가 퍼진 폭
  - 이상치 기준은 보통 `Q1 - 1.5*IQR` 미만 또는 `Q3 + 1.5*IQR` 초과.
- Q: pandas `quantile`의 기본 보간 방식 — `'linear'`
  - 위치 `(n-1)*q`가 정수가 아니면 양옆 값을 선형으로 잇는다. `np.percentile`도 기본은 linear다.

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
  s = pd.Series([12, 15, 14, 10, 13, 50, 11, 16, -8])
  q1, q3 = s.quantile([0.25, 0.75])
  iqr = q3 - q1
  out = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
  print(q1, q3, out.tolist())
  ```
  - 답: `11.0 15.0 [50, -8]`
  - 경계는 5와 21이다.

## 분산·표준편차

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
  - 같은 데이터라도 ddof에 따라 답이 달라진다. 문제가 지정하지 않으면 pandas 기본(표본)이 흔히 기대된다.

## 왜도·첨도와 로그 변환

- **왜도 (Skewness)** — 분포가 좌우 어느 쪽으로 기울었는지 나타내는 값. 오른쪽 꼬리가 길면 양수
- **첨도 (Kurtosis)** — 분포 꼬리의 두께를 나타내는 값. pandas `kurt()`는 정규분포를 0으로 맞춘 초과값을 준다
- Q: `scipy.stats.skew`·`kurtosis`의 값이 pandas `skew()`·`kurt()`와 다르게 나오는 이유 — scipy 기본이 `bias=True`라 표본 보정을 하지 않는다
  - `bias=False`를 주면 pandas와 같은 값이 나온다.
- Q: 0이 들어 있는 양수 데이터를 로그 변환할 때 쓰는 함수 — `np.log1p`
  - `log(1 + x)`라 0에서도 정의된다. 되돌릴 때는 `np.expm1`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  s = pd.Series([1, 2, 3, 4, 10])
  print(round(s.skew(), 3), round(stats.skew(s), 3))
  ```
  - 답: `1.697 1.138`
  - pandas는 표본 보정한 값을, scipy는 기본 `bias=True`로 보정하지 않은 값을 준다. `stats.skew(s, bias=False)`면 pandas와 같다.

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

## 상관계수

- Q: pandas `corr()`의 기본 방법 — `'pearson'`
  - 순위 상관은 `method='spearman'` 또는 `'kendall'`.
- Q: pandas 2.x에서 문자열 열이 섞인 DataFrame에 `df.corr()`를 하면 — ValueError가 난다
  - `numeric_only` 기본값이 2.0부터 False가 됐다. `df.corr(numeric_only=True)`로 숫자 열만 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 2, 3, 4, 5],
                     'b': [1, 4, 9, 16, 100]})
  print(round(df['a'].corr(df['b']), 3), round(df['a'].corr(df['b'], method='spearman'), 3))
  ```
  - 답: `0.795 1.0`
  - 순서가 완전히 같으면 스피어만은 1이다. 반올림하지 않으면 부동소수 오차로 `0.9999999999999999`가 찍힌다.

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

## 표준화·정규화

- Q: scikit-learn `StandardScaler`가 쓰는 표준편차 — 모표준편차 (ddof=0)
  - 손으로 `(x - x.mean()) / x.std()`를 하면 pandas가 ddof=1을 써서 값이 조금 다르다.
- Q: min-max 정규화 식 — `(x - min) / (max - min)`
  - 결과 범위는 0~1.

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
  s = pd.Series([10, 20, 25, 40, 60])
  mm = (s - s.min()) / (s.max() - s.min())
  print(mm.tolist(), (mm > 0.5).sum())
  ```
  - 답: `[0.0, 0.2, 0.3, 0.6, 1.0] 2`

- Q: 빈칸을 채우면?
  ```text
  import pandas as pd
  from sklearn.preprocessing import MinMaxScaler
  df = pd.read_csv('data.csv')
  df['x_mm'] = MinMaxScaler().fit_transform(①)
  ```
  - 답: `① df[['x']]`
  - 스케일러는 2차원 입력을 받는다. `df['x']`(1차원 Series)를 넣으면 오류가 난다.

## 거듭제곱 변환 (Box-Cox·Yeo-Johnson)

- **Box-Cox 변환 (Box-Cox Transformation)** — 양수 데이터에 λ 거듭제곱을 적용해 분포를 정규에 가깝게 만드는 변환. λ = 0이면 자연로그와 같다
  - 0이나 음수가 있으면 쓸 수 없다.
- **Yeo-Johnson 변환 (Yeo-Johnson Transformation)** — Box-Cox를 0과 음수까지 쓸 수 있게 넓힌 거듭제곱 변환
- Q: `PowerTransformer()`의 기본 방법과 표준화 여부 — `method='yeo-johnson'`, `standardize=True`
  - 그래서 결과는 평균 0, 표준편차 1로 맞춰져 나온다. 변환값 자체가 필요하면 `standardize=False`.
- Q: `scipy.stats.boxcox(x)`를 λ 없이 부르면 돌려주는 것 — 변환된 배열과 추정한 λ의 튜플
  - `lmbda=`를 지정하면 배열 하나만 돌려준다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([0.0, 1.0, 3.0])
  print(stats.yeojohnson(x, lmbda=0).round(3).tolist(), np.log1p(x).round(3).tolist())
  ```
  - 답: `[0.0, 0.693, 1.386] [0.0, 0.693, 1.386]`
  - 0 이상의 값에서 λ = 0인 Yeo-Johnson은 `log1p`와 같다.

## 반올림과 출력

- Q: 파이썬 `round(2.5)`와 `round(3.5)`의 값 — `2`와 `4`
  - 정확히 반인 값은 짝수 쪽으로 보낸다(은행가 반올림). `np.round`와 pandas `round`도 같다.

- Q: 출력 결과는?
  ```text
  print(round(0.125, 2), round(0.375, 2), round(2.675, 2))
  ```
  - 답: `0.12 0.38 2.67`
  - 0.125와 0.375는 이진수로 정확히 표현돼 짝수 쪽으로 간다. 2.675는 실제 저장값이 2.67499…라 내려간다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([1, 2, 3, 4])
  print(s.mean(), [s.mean()], float(s.mean()))
  ```
  - 답: `2.5 [2.5] 2.5`
  - 시험 환경의 numpy 1.26 기준이다. numpy 2부터는 리스트 안의 numpy 실수가 `[np.float64(2.5)]`로 찍힌다. 답으로 낼 값은 `float()`로 감싸 두면 어느 버전이든 같다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 4, 4])
  print(int(s.mean()), round(s.mean()), round(s.mean(), 0))
  ```
  - 답: `3 4 4.0`
  - `int()`는 버림(3.67 → 3)이고, `round(x)`는 정수, `round(x, 0)`은 실수를 돌려준다.
