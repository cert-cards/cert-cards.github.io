# statsmodels · 회귀·분산분석

> statsmodels 선형회귀(smf.ols, sm.OLS), 로지스틱 회귀(smf.logit, smf.glm), 결과 속성, 범주형 처리, 예측, 분산분석표(anova_lm), 사후검정(pairwise_tukeyhsd)을 다룬다. 코드는 `import statsmodels.api as sm`, `import statsmodels.formula.api as smf` 기준이다.

## smf.ols

- Q: `smf.ols('y ~ x1 + x2', data=df)`의 특징 — 수식 문자열과 DataFrame으로 모형을 지정하고 절편을 자동으로 넣는다
  - 문자열 열은 자동으로 범주형(더미) 처리된다.
- Q: `smf.ols('y ~ x', data=df)`만 하고 `.params`를 읽으면 — 오류. `.fit()`이 돌려준 결과 객체에 계수가 있다
- Q: formula에서 절편을 빼려면 — `'y ~ x - 1'` 또는 `'y ~ x + 0'`
- Q: formula 안에서 x의 제곱항을 넣으려면 — `I(x ** 2)`
  - `I()` 없이 쓰면 수식 문법의 연산으로 해석돼 제곱항이 들어가지 않는다.
- Q: formula `y ~ x1 * x2`가 펼쳐지는 항 — `x1 + x2 + x1:x2`
  - `:`는 상호작용 항 하나만 넣는다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  a = smf.ols('y ~ x + I(x ** 2)', data=df).fit()
  b = smf.ols('np.log(y) ~ x', data=df).fit()
  print(a.params.index.tolist())
  print(b.params.round(4).tolist())
  ```
  - 답:
    ```text
    ['Intercept', 'x', 'I(x ** 2)']
    [0.6111, 0.3395]
    ```
  - 수식 안의 `np`를 찾으려면 코드에 `import numpy as np`가 있어야 한다.

## sm.OLS · sm.add_constant

- Q: `sm.OLS`에 넘기는 인자 순서 — `sm.OLS(y, X)` (종속변수가 먼저)
  - sklearn은 `fit(X, y)`로 반대다.
- Q: `sm.OLS`에서 절편을 추정하게 하려면 — `sm.add_constant(X)`로 값이 모두 1인 `const` 열을 붙인다
  - 빠뜨리면 원점을 지나는 회귀가 된다. formula API는 절편 이름이 `Intercept`다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  a = sm.OLS(df['y'], df['x']).fit()
  b = smf.ols('y ~ x', data=df).fit()
  print(a.params.round(4).tolist())
  print(b.params.round(4).tolist())
  ```
  - 답:
    ```text
    [2.0154]
    [-0.02, 2.02]
    ```
  - 절편 열이 없으면 기울기 하나만 나오고 그 값도 달라진다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  a = sm.OLS(df['y'], df['x']).fit()
  b = sm.OLS(df['y'], sm.add_constant(df['x'])).fit()
  print(round(a.rsquared, 4), round(b.rsquared, 4))
  ```
  - 답: `0.9997 0.9982`
  - 절편이 없으면 평균을 빼지 않은(uncentered) R²를 계산해 값이 부풀려진다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  X = sm.add_constant(df[['x1', 'x2']])
  m = sm.OLS(df['y'], X).fit()
  print(m.params.index.tolist())
  ```
  - 답: `['const', 'x1', 'x2']`

## params · pvalues · bse · tvalues

- Q: 계수, p값, 표준오차, t값을 담은 결과 속성 — `params`, `pvalues`, `bse`, `tvalues`
  - 모두 변수 이름이 인덱스인 Series라 `m.pvalues['x']`처럼 이름으로 꺼낸다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(m.params.index.tolist())
  print(round(m.params['Intercept'], 3), round(m.pvalues['Intercept'], 4))
  ```
  - 답:
    ```text
    ['Intercept', 'x']
    -0.02 0.9102
    ```
  - 절편 p값이 0.05보다 커서 절편은 유의하지 않다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(round(m.bse['x'], 4), round(m.tvalues['x'], 3), round(m.params['x'] / m.bse['x'], 3))
  ```
  - 답: `0.0428 47.238 47.238`
  - t값은 계수를 표준오차로 나눈 값이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = smf.ols('y ~ x1 + x2', data=df).fit()
  p = m.pvalues.drop('Intercept')
  print([k for k, v in p.items() if v < 0.05])
  print(p.idxmax(), round(p.max(), 3))
  ```
  - 답:
    ```text
    ['x1']
    x2 0.573
    ```
  - 「유의한 변수」를 물을 때 절편 행을 뺀다. 이 자료는 절편 p값(0.0116)도 0.05보다 작다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = smf.ols('y ~ x1 + x2', data=df).fit()
  print(m.params.round(4).tolist())
  ```
  - 답: `[1.8831, 1.7097, 0.1129]`
  - 순서는 Intercept, x1, x2. 리스트로 꺼내면 이름이 사라지니 순서를 확인한다.

## conf_int

- Q: `conf_int()`의 기본 신뢰수준 — 95% (`alpha=0.05`)
  - 90% 구간은 `conf_int(alpha=0.1)`. 인자는 신뢰수준이 아니라 유의수준이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(m.conf_int().loc['x'].round(3).tolist())
  print(m.conf_int(alpha=0.1).loc['x'].round(3).tolist())
  ```
  - 답:
    ```text
    [1.901, 2.139]
    [1.929, 2.111]
    ```
  - 행이 변수, 열 0과 1이 하한과 상한이다.

## rsquared · rsquared_adj · 잔차

- Q: 수정 결정계수 식 — 1 − (1 − R²)(n − 1)/(n − p − 1)
  - 설명변수를 늘리면 R²는 줄지 않지만 수정 R²는 줄 수 있다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m1 = smf.ols('y ~ x1', data=df).fit()
  m2 = smf.ols('y ~ x1 + x2', data=df).fit()
  print(round(m1.rsquared, 4), round(m2.rsquared, 4))
  print(round(m1.rsquared_adj, 4), round(m2.rsquared_adj, 4))
  ```
  - 답:
    ```text
    0.9904 0.991
    0.9888 0.9874
    ```
  - 쓸모없는 x2를 넣으니 R²는 조금 오르고 수정 R²는 내려갔다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(m.nobs, m.df_model, m.df_resid)
  print(round(m.ssr, 4), round(m.mse_resid, 4), round(m.ssr / m.df_resid, 4))
  ```
  - 답:
    ```text
    6.0 1.0 4.0
    0.128 0.032 0.032
    ```
  - `ssr`은 잔차제곱합, `mse_resid`는 그것을 잔차 자유도(n − p − 1)로 나눈 값이다. 잔차는 `m.resid`, 적합값은 `m.fittedvalues`.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  r = df['x'].corr(df['y'])
  print(round(r ** 2, 4), round(m.rsquared, 4))
  ```
  - 답: `0.9982 0.9982`
  - 단순회귀에서만 R² = r²이다.

## fvalue · f_pvalue

- Q: 다중회귀 모형 F검정의 귀무가설 — 절편을 뺀 모든 회귀계수가 0이다
- Q: summary 위쪽의 `Prob (F-statistic)`에 해당하는 속성 — `f_pvalue`
  - 계수 하나의 p값이 아니라 모형 전체 F검정의 p값이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(round(m.fvalue, 2), round(m.tvalues['x'] ** 2, 2))
  ```
  - 답: `2231.47 2231.47`
  - 설명변수가 하나면 모형 F값은 기울기 t값의 제곱이고 두 p값도 같다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = smf.ols('y ~ x1 + x2', data=df).fit()
  print(round(m.fvalue, 3), m.f_pvalue < 0.05)
  ```
  - 답: `276.125 True`

## aic · bic · llf

- Q: AIC와 BIC를 로그우도로 쓰면 — AIC = −2·llf + 2k, BIC = −2·llf + k·ln(n) (k는 절편 포함 계수 수)
  - 둘 다 작을수록 좋은 모형이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(round(m.llf, 3), round(m.aic, 3), round(m.bic, 3))
  print(round(-2 * m.llf + 2 * 2, 3))
  ```
  - 답:
    ```text
    3.029 -2.058 -2.474
    -2.058
    ```

## summary와 속성

- Q: `summary()`와 `.params`·`.pvalues` 중 답을 꺼낼 때 쓰는 것 — 속성
  - summary는 이미 반올림된 표시용 표다. 문제의 자릿수로 직접 반올림하려면 속성을 쓴다.
- Q: OLS summary 표에서 계수별 p값 열 이름 — `P>|t|`
  - Logit·GLM 표는 z검정이라 `P>|z|`다.

## C() · Treatment (범주형 변수)

- Q: `C()`로 만든 더미의 기본 기준 범주 — 정렬했을 때 첫 수준
  - 데이터에 처음 나온 값이 아니다. 기준 범주는 계수표에서 빠지고 절편에 흡수된다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'g': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'B', 'C'],
                     'y': [10, 12, 15, 17, 20, 22, 11, 16, 21]})
  m = smf.ols('y ~ C(g)', data=df).fit()
  print(m.params.round(2).to_dict())
  ```
  - 답: `{'Intercept': 11.0, 'C(g)[T.B]': 5.0, 'C(g)[T.C]': 10.0}`
  - 절편은 기준 A의 평균, `C(g)[T.B]`는 B 평균 − A 평균이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'g': ['B', 'B', 'A', 'A', 'C', 'C', 'B', 'A', 'C'],
                     'y': [10, 12, 15, 17, 20, 22, 11, 16, 21]})
  m = smf.ols('y ~ g', data=df).fit()
  print(m.params.index.tolist())
  print(round(m.params['g[T.B]'], 2))
  ```
  - 답:
    ```text
    ['Intercept', 'g[T.B]', 'g[T.C]']
    -5.0
    ```
  - 문자열 열은 `C()` 없이도 범주형이 되고, B가 먼저 나와도 기준은 A다.
- Q: 빈칸을 채우면? (범주 C를 기준으로)
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'g': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'B', 'C'],
                     'y': [10, 12, 15, 17, 20, 22, 11, 16, 21]})
  m = smf.ols("y ~ C(g, ①(reference='C'))", data=df).fit()
  print(m.params.round(2).tolist())
  ```
  - 답: ① `Treatment`
  - 출력은 `[21.0, -10.0, -5.0]`. 절편이 C의 평균이 되고 계수 이름이 `C(g, Treatment(reference='C'))[T.A]`처럼 길어진다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'g': [1, 1, 2, 2, 3, 3, 1, 2, 3],
                     'y': [10, 12, 15, 17, 20, 22, 11, 16, 21]})
  a = smf.ols('y ~ g', data=df).fit()
  b = smf.ols('y ~ C(g)', data=df).fit()
  print(len(a.params), len(b.params))
  ```
  - 답: `2 3`
  - 숫자로 코딩된 범주는 `C()`를 씌우지 않으면 연속형 하나로 들어간다.

## predict

- Q: formula로 적합한 결과의 `predict`에 넣는 것 — 학습 때와 같은 열 이름을 가진 DataFrame
  - 절편 열은 넣지 않는다. 인자 없이 부르면 학습 데이터의 적합값을 준다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(m.predict(pd.DataFrame({'x': [10, 0]})).round(2).tolist())
  ```
  - 답: `[20.18, -0.02]`
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = sm.OLS(df['y'], sm.add_constant(df[['x1', 'x2']])).fit()
  new = pd.DataFrame({'x1': [10, 4], 'x2': [3, 2]})
  print(m.predict(sm.add_constant(new)).round(2).tolist())
  ```
  - 답: `[19.32, 8.95]`
  - array API는 새 자료에도 `add_constant`를 똑같이 붙여 열 수를 맞춘다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  new = pd.DataFrame({'x': [10]})
  print(sm.add_constant(new).shape, sm.add_constant(new, has_constant='add').shape)
  ```
  - 답: `(1, 1) (1, 2)`
  - 한 행짜리는 모든 열이 상수로 보여 기본값 `has_constant='skip'`이 절편을 붙이지 않는다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  f = m.get_prediction(pd.DataFrame({'x': [10]})).summary_frame(alpha=0.05)
  print(f[['mean_ci_lower', 'mean_ci_upper']].round(2).values.tolist())
  ```
  - 답: `[[19.38, 20.98]]`
  - 평균 반응의 신뢰구간은 `mean_ci_*`, 개별 관측값의 예측구간은 더 넓은 `obs_ci_*` 열이다.

## smf.logit

- Q: `smf.logit(...).fit(disp=0)`의 `disp=0` — 최적화 반복 메시지를 출력하지 않게 한다
  - 결과값은 바뀌지 않는다.
- Q: 로지스틱 회귀 계수의 단위 — 로그 오즈 log(p / (1 − p))의 변화량
  - 확률 변화가 아니다. 오즈비로 해석하려면 `np.exp`를 씌운다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(m.params.round(4).tolist(), round(m.pvalues['x'], 4))
  ```
  - 답: `[-3.7219, 0.6767] 0.089`
  - 유의수준 0.05에서 x의 계수는 유의하지 않다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  p = m.predict(pd.DataFrame({'x': [3, 8]}))
  print(p.round(3).tolist(), (p > 0.5).astype(int).tolist())
  ```
  - 답: `[0.156, 0.844] [0, 1]`
  - logit의 `predict`는 클래스가 아니라 y = 1일 확률을 준다. 분류는 0.5 기준으로 직접 자른다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  b0, b1 = m.params
  z = b0 + b1 * 8
  print(round(1 / (1 + np.exp(-z)), 3))
  ```
  - 답: `0.844`
  - 선형식 값을 시그모이드에 넣은 것이 예측 확률이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  acc = ((m.predict() > 0.5).astype(int) == df['y']).mean()
  print(m.pred_table().tolist(), acc)
  ```
  - 답: `[[4.0, 1.0], [1.0, 4.0]] 0.8`
  - `pred_table()`은 0.5 기준 혼동행렬(행이 실제, 열이 예측)이다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(-2 * m.llf, 4), round(-2 * m.llnull, 4))
  print(round(m.llr, 4), round(m.llr_pvalue, 4), round(m.prsquared, 4))
  ```
  - 답:
    ```text
    8.6702 13.8629
    5.1927 0.0227 0.3746
    ```
  - Logit 결과에는 `deviance` 속성이 없어 −2·llf(잔차 이탈도)와 −2·llnull(영 이탈도)로 계산한다. `llr`은 둘의 차이, `prsquared`는 McFadden R²(1 − llf/llnull)다.

## 오즈비 (np.exp)

- Q: 로지스틱 계수로 오즈비를 구하는 코드 — `np.exp(m.params['x'])`
  - 신뢰구간도 `np.exp(m.conf_int())`로 같이 변환한다.
- Q: 오즈비가 1.97이면 해석 — x가 1 증가할 때 y = 1의 오즈가 약 1.97배(97% 증가)가 된다
  - 확률이 1.97배가 되는 것이 아니다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(np.exp(m.params['x']), 4), round(np.exp(3 * m.params['x']), 2))
  ```
  - 답: `1.9674 7.61`
  - x가 3 늘 때의 오즈비는 exp(3 × 계수)로, 1.9674의 세제곱이다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(np.exp(m.conf_int().loc['x']).round(3).tolist())
  ```
  - 답: `[0.902, 4.291]`
  - 오즈비 구간이 1을 포함하므로 유의하지 않다는 p값(0.089)과 맞는다.

## smf.glm (family=Binomial)

- Q: 빈칸을 채우면? (로지스틱 회귀를 GLM으로)
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=①).fit()
  print(m.params.round(4).tolist())
  ```
  - 답: ① `sm.families.Binomial()`
  - 출력은 `[-3.7219, 0.6767]`로 logit과 같다. family를 빼면 기본 Gaussian이라 선형회귀가 된다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=sm.families.Binomial()).fit()
  print(round(m.deviance, 4), round(m.null_deviance, 4))
  ```
  - 답: `8.6702 13.8629`
  - GLM은 잔차 이탈도와 영 이탈도를 속성으로 바로 준다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=sm.families.Binomial()).fit()
  print(round(m.pseudo_rsquared(), 4), round(m.pseudo_rsquared(kind='mcf'), 4))
  ```
  - 답: `0.405 0.3746`
  - GLM `pseudo_rsquared()`의 기본은 Cox-Snell(`kind='cs'`)이다. McFadden은 `kind='mcf'`.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=sm.families.Binomial()).fit()
  print(round(m.aic, 4), round(m.bic, 4), round(m.bic_llf, 4))
  ```
  - 답: `12.6702 -9.7505 13.2754`
  - GLM `.bic`는 이탈도 기반 공식이라(경고가 함께 뜬다) 값이 다르다. 로그우도 기반 BIC는 `bic_llf`이고 logit의 `bic`와 같다.
- Q: 시험에서 로지스틱 회귀의 계수·p값·오즈비를 물을 때 쓰는 라이브러리 — statsmodels (`smf.logit` 또는 `smf.glm`)
  - sklearn `LogisticRegression`은 기본으로 L2 규제가 걸려 계수가 다르고 p값을 주지 않는다.

## sm.stats.anova_lm

- Q: `sm.stats.anova_lm`의 `typ` 기본값 — `1` (Type I, 순차 제곱합)
  - 불균형 설계에서는 항 순서에 따라 결과가 바뀐다. 문제가 지정하면 `typ=2`나 `typ=3`을 넣는다.
- Q: anova_lm 표에서 p값이 든 열 이름 — `PR(>F)`
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
  - 같은 자료의 `stats.f_oneway`와 F가 같다.
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
  print(round(table.loc['C(A):C(B)', 'F'], 2), round(table.loc['C(A):C(B)', 'PR(>F)'], 4))
  ```
  - 답:
    ```text
    ['C(A)', 'C(B)', 'C(A):C(B)', 'Residual']
    9.0 0.0399
    ```
  - `*`는 주효과 둘과 상호작용을 모두 넣는다. 상호작용이 유의하면 A의 효과가 B 수준에 따라 다르다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'A': ['x', 'x', 'x', 'y', 'y', 'y', 'y', 'y'],
                     'B': ['p', 'q', 'q', 'p', 'p', 'q', 'p', 'q'],
                     'y': [10, 15, 17, 11, 13, 22, 12, 24]})
  m = smf.ols('y ~ C(A) + C(B)', data=df).fit()
  f1 = sm.stats.anova_lm(m).loc['C(A)', 'F']
  f2 = sm.stats.anova_lm(m, typ=2).loc['C(A)', 'F']
  print(round(f1, 3), round(f2, 3))
  ```
  - 답: `3.231 12.35`
  - 불균형 자료에서 Type I은 먼저 들어간 A에 B와 겹치는 몫까지 준다. Type II는 B를 통제한 A의 효과다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m1 = smf.ols('y ~ x1', data=df).fit()
  m2 = smf.ols('y ~ x1 + x2', data=df).fit()
  t = sm.stats.anova_lm(m1, m2)
  print(t['df_diff'].tolist()[1], round(t['Pr(>F)'][1], 3))
  ```
  - 답: `1.0 0.573`
  - 모형 두 개를 넣으면 중첩 모형 비교(부분 F검정)를 한다. 추가한 항이 하나면 그 계수의 t검정 p값과 같다.

## pairwise_tukeyhsd

- Q: 분산분석에서 H0가 기각된 뒤 어느 집단 쌍이 다른지 찾는 함수 — `pairwise_tukeyhsd(endog, groups, alpha=0.05)`
  - `from statsmodels.stats.multicomp import pairwise_tukeyhsd`. 집단이 k개면 k(k − 1)/2쌍을 비교한다.
- Q: 출력 결과는?
  ```text
  from statsmodels.stats.multicomp import pairwise_tukeyhsd
  y = [23, 25, 21, 24, 22, 28, 27, 30, 26, 29, 24, 26, 23, 25, 27]
  g = ['a'] * 5 + ['b'] * 5 + ['c'] * 5
  res = pairwise_tukeyhsd(endog=y, groups=g, alpha=0.05)
  print(res.reject.tolist())
  print(res.meandiffs.round(2).tolist(), res.pvalues.round(4).tolist())
  ```
  - 답:
    ```text
    [True, False, True]
    [5.0, 2.0, -3.0] [0.0008, 0.1546, 0.0277]
    ```
  - 쌍 순서는 (a, b), (a, c), (b, c)이고 `meandiff`는 group2 평균 − group1 평균이다. 표로 보려면 `print(res.summary())`.
