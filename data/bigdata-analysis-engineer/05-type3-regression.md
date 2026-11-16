# 작업형 3 · 회귀분석

> 숫자는 시험 체험환경(제12회 기준) 버전인 pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1에서 실행해 확인한 출력이다. 답으로 내는 값은 summary() 표를 눈으로 읽지 말고 속성으로 꺼내 반올림한다.

## formula API와 array API

- **smf.ols (statsmodels.formula.api.ols)** — `'y ~ x1 + x2'` 같은 수식 문자열과 DataFrame으로 선형회귀를 지정한다. 절편이 자동으로 들어가고 문자열 열은 자동으로 범주형 처리된다
- **sm.OLS (statsmodels.api.OLS)** — 종속변수 배열과 설명변수 행렬을 직접 넘기는 방식. 절편 열을 넣어 주지 않으면 원점을 지나는 회귀가 된다
- **add_constant (sm.add_constant)** — 설명변수 행렬 맨 앞에 값이 모두 1인 `const` 열을 붙여 절편을 추정하게 만드는 함수
- Q: `sm.OLS`에 넘기는 인자 순서는? — `sm.OLS(y, X)` (종속변수가 먼저)
  - sklearn은 `fit(X, y)`로 순서가 반대다.
- Q: formula에서 절편을 빼려면? — `'y ~ x - 1'` 또는 `'y ~ x + 0'`
- Q: `smf.ols('y ~ x', data=df)`만 하고 `.params`를 읽으면? — 오류. `.fit()`을 불러야 결과 객체가 나온다
  - `smf.ols(...)`는 모델 지정만 한 객체이고, 계수·p값은 `fit()`이 돌려준 결과에 있다.

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
  - `add_constant`를 빠뜨리면 기울기 하나만 나오고 그 값도 달라진다. 붙이면 절편 이름은 `const`(formula API는 `Intercept`)다.

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
  - 절편이 없으면 statsmodels는 평균을 빼지 않은(uncentered) R²를 계산해 값이 부풀려진다.

- Q: 빈칸을 채우면? (로지스틱 회귀를 GLM으로)
  ```text
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  m = smf.glm('y ~ x', data=df, family=①).fit()
  ```
  - 답: ① `sm.families.Binomial()`
  - 기본 family는 Gaussian이라 빼면 그냥 선형회귀가 된다.

## 결과 속성 읽기

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
  - 절편 p값이 0.05보다 크므로 절편은 유의하지 않다. 행 이름으로 꺼내면 행을 잘못 읽을 일이 없다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(round(m.rsquared, 4), round(m.rsquared_adj, 4))
  ```
  - 답: `0.9982 0.9978`

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  print(round(m.bse['x'], 4), round(m.tvalues['x'], 3))
  print(round(m.params['x'] / m.bse['x'], 3))
  ```
  - 답:
    ```text
    0.0428 47.238
    47.238
    ```
  - t값은 계수를 표준오차(`bse`)로 나눈 값이다.

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
  - 행이 변수, 열 0·1이 하한·상한이다. 신뢰수준을 낮추면 구간이 좁아진다.

- Q: `conf_int()`의 기본 신뢰수준은? — 95% (`alpha=0.05`)
  - 90% 구간은 `conf_int(alpha=0.1)`. 인자는 신뢰수준이 아니라 유의수준이다.

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
  - AIC = -2·llf + 2k. k는 절편을 포함한 추정 계수 수(여기선 2)다. AIC·BIC는 작을수록 좋다.

- **수정 결정계수 (adjusted R²)** — 1 - (1 - R²)(n - 1)/(n - p - 1). 설명변수 수 p가 늘어난 만큼 벌점을 줘서, 쓸모없는 변수를 넣으면 오히려 줄어들 수 있다
- Q: `summary()`와 `.params`·`.pvalues` 중 답을 꺼낼 때 쓰는 것은? — 속성(`.params` 등)
  - summary()는 표시용 문자열이라 이미 반올림된 값이 찍힌다. 문제에서 정한 자릿수로 직접 반올림하려면 속성을 쓴다.
- Q: OLS summary 표에서 계수별 p값이 있는 열 이름은? — `P>|t|`
  - 로지스틱(Logit)·GLM 표는 z검정이라 `P>|z|`다.
- Q: summary 위쪽의 `Prob (F-statistic)`은 어느 속성인가? — `f_pvalue`
  - 계수 하나의 p값이 아니라 모형 전체 F검정의 p값이다.

## 범주형 변수

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
  - 절편은 기준 범주 A의 평균, `C(g)[T.B]`는 B 평균 - A 평균이다.

- Q: `C()`로 만든 더미의 기준 범주는 기본으로 무엇인가? — 정렬했을 때 첫 수준
  - 데이터에 처음 나온 값이 아니다. 문자열이면 사전순 첫 값이 계수표에서 빠진다.

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
  m = smf.ols("y ~ C(g, ①(reference='C'))", data=df).fit()
  ```
  - 답: ① `Treatment`
  - 계수 이름이 `C(g, Treatment(reference='C'))[T.A]`처럼 길어진다. 행은 `m.params.index`로 확인하고 꺼낸다.

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
  - 숫자로 코딩된 범주(1·2·3)는 `C()`를 씌우지 않으면 연속형 하나로 들어간다.

## 예측

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  new = pd.DataFrame({'x': [10, 0]})
  print(m.predict(new).round(2).tolist())
  ```
  - 답: `[20.18, -0.02]`
  - formula 결과에는 학습 때와 같은 열 이름의 DataFrame을 넣는다. 절편 열은 넣지 않는다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  new = pd.DataFrame({'x': [10]})
  print(sm.add_constant(new).shape)
  print(sm.add_constant(new, has_constant='add').shape)
  ```
  - 답:
    ```text
    (1, 1)
    (1, 2)
    ```
  - 한 행짜리는 모든 열이 상수로 보여 기본값 `has_constant='skip'`이 절편을 안 붙인다. array API로 한 행을 예측할 때 `predict`가 모양 오류를 낸다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = smf.ols('y ~ x1 + x2', data=df).fit()
  new = pd.DataFrame({'x1': [10], 'x2': [3]})
  print(round(m.predict(new)[0], 2))
  ```
  - 답: `19.32`
  - 손으로 검산: 절편 + 계수·값의 합. `m.params`로 직접 곱해도 같다.

## 다중 회귀와 유의성

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
  - "유의한 변수"를 물을 때 절편 행을 빼는 것을 잊지 않는다. 여기서 절편 p값(0.0116)도 0.05보다 작다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x1': [2, 4, 3, 6, 5, 8, 7, 9],
                     'x2': [1, 3, 2, 2, 4, 3, 5, 4],
                     'y': [5, 9, 8, 12, 11, 16, 14, 18]})
  m = smf.ols('y ~ x1 + x2', data=df).fit()
  print(m.params.round(4).tolist())
  print(round(m.fvalue, 3), m.f_pvalue < 0.05)
  ```
  - 답:
    ```text
    [1.8831, 1.7097, 0.1129]
    276.125 True
    ```
  - 순서는 Intercept, x1, x2. 리스트로 꺼내면 행 이름이 사라지니 순서를 확인한다.

- Q: 다중회귀 모형의 F검정에서 귀무가설은? — 절편을 뺀 모든 회귀계수가 0이다
- Q: 다중회귀에서 x2의 p값이 0.573이면 결론은? — 유의수준 0.05에서 x2의 계수가 0이라는 귀무가설을 기각하지 못한다
- Q: formula 안에서 x의 제곱항을 넣으려면? — `I(x ** 2)`
  - `I()` 없이 `x ** 2`를 쓰면 수식 문법의 연산으로 해석돼 제곱항이 들어가지 않는다.
- Q: formula `y ~ x1 * x2`가 펼쳐지는 항은? — `x1 + x2 + x1:x2`
  - `:`는 교호작용 항 하나만 넣는다.
- Q: formula에서 y에 로그를 씌워 적합하려면? — `smf.ols('np.log(y) ~ x', data=df)`
  - 코드에 `import numpy as np`가 있어야 수식 안의 `np`를 찾는다.

## 상관과 회귀

- **상관계수와 회귀의 차이 (correlation vs regression)** — 상관은 두 변수의 선형 관계 강도를 대칭적으로 재고(-1~1), 회귀는 한 변수로 다른 변수를 예측하는 식을 세운다. x와 y를 바꾸면 상관은 같고 기울기는 달라진다
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
  - 단순회귀에서만 R² = r². 다중회귀에서는 성립하지 않는다.

- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  from scipy import stats
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  m = smf.ols('y ~ x', data=df).fit()
  r, p = stats.pearsonr(df['x'], df['y'])
  print(bool(np.isclose(p, m.pvalues['x'])))
  ```
  - 답: `True`
  - 상관계수 검정의 p값과 단순회귀 기울기 t검정의 p값은 같다.

## 로지스틱 회귀

- **오즈비 (odds ratio)** — 설명변수가 1 늘 때 오즈(성공확률/실패확률)가 몇 배가 되는지. 로지스틱 계수에 `np.exp`를 씌워 구한다
- **로그 오즈 (log-odds, logit)** — log(p / (1 - p)). 로지스틱 회귀의 계수는 이 값의 변화량이라 그대로는 확률 변화가 아니다
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(m.params.round(4).tolist())
  print(round(np.exp(m.params['x']), 4))
  ```
  - 답:
    ```text
    [-3.7219, 0.6767]
    1.9674
    ```
  - x가 1 늘면 y=1일 오즈가 약 1.97배가 된다.

- Q: 오즈비가 1.97이면 해석은? — x가 1 증가할 때 y=1의 오즈가 약 1.97배(97% 증가)가 된다
  - 확률이 1.97배가 되는 것이 아니다.
- Q: 출력 결과는?
  ```text
  import numpy as np
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(np.exp(3 * m.params['x']), 2))
  ```
  - 답: `7.61`
  - x가 3 늘 때의 오즈비는 exp(3 × 계수). 오즈비 1.9674를 3배 하는 것이 아니라 세제곱이다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  p = m.predict(pd.DataFrame({'x': [3, 8]}))
  print(p.round(3).tolist())
  print((p > 0.5).astype(int).tolist())
  ```
  - 답:
    ```text
    [0.156, 0.844]
    [0, 1]
    ```
  - logit의 `predict`는 클래스가 아니라 y=1일 확률을 돌려준다. 분류는 0.5 기준으로 직접 자른다.

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
  - 선형식 값 z를 시그모이드에 넣은 것이 예측 확률이다.

- Q: `smf.logit(...).fit(disp=0)`의 `disp=0`은? — 최적화 반복 메시지를 출력하지 않게 한다
  - 결과값은 바뀌지 않는다. 출력이 섞이는 것만 막는다.
- Q: 학습 데이터의 정분류율을 구할 때 `m.predict()`에 인자를 안 주면? — 학습 데이터 각 행의 예측 확률이 나온다
  - 이것을 0.5로 잘라 `y`와 비교해 평균을 내면 정확도다.

## 이탈도와 적합도

- **잔차 이탈도 (residual deviance)** — 적합한 모형의 -2 × 로그우도(0/1 자료 기준). 작을수록 데이터에 잘 맞는다
- **영 이탈도 (null deviance)** — 절편만 있는 모형의 -2 × 로그우도. 설명변수를 넣어 잔차 쪽이 얼마나 줄었는지 비교하는 기준이 된다
- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(-2 * m.llf, 4), round(-2 * m.llnull, 4))
  ```
  - 답: `8.6702 13.8629`
  - Logit 결과에는 `deviance` 속성이 없다. `llf`(모형)와 `llnull`(절편만)로 계산한다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=sm.families.Binomial()).fit()
  print(round(m.deviance, 4), round(m.null_deviance, 4))
  print(m.params.round(4).tolist())
  ```
  - 답:
    ```text
    8.6702 13.8629
    [-3.7219, 0.6767]
    ```
  - GLM Binomial은 logit과 같은 계수를 주고, 이탈도를 속성으로 바로 준다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(m.prsquared, 4), round(1 - m.llf / m.llnull, 4))
  ```
  - 답: `0.3746 0.3746`
  - Logit의 `prsquared`가 McFadden pseudo R²이고, 1 - 모형 로그우도 / 절편만 로그우도다.

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
  - GLM의 `pseudo_rsquared()` 기본은 Cox-Snell(`kind='cs'`)이다. McFadden을 물으면 `kind='mcf'`.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.logit('y ~ x', data=df).fit(disp=0)
  print(round(m.aic, 4), round(-2 * m.llf + 2 * 2, 4))
  print(round(m.bic, 4))
  ```
  - 답:
    ```text
    12.6702 12.6702
    13.2754
    ```
  - BIC = -2·llf + k·ln(n). 여기선 8.6702 + 2·ln(10).

- Q: 출력 결과는?
  ```text
  import pandas as pd
  import statsmodels.api as sm
  import statsmodels.formula.api as smf
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  m = smf.glm('y ~ x', data=df, family=sm.families.Binomial()).fit()
  print(round(m.bic, 4), round(m.bic_llf, 4))
  ```
  - 답: `-9.7505 13.2754`
  - statsmodels 0.14의 GLM `.bic`는 이탈도 기반 공식이라(경고가 함께 뜬다) 값이 다르다. 로그우도 기반 BIC는 `bic_llf`. AIC는 같다.

- Q: 이탈도로 두 로지스틱 모형(중첩)을 비교하는 검정 통계량은? — 두 모형 잔차 이탈도의 차이
  - 카이제곱 분포를 따르고 자유도는 추가된 계수 수다. 영 이탈도 - 잔차 이탈도는 Logit 결과의 `llr`, 그 p값은 `llr_pvalue`.

## sklearn과의 차이

- Q: sklearn `LogisticRegression()`의 기본 규제는? — `penalty='l2'`, `C=1.0`
  - 규제 때문에 계수가 0 쪽으로 줄어든다. 규제를 끄려면 `penalty=None`.
- Q: 시험에서 로지스틱 회귀의 계수·p값·오즈비를 물으면 쓰는 것은? — statsmodels (`smf.logit` 또는 `smf.glm`)
  - sklearn은 규제가 기본으로 걸려 있고 p값·표준오차를 주지 않는다.
- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.linear_model import LogisticRegression
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     'y': [0, 0, 0, 1, 0, 1, 0, 1, 1, 1]})
  a = LogisticRegression().fit(df[['x']], df['y'])
  b = LogisticRegression(penalty=None).fit(df[['x']], df['y'])
  print(round(a.coef_[0][0], 2), round(b.coef_[0][0], 2))
  ```
  - 답: `0.59 0.68`
  - 규제를 끈 쪽이 statsmodels 계수(0.6767)에 가깝다. 반복 최적화 결과라 소수 넷째 자리는 버전마다 다를 수 있다.

- Q: 출력 결과는?
  ```text
  import pandas as pd
  from sklearn.linear_model import LinearRegression
  df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                     'y': [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]})
  lr = LinearRegression().fit(df[['x']], df['y'])
  print(round(lr.coef_[0], 4), round(lr.intercept_, 4))
  print(round(lr.score(df[['x']], df['y']), 4))
  ```
  - 답:
    ```text
    2.02 -0.02
    0.9982
    ```
  - LinearRegression은 규제가 없어 OLS와 계수가 같고 절편도 자동으로 넣는다. `score`는 R²다.
