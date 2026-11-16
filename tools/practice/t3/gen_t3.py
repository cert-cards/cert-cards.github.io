"""작업형3 실습 문제 10개 생성기. 시험 버전 파이썬(examenv)으로 실행한다.

각 문제: gen(rng) -> DataFrame, solution 코드(a1,a2,a3 계산 후 print), 조건 검사.
시드를 0부터 올려 조건(반올림 경계 회피, 판정 여유 등)을 만족하는 첫 데이터를 쓴다.
"""
import contextlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))
OUT_JSON = os.path.join(REPO, "parts", "t3.json")

F3 = "반올림하여 소수 셋째 자리까지"
F2 = "반올림하여 소수 둘째 자리까지"
F4 = "반올림하여 소수 넷째 자리까지"
FI = "정수"
FD = "기각 또는 채택"
DIG = {F2: 2, F3: 3, F4: 4}


def margin_ok(x, d, m=0.05):
    """x*10^d 의 소수 부분이 0.5에서 m 이상 떨어져 있나 (반올림 경계 회피)."""
    v = abs(float(x)) * 10 ** d
    frac = v - math.floor(v)
    return abs(frac - 0.5) > m


def fmt(x, f):
    if f in DIG:
        d = DIG[f]
        return f"{round(float(x), d):.{d}f}"
    if f == FI:
        return str(int(x))
    return str(x)


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


P = []

# ---------------------------------------------------------------- m1-3-1 OLS
def gen_m1_1(rng):
    n = 150
    seats = rng.integers(20, 81, n)
    staff = rng.integers(2, 11, n)
    parking = rng.integers(0, 2, n)
    dist = rng.integers(50, 1501, n)
    rating = np.round(rng.uniform(3.0, 5.0, n), 1)
    age = rng.integers(1, 21, n)
    sales = 8 + 0.22 * seats + 1.6 * staff + 2.5 * parking - 0.0045 * dist + 0.6 * rating + rng.normal(0, 4.5, n)
    return pd.DataFrame({
        "store_id": [f"S{i:03d}" for i in range(1, n + 1)],
        "seats": seats, "staff": staff, "parking": parking, "station_dist": dist,
        "rating": rating, "age_years": age, "sales": np.round(sales, 1),
    })


def chk_m1_1(ns, df):
    import statsmodels.formula.api as smf
    m = smf.ols("sales ~ seats + staff + parking + station_dist + rating + age_years", data=df).fit()
    pv = m.pvalues.drop("Intercept")
    if any(0.02 < p < 0.1 for p in pv):
        return False
    return 0.1 < ns["a2"] < 0.9


P.append(dict(
    id="m1-3-1", set="m1", no="3-1", file="t3_1.csv", gen=gen_m1_1, chk=chk_m1_1,
    title="음식점 월매출 다중선형회귀 — 계수, p-value, 유의 변수 수",
    statement="""어느 외식 프랜차이즈 본사가 가맹 음식점 150곳의 월매출과 매장 특성을 조사했다. 데이터 `t3_1.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| store_id | 매장 ID |
| seats | 좌석 수 |
| staff | 직원 수(명) |
| parking | 전용 주차장 유무 (1 있음, 0 없음) |
| station_dist | 가장 가까운 지하철역까지 거리(m) |
| rating | 배달앱 평균 평점 |
| age_years | 운영 연수(년) |
| sales | 월매출(백만 원) |

sales를 종속변수로, seats, staff, parking, station_dist, rating, age_years 6개를 독립변수로 하는 다중선형회귀 모형을 전체 데이터로 적합하시오.

- 절편을 포함한다.
- statsmodels formula API(`smf.ols`)를 사용한다. 독립변수는 원래 값 그대로 쓰고 변환하지 않는다.
- p-value는 statsmodels가 출력하는 양측 검정 값을 쓰고, 유의수준은 0.05이다.

① staff의 회귀계수를 구하시오.

② rating의 p-value를 구하시오.

③ 유의수준 0.05에서 유의한 독립변수의 개수를 구하시오. (절편은 세지 않는다)

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 정수""",
    formats=[F3, F3, FI],
    solution="""import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv('data/t3_1.csv')
model = smf.ols('sales ~ seats + staff + parking + station_dist + rating + age_years', data=df).fit()

a1 = model.params['staff']
a2 = model.pvalues['rating']
a3 = (model.pvalues.drop('Intercept') < 0.05).sum()

print(round(a1, 3))
print(round(a2, 3))
print(int(a3))
""",
    explain="""`model.summary()`의 coef 열이 ①, P>|t| 열이 ②다. ③은 `model.pvalues`에서 Intercept를 빼고 0.05 미만인 것을 센다. 절편까지 세면 하나가 늘어나는 것이 흔한 실수다.
store_id는 식별자라 모형에 넣지 않는다. statsmodels 회귀계수의 p-value는 양측 t검정 값이다.""",
))


# ---------------------------------------------------------------- m1-3-2 F, 합동분산, 독립 t
def gen_m1_2(rng):
    na, nb = 52, 40
    la = rng.normal(3.40, 0.38, na)
    lb = rng.normal(3.24, 0.27, nb)
    hub = np.array(["A"] * na + ["B"] * nb)
    mins = np.round(np.exp(np.concatenate([la, lb])), 1)
    idx = rng.permutation(na + nb)
    return pd.DataFrame({
        "parcel_id": [f"P{i:04d}" for i in range(1, na + nb + 1)],
        "hub": hub[idx], "minutes": mins[idx],
    })


def chk_m1_2(ns, df):
    la = np.log(df.loc[df.hub == "A", "minutes"])
    lb = np.log(df.loc[df.hub == "B", "minutes"])
    if not la.var(ddof=1) > 1.3 * lb.var(ddof=1):
        return False
    p_lib = stats.ttest_ind(la, lb, equal_var=True).pvalue
    if abs(p_lib - ns["a3"]) > 1e-12:
        return False
    return 0.005 < ns["a3"] < 0.04


P.append(dict(
    id="m1-3-2", set="m1", no="3-2", file="t3_2.csv", gen=gen_m1_2, chk=chk_m1_2,
    title="두 허브 처리시간 — 로그 변환 후 F 통계량, 합동분산, 독립표본 t검정",
    statement="""택배회사가 두 분류 허브(A, B)에서 소포 한 건을 처리하는 데 걸린 시간을 표본 조사했다. 데이터 `t3_2.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| parcel_id | 소포 ID |
| hub | 허브 (A 또는 B) |
| minutes | 처리 시간(분) |

처리 시간은 오른쪽으로 긴 꼬리를 가지므로 minutes에 자연로그(`np.log`)를 취한 값으로 아래를 계산하시오. 두 허브의 로그 처리 시간은 각각 정규분포를 따르고 서로 독립이라고 가정한다.

- 표본분산은 n−1로 나눈 불편분산(ddof=1)이다.
- F 통계량은 (두 표본분산 중 큰 값) / (작은 값)으로 정의한다. 이 데이터에서는 분자 쪽 집단의 표본 크기가 더 크므로 분자 자유도가 분모 자유도보다 크다.
- 합동분산은 ((n1−1)·s1² + (n2−1)·s2²) / (n1+n2−2)이다.
- 공식으로 직접 계산해도 되고 scipy.stats를 써도 된다. 유의수준은 0.05이다.

① F 통계량을 구하시오.

② 합동분산 추정량을 구하시오.

③ 등분산을 가정하고 ②의 합동분산을 이용한 독립표본 t검정을 수행할 때, 두 허브의 로그 처리 시간 평균이 같다는 귀무가설에 대한 양측 검정 p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F4, F4],
    solution="""import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('data/t3_2.csv')
df['log_min'] = np.log(df['minutes'])
a = df.loc[df['hub'] == 'A', 'log_min']
b = df.loc[df['hub'] == 'B', 'log_min']

va, vb = a.var(ddof=1), b.var(ddof=1)
n1, n2 = len(a), len(b)

a1 = max(va, vb) / min(va, vb)
a2 = ((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)
t = (a.mean() - b.mean()) / np.sqrt(a2 * (1 / n1 + 1 / n2))
a3 = 2 * stats.t.sf(abs(t), n1 + n2 - 2)
# stats.ttest_ind(a, b, equal_var=True).pvalue 와 같다

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 4))
""",
    explain="""로그를 먼저 취하고 모든 계산을 로그 값으로 한다. 원래 분 단위로 계산하면 세 답이 모두 달라진다.
pandas `.var()`는 기본이 ddof=1이지만 `np.var`는 ddof=0이라 섞어 쓰면 틀린다. 분산이 큰 쪽은 A 허브(52건)라 F의 자유도는 (51, 39)다.
t = (평균 차) / sqrt(합동분산 × (1/n1 + 1/n2)), 자유도 n1+n2−2로 양측 p-value를 낸다. `ttest_ind(..., equal_var=True)`가 같은 값을 준다.""",
))


# ---------------------------------------------------------------- m2-3-1 logit
def gen_m2_1(rng):
    n = 320
    hours = np.round(rng.uniform(0.5, 15, n), 1)
    quiz = rng.integers(30, 101, n)
    age = rng.integers(19, 59, n)
    mobile = (rng.random(n) < 0.45).astype(int)
    eta = -5.2 + 0.22 * hours + 0.05 * quiz - 0.015 * age - 0.7 * mobile
    y = (rng.random(n) < sigmoid(eta)).astype(int)
    return pd.DataFrame({
        "learner_id": [f"L{i:04d}" for i in range(1, n + 1)],
        "study_hours": hours, "quiz_avg": quiz, "age": age, "mobile": mobile, "completed": y,
    })


def chk_m2_1(ns, df):
    return 0.25 < df.completed.mean() < 0.75 and ns["a1"] < 0.9


P.append(dict(
    id="m2-3-1", set="m2", no="3-1", file="t3_1.csv", gen=gen_m2_1, chk=chk_m2_1,
    title="온라인 강의 수료 로지스틱 회귀 — 오즈비, k단위 오즈비, 잔차이탈도",
    statement="""온라인 교육 플랫폼이 한 과정 수강생 320명의 학습 기록과 수료 여부를 정리했다. 데이터 `t3_1.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| learner_id | 수강생 ID |
| study_hours | 주당 평균 학습 시간(시간) |
| quiz_avg | 퀴즈 평균 점수(0~100) |
| age | 나이 |
| mobile | 주로 모바일로 수강했는지 (1 모바일, 0 PC) |
| completed | 수료 여부 (1 수료, 0 미수료) |

completed를 종속변수로, study_hours, quiz_avg, age, mobile 4개를 독립변수로 하는 로지스틱 회귀 모형을 전체 데이터로 적합하시오.

- 절편을 포함한다.
- statsmodels formula API(`smf.logit`)를 사용한다. sklearn의 LogisticRegression은 기본으로 규제가 걸려 결과가 달라지므로 쓰지 않는다.
- 유의수준은 0.05이다.

① 다른 변수가 같을 때, 모바일 수강생(mobile=1)의 수료 오즈는 PC 수강생의 몇 배인지 오즈비를 구하시오.

② 다른 변수가 같을 때, quiz_avg가 10점 높아지면 수료 오즈가 몇 배가 되는지 구하시오.

③ 적합한 모형의 잔차이탈도(residual deviance, −2 × 로그우도)를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 둘째 자리까지""",
    formats=[F3, F3, F2],
    solution="""import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv('data/t3_1.csv')
model = smf.logit('completed ~ study_hours + quiz_avg + age + mobile', data=df).fit(disp=0)

a1 = np.exp(model.params['mobile'])
a2 = np.exp(model.params['quiz_avg'] * 10)
a3 = -2 * model.llf

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 2))
""",
    explain="""로지스틱 회귀계수 β는 로그 오즈의 변화량이라 오즈비는 exp(β)다. k단위 증가의 오즈비는 exp(β×k)이고, exp(β)×k로 계산하면 틀린다.
잔차이탈도는 `-2 * model.llf`다. 영모형 이탈도(`-2 * model.llnull`)와 헷갈리지 않는다.""",
))


# ---------------------------------------------------------------- m2-3-2 chi2 독립성 2x2 (Yates 미적용)
def gen_m2_2(rng):
    n = 140
    ch = np.where(rng.random(n) < 0.5, "문자", "앱푸시")
    pr = np.where(ch == "문자", 0.30, 0.43)
    rv = np.where(rng.random(n) < pr, "Y", "N")
    gender = np.where(rng.random(n) < 0.52, "여", "남")
    return pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(1, n + 1)],
        "gender": gender, "channel": ch, "revisit": rv,
    })


def chk_m2_2(ns, df):
    t = pd.crosstab(df.channel, df.revisit)
    pc = stats.chi2_contingency(t, correction=True)[1]
    return 0.015 < ns["a2"] < 0.042 and 0.058 < pc < 0.15


P.append(dict(
    id="m2-3-2", set="m2", no="3-2", file="t3_2.csv", gen=gen_m2_2, chk=chk_m2_2,
    title="쿠폰 발송 채널과 재방문 — 2×2 카이제곱 독립성 검정 (연속성 보정 없음)",
    statement="""어느 화장품 매장이 쿠폰을 문자 또는 앱 푸시로 보낸 고객 140명을 대상으로 한 달 안에 재방문했는지 기록했다. 한 행이 고객 한 명이다. 데이터 `t3_2.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| customer_id | 고객 ID |
| gender | 성별 |
| channel | 쿠폰 발송 채널 (문자, 앱푸시) |
| revisit | 한 달 안 재방문 여부 (Y, N) |

channel과 revisit으로 2×2 분할표를 만들고, 두 변수가 서로 독립이라는 귀무가설을 카이제곱 독립성 검정으로 검정하시오.

- 연속성 보정(Yates)은 적용하지 않는다. scipy.stats의 `chi2_contingency`를 쓴다면 2×2 표에서 기본값이 보정을 적용하므로 이를 끈다.
- 카이제곱 검정은 오른쪽 꼬리(상측) 검정이다. 유의수준은 0.05이다.
- gender는 이 검정에 쓰지 않는다.

① 검정통계량을 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F3, F4, FD],
    solution="""import pandas as pd
from scipy.stats import chi2_contingency

df = pd.read_csv('data/t3_2.csv')
table = pd.crosstab(df['channel'], df['revisit'])

a1, a2, dof, expected = chi2_contingency(table, correction=False)
a3 = '기각' if a2 < 0.05 else '채택'

print(round(a1, 3))
print(round(a2, 4))
print(a3)
""",
    explain="""원자료(한 행 = 한 명)는 `pd.crosstab`으로 빈도표를 먼저 만든다. 원자료를 그대로 넣으면 안 된다.
`chi2_contingency`는 자유도가 1(2×2 표)일 때 기본값 `correction=True`로 Yates 보정을 적용한다. 이 데이터에서 보정을 끄지 않으면 p-value가 0.05를 넘어 판정이 채택으로 뒤집힌다.
자유도는 (2−1)×(2−1) = 1이다.""",
))


# ---------------------------------------------------------------- m3-3-1 OLS + id split + 재적합
def gen_m3_1(rng):
    n = 240
    area = rng.integers(300, 3001, n)
    workers = np.clip(np.round(area / 20 * rng.uniform(0.6, 1.4, n)), 10, None).astype(int)
    temp = np.round(rng.uniform(-2, 28, n), 1)
    floors = rng.integers(1, 16, n)
    window = np.round(rng.uniform(0.1, 0.6, n), 2)
    built = rng.integers(1985, 2023, n)
    kwh = 4 + 0.017 * area + 0.08 * workers + 0.9 * floors - 0.12 * (built - 2000) + rng.normal(0, 5, n)
    df = pd.DataFrame({
        "id": np.arange(1, n + 1), "area": area, "workers": workers, "avg_temp": temp,
        "floors": floors, "window_ratio": window, "built_year": built, "kwh": np.round(kwh, 1),
    })
    return df.iloc[rng.permutation(n)].reset_index(drop=True)


def chk_m3_1(ns, df):
    import statsmodels.formula.api as smf
    tr = df[df.id <= 180]
    m = smf.ols("kwh ~ area + workers + avg_temp + floors + window_ratio + built_year", data=tr).fit()
    pv = m.pvalues.drop("Intercept")
    if any(0.02 < p < 0.1 for p in pv):
        return False
    # 행 순서로 자르면 답이 달라야 함정이 산다
    tr2 = df.iloc[:180]
    m2 = smf.ols("kwh ~ area + workers + avg_temp + floors + window_ratio + built_year", data=tr2).fit()
    return abs(m2.rsquared - ns["a2"]) > 0.002 and ns["a1"] in (3, 4)


P.append(dict(
    id="m3-3-1", set="m3", no="3-1", file="t3_1.csv", gen=gen_m3_1, chk=chk_m3_1,
    title="사무용 건물 전력사용량 — id 분할, 유의 변수 재적합, test RMSE",
    statement="""어느 지자체가 관내 사무용 건물 240동의 월 전력사용량과 건물 정보를 모았다. 데이터 `t3_1.csv`의 칼럼은 다음과 같다. 행은 id 순서로 정렬되어 있지 않다.

| 칼럼 | 설명 |
|---|---|
| id | 건물 일련번호 (1~240) |
| area | 연면적(m²) |
| workers | 상주 인원(명) |
| avg_temp | 해당 월 평균 기온(℃) |
| floors | 층수 |
| window_ratio | 창면적비 |
| built_year | 준공 연도 |
| kwh | 월 전력사용량(MWh) |

id가 1 이상 180 이하인 건물을 train, 181 이상 240 이하인 건물을 test로 나눈다. (행 순서가 아니라 id 값으로 나눈다)

- 모든 모형은 절편을 포함하고 statsmodels formula API(`smf.ols`)로 train에서만 적합한다.
- p-value는 statsmodels가 출력하는 양측 검정 값을 쓰고, 유의수준은 0.05이다.

① train에서 kwh를 종속변수로, area, workers, avg_temp, floors, window_ratio, built_year 6개를 독립변수로 하는 다중선형회귀 모형을 적합할 때 유의한 독립변수의 개수를 구하시오. (절편은 세지 않는다)

② ①에서 유의한 독립변수만으로 train에서 모형을 다시 적합하고, 그 모형의 결정계수(R²)를 구하시오.

③ ②의 모형으로 test의 kwh를 예측하고 RMSE를 구하시오. RMSE = sqrt(mean((실제값 − 예측값)²))이다.

【제출 형식】 ① 정수 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 셋째 자리까지""",
    formats=[FI, F3, F3],
    solution="""import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv('data/t3_1.csv')
train = df[df['id'] <= 180]
test = df[df['id'] > 180]

full = smf.ols('kwh ~ area + workers + avg_temp + floors + window_ratio + built_year', data=train).fit()
pv = full.pvalues.drop('Intercept')
sig = pv[pv < 0.05].index.tolist()
a1 = len(sig)

refit = smf.ols('kwh ~ ' + ' + '.join(sig), data=train).fit()
a2 = refit.rsquared

pred = refit.predict(test)
a3 = np.sqrt(((test['kwh'] - pred) ** 2).mean())

print(a1)
print(round(a2, 3))
print(round(a3, 3))
""",
    explain="""행이 섞여 있으므로 `df.iloc[:180]`으로 자르면 다른 건물들이 train이 되어 ②③이 달라진다. 반드시 id 값으로 거른다.
유의 변수 목록을 `pvalues`에서 뽑아 formula 문자열로 다시 붙이면 재적합이 간단하다. R²는 수정 R²(`rsquared_adj`)가 아니라 `rsquared`다.
RMSE는 test에서 계산한다. sklearn의 `mean_squared_error`에 제곱근을 씌워도 같다.""",
))


# ---------------------------------------------------------------- m3-3-2 대응표본 t (단측) + 단측 CI 하한
def gen_m3_2(rng):
    n = 32
    before = np.round(rng.normal(372, 35, n)).astype(int)
    diff = rng.normal(9, 22, n)
    after = np.round(before + diff).astype(int)
    subj = [f"U{i:02d}" for i in range(1, n + 1)]
    df = pd.DataFrame({
        "subject": subj * 2, "phase": ["before"] * n + ["after"] * n,
        "sleep_min": np.concatenate([before, after]),
    })
    return df.iloc[rng.permutation(2 * n)].reset_index(drop=True)


def chk_m3_2(ns, df):
    return 0.005 < ns["a2"] < 0.04 and ns["a3"] > 0.5


P.append(dict(
    id="m3-3-2", set="m3", no="3-2", file="t3_2.csv", gen=gen_m3_2, chk=chk_m3_2,
    title="수면 앱 사용 전후 — 단측 대응표본 t검정과 단측 신뢰구간 하한",
    statement="""수면 관리 앱 개발사가 참여자 32명의 앱 사용 전 4주와 사용 후 4주의 하루 평균 수면 시간을 기록했다. 한 행이 참여자 한 명의 한 시기 기록이며, 행 순서는 섞여 있다. 데이터 `t3_2.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| subject | 참여자 ID |
| phase | 시기 (before 사용 전, after 사용 후) |
| sleep_min | 하루 평균 수면 시간(분) |

참여자별로 차이 d = (after의 sleep_min) − (before의 sleep_min)를 만들고, 앱 사용 후 수면 시간이 늘었는지 대응표본 t검정으로 검정하시오. 차이는 정규분포를 따른다고 가정한다.

- 귀무가설: 차이의 모평균 μd = 0, 대립가설: μd > 0 (단측 검정)
- 유의수준은 0.05이다. scipy.stats를 써도 되고 공식으로 직접 계산해도 된다.

① 검정통계량 t를 구하시오.

② 단측 검정의 p-value를 구하시오.

③ 대립가설 방향에 맞춘 μd의 단측 95% 신뢰구간 [L, ∞)의 하한 L을 구하시오. L = d̄ − t(0.95, n−1) × s_d / √n 이며, s_d는 차이의 표본표준편차(ddof=1), t(0.95, n−1)는 자유도 n−1인 t분포의 0.95 분위수이다.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 셋째 자리까지""",
    formats=[F3, F4, F3],
    solution="""import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('data/t3_2.csv')
wide = df.pivot(index='subject', columns='phase', values='sleep_min')
d = wide['after'] - wide['before']
n = len(d)

res = stats.ttest_rel(wide['after'], wide['before'], alternative='greater')
a1 = res.statistic
a2 = res.pvalue
a3 = d.mean() - stats.t.ppf(0.95, n - 1) * d.std(ddof=1) / np.sqrt(n)

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 3))
""",
    explain="""긴 형식이고 행이 섞여 있어 `pivot`으로 참여자별 before·after를 짝지어야 한다. 두 칼럼을 순서대로 뽑아 빼면 다른 사람끼리 짝지어진다.
`ttest_rel(after, before, alternative='greater')`처럼 인자 순서가 d의 방향과 맞아야 한다. 순서를 바꾸면 t의 부호가 뒤집히고 p-value가 1−p가 된다.
단측 구간의 하한은 0.975가 아니라 0.95 분위수를 쓴다. 하한이 0보다 크다는 것과 단측 p < 0.05가 같은 결론이다.""",
))


# ---------------------------------------------------------------- m4-3-1 logit + 행 순서 분할 + 0.5 분류
def gen_m4_1(rng):
    n = 350
    visits = np.round(rng.uniform(0, 6, n), 1)
    months = rng.integers(1, 37, n)
    age = rng.integers(18, 66, n)
    pt = (rng.random(n) < 0.3).astype(int)
    fee = rng.integers(4, 13, n)
    eta = 1.2 - 0.55 * visits - 0.06 * months - 0.8 * pt + 0.12 * fee
    churn = (rng.random(n) < sigmoid(eta)).astype(int)
    return pd.DataFrame({
        "member_id": [f"M{i:04d}" for i in range(1, n + 1)],
        "visits": visits, "months": months, "age": age, "pt": pt, "fee": fee, "churn": churn,
    })


def chk_m4_1(ns, df):
    import statsmodels.formula.api as smf
    tr, te = df.iloc[:260], df.iloc[260:]
    m = smf.logit("churn ~ visits + months + age + pt + fee", data=tr).fit(disp=0)
    pr = m.predict(te)
    if ((pr > 0.47) & (pr < 0.53)).any():
        return False
    pos = te.churn.sum()
    return 0.3 < df.churn.mean() < 0.6 and pos >= 25 and 0.15 < ns["a1"] < 0.85


P.append(dict(
    id="m4-3-1", set="m4", no="3-1", file="t3_1.csv", gen=gen_m4_1, chk=chk_m4_1,
    title="헬스장 회원 해지 로지스틱 회귀 — 예측확률, 오류율, 민감도",
    statement="""어느 헬스장이 회원 350명의 이용 기록과 다음 달 해지 여부를 정리했다. 데이터 `t3_1.csv`의 칼럼은 다음과 같고, 행은 member_id 순서로 정렬되어 있다.

| 칼럼 | 설명 |
|---|---|
| member_id | 회원 ID |
| visits | 최근 3개월 주당 평균 방문 횟수 |
| months | 가입 기간(개월) |
| age | 나이 |
| pt | 개인 PT 이용 여부 (1 이용, 0 미이용) |
| fee | 월 회비(만 원) |
| churn | 다음 달 해지 여부 (1 해지, 0 유지) |

앞에서부터 260행을 train, 나머지 90행을 test로 나눈다. train에서 churn을 종속변수로, visits, months, age, pt, fee 5개를 독립변수로 하는 로지스틱 회귀 모형을 적합하시오.

- 절편을 포함한다.
- statsmodels formula API(`smf.logit`)를 사용한다. sklearn의 LogisticRegression은 기본으로 규제가 걸려 결과가 달라지므로 쓰지 않는다.
- 분류 기준: 예측확률이 0.5 이상이면 1(해지), 0.5 미만이면 0(유지)으로 분류한다.
- 양성 클래스는 churn=1이다.

① test에 있는 회원 M0300의 해지 예측확률을 구하시오.

② test 90행을 분류했을 때 오류율(1 − 정확도)을 구하시오.

③ test에서 민감도(실제 해지 회원 가운데 해지로 분류된 비율, TP / (TP + FN))를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 셋째 자리까지""",
    formats=[F3, F3, F3],
    solution="""import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv('data/t3_1.csv')
train = df.iloc[:260]
test = df.iloc[260:]

model = smf.logit('churn ~ visits + months + age + pt + fee', data=train).fit(disp=0)
prob = model.predict(test)

a1 = prob[test['member_id'] == 'M0300'].iloc[0]

pred = (prob >= 0.5).astype(int)
a2 = (pred != test['churn']).mean()

tp = ((pred == 1) & (test['churn'] == 1)).sum()
fn = ((pred == 0) & (test['churn'] == 1)).sum()
a3 = tp / (tp + fn)

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 3))
""",
    explain="""`model.predict(test)`는 로그 오즈가 아니라 확률을 돌려준다. 확률 > 0.5와 ≥ 0.5는 이 데이터에서 결과가 같지만, 지시된 기준을 그대로 쓰는 습관을 들인다.
오류율은 1 − 정확도, 민감도는 실제 1인 행만 분모로 쓴다. 특이도(실제 0 중 0으로 맞힌 비율)나 정밀도(1로 예측한 것 중 실제 1)와 헷갈리지 않는다.
sklearn의 `recall_score(test['churn'], pred)`와 `confusion_matrix`로 확인해도 같다.""",
))


# ---------------------------------------------------------------- m4-3-2 chi2 적합도
CATS = ["요금", "장애", "해지", "변경", "기타"]
RATIO = [0.35, 0.25, 0.15, 0.15, 0.10]


def gen_m4_2(rng):
    n = 373
    t = rng.choice(CATS, n, p=[0.32, 0.24, 0.20, 0.14, 0.10])
    wait = rng.integers(5, 600, n)
    return pd.DataFrame({
        "call_id": [f"Q{i:05d}" for i in range(10001, 10001 + n)],
        "type": t, "wait_sec": wait,
    })


def chk_m4_2(ns, df):
    # value_counts 순서 그대로 기대비율을 붙이면 답이 달라져야 한다
    vc = df["type"].value_counts()
    if list(vc.index) == CATS:
        return False
    return 0.008 < ns["a3"] < 0.04


P.append(dict(
    id="m4-3-2", set="m4", no="3-2", file="t3_2.csv", gen=gen_m4_2, chk=chk_m4_2,
    title="콜센터 문의 유형 분포 — 카이제곱 적합도 검정",
    statement="""어느 통신사 콜센터가 이번 달 무작위로 뽑은 상담 373건의 문의 유형을 기록했다. 데이터 `t3_2.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| call_id | 상담 ID |
| type | 문의 유형 (요금, 장애, 해지, 변경, 기타) |
| wait_sec | 연결 대기 시간(초) |

작년 한 해 전체 상담의 문의 유형 비율은 다음과 같았다.

| 유형 | 요금 | 장애 | 해지 | 변경 | 기타 |
|---|---|---|---|---|---|
| 비율 | 0.35 | 0.25 | 0.15 | 0.15 | 0.10 |

이번 달 문의 유형 분포가 작년 비율과 같다는 귀무가설을 카이제곱 적합도 검정으로 검정하시오.

- 각 유형의 기대빈도는 (전체 상담 건수) × (작년 비율)이다.
- 카이제곱 검정은 오른쪽 꼬리(상측) 검정이며, 자유도는 (유형 수 − 1)이다. 유의수준은 0.05이다.
- scipy.stats를 써도 되고 공식으로 직접 계산해도 된다. wait_sec는 쓰지 않는다.

① 이번 달 상담 가운데 해지 문의의 비율을 구하시오.

② 검정통계량을 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F3, F4],
    solution="""import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('data/t3_2.csv')
cats = ['요금', '장애', '해지', '변경', '기타']
ratio = np.array([0.35, 0.25, 0.15, 0.15, 0.10])

obs = df['type'].value_counts().reindex(cats)
a1 = obs['해지'] / obs.sum()

expected = ratio * obs.sum()
a2, a3 = stats.chisquare(obs, f_exp=expected)

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 4))
""",
    explain="""`value_counts()`는 빈도 내림차순으로 정렬하므로 기대비율 순서와 어긋난다. `reindex`로 관측빈도를 기대비율과 같은 순서로 맞춘다.
적합도 검정은 `chisquare(관측빈도, f_exp=기대빈도)`다. `chi2_contingency`는 독립성 검정이라 여기서는 쓰지 않는다.
`f_exp`에 비율을 그대로 넣으면 합계가 관측빈도 합과 달라 오류가 나거나 엉뚱한 값이 나온다. 반드시 건수로 바꾼다.""",
))


# ---------------------------------------------------------------- m5-3-1 OLS + C() 기준범주
def gen_m5_1(rng):
    n = 210
    at = rng.choice(["대학가", "역세권", "주거지"], n, p=[0.3, 0.35, 0.35])
    temp = np.round(rng.uniform(5, 33, n), 1)
    price = rng.choice(np.arange(3000, 5600, 100), n)
    seats = rng.integers(15, 81, n)
    eff = pd.Series(at).map({"주거지": 0, "대학가": 18, "역세권": 31}).to_numpy()
    cups = 60 + 2.2 * temp - 0.018 * price + 0.9 * seats + eff + rng.normal(0, 14, n)
    return pd.DataFrame({
        "cafe_id": [f"K{i:03d}" for i in range(1, n + 1)],
        "area_type": at, "temp": temp, "price": price, "seats": seats,
        "cups": np.round(cups).astype(int),
    })


def chk_m5_1(ns, df):
    return 5 < ns["a1"] < 40


P.append(dict(
    id="m5-3-1", set="m5", no="3-1", file="t3_1.csv", gen=gen_m5_1, chk=chk_m5_1,
    title="카페 판매량 회귀 — 범주형 변수 기준범주 지정, 수정 R², 예측",
    statement="""커피 프랜차이즈가 매장 210곳의 어느 하루 아메리카노 판매량과 매장 조건을 모았다. 데이터 `t3_1.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| cafe_id | 매장 ID |
| area_type | 상권 유형 (대학가, 역세권, 주거지) |
| temp | 그날 최고 기온(℃) |
| price | 아메리카노 가격(원) |
| seats | 좌석 수 |
| cups | 아메리카노 판매량(잔) |

cups를 종속변수로, temp, price, seats와 범주형 변수 area_type을 독립변수로 하는 다중선형회귀 모형을 전체 데이터로 적합하시오.

- 절편을 포함한다.
- statsmodels formula API(`smf.ols`)를 사용하고, area_type은 `C()`로 더미 변수화하되 기준범주(reference)를 주거지로 지정한다.
- 유의수준은 0.05이며, p-value는 statsmodels가 출력하는 양측 검정 값을 쓴다.

① 대학가 더미 변수의 회귀계수(다른 조건이 같을 때 주거지 대비 대학가 매장의 판매량 차이)를 구하시오.

② 이 모형의 수정 결정계수(adjusted R²)를 구하시오.

③ area_type이 역세권, temp가 24.0, price가 4200, seats가 40인 매장의 판매량 예측값을 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 둘째 자리까지""",
    formats=[F3, F3, F2],
    solution="""import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv('data/t3_1.csv')
formula = "cups ~ temp + price + seats + C(area_type, Treatment(reference='주거지'))"
model = smf.ols(formula, data=df).fit()

a1 = model.params["C(area_type, Treatment(reference='주거지'))[T.대학가]"]
a2 = model.rsquared_adj

new = pd.DataFrame({'area_type': ['역세권'], 'temp': [24.0], 'price': [4200], 'seats': [40]})
a3 = model.predict(new).iloc[0]

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 2))
""",
    explain="""`C(area_type)`만 쓰면 가나다순 첫 범주(대학가)가 기준이 되어 대학가 계수 자체가 없어진다. `Treatment(reference='주거지')`로 기준을 바꾼다.
계수 이름은 `model.params.index`로 확인하고 그대로 복사해 쓴다. 기준범주를 바꿔도 예측값(③)과 R²는 변하지 않고 더미 계수만 바뀐다.
새 행은 원래 칼럼 이름 그대로 DataFrame으로 만들어 `predict`에 넣으면 formula가 더미 변환까지 해 준다.""",
))


# ---------------------------------------------------------------- m5-3-2 일원분산분석
def gen_m5_2(rng):
    sizes = {"종이목록": 24, "핸드스캐너": 27, "음성안내": 25}
    mus = {"종이목록": 112.0, "핸드스캐너": 121.0, "음성안내": 118.5}
    rows = []
    for g, k in sizes.items():
        for v in rng.normal(mus[g], 13.0, k):
            rows.append((g, round(float(v), 1)))
    df = pd.DataFrame(rows, columns=["method", "picks_per_hour"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    miss = rng.choice(len(df), 5, replace=False)
    df.loc[miss, "picks_per_hour"] = np.nan
    df.insert(0, "worker_id", [f"W{i:03d}" for i in range(1, len(df) + 1)])
    df["tenure_m"] = rng.integers(2, 60, len(df))
    return df


def chk_m5_2(ns, df):
    # 결측이 세 집단 중 둘 이상에 흩어져 있고, 평균 대체를 하면 F가 달라져야 한다
    if (df.groupby("method")["picks_per_hour"].apply(lambda s: s.isna().sum()) > 0).sum() < 2:
        return False
    d = df.copy()
    d["picks_per_hour"] = d["picks_per_hour"].fillna(d["picks_per_hour"].mean())
    f_fill = stats.f_oneway(*[g["picks_per_hour"] for _, g in d.groupby("method")])[0]
    if round(f_fill, 3) == round(ns["a1"], 3):
        return False
    return 0.005 < ns["a2"] < 0.04


P.append(dict(
    id="m5-3-2", set="m5", no="3-2", file="t3_2.csv", gen=gen_m5_2, chk=chk_m5_2,
    title="피킹 방식별 시간당 처리량 — 일원분산분석",
    statement="""어느 물류 창고가 신입 작업자 76명에게 피킹(주문 상품 꺼내기) 방식 세 가지 중 하나를 무작위로 배정하고, 2주 차의 시간당 피킹 건수를 측정했다. 측정 기간에 근무하지 않은 작업자는 기록이 비어 있다. 데이터 `t3_2.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| worker_id | 작업자 ID |
| method | 피킹 방식 (종이목록, 핸드스캐너, 음성안내) |
| picks_per_hour | 시간당 피킹 건수 |
| tenure_m | 이전 직장 물류 경력(개월) |

picks_per_hour가 결측인 행을 제거한 뒤, 세 방식의 평균 picks_per_hour가 모두 같다는 귀무가설을 일원분산분석(one-way ANOVA)으로 검정하시오. 각 집단은 정규분포를 따르고 분산이 같다고 가정한다.

- 대립가설은 "적어도 한 방식의 평균이 다르다"이며, F검정은 오른쪽 꼬리(상측) 검정이다.
- scipy.stats의 `f_oneway`나 statsmodels의 `anova_lm`을 써도 된다. 유의수준은 0.05이다. tenure_m은 쓰지 않는다.

① F 통계량을 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F3, F4, FD],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/t3_2.csv')
df = df.dropna(subset=['picks_per_hour'])

groups = [g['picks_per_hour'] for _, g in df.groupby('method')]
a1, a2 = stats.f_oneway(*groups)
a3 = '기각' if a2 < 0.05 else '채택'

print(round(a1, 3))
print(round(a2, 4))
print(a3)
""",
    explain="""결측이 남아 있으면 `f_oneway`가 nan을 돌려준다. 결측 행을 먼저 지운다. 전체 평균으로 채우면 빈 자리가 모두 같은 값이 되어 집단 평균과 분산이 바뀌고 F가 달라진다.
statsmodels로는 `anova_lm(smf.ols('picks_per_hour ~ C(method)', data=df).fit())`의 F, PR(>F) 열이 같은 값이다.
p-value가 0.05보다 작으므로 기각한다. 적어도 한 방식의 평균 처리량이 다르다는 뜻이며, 어느 방식끼리 다른지는 사후검정(예: Tukey HSD)으로 따로 본다.""",
))


# ---------------------------------------------------------------- 실행
def run_solution(code, csv_name, df):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data"))
    df.to_csv(os.path.join(tmp, "data", csv_name), index=False)
    # CSV 왕복을 거친 데이터로 계산한다
    df2 = pd.read_csv(os.path.join(tmp, "data", csv_name))
    cwd = os.getcwd()
    os.chdir(tmp)
    ns = {}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, ns)
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp)
    return ns, buf.getvalue(), df2


def ok_margins(ns, formats):
    for k, f in zip(["a1", "a2", "a3"], formats):
        if f in DIG and not margin_ok(ns[k], DIG[f]):
            return False
        if f == FD:
            p = ns["a2"]
            if abs(p - 0.05) < 0.008:
                return False
    return True


def main():
    out = []
    for prob in P:
        for seed in range(2000):
            rng = np.random.default_rng(seed + 1000 * (len(out) + 1))
            df = prob["gen"](rng)
            ns, text, df2 = run_solution(prob["solution"], prob["file"], df)
            if not ok_margins(ns, prob["formats"]):
                continue
            if not prob["chk"](ns, df2):
                continue
            break
        else:
            raise SystemExit(f"{prob['id']}: no seed")
        d = os.path.join(REPO, prob["set"])
        os.makedirs(d, exist_ok=True)
        df.to_csv(os.path.join(d, prob["file"]), index=False)
        vals = [fmt(ns[k], f) for k, f in zip(["a1", "a2", "a3"], prob["formats"])]
        print(prob["id"], "seed", seed, "rows", len(df), vals, "| raw", [ns[k] for k in ["a1", "a2", "a3"]])
        out.append({
            "id": prob["id"], "set": prob["set"], "type": 3, "no": prob["no"], "points": 15,
            "title": prob["title"], "statement": prob["statement"],
            "files": [f"{prob['set']}/{prob['file']}"],
            "starter": f"import pandas as pd\ndf = pd.read_csv('data/{prob['file']}')\n",
            "answers": [{"label": l, "format": f, "value": v}
                        for l, f, v in zip(["①", "②", "③"], prob["formats"], vals)],
            "solution": prob["solution"].rstrip("\n"),
            "explain": prob["explain"],
        })
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", OUT_JSON, len(out))


if __name__ == "__main__":
    main()
