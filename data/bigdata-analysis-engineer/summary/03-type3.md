# 작업형 3 · 검정과 회귀

> 시험 버전 scipy 1.14 · statsmodels 0.14 기준. 답은 화면 표를 눈으로 읽지 말고 결과 객체의 속성으로 꺼내 반올림한다.

## 0. 공통

```python
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
```

- 판정: p값 < 유의수준(보통 0.05)이면 귀무가설 기각, 아니면 채택(기각하지 못함).
- 검정 결과는 `res.statistic`, `res.pvalue`로 꺼낸다. 소수 자리는 `round(x, 3)`.
- 단측 검정은 `alternative='greater'` 또는 `'less'`. 방향은 첫 인자 − 둘째 인자 기준이다. 대립가설이 「A가 B보다 크다」면 `(A, B, alternative='greater')`.
- 표본표준편차·표본분산은 `ddof=1`. pandas `.std()`·`.var()`는 기본이 1, numpy `np.std`·`np.var`는 기본이 0.

## 1. 어떤 검정을 쓰나

| 묻는 것 | 검정 | 함수 |
|---|---|---|
| 한 집단 평균이 기준값과 같은가 | 단일표본 t | `stats.ttest_1samp(x, 기준값)` |
| 두 독립 집단 평균 (등분산 가정) | 독립표본 t | `stats.ttest_ind(a, b)` |
| 두 독립 집단 평균 (등분산 가정 안 함) | Welch t | `stats.ttest_ind(a, b, equal_var=False)` |
| 같은 대상의 전후 | 대응표본 t | `stats.ttest_rel(after, before)` |
| 정규분포를 따르나 | Shapiro-Wilk | `stats.shapiro(x)` |
| 두 집단 이상의 분산이 같나 | Levene · Bartlett | `stats.levene(a, b)` · `stats.bartlett(a, b)` |
| 두 집단 분산비 | F 검정 | 직접 계산 (아래 2절) |
| 세 집단 이상 평균 | 일원분산분석 | `stats.f_oneway(g1, g2, g3)` |
| 두 요인과 상호작용 | 이원분산분석 | `smf.ols('y ~ C(A) * C(B)')` + `sm.stats.anova_lm` |
| 어느 집단끼리 다른가 | Tukey HSD | `pairwise_tukeyhsd(y, group)` |
| 범주 비율이 기대와 같나 | 카이제곱 적합도 | `stats.chisquare(관측, f_exp=기대)` |
| 두 범주형 변수가 독립인가 | 카이제곱 독립성 | `stats.chi2_contingency(pd.crosstab(a, b))` |
| 정규성 못 쓸 때 두 독립 집단 | Mann-Whitney U | `stats.mannwhitneyu(a, b)` |
| 정규성 못 쓸 때 대응 | Wilcoxon 부호순위 | `stats.wilcoxon(after, before)` |
| 정규성 못 쓸 때 세 집단 이상 | Kruskal-Wallis | `stats.kruskal(g1, g2, g3)` |
| 두 연속형 변수의 상관 | 피어슨 · 스피어만 | `stats.pearsonr(x, y)` · `stats.spearmanr(x, y)` |
| 연속형 y를 설명 | 선형회귀 | `smf.ols('y ~ x1 + x2', data=df).fit()` |
| 0/1 y를 설명 | 로지스틱 회귀 | `smf.logit('y ~ x1 + x2', data=df).fit()` |

## 2. t검정

### 단일표본 t

```python
x = [12.1, 11.8, 12.4, 12.0, 11.6, 12.3, 11.9, 12.2]
res = stats.ttest_1samp(x, 12)                          # 양측
res = stats.ttest_1samp(x, 12, alternative='less')      # 대립가설: 평균 < 12
print(round(res.statistic, 3), round(res.pvalue, 4), res.df)   # 자유도 n − 1
ci = res.confidence_interval(0.95)                      # 신뢰구간 (단측이면 한쪽이 무한대)
print(round(ci.low, 3), round(ci.high, 3))
```

신뢰구간을 손으로 구하면 `stats.t.interval(0.95, n - 1, loc=np.mean(x), scale=stats.sem(x))`. `stats.sem`은 `ddof=1` 표준오차다.

### 독립표본 t (합동분산 · Welch)

```python
a = [23, 25, 28, 30, 26, 27, 24]
b = [20, 22, 25, 21, 24, 23]
res = stats.ttest_ind(a, b)                    # equal_var=True 기본: 합동분산, 자유도 n1 + n2 − 2
res_w = stats.ttest_ind(a, b, equal_var=False) # Welch: 자유도가 소수로 나온다
print(round(res.pvalue, 4), round(res_w.pvalue, 4))
```

합동 분산 추정량과 두 집단 분산비 F 검정은 함수가 따로 없어 직접 계산한다.

```python
n1, n2 = len(a), len(b)
v1, v2 = np.var(a, ddof=1), np.var(b, ddof=1)
sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)     # 합동 분산
F = v1 / v2                                                 # 분자·분모는 지문 지시대로
p = 2 * min(stats.f.cdf(F, n1 - 1, n2 - 1), stats.f.sf(F, n1 - 1, n2 - 1))   # 양측
print(round(sp2, 3), round(F, 3), round(p, 4))
```

> 「분자의 자유도가 분모의 자유도보다 크도록」은 표본 수가 많은 집단의 분산을 분자에 두라는 뜻이다. 큰 분산을 분자에 두라는 뜻이 아니다.

### 대응표본 t

```python
before = [72, 68, 75, 80, 66, 71, 77]
after  = [70, 65, 74, 76, 66, 68, 73]
res = stats.ttest_rel(after, before)                       # 차이 = after − before
res = stats.ttest_rel(after, before, alternative='less')   # 대립가설: 평균 차이 < 0
d = np.array(after) - np.array(before)
print(round(res.statistic, 3), round(res.pvalue, 4), round(d.mean(), 3))
```

대응표본 t는 차이 d에 대한 단일표본 t와 같다: `stats.ttest_1samp(d, 0)`. 긴 형식(id, 시점, 값) 데이터면 먼저 `pivot`으로 전·후 칼럼을 만든다.

## 3. 정규성과 등분산

```python
x = [5.1, 4.9, 5.3, 5.0, 5.6, 4.8, 5.2, 5.4, 4.7, 5.0]
res = stats.shapiro(x)                       # 귀무가설: 정규분포를 따른다
print(round(res.statistic, 4), round(res.pvalue, 4))

a, b, c = [10, 12, 11, 13, 12], [14, 9, 16, 8, 15], [11, 12, 12, 13, 11]
print(stats.levene(a, b, c).pvalue)                 # 기본 center='median' (Brown-Forsythe)
print(stats.levene(a, b, c, center='mean').pvalue)  # 원래 Levene
print(stats.bartlett(a, b, c).pvalue)               # 정규성 가정
```

p > 0.05면 정규성·등분산을 기각하지 못한다. 지문이 center를 지정하면 그대로 따른다.

## 4. 분산분석

### 일원분산분석

```python
df = pd.DataFrame({'g': ['A'] * 5 + ['B'] * 5 + ['C'] * 5,
                   'y': [20, 22, 21, 23, 24, 25, 27, 26, 28, 27, 21, 23, 22, 22, 24]})
groups = [s.dropna() for _, s in df.groupby('g')['y']]   # 결측이 있으면 nan이 나오니 먼저 뺀다
res = stats.f_oneway(*groups)
print(round(res.statistic, 3), round(res.pvalue, 4))

m = smf.ols('y ~ C(g)', data=df).fit()
tab = sm.stats.anova_lm(m)          # 칼럼: df, sum_sq, mean_sq, F, PR(>F)
print(tab.loc['C(g)', ['F', 'PR(>F)']].round(4).tolist())
```

### 이원분산분석

```python
df2 = pd.DataFrame({'A': ['a1', 'a1', 'a2', 'a2'] * 4, 'B': ['b1', 'b2'] * 8,
                    'y': [12, 15, 14, 19, 11, 16, 15, 20, 13, 14, 14, 18, 12, 15, 16, 21]})
m = smf.ols('y ~ C(A) * C(B)', data=df2).fit()     # *는 두 주효과 + 상호작용
tab = sm.stats.anova_lm(m, typ=2)                  # 기본 typ=1. 지문이 정하면 따른다
print(round(tab.loc['C(A):C(B)', 'PR(>F)'], 4))     # 상호작용 행 이름
```

### 사후검정 Tukey HSD

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
t = pairwise_tukeyhsd(df['y'], df['g'], alpha=0.05)
print(t)                                  # group1 group2 meandiff p-adj lower upper reject
print(t.meandiffs.round(3).tolist(), t.reject.tolist())   # 순서: (A,B) (A,C) (B,C)
```

## 5. 카이제곱

### 적합도 검정

```python
obs = [48, 35, 17]                    # 관측 도수
ratio = [0.5, 0.3, 0.2]               # 기대 비율
exp = [r * sum(obs) for r in ratio]   # 기대 도수 = 비율 × 전체 (합이 관측과 같아야 한다)
res = stats.chisquare(obs, f_exp=exp) # 자유도 = 범주 수 − 1
print(round(res.statistic, 3), round(res.pvalue, 4))
```

`f_exp`에 비율을 그대로 넣으면 합이 달라 오류가 난다. 관측 도수를 `value_counts()`로 만들면 기대 비율과 범주 순서를 `reindex`로 맞춘다.

### 독립성 검정

```python
df3 = pd.DataFrame({'channel': ['문자'] * 60 + ['앱'] * 50,
                    'revisit': ['Y'] * 35 + ['N'] * 25 + ['Y'] * 20 + ['N'] * 30})
tab = pd.crosstab(df3['channel'], df3['revisit'])
chi2, p, dof, expected = stats.chi2_contingency(tab)                    # 2×2면 Yates 보정이 기본으로 켜진다
chi2_n, p_n, _, _ = stats.chi2_contingency(tab, correction=False)       # 「연속성 보정을 하지 않는다」
print(round(chi2, 3), round(p, 4), dof, round(chi2_n, 3), round(p_n, 4))
print(np.round(expected, 2).tolist())   # 기대 도수 = 행합 × 열합 / 전체
```

보정은 자유도가 1인 표(2×2)에만 걸린다. 3×3 같은 표는 `correction`과 상관없이 같다.

## 6. 비모수 검정

```python
a = [3.1, 2.8, 3.6, 3.3, 2.9, 3.4]
b = [2.6, 2.7, 2.4, 3.0, 2.5, 2.2]
print(stats.mannwhitneyu(a, b, alternative='greater').pvalue)   # 두 독립 집단, U는 첫 인자 기준
before = [7, 5, 8, 6, 9, 7, 6, 8]
after  = [6, 4, 8, 5, 7, 6, 4, 7]
print(stats.wilcoxon(after, before).pvalue)    # 대응, 차이가 0인 쌍은 기본으로 버린다
print(stats.kruskal([1, 3, 2, 4], [5, 6, 7, 5], [2, 3, 3, 4]).pvalue)   # 세 집단 이상
```

## 7. 상관분석

```python
x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2.1, 2.9, 3.2, 4.8, 5.1, 5.9, 7.2, 7.8]
r = stats.pearsonr(x, y)                  # 선형 상관, 귀무가설: 상관계수 = 0
s = stats.spearmanr(x, y)                 # 순위 상관 (단조 관계, 이상값에 덜 민감)
print(round(r.statistic, 4), round(r.pvalue, 4), round(s.statistic, 4))
```

데이터프레임 전체 상관행렬은 `df.corr(method='pearson')`이지만 p값은 주지 않는다. p값이 필요하면 `stats.pearsonr`.

## 8. 선형회귀 (OLS)

```python
rng = np.random.default_rng(0)
d = pd.DataFrame({'x1': rng.normal(10, 2, 60), 'x2': rng.normal(5, 1, 60),
                  'area': rng.choice(['주거지', '대학가', '오피스'], 60)})
d['y'] = 3 + 2 * d['x1'] - 1.5 * d['x2'] + rng.normal(0, 2, 60)
m = smf.ols('y ~ x1 + x2', data=d).fit()      # 절편이 자동으로 들어간다
print(m.params.round(3).to_dict())             # 계수 (Intercept, x1, x2)
print(m.pvalues.round(4).to_dict())            # 계수별 p값 (t검정)
print(round(m.rsquared, 3), round(m.rsquared_adj, 3), round(m.f_pvalue, 4))
print((m.pvalues.drop('Intercept') < 0.05).sum())   # 유의한 변수 수 (절편 제외)
new = pd.DataFrame({'x1': [11], 'x2': [4.5]})
print(round(m.predict(new).iloc[0], 2))        # 새 관측치 예측 (DataFrame으로 넣는다)
```

| 원하는 값 | 속성 |
|---|---|
| 계수 · p값 · 표준오차 · t값 | `params` · `pvalues` · `bse` · `tvalues` |
| 계수 신뢰구간 | `conf_int(alpha=0.05)` |
| 결정계수 · 수정 결정계수 | `rsquared` · `rsquared_adj` |
| 모형 F 통계량 · p값 | `fvalue` · `f_pvalue` |
| AIC · BIC · 로그우도 | `aic` · `bic` · `llf` |
| 잔차 · 적합값 · 관측 수 | `resid` · `fittedvalues` · `nobs` |

- 범주형은 `C(area)`. 기준 범주를 정하려면 `C(area, Treatment(reference='주거지'))`. 문자열 칼럼은 `C()` 없이도 범주형이고 기본 기준은 정렬했을 때 첫 값이다.
- 변환은 식 안에서: `np.log(x1)`, 제곱은 `I(x1 ** 2)`, 상호작용은 `x1:x2`(곱만) 또는 `x1 * x2`(주효과 + 곱).
- train/test 지시가 있으면 train으로만 적합하고 `m.predict(test)`로 test RMSE: `np.sqrt(((test['y'] - pred) ** 2).mean())`.
- 「유의한 변수만으로 다시 적합」은 식을 새로 써서 `fit()`을 한 번 더.

## 9. 로지스틱 회귀

```python
rng = np.random.default_rng(1)
c = pd.DataFrame({'visits': rng.normal(3, 1, 200), 'fee': rng.normal(8, 2, 200)})
p_true = 1 / (1 + np.exp(-(1.5 - 0.9 * c['visits'] + 0.1 * c['fee'])))
c['churn'] = (rng.random(200) < p_true).astype(int)
m = smf.logit('churn ~ visits + fee', data=c).fit(disp=0)   # disp=0: 반복 로그 숨김
b = m.params['visits']
print(round(np.exp(b), 3))           # 오즈비: visits가 1 늘 때 오즈가 몇 배
print(round(np.exp(5 * b), 3))       # 5 늘 때는 exp(5 × b) (오즈비 × 5가 아니다)
print(round(m.pvalues['visits'], 4))
prob = m.predict(c)                  # 확률이 나온다 (0/1이 아니다)
pred = (prob >= 0.5).astype(int)     # 분류 기준은 지문대로 (이상/초과)
print(round((pred != c['churn']).mean(), 3))           # 오류율 = 1 − 정확도
tp = ((pred == 1) & (c['churn'] == 1)).sum()
print(round(tp / (c['churn'] == 1).sum(), 3))          # 민감도 = TP / (TP + FN)
print(round(-2 * m.llf, 2), round(-2 * m.llnull, 2))   # 잔차 이탈도 · 영 이탈도
```

| 원하는 값 | 꺼내는 법 |
|---|---|
| 오즈비 · 오즈비 신뢰구간 | `np.exp(m.params)` · `np.exp(m.conf_int())` |
| 잔차 이탈도 | `-2 * m.llf` (logit 결과에는 `deviance`가 없다) |
| 영 이탈도 | `-2 * m.llnull` |
| McFadden 의사 R² | `m.prsquared` |
| AIC · BIC | `m.aic` · `m.bic` |

- GLM으로 적합하면 이탈도가 바로 나온다: `smf.glm('churn ~ visits + fee', data=c, family=sm.families.Binomial()).fit()` 뒤 `.deviance`, `.null_deviance`.
- scikit-learn `LogisticRegression`은 기본으로 L2 규제(`C=1.0`)가 걸려 계수가 다르고 p값도 없다. 계수·p값·오즈비를 묻으면 statsmodels.
- 특이도 = TN / (TN + FP), 정밀도 = TP / (TP + FP). 민감도(재현율)와 헷갈리지 않는다.

## 10. 시험장 체크리스트

- 유의수준, 단측·양측, 등분산 가정, 연속성 보정, 절편 포함, 기준 범주를 지문에서 먼저 확인한다.
- 단측이면 `alternative`를 넣고, 방향은 첫 인자 기준인지 다시 본다.
- 결측치가 있으면 검정 함수가 nan을 돌려준다. 지문이 말한 처리(제거)를 먼저 한다.
- 범주형 칼럼이 숫자로 들어 있으면(1, 2, 3) 회귀식에서 `C()`로 감싼다.
- 회귀 결과에서 「유의한 변수 수」는 절편을 빼고 센다.
- 반올림 자릿수와 판정 단어(기각/채택)를 제출 형식에 맞춘다.
