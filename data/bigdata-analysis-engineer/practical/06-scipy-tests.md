# scipy.stats · 가설검정

> scipy.stats 검정 함수(t검정, 정규성·등분산, 분산분석, 카이제곱, 비모수, 상관)의 호출 모양, 인자, 결과 읽기와 판단을 다룬다. 코드는 `from scipy import stats` 기준이다.

## 결과 읽기와 판단

- Q: scipy 검정 결과에서 통계량과 p값을 꺼내는 속성 — `.statistic`, `.pvalue`
  - `stat, p = stats.ttest_ind(a, b)`처럼 풀어도 된다. t검정 결과에는 `.df`(자유도)도 있다.
- Q: 유의수준 0.05에서 p값이 0.03이면 결론 — 귀무가설을 기각한다
- Q: 유의수준 0.01에서 p값이 0.03이면 결론 — 귀무가설을 기각하지 못한다
  - 문제가 준 α로 판단한다. 따로 없으면 0.05다.
- Q: scipy 검정 함수에서 단측·양측을 정하는 인자와 기본값 — `alternative`, 기본값 `'two-sided'`
  - 단측은 `'less'` 또는 `'greater'`. 방향은 첫 번째 인자를 기준으로 읽는다.
- Q: `stats.ttest_ind(a, b, alternative='greater')`의 대립가설 — a 모집단 평균이 b 모집단 평균보다 크다
- Q: 통계량 부호가 대립가설 방향과 같을 때 단측 p값과 양측 p값의 관계 — 단측 p값이 양측 p값의 절반이다
  - 부호가 반대 방향이면 단측 p값은 1 − (양측 p값 / 2)로 커진다.
- Q: 검정 함수에 NaN이 섞인 자료를 넣으면 기본으로 — 결과가 전부 `nan`이 된다 (`nan_policy='propagate'`)
  - `nan_policy='omit'`을 주거나 `dropna()`로 먼저 뺀다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  from scipy import stats
  s = pd.Series([52, 48, np.nan, 55, 51])
  print(stats.ttest_1samp(s, 50).pvalue)
  print(round(stats.ttest_1samp(s.dropna(), 50).pvalue, 4))
  ```
  - 답:
    ```text
    nan
    0.3751
    ```
  - pandas `mean()`과 달리 scipy는 결측을 알아서 빼지 않는다.

## stats.ttest_1samp

- Q: 한 집단의 평균이 특정 값과 같은지 볼 때 쓰는 함수 — `stats.ttest_1samp(x, popmean)`
  - 자유도는 n − 1.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [52, 48, 55, 51, 49, 53, 54, 50]
  res = stats.ttest_1samp(x, popmean=50)
  print(round(res.statistic, 3), round(res.pvalue, 4), res.df)
  ```
  - 답: `1.732 0.1269 7`
  - 유의수준 0.05에서 평균이 50이라는 H0를 기각하지 못한다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [52, 48, 55, 51, 49, 53, 54, 50]
  res = stats.ttest_1samp(x, popmean=50, alternative='greater')
  print(round(res.pvalue, 4))
  ```
  - 답: `0.0634`
  - t가 양수라 greater 단측 p값은 양측의 절반이다.
- Q: 빈칸을 채워 「평균이 100보다 작다」를 대립가설로 하는 검정을 완성하면?
  ```text
  from scipy import stats
  x = [96, 101, 94, 98, 97, 99]
  res = stats.ttest_1samp(x, ①, alternative=②)
  print(res.pvalue)
  ```
  - 답: ① `100` ② `'less'`
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [52, 48, 55, 51, 49, 53, 54, 50]
  ci = stats.ttest_1samp(x, 50).confidence_interval(0.95)
  print(round(ci.low, 2), round(ci.high, 2))
  ```
  - 답: `49.45 53.55`
  - 결과 객체의 `confidence_interval`이 모평균의 t 신뢰구간을 준다. 50이 구간 안에 있으니 양측 검정에서 기각하지 못한 것과 맞는다.

## stats.ttest_ind

- Q: 서로 다른 두 집단(남/여, A/B반)의 평균을 비교하는 함수 — `stats.ttest_ind(a, b)`
- Q: `ttest_ind`의 `equal_var` 기본값과 `False`의 뜻 — `True`(합동분산 t검정) / `False`면 Welch t검정
  - 「등분산을 가정하지 않는다」는 지시가 있으면 `False`.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  r1 = stats.ttest_ind(a, b)
  r2 = stats.ttest_ind(a, b, equal_var=False)
  print(round(r1.pvalue, 4), round(r2.pvalue, 4))
  print(r1.df, round(r2.df, 2))
  ```
  - 답:
    ```text
    0.1452 0.1362
    11.0 6.87
    ```
  - 합동분산 자유도는 n1 + n2 − 2, Welch는 Welch-Satterthwaite 식이라 소수가 나온다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  print(round(stats.ttest_ind(a, b, alternative='less').pvalue, 4))
  ```
  - 답: `0.0726`
  - t가 음수(a 평균이 더 작음)라 less 단측 p값이 양측(0.1452)의 절반이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  df = pd.DataFrame({'group': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
                     'score': [78, 85, 82, 88, 75, 90, 80, 84]})
  a = df.loc[df['group'] == 'A', 'score']
  b = df.loc[df['group'] == 'B', 'score']
  res = stats.ttest_ind(a, b)
  print(round(res.statistic, 3), round(res.pvalue, 4))
  ```
  - 답: `-3.939 0.0076`
  - 긴 형식(그룹 열 + 값 열)은 불리언 인덱싱으로 두 Series를 나눠 넣는다.

## stats.ttest_rel

- Q: 같은 대상을 처리 전후로 두 번 잰 값을 비교하는 함수 — `stats.ttest_rel(a, b)`
  - 두 배열 길이가 같아야 하고 같은 위치끼리 짝이다. 자유도는 쌍의 수 − 1.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  before = [72, 75, 68, 80, 77, 70]
  after = [75, 78, 70, 83, 76, 74]
  res = stats.ttest_rel(after, before)
  print(round(res.statistic, 3), round(res.pvalue, 4), res.df)
  ```
  - 답: `3.264 0.0224 5`
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  before = np.array([72, 75, 68, 80, 77, 70])
  after = np.array([75, 78, 70, 83, 76, 74])
  r1 = stats.ttest_rel(after, before)
  r2 = stats.ttest_1samp(after - before, 0)
  print(bool(np.isclose(r1.statistic, r2.statistic)))
  ```
  - 답: `True`
  - 대응표본 t검정은 차이값의 평균이 0인지 보는 단일표본 t검정과 같다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  before = [72, 75, 68, 80, 77, 70]
  after = [75, 78, 70, 83, 76, 74]
  print(stats.ttest_rel(before, after).statistic < 0)
  print(round(stats.ttest_rel(after, before, alternative='greater').pvalue, 4))
  ```
  - 답:
    ```text
    True
    0.0112
    ```
  - 순서를 바꾸면 t 부호가 바뀐다. 「처리 후가 더 크다」는 `(after, before, alternative='greater')`.

## stats.shapiro

- Q: `stats.shapiro`의 귀무가설 — 자료가 정규분포를 따른다
  - p값이 α보다 작으면 정규성이 없다고 보고 비모수 검정을 고려한다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [12, 15, 14, 10, 13, 15, 11, 14, 13, 12]
  res = stats.shapiro(x)
  print(round(res.statistic, 4), round(res.pvalue, 4), res.pvalue > 0.05)
  ```
  - 답: `0.9481 0.6459 True`
  - p값이 0.05보다 커서 정규성 가정을 기각하지 못한다.
- Q: 대응표본 자료의 정규성을 확인할 때 shapiro에 넣는 것 — 두 측정값의 차이
  - 대응표본 t검정은 차이가 정규분포를 따른다고 가정한다.

## stats.levene · stats.bartlett

- Q: 두 집단 이상의 분산이 같은지 보는 함수 두 가지 — `stats.levene`, `stats.bartlett`
  - bartlett은 정규성에 민감하고, levene은 정규성이 깨져도 비교적 버틴다. H0는 모든 집단의 분산이 같다.
- Q: `stats.levene`의 `center` 기본값 — `'median'`
  - `'mean'`이 원래 Levene 검정, `'median'`은 Brown-Forsythe 방식이다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  p_med = stats.levene(a, b).pvalue
  p_mean = stats.levene(a, b, center='mean').pvalue
  p_bart = stats.bartlett(a, b).pvalue
  print(round(p_med, 4), round(p_mean, 4), round(p_bart, 4))
  ```
  - 답: `0.063 0.028 0.0078`
  - 같은 자료인데 기본 levene만 0.05를 넘는다. 문제가 방법을 지정하면 그대로 따른다.
- Q: 빈칸을 채우면? (등분산 검정 결과로 t검정 방식을 고른다)
  ```text
  from scipy import stats
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  p_lev = stats.levene(a, b).pvalue
  res = stats.ttest_ind(a, b, equal_var=①)
  ```
  - 답: ① `p_lev > 0.05`
  - 등분산 H0를 기각하지 못하면 `True`(합동분산), 기각하면 `False`(Welch).

## 분산비 F검정 (stats.f) · 합동분산

- Q: scipy에 두 집단 분산비 F검정 함수가 있나 — 없다. 표본분산 비를 구해 `stats.f`로 p값을 계산한다
- Q: 분산비 F검정에서 「분자의 자유도가 분모의 자유도보다 크도록」 하라는 지시의 뜻 — 표본 수가 더 많은 집단의 표본분산을 분자에 둔다
  - 그래서 F가 1보다 작게 나올 수도 있다. 큰 분산을 분자에 두라는 뜻이 아니다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  a = [4.1, 3.8, 4.5, 4.9, 3.6, 4.2, 4.7, 3.9]
  b = [5.0, 4.4, 5.8, 3.9, 5.5]
  F = np.var(a, ddof=1) / np.var(b, ddof=1)
  d1, d2 = len(a) - 1, len(b) - 1
  p = 2 * min(stats.f.cdf(F, d1, d2), stats.f.sf(F, d1, d2))
  print(round(F, 3), round(p, 3))
  ```
  - 답: `0.341 0.204`
  - 표본분산이라 `ddof=1`. 양측이면 작은 쪽 꼬리 확률의 두 배다.
- Q: 두 집단의 합동 분산 추정량(pooled variance) 식 — ((n1 − 1)s1² + (n2 − 1)s2²) / (n1 + n2 − 2)
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  a = [4.1, 3.8, 4.5, 4.9, 3.6, 4.2, 4.7, 3.9]
  b = [5.0, 4.4, 5.8, 3.9, 5.5]
  n1, n2 = len(a), len(b)
  sp2 = ((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2)
  t = (np.mean(a) - np.mean(b)) / np.sqrt(sp2 * (1 / n1 + 1 / n2))
  p = 2 * stats.t.sf(abs(t), n1 + n2 - 2)
  print(round(sp2, 3), round(p, 3), round(stats.ttest_ind(a, b).pvalue, 3))
  ```
  - 답: `0.352 0.061 0.061`
  - 합동분산으로 직접 구한 t검정과 `ttest_ind` 기본값은 같은 결과를 낸다.

## stats.f_oneway

- Q: 세 집단 이상의 평균을 한 번에 비교하는 함수 — `stats.f_oneway(g1, g2, g3, ...)`
  - 집단을 리스트 하나로 묶지 않고 각각 인자로 넣는다.
- Q: 일원 분산분석에서 집단 수 k, 전체 관측치 N일 때 F의 자유도 — 분자 k − 1, 분모 N − k
- Q: 출력 결과는?
  ```text
  from scipy import stats
  g1 = [23, 25, 21, 24, 22]
  g2 = [28, 27, 30, 26, 29]
  g3 = [24, 26, 23, 25, 27]
  res = stats.f_oneway(g1, g2, g3)
  print(round(res.statistic, 3), round(res.pvalue, 4))
  ```
  - 답: `12.667 0.0011`
  - 세 집단 평균이 모두 같다는 H0를 기각한다. 어느 쌍이 다른지는 사후검정(Tukey HSD)으로 본다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  df = pd.DataFrame({'g': ['a'] * 5 + ['b'] * 5 + ['c'] * 5,
                     'y': [23, 25, 21, 24, 22, 28, 27, 30, 26, 29, 24, 26, 23, 25, 27]})
  groups = [s.values for _, s in df.groupby('g')['y']]
  print(len(groups), round(stats.f_oneway(*groups).statistic, 3))
  ```
  - 답: `3 12.667`
  - 긴 형식 자료는 groupby로 집단별 배열을 모은 뒤 `*`로 풀어 넣는다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  g1 = [23, 25, 21, 24, 22]
  g2 = [28, 27, 30, 26, 29]
  g3 = [24, 26, 23, 25, 27]
  res = stats.tukey_hsd(g1, g2, g3)
  print(round(res.pvalue[0, 1], 4), round(res.pvalue[0, 2], 4))
  ```
  - 답: `0.0008 0.1546`
  - `res.pvalue[i, j]`는 i번째와 j번째 집단 비교의 p값이다(0부터 센다).

## stats.chisquare

- Q: 관측 빈도가 정해진 비율을 따르는지 보는 적합도 검정 함수 — `stats.chisquare(f_obs, f_exp)`
  - 자유도는 범주 수 − 1.
- Q: `stats.chisquare`에서 `f_exp`를 주지 않으면 기대빈도 — 모든 범주가 같은 빈도(관측 빈도의 평균)
- Q: 출력 결과는?
  ```text
  from scipy import stats
  res = stats.chisquare([18, 22, 30, 30])
  print(round(res.statistic, 2), round(res.pvalue, 4))
  ```
  - 답: `4.32 0.2289`
  - 기대빈도는 100 / 4 = 25씩이다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  obs = np.array([55, 25, 20])
  ratio = np.array([0.5, 0.3, 0.2])
  exp = obs.sum() * ratio
  res = stats.chisquare(obs, f_exp=exp)
  print(exp.tolist(), round(res.statistic, 3), round(res.pvalue, 4))
  ```
  - 답: `[50.0, 30.0, 20.0] 1.333 0.5134`
  - 기대 비율은 반드시 전체 합에 곱해 빈도로 바꿔 넣는다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  try:
      stats.chisquare([55, 25, 20], f_exp=[0.5, 0.3, 0.2])
  except Exception as e:
      print(type(e).__name__)
  ```
  - 답: `ValueError`
  - 관측 합(100)과 기대 합(1)이 다르면 오류가 난다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  res = stats.chisquare([18, 22, 30, 30], ddof=1)
  print(round(res.pvalue, 4))
  ```
  - 답: `0.1153`
  - `ddof`는 자유도를 범주 수 − 1 − ddof로 줄인다. 자료에서 모수를 추정해 기대빈도를 만들 때 쓴다.

## stats.chi2_contingency

- Q: 두 범주형 변수가 서로 독립인지 보는 함수 — `stats.chi2_contingency(table)`
  - 원자료면 `pd.crosstab`으로 분할표를 먼저 만든다. 자유도는 (r − 1)(c − 1).
- Q: `chi2_contingency`의 `correction` 기본값과 적용 범위 — `True`, 자유도가 1인 2×2 표에서만 Yates 보정을 한다
- Q: `chi2_contingency` 결과를 튜플로 풀 때 순서 — 통계량, p값, 자유도, 기대빈도 배열
  - 속성 이름은 `statistic`, `pvalue`, `dof`, `expected_freq`.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  df = pd.DataFrame({'gender': ['M', 'M', 'F', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'M'],
                     'buy': ['Y', 'N', 'Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'N', 'N', 'Y']})
  table = pd.crosstab(df['gender'], df['buy'])
  r1 = stats.chi2_contingency(table)
  r2 = stats.chi2_contingency(table, correction=False)
  print(r1.dof, round(r1.pvalue, 4), round(r2.pvalue, 4))
  ```
  - 답: `1 0.2416 0.079`
  - 보정을 빼라는 문제면 `correction=False`. 같은 자료에서 결론이 바뀔 수 있다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  table = pd.DataFrame({'A': [30, 20], 'B': [15, 25], 'C': [5, 5]}, index=['M', 'F'])
  chi2, p, dof, exp = stats.chi2_contingency(table)
  print(dof, exp[0].tolist())
  print(round(chi2, 3), round(p, 4))
  ```
  - 답:
    ```text
    2 [25.0, 20.0, 5.0]
    4.5 0.1054
    ```
  - 기대빈도 = 행 합 × 열 합 / 전체 합. 2×3 표라 보정이 없다.

## stats.wilcoxon

- Q: 정규성이 없는 대응표본(전후 비교)에 쓰는 비모수 검정 — `stats.wilcoxon(x, y)` (부호순위 검정)
  - 차이 하나만 넣어 `stats.wilcoxon(x - y)`로 불러도 같다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  before = [85, 90, 78, 92, 88, 76, 95, 81]
  after = [80, 86, 79, 85, 82, 70, 91, 75]
  res = stats.wilcoxon(before, after)
  print(res.statistic, round(res.pvalue, 4))
  ```
  - 답: `1.0 0.0156`
  - 양측 검정의 통계량은 양의 순위합과 음의 순위합 중 작은 쪽이다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  before = [85, 90, 78, 92, 88, 76, 95, 81]
  after = [80, 86, 79, 85, 82, 70, 91, 75]
  res = stats.wilcoxon(before, after, alternative='greater')
  print(res.statistic, round(res.pvalue, 4))
  ```
  - 답: `35.0 0.0078`
  - 단측이면 통계량이 양의 순위합(x − y > 0 쪽)으로 바뀐다.

## stats.mannwhitneyu

- Q: 정규성이 없는 독립 두 집단을 비교하는 비모수 검정 — `stats.mannwhitneyu(a, b)`
- Q: 출력 결과는?
  ```text
  from scipy import stats
  a = [12, 15, 11, 18, 14, 13]
  b = [20, 17, 22, 16, 25, 19, 21]
  r1 = stats.mannwhitneyu(a, b)
  r2 = stats.mannwhitneyu(b, a)
  print(r1.statistic, r2.statistic, round(r1.pvalue, 4))
  ```
  - 답: `2.0 40.0 0.0047`
  - 통계량은 첫 인자의 U다. 순서를 바꾸면 n1 × n2 − U(42 − 2)가 나오고 양측 p값은 같다.
- Q: `mannwhitneyu`의 `method` 기본값 `'auto'`의 동작 — 표본이 작고 동점이 없으면 정확(exact) p값, 아니면 정규근사
  - `method='asymptotic'`을 주면 작은 표본에서도 근사 p값이 나와 값이 달라진다.

## stats.kruskal

- Q: 정규성이 없는 세 집단 이상을 비교하는 비모수 검정 — `stats.kruskal(g1, g2, g3, ...)`
  - H 통계량을 자유도 k − 1인 카이제곱으로 근사한다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  g1 = [3, 5, 4, 6, 2]
  g2 = [8, 9, 7, 10, 6]
  g3 = [5, 6, 7, 4, 5]
  res = stats.kruskal(g1, g2, g3)
  print(round(res.statistic, 3), round(res.pvalue, 4))
  ```
  - 답: `8.802 0.0123`

## stats.pearsonr · stats.spearmanr

- Q: 두 연속형 변수의 선형 상관과 그 유의성을 함께 주는 함수 — `stats.pearsonr(x, y)`
  - pandas `corr()`는 계수만 주고 p값을 주지 않는다. 검정 자유도는 n − 2.
- Q: 순위 기반 상관을 검정하는 함수 — `stats.spearmanr` (켄달은 `stats.kendalltau`)
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [2, 4, 5, 7, 8, 10]
  y = [3, 6, 5, 9, 11, 12]
  res = stats.pearsonr(x, y)
  print(round(res.statistic, 4), round(res.pvalue, 4))
  ```
  - 답: `0.9695 0.0014`
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [2, 4, 5, 7, 8, 10]
  y = [3, 6, 5, 9, 11, 12]
  ci = stats.pearsonr(x, y).confidence_interval(0.95)
  print(round(ci.low, 3), round(ci.high, 3))
  ```
  - 답: `0.741 0.997`
  - 상관계수의 신뢰구간(Fisher 변환)을 결과 객체가 준다.
- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [1, 2, 3, 4, 5, 6]
  y = [1, 4, 9, 16, 25, 100]
  r_p = stats.pearsonr(x, y).statistic
  r_s = stats.spearmanr(x, y).statistic
  print(round(r_p, 4), round(r_s, 4))
  ```
  - 답: `0.8086 1.0`
  - 순위가 완전히 같이 움직이면 스피어만은 1이다. 피어슨은 선형성만 본다.
