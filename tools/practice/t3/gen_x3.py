"""작업형3 검정별 연습(세트 x3) 15문제 생성기. 시험 버전 파이썬(examenv)으로 실행한다.

검정·모형 하나에 문제 하나. gen_t3.py와 같은 방식이다:
각 문제는 gen(rng) -> DataFrame, solution 코드(a1, a2[, a3] 계산 후 print), 조건 검사(chk).
시드를 0부터 올려 반올림 경계 회피·판정 여유·심은 함정이 실제로 답을 바꾸는지를 만족하는 첫 데이터를 쓴다.
출력: practice/x3/x3_01.csv … x3_15.csv, practice/parts/x3.json
"""
import contextlib
import io
import json
import math
import os
import shutil
import tempfile
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))
SET = "x3"
OUT_JSON = os.path.join(REPO, "parts", "x3.json")

F1 = "반올림하여 소수 첫째 자리까지"
F2 = "반올림하여 소수 둘째 자리까지"
F3 = "반올림하여 소수 셋째 자리까지"
F4 = "반올림하여 소수 넷째 자리까지"
FI = "정수"
FD = "기각 또는 채택"
FPAIR = "두 브랜드를 알파벳순으로 하이픈(-)으로 이어 쓴다 (예: A-B)"
DIG = {F1: 1, F2: 2, F3: 3, F4: 4}
KEYS = ["a1", "a2", "a3"]
LABELS = ["①", "②", "③"]


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


def r(x, f):
    """제출 형식으로 반올림한 값 (함정 비교용)."""
    return round(float(x), DIG[f])


def away(p, lo=0.05, gap=0.008):
    return abs(p - lo) >= gap


P = []


# ---------------------------------------------------------------- x3-01 단일표본 t (양측)
def gen_01(rng):
    na, nb = 58, 66
    va = rng.normal(500.3, 2.6, na)
    vb = rng.normal(500.0 + rng.uniform(0.7, 1.3), rng.uniform(2.6, 3.4), nb)
    line = np.array(["A"] * na + ["B"] * nb)
    vol = np.round(np.concatenate([va, vb]), 1)
    idx = rng.permutation(na + nb)
    return pd.DataFrame({
        "bottle_id": [f"W{i:04d}" for i in range(1, na + nb + 1)],
        "line": line[idx], "volume_ml": vol[idx],
    })


def chk_01(ns, df):
    b = df.loc[df.line == "B", "volume_ml"]
    if r(b.std(ddof=0), F3) == r(ns["a1"], F3):
        return False
    p_all = stats.ttest_1samp(df.volume_ml, 500).pvalue
    if r(p_all, F4) == r(ns["a3"], F4):
        return False
    return 0.004 < ns["a3"] < 0.04


P.append(dict(
    no="01", gen=gen_01, chk=chk_01,
    title="단일표본 t검정 — 생수 용량",
    statement="""어느 생수 공장은 두 충전 라인(A, B)에서 표시 용량 500 mL 생수를 생산한다. 품질관리팀이 두 라인에서 생산된 생수를 무작위로 뽑아 실제 용량을 측정했다. 데이터 `x3_01.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| bottle_id | 병 ID |
| line | 충전 라인 (A, B) |
| volume_ml | 측정 용량(mL) |

라인 B에서 생산된 생수의 평균 용량이 표시 용량 500 mL와 같은지 단일표본 t검정으로 검정하시오. 라인 B의 용량은 정규분포를 따른다고 가정한다.

- 귀무가설: μ = 500, 대립가설: μ ≠ 500 (양측 검정)
- 유의수준은 0.05이다.

① 라인 B 용량의 표본표준편차(n−1로 나눔)를 구하시오.

② 검정통계량 t를 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F3, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_01.csv')
b = df.loc[df['line'] == 'B', 'volume_ml']

res = stats.ttest_1samp(b, 500)
a1 = b.std(ddof=1)
a2 = res.statistic
a3 = res.pvalue

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 4))
""",
    explain="""라인 B만 남긴 뒤 검정한다. 두 라인을 섞어 검정하면 표본 수와 평균이 달라져 p-value가 바뀐다.
pandas `.std()`는 기본이 ddof=1이지만 `np.std`는 ddof=0이라 ①이 달라진다.
t = (표본평균 − 500) / (s / √n), 자유도 n−1의 양측 p-value가 `ttest_1samp`의 기본값이다.""",
))


# ---------------------------------------------------------------- x3-02 단일표본 t (단측) + 단측 신뢰구간
def gen_02(rng):
    n = 72
    km = rng.normal(40.0 - rng.uniform(0.6, 1.2), rng.uniform(2.8, 3.6), n)
    temp = np.round(rng.uniform(-2, 31, n), 1)
    return pd.DataFrame({
        "scooter_id": [f"K{i:03d}" for i in range(1, n + 1)],
        "temp_c": temp,
        "range_m": np.round(km * 1000).astype(int),
    })


def chk_02(ns, df):
    x = df.range_m / 1000
    n = len(x)
    p2 = stats.ttest_1samp(x, 40).pvalue
    if p2 < 0.055:  # 양측으로 하면 판정이 채택으로 뒤집혀야 한다
        return False
    u975 = x.mean() + stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    if r(u975, F3) == r(ns["a3"], F3):
        return False
    return 0.006 < ns["a2"] < 0.045


P.append(dict(
    no="02", gen=gen_02, chk=chk_02,
    title="단측 단일표본 t검정과 신뢰구간 — 전동킥보드 주행거리",
    statement="""어느 공유 전동킥보드 업체는 새로 들인 기종이 1회 충전으로 평균 40 km를 달린다고 안내하고 있다. 소비자단체가 이 기종 72대를 완전히 충전한 뒤 배터리가 다 닳을 때까지의 주행거리를 측정했다. 데이터 `x3_02.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| scooter_id | 킥보드 ID |
| temp_c | 측정 당일 평균 기온(℃) |
| range_m | 1회 충전 주행거리(m) |

이 기종의 평균 주행거리가 안내보다 짧은지 단일표본 t검정으로 검정하시오. 주행거리는 정규분포를 따른다고 가정하며, 모든 답은 km 단위로 구한다.

- 귀무가설: μ = 40 km, 대립가설: μ < 40 km (단측 검정)
- 유의수준은 0.05이다.

① 검정통계량 t를 구하시오.

② 단측 검정의 p-value를 구하시오.

③ 표본표준편차(n−1로 나눔)와 t분포를 이용하여 μ의 단측 95% 신뢰구간 (−∞, U]의 상한 U를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 셋째 자리까지""",
    formats=[F3, F4, F3],
    solution="""import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_02.csv')
x = df['range_m'] / 1000
n = len(x)

res = stats.ttest_1samp(x, 40, alternative='less')
a1 = res.statistic
a2 = res.pvalue
a3 = x.mean() + stats.t.ppf(0.95, n - 1) * x.std(ddof=1) / np.sqrt(n)

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 3))
""",
    explain="""주행거리가 m 단위라 1000으로 나눠 km로 바꾼 뒤 40과 비교한다. 바꾸지 않으면 t가 엉뚱하게 커진다.
대립가설이 μ < 40이므로 `alternative='less'`다. 기본값(양측)으로 두면 p-value가 두 배가 되어 0.05를 넘고 판정이 채택으로 뒤집힌다.
구하는 구간이 [L, ∞)가 아니라 (−∞, U]이므로 U = 표본평균 + t(0.95, n−1) × s/√n이다. 0.975 분위수를 쓰면 양측 구간의 상한이 된다. U가 40보다 작다는 것과 단측 p < 0.05가 같은 결론이다.""",
))


# ---------------------------------------------------------------- x3-03 독립 t (등분산 가정)
def gen_03(rng):
    sizes = {"기존": 27, "저당": 41, "고단백": 33}
    mus = {"기존": 1820.0, "저당": 1820.0 - rng.uniform(28, 46), "고단백": 1760.0}
    sds = {"기존": rng.uniform(52, 62), "저당": rng.uniform(40, 48), "고단백": 50.0}
    rows = []
    for g, k in sizes.items():
        for v in rng.normal(mus[g], sds[g], k):
            rows.append((g, round(float(v))))
    df = pd.DataFrame(rows, columns=["recipe", "volume_cc"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    df.insert(0, "loaf_id", [f"B{i:03d}" for i in range(1, len(df) + 1)])
    df["oven_no"] = rng.integers(1, 5, len(df))
    return df


def chk_03(ns, df):
    a = df.loc[df.recipe == "기존", "volume_cc"]
    b = df.loc[df.recipe == "저당", "volume_cc"]
    pw = stats.ttest_ind(a, b, equal_var=False).pvalue
    if r(pw, F4) == r(ns["a3"], F4):
        return False
    return 0.004 < ns["a3"] < 0.045


P.append(dict(
    no="03", gen=gen_03, chk=chk_03,
    title="독립표본 t검정(등분산 가정) — 식빵 레시피 부피",
    statement="""어느 제과점이 식빵 반죽 레시피 세 가지(기존, 저당, 고단백)로 식빵을 구워 한 덩이씩 부피를 쟀다. 데이터 `x3_03.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| loaf_id | 식빵 ID |
| recipe | 레시피 (기존, 저당, 고단백) |
| volume_cc | 구운 뒤 부피(cm³) |
| oven_no | 사용한 오븐 번호 |

기존 레시피와 저당 레시피로 구운 식빵의 평균 부피가 같은지 독립표본 t검정으로 검정하시오. 두 레시피의 부피는 각각 정규분포를 따르고 서로 독립이며, 두 모분산은 같다고 가정한다.

- 귀무가설: μ기존 = μ저당, 대립가설: μ기존 ≠ μ저당 (양측 검정)
- 유의수준은 0.05이다.

① 두 레시피 표본평균의 차(기존 − 저당)를 구하시오.

② 검정통계량 t를 구하시오. (기존 − 저당 방향)

③ p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 둘째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F2, F3, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_03.csv')
a = df.loc[df['recipe'] == '기존', 'volume_cc']
b = df.loc[df['recipe'] == '저당', 'volume_cc']

res = stats.ttest_ind(a, b, equal_var=True)
a1 = a.mean() - b.mean()
a2 = res.statistic
a3 = res.pvalue

print(round(a1, 2))
print(round(a2, 3))
print(round(a3, 4))
""",
    explain="""고단백 레시피는 비교 대상이 아니므로 두 레시피만 뽑는다. 등분산을 가정하므로 합동분산 sp² = ((n1−1)s1² + (n2−1)s2²) / (n1+n2−2)를 쓰고 자유도는 n1+n2−2다.
`ttest_ind`의 기본값이 `equal_var=True`라 이 문제에서는 기본값 그대로 맞는다. `equal_var=False`(Welch)로 하면 두 집단 크기와 분산이 달라 p-value가 달라진다.
인자를 (저당, 기존) 순서로 넣으면 ①②의 부호가 뒤집힌다.""",
))


# ---------------------------------------------------------------- x3-04 Welch t
def gen_04(rng):
    n1, n2 = 64, 26
    c1 = rng.normal(0.52, rng.uniform(0.05, 0.07), n1)
    c2 = rng.normal(0.52 + rng.uniform(0.025, 0.045), rng.uniform(0.11, 0.14), n2)
    plant = np.array(["북부"] * n1 + ["남부"] * n2)
    val = np.round(np.concatenate([c1, c2]), 3)
    idx = rng.permutation(n1 + n2)
    day = rng.integers(1, 31, n1 + n2)
    return pd.DataFrame({
        "sample_id": [f"Q{i:03d}" for i in range(1, n1 + n2 + 1)],
        "plant": plant[idx], "sample_day": day, "chlorine_mgL": val[idx],
    })


def chk_04(ns, df):
    a = df.loc[df.plant == "북부", "chlorine_mgL"]
    b = df.loc[df.plant == "남부", "chlorine_mgL"]
    pp = stats.ttest_ind(a, b, equal_var=True).pvalue
    # 등분산으로 하면 기각, Welch로 하면 채택이 되어야 한다
    return pp < 0.045 and 0.058 < ns["a3"] < 0.2


P.append(dict(
    no="04", gen=gen_04, chk=chk_04,
    title="웰치 t검정 — 정수장 잔류염소 농도",
    statement="""어느 시 상수도사업본부가 두 정수장(북부, 남부)에서 내보낸 수돗물의 잔류염소 농도를 한 달 동안 표본 측정했다. 데이터 `x3_04.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| sample_id | 시료 ID |
| plant | 정수장 (북부, 남부) |
| sample_day | 채수일(일) |
| chlorine_mgL | 잔류염소 농도(mg/L) |

두 정수장의 평균 잔류염소 농도가 같은지 독립표본 t검정으로 검정하시오. 두 정수장의 농도는 각각 정규분포를 따르고 서로 독립이며, 두 모분산이 같다고 가정하지 않는다.

- 귀무가설: μ북부 = μ남부, 대립가설: μ북부 ≠ μ남부 (양측 검정)
- 자유도는 Welch–Satterthwaite 근사식으로 구한다.
- 유의수준은 0.05이다.

① 검정통계량 t를 구하시오. (북부 − 남부 방향)

② 자유도를 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 둘째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F2, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_04.csv')
a = df.loc[df['plant'] == '북부', 'chlorine_mgL']
b = df.loc[df['plant'] == '남부', 'chlorine_mgL']

res = stats.ttest_ind(a, b, equal_var=False)
va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)

a1 = res.statistic
a2 = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
a3 = res.pvalue

print(round(a1, 3))
print(round(a2, 2))
print(round(a3, 4))
""",
    explain="""등분산을 가정하지 않으므로 `ttest_ind(..., equal_var=False)`(Welch 검정)다. 기본값 `equal_var=True`로 두면 이 데이터에서는 p-value가 0.05보다 작아져 판정이 기각으로 뒤집힌다. 표본이 많은 북부의 분산이 작아 합동분산이 작게 잡히기 때문이다.
t = (x̄1 − x̄2) / √(s1²/n1 + s2²/n2), 자유도 = (s1²/n1 + s2²/n2)² / [(s1²/n1)²/(n1−1) + (s2²/n2)²/(n2−1)]이다. scipy 1.11 이상이면 `res.df`로도 자유도를 볼 수 있다.""",
))


# ---------------------------------------------------------------- x3-05 대응 t (양측, wide)
def gen_05(rng):
    n = 60
    base = rng.normal(118, 24, n)
    a = base + rng.normal(0, 3.5, n)
    b = base - rng.uniform(1.0, 1.8) + rng.normal(0, 3.5, n)
    ram = rng.choice([8, 16, 32], n, p=[0.35, 0.45, 0.2])
    return pd.DataFrame({
        "laptop_id": [f"N{i:02d}" for i in range(1, n + 1)],
        "ram_gb": ram,
        "tool_a_sec": np.round(a, 1), "tool_b_sec": np.round(b, 1),
    })


def chk_05(ns, df):
    pi = stats.ttest_ind(df.tool_a_sec, df.tool_b_sec).pvalue
    return pi > 0.3 and 0.004 < ns["a3"] < 0.04


P.append(dict(
    no="05", gen=gen_05, chk=chk_05,
    title="대응표본 t검정 — 압축 프로그램 처리 시간",
    statement="""어느 IT 매체가 노트북 60대에서 같은 폴더(약 20GB)를 두 압축 프로그램(A, B)으로 각각 한 번씩 압축하고 걸린 시간을 쟀다. 한 행이 노트북 한 대이다. 데이터 `x3_05.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| laptop_id | 노트북 ID |
| ram_gb | 메모리 용량(GB) |
| tool_a_sec | 프로그램 A 압축 시간(초) |
| tool_b_sec | 프로그램 B 압축 시간(초) |

노트북별로 차이 d = tool_a_sec − tool_b_sec를 만들고, 두 프로그램의 평균 압축 시간이 같은지 대응표본 t검정으로 검정하시오. 차이는 정규분포를 따른다고 가정한다.

- 귀무가설: μd = 0, 대립가설: μd ≠ 0 (양측 검정)
- 유의수준은 0.05이다.

① 차이 d의 표본평균을 구하시오.

② 검정통계량 t를 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F3, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_05.csv')
d = df['tool_a_sec'] - df['tool_b_sec']

res = stats.ttest_rel(df['tool_a_sec'], df['tool_b_sec'])
a1 = d.mean()
a2 = res.statistic
a3 = res.pvalue

print(round(a1, 3))
print(round(a2, 3))
print(round(a3, 4))
""",
    explain="""같은 노트북에서 두 프로그램을 잰 짝지은 자료라 대응표본 검정이다. t = d̄ / (s_d / √n), 자유도 n−1. `ttest_1samp(d, 0)`과 같은 값이다.
독립표본 t검정(`ttest_ind`)으로 하면 노트북 사이의 성능 차이(수십 초)가 오차에 섞여 p-value가 0.3을 넘고 차이를 놓친다.
인자 순서를 (B, A)로 바꾸면 t의 부호만 뒤집힌다.""",
))


# ---------------------------------------------------------------- x3-06 Shapiro–Wilk
def gen_06(rng):
    n_new, n_old = 78, 150
    new = rng.normal(46, 11, n_new)
    old = rng.lognormal(np.log(38), 0.55, n_old)
    days = np.concatenate([rng.integers(1, 31, n_new), rng.integers(31, 721, n_old)])
    play = np.round(np.clip(np.concatenate([new, old]), 1, None), 1)
    dev = np.where(rng.random(n_new + n_old) < 0.55, "android", "ios")
    idx = rng.permutation(n_new + n_old)
    return pd.DataFrame({
        "user_id": [f"G{i:04d}" for i in range(1, n_new + n_old + 1)],
        "device": dev, "signup_days": days[idx], "play_min": play[idx],
    })


def chk_06(ns, df):
    p_all = stats.shapiro(df.play_min).pvalue
    return p_all < 0.01 and 0.12 < ns["a2"] < 0.8


P.append(dict(
    no="06", gen=gen_06, chk=chk_06,
    title="샤피로–윌크 정규성 검정 — 신규 이용자 플레이 시간",
    statement="""어느 모바일 게임사가 이용자 228명의 지난주 하루 평균 플레이 시간을 뽑았다. 데이터 `x3_06.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| user_id | 이용자 ID |
| device | 기기 (android, ios) |
| signup_days | 가입 후 경과 일수(일) |
| play_min | 하루 평균 플레이 시간(분) |

가입 후 경과 일수가 30일 이하인 신규 이용자만 대상으로, play_min이 정규분포를 따르는지 샤피로–윌크(Shapiro–Wilk) 검정으로 검정하시오.

- 귀무가설: 신규 이용자의 play_min은 정규분포를 따른다.
- 유의수준은 0.05이다.

① 검정통계량 W를 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 넷째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F4, F4, FD], pkey="a2",
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_06.csv')
new = df.loc[df['signup_days'] <= 30, 'play_min']

a1, a2 = stats.shapiro(new)
a3 = '기각' if a2 < 0.05 else '채택'

print(round(a1, 4))
print(round(a2, 4))
print(a3)
""",
    explain="""경과 일수 30일 이하(30 포함)인 행만 남긴다. 전체 이용자로 검정하면 오래된 이용자의 오른쪽으로 긴 꼬리 때문에 p-value가 0.01보다 작아져 기각으로 뒤집힌다.
샤피로–윌크 검정의 귀무가설은 "정규분포를 따른다"이다. p-value가 0.05보다 크므로 채택(정규성 가정을 기각하지 못함)이다.
W는 1에 가까울수록 정규분포에 가깝다.""",
))


# ---------------------------------------------------------------- x3-07 Levene(평균 중심) + Bartlett
def gen_07(rng):
    sizes = {"101번": 42, "230번": 47, "702번": 39}
    sds = {"101번": 2.6, "230번": 2.6 * rng.uniform(1.1, 1.35), "702번": 2.6 * rng.uniform(0.95, 1.15)}
    mus = {"101번": 9.0, "230번": 9.5, "702번": 8.6}
    rows = []
    for g, k in sizes.items():
        v = mus[g] + sds[g] * rng.standard_t(5, k) * np.sqrt(3 / 5)
        for x in np.clip(v, 1.0, None):
            rows.append((g, round(float(x), 1)))
    df = pd.DataFrame(rows, columns=["route", "interval_min"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    df.insert(0, "record_id", [f"R{i:03d}" for i in range(1, len(df) + 1)])
    df["hour"] = rng.integers(6, 23, len(df))
    return df


def chk_07(ns, df):
    groups = [g["interval_min"] for _, g in df.groupby("route")]
    lm = stats.levene(*groups)  # 기본값: 중앙값 중심
    if r(lm.statistic, F3) == r(ns["a1"], F3):
        return False
    return away(ns["a2"], gap=0.01) and away(ns["a3"], gap=0.01) and 0.005 < ns["a2"] < 0.6


P.append(dict(
    no="07", gen=gen_07, chk=chk_07,
    title="레빈·바틀렛 등분산 검정 — 시내버스 노선별 배차 간격",
    statement="""어느 시 교통정보센터가 시내버스 세 노선(101번, 230번, 702번)의 정류장 도착 기록에서 연이은 두 차량의 배차 간격을 뽑았다. 데이터 `x3_07.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| record_id | 기록 ID |
| route | 노선 (101번, 230번, 702번) |
| interval_min | 배차 간격(분) |
| hour | 도착 시각(시) |

세 노선의 배차 간격 모분산이 모두 같다는 귀무가설을 두 가지 방법으로 검정하시오.

- 레빈(Levene) 검정은 각 관측값과 그 노선 평균의 차의 절댓값으로 계산한다.
- 바틀렛(Bartlett) 검정은 각 노선의 배차 간격이 정규분포를 따른다고 가정한다.
- 유의수준은 0.05이다.

① 레빈 검정의 검정통계량을 구하시오.

② 레빈 검정의 p-value를 구하시오.

③ 바틀렛 검정의 p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F4, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_07.csv')
groups = [g['interval_min'] for _, g in df.groupby('route')]

lev = stats.levene(*groups, center='mean')
bar = stats.bartlett(*groups)
a1 = lev.statistic
a2 = lev.pvalue
a3 = bar.pvalue

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 4))
""",
    explain="""scipy `levene`의 기본값은 `center='median'`(Brown–Forsythe 변형)이다. 지문이 평균 기준이므로 `center='mean'`을 줘야 하며, 기본값으로 두면 ①②가 달라진다.
레빈 검정은 |x − 집단 평균|에 일원분산분석을 한 것과 같다. 바틀렛 검정은 정규성에 민감해 꼬리가 두꺼운 자료에서는 레빈과 p-value가 크게 다를 수 있다.""",
))


# ---------------------------------------------------------------- x3-08 일원 ANOVA + Tukey HSD
def gen_08(rng):
    sizes = {"A": 18, "B": 23, "C": 20, "D": 25}
    mus = {"A": 1500, "B": 1500 + rng.uniform(40, 70), "C": 1500 + rng.uniform(-40, -15), "D": 1500 + rng.uniform(85, 120)}
    rows = []
    for g, k in sizes.items():
        for v in rng.normal(mus[g], 62, k):
            rows.append((g, int(round(v))))
    df = pd.DataFrame(rows, columns=["brand", "pages"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    df.insert(0, "cartridge_id", [f"C{i:03d}" for i in range(1, len(df) + 1)])
    df["coverage_pct"] = 5
    return df


def chk_08(ns, df):
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    from itertools import combinations
    tk = pairwise_tukeyhsd(df["pages"], df["brand"], alpha=0.05)
    if any(abs(p - 0.05) < 0.01 for p in tk.pvalues):
        return False
    gs = sorted(df.brand.unique())
    sc = stats.tukey_hsd(*[df.loc[df.brand == g, "pages"] for g in gs])
    n_sc = sum(sc.pvalue[i, j] < 0.05 for i, j in combinations(range(len(gs)), 2))
    if n_sc != ns["a2"]:
        return False
    # 보정 없는 두 집단 t검정을 반복하면 유의 쌍이 더 많이 나와야 한다
    n_raw = sum(stats.ttest_ind(df.loc[df.brand == a, "pages"], df.loc[df.brand == b, "pages"]).pvalue < 0.05
                for a, b in combinations(gs, 2))
    if n_raw <= ns["a2"]:
        return False
    m = df.groupby("brand")["pages"].mean()
    diffs = sorted(abs(m[a] - m[b]) for a, b in combinations(gs, 2))
    if diffs[-1] - diffs[-2] < 15:
        return False
    return 1 <= ns["a2"] <= 4


P.append(dict(
    no="08", gen=gen_08, chk=chk_08,
    title="일원분산분석과 Tukey HSD — 프린터 카트리지 출력 매수",
    statement="""어느 사무용품 비교 사이트가 호환 잉크 카트리지 네 브랜드(A, B, C, D)를 같은 프린터에 끼우고, 인쇄 면적 5% 문서를 잉크가 다 떨어질 때까지 출력한 매수를 기록했다. 데이터 `x3_08.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| cartridge_id | 카트리지 ID |
| brand | 브랜드 (A, B, C, D) |
| pages | 출력 매수(장) |
| coverage_pct | 문서 인쇄 면적(%) |

네 브랜드의 평균 출력 매수가 모두 같다는 귀무가설을 일원분산분석으로 검정하고, 사후검정으로 Tukey HSD를 수행하시오. 각 브랜드의 출력 매수는 정규분포를 따르고 분산이 같다고 가정한다.

- F검정은 오른쪽 꼬리(상측) 검정이다.
- 유의수준은 0.05이며, 사후검정의 유의 여부는 Tukey 방법으로 조정한 p-value로 판단한다.

① 일원분산분석의 F 통계량을 구하시오.

② Tukey HSD 결과 평균 출력 매수가 유의하게 다른 브랜드 쌍의 개수를 구하시오.

③ 여섯 쌍 가운데 두 브랜드 표본평균의 차(절댓값)가 가장 큰 쌍을 쓰시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 정수 ③ 두 브랜드를 알파벳순으로 하이픈(-)으로 이어 쓴다 (예: A-B)""",
    formats=[F3, FI, FPAIR],
    solution="""import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

df = pd.read_csv('data/x3_08.csv')
groups = [g['pages'] for _, g in df.groupby('brand')]
a1 = stats.f_oneway(*groups).statistic

tk = pairwise_tukeyhsd(df['pages'], df['brand'], alpha=0.05)
res = pd.DataFrame(tk.summary().data[1:], columns=tk.summary().data[0])
a2 = int(res['reject'].sum())

big = res.loc[res['meandiff'].abs().idxmax()]
a3 = f"{big['group1']}-{big['group2']}"

print(round(a1, 3))
print(a2)
print(a3)
""",
    explain="""`pairwise_tukeyhsd(값, 집단)` 결과표의 reject 열이 True인 쌍이 ②다. group1·group2는 알파벳순으로 나오고 meandiff는 group2 − group1이므로 절댓값으로 비교한다.
두 브랜드씩 보정 없이 t검정을 여섯 번 하면 1종 오류가 부풀어 유의한 쌍이 더 많이 나온다. Tukey HSD는 여섯 비교 전체의 유의수준을 0.05로 맞춘다.
scipy 1.8 이상의 `stats.tukey_hsd(*groups)`도 같은 판정을 준다(`pvalue` 행렬). F는 `f_oneway` 또는 `anova_lm(smf.ols('pages ~ C(brand)', df).fit())`로 같다.""",
))


# ---------------------------------------------------------------- x3-09 이원 ANOVA (Type II, 불균형)
def gen_09(rng):
    paints = ["수성", "유성", "우레탄"]
    drys = ["자연", "열풍"]
    eff_p = {"수성": 0.0, "유성": rng.uniform(1.0, 2.0), "우레탄": rng.uniform(2.0, 3.0)}
    eff_d = {"자연": 0.0, "열풍": rng.uniform(1.5, 2.5)}
    inter = rng.uniform(1.2, 2.4)
    rows = []
    for p in paints:
        for d in drys:
            k = int(rng.integers(6, 17))
            mu = 60 + eff_p[p] + eff_d[d] + (inter if (p == "우레탄" and d == "열풍") else 0)
            for v in rng.normal(mu, 2.4, k):
                rows.append((p, d, round(float(v), 2)))
    df = pd.DataFrame(rows, columns=["paint", "drying", "hardness"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    df.insert(0, "panel_id", [f"T{i:03d}" for i in range(1, len(df) + 1)])
    return df


def chk_09(ns, df):
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm
    if len(df) < 60:
        return False
    m = smf.ols("hardness ~ C(paint) * C(drying)", data=df).fit()
    t1 = anova_lm(m, typ=1)
    if r(t1.loc["C(paint)", "PR(>F)"], F4) == r(ns["a3"], F4):
        return False
    return away(ns["a2"], gap=0.01) and 0.0005 < ns["a3"] < 0.04 and 0.0005 < ns["a2"] < 0.6


P.append(dict(
    no="09", gen=gen_09, chk=chk_09,
    title="이원분산분석 — 도료와 건조 방식별 도막 경도",
    statement="""어느 도료 회사 연구소가 세 도료(수성, 유성, 우레탄)를 두 건조 방식(자연, 열풍) 가운데 하나로 말린 시험판에 칠하고 도막 경도를 측정했다. 조합마다 시험판 수가 다르다. 데이터 `x3_09.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| panel_id | 시험판 ID |
| paint | 도료 (수성, 유성, 우레탄) |
| drying | 건조 방식 (자연, 열풍) |
| hardness | 도막 경도 지수 |

hardness를 종속변수로, paint와 drying 두 요인의 주효과와 상호작용효과를 모두 포함하는 이원분산분석을 수행하시오. 오차는 정규분포를 따르고 등분산이라고 가정한다.

- 각 효과의 제곱합은 제2종(Type II) 제곱합으로 계산한다.
- F검정은 오른쪽 꼬리(상측) 검정이며, 유의수준은 0.05이다.

① 상호작용효과(paint × drying)의 F 통계량을 구하시오.

② 상호작용효과의 p-value를 구하시오.

③ paint 주효과의 p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F4, F4],
    solution="""import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

df = pd.read_csv('data/x3_09.csv')
model = smf.ols('hardness ~ C(paint) * C(drying)', data=df).fit()
table = anova_lm(model, typ=2)

a1 = table.loc['C(paint):C(drying)', 'F']
a2 = table.loc['C(paint):C(drying)', 'PR(>F)']
a3 = table.loc['C(paint)', 'PR(>F)']

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 4))
""",
    explain="""`C(paint) * C(drying)`는 두 주효과와 상호작용을 모두 넣는다. `anova_lm`의 기본값은 `typ=1`(순차 제곱합)이다. 조합마다 표본 수가 달라(불균형) 제1종에서는 먼저 들어간 paint의 제곱합이 drying을 보정하지 않은 값이 되어 ③이 달라진다. 제2종은 각 주효과를 다른 주효과로 보정한다.
상호작용항은 모형의 마지막 항이라 제1종·제2종에서 같다. 숫자형 칼럼이 아니어도 `C()`로 감싸면 범주로 처리된다.""",
))


# ---------------------------------------------------------------- x3-10 카이제곱 적합도 (요일 균등)
def gen_10(rng):
    start = pd.Timestamp("2026-03-02")  # 월요일, 26주 = 182일
    w = np.array([1.0, 0.95, 1.0, 0.98, 1.05, 1.0 + rng.uniform(0.35, 0.6), 1.0 + rng.uniform(0.25, 0.5)])
    n = int(rng.integers(180, 230))
    days = []
    for _ in range(n):
        wd = rng.choice(7, p=w / w.sum())
        wk = rng.integers(0, 26)
        days.append(start + pd.Timedelta(days=int(wk * 7 + wd)))
    hm = rng.integers(6 * 60, 22 * 60, n)
    ts = [d + pd.Timedelta(minutes=int(m)) for d, m in zip(days, hm)]
    kind = rng.choice(["미끄러짐", "부딪힘", "근육경련", "기타"], n, p=[0.45, 0.25, 0.2, 0.1])
    df = pd.DataFrame({"occurred_at": ts, "kind": kind}).sort_values("occurred_at").reset_index(drop=True)
    df["occurred_at"] = df["occurred_at"].dt.strftime("%Y-%m-%d %H:%M")
    df.insert(0, "incident_id", [f"I{i:04d}" for i in range(1, n + 1)])
    return df


def chk_10(ns, df):
    wd = pd.to_datetime(df.occurred_at).dt.dayofweek.value_counts()
    if (wd == wd.max()).sum() != 1:
        return False
    return away(ns["a3"], gap=0.01) and 0.004 < ns["a3"] < 0.045


P.append(dict(
    no="10", gen=gen_10, chk=chk_10,
    title="카이제곱 적합도 검정 — 요일별 수영장 안전사고",
    statement="""어느 시립 수영장이 2026년 3월 2일(월)부터 8월 30일(일)까지 26주 동안 접수된 안전사고를 한 건씩 기록했다. 이 기간에는 월요일부터 일요일까지 각 요일이 26일씩 있으며, 수영장은 휴관일 없이 매일 운영했다. 데이터 `x3_10.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| incident_id | 사고 ID |
| occurred_at | 발생 일시 (YYYY-MM-DD HH:MM) |
| kind | 사고 유형 |

안전사고가 요일과 관계없이 고르게(일곱 요일이 각각 1/7의 비율로) 발생한다는 귀무가설을 카이제곱 적합도 검정으로 검정하시오.

- 카이제곱 검정은 오른쪽 꼬리(상측) 검정이며, 유의수준은 0.05이다.

① 사고가 가장 많이 발생한 요일의 사고 건수를 구하시오.

② 검정통계량을 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 정수 ② 반올림하여 소수 셋째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[FI, F3, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_10.csv')
df['occurred_at'] = pd.to_datetime(df['occurred_at'])
obs = df['occurred_at'].dt.dayofweek.value_counts().reindex(range(7), fill_value=0)

exp = [len(df) / 7] * 7
res = stats.chisquare(obs, f_exp=exp)
a1 = obs.max()
a2 = res.statistic
a3 = res.pvalue

print(int(a1))
print(round(a2, 3))
print(round(a3, 4))
""",
    explain="""발생 일시를 날짜형으로 바꾼 뒤 `dt.dayofweek`(월=0 … 일=6)로 요일을 뽑아 센다. 기대빈도는 전체 건수 / 7이고, `chisquare`의 `f_exp`를 생략해도 균등 분포로 계산한다.
자유도는 범주 수 − 1 = 6이다. 각 요일이 26일씩으로 같으므로 기대비율이 1/7씩이다. 기간에 요일별 일수가 다르면 기대빈도를 일수에 비례하게 잡아야 한다.""",
))


# ---------------------------------------------------------------- x3-11 카이제곱 독립성 2x2 (Yates 적용)
def gen_11(rng):
    n = int(rng.integers(150, 190))
    badge = np.where(rng.random(n) < 0.5, "표시", "미표시")
    pr = np.where(badge == "표시", 0.55, 0.55 + rng.uniform(0.13, 0.19))
    ab = np.where(rng.random(n) < pr, "Y", "N")
    dev = np.where(rng.random(n) < 0.7, "모바일", "PC")
    return pd.DataFrame({
        "session_id": [f"S{i:04d}" for i in range(1, n + 1)],
        "device": dev, "free_ship_badge": badge, "abandoned": ab,
    })


def chk_11(ns, df):
    t = pd.crosstab(df.free_ship_badge, df.abandoned)
    pu = stats.chi2_contingency(t, correction=False)[1]
    return pu < 0.045 and 0.056 < ns["a2"] < 0.15


P.append(dict(
    no="11", gen=gen_11, chk=chk_11,
    title="카이제곱 독립성 검정(Yates 보정) — 무료배송 표시와 장바구니 이탈",
    statement="""어느 온라인 쇼핑몰이 장바구니 화면에 무료배송 안내 문구를 무작위로 표시하거나 표시하지 않고, 그 세션에서 결제하지 않고 떠났는지(장바구니 이탈)를 기록했다. 한 행이 세션 하나이다. 데이터 `x3_11.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| session_id | 세션 ID |
| device | 접속 기기 (모바일, PC) |
| free_ship_badge | 무료배송 문구 (표시, 미표시) |
| abandoned | 장바구니 이탈 여부 (Y, N) |

free_ship_badge와 abandoned로 2×2 분할표를 만들고, 두 변수가 서로 독립이라는 귀무가설을 카이제곱 독립성 검정으로 검정하시오.

- 연속성 보정(Yates)을 적용한다.
- 카이제곱 검정은 오른쪽 꼬리(상측) 검정이며, 유의수준은 0.05이다.

① 검정통계량을 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F3, F4, FD], pkey="a2",
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_11.csv')
table = pd.crosstab(df['free_ship_badge'], df['abandoned'])

chi2, p, dof, expected = stats.chi2_contingency(table, correction=True)
a1 = chi2
a2 = p
a3 = '기각' if p < 0.05 else '채택'

print(round(a1, 3))
print(round(a2, 4))
print(a3)
""",
    explain="""원자료는 `pd.crosstab`으로 빈도표를 먼저 만든다. `chi2_contingency`는 자유도가 1(2×2 표)일 때 기본값 `correction=True`로 Yates 보정을 적용하므로 이 문제에서는 기본값 그대로 맞는다.
Yates 보정은 각 칸에서 |관측 − 기대|를 0.5만큼 줄여 통계량을 작게 만든다. 보정을 끄면(`correction=False`) 이 데이터에서는 p-value가 0.05보다 작아져 판정이 기각으로 뒤집힌다.
자유도는 (2−1)×(2−1) = 1이다. device는 쓰지 않는다.""",
))


# ---------------------------------------------------------------- x3-12 Mann–Whitney U (단측)
def gen_12(rng):
    n1, n2 = 46, 52
    shift = rng.uniform(0.45, 0.8)
    new = np.clip(np.round(rng.normal(6.6 + shift, 1.7, n1)), 1, 10).astype(int)
    old = np.clip(np.round(rng.normal(6.6, 1.7, n2)), 1, 10).astype(int)
    model = np.array(["신형"] * n1 + ["구형"] * n2)
    sc = np.concatenate([new, old])
    idx = rng.permutation(n1 + n2)
    age = rng.integers(18, 61, n1 + n2)
    return pd.DataFrame({
        "tester_id": [f"E{i:03d}" for i in range(1, n1 + n2 + 1)],
        "age": age, "model": model[idx], "comfort": sc[idx],
    })


def chk_12(ns, df):
    a = df.loc[df.model == "신형", "comfort"]
    b = df.loc[df.model == "구형", "comfort"]
    p2 = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    # 양측으로 하면 채택으로 뒤집혀야 한다
    return p2 > 0.055 and 0.008 < ns["a2"] < 0.045


P.append(dict(
    no="12", gen=gen_12, chk=chk_12,
    title="맨–휘트니 U 검정(단측) — 이어폰 착용감 점수",
    statement="""어느 음향기기 회사가 무선 이어폰 신형과 구형을 체험단에게 무작위로 나눠 주고 일주일 사용 후 착용감을 1~10점으로 평가받았다. 한 사람은 한 기종만 평가했다. 데이터 `x3_12.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| tester_id | 체험단 ID |
| age | 나이 |
| model | 평가한 기종 (신형, 구형) |
| comfort | 착용감 점수(1~10, 정수) |

착용감 점수는 정규분포를 가정하기 어렵다. 신형의 착용감 점수가 구형보다 높은 쪽으로 치우쳐 있는지 맨–휘트니 U 검정(윌콕슨 순위합 검정)으로 검정하시오.

- 귀무가설: 두 기종의 점수 분포가 같다. 대립가설: 신형의 점수가 구형보다 큰 쪽으로 치우쳐 있다 (단측 검정).
- 동점은 평균 순위를 주고, p-value는 동순위 보정을 한 정규근사로 구하며 연속성 보정을 적용한다.
- 유의수준은 0.05이다.

① 신형 기준의 U 통계량 (신형 점수의 순위합 − n신형(n신형+1)/2)을 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 첫째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F1, F4, FD], pkey="a2",
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_12.csv')
new = df.loc[df['model'] == '신형', 'comfort']
old = df.loc[df['model'] == '구형', 'comfort']

res = stats.mannwhitneyu(new, old, alternative='greater')
a1 = res.statistic
a2 = res.pvalue
a3 = '기각' if a2 < 0.05 else '채택'

print(round(a1, 1))
print(round(a2, 4))
print(a3)
""",
    explain="""`mannwhitneyu(x, y)`의 statistic은 첫 번째 인자(x) 기준 U다. 인자 순서를 바꾸면 U가 n1·n2 − U로 바뀌고, alternative도 'less'로 바꿔야 같은 p-value가 나온다.
동점이 많으면 기본값 `method='auto'`가 정규근사를 고르며 동순위 보정과 연속성 보정(`use_continuity=True`)을 적용한다.
대립가설이 "신형이 더 크다"이므로 `alternative='greater'`다. 기본값(양측)으로 두면 p-value가 약 두 배가 되어 0.05를 넘고 판정이 채택으로 뒤집힌다.""",
))


# ---------------------------------------------------------------- x3-13 Wilcoxon 부호순위 (양측)
def gen_13(rng):
    n = 72
    before = rng.poisson(rng.uniform(22, 30), n) + rng.integers(0, 15, n)
    delta = np.round(rng.normal(-rng.uniform(1.2, 2.0), 3.2, n)).astype(int)
    zero = rng.random(n) < 0.12
    delta[zero] = 0
    after = np.clip(before + delta, 0, None)
    dept = rng.choice(["영업", "개발", "인사", "재무"], n)
    return pd.DataFrame({
        "emp_id": [f"M{i:03d}" for i in range(1, n + 1)],
        "dept": dept, "before_mail": before, "after_mail": after,
    })


def chk_13(ns, df):
    d = df.after_mail - df.before_mail
    if ns["a1"] <= 52 or (d == 0).sum() < 4:
        return False
    pz = stats.wilcoxon(df.after_mail, df.before_mail, zero_method="zsplit").pvalue
    if r(pz, F4) == r(ns["a3"], F4):
        return False
    return away(ns["a3"], gap=0.01) and 0.003 < ns["a3"] < 0.04


P.append(dict(
    no="13", gen=gen_13, chk=chk_13,
    title="윌콕슨 부호순위 검정 — 메신저 도입 전후 이메일 발송 수",
    statement="""어느 회사가 사내 메신저를 도입하고, 직원 72명의 도입 전 한 주와 도입 후 한 주의 업무 이메일 발송 건수를 비교했다. 한 행이 직원 한 명이다. 데이터 `x3_13.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| emp_id | 직원 ID |
| dept | 부서 |
| before_mail | 도입 전 주간 이메일 발송 건수 |
| after_mail | 도입 후 주간 이메일 발송 건수 |

직원별로 차이 d = after_mail − before_mail을 만들고, d의 분포가 0을 중심으로 대칭이라는 귀무가설을 윌콕슨 부호순위 검정으로 검정하시오.

- 대립가설은 "0을 중심으로 대칭이 아니다"이다 (양측 검정).
- d = 0인 직원은 분석에서 제외한다. |d|가 같으면 평균 순위를 준다.
- p-value는 동순위 보정을 한 정규근사로 구하며, 연속성 보정은 적용하지 않는다.
- 유의수준은 0.05이다.

① d = 0인 직원을 제외한 분석 인원을 구하시오.

② 양(+)의 부호순위합과 음(−)의 부호순위합 가운데 작은 값을 검정통계량으로 할 때, 그 값을 구하시오.

③ p-value를 구하시오.

【제출 형식】 ① 정수 ② 반올림하여 소수 첫째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[FI, F1, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_13.csv')
d = df['after_mail'] - df['before_mail']

res = stats.wilcoxon(df['after_mail'], df['before_mail'])
a1 = (d != 0).sum()
a2 = res.statistic
a3 = res.pvalue

print(int(a1))
print(round(a2, 1))
print(round(a3, 4))
""",
    explain="""`wilcoxon(x, y)`는 d = x − y로 계산하고, 기본값 `zero_method='wilcox'`가 d = 0인 쌍을 버린 뒤 순위를 매긴다. 양측 검정의 statistic은 양·음 순위합 중 작은 값이다.
분석 인원이 50을 넘고 동점이 있어 기본값 `method='auto'`가 정규근사를 쓰며, 기본값 `correction=False`라 연속성 보정은 하지 않는다.
`zero_method='zsplit'`이나 'pratt'처럼 0을 순위에 넣으면 ②③이 달라진다. 정규성을 가정하는 대응 t검정과도 p-value가 다르다.""",
))


# ---------------------------------------------------------------- x3-14 Kruskal–Wallis
def gen_14(rng):
    sizes = {"라이트": 34, "스탠다드": 38, "프리미엄": 30, "무제한": 22}
    meds = {"라이트": 6.0, "스탠다드": 6.0 * rng.uniform(1.12, 1.3), "프리미엄": 6.0 * rng.uniform(1.25, 1.45), "무제한": 40.0}
    rows = []
    for g, k in sizes.items():
        for v in rng.lognormal(np.log(meds[g]), 0.75, k):
            rows.append((g, round(float(v), 2)))
    df = pd.DataFrame(rows, columns=["plan", "data_gb"])
    df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    miss = rng.choice(len(df), 6, replace=False)
    df.loc[miss, "data_gb"] = np.nan
    df.insert(0, "line_id", [f"L{i:04d}" for i in range(1, len(df) + 1)])
    df["tenure_m"] = rng.integers(1, 97, len(df))
    return df


def chk_14(ns, df):
    d = df.dropna(subset=["data_gb"])
    if (df.loc[df.plan != "무제한"].data_gb.isna().sum()) < 3:
        return False
    h_all = stats.kruskal(*[g.data_gb for _, g in d.groupby("plan")])
    if r(h_all.statistic, F3) == r(ns["a1"], F3):
        return False
    s = d[d.plan != "무제한"]
    pa = stats.f_oneway(*[g.data_gb for _, g in s.groupby("plan")]).pvalue
    # 정규성을 가정한 분산분석과 판정이 갈리면 비모수 검정의 의미가 산다
    if (pa < 0.05) == (ns["a2"] < 0.05):
        return False
    return 0.004 < ns["a2"] < 0.042


P.append(dict(
    no="14", gen=gen_14, chk=chk_14,
    title="크러스컬–월리스 검정 — 요금제별 월 데이터 사용량",
    statement="""어느 알뜰폰 통신사가 가입 회선 124개의 지난달 모바일 데이터 사용량을 뽑았다. 일부 회선은 집계 오류로 사용량이 비어 있다. 데이터 `x3_14.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| line_id | 회선 ID |
| plan | 요금제 (라이트, 스탠다드, 프리미엄, 무제한) |
| data_gb | 지난달 데이터 사용량(GB) |
| tenure_m | 가입 기간(개월) |

무제한 요금제를 제외한 세 요금제(라이트, 스탠다드, 프리미엄)만 대상으로 하고, data_gb가 결측인 행을 제거한 뒤, 세 요금제의 데이터 사용량 분포가 모두 같다는 귀무가설을 크러스컬–월리스(Kruskal–Wallis) 검정으로 검정하시오.

- 동점은 평균 순위를 주고, 검정통계량은 동순위 보정을 한 H이며, p-value는 카이제곱 근사로 구한다.
- 유의수준은 0.05이다.

① 검정통계량 H를 구하시오.

② p-value를 구하시오.

③ 유의수준 0.05에서 귀무가설을 기각하는지 채택하는지 쓰시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 기각 또는 채택""",
    formats=[F3, F4, FD], pkey="a2",
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_14.csv')
df = df[df['plan'] != '무제한'].dropna(subset=['data_gb'])

groups = [g['data_gb'] for _, g in df.groupby('plan')]
a1, a2 = stats.kruskal(*groups)
a3 = '기각' if a2 < 0.05 else '채택'

print(round(a1, 3))
print(round(a2, 4))
print(a3)
""",
    explain="""무제한 요금제를 먼저 빼고, 결측을 지운다. 결측이 남아 있으면 `kruskal`이 nan을 돌려준다. 무제한까지 넣으면 사용량이 훨씬 큰 집단이 섞여 H가 크게 달라진다.
H의 자유도는 집단 수 − 1 = 2인 카이제곱 분포로 p-value를 낸다. 사용량은 오른쪽으로 긴 꼬리라 평균을 비교하는 일원분산분석으로 하면 이 데이터에서는 판정이 갈린다.""",
))


# ---------------------------------------------------------------- x3-15 Pearson vs Spearman
def gen_15(rng):
    n = 70
    ep = rng.integers(20, 181, n)
    z = 0.35 * (ep - 100) / 46 + rng.normal(0, 1, n)
    com = np.exp(5.2 + 0.55 * z)
    hits = rng.choice(n, 3, replace=False)
    com[hits] = com[hits] * rng.uniform(6, 12, 3)
    genre = rng.choice(["로맨스", "액션", "판타지", "일상", "스릴러"], n)
    return pd.DataFrame({
        "title_id": [f"WT{i:03d}" for i in range(1, n + 1)],
        "genre": genre, "episodes": ep, "avg_comments": np.round(com).astype(int),
    })


def chk_15(ns, df):
    sp = stats.spearmanr(df.episodes, df.avg_comments)
    if not away(ns["a2"], gap=0.01) or not away(ns["a3"], gap=0.01):
        return False
    # 두 상관 검정의 판정이 서로 달라야 한다
    return (ns["a2"] < 0.05) != (ns["a3"] < 0.05) and 0.001 < min(ns["a2"], ns["a3"]) and abs(sp.statistic) > 0.15


P.append(dict(
    no="15", gen=gen_15, chk=chk_15,
    title="피어슨·스피어만 상관 검정 — 웹툰 연재 회차와 댓글 수",
    statement="""어느 웹툰 플랫폼이 완결 작품 70편의 총 연재 회차 수와 회당 평균 댓글 수를 정리했다. 데이터 `x3_15.csv`의 칼럼은 다음과 같다.

| 칼럼 | 설명 |
|---|---|
| title_id | 작품 ID |
| genre | 장르 |
| episodes | 총 연재 회차 수 |
| avg_comments | 회당 평균 댓글 수 |

episodes와 avg_comments 사이에 상관관계가 있는지 두 가지 상관계수로 검정하시오.

- 두 검정 모두 귀무가설은 "모상관계수 = 0", 대립가설은 "모상관계수 ≠ 0"(양측 검정)이다.
- 스피어만 순위상관은 동점에 평균 순위를 준다.
- 두 검정의 p-value는 모두 t분포 근사(검정통계량 t = r√(n−2)/√(1−r²), 자유도 n−2)로 구한다.
- 유의수준은 0.05이다.

① 피어슨 상관계수를 구하시오.

② 피어슨 상관계수 검정의 p-value를 구하시오.

③ 스피어만 순위상관계수 검정의 p-value를 구하시오.

【제출 형식】 ① 반올림하여 소수 셋째 자리까지 ② 반올림하여 소수 넷째 자리까지 ③ 반올림하여 소수 넷째 자리까지""",
    formats=[F3, F4, F4],
    solution="""import pandas as pd
from scipy import stats

df = pd.read_csv('data/x3_15.csv')

pr = stats.pearsonr(df['episodes'], df['avg_comments'])
sr = stats.spearmanr(df['episodes'], df['avg_comments'])
a1 = pr.statistic
a2 = pr.pvalue
a3 = sr.pvalue

print(round(a1, 3))
print(round(a2, 4))
print(round(a3, 4))
""",
    explain="""피어슨은 값 그대로의 선형 관계를, 스피어만은 순위의 관계를 본다. 댓글 수가 몇 작품에서 수천 단위로 튀어 피어슨 상관계수가 그 몇 점에 끌려가 부호까지 음수로 바뀐다. 순위로 보면 회차가 많을수록 댓글이 많은 양의 관계(ρ ≈ 0.27)라 이 데이터에서는 두 검정의 판정이 서로 다르다.
피어슨 p-value는 t = r√(n−2)/√(1−r²), 자유도 n−2의 t분포에서 나온다. 스피어만 p-value도 순위상관계수로 같은 t 근사를 쓴다. `df[['episodes', 'avg_comments']].corr(method='spearman')`은 계수만 주고 p-value는 주지 않는다.""",
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


def ok_margins(ns, prob):
    for k, f in zip(KEYS, prob["formats"]):
        if f in DIG and not margin_ok(ns[k], DIG[f]):
            return False
        if f == FD and abs(ns[prob["pkey"]] - 0.05) < 0.008:
            return False
    return True


def check_csv(df):
    for c in df.columns:
        if df[c].dtype == object:
            s = df[c].dropna().astype(str)
            if s.str.contains('[,"]').any():
                return False
    return 60 <= len(df) <= 400


def main():
    out = []
    for i, prob in enumerate(P, start=1):
        prob["file"] = f"x3_{prob['no']}.csv"
        assert prob["no"] == f"{i:02d}"
        for seed in range(3000):
            rng = np.random.default_rng(seed + 1000 * i + 70000)
            df = prob["gen"](rng)
            if not check_csv(df):
                continue
            ns, text, df2 = run_solution(prob["solution"], prob["file"], df)
            if not ok_margins(ns, prob):
                continue
            if not prob["chk"](ns, df2):
                continue
            break
        else:
            raise SystemExit(f"x3-{prob['no']}: no seed")
        k = len(prob["formats"])
        vals = [fmt(ns[key], f) for key, f in zip(KEYS[:k], prob["formats"])]
        printed = text.strip().splitlines()
        assert len(printed) == k and all(
            (float(o) == float(v)) if prob["formats"][j] not in (FD, FPAIR) else o == v
            for j, (o, v) in enumerate(zip(printed, vals))), (prob["no"], printed, vals)
        d = os.path.join(REPO, SET)
        os.makedirs(d, exist_ok=True)
        df.to_csv(os.path.join(d, prob["file"]), index=False)
        print(f"x3-{prob['no']}", "seed", seed, "rows", len(df), vals, "| raw", [ns[key] for key in KEYS[:k]])
        out.append({
            "id": f"x3-{prob['no']}", "set": SET, "type": 3, "no": prob["no"], "points": 15,
            "title": prob["title"], "statement": prob["statement"],
            "files": [f"{SET}/{prob['file']}"],
            "starter": f"import pandas as pd\ndf = pd.read_csv('data/{prob['file']}')\n",
            "answers": [{"label": l, "format": f, "value": v}
                        for l, f, v in zip(LABELS, prob["formats"], vals)],
            "solution": prob["solution"].rstrip("\n"),
            "explain": prob["explain"],
        })
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", OUT_JSON, len(out))


if __name__ == "__main__":
    main()
