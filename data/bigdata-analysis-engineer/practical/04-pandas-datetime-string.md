# pandas · 날짜·문자열

> 날짜형 변환과 dt 접근자, 기간별 집계, 날짜 차이 계산, str 접근자로 문자열을 고르고 자르고 바꾸는 pandas 함수.

## pd.to_datetime

- Q: 문자열 날짜 열을 날짜형으로 바꾸는 함수 — `pd.to_datetime`
  - 바꾸지 않은 문자열 열에 `.dt`를 쓰면 AttributeError가 난다.
- Q: 날짜로 바꿀 수 없는 값을 오류 대신 NaT로 두는 `to_datetime` 인자 — `errors='coerce'`
  - 기본값 `errors='raise'`는 한 값이라도 못 읽으면 ValueError를 낸다.
- Q: `'20260301'`이나 `'01/03/2026'`처럼 모양을 정해 읽게 하는 인자 — `format`
  - 예: `format='%Y%m%d'`, `format='%d/%m/%Y'`. `%Y` 네 자리 연도, `%m` 월, `%d` 일, `%H` 시, `%M` 분.
- Q: `read_csv`에서 날짜 열을 처음부터 날짜형으로 읽는 인자 — `parse_dates=['열']`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['2026-01-05', '미정', '2026-03-10'])
  d = pd.to_datetime(s, errors='coerce')
  print(d.isna().sum(), d.dt.month.tolist())
  ```
  - 답: `1 [1.0, nan, 3.0]`
  - NaT가 섞인 열에서 `dt.month`를 꺼내면 결과가 실수형이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  print(pd.Timestamp('2026-11-28').day_name(), pd.to_datetime('05/03/2026').month)
  ```
  - 답: `Saturday 5`
  - 슬래시 날짜는 기본이 월/일/연이다. 일이 앞이면 `dayfirst=True`나 `format='%d/%m/%Y'`을 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['20260301', '20261225'])
  d = pd.to_datetime(s, format='%Y%m%d')
  print(d.dt.month.tolist(), d.dt.day.tolist())
  ```
  - 답: `[3, 12] [1, 25]`

- Q: 빈칸을 채우면?
  ```text
  import pandas as pd
  df = pd.read_csv('data.csv')
  # '2026/11/28 14:05' 모양의 문자열을 날짜형으로 바꾼다
  df['ts'] = pd.to_datetime(df['ts'], format=①)
  ```
  - 답: `① '%Y/%m/%d %H:%M'`

## dt.year · month · day · hour · quarter

- Q: 날짜형 열에서 시각(0~23)과 분기(1~4)를 꺼내는 속성 — `dt.hour`, `dt.quarter`

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
  t = pd.to_datetime(pd.Series(['2026-02-01 08:30', '2026-05-03 14:00', '2026-11-20 23:10']))
  print(t.dt.hour.tolist(), t.dt.quarter.tolist(), t.dt.hour.between(9, 18).sum())
  ```
  - 답: `[8, 14, 23] [1, 2, 4] 1`

## dt.dayofweek · day_name

- Q: `dt.dayofweek`에서 월요일과 일요일의 값 — 월요일 0, 일요일 6
  - `dt.weekday`도 같은 값이다.
- Q: 주말(토·일) 여부를 만드는 조건 — `dt.dayofweek >= 5`
- Q: 요일 이름 문자열을 꺼내는 메서드 — `dt.day_name()`
  - 속성이 아니라 메서드라 괄호가 필요하다. 영어 이름(`'Monday'` 등)을 준다.

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
  df = pd.DataFrame({'date': pd.to_datetime(['2026-11-14', '2026-11-16', '2026-11-21', '2026-11-18']),
                     'sales': [30, 10, 50, 20]})
  wkend = df['date'].dt.dayofweek >= 5
  print(df.loc[wkend, 'sales'].mean(), df['date'].dt.day_name().iloc[1])
  ```
  - 답: `40.0 Monday`
  - 11-14와 11-21이 토요일이다.

## dt.is_month_end · is_month_start

- Q: 날짜가 그 달의 마지막 날인지를 불리언으로 주는 속성 — `dt.is_month_end`
  - 첫날은 `dt.is_month_start`. 윤년 2월 29일도 월말로 잡는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  d = pd.to_datetime(pd.Series(['2026-01-31', '2026-02-28', '2026-03-30', '2024-02-29', '2026-04-01']))
  print(d.dt.is_month_end.tolist(), d.dt.is_month_start.sum())
  ```
  - 답: `[True, True, False, True, False] 1`

## dt.strftime · dt.to_period

- Q: 날짜형 열을 `'2026-03'` 같은 연-월 문자열로 바꾸는 코드 — `dt.strftime('%Y-%m')`
  - 결과는 문자열(object)이다.
- Q: 연-월 단위로 묶을 때 `dt.month` 대신 `dt.to_period('M')`을 쓰는 이유 — 서로 다른 해의 같은 달이 섞이지 않는다

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
  - 거래가 없는 3월은 groupby 결과에 아예 나오지 않는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  d = pd.to_datetime(pd.Series(['2025-03-02', '2026-03-15', '2026-03-28']))
  print(d.dt.month.nunique(), d.dt.strftime('%Y-%m').nunique())
  ```
  - 답: `1 2`
  - 월 번호만 보면 세 날짜가 모두 3월이다.

## resample

- Q: `resample`을 쓰기 위한 조건 — 인덱스가 DatetimeIndex여야 한다
  - 날짜가 열에 있으면 `set_index('date')`를 먼저 하거나 `resample('MS', on='date')`처럼 `on`을 준다.
- Q: pandas 2.2에서 월 단위 resample에 쓰는 별칭과 라벨 — `'ME'`는 월말 날짜, `'MS'`는 월초 날짜로 라벨을 단다
  - 예전 `'M'`은 FutureWarning을 낸다.
- Q: `resample('W')`의 기본 주 경계 — 일요일에 끝나는 주 (`'W-SUN'`)
  - 결과 라벨도 그 주의 일요일 날짜다. 월요일에 끝나게 하려면 `'W-MON'`.
- Q: resample과 groupby(월)의 차이 — resample은 데이터가 없는 기간도 빈 칸으로 만든다

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
  - 거래가 없는 3월도 합계 0으로 한 칸 생긴다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': pd.to_datetime(['2026-01-05', '2026-01-20', '2026-02-03', '2026-04-10']),
                     'temp': [2.0, 4.0, 6.0, 15.0]})
  m = df.resample('ME', on='date')['temp'].mean()
  print(str(m.index[0].date()), m.isna().sum(), m.tolist()[0])
  ```
  - 답: `2026-01-31 1 3.0`
  - 평균은 빈 3월을 NaN으로 둔다. 합계(sum)였다면 0이 된다.

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

## Timedelta · dt.days · total_seconds

- Q: Timedelta 열을 일 수 정수로 바꾸는 코드 — `.dt.days`
  - 시간 단위가 필요하면 `.dt.total_seconds() / 3600`.
- Q: Timedelta의 `seconds` 속성과 `total_seconds()`의 차이 — seconds는 일 단위를 뺀 나머지 초만, total_seconds()는 전체 길이를 초로 준다

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

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.to_datetime(pd.Series(['2026-11-17 09:00', '2026-11-17 22:30']))
  e = pd.to_datetime(pd.Series(['2026-11-17 11:30', '2026-11-18 01:00']))
  h = (e - s).dt.total_seconds() / 3600
  print(h.tolist(), (e - s).dt.days.tolist())
  ```
  - 답: `[2.5, 2.5] [0, 0]`
  - 날짜를 넘겨도 2시간 30분이라 `dt.days`는 0이다.

## 날짜 더하기·빼기·비교

- Q: 날짜에 일 수를 더하는 코드 — `d + pd.Timedelta(days=n)`
- Q: 날짜에 개월 수를 더하는 코드 — `d + pd.DateOffset(months=n)`
  - 달마다 일 수가 달라 Timedelta로는 개월을 더할 수 없다. 넘치는 날은 그 달 말일로 맞춘다.
- Q: 날짜형 열을 특정 날짜 이후로 거르는 코드 — `df[df['date'] >= '2026-03-01']`
  - 날짜형 열과 날짜 문자열을 바로 비교할 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  t = pd.Timestamp('2026-01-31')
  print(str((t + pd.DateOffset(months=1)).date()), str((t + pd.Timedelta(days=30)).date()))
  ```
  - 답: `2026-02-28 2026-03-02`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'date': pd.to_datetime(['2026-02-10', '2026-03-01', '2026-03-15', '2026-04-02']),
                     'v': [1, 2, 3, 4]})
  m = (df['date'] >= '2026-03-01') & (df['date'] < '2026-04-01')
  print(df.loc[m, 'v'].sum(), (pd.Timestamp('2026-04-02') - df['date'].min()).days)
  ```
  - 답: `5 51`
  - 2월 10일부터 4월 2일까지는 18 + 31 + 2 = 51일이다.

## str.contains

- Q: `str.contains`가 돌려주는 것 — 각 값이 패턴을 포함하는지를 담은 불리언 Series
- Q: `str.contains`의 `regex` 기본값 — `True`
  - 마침표·괄호·`+` 같은 문자를 글자 그대로 찾으려면 `regex=False`를 준다.
- Q: 대소문자를 무시하고 찾는 인자 — `case=False`
- Q: `str.contains`를 결측이 있는 열에 써서 불리언 인덱싱할 때 주는 인자 — `na=False`
  - 결측 자리가 NaN으로 남으면 인덱싱에서 오류가 난다.

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
  import numpy as np
  s = pd.Series(['apple', np.nan, 'banana', 'kiwi', 'Apricot'])
  print(s.str.contains('ap', case=False, na=False).sum(), s.str.contains('a|k', na=False).sum())
  ```
  - 답: `2 3`
  - `|`는 정규식에서 또는이다. a나 k를 포함하는 값은 apple, banana, kiwi다. Apricot은 대문자 A라 기본(`case=True`)으로는 걸리지 않는다.

## str.startswith · endswith

- Q: 문자열이 특정 글자로 시작하는 행만 고르는 메서드 — `str.startswith`
  - 끝 글자는 `str.endswith`. 둘 다 정규식이 아니라 글자 그대로 비교한다.
- Q: 여러 접두어 중 하나로 시작하는지 볼 때 `startswith`에 주는 것 — 문자열 튜플
  - 예: `s.str.startswith(('A', 'B'))`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['A101', 'B202', 'A303', 'C404', 'xA'])
  print(s.str.startswith('A').sum(), s.str.startswith(('A', 'B')).sum(), s.str.endswith('4').sum())
  ```
  - 답: `2 3 1`

## str.slice · str[:n]

- Q: 각 문자열의 앞 n글자를 자르는 두 가지 코드 — `s.str[:n]` 또는 `s.str.slice(0, n)`
  - 뒤 n글자는 `s.str[-n:]`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['AB-101', 'CD-205', 'AB-330', 'EF-112', 'AB-090'])
  print(s.str[:2].value_counts().idxmax(), s.str[-3:].astype(int).max())
  ```
  - 답: `AB 330`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['20261128', '20250301'])
  print(s.str.slice(0, 4).astype(int).tolist(), s.str.slice(4, 6).tolist(), s.str[0].tolist())
  ```
  - 답: `[2026, 2025] ['11', '03'] ['2', '2']`

## str.replace

- Q: pandas 2.x에서 `str.replace`의 `regex` 기본값 — `False`
  - 패턴을 글자 그대로 바꾼다. 정규식으로 바꾸려면 `regex=True`를 준다.
- Q: 숫자가 아닌 글자를 모두 지우는 코드 — `s.str.replace(r'\D', '', regex=True)`

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
  s = pd.Series(['a1.b2', 'c33'])
  print(s.str.replace('.', '').tolist(), s.str.replace(r'\d', '', regex=True).tolist())
  ```
  - 답: `['a1b2', 'c33'] ['a.b', 'c']`
  - 기본은 글자 그대로라 `.`만 지워진다.

## str.split

- Q: `str.split('-')`가 돌려주는 것 — 각 칸이 리스트인 Series
  - n번째 조각은 `.str[n]`으로 꺼낸다.
- Q: 나눈 조각을 바로 여러 열의 DataFrame으로 받는 인자 — `expand=True`
- Q: 앞에서부터 몇 번만 나눌지 정하는 인자 — `n`
  - `n=1`이면 처음 구분자에서만 나눠 두 조각이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['kim-서울-30', 'lee-부산-41', 'park-서울-25'])
  parts = s.str.split('-')
  print(parts.str[1].tolist(), parts.str[2].astype(int).sum())
  ```
  - 답: `['서울', '부산', '서울'] 96`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['2026-11-28', '2025-01-02'])
  e = s.str.split('-', expand=True)
  print(e.shape, e[0].astype(int).tolist(), s.str.split('-', n=1, expand=True).shape)
  ```
  - 답: `(2, 3) [2026, 2025] (2, 2)`

## str.len

- Q: 각 문자열의 글자 수를 주는 메서드 — `str.len()`
  - 결측이 섞이면 결과가 실수형이 된다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import numpy as np
  s = pd.Series(['apple', np.nan, 'banana', 'kiwi', 'Apricot'])
  print(s.str.len().max(), (s.str.len() >= 5).sum())
  ```
  - 답: `7.0 3`
  - 결측이 섞여 `str.len()` 결과가 실수형이라 `7.0`이 찍힌다.

## str.upper · lower · strip

- Q: 문자열 앞뒤 공백을 지우는 메서드 — `str.strip()`
  - 왼쪽만은 `lstrip`, 오른쪽만은 `rstrip`. 가운데 공백은 지우지 않는다.
- Q: 대소문자가 섞인 범주를 하나로 맞추는 메서드 — `str.lower()` 또는 `str.upper()`

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
  s = pd.Series([' a b ', 'Cd'])
  print(s.str.strip().tolist(), s.str.upper().str.strip().tolist())
  ```
  - 답: `['a b', 'Cd'] ['A B', 'CD']`

## str.extract

- Q: 정규식의 괄호 그룹에 걸린 부분을 꺼내는 메서드 — `str.extract`
  - 그룹이 하나여도 기본(`expand=True`)으로 DataFrame을 준다. Series로 받으려면 `expand=False`.
- Q: extract 결과 열 이름을 정하는 정규식 모양 — `(?P<이름>...)`
  - 이름이 없으면 열 이름은 0, 1, ...이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['강남구 12명', '서초구 7명', '송파구 30명'])
  n = s.str.extract(r'(\d+)')[0].astype(int)
  print(n.sum(), s.str.extract(r'(\d+)', expand=False).tolist())
  ```
  - 답: `49 ['12', '7', '30']`
  - 꺼낸 값은 문자열이라 계산하려면 `astype(int)`를 한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  s = pd.Series(['강남구 12명', '서초구 7명'])
  e = s.str.extract(r'(?P<gu>\w+구) (?P<n>\d+)')
  print(e.columns.tolist(), e.loc[1, 'gu'])
  ```
  - 답: `['gu', 'n'] 서초구`
