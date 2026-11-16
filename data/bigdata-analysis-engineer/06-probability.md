# 작업형 3 · 확률분포·추정·연관규칙

> 코드는 `from scipy import stats` 기준이다. 숫자는 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다.

## 분포 함수의 공통 메서드

- **pmf (Probability Mass Function)** — 이산분포에서 확률변수가 정확히 한 값 k를 가질 확률 P(X = k)를 돌려주는 메서드
- **pdf (Probability Density Function)** — 연속분포에서 한 점의 확률밀도. 확률 자체가 아니며, 구간 확률은 면적(cdf 차이)으로 구한다
- **cdf (Cumulative Distribution Function)** — P(X ≤ x)를 돌려주는 메서드. 이산분포에서는 x 자신을 포함한다
- **sf (Survival Function)** — 1 − cdf(x), 즉 P(X > x)를 돌려주는 메서드
- **ppf (Percent Point Function)** — cdf의 역함수. 누적확률 q를 주면 P(X ≤ x) = q가 되는 x를 돌려준다
- Q: 이산분포에서 P(X ≥ k)를 sf로 구하려면? — `sf(k - 1)`
  - sf(k)는 P(X > k)라서 k 자신이 빠진다.
- Q: `stats.norm.cdf(x, loc, scale)`에서 `scale`에 넣는 값은? — 표준편차
  - 분산이 주어지면 제곱근을 씌워 넣는다.

## 이항분포·포아송분포

- **이항분포 (Binomial Distribution)** — 성공 확률 p인 독립 시행을 n번 했을 때 성공 횟수의 분포. 평균 np, 분산 np(1 − p)
- **포아송분포 (Poisson Distribution)** — 일정한 시간·공간 단위에서 드물게 일어나는 사건의 발생 횟수 분포. 평균과 분산이 모두 λ
- Q: `stats.binom.pmf(k, n, p)`의 인자 순서는? — 성공 횟수 k, 시행 횟수 n, 성공 확률 p
- Q: `stats.poisson.pmf(k, mu)`에서 `mu`는? — 단위 구간당 평균 발생 횟수 λ
- Q: 1시간에 평균 6건 오는 문의가 30분 동안 오는 횟수의 포아송 모수는? — 3
  - 구간 길이에 비례해 λ를 바꾼다.

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
  print(round(stats.binom.cdf(2, n, p), 4))
  print(round(stats.binom.sf(2, n, p), 4), round(1 - stats.binom.cdf(2, n, p), 4))
  ```
  - 답:
    ```text
    0.3828
    0.6172 0.6172
    ```
  - 첫 줄은 P(X ≤ 2), 둘째 줄은 둘 다 P(X ≥ 3)이다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  n, p = 10, 0.3
  wrong = stats.binom.sf(3, n, p)
  right = stats.binom.sf(2, n, p)
  print(round(wrong, 4), round(right, 4))
  ```
  - 답: `0.3504 0.6172`
  - "3번 이상"을 sf(3)으로 쓰면 X = 3이 빠져 작게 나온다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  n, p = 20, 0.4
  print(stats.binom.mean(n, p), round(stats.binom.var(n, p), 2), round(stats.binom.std(n, p), 4))
  ```
  - 답: `8.0 4.8 2.1909`
  - 평균 np = 8, 분산 np(1 − p) = 4.8

- Q: 빈칸을 채워 "불량률 5%인 부품 50개 중 불량이 2개 이하일 확률"을 구하면?
  ```text
  from scipy import stats
  prob = stats.binom.①(2, ②, ③)
  ```
  - 답: ① `cdf` ② `50` ③ `0.05`

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.poisson.pmf(2, 3), 4))
  print(round(stats.poisson.cdf(2, 3), 4))
  ```
  - 답:
    ```text
    0.224
    0.4232
    ```
  - λ = 3일 때 P(X = 2)와 P(X ≤ 2)

- Q: 출력 결과는?
  ```text
  from scipy import stats
  mu = 4 * 0.5
  p0 = stats.poisson.pmf(0, mu)
  print(round(p0, 4), round(1 - p0, 4))
  ```
  - 답: `0.1353 0.8647`
  - 시간당 4건이면 30분 λ = 2. "적어도 1건"은 1 − P(X = 0)

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(stats.poisson.mean(3.5), stats.poisson.var(3.5))
  ```
  - 답: `3.5 3.5`

## 정규분포·t분포

- Q: 표준정규분포에서 상위 2.5%를 자르는 값(`norm.ppf(0.975)`)은? — 약 1.96
- Q: 표본이 작고 모표준편차를 모를 때 평균 구간추정에 쓰는 분포는? — 자유도 n − 1인 t분포

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
  - 분산 100을 scale에 그대로 넣은 두 번째 줄이 틀린 값이다. 표준편차 10을 넣어야 한다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  mu, sigma = 70, 5
  p = stats.norm.cdf(80, mu, sigma) - stats.norm.cdf(65, mu, sigma)
  print(round(p, 4))
  ```
  - 답: `0.8186`
  - 구간 확률은 cdf의 차이로 구한다. 65는 −1σ, 80은 +2σ 지점이다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.norm.sf(85, loc=75, scale=8), 4))
  ```
  - 답: `0.1056`
  - 평균 75, 표준편차 8에서 85점 초과 비율

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
  - 둘째 줄은 평균 50, 표준편차 10에서 하위 90% 지점(상위 10% 컷)이다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  print(round(stats.t.ppf(0.975, df=9), 3), round(stats.t.ppf(0.975, df=100), 3))
  ```
  - 답: `2.262 1.984`
  - 자유도가 커질수록 t분포 임계값이 1.96에 가까워진다.

## 기댓값·분산

- **기댓값 (Expected Value)** — 확률변수가 갖는 값에 그 확률을 곱해 모두 더한 값. 분포의 중심
- Q: 분산을 기댓값으로 나타내면? — E(X²) − {E(X)}²
- Q: Y = 3X + 2일 때 E(Y)와 Var(Y)는? — E(Y) = 3E(X) + 2, Var(Y) = 9Var(X)
  - 상수를 더하는 것은 분산에 영향이 없고, 곱한 상수는 제곱으로 들어간다.

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

## 점추정

- **점추정 (Point Estimation)** — 모수를 표본에서 계산한 하나의 값으로 추정하는 것. 모평균은 표본평균, 모분산은 n − 1로 나눈 표본분산을 쓴다
- **불편추정량 (Unbiased Estimator)** — 기댓값이 추정하려는 모수와 정확히 같은 추정량. n − 1로 나눈 표본분산이 모분산에 대해 이 성질을 갖는다
- **표준오차 (Standard Error)** — 표본평균의 표준편차. 표본표준편차를 √n으로 나눠 구한다
- Q: 판다스 `var()`·`std()`와 넘파이 `np.var()`·`np.std()`의 ddof 기본값은? — 판다스 1, 넘파이 0

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
  - 문제가 "불편분산" 또는 "표본분산"이면 ddof=1 값을 낸다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'w': [61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9]})
  print(round(df['w'].mean(), 3), round(df['w'].std(), 3), round(df['w'].std(ddof=0), 3))
  ```
  - 답: `60.475 1.737 1.625`

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  se1 = stats.sem(x)
  se2 = x.std(ddof=1) / np.sqrt(len(x))
  print(round(se1, 4), round(se2, 4))
  ```
  - 답: `0.614 0.614`
  - `stats.sem`의 ddof 기본값은 1이다.

## 구간추정

- **신뢰구간 (Confidence Interval)** — 같은 방식으로 표본을 반복해 구간을 만들 때 그중 정해진 비율(예: 95%)이 모수를 포함하도록 만든 구간
- Q: 다른 조건이 같을 때 표본 크기를 4배로 늘리면 평균 신뢰구간의 폭은? — 절반으로 준다
  - 폭이 표준오차 σ/√n에 비례한다.
- Q: 신뢰수준을 95%에서 99%로 올리면 구간의 폭은? — 넓어진다
- Q: 시험 환경 scipy(1.14)의 `stats.t.interval` 첫 인자 이름은? — `confidence`
  - 옛 버전은 `alpha`였다. 위치 인자로 `stats.t.interval(0.95, ...)`처럼 넣으면 버전과 상관없다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  lo, hi = stats.t.interval(0.95, df=len(x) - 1, loc=x.mean(), scale=stats.sem(x))
  print(round(lo, 2), round(hi, 2))
  ```
  - 답: `59.02 61.93`
  - scale에는 표준편차가 아니라 표준오차를 넣는다.

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
  - 식으로 직접 계산해도 `t.interval`과 같은 구간이 나온다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  x = np.array([61.2, 58.4, 63.0, 59.8, 60.5, 62.1, 57.9, 60.9])
  ci = stats.ttest_1samp(x, popmean=60).confidence_interval(0.95)
  print(round(ci.low, 2), round(ci.high, 2))
  ```
  - 답: `59.02 61.93`
  - t검정 결과 객체의 `confidence_interval`도 같은 구간을 준다(scipy 1.10 이상).

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  mean, sigma, n = 50.0, 4.0, 36
  lo, hi = stats.norm.interval(0.95, loc=mean, scale=sigma / np.sqrt(n))
  print(round(lo, 2), round(hi, 2))
  ```
  - 답: `48.69 51.31`
  - 모표준편차를 알면 정규분포(z)로 구간을 만든다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  n, k = 400, 120
  p_hat = k / n
  se = np.sqrt(p_hat * (1 - p_hat) / n)
  z = stats.norm.ppf(0.975)
  print(p_hat, round(p_hat - z * se, 4), round(p_hat + z * se, 4))
  ```
  - 답: `0.3 0.2551 0.3449`
  - 모비율 신뢰구간(정규근사): p̂ ± z × √(p̂(1 − p̂)/n)

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  df = pd.DataFrame({'churn': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]})
  p_hat = df['churn'].mean()
  lo, hi = stats.norm.interval(0.95, loc=p_hat, scale=(p_hat * (1 - p_hat) / len(df)) ** 0.5)
  print(round(p_hat, 4), round(lo, 4), round(hi, 4))
  ```
  - 답: `0.3333 0.0666 0.6001`
  - 0/1 열의 평균이 곧 표본비율이다.

## 연관규칙

- **지지도 (Support)** — 전체 거래 중 해당 품목(집합)이 함께 들어 있는 거래의 비율
- **신뢰도 (Confidence)** — A를 산 거래 중 B도 산 거래의 비율. P(B | A) = 지지도(A, B) / 지지도(A)
- **향상도 (Lift)** — A를 샀다는 정보가 B 구매 가능성을 얼마나 바꾸는지 나타내는 값. 신뢰도(A → B) / 지지도(B)
- Q: 향상도가 1이면? — A와 B는 서로 독립이다
  - 1보다 크면 함께 사는 경향(양의 연관), 1보다 작으면 서로 피하는 경향이다.
- Q: A → B와 B → A에서 값이 같은 지표와 다를 수 있는 지표는? — 지지도·향상도는 같고, 신뢰도는 다를 수 있다
- Q: 거래 10건 중 A 포함 5건, B 포함 4건, 둘 다 포함 2건일 때 A → B 향상도는? — 1
  - 신뢰도 2/5 = 0.4, 지지도(B) = 0.4, 향상도 0.4 / 0.4 = 1

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'milk':  [1, 1, 0, 1, 1, 0, 1, 0],
                     'bread': [1, 0, 1, 1, 1, 0, 1, 1],
                     'egg':   [0, 1, 0, 1, 0, 1, 1, 0]})
  sup_m = df['milk'].mean()
  sup_mb = ((df['milk'] == 1) & (df['bread'] == 1)).mean()
  print(sup_m, sup_mb)
  ```
  - 답: `0.625 0.5`
  - 0/1 열의 평균이 지지도다. 두 품목은 둘 다 1인 행의 비율이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'milk':  [1, 1, 0, 1, 1, 0, 1, 0],
                     'bread': [1, 0, 1, 1, 1, 0, 1, 1],
                     'egg':   [0, 1, 0, 1, 0, 1, 1, 0]})
  both = ((df['milk'] == 1) & (df['bread'] == 1)).mean()
  conf = both / df['milk'].mean()
  lift = conf / df['bread'].mean()
  print(round(conf, 4), round(lift, 4))
  ```
  - 답: `0.8 1.0667`
  - milk → bread 규칙. 향상도가 1보다 크므로 우유가 든 거래에 빵이 평소보다 조금 더 자주 함께 들어 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  df = pd.DataFrame({'milk':  [1, 1, 0, 1, 1, 0, 1, 0],
                     'bread': [1, 0, 1, 1, 1, 0, 1, 1],
                     'egg':   [0, 1, 0, 1, 0, 1, 1, 0]})
  both = ((df['milk'] == 1) & (df['egg'] == 1)).mean()
  conf_me = both / df['milk'].mean()
  conf_em = both / df['egg'].mean()
  print(round(conf_me, 4), round(conf_em, 4))
  ```
  - 답: `0.6 0.75`
  - 분모가 조건 쪽 품목의 지지도라 방향에 따라 신뢰도가 달라진다.

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
  - 긴 형식 거래 로그는 crosstab으로 거래 × 품목 표를 만든다. 같은 거래에 같은 품목이 두 번 있을 수 있으니 1로 자른다.

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
  - {A, B} → C 규칙. 조건 쪽이 품목 두 개면 두 열이 모두 1인 행이 분모가 된다.
