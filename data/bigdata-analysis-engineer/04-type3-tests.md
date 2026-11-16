# 작업형 3 · 가설검정

> 코드는 `from scipy import stats` 기준이다. 숫자는 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다.

## 가설과 판단

- **귀무가설 (Null Hypothesis, H0)** — 차이·효과·관계가 없다고 두는 기본 주장. 검정은 이 주장을 기각할 수 있는지를 본다
- **대립가설 (Alternative Hypothesis, H1)** — 분석자가 데이터로 보이고 싶은 주장. 차이가 있다, 크다, 작다처럼 쓴다
- **유의수준 (Significance Level, α)** — 참인 H0를 잘못 기각할 확률을 어디까지 허용할지 미리 정한 값. 따로 주지 않으면 0.05
- **p값 (p-value)** — H0가 참이라고 가정할 때 지금 얻은 검정통계량만큼, 또는 그보다 더 극단적인 값이 나올 확률
- **1종 오류 (Type I Error)** — 실제로는 참인 H0를 기각하는 잘못. 일어날 확률의 상한이 α다
- **2종 오류 (Type II Error)** — 실제로는 거짓인 H0를 기각하지 못하는 잘못. 1에서 이 확률을 뺀 것이 검정력이다
- Q: 유의수준 0.05에서 p값이 0.03이면 결론은? — 귀무가설 기각
- Q: 유의수준 0.01에서 p값이 0.03이면 결론은? — 귀무가설을 기각하지 못한다
  - 0.03은 0.05보다 작지만 0.01보다는 크다. 문제가 준 α로 판단한다.
- Q: scipy 검정 함수에서 단측·양측을 정하는 인자와 기본값은? — `alternative`, 기본값 `'two-sided'`
  - 단측은 `'less'` 또는 `'greater'`
- Q: `stats.ttest_ind(a, b, alternative='greater')`의 대립가설은? — a 모집단 평균이 b 모집단 평균보다 크다
  - 비교 방향은 인자 순서(첫 번째 기준)로 정해진다.
- Q: scipy 검정 결과에서 통계량과 p값을 꺼내는 속성 이름은? — `.statistic`, `.pvalue`
  - `stat, p = stats.ttest_ind(a, b)`처럼 튜플로 풀어도 된다.

## 상황별 검정 고르기

- Q: 한 집단의 평균이 특정 값(예: 50)과 같은지 볼 때 쓰는 함수는? — `stats.ttest_1samp`
- Q: 서로 다른 두 집단(남/여, A/B반)의 평균을 비교하는 함수는? — `stats.ttest_ind`
- Q: 같은 사람을 처리 전후로 두 번 잰 값을 비교하는 함수는? — `stats.ttest_rel`
- Q: 세 집단 이상의 평균을 한 번에 비교하는 함수는? — `stats.f_oneway` (일원 분산분석)
- Q: 데이터가 정규분포를 따르는지 볼 때 쓰는 함수는? — `stats.shapiro`
  - H0: 정규분포를 따른다. p값이 α보다 작으면 정규성이 없다고 본다.
- Q: 두 집단 이상의 분산이 같은지 보는 함수 두 가지는? — `stats.levene`, `stats.bartlett`
  - bartlett은 정규성에 민감하고, levene은 정규성이 깨져도 비교적 버틴다.
- Q: 정규성이 없는 독립 두 집단을 비교하는 비모수 검정은? — Mann-Whitney U (`stats.mannwhitneyu`)
- Q: 정규성이 없는 대응표본(전후 비교)에 쓰는 비모수 검정은? — Wilcoxon 부호순위 (`stats.wilcoxon`)
- Q: 정규성이 없는 세 집단 이상을 비교하는 비모수 검정은? — Kruskal-Wallis (`stats.kruskal`)
- Q: 관측 빈도가 정해진 비율(예: 2:1:1)을 따르는지 보는 함수는? — `stats.chisquare` (적합도 검정)
- Q: 두 범주형 변수가 서로 독립인지 보는 함수는? — `stats.chi2_contingency` (독립성 검정)
- Q: 분산분석에서 H0가 기각된 뒤 어느 집단 쌍이 다른지 찾는 절차는? — 사후검정 (Tukey HSD)

## t검정

- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [52, 48, 55, 51, 49, 53, 54, 50]
  res = stats.ttest_1samp(x, popmean=50)
  print(round(res.statistic, 3), round(res.pvalue, 4), res.df)
  ```
  - 답: `1.732 0.1269 7`
  - 자유도는 n − 1 = 7. 유의수준 0.05에서 H0(평균 50)를 기각하지 못한다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [52, 48, 55, 51, 49, 53, 54, 50]
  res = stats.ttest_1samp(x, popmean=50, alternative='greater')
  print(round(res.pvalue, 4))
  ```
  - 답: `0.0634`
  - t가 양수일 때 greater 단측 p값은 양측 p값의 절반이다.

- Q: 빈칸을 채워 "평균이 100보다 작다"를 대립가설로 하는 검정을 완성하면?
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
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  p1 = stats.ttest_ind(a, b).pvalue
  p2 = stats.ttest_ind(a, b, equal_var=False).pvalue
  print(round(p1, 4), round(p2, 4))
  ```
  - 답: `0.1452 0.1362`
  - 기본값 `equal_var=True`는 합동분산 t검정, `False`는 Welch t검정이다. 문제에서 "등분산을 가정하지 않는다"면 `False`를 넣는다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  a = [20, 22, 19, 24, 21, 23]
  b = [30, 18, 35, 15, 28, 26, 33]
  r1 = stats.ttest_ind(a, b)
  r2 = stats.ttest_ind(a, b, equal_var=False)
  print(r1.df, round(r2.df, 2))
  ```
  - 답: `11.0 6.87`
  - 합동분산은 n1 + n2 − 2. Welch는 Welch-Satterthwaite 식이라 소수가 나온다.

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
  - 긴 형식(그룹 열 + 값 열)은 불리언 인덱싱으로 두 시리즈를 나눠 넣는다. t가 음수인 것은 첫 인자(A) 평균이 더 작기 때문이다.

- Q: 출력 결과는?
  ```text
  from scipy import stats
  before = [72, 75, 68, 80, 77, 70]
  after = [75, 78, 70, 83, 76, 74]
  res = stats.ttest_rel(after, before)
  print(round(res.statistic, 3), round(res.pvalue, 4), res.df)
  ```
  - 답: `3.264 0.0224 5`
  - 대응표본의 자유도는 쌍의 수 − 1이다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  from scipy import stats
  before = np.array([72, 75, 68, 80, 77, 70])
  after = np.array([75, 78, 70, 83, 76, 74])
  r1 = stats.ttest_rel(after, before)
  r2 = stats.ttest_1samp(after - before, 0)
  print(round(r1.statistic, 6) == round(r2.statistic, 6))
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
  - 순서를 바꾸면 t의 부호가 바뀐다. "처리 후가 더 크다"는 `(after, before, alternative='greater')`로 쓴다.

## 정규성·등분산

- Q: 출력 결과는?
  ```text
  from scipy import stats
  x = [12, 15, 14, 10, 13, 15, 11, 14, 13, 12]
  res = stats.shapiro(x)
  print(round(res.pvalue, 4), res.pvalue > 0.05)
  ```
  - 답: `0.6459 True`
  - p값이 0.05보다 크면 정규성 가정을 기각하지 못한다.

- Q: `stats.levene`의 `center` 기본값은? — `'median'`
  - `'mean'`으로 바꾸면 원래 Levene 검정, `'median'`은 Brown-Forsythe 방식이다. 결과가 달라질 수 있다.

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
  - 같은 데이터인데 기본 levene만 0.05를 넘는다. 문제가 검정 방법을 지정하면 그대로 따른다.

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

## 분산분석

- **일원 분산분석 (One-way ANOVA)** — 범주형 요인 하나의 수준(집단)별로 연속형 반응의 평균이 모두 같은지 F통계량으로 검정하는 방법
- Q: 일원 분산분석에서 집단 수 k, 전체 관측치 N일 때 F의 자유도는? — 분자 k − 1, 분모 N − k

- Q: 출력 결과는?
  ```text
  from scipy import stats
  g1 = [23, 25, 21, 24, 22]
  g2 = [28, 27, 30, 26, 29]
  g3 = [24, 26, 23, 25, 27]
  res = stats.f_oneway(g1, g2, g3)
  print(round(res.statistic, 3), round(res.pvalue, 5))
  ```
  - 답: `12.667 0.0011`
  - p값이 0.05보다 작으므로 세 집단 평균이 모두 같다는 H0를 기각한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'g': ['a'] * 5 + ['b'] * 5 + ['c'] * 5,
                     'y': [23, 25, 21, 24, 22, 28, 27, 30, 26, 29, 24, 26, 23, 25, 27]})
  model = smf.ols('y ~ C(g)', data=df).fit()
  table = sm.stats.anova_lm(model)
  print(table['df'].tolist(), round(table.loc['C(g)', 'F'], 3))
  ```
  - 답: `[2.0, 12.0] 12.667`
  - 같은 데이터의 `f_oneway`와 F가 같다. `C()`는 숫자로 된 집단 코드도 범주로 다루게 한다.

- Q: `sm.stats.anova_lm`의 `typ` 기본값은? — `1` (Type I, 순차 제곱합)
  - 불균형 설계의 이원 분산분석은 `typ=2`나 `typ=3`과 결과가 달라진다. 문제가 지정하면 그대로 넣는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'A': ['x', 'x', 'x', 'x', 'y', 'y', 'y', 'y'],
                     'B': ['p', 'p', 'q', 'q', 'p', 'p', 'q', 'q'],
                     'y': [10, 12, 15, 17, 11, 13, 22, 24]})
  model = smf.ols('y ~ C(A) * C(B)', data=df).fit()
  table = sm.stats.anova_lm(model, typ=2)
  print(table.index.tolist())
  ```
  - 답: `['C(A)', 'C(B)', 'C(A):C(B)', 'Residual']`
  - `*`는 주효과 두 개와 상호작용(`:`)을 모두 넣는다. `+`만 쓰면 상호작용 행이 없다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'A': ['x', 'x', 'x', 'x', 'y', 'y', 'y', 'y'],
                     'B': ['p', 'p', 'q', 'q', 'p', 'p', 'q', 'q'],
                     'y': [10, 12, 15, 17, 11, 13, 22, 24]})
  model = smf.ols('y ~ C(A) * C(B)', data=df).fit()
  table = sm.stats.anova_lm(model, typ=2)
  print(round(table.loc['C(A):C(B)', 'F'], 2), round(table.loc['C(A):C(B)', 'PR(>F)'], 4))
  ```
  - 답: `9.0 0.0399`
  - p값 열 이름은 `PR(>F)`다. 상호작용이 유의하면 A의 효과가 B 수준에 따라 다르다는 뜻이다.

- Q: 출력 결과는?
  ```text
  from statsmodels.stats.multicomp import pairwise_tukeyhsd
  y = [23, 25, 21, 24, 22, 28, 27, 30, 26, 29, 24, 26, 23, 25, 27]
  g = ['a'] * 5 + ['b'] * 5 + ['c'] * 5
  res = pairwise_tukeyhsd(endog=y, groups=g, alpha=0.05)
  print(res.reject.tolist())
  ```
  - 답: `[True, False, True]`
  - 쌍 순서는 (a, b), (a, c), (b, c)다. `True`인 쌍의 평균 차이가 유의하다.

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

- Q: 집단이 4개일 때 Tukey HSD가 비교하는 쌍의 수는? — 6
  - k(k − 1) / 2

## 카이제곱 검정

- Q: `stats.chisquare`에서 `f_exp`를 주지 않으면 기대빈도는? — 모든 범주가 같은 빈도 (관측 빈도의 평균)

- Q: 출력 결과는?
  ```text
  from scipy import stats
  obs = [18, 22, 30, 30]
  res = stats.chisquare(obs)
  print(round(res.statistic, 2), round(res.pvalue, 4))
  ```
  - 답: `4.32 0.2289`
  - 기대빈도는 100 / 4 = 25씩이다. 자유도는 범주 수 − 1 = 3.

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
  - 관측 합(100)과 기대 합(1)이 다르면 오류가 난다. 비율을 그대로 넣는 실수다.

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
  - 2×2(자유도 1)에서만 기본값 `correction=True`가 Yates 연속성 보정을 한다. 보정을 빼라는 문제면 `False`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from scipy import stats
  table = pd.DataFrame({'A': [30, 20], 'B': [15, 25], 'C': [5, 5]}, index=['M', 'F'])
  res = stats.chi2_contingency(table)
  print(res.dof, res.expected_freq[0].tolist())
  print(round(res.statistic, 3), round(res.pvalue, 4))
  ```
  - 답:
    ```text
    2 [25.0, 20.0, 5.0]
    4.5 0.1054
    ```
  - 자유도 (2 − 1) × (3 − 1) = 2. 기대빈도 = 행 합 × 열 합 / 전체 합.

- Q: r행 c열 분할표의 독립성 검정 자유도는? — (r − 1)(c − 1)

## 비모수 검정

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
  a = [12, 15, 11, 18, 14, 13]
  b = [20, 17, 22, 16, 25, 19, 21]
  res = stats.mannwhitneyu(a, b)
  print(res.statistic, round(res.pvalue, 4))
  ```
  - 답: `2.0 0.0047`
  - 통계량은 첫 인자 a의 U다. 인자 순서를 바꾸면 n1 × n2 − U가 나온다.

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
  - 순위 기반 H 통계량이며 자유도 k − 1인 카이제곱 분포로 근사한다.

## 상관분석

- Q: 피어슨 상관계수 검정의 t통계량 자유도는? — n − 2

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
  x = [1, 2, 3, 4, 5, 6]
  y = [1, 4, 9, 16, 25, 100]
  r_p = stats.pearsonr(x, y).statistic
  r_s = stats.spearmanr(x, y).statistic
  print(round(r_p, 4), round(r_s, 4))
  ```
  - 답: `0.8086 1.0`
  - 순위가 완전히 같이 움직이면 스피어만은 1이다. 피어슨은 선형성만 본다.
  - 판다스 `df['x'].corr(df['y'])`는 기본이 피어슨이고 p값을 주지 않는다. 검정은 scipy로 한다.
