# numpy · scipy 기초 통계·분포

> numpy 요약 통계·변환·반올림 함수, scipy.stats 분포 객체(pmf·cdf·sf·ppf·interval), 표준화·거듭제곱 변환, 기술통계, 점추정·구간추정, 연관규칙 손계산을 다룬다. 코드는 `import numpy as np`, `from scipy import stats` 기준이다.

## np.mean · np.nanmean

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  x = np.array([1, 2, np.nan, 5])
  print(np.mean(x), round(np.nanmean(x), 3), round(pd.Series(x).mean(), 3))
  ```
  - 답: `nan 2.667 2.667`
  - numpy 함수는 결측을 그대로 퍼뜨리고, `nan`이 붙은 함수(`nanmean`·`nanstd`·`nanmedian`)가 결측을 뺀다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  a = np.array([[1, 2, 3],
                [4, 5, 6]])
  print(a.mean(axis=0).tolist(), a.mean(axis=1).tolist(), a.mean())
  ```
  - 답: `[2.5, 3.5, 4.5] [2.0, 5.0] 3.5`
  - `axis=0`은 행 방향으로 내려가며 열마다, `axis=1`은 행마다 계산한다. 생략하면 전체 하나다.

## np.var · np.std (ddof)

- Q: `np.var`·`np.std`의 `ddof` 기본값과 그 뜻 — `0`, n으로 나누는 모분산·모표준편차
  - pandas `var()`·`std()`는 기본 `ddof=1`(n − 1로 나누는 표본 값)이다. 같은 자료라도 라이브러리에 따라 답이 다르다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  x = [4, 8, 6, 5, 7]
  print(np.var(x), pd.Series(x).var())
  print(np.var(x, ddof=1))
  ```
  - 답:
    ```text
    2.0 2.5
    2.5
    ```
  - 편차 제곱합이 10이다. n = 5로 나누면 2.0, n − 1 = 4로 나누면 2.5.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  s = pd.Series([2, 4, 4, 4, 5, 5, 7, 9])
  print(round(s.std(), 2), round(np.std(s.values), 2), round(s.values.std(ddof=1), 2))
  ```
  - 답: `2.14 2.0 2.14`
  - 배열 메서드 `.std()`도 numpy라 기본 `ddof=0`이다. pandas Series의 `.std()`만 기본 1이다.

## np.percentile · np.quantile

- Q: `np.percentile`과 `np.quantile`의 차이 — 위치를 percentile은 0~100으로, quantile은 0~1로 받는다
  - 계산 방식은 같다. `np.percentile(x, 25)`와 `np.quantile(x, 0.25)`는 같은 값이다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  x = [1, 2, 3, 4]
  print(np.percentile(x, 25), np.quantile(x, 0.25), pd.Series(x).quantile(0.25))
  ```
  - 답: `1.75 1.75 1.75`
  - 위치 (4 − 1) × 0.25 = 0.75라 1과 2 사이 75% 지점이다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  x = [1, 2, 3, 4]
  print([float(np.percentile(x, 25, method=m)) for m in ['lower', 'higher', 'midpoint']])
  ```
  - 답: `[1.0, 2.0, 1.5]`
  - 보간하지 않고 아래 값, 위 값, 두 값의 가운데를 고른다. 문제가 방식을 지정할 때만 바꾼다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  x = np.array([12, 15, 14, 10, 13, 50, 11, 16, -8])
  q1, q3 = np.percentile(x, [25, 75])
  iqr = q3 - q1
  out = x[(x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)]
  print(q1, q3, out.tolist())
  ```
  - 답: `11.0 15.0 [50, -8]`
  - 위치 리스트를 주면 사분위수를 한 번에 받는다. 경계는 5와 21이다.

## np.log · np.log1p · np.exp · np.sqrt

- Q: 0이 들어 있는 0 이상 자료를 로그 변환할 때 쓰는 함수 — `np.log1p`
  - log(1 + x)라 0에서 0이 된다. `np.log(0)`은 `-inf`다. 되돌릴 때는 `np.expm1`.
- Q: 출력 결과는?
  ```text
  import numpy as np
  print(np.log(0), np.log1p(0), np.log10(1000), np.expm1(np.log1p(3)))
  ```
  - 답: `-inf 0.0 3.0 3.0`
  - `np.log(0)`은 오류 대신 경고와 함께 `-inf`를 돌려준다. 이후 평균이 전부 `-inf`가 된다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  s = pd.Series([0, 1, 2, 3, 50, 200])
  before = s.skew()
  after = np.log1p(s).skew()
  print(round(before, 2), round(after, 2))
  ```
  - 답: `2.16 0.93`
  - 오른쪽 꼬리가 긴 자료는 로그 변환으로 왜도가 줄어든다. numpy 함수를 Series에 쓰면 Series가 돌아온다.

## np.round · np.floor · np.ceil

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  print(round(2.5), round(3.5), np.round(2.5))
  print(pd.Series([0.5, 1.5, 2.5]).round().tolist())
  ```
  - 답:
    ```text
    2 4 2.0
    [0.0, 2.0, 2.0]
    ```
- Q: 출력 결과는?
  ```text
  print(round(0.125, 2), round(0.375, 2), round(2.675, 2))
  ```
  - 답: `0.12 0.38 2.67`
  - 0.125와 0.375는 이진수로 정확히 표현돼 짝수 쪽으로 간다. 2.675는 실제 저장값이 2.67499…라 내려간다.
- Q: 시험지의 「반올림」(사사오입)과 `round`가 다른 답을 내는 경우 — 반올림할 자리 바로 뒤가 정확히 5일 때뿐
  - 일반 실수 계산 결과는 거의 이 경우가 아니라 `round(x, k)`를 그대로 써도 된다.
- Q: 출력 결과는?
  ```text
  from decimal import Decimal, ROUND_HALF_UP
  x = 2.675
  print(float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)))
  ```
  - 답: `2.68`
  - 사사오입이 꼭 필요하면 문자열을 거쳐 `Decimal`로 자른다. `Decimal(x)`처럼 실수를 바로 넣으면 2.67499…가 그대로 들어간다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  print(np.floor(-2.5), np.ceil(-2.5), np.trunc(-2.5), int(-2.5))
  ```
  - 답: `-3.0 -2.0 -2.0 -2`
  - `floor`는 작은 쪽, `ceil`은 큰 쪽, `trunc`와 `int()`는 0 쪽으로 자른다. 음수에서 `floor`와 `int`가 갈린다.

## np.where

- Q: `np.where(cond, a, b)`가 돌려주는 것 — cond가 참인 자리는 a, 거짓인 자리는 b인 배열
  - 인자를 cond 하나만 주면 참인 위치의 인덱스 튜플을 돌려준다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  df = pd.DataFrame({'score': [55, 72, 90, 38]})
  df['pass'] = np.where(df['score'] >= 60, 'Y', 'N')
  print(df['pass'].tolist(), (df['pass'] == 'Y').sum())
  ```
  - 답: `['N', 'Y', 'Y', 'N'] 2`
- Q: 출력 결과는?
  ```text
  import numpy as np
  x = np.array([0, 3, 0, 5])
  print(np.where(x > 0)[0].tolist())
  ```
  - 답: `[1, 3]`
  - 인자가 하나면 위치를 준다. 결과가 튜플이라 `[0]`으로 꺼낸다.

## np.select

- Q: 출력 결과는?
  ```text
  import numpy as np
  s = np.array([95, 82, 67, 45])
  conds = [s >= 90, s >= 80, s >= 60]
  print(np.select(conds, ['A', 'B', 'C'], default='F').tolist())
  print(np.select(conds, ['A', 'B', 'C']).tolist())
  ```
  - 답:
    ```text
    ['A', 'B', 'C', 'F']
    ['A', 'B', 'C', '0']
    ```
  - `default` 기본값은 0이다. 문자열 선택지에서는 문자열 `'0'`이 들어간다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  s = np.array([95, 82, 67, 45])
  print(np.select([s >= 60, s >= 80, s >= 90], ['C', 'B', 'A'], default='F').tolist())
  ```
  - 답: `['C', 'C', 'C', 'F']`
  - 95점도 첫 조건(60 이상)에서 걸린다. 조건은 좁은 것부터 쓴다.

## scipy.stats 분포 메서드

- Q: 이산분포에서 P(X = k)를 주는 메서드 — `pmf`
  - 연속분포에는 `pmf`가 없고 `pdf`(밀도)가 있다. 밀도는 확률이 아니다.
- Q: 이산분포에서 P(X ≥ k)를 sf로 구하려면 — `sf(k - 1)`
  - `sf(k)`는 P(X > k)라서 k 자신이 빠진다.
- Q: `ppf(q)`가 돌려주는 값 — 누적확률이 q가 되는 x (cdf의 역함수)
- Q: 연속분포 메서드의 `loc`·`scale`에 넣는 값 — 정규분포 기준 평균과 표준편차
  - 기본값은 `loc=0`, `scale=1`. 분산이 주어지면 제곱근을 씌운다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  rv = stats.norm(loc=60, scale=10)
  print(round(rv.cdf(70), 4), round(stats.norm.cdf(70, 60, 10), 4))
  ```
  - 답: `0.8413 0.8413`
  - 모수를 먼저 넣어 얼린(frozen) 분포 객체를 만들면 메서드마다 모수를 다시 쓰지 않아도 된다.

## stats.binom

- Q: `stats.binom.pmf(k, n, p)`의 인자 순서 — 성공 횟수 k, 시행 횟수 n, 성공 확률 p
- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.binom.pmf(3, 10, 0.3), 4))
  ```
  - 답: `0.2668`
  - 10번 중 정확히 3번 성공할 확률. 10C3 × 0.3³ × 0.7⁷
- Q: 출력 결과는?
  ```text
  from scipy import stats
  n, p = 10, 0.3
  wrong = stats.binom.sf(3, n, p)
  right = stats.binom.sf(2, n, p)
  print(round(wrong, 4), round(right, 4), round(1 - stats.binom.cdf(2, n, p), 4))
  ```
  - 답: `0.3504 0.6172 0.6172`
  - 「3번 이상」을 `sf(3)`으로 쓰면 X = 3이 빠져 작게 나온다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  n, p = 20, 0.4
  print(stats.binom.mean(n, p), round(stats.binom.var(n, p), 2), round(stats.binom.std(n, p), 4))
  ```
  - 답: `8.0 4.8 2.1909`
  - 평균 np, 분산 np(1 − p)
- Q: 빈칸을 채워 「불량률 5%인 부품 50개 중 불량이 2개 이하일 확률」을 구하면?
  ```text
  from scipy import stats
  prob = stats.binom.①(2, ②, ③)
  ```
  - 답: ① `cdf` ② `50` ③ `0.05`

## stats.poisson

- Q: `stats.poisson.pmf(k, mu)`에서 `mu` — 단위 구간당 평균 발생 횟수 λ
  - 구간 길이가 바뀌면 λ도 비례해서 바꾼다. 1시간에 6건이면 30분은 3.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.poisson.pmf(2, 3), 4), round(stats.poisson.cdf(2, 3), 4))
  ```
  - 답: `0.224 0.4232`
  - λ = 3일 때 P(X = 2)와 P(X ≤ 2)
- Q: 출력 결과는?
  ```text
  from scipy import stats
  mu = 4 * 0.5
  p0 = stats.poisson.pmf(0, mu)
  print(round(p0, 4), round(1 - p0, 4), round(stats.poisson.sf(0, mu), 4))
  ```
  - 답: `0.1353 0.8647 0.8647`
  - 시간당 4건이면 30분 λ = 2. 「적어도 1건」은 1 − P(X = 0) = `sf(0)`

## stats.norm

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.norm.cdf(70, loc=60, scale=10), 4))
  print(round(stats.norm.cdf(70, loc=60, scale=100), 4))
  ```
  - 답:
    ```text
    0.8413
    0.5398
    ```
  - 분산 100을 `scale`에 그대로 넣은 둘째 줄이 틀린 값이다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  mu, sigma = 70, 5
  p = stats.norm.cdf(80, mu, sigma) - stats.norm.cdf(65, mu, sigma)
  print(round(p, 4), round(stats.norm.sf(85, loc=75, scale=8), 4))
  ```
  - 답: `0.8186 0.1056`
  - 구간 확률은 cdf의 차이, 상위 비율은 `sf`로 구한다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.norm.ppf(0.95), 3), round(stats.norm.ppf(0.975), 3))
  print(round(stats.norm.ppf(0.9, loc=50, scale=10), 2))
  ```
  - 답:
    ```text
    1.645 1.96
    62.82
    ```
  - 둘째 줄은 평균 50, 표준편차 10에서 상위 10%를 자르는 점수다.

## stats.t · stats.chi2 · stats.f

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.t.ppf(0.975, df=9), 3), round(stats.t.ppf(0.975, df=100), 3))
  ```
  - 답: `2.262 1.984`
  - 자유도가 커질수록 t 임계값이 1.96에 가까워진다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  t, df = 2.5, 12
  print(round(2 * stats.t.sf(abs(t), df), 4), round(stats.t.sf(t, df), 4))
  ```
  - 답: `0.0279 0.014`
  - 손으로 구한 검정통계량의 p값은 `sf`로 얻는다. 양측 p값은 한쪽 꼬리의 두 배다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.chi2.ppf(0.95, 3), 3), round(stats.chi2.sf(7.815, 3), 3))
  print(round(stats.f.ppf(0.95, 2, 12), 3))
  ```
  - 답:
    ```text
    7.815 0.05
    3.885
    ```
  - 카이제곱·F 검정은 오른쪽 꼬리만 본다. `stats.f`는 분자 자유도, 분모 자유도 순서다.

## stats.zscore

- Q: `stats.zscore`의 `ddof` 기본값 — `0` (모표준편차로 나눈다)
  - pandas로 `(s - s.mean()) / s.std()`를 하면 `ddof=1`이라 값이 조금 다르다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [2, 4, 6, 8]
  print(stats.zscore(x).round(3).tolist())
  print(stats.zscore(x, ddof=1).round(3).tolist())
  ```
  - 답:
    ```text
    [-1.342, -0.447, 0.447, 1.342]
    [-1.162, -0.387, 0.387, 1.162]
    ```
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([10, 12, 11, 13, 12, 11, 10, 12, 11, 13, 12, 60])
  z = stats.zscore(x)
  print(x[np.abs(z) > 3].tolist())
  ```
  - 답: `[60]`
  - z 절댓값이 3을 넘는 값을 이상치로 보는 규칙이다. 기준(2 또는 3)은 문제가 준 값을 쓴다.

## stats.boxcox · stats.yeojohnson

- Q: `stats.boxcox(x)`를 `lmbda` 없이 부르면 돌려주는 것 — 변환된 배열과 추정한 λ의 튜플
  - `lmbda=`를 지정하면 배열 하나만 돌려준다. 0이나 음수가 섞이면 ValueError라 그때는 `stats.yeojohnson`을 쓴다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([1.0, np.e, np.e ** 2])
  print(stats.boxcox(x, lmbda=0).round(3).tolist(), stats.boxcox(x, lmbda=1).round(3).tolist())
  ```
  - 답: `[0.0, 1.0, 2.0] [0.0, 1.718, 6.389]`
  - λ = 0이면 자연로그, λ = 1이면 x − 1이다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  y, lam = stats.boxcox([1, 2, 3, 4, 10])
  print(round(lam, 4), round(y[-1], 4))
  ```
  - 답: `-0.1207 2.0103`
  - λ는 최대우도로 추정한다. 반환이 두 개라 언패킹하지 않으면 튜플 전체가 들어간다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([0.0, 1.0, 3.0])
  print(stats.yeojohnson(x, lmbda=0).round(3).tolist(), np.log1p(x).round(3).tolist())
  ```
  - 답: `[0.0, 0.693, 1.386] [0.0, 0.693, 1.386]`
  - 0 이상인 값에서 λ = 0인 Yeo-Johnson은 `log1p`와 같다.

## stats.describe · skew · kurtosis

- Q: `stats.describe`가 돌려주는 항목 — nobs, minmax, mean, variance, skewness, kurtosis
  - variance는 `ddof=1`, skewness·kurtosis는 `bias=True`(보정 안 함)가 기본이다.
- Q: `stats.kurtosis`의 `fisher` 기본값과 뜻 — `True`, 정규분포를 0으로 맞춘 초과첨도
  - `fisher=False`면 정규분포가 3인 원래 첨도를 준다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  x = [1, 2, 3, 4, 10]
  print(round(pd.Series(x).skew(), 3), round(stats.skew(x), 3), round(stats.skew(x, bias=False), 3))
  ```
  - 답: `1.697 1.138 1.697`
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  x = [1, 2, 3, 4, 10]
  print(round(stats.kurtosis(x), 3), round(stats.kurtosis(x, fisher=False), 3))
  print(round(pd.Series(x).kurt(), 3), round(stats.kurtosis(x, bias=False), 3))
  ```
  - 답:
    ```text
    -0.212 2.788
    3.152 3.152
    ```
  - `fisher` 차이는 정확히 3이다. 보정 여부는 작은 표본에서 값을 크게 바꾼다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  d = stats.describe([1, 2, 3, 4, 10])
  print(d.nobs, d.minmax, d.mean, d.variance)
  ```
  - 답: `5 (1, 10) 4.0 12.5`

## stats.sem과 점추정

- Q: 모평균·모분산의 점추정값으로 쓰는 것 — 표본평균, n − 1로 나눈 표본분산
  - n − 1로 나눈 분산은 기댓값이 모분산과 같은 불편추정량이다.
- Q: `stats.sem(x)`가 계산하는 값 — 표준오차, 표본표준편차(ddof=1) / √n
  - `ddof` 기본값이 1이다. `np.std`(기본 0)로 손계산하면 값이 다르다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  se1 = stats.sem(x)
  se2 = x.std(ddof=1) / np.sqrt(len(x))
  print(round(x.mean(), 3), round(se1, 4), round(se2, 4))
  ```
  - 답: `60.475 0.614 0.614`
- Q: 출력 결과는?
  ```text
  import numpy as np
  x = np.array([0, 1, 2, 3])
  p = np.array([0.1, 0.3, 0.4, 0.2])
  ex = (x * p).sum()
  var = (x ** 2 * p).sum() - ex ** 2
  print(round(ex, 2), round(var, 2))
  ```
  - 답: `1.7 0.81`
  - 확률분포표가 주어지면 E(X) = Σxp, Var(X) = E(X²) − {E(X)}²

## stats.t.interval · stats.norm.interval

- Q: scipy 1.14의 `interval` 첫 인자 이름 — `confidence`
  - 옛 버전은 `alpha`였다. `stats.t.interval(0.95, ...)`처럼 위치 인자로 넣으면 이름과 상관없다.
- Q: 모표준편차를 모르는 소표본 평균의 신뢰구간에 쓰는 분포 — 자유도 n − 1인 t분포 (`stats.t.interval`)
  - 모표준편차를 알면 `stats.norm.interval`.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  lo, hi = stats.t.interval(0.95, df=len(x) - 1, loc=x.mean(), scale=stats.sem(x))
  print(round(lo, 2), round(hi, 2))
  ```
  - 답: `59.02 61.93`
  - `scale`에는 표준편차가 아니라 표준오차를 넣는다.
- Q: 빈칸을 채워 모평균의 95% 신뢰구간을 구하면?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([12.1, 11.8, 12.5, 12.0, 11.6, 12.3])
  ci = stats.t.interval(0.95, df=①, loc=x.mean(), scale=②)
  ```
  - 답: ① `len(x) - 1` ② `stats.sem(x)`
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  n = len(x)
  t_crit = stats.t.ppf(0.975, n - 1)
  margin = t_crit * x.std(ddof=1) / np.sqrt(n)
  print(round(t_crit, 4), round(x.mean() - margin, 2), round(x.mean() + margin, 2))
  ```
  - 답: `2.3646 59.02 61.93`
  - 식으로 직접 풀어도 `t.interval`과 같은 구간이 나온다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  mean, sigma, n = 50.0, 4.0, 36
  lo, hi = stats.norm.interval(0.95, loc=mean, scale=sigma / np.sqrt(n))
  print(round(lo, 2), round(hi, 2))
  ```
  - 답: `48.69 51.31`
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  df = pd.DataFrame({'churn': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]})
  p_hat = df['churn'].mean()
  se = (p_hat * (1 - p_hat) / len(df)) ** 0.5
  lo, hi = stats.norm.interval(0.95, loc=p_hat, scale=se)
  print(round(p_hat, 4), round(lo, 4), round(hi, 4))
  ```
  - 답: `0.3333 0.0666 0.6001`
  - 모비율 구간(정규근사)은 p̂ ± z × √(p̂(1 − p̂)/n). 0/1 열의 평균이 표본비율이다.

## 연관규칙 (support · confidence · lift)

- Q: 신뢰도 A → B 계산 — support(A, B) / support(A)
  - 방향을 바꾸면 분모가 바뀌어 값이 달라질 수 있다.
- Q: 향상도 A → B 계산 — confidence(A → B) / support(B)
  - 1이면 독립, 1보다 크면 함께 사는 경향이다. 방향을 바꿔도 값이 같다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'milk':  [1, 1, 0, 1, 1, 0, 1, 0],
                     'bread': [1, 0, 1, 1, 1, 0, 1, 1]})
  both = ((df['milk'] == 1) & (df['bread'] == 1)).mean()
  conf = both / df['milk'].mean()
  lift = conf / df['bread'].mean()
  print(both, round(conf, 4), round(lift, 4))
  ```
  - 답: `0.5 0.8 1.0667`
  - milk → bread 규칙. 향상도가 1보다 조금 크다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'milk': [1, 1, 0, 1, 1, 0, 1, 0],
                     'egg':  [0, 1, 0, 1, 0, 1, 1, 0]})
  both = ((df['milk'] == 1) & (df['egg'] == 1)).mean()
  print(round(both / df['milk'].mean(), 4), round(both / df['egg'].mean(), 4))
  ```
  - 답: `0.6 0.75`
  - milk → egg와 egg → milk의 신뢰도. 분모가 조건 쪽 지지도다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  log = pd.DataFrame({'tid':  [1, 1, 2, 2, 2, 3, 4, 4, 5, 5],
                      'item': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'C', 'B', 'C']})
  basket = pd.crosstab(log['tid'], log['item']).clip(upper=1)
  sup_ac = ((basket['A'] == 1) & (basket['C'] == 1)).mean()
  print(basket.shape, sup_ac)
  ```
  - 답: `(5, 3) 0.4`
  - 긴 형식 거래 기록은 `crosstab`으로 거래 × 품목 표를 만들고, 같은 품목이 두 번 있을 수 있으니 1로 자른다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'A': [1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
                     'B': [1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
                     'C': [1, 0, 0, 0, 1, 0, 0, 1, 1, 1]})
  ab = (df['A'] == 1) & (df['B'] == 1)
  abc = ab & (df['C'] == 1)
  conf = abc.mean() / ab.mean()
  print(ab.mean(), abc.mean(), round(conf, 4), round(conf / df['C'].mean(), 4))
  ```
  - 답: `0.5 0.4 0.8 1.6`
  - {A, B} → C 규칙. 조건 쪽이 두 품목이면 두 열이 모두 1인 행이 분모다.
