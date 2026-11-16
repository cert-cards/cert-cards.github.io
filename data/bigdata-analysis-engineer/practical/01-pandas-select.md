# pandas · 읽기·선택·정렬

> 파일을 읽고, 행과 열을 고르고, 정렬하고, 값의 빈도를 세는 pandas 함수.

## pd.read_csv

- Q: `pd.read_csv('data.csv')`가 돌려주는 것 — DataFrame
  - 첫 줄을 열 이름으로 쓰고(기본 `header='infer'`는 `names`가 없으면 `header=0`과 같다), 인덱스는 0부터 새로 매긴다.
- Q: 윈도 엑셀에서 저장한 한글 CSV가 깨지거나 UnicodeDecodeError가 날 때 주는 인자 — `encoding='cp949'`
  - 기본값은 `None`이고 UTF-8로 읽는다. `'euc-kr'`도 쓰지만 cp949가 글자를 더 많이 받는다.
- Q: 파일의 첫 열을 인덱스로 읽게 하는 인자 — `index_col=0`
  - 인덱스를 함께 저장한 파일을 그냥 읽으면 `Unnamed: 0` 열이 하나 더 생긴다.
- Q: 제출 파일을 `to_csv`로 저장할 때 인덱스가 열로 붙지 않게 하는 인자 — `index=False`
  - 기본값 `index=True`면 맨 앞에 이름 없는 열이 생겨 제출 형식이 틀어진다.

- Q: 출력 결과는?
  ```text
  import io
  import pandas as pd
  csv = 'id,name,score\n1,A,70\n2,B,\n3,C,90\n'
  df = pd.read_csv(io.StringIO(csv), index_col='id', usecols=['id', 'score'])
  print(df.shape, df.index.tolist(), df['score'].isna().sum())
  ```
  - 답: `(3, 1) [1, 2, 3] 1`
  - `index_col`로 쓴 열은 열 개수에서 빠진다. 빈 칸은 NaN으로 읽힌다.

- Q: 빈칸을 채우면?
  ```text
  import pandas as pd
  # 한글이 들어 있는 cp949 파일을 읽고, 첫 열을 인덱스로 쓴다
  df = pd.read_csv('data.csv', ①='cp949', ②=0)
  ```
  - 답: `① encoding ② index_col`

## head · info · describe · shape · dtypes

- Q: `df.shape`가 돌려주는 것 — (행 수, 열 수) 튜플
  - 행 수만 필요하면 `df.shape[0]` 또는 `len(df)`.
- Q: 열마다 결측이 아닌 개수와 자료형을 한 번에 출력하는 메서드 — `df.info()`
  - 출력만 하고 돌려주는 값은 None이다. 값을 계산에 쓰려면 `df.count()`나 `df.dtypes`.
- Q: `describe()`가 기본으로 요약하는 열 — 숫자 열만
  - 문자열 열은 `include='object'`를 주면 count, unique, top, freq를 보여 준다.
- Q: 숫자 열에 대한 `describe()` 결과의 행 이름 8개 — count, mean, std, min, 25%, 50%, 75%, max
  - std는 표본 표준편차(ddof=1)다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'n': [1, 2, 3], 'x': [1.5, 2.0, None], 'c': ['a', 'b', 'c']})
  print(df.dtypes.astype(str).tolist(), df.shape)
  ```
  - 답: `['int64', 'float64', 'object'] (3, 3)`
  - 결측이 섞인 숫자 열은 float64가 된다. 문자열 열은 object.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'x': [2, 4, 4, 6, 9], 'c': list('abcde')})
  d = df.describe()
  print(d.shape, d.loc['50%', 'x'], d.loc['count', 'x'])
  ```
  - 답: `(8, 1) 4.0 5.0`
  - 문자열 열 c는 빠지고 x 하나만 요약된다. count도 실수로 나온다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'v': range(12)})
  print(len(df.head()), len(df.tail(3)), df.head(2)['v'].tolist())
  ```
  - 답: `5 3 [0, 1]`
  - `head`와 `tail`의 기본 n은 5다.

## loc · iloc

- Q: `df.loc`과 `df.iloc`의 차이 — loc은 라벨로, iloc은 정수 위치로 고른다
- Q: `df['a']`와 `df[['a']]`의 차이 — 대괄호 하나는 Series, 두 겹은 DataFrame
  - scikit-learn에 열 하나를 넣을 때는 2차원인 `df[['a']]`를 쓴다.
- Q: 조건에 맞는 행의 한 열 값을 바꾸는 코드 모양 — `df.loc[조건, '열'] = 값`
  - `df[조건]['열'] = 값`처럼 두 번 나눠 쓰면 복사본에 대입돼 원본이 바뀌지 않는다(SettingWithCopyWarning).

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'v': [10, 20, 30, 40, 50]})
  print(len(df.loc[1:3]), len(df.iloc[1:3]), df.iloc[-1, 0])
  ```
  - 답: `3 2 50`
  - 인덱스가 0부터 매겨진 기본 인덱스라도 loc은 라벨로 읽어 끝 3을 포함한다.

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
  - 60 미만인 45, 58, 30이 60으로 바뀐다.

## 불리언 마스크 (& · | · ~)

- Q: 조건 두 개를 동시에 거는 불리언 인덱싱에서 `and` 대신 쓰는 연산자 — `&`
  - 또는 `|`. 파이썬 `and`·`or`를 Series에 쓰면 ValueError가 난다.
- Q: `&`·`|`로 조건을 이을 때 각 조건을 괄호로 감싸는 이유 — `&`가 `>=`·`==`보다 먼저 묶이기 때문
  - `df['a'] > 1 & df['b'] < 5`는 `1 & df['b']`부터 계산된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 5, 3, 8, 2], 'b': [9, 2, 7, 1, 6]})
  print(((df['a'] > 2) & (df['b'] > 2)).sum(), ((df['a'] > 2) | (df['b'] > 2)).sum(), (~(df['a'] > 2)).sum())
  ```
  - 답: `1 5 2`
  - 둘 다 2보다 큰 행은 (3, 7) 하나다. 불리언 Series의 `sum()`은 True 개수다. `~`는 조건을 뒤집는다(파이썬 `not`은 Series에 못 쓴다).

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 5, 3, 8, 2], 'b': [9, 2, 7, 1, 6]})
  print(df[df['b'] > 5]['a'].sum(), df[(df['a'] % 2 == 0)]['b'].tolist())
  ```
  - 답: `6 [1, 6]`
  - b가 5보다 큰 행의 a는 1, 3, 2다.

## isin · between

- Q: 열 값이 주어진 목록 중 하나인 행만 고르는 메서드 — `isin`
  - 목록에 없는 행은 `~df['c'].isin([...])`.
- Q: `between(a, b)`의 경계 포함 기본값 — 양쪽 다 포함 (`inclusive='both'`)
  - `'left'`, `'right'`, `'neither'`로 바꿀 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['서울', '부산', '대구', '서울', '광주', '인천'])
  print(s.isin(['서울', '인천']).sum(), (~s.isin(['서울', '인천'])).sum())
  ```
  - 답: `3 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([10, 15, 20, 25, 30])
  print(s.between(10, 20).sum(), s.between(10, 20, inclusive='neither').sum())
  ```
  - 답: `3 1`
  - 경계 10과 20을 빼면 15만 남는다.

## query

- Q: `df.query`에 주는 조건의 모양 — 문자열 식
  - `df.query('age >= 30 and city == "서울"')`처럼 `and`·`or`를 그대로 쓸 수 있다.
- Q: query 문자열 안에서 파이썬 변수를 쓰는 표시 — `@`
  - `df.query('score > @cut')`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'age': [25, 34, 41, 29, 52],
                     'city': ['서울', '부산', '서울', '서울', '부산']})
  cut = 30
  print(len(df.query('age > @cut and city == "서울"')), df.query('city != "서울"')['age'].sum())
  ```
  - 답: `1 86`
  - 30세 초과 서울은 41세 한 명이다.

## sort_values

- Q: `sort_values`의 정렬 방향 기본값 — 오름차순 (`ascending=True`)
  - 결측은 기본으로 맨 뒤에 놓인다(`na_position='last'`).
- Q: 여러 열로 정렬하면서 열마다 방향을 다르게 주는 방법 — `by`와 `ascending`에 같은 길이의 리스트를 준다
  - `sort_values(['g', 'v'], ascending=[True, False])`.

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
  df = pd.DataFrame({'g': ['b', 'a', 'b', 'a', 'a'],
                     'v': [3, 7, 9, 1, 4]})
  r = df.sort_values(['g', 'v'], ascending=[True, False])
  print(r['v'].tolist())
  ```
  - 답: `[7, 4, 1, 9, 3]`
  - g는 a부터, 같은 g 안에서는 v가 큰 것부터 나온다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series([3, np.nan, 1, 2])
  print(s.sort_values().index.tolist(), s.sort_values(ascending=False).index.tolist())
  ```
  - 답: `[2, 3, 0, 1] [0, 3, 2, 1]`
  - 내림차순이어도 NaN은 맨 뒤에 남는다.

## nlargest · nsmallest

- Q: `df.nlargest(3, 'score')`와 같은 결과를 내는 정렬 코드 — `df.sort_values('score', ascending=False).head(3)`
  - 작은 쪽은 `nsmallest`. Series에서는 열 이름 없이 `s.nlargest(3)`.
- Q: `nlargest`의 `keep` 기본값 — `'first'`
  - `keep='all'`은 마지막 순위의 동점을 모두 남겨 n개보다 많아질 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'score': [90, 85, 85, 70, 60]})
  print(len(df.nlargest(2, 'score')), len(df.nlargest(2, 'score', keep='all')))
  ```
  - 답: `2 3`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([40, 10, 30, 20, 50], index=list('abcde'))
  print(s.nsmallest(2).index.tolist(), s.nlargest(2).sum())
  ```
  - 답: `['b', 'd'] 90`

## reset_index

- Q: `reset_index()`가 하는 일 — 지금 인덱스를 열로 꺼내고 0부터 새 인덱스를 매긴다
  - groupby 결과의 키를 일반 열로 돌릴 때 쓴다.
- Q: 기존 인덱스를 열로 남기지 않고 버리는 인자 — `drop=True`
  - 필터링이나 정렬 뒤 인덱스만 다시 매기고 싶을 때 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'v': [5, 3, 8, 1]})
  a = df[df['v'] > 2].reset_index()
  b = df[df['v'] > 2].reset_index(drop=True)
  print(a.columns.tolist(), b.index.tolist())
  ```
  - 답: `['index', 'v'] [0, 1, 2]`
  - drop 없이 하면 원래 인덱스가 `index`라는 열로 들어온다.

## value_counts

- Q: `value_counts()`의 기본 정렬 — 빈도 내림차순
  - 그래서 최빈값은 `.index[0]` 또는 `.idxmax()`로 꺼낸다.
- Q: `value_counts`가 개수 대신 비율을 돌려주게 하는 인자 — `normalize=True`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['x', 'y', np.nan, 'x', np.nan])
  print(s.value_counts().sum(), len(s.value_counts(dropna=False)))
  ```
  - 답: `3 3`
  - 기본으로는 결측 2개가 빠진다. `dropna=False`면 NaN이 한 칸으로 들어온다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['A', 'B', 'A', 'C', 'A', 'B', 'A', 'C'])
  vc = s.value_counts(normalize=True)
  print(vc.index[0], vc['A'], vc.tolist())
  ```
  - 답: `A 0.5 [0.5, 0.25, 0.25]`

## unique · nunique

- Q: `unique()`가 돌려주는 것 — 처음 나온 순서대로 고유값을 담은 배열
  - 정렬하지 않으며 결측도 하나의 값으로 들어간다.
- Q: `nunique()`가 결측을 다루는 기본 방식 — 세지 않는다 (`dropna=True`)
  - DataFrame에 쓰면 열마다 고유값 개수를 Series로 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['b', 'a', np.nan, 'b', 'c'])
  print(len(s.unique()), s.nunique(), s.nunique(dropna=False))
  ```
  - 답: `4 3 4`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1, 1, 2], 'b': ['x', 'y', 'z'], 'c': [0, 0, 0]})
  n = df.nunique()
  print(n.tolist(), n.idxmax())
  ```
  - 답: `[2, 3, 1] b`
  - 고유값이 하나뿐인 열(c)은 모델에 정보를 주지 못해 지울 후보가 된다.

## astype

- Q: 열의 자료형을 바꾸는 메서드 — `astype`
  - `astype(int)`, `astype(float)`, `astype(str)`, `astype('category')`.
- Q: 실수를 `astype(int)`로 바꿀 때 소수점 처리 — 버린다 (0 쪽으로 자른다)
  - 반올림이 필요하면 `round()`를 먼저 한다.
- Q: 결측이 있는 실수 열에 `astype(int)`를 하면 — 오류가 난다 (IntCastingNaNError)
  - 결측을 먼저 채우거나 결측을 받는 `'Int64'`(대문자 I)를 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([1.7, -1.7, 2.5])
  print(s.astype(int).tolist(), s.round().astype(int).tolist())
  ```
  - 답: `[1, -1, 2] [2, -2, 2]`
  - `round()`는 반이면 짝수 쪽으로 보내 2.5가 2가 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['3', '10', '2'])
  print(s.max(), s.astype(int).max())
  ```
  - 답: `3 10`
  - 문자열끼리는 사전 순으로 비교해 '3'이 '10'보다 크다.

## rename

- Q: 열 이름 하나를 바꾸는 코드 — `df.rename(columns={'old': 'new'})`
  - 기본으로 새 DataFrame을 돌려주고 원본은 그대로다. 결과를 다시 대입한다.
- Q: 모든 열 이름을 한꺼번에 새 리스트로 바꾸는 코드 — `df.columns = [...]`
  - 리스트 길이가 열 개수와 같아야 한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'a': [1], 'b': [2]})
  df.rename(columns={'a': 'x'})
  r = df.rename(columns={'a': 'x'})
  print(df.columns.tolist(), r.columns.tolist())
  ```
  - 답: `['a', 'b'] ['x', 'b']`
  - 결과를 대입하지 않은 첫 줄은 원본을 바꾸지 않는다.

## drop · pop

- Q: 열을 지우는 `drop` 코드 두 가지 — `df.drop(columns=['a'])` 또는 `df.drop('a', axis=1)`
- Q: `df.drop('a')`처럼 axis 없이 열 이름을 주면 — KeyError가 난다
  - axis 기본값이 0이라 행 라벨에서 'a'를 찾는다.
- Q: 열을 꺼내 돌려주면서 원본에서 지우는 메서드 — `pop`
  - test의 ID 열을 따로 보관하면서 입력에서 뺄 때 쓴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  train = pd.DataFrame({'id': [1, 2, 3, 4], 'age': [20, 35, 41, 28],
                        'city': ['A', 'B', 'A', 'C'], 'target': [0, 1, 1, 0]})
  test = pd.DataFrame({'id': [5, 6], 'age': [33, 50], 'city': ['B', 'A']})
  X = train.drop(columns=['id', 'target'])
  test_id = test.pop('id')
  print(list(X.columns), list(test.columns), test_id.tolist())
  ```
  - 답: `['age', 'city'] ['age', 'city'] [5, 6]`
  - X와 test의 열이 같아야 predict가 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'v': [10, 20, 30, 40]}, index=['a', 'b', 'c', 'd'])
  print(df.drop(['b', 'd'])['v'].sum(), df.drop(index='a').shape)
  ```
  - 답: `40 (3, 1)`
  - axis를 안 주면 행 라벨을 지운다.

## select_dtypes

- Q: 문자열(범주형) 열만 고르는 코드 — `df.select_dtypes(include='object')`
  - 숫자 열만은 `include='number'`. `exclude='object'`는 bool·category·날짜 열도 남기고, `include='object'`는 category 열을 빠뜨린다(둘 다는 `include=['object', 'category']`).

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'age': [20, 35, 41], 'city': ['A', 'B', 'A'],
                     'score': [3.5, 4.0, 2.5], 'job': ['x', 'y', 'y']})
  print(df.select_dtypes(include='object').columns.tolist(), df.select_dtypes(include='number').columns.tolist())
  ```
  - 답: `['city', 'job'] ['age', 'score']`

## idxmax · idxmin

- Q: 최댓값이 있는 위치의 라벨을 돌려주는 메서드 — `idxmax()`
  - 최솟값은 `idxmin()`. 값 자체가 필요하면 `max()`.
- Q: `idxmax`와 `argmax`의 차이 — idxmax는 인덱스 라벨을, argmax는 0부터 센 정수 위치를 준다

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series([3, 9, 2, 9], index=['p', 'q', 'r', 's'])
  print(s.idxmax(), s.argmax(), s.idxmin())
  ```
  - 답: `q 1 r`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'team': ['x', 'y', 'x', 'z', 'y', 'z'],
                     'pts': [10, 25, 30, 18, 15, 20]})
  print(df.groupby('team')['pts'].mean().idxmax())
  ```
  - 답: `x`
  - 평균은 x 20, y 20, z 19로 x와 y가 같다. groupby 결과는 키 순서로 정렬되므로 먼저 나온 x가 답이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  df = pd.DataFrame({'a': [1, np.nan, 3, np.nan],
                     'b': [np.nan, 2, 3, 4],
                     'c': [1, 2, np.nan, np.nan]})
  print(df.isna().mean().idxmax())
  ```
  - 답: `a`
  - 결측 비율은 a와 c가 50%로 같고, 먼저 나온 a가 나온다.
