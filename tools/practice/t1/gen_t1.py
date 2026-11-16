# 작업형1 실습 문제 15개 생성기. 데이터 CSV와 parts/t1.json을 만든다.
# 각 문제: make(seed) -> df, check(df) -> (ok, raw_values, info). ok인 첫 시드를 쓴다.
import json, math, os, sys
import numpy as np
import pandas as pd

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'bigdata-analysis-engineer', 'practice'))


def near_half(x, d, tol=0.06):
    v = abs(x) * 10 ** d
    f = v - math.floor(v)
    return abs(f - 0.5) < tol


def near_int(x, tol=0.01):
    f = abs(x) - math.floor(abs(x))
    return f < tol or f > 1 - tol


def fmt(x, d):
    return f"{x:.{d}f}"


def table(rows):
    s = "| 칼럼 | 설명 |\n|---|---|\n"
    return s + "\n".join(f"| {a} | {b} |" for a, b in rows)


PROBLEMS = []


def problem(fn):
    PROBLEMS.append(fn)
    return fn


# ---------------------------------------------------------------- m1-1-1
@problem
def m1_1():
    def make(seed):
        rng = np.random.default_rng(seed)
        n = 340
        region = rng.choice(['서울', '경기', '부산', '대구', '광주'], n, p=[.3, .3, .15, .13, .12])
        stype = rng.choice(['직영', '가맹'], n, p=[.35, .65])
        visitors = rng.integers(600, 5200, n)
        visitors[rng.choice(n, 6, replace=False)] = 1500
        rate = rng.beta(4, 8, n)
        buyers = np.round(visitors * rate).astype(int)
        sales = np.round(buyers * rng.normal(0.95, 0.15, n) * 1.2).astype(int)
        staff = rng.integers(3, 13, n)
        return pd.DataFrame({'store_id': [f'S{i:03d}' for i in range(1, n + 1)], 'region': region,
                             'store_type': stype, 'visitors': visitors, 'buyers': buyers,
                             'sales': sales, 'staff': staff})

    def solve(df, trap=None):
        cond = df['region'].isin(['서울', '경기']) & (df['store_type'] == '가맹')
        if trap != 'no_visit':
            cond &= (df['visitors'] >= 1500)
        d = df[cond].copy()
        d['conv'] = d['buyers'] / d['visitors']
        d = d.sort_values(['conv', 'store_id'], ascending=[False, True])
        return d

    def check(df):
        d = solve(df)
        c = d['conv'].values
        ok = all(abs(c[i] - c[i + 1]) > 1e-4 for i in range(2, 6))
        ans = d.iloc[4]['store_id']
        ok &= solve(df, 'no_visit').iloc[4]['store_id'] != ans
        # 경계값 1500인 지점이 상위권에 끼면 >= 와 > 를 가르는 함정이 생긴다
        return ok, [ans], {'top6': list(zip(d['store_id'][:6], np.round(c[:6], 5)))}

    statement = (
        "어느 편의점 체인의 지점별 한 달 실적 데이터이다.\n\n"
        + table([('store_id', '지점 ID'), ('region', '지역'), ('store_type', '운영 형태(직영/가맹)'),
                 ('visitors', '방문객 수(명)'), ('buyers', '구매 고객 수(명)'), ('sales', '매출(만 원)'),
                 ('staff', '근무 인원(명)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) region이 서울 또는 경기이고, store_type이 가맹이며, visitors가 1500 이상인 지점만 남긴다.\n"
        "- 2) 구매전환율 = buyers / visitors 를 계산한다.\n"
        "- 3) 구매전환율이 높은 순으로 정렬한다. 구매전환율이 같으면 store_id 오름차순으로 둔다.\n\n"
        "정렬 결과 5번째 지점의 store_id를 구하시오.\n\n"
        "【제출 형식】 store_id 값 그대로 (예: S001)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_1.csv')\n"
        "cond = df['region'].isin(['서울', '경기']) & (df['store_type'] == '가맹') & (df['visitors'] >= 1500)\n"
        "d = df[cond].copy()\n"
        "d['conv'] = d['buyers'] / d['visitors']\n"
        "d = d.sort_values(['conv', 'store_id'], ascending=[False, True])\n"
        "print(d.iloc[4]['store_id'])\n"
    )
    explain = (
        "세 조건을 & 로 묶고 지역은 isin으로 거른다. visitors는 '1500 이상'이라 >= 를 쓴다(1500인 지점이 데이터에 있다).\n\n"
        "sort_values에 두 칼럼과 ascending=[False, True]를 주면 동률 처리까지 한 번에 된다. "
        "5번째는 0부터 세는 iloc[4]다. 방문객 조건을 빠뜨리면 다른 지점이 나온다."
    )
    return dict(make=make, check=check, title='가맹 지점 구매전환율 5위 지점',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', 'store_id 값 그대로', None)])


# ---------------------------------------------------------------- m1-1-2
@problem
def m1_2():
    teams = ['상담1팀', '상담2팀', '상담3팀', '상담4팀', '상담5팀']
    means = [330, 352, 401, 344, 371]

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 900
        ti = rng.integers(0, 5, n)
        day = rng.integers(0, 61, n)
        sec = rng.integers(9 * 3600, 20 * 3600, n)
        start = pd.Timestamp('2025-09-01') + pd.to_timedelta(day, 'D') + pd.to_timedelta(sec, 's')
        dur = np.round(np.array(means)[ti] * rng.lognormal(0, 0.45, n)).astype(int) + 30
        end = start + pd.to_timedelta(dur, 's')
        cat = rng.choice(['요금', '해지', '기기', '배송', '기타'], n)
        df = pd.DataFrame({'call_id': [f'C{i:05d}' for i in range(1, n + 1)], 'team': np.array(teams)[ti],
                           'category': cat, 'start_time': start.strftime('%Y-%m-%d %H:%M:%S'),
                           'end_time': end.strftime('%Y-%m-%d %H:%M:%S')})
        return df.sort_values('start_time').reset_index(drop=True).assign(
            call_id=lambda x: [f'C{i:05d}' for i in range(1, len(x) + 1)])

    def check(df):
        s = pd.to_datetime(df['start_time']); e = pd.to_datetime(df['end_time'])
        m = ((e - s).dt.total_seconds() / 60).groupby(df['team']).mean().sort_values(ascending=False)
        top = m.index[0]
        ok = (m.iloc[0] - m.iloc[1] > 0.1) and not near_half(m.iloc[0], 2)
        w = int(((df['team'] == top) & (s.dt.dayofweek >= 5)).sum())
        return ok, [fmt(m.iloc[0], 2), str(w)], {'means': m.round(4).to_dict(), 'top': top}

    statement = (
        "어느 통신사 고객센터의 상담 기록이다. 한 행이 상담 한 건이다.\n\n"
        + table([('call_id', '상담 ID'), ('team', '상담팀'), ('category', '문의 유형'),
                 ('start_time', '상담 시작 시각 (YYYY-MM-DD HH:MM:SS)'), ('end_time', '상담 종료 시각 (YYYY-MM-DD HH:MM:SS)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) start_time과 end_time을 날짜시간형으로 바꾼다.\n"
        "- 2) 상담시간(분) = (end_time − start_time)을 초로 바꾼 값 / 60 으로 계산한다.\n"
        "- 3) team별 상담시간 평균을 구한다.\n\n"
        "① 상담시간 평균이 가장 긴 팀의 평균 상담시간(분)을 구하시오.\n\n"
        "② ①에서 찾은 팀의 상담 중, start_time이 주말(토요일·일요일)인 상담 건수를 구하시오.\n\n"
        "【제출 형식】 ① 반올림하여 소수 둘째 자리까지 ② 정수(건수)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_2.csv')\n"
        "df['start_time'] = pd.to_datetime(df['start_time'])\n"
        "df['end_time'] = pd.to_datetime(df['end_time'])\n"
        "df['minutes'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60\n"
        "m = df.groupby('team')['minutes'].mean()\n"
        "top = m.idxmax()\n"
        "print(round(m.max(), 2))\n"
        "w = df[(df['team'] == top) & (df['start_time'].dt.dayofweek >= 5)]\n"
        "print(len(w))\n"
    )
    explain = (
        "두 시각의 차는 Timedelta이고 dt.total_seconds()로 초를 얻어 60으로 나눈다. "
        "dt.minute는 시각의 '분' 자리일 뿐 경과 분이 아니니 쓰면 안 된다.\n\n"
        "②는 ①의 팀(idxmax)을 그대로 받아 쓴다. dt.dayofweek는 월요일 0 ~ 일요일 6이라 주말은 >= 5다."
    )
    return dict(make=make, check=check, title='상담팀별 평균 상담시간과 주말 상담 건수',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '반올림하여 소수 둘째 자리까지', None), ('②', '정수(건수)', None)])


# ---------------------------------------------------------------- m1-1-3
@problem
def m1_3():
    wards = ['내과', '외과', '정형외과', '신경과']
    mu = [206, 188, 182, 217]

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 520
        wi = rng.integers(0, 4, n)
        chol = np.round(np.array(mu)[wi] + rng.normal(0, 27, n), 1)
        idx = rng.choice(n, 9, replace=False)
        chol[idx[:6]] = np.round(rng.uniform(305, 360, 6), 1)
        chol[idx[6:]] = np.round(rng.uniform(92, 110, 3), 1)
        chol = chol.astype(float)
        na = rng.choice(np.setdiff1d(np.arange(n), idx), 46, replace=False)
        chol[na] = np.nan
        age = rng.integers(25, 86, n)
        sbp = np.round(115 + 0.35 * age + rng.normal(0, 12, n)).astype(int)
        return pd.DataFrame({'patient_id': [f'P{i:04d}' for i in range(1, n + 1)],
                             'ward': np.array(wards)[wi], 'age': age, 'sbp': sbp, 'chol': chol})

    def solve(df, how='ward'):
        c = df['chol'].copy()
        if how == 'ward':
            c = c.fillna(df.groupby('ward')['chol'].transform('median'))
        else:
            c = c.fillna(c.median())
        m, s = c.mean(), c.std()
        lo, hi = m - 2 * s, m + 2 * s
        return c, lo, hi, int(((c < lo) | (c > hi)).sum())

    def check(df):
        c, lo, hi, cnt = solve(df)
        margin = min((c - lo).abs().min(), (c - hi).abs().min())
        ok = margin > 0.15
        cnt0 = int(((c < c.mean() - 2 * c.std(ddof=0)) | (c > c.mean() + 2 * c.std(ddof=0))).sum())
        _, _, _, cnt_all = solve(df, 'all')
        return ok, [str(cnt)], {'lo': lo, 'hi': hi, 'margin': margin, 'ddof0': cnt0, 'overall_median': cnt_all}

    statement = (
        "어느 병원의 외래 환자 혈액검사 데이터이다. chol(총콜레스테롤)에 결측치가 있다.\n\n"
        + table([('patient_id', '환자 ID'), ('ward', '진료과'), ('age', '나이'),
                 ('sbp', '수축기 혈압(mmHg)'), ('chol', '총콜레스테롤(mg/dL)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) chol의 결측치를 같은 ward의 chol 중앙값으로 채운다(중앙값은 결측을 뺀 값으로 계산).\n"
        "- 2) 결측을 채운 chol 전체의 평균과 표준편차를 구한다. 표준편차는 표본표준편차(n−1로 나눔)를 쓴다.\n"
        "- 3) chol이 (평균 − 2×표준편차)보다 작거나 (평균 + 2×표준편차)보다 큰 행을 이상치로 본다.\n\n"
        "이상치인 행의 수를 구하시오.\n\n"
        "【제출 형식】 정수(행 수)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_3.csv')\n"
        "df['chol'] = df['chol'].fillna(df.groupby('ward')['chol'].transform('median'))\n"
        "m = df['chol'].mean()\n"
        "s = df['chol'].std()\n"
        "out = df[(df['chol'] < m - 2 * s) | (df['chol'] > m + 2 * s)]\n"
        "print(len(out))\n"
    )
    explain = (
        "groupby('ward')['chol'].transform('median')은 각 행 자리에 그 행 진료과의 중앙값을 놓아 주므로 fillna에 바로 넣을 수 있다. "
        "전체 중앙값으로 채우면 평균·표준편차가 달라진다.\n\n"
        "pandas의 std()는 기본이 ddof=1(표본표준편차)이다. numpy의 np.std는 ddof=0이니 섞어 쓰지 않는다."
    )
    return dict(make=make, check=check, title='진료과 중앙값 대체 후 2SD 이상치 개수',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '정수(행 수)', None)])


# ---------------------------------------------------------------- m2-1-1
@problem
def m2_1():
    centers = ['이천', '평택', '김해', '칠곡', '광주', '대전']

    def make(seed):
        rng = np.random.default_rng(seed)
        yms = [f'{y}-{m:02d}' for y in (2024, 2025) for m in range(1, 13)]
        rows = []
        base_delay = dict(zip(centers, [0.041, 0.046, 0.039, 0.044, 0.047, 0.043]))
        for c in centers:
            for ym in yms:
                shipped = int(rng.integers(2500, 9500))
                # 물량이 많은 달에 지연율이 낮아지는 센터가 있어 '평균의 비율'과 '합의 비율'이 갈린다
                dr = base_delay[c] + rng.normal(0, 0.006)
                if c in ('광주', '평택'):
                    dr += (5500 - shipped) / 5500 * 0.012
                delayed = int(round(shipped * max(dr, 0.005)))
                returned = int(round(shipped * rng.uniform(0.008, 0.035)))
                rows.append((c, ym, shipped, delayed, returned))
        return pd.DataFrame(rows, columns=['center', 'ym', 'shipped', 'delayed', 'returned'])

    def check(df):
        r = df['delayed'] / df['shipped']
        g = r.groupby(df['center']).mean().sort_values(ascending=False)
        top = g.index[0]
        gs = (df.groupby('center')['delayed'].sum() / df.groupby('center')['shipped'].sum()).idxmax()
        d = df[df['center'] == top].copy()
        d['rr'] = d['returned'] / d['shipped']
        d = d.sort_values(['rr', 'ym'], ascending=[False, True])
        rr = d['rr'].values
        ok = (g.iloc[0] - g.iloc[1] > 0.0005) and gs != top and abs(rr[2] - rr[1]) > 1e-5 and abs(rr[2] - rr[3]) > 1e-5
        return ok, [top, str(int(d.iloc[2]['delayed']))], {'g': g.round(5).to_dict(), 'sumratio_top': gs}

    statement = (
        "어느 택배사 물류센터 6곳의 2024~2025년 월별 처리 실적이다.\n\n"
        + table([('center', '물류센터'), ('ym', '연-월 (YYYY-MM)'), ('shipped', '출고 건수'),
                 ('delayed', '배송 지연 건수'), ('returned', '반품 건수')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) 행마다 지연율 = delayed / shipped 를 계산한다.\n"
        "- 2) center별로 월별 지연율의 평균을 구한다(지연 건수 합을 출고 건수 합으로 나누는 것이 아니다).\n\n"
        "① 월별 지연율의 평균이 가장 높은 center를 구하시오.\n\n"
        "② ①의 center 행만 남기고 반품률 = returned / shipped 를 계산한다. 반품률이 높은 순으로 정렬했을 때(같으면 ym이 빠른 순) "
        "3번째 행의 delayed 값을 구하시오.\n\n"
        "【제출 형식】 ① 센터 이름 그대로 (예: 이천) ② 정수"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_1.csv')\n"
        "df['delay_rate'] = df['delayed'] / df['shipped']\n"
        "top = df.groupby('center')['delay_rate'].mean().idxmax()\n"
        "print(top)\n"
        "d = df[df['center'] == top].copy()\n"
        "d['return_rate'] = d['returned'] / d['shipped']\n"
        "d = d.sort_values(['return_rate', 'ym'], ascending=[False, True])\n"
        "print(d.iloc[2]['delayed'])\n"
    )
    explain = (
        "비율을 행마다 만든 뒤 groupby().mean().idxmax()로 센터 이름을 바로 얻는다. "
        "지연 건수 합 / 출고 건수 합으로 계산하면 물량이 큰 달의 비중이 커져 다른 센터가 1위가 된다. 지문이 정한 '월별 지연율의 평균'을 따른다.\n\n"
        "②는 ①의 이름으로 다시 거르고, 정렬 후 iloc[2]로 3번째 행을 읽어 다른 칼럼(delayed)을 답한다."
    )
    return dict(make=make, check=check, title='지연율 최고 센터의 반품률 3위 달 지연 건수',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '센터 이름 그대로', None), ('②', '정수', None)])


# ---------------------------------------------------------------- m2-1-2
@problem
def m2_2():
    pos = ['화면이 선명해요', '배송이 빨라서 좋았습니다', '포장이 꼼꼼했어요', '가격 대비 만족합니다',
           '재구매 의사 있어요', '디자인이 예뻐요', '소리가 깨끗합니다', '설치가 간단했어요', '부모님 선물로 드렸어요']
    neg = ['충전이 너무 느리고 발열이 심해요', '연결이 자주 끊겨서 쓰기 불편합니다', '교환을 요청했는데 아직 답변이 없네요',
           '설명서가 부실해서 설정을 못 하겠어요', '생각보다 무겁고 버튼이 뻑뻑합니다', '한 달 만에 화면에 줄이 생겼어요',
           '배송이 일주일이나 걸렸어요', '포장 상자가 찌그러져 왔습니다']
    mid = ['그냥 그래요', '쓸만합니다', '기대만큼은 아니에요', '보통입니다']

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 640
        cats = rng.choice(['DG', 'KT', 'LV', 'BT'], n, p=[.35, .25, .2, .2])
        sub = {'DG': ['TV', 'PHN', 'EAR', 'LAP'], 'KT': ['PAN', 'POT', 'KNF'], 'LV': ['LMP', 'RUG'], 'BT': ['CRM', 'SRM']}
        codes = [f"{c}-{rng.choice(sub[c])}-{rng.integers(1, 9999):04d}" for c in cats]
        rating = rng.choice([1, 2, 3, 4, 5], n, p=[.1, .12, .18, .3, .3])
        texts = []
        for r in rating:
            if r >= 4:
                k = rng.integers(1, 4); parts = list(rng.choice(pos, k, replace=False))
            elif r <= 2:
                k = rng.integers(1, 3); parts = list(rng.choice(neg, k, replace=False))
                if rng.random() < 0.5:
                    parts.append(rng.choice(mid))
            else:
                parts = [rng.choice(mid)] + list(rng.choice(pos + neg, rng.integers(0, 2), replace=False))
            t = ' '.join(parts)
            if rng.random() < 0.18:  # 띄어쓰기가 두 칸인 리뷰
                w = t.split(' ')
                j = rng.integers(1, len(w)) if len(w) > 1 else 0
                if j:
                    w[j] = ' ' + w[j]
                t = ' '.join(w)
            texts.append(t)
        return pd.DataFrame({'review_id': [f'R{i:04d}' for i in range(1, n + 1)], 'product_code': codes,
                             'rating': rating, 'review': texts})

    def check(df):
        cat = df['product_code'].str.split('-').str[0]
        d = df[cat == 'DG']
        w = d['review'].str.split().str.len()
        v = w[d['rating'] >= 4].mean() - w[d['rating'] <= 2].mean()
        w2 = d['review'].str.split(' ').str.len()
        v2 = w2[d['rating'] >= 4].mean() - w2[d['rating'] <= 2].mean()
        ok = (not near_half(v, 3)) and round(v, 3) != round(v2, 3) and df['review'].str.contains('  ').any()
        return ok, [fmt(v, 3)], {'raw': v, 'split_space': v2, 'nDG': len(d)}

    statement = (
        "어느 쇼핑몰의 상품 리뷰 데이터이다. product_code는 '대분류-소분류-번호' 형식이다.\n\n"
        + table([('review_id', '리뷰 ID'), ('product_code', '상품 코드 (예: DG-TV-0412)'),
                 ('rating', '평점(1~5)'), ('review', '리뷰 본문')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) product_code를 '-'로 나눈 첫 부분을 대분류로 쓴다. 대분류가 DG인 리뷰만 남긴다.\n"
        "- 2) review의 단어 수를 공백 기준으로 센다. 공백이 두 칸 이상 연속된 곳은 공백 하나로 본다.\n"
        "- 3) rating이 4 이상인 리뷰의 평균 단어 수(A)와 rating이 2 이하인 리뷰의 평균 단어 수(B)를 구한다.\n\n"
        "A − B 를 구하시오(음수이면 음수 그대로).\n\n"
        "【제출 형식】 반올림하여 소수 셋째 자리까지"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_2.csv')\n"
        "df['cat'] = df['product_code'].str.split('-').str[0]\n"
        "d = df[df['cat'] == 'DG'].copy()\n"
        "d['words'] = d['review'].str.split().str.len()\n"
        "a = d[d['rating'] >= 4]['words'].mean()\n"
        "b = d[d['rating'] <= 2]['words'].mean()\n"
        "print(round(a - b, 3))\n"
    )
    explain = (
        "str.split('-').str[0]으로 코드 앞부분을 꺼낸다. 단어 수는 인자 없는 str.split()을 써야 연속 공백이 하나로 처리된다. "
        "str.split(' ')는 두 칸 공백 사이에 빈 문자열을 만들어 단어를 하나 더 센다(이 데이터에는 두 칸 공백 리뷰가 섞여 있다).\n\n"
        "빼는 순서가 A − B로 정해져 있어 결과는 음수다. 절댓값을 취하지 않는다."
    )
    return dict(make=make, check=check, title='디지털 상품 리뷰의 평점별 단어 수 차이',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '반올림하여 소수 셋째 자리까지', None)])


# ---------------------------------------------------------------- m2-1-3
@problem
def m2_3():
    def make(seed):
        rng = np.random.default_rng(seed)
        n = 420
        ut = rng.choice(['사무', '상업', '교육'], n, p=[.45, .3, .25])
        area = np.round(np.exp(rng.normal(8.2, 0.7, n)), 1)
        inten = np.where(ut == '사무', 180, np.where(ut == '상업', 260, 120))
        energy = np.round(area * inten * rng.lognormal(0, 0.35, n)).astype(int)
        temp = np.round(rng.normal(14.5, 3, n), 1)
        return pd.DataFrame({'building_id': [f'B{i:03d}' for i in range(1, n + 1)], 'use_type': ut,
                             'floor_area': area, 'energy_kwh': energy, 'avg_temp': temp})

    def check(df):
        mm = lambda s: (s - s.min()) / (s.max() - s.min())
        e = df['use_type'] == '교육'
        v = mm(df['energy_kwh'])[e].std() - mm(df['floor_area'])[e].std()
        v0 = mm(df['energy_kwh'])[e].std(ddof=0) - mm(df['floor_area'])[e].std(ddof=0)
        sub = df[e]
        vf = mm(sub['energy_kwh']).std() - mm(sub['floor_area']).std()
        ok = (not near_half(v, 4, 0.1)) and round(v, 4) != round(v0, 4)
        return ok, [fmt(v, 4)], {'raw': v, 'ddof0': v0, 'filter_first': vf}

    statement = (
        "어느 지자체가 관리하는 공공건물의 연간 에너지 사용량 데이터이다.\n\n"
        + table([('building_id', '건물 ID'), ('use_type', '용도(사무/상업/교육)'), ('floor_area', '연면적(㎡)'),
                 ('energy_kwh', '연간 전력 사용량(kWh)'), ('avg_temp', '연평균 기온(℃)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) 전체 데이터(420개 건물)를 기준으로 energy_kwh와 floor_area를 각각 Min-Max 정규화한다. (x − 최솟값) / (최댓값 − 최솟값)\n"
        "- 2) use_type이 교육인 건물만 남긴다.\n"
        "- 3) 남은 건물에서 정규화한 energy_kwh의 표준편차(A)와 정규화한 floor_area의 표준편차(B)를 구한다. 표준편차는 표본표준편차(n−1로 나눔)를 쓴다.\n\n"
        "A − B 를 구하시오.\n\n"
        "【제출 형식】 반올림하여 소수 넷째 자리까지"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_3.csv')\n"
        "for c in ['energy_kwh', 'floor_area']:\n"
        "    df[c + '_mm'] = (df[c] - df[c].min()) / (df[c].max() - df[c].min())\n"
        "e = df[df['use_type'] == '교육']\n"
        "print(round(e['energy_kwh_mm'].std() - e['floor_area_mm'].std(), 4))\n"
    )
    explain = (
        "정규화 기준(최솟값·최댓값)은 전체 데이터에서 잡고, 표준편차는 교육 건물에서만 낸다. 순서를 바꿔 교육 건물만으로 정규화하면 값이 달라진다.\n\n"
        "sklearn의 MinMaxScaler를 써도 되지만 결과가 numpy 배열이라 np.std로 이어 쓰기 쉽다. np.std는 기본 ddof=0이라 "
        "지문의 표본표준편차와 다르다(넷째 자리가 바뀐다). pandas Series의 std()는 ddof=1이다."
    )
    return dict(make=make, check=check, title='교육 건물의 정규화 사용량과 면적 표준편차 차이',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '반올림하여 소수 넷째 자리까지', None)])


# ---------------------------------------------------------------- m3-1-1
@problem
def m3_1():
    classes = ['A반', 'B반', 'C반', 'D반', 'E반', 'F반']

    def make(seed):
        rng = np.random.default_rng(seed)
        rows = []
        eff = rng.normal(0, 3.5, 6)
        sid = 1
        for ci, c in enumerate(classes):
            for _ in range(60):
                ab = rng.normal(70 + eff[ci], 11)
                mid = int(np.clip(round(ab + rng.normal(0, 7)), 0, 100))
                fin = int(np.clip(round(ab + rng.normal(0, 8)), 0, 100))
                asg = int(np.clip(round(ab + 5 + rng.normal(0, 6)), 0, 100))
                att = int(np.clip(round(52 + (ab - 70) * 0.25 + rng.normal(0, 3)), 30, 60))
                rows.append((f'ST{sid:04d}', c, mid, fin, asg, att))
                sid += 1
        df = pd.DataFrame(rows, columns=['student_id', 'class', 'mid', 'final', 'assignment', 'attendance'])
        return df.sample(frac=1, random_state=seed).reset_index(drop=True)

    def check(df):
        tot10 = df['mid'] * 3 + df['final'] * 4 + df['assignment'] * 3  # 정수로 동률 확인
        cm = (tot10 / 10).groupby(df['class']).mean().sort_values(ascending=False)
        second = cm.index[1]
        d = df.assign(t=tot10)[df['class'] == second].sort_values(['t', 'student_id'], ascending=[False, True])
        t = d['t'].values
        ok = (cm.iloc[0] - cm.iloc[1] > 0.3) and (cm.iloc[1] - cm.iloc[2] > 0.3) and len(set(t[:6])) == 6
        return ok, [second, str(int(d.iloc[3]['attendance']))], {'cm': cm.round(3).to_dict(), 't': t[:6] / 10}

    statement = (
        "어느 학원의 한 학기 성적 데이터이다. 반마다 60명씩이다.\n\n"
        + table([('student_id', '학생 ID'), ('class', '반'), ('mid', '중간고사 점수'), ('final', '기말고사 점수'),
                 ('assignment', '과제 점수'), ('attendance', '출석 일수')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) 총점 = mid × 0.3 + final × 0.4 + assignment × 0.3 을 계산한다.\n"
        "- 2) class별 총점 평균을 구한다.\n\n"
        "① 총점 평균이 두 번째로 높은 반을 구하시오.\n\n"
        "② ①의 반 학생을 총점이 높은 순으로 정렬했을 때(총점이 같으면 student_id 오름차순) 4번째 학생의 attendance를 구하시오.\n\n"
        "【제출 형식】 ① 반 이름 그대로 (예: A반) ② 정수"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_1.csv')\n"
        "df['total'] = df['mid'] * 0.3 + df['final'] * 0.4 + df['assignment'] * 0.3\n"
        "cm = df.groupby('class')['total'].mean().sort_values(ascending=False)\n"
        "second = cm.index[1]\n"
        "print(second)\n"
        "d = df[df['class'] == second].sort_values(['total', 'student_id'], ascending=[False, True])\n"
        "print(d.iloc[3]['attendance'])\n"
    )
    explain = (
        "두 번째로 높은 반은 평균을 내림차순 정렬한 뒤 index[1]로 꺼낸다(nlargest(2).index[-1]도 같다).\n\n"
        "②는 ①의 반으로 다시 거른 뒤 총점으로 정렬하고 iloc[3]의 attendance를 읽는다. 총점이 아니라 출석 일수를 답하는 문제라 "
        "읽는 칼럼을 헷갈리지 않는다."
    )
    return dict(make=make, check=check, title='총점 2위 반에서 4등 학생의 출석 일수',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '반 이름 그대로', None), ('②', '정수', None)])


# ---------------------------------------------------------------- m3-1-2
@problem
def m3_2():
    facs = ['수영장', '테니스장', '풋살장', '배드민턴장', '탁구장']
    # 월(1~12)별 시설 이용 경향. 여름엔 수영장, 봄·가을엔 야외 코트가 붐빈다
    season = {'수영장': [.6, .6, .7, .8, 1.0, 1.4, 1.9, 2.0, 1.2, .8, .6, .6],
              '테니스장': [.5, .6, 1.0, 1.3, 1.4, 1.0, .8, .8, 1.3, 1.4, 1.0, .6],
              '풋살장': [.7, .7, 1.0, 1.2, 1.2, 1.0, .8, .8, 1.1, 1.2, 1.0, .8],
              '배드민턴장': [1.2, 1.2, 1.0, .9, .9, 1.0, 1.0, 1.0, .9, 1.0, 1.1, 1.3],
              '탁구장': [1.3, 1.2, 1.0, .9, .8, .9, 1.0, 1.0, .9, 1.0, 1.2, 1.3]}
    size = {'수영장': (4, 15), '테니스장': (2, 5), '풋살장': (8, 13), '배드민턴장': (2, 7), '탁구장': (2, 5)}

    def make(seed):
        rng = np.random.default_rng(seed)
        days = pd.date_range('2024-03-01', '2025-10-31', freq='D')
        n = 1480
        fi = rng.choice(len(facs), n, p=[.24, .18, .2, .2, .18])
        f = np.array(facs)[fi]
        mw = np.array([season[x] for x in facs])  # 5 x 12
        di = np.empty(n, dtype=int)
        mon = days.month.values - 1
        grow = np.where(days.year == 2025, 1.1, 1.0)
        for k in range(len(facs)):
            w = mw[k][mon] * grow
            idx = np.where(fi == k)[0]
            di[idx] = rng.choice(len(days), len(idx), p=w / w.sum())
        ppl = np.array([int(rng.integers(*size[x])) for x in f])
        df = pd.DataFrame({'use_date': days[di].strftime('%Y-%m-%d'), 'facility': f, 'people': ppl})
        df = df.sort_values(['use_date', 'facility']).reset_index(drop=True)
        df.insert(0, 'booking_id', [f'BK{i:05d}' for i in range(1, n + 1)])
        return df

    def solve(df):
        ym = pd.to_datetime(df['use_date']).dt.to_period('M')
        s = df.groupby(ym)['people'].sum().sort_values(ascending=False)
        ym2 = s.index[1]
        cur = df[ym == ym2].groupby('facility')['people'].sum()
        bef = df[ym == ym2 - 1].groupby('facility')['people'].sum()
        return s, ym2, cur, bef

    def check(df):
        s, ym2, cur, bef = solve(df)
        dt = pd.to_datetime(df['use_date'])
        sm = df.groupby(dt.dt.month)['people'].sum().sort_values(ascending=False)
        inc = (cur - bef).sort_values(ascending=False)
        ok = len(set(s.values[:4])) == 4 and len(cur) == 5 and len(bef) == 5 and ym2 - 1 in set(s.index)
        ok &= inc.iloc[0] - inc.iloc[1] >= 5                  # 증가량 1위가 분명하다
        ok &= sm.iloc[1] != s.iloc[1]                         # 월만으로 묶으면 ①이 달라진다
        ok &= cur.idxmax() != inc.index[0]                    # 그 달 합계 1위와 증가량 1위가 다르다
        return ok, [str(int(s.iloc[1])), inc.index[0]], {'top4': {str(k): int(v) for k, v in s.head(4).items()}, 'ym2': str(ym2),
                                                        'month_only2': int(sm.index[1]), 'inc': inc.to_dict(), 'cur_top': cur.idxmax()}

    statement = (
        "어느 구청이 운영하는 공공 체육시설의 2024년 3월 ~ 2025년 10월 예약 기록이다. 한 행이 예약 한 건이다.\n\n"
        + table([('booking_id', '예약 ID'), ('use_date', '이용일 (YYYY-MM-DD)'), ('facility', '시설'),
                 ('people', '이용 인원(명)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) use_date를 날짜형으로 바꾸고 연-월(예: 2025-03)을 만든다. 같은 월이라도 연도가 다르면 다른 연-월이다.\n"
        "- 2) 연-월별 people 합계를 구한다.\n\n"
        "① people 합계가 두 번째로 큰 연-월의 people 합계를 구하시오.\n\n"
        "② ①의 연-월과 그 바로 앞 연-월(예: 2025-01의 바로 앞은 2024-12)에 대해 각각 facility별 people 합계를 구한다. "
        "증가량 = (①의 연-월 합계) − (바로 앞 연-월 합계) 가 가장 큰 facility를 구하시오. 증가량은 음수일 수도 있다.\n\n"
        "【제출 형식】 ① 정수 ② 시설 이름 그대로 (예: 수영장)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_2.csv')\n"
        "df['use_date'] = pd.to_datetime(df['use_date'])\n"
        "df['ym'] = df['use_date'].dt.to_period('M')\n"
        "s = df.groupby('ym')['people'].sum().sort_values(ascending=False)\n"
        "ym2 = s.index[1]\n"
        "print(s.iloc[1])\n"
        "cur = df[df['ym'] == ym2].groupby('facility')['people'].sum()\n"
        "bef = df[df['ym'] == ym2 - 1].groupby('facility')['people'].sum()\n"
        "print((cur - bef).idxmax())\n"
    )
    explain = (
        "dt.to_period('M')은 연과 월을 함께 가진 값이라 2024-07과 2025-07이 따로 묶인다. dt.month로 묶으면 3~10월이 두 해치씩 합쳐져 2위의 합계가 달라진다.\n\n"
        "Period에서 1을 빼면 바로 앞 달이 된다(2025-01 − 1 = 2024-12). 문자열 연-월을 쓴다면 앞 달을 직접 만들어야 하니 Period가 편하다. "
        "두 달의 facility별 합계는 인덱스가 시설 이름이라 그대로 빼면 시설끼리 맞춰 계산된다. "
        "그 달 합계가 가장 큰 시설과 증가량이 가장 큰 시설은 다르니 뺄셈을 건너뛰지 않는다."
    )
    return dict(make=make, check=check, title='이용 인원 2위 연-월과 전월 대비 증가 1위 시설',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '정수', None), ('②', '시설 이름 그대로', None)])


# ---------------------------------------------------------------- m3-1-3
@problem
def m3_3():
    dists = ['강서구', '마포구', '송파구', '노원구', '성동구']
    ppm = [960, 1340, 1490, 790, 1260]

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 720
        di = rng.integers(0, 5, n)
        area = np.round(rng.uniform(39, 135, n), 2)
        price = np.round(area * np.array(ppm)[di] * rng.lognormal(0, 0.11, n) / 10).astype(int) * 10
        idx = rng.choice(n, 12, replace=False)
        price[idx[:7]] = price[idx[:7]] * 10      # 금액 입력 실수(0 하나 더)
        price[idx[7:]] = (price[idx[7:]] / 10).astype(int)
        floor = rng.integers(1, 30, n)
        built = rng.integers(1988, 2024, n)
        return pd.DataFrame({'deal_id': [f'D{i:04d}' for i in range(1, n + 1)], 'district': np.array(dists)[di],
                             'area_m2': area, 'price': price, 'floor': floor, 'built_year': built})

    def check(df):
        p = df['price'] / df['area_m2']
        q1, q3 = p.quantile(0.25), p.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        keep = (p >= lo) & (p <= hi)
        g = p[keep].groupby(df['district'][keep]).mean()
        v = g['마포구'] - g['노원구']
        g0 = p.groupby(df['district']).mean()
        v0 = g0['마포구'] - g0['노원구']
        margin = min((p - lo).abs().min(), (p - hi).abs().min())
        ok = margin > 0.5 and not near_int(v, 0.02) and int(v) != int(v0) and (~keep).sum() >= 10
        return ok, [str(int(v))], {'raw': v, 'no_removal': v0, 'removed': int((~keep).sum()), 'fence': (lo, hi)}

    statement = (
        "서울 5개 구의 아파트 실거래 데이터이다. 일부 거래는 금액이 잘못 입력되어 있다.\n\n"
        + table([('deal_id', '거래 ID'), ('district', '자치구'), ('area_m2', '전용면적(㎡)'),
                 ('price', '거래 금액(만 원)'), ('floor', '층'), ('built_year', '준공 연도')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) ㎡당 가격 = price / area_m2 를 계산한다.\n"
        "- 2) 전체 데이터의 ㎡당 가격으로 1사분위수(Q1)와 3사분위수(Q3)를 구하고 IQR = Q3 − Q1 로 둔다. 분위수는 pandas quantile 기본값(선형 보간)을 쓴다.\n"
        "- 3) ㎡당 가격이 Q1 − 1.5×IQR 보다 작거나 Q3 + 1.5×IQR 보다 큰 거래를 제거한다.\n"
        "- 4) 남은 거래로 district별 ㎡당 가격 평균을 구한다.\n\n"
        "마포구 평균 − 노원구 평균 을 구하시오.\n\n"
        "【제출 형식】 소수점 이하를 버리고 정수로"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_3.csv')\n"
        "df['ppm'] = df['price'] / df['area_m2']\n"
        "q1 = df['ppm'].quantile(0.25)\n"
        "q3 = df['ppm'].quantile(0.75)\n"
        "iqr = q3 - q1\n"
        "d = df[(df['ppm'] >= q1 - 1.5 * iqr) & (df['ppm'] <= q3 + 1.5 * iqr)]\n"
        "g = d.groupby('district')['ppm'].mean()\n"
        "print(int(g['마포구'] - g['노원구']))\n"
    )
    explain = (
        "이상치 기준은 구별이 아니라 전체 데이터로 한 번 잡는다고 지문이 정했다. 금액이 10배·10분의 1로 잘못 들어간 거래가 울타리 밖으로 빠진다.\n\n"
        "제거하지 않고 평균을 내면 답이 크게 달라진다. 버림은 int()로 하며 결과가 양수라 math.floor와 같다."
    )
    return dict(make=make, check=check, title='IQR 이상치 제거 후 두 구의 ㎡당 가격 차이',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '소수점 이하를 버리고 정수로', None)])


# ---------------------------------------------------------------- m4-1-1
@problem
def m4_1():
    def make(seed):
        rng = np.random.default_rng(seed)
        rows = []
        eid = 1
        for c in range(1, 29):
            n = int(rng.integers(8, 33))
            p = rng.uniform(0.45, 0.92)
            for _ in range(n):
                yr = int(rng.choice([1, 2, 3, 4], p=[.35, .3, .2, .15]))
                done = int(rng.random() < p)
                rows.append((f'E{eid:05d}', f'K{c:02d}', yr, int(rng.integers(0, 15)), done))
                eid += 1
        df = pd.DataFrame(rows, columns=['enroll_id', 'course', 'year', 'forum_posts', 'completed'])
        return df.sample(frac=1, random_state=seed).reset_index(drop=True)

    def solve(df, min_n=15, dense=True):
        g = df.groupby('course')['completed'].agg(['count', 'mean'])
        g = g[g['count'] >= min_n]
        m = g['mean'].sort_values(ascending=False)
        return m.drop_duplicates() if dense else m

    def check(df):
        u = solve(df)
        v = u.iloc[2]
        no_dedup = solve(df, dense=False).iloc[2]
        no_filter = solve(df, min_n=0).iloc[2]
        m = solve(df, dense=False)
        ok = no_dedup != v and no_filter != v and m.iloc[:4].duplicated().any() and not near_half(v, 3, 0.08)
        ok &= round(no_filter, 3) != round(v, 3) and round(no_dedup, 3) != round(v, 3)
        return ok, [fmt(v, 3)], {'top6': m.head(6).round(5).to_dict(), 'no_dedup': no_dedup, 'no_filter': no_filter,
                                 'kept': len(m)}

    statement = (
        "어느 대학 온라인 교양 강좌 28개의 한 학기 수강 기록이다. 한 행이 수강 신청 한 건이다.\n\n"
        + table([('enroll_id', '수강 신청 ID'), ('course', '강좌 코드'), ('year', '학년(1~4)'),
                 ('forum_posts', '토론 게시판 글 수'), ('completed', '이수 여부(1 이수, 0 미이수)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) course별 수강 인원(행 수)과 이수율 = completed의 평균 을 구한다.\n"
        "- 2) 수강 인원이 15명 미만인 강좌는 제외한다.\n"
        "- 3) 남은 강좌에 이수율이 높은 순으로 순위를 매긴다. 이수율이 같은 강좌는 같은 순위를 받고, 다음 순위는 건너뛰지 않고 바로 이어진다"
        "(예: 이수율이 0.9, 0.8, 0.8, 0.7이면 순위는 1, 2, 2, 3).\n\n"
        "순위가 3인 강좌의 이수율을 구하시오.\n\n"
        "【제출 형식】 반올림하여 소수 셋째 자리까지"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_1.csv')\n"
        "g = df.groupby('course')['completed'].agg(['count', 'mean'])\n"
        "g = g[g['count'] >= 15].copy()\n"
        "g['rank'] = g['mean'].rank(method='dense', ascending=False)\n"
        "print(round(g.loc[g['rank'] == 3, 'mean'].iloc[0], 3))\n"
    )
    explain = (
        "agg(['count', 'mean'])로 인원과 이수율을 한 번에 구하고, 집계한 표에서 인원 조건으로 거른다(행을 거르는 것이 아니라 강좌를 거른다). "
        "인원 조건을 빠뜨리면 수강생이 적어 이수율이 들쭉날쭉한 강좌가 상위에 끼어 답이 바뀐다.\n\n"
        "지문의 순위 규칙은 rank(method='dense')다. 기본값 method='average'나 'min'을 쓰면 동률 다음 순위가 건너뛰어진다. "
        "이수율이 같은 강좌가 상위권에 있어서 sort_values().iloc[2]처럼 세 번째 행을 읽으면 동률 값을 두 번 세어 다른 답이 나온다. "
        "같은 순위의 강좌가 여럿이어도 이수율은 같으니 iloc[0]으로 하나만 읽는다."
    )
    return dict(make=make, check=check, title='수강 15명 이상 강좌의 이수율 3순위(조밀 순위)',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '반올림하여 소수 셋째 자리까지', None)])


# ---------------------------------------------------------------- m4-1-2
@problem
def m4_2():
    stations = ['여의나루역', '뚝섬유원지역', '망원한강공원', '서울숲', '잠실새내역', '홍대입구역']
    wk = [24, 21, 22, 20, 15, 14]
    we = [33, 36, 31, 34, 19, 18]

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 1150
        days = pd.date_range('2025-04-01', '2025-06-30', freq='D')
        d = days[rng.integers(0, len(days), n)]
        weekend = d.dayofweek >= 5
        hour_p = np.array([1, 1, 0, 0, 0, 0, 1, 3, 5, 4, 4, 5, 6, 6, 6, 7, 8, 9, 9, 8, 7, 5, 3, 2], float)
        hours = rng.choice(24, n, p=hour_p / hour_p.sum())
        mins = rng.integers(0, 60, n)
        si = rng.integers(0, 6, n)
        mean = np.where(weekend, np.array(we)[si], np.array(wk)[si])
        dur = np.maximum(3, np.round(mean * rng.lognormal(0, 0.5, n))).astype(int)
        rent = d + pd.to_timedelta(hours, 'h') + pd.to_timedelta(mins, 'm')
        ret = rent + pd.to_timedelta(dur, 'm')
        df = pd.DataFrame({'rent_time': rent, 'station': np.array(stations)[si], 'return_time': ret,
                           'distance_km': np.round(dur * rng.uniform(0.12, 0.22, n), 2)})
        df = df.sort_values('rent_time').reset_index(drop=True)
        df['rent_time'] = df['rent_time'].dt.strftime('%Y-%m-%d %H:%M')
        df['return_time'] = df['return_time'].dt.strftime('%Y-%m-%d %H:%M')
        df.insert(0, 'rent_id', [f'B{i:05d}' for i in range(1, n + 1)])
        return df

    def check(df):
        r = pd.to_datetime(df['rent_time']); t = pd.to_datetime(df['return_time'])
        mi = (t - r).dt.total_seconds() / 60
        wmask = r.dt.dayofweek >= 5
        g = mi[wmask].groupby(df['station'][wmask]).mean().sort_values(ascending=False)
        gall = mi.groupby(df['station']).mean().idxmax()
        top = g.index[0]
        h = r[wmask & (df['station'] == top)].dt.hour.value_counts().sort_values(ascending=False)
        ok = g.iloc[0] - g.iloc[1] > 0.5 and h.iloc[0] > h.iloc[1] and gall != top and ((t.dt.date != r.dt.date).sum() > 0)
        return ok, [top, str(int(h.index[0]))], {'g': g.round(3).to_dict(), 'all_top': gall, 'h': h.head(4).to_dict(),
                                                'cross_midnight': int((t.dt.date != r.dt.date).sum())}

    statement = (
        "어느 도시 공공자전거의 2025년 2분기 대여 기록이다. 한 행이 대여 한 건이다.\n\n"
        + table([('rent_id', '대여 ID'), ('rent_time', '대여 시각 (YYYY-MM-DD HH:MM)'), ('station', '대여 정류소'),
                 ('return_time', '반납 시각 (YYYY-MM-DD HH:MM)'), ('distance_km', '이동 거리(km)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) rent_time과 return_time을 날짜시간형으로 바꾼다. 자정을 넘겨 반납한 건도 있다.\n"
        "- 2) 이용시간(분) = (return_time − rent_time)을 분으로 바꾼 값 으로 계산한다.\n"
        "- 3) rent_time이 주말(토요일·일요일)인 대여만 남긴다.\n\n"
        "① 주말 대여 중 station별 평균 이용시간이 가장 긴 station을 구하시오.\n\n"
        "② ①의 station에서 주말에 대여한 건을 대여 시각의 시(hour, 0~23)별로 셀 때 건수가 가장 많은 시를 구하시오.\n\n"
        "【제출 형식】 ① 정류소 이름 그대로 ② 정수(0~23)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_2.csv')\n"
        "df['rent_time'] = pd.to_datetime(df['rent_time'])\n"
        "df['return_time'] = pd.to_datetime(df['return_time'])\n"
        "df['minutes'] = (df['return_time'] - df['rent_time']).dt.total_seconds() / 60\n"
        "w = df[df['rent_time'].dt.dayofweek >= 5]\n"
        "top = w.groupby('station')['minutes'].mean().idxmax()\n"
        "print(top)\n"
        "h = w[w['station'] == top]['rent_time'].dt.hour.value_counts()\n"
        "print(h.idxmax())\n"
    )
    explain = (
        "시각 차는 날짜까지 포함한 datetime끼리 빼야 자정을 넘긴 대여가 음수가 되지 않는다. 시:분만 떼어 빼면 틀린다.\n\n"
        "주말로 먼저 거른 뒤 평균을 낸다. 전체 대여로 평균을 내면 1위 정류소가 바뀐다. "
        "②는 ①의 정류소로 다시 거르고 dt.hour.value_counts().idxmax()로 가장 많은 시를 읽는다."
    )
    return dict(make=make, check=check, title='주말 이용시간 최장 정류소와 최다 대여 시각',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '정류소 이름 그대로', None), ('②', '정수(0~23)', None)])


# ---------------------------------------------------------------- m4-1-3
@problem
def m4_3():
    schools = ['한빛중', '새솔중', '가람중', '누리중', '다온중']
    su_mu = [33.0, 35.5, 31.8, 34.6, 36.2]

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 860
        si = rng.integers(0, 5, n)
        gender = rng.choice(['F', 'M'], n, p=[.48, .52])
        fem = gender == 'F'
        # 오래달리기 기록(초): 남학생이 빠르다. 성별 분포가 달라 전체로 Z-점수를 내면 기준이 흐려진다
        run = np.round(np.where(fem, 470, 395) + rng.normal(0, np.where(fem, 38, 34), n)).astype(int)
        situp = np.round(np.array(su_mu)[si] + np.where(fem, -3, 4) + rng.normal(0, 7, n)).clip(3, None).astype(int)
        # 여학생 기록 일부가 측정·입력 오류로 비정상적으로 길다
        cand = np.where(fem)[0]
        sp = rng.choice(cand, 7, replace=False)
        run[sp] = rng.integers(585, 660, 7)
        situp[sp] = rng.integers(48, 62, 7)
        return pd.DataFrame({'student_id': [f'P{i:04d}' for i in range(1, n + 1)], 'school': np.array(schools)[si],
                             'gender': gender, 'run_sec': run, 'situp': situp})

    def solve(df, sub_first=True):
        f = df[df['gender'] == 'F'].copy()
        if sub_first:
            z = (f['run_sec'] - f['run_sec'].mean()) / f['run_sec'].std()
        else:
            z_all = (df['run_sec'] - df['run_sec'].mean()) / df['run_sec'].std()
            z = z_all[f.index]
        k = f[z.abs() <= 3]
        g = k.groupby('school')['situp'].mean()
        return z, g, g.max() - g.min()

    def check(df):
        z, g, v = solve(df)
        z2, g2, v2 = solve(df, False)
        margin = (z.abs() - 3).abs().min()
        # 해설대로: 전체 기준 Z는 여학생 기준보다 정확히 한 명 더 지운다
        r1, r2 = set(z.index[z.abs() > 3]), set(z2.index[z2.abs() > 3])
        if not (r1 < r2 and len(r2 - r1) == 1):
            return False, [], {}
        ok = margin > 0.01 and not near_half(v, 2, 0.1) and round(v2, 2) != round(v, 2)
        ok &= g.idxmax() != g.idxmin() and (z.abs() > 3).sum() >= 5
        return ok, [fmt(v, 2)], {'g': g.round(4).to_dict(), 'whole_z': round(v2, 4), 'margin': margin,
                                 'removed': int((z.abs() > 3).sum())}

    statement = (
        "어느 교육지원청이 관내 중학교 5곳의 학생건강체력평가 기록을 모았다. 한 행이 학생 한 명이다.\n\n"
        + table([('student_id', '학생 ID'), ('school', '학교'), ('gender', '성별(F/M)'),
                 ('run_sec', '오래달리기 기록(초)'), ('situp', '윗몸 말아 올리기 횟수(회)')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) gender가 F인 학생만 남긴다.\n"
        "- 2) 남은 학생의 run_sec 평균과 표준편차로 Z-점수 = (run_sec − 평균) / 표준편차 를 계산한다. 표준편차는 표본표준편차(n−1로 나눔)를 쓴다.\n"
        "- 3) Z-점수의 절댓값이 3보다 큰 학생을 제거한다.\n"
        "- 4) 남은 학생으로 school별 situp 평균을 구한다.\n\n"
        "school별 situp 평균 가운데 가장 큰 값과 가장 작은 값의 차이를 구하시오.\n\n"
        "【제출 형식】 반올림하여 소수 둘째 자리까지"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_3.csv')\n"
        "f = df[df['gender'] == 'F'].copy()\n"
        "f['z'] = (f['run_sec'] - f['run_sec'].mean()) / f['run_sec'].std()\n"
        "f = f[f['z'].abs() <= 3]\n"
        "g = f.groupby('school')['situp'].mean()\n"
        "print(round(g.max() - g.min(), 2))\n"
    )
    explain = (
        "Z-점수의 평균과 표준편차는 여학생만 남긴 뒤 다시 계산한다. 남녀를 합친 전체로 계산하면 기록이 빠른 남학생 때문에 평균이 낮아져 "
        "여학생 기록이 실제보다 극단적으로 계산된다. 이 데이터에서는 여학생 기준으로는 남아야 할 기록이 하나 더 지워져 답이 달라진다.\n\n"
        "scipy.stats.zscore는 기본 ddof=0이라 지문의 표본표준편차와 다르다. 쓸 거면 ddof=1을 준다. "
        "마지막은 학교별 평균의 최댓값 − 최솟값이라 g.max() - g.min()이다."
    )
    return dict(make=make, check=check, title='여학생 달리기 Z-점수 이상치 제거 후 학교별 격차',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '반올림하여 소수 둘째 자리까지', None)])


# ---------------------------------------------------------------- m5-1-1
@problem
def m5_1():
    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원']

    def make(seed):
        rng = np.random.default_rng(seed)
        rows = []
        fbias = rng.normal(0, 0.12, len(regions))
        size = rng.uniform(0.3, 2.5, len(regions))
        for ri, r in enumerate(regions):
            for g in ['F', 'M']:
                for a in ['20대', '30대', '40대', '50대', '60대']:
                    for m in range(1, 7):
                        cnt = int(size[ri] * rng.integers(800, 2000) * (1 + (fbias[ri] if g == 'F' else 0)))
                        per = rng.normal(48000 if g == 'F' else 52000, 6000)
                        rows.append((r, g, a, f'2025-{m:02d}', int(cnt * per), cnt))
        return pd.DataFrame(rows, columns=['region', 'gender', 'age_band', 'ym', 'amount', 'count'])

    def check(df):
        p = df.pivot_table(index='region', columns='gender', values='amount', aggfunc='sum')
        dd = (p['F'] - p['M']).sort_values(ascending=False)
        r = dd.index[1]
        da = (p['F'] - p['M']).abs().sort_values(ascending=False)
        d = df[df['region'] == r]
        v = d['amount'].sum() / d['count'].sum()
        v2 = (d['amount'] / d['count']).mean()
        ok = dd.iloc[1] - dd.iloc[2] > 1e6 and dd.iloc[0] - dd.iloc[1] > 1e6 and not near_int(v, 0.02) and da.index[1] != r \
            and int(v) != int(v2)
        return ok, [r, str(int(v))], {'dd': (dd / 1e6).round(1).to_dict(), 'abs2': da.index[1], 'v': v, 'rowmean': v2}

    statement = (
        "어느 카드사의 2025년 상반기 지역·성별·연령대·월별 카드 이용 집계 데이터이다.\n\n"
        + table([('region', '지역'), ('gender', '성별(F/M)'), ('age_band', '연령대'), ('ym', '연-월'),
                 ('amount', '이용 금액 합계(원)'), ('count', '이용 건수')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) region을 행, gender를 열로 하는 amount 합계 표를 만든다.\n"
        "- 2) 지역별 차이 = F의 합계 − M의 합계 를 계산한다(절댓값을 취하지 않는다).\n\n"
        "① 차이가 두 번째로 큰 region을 구하시오.\n\n"
        "② ①의 region에서 건당 평균 이용 금액 = (그 지역 amount 전체 합) / (그 지역 count 전체 합) 을 구하시오. 성별·연령대·월 구분 없이 모두 합친다.\n\n"
        "【제출 형식】 ① 지역 이름 그대로 ② 소수점 이하를 버리고 정수로"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_1.csv')\n"
        "p = df.pivot_table(index='region', columns='gender', values='amount', aggfunc='sum')\n"
        "diff = (p['F'] - p['M']).sort_values(ascending=False)\n"
        "r = diff.index[1]\n"
        "print(r)\n"
        "d = df[df['region'] == r]\n"
        "print(int(d['amount'].sum() / d['count'].sum()))\n"
    )
    explain = (
        "pivot_table의 aggfunc 기본값은 mean이라 aggfunc='sum'을 꼭 준다. groupby(['region', 'gender'])['amount'].sum().unstack()도 같은 표다.\n\n"
        "차이는 F − M 그대로 정렬한다. 절댓값으로 정렬하면 2위가 바뀐다. "
        "②는 합을 합으로 나누는 가중 평균이다. 행마다 amount / count를 구해 평균하면 다른 값이 나온다."
    )
    return dict(make=make, check=check, title='성별 이용액 차이 2위 지역의 건당 이용액',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '지역 이름 그대로', None), ('②', '소수점 이하를 버리고 정수로', None)])


# ---------------------------------------------------------------- m5-1-2
@problem
def m5_2():
    domains = ['gmail.com', 'naver.com', 'daum.net', 'kakao.com', 'hanmail.net']
    letters = 'abcdefghijklmnopqrstuvwxyz'
    kor = ['별', '달', '해', '숲', '빛', '꿈', '봄', '산', '강', '눈']

    def make(seed):
        rng = np.random.default_rng(seed)
        n = 820
        dom = rng.choice(domains, n, p=[.33, .30, .15, .12, .10])
        emails, nicks = [], []
        for i in range(n):
            local = ''.join(rng.choice(list(letters), rng.integers(4, 10))) + str(rng.integers(1, 999))
            d = dom[i]
            if d == 'naver.com' and rng.random() < 0.2:
                d = rng.choice(['NAVER.COM', 'Naver.com', 'naver.COM'])
            elif d == 'gmail.com' and rng.random() < 0.03:
                d = 'Gmail.com'
            emails.append(f'{local}@{d}')
            L = int(rng.integers(3, 13))
            if rng.random() < 0.3:
                nk = ''.join(rng.choice(kor, max(2, L // 2)))
            else:
                nk = rng.choice(list(letters)) + ''.join(rng.choice(list(letters + '0123456789_'), L - 1))
            nicks.append(nk)
        return pd.DataFrame({'member_id': [f'M{i:04d}' for i in range(1, n + 1)], 'email': emails, 'nickname': nicks,
                             'grade': rng.choice(['일반', '실버', '골드', 'VIP'], n, p=[.5, .3, .15, .05])})

    def check(df):
        dom = df['email'].str.split('@').str[1].str.lower()
        vc = dom.value_counts()
        raw = df['email'].str.split('@').str[1].value_counts()
        top = vc.index[0]
        d = df[dom == top]
        v = (d['nickname'].str.len() >= 8).mean()
        ok = vc.iloc[0] > vc.iloc[1] and raw.index[0] != top and not near_half(v, 3, 0.08) \
            and not df['nickname'].isin(['NA', 'null', 'nan', 'None']).any()
        return ok, [fmt(v, 3)], {'vc': vc.to_dict(), 'raw_top': raw.index[0], 'v': v}

    statement = (
        "어느 온라인 서비스의 회원 정보이다. email의 도메인 표기에 대문자가 섞여 있다.\n\n"
        + table([('member_id', '회원 ID'), ('email', '이메일 주소'), ('nickname', '닉네임'), ('grade', '회원 등급')])
        + "\n\n다음 순서로 수행하시오.\n\n"
        "- 1) email에서 '@' 뒤의 부분을 도메인으로 꺼내고, 모두 소문자로 바꾼다(NAVER.COM과 naver.com은 같은 도메인이다).\n"
        "- 2) 회원 수가 가장 많은 도메인을 찾는다.\n"
        "- 3) 그 도메인 회원 중 nickname의 글자 수가 8 이상인 회원의 비율을 구한다.\n\n"
        "3)의 비율을 구하시오.\n\n"
        "【제출 형식】 반올림하여 소수 셋째 자리까지 (예: 0.123)"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_2.csv')\n"
        "df['domain'] = df['email'].str.split('@').str[1].str.lower()\n"
        "top = df['domain'].value_counts().idxmax()\n"
        "d = df[df['domain'] == top]\n"
        "print(round((d['nickname'].str.len() >= 8).mean(), 3))\n"
    )
    explain = (
        "str.split('@').str[1]로 도메인을 꺼내고 str.lower()로 표기를 맞춘다. 소문자로 바꾸지 않으면 naver.com이 여러 표기로 쪼개져 1위 도메인이 바뀐다.\n\n"
        "str.len()은 한글도 한 글자로 센다. 불리언 Series의 mean()이 곧 비율이다."
    )
    return dict(make=make, check=check, title='최다 이메일 도메인 회원의 긴 닉네임 비율',
                statement=statement, solution=solution, explain=explain,
                answers=[('답', '반올림하여 소수 셋째 자리까지', None)])


# ---------------------------------------------------------------- m5-1-3
@problem
def m5_3():
    def make(seed):
        rng = np.random.default_rng(seed)
        n = 460
        grade = rng.integers(1, 7, n)
        screen = np.round(55 + 22 * grade + rng.normal(0, 30, n)).clip(10, None)
        sleep = np.round(10.2 - 0.25 * grade - 0.008 * screen + rng.normal(0, 0.55, n), 1)
        height = np.round(118 + 5.8 * grade + rng.normal(0, 5, n), 1)
        weight = np.round(22 + 3.3 * grade + rng.normal(0, 4, n), 1)
        screen = screen.astype(float)
        na_s = rng.choice(n, 47, replace=False)
        na_l = rng.choice(np.setdiff1d(np.arange(n), na_s[:20]), 28, replace=False)
        screen[na_s] = np.nan
        sleep[na_l] = np.nan
        return pd.DataFrame({'student_id': [f'K{i:04d}' for i in range(1, n + 1)], 'grade': grade, 'height': height,
                             'weight': weight, 'sleep_hours': sleep, 'screen_time': screen})

    def solve(df, order='fill_first'):
        d = df.copy()
        if order == 'fill_first':
            d['screen_time'] = d['screen_time'].fillna(d.groupby('grade')['screen_time'].transform('mean'))
            d = d.dropna(subset=['sleep_hours'])
        else:
            d = d.dropna(subset=['sleep_hours'])
            d['screen_time'] = d['screen_time'].fillna(d.groupby('grade')['screen_time'].transform('mean'))
        return d['screen_time'].corr(d['sleep_hours']), d['screen_time'].quantile(0.75)

    def check(df):
        r, q = solve(df)
        r2, q2 = solve(df, 'drop_first')
        ok = (not near_half(r, 4, 0.1)) and not near_int(q, 0.03) and round(r, 4) != round(r2, 4)
        return ok, [fmt(r, 4), str(int(q))], {'r': r, 'q': q, 'drop_first': (r2, q2)}

    statement = (
        "어느 초등학교 학생들의 생활습관 조사 데이터이다. sleep_hours와 screen_time에 결측치가 있다.\n\n"
        + table([('student_id', '학생 ID'), ('grade', '학년(1~6)'), ('height', '키(cm)'), ('weight', '몸무게(kg)'),
                 ('sleep_hours', '하루 수면 시간(시간)'), ('screen_time', '하루 화면 사용 시간(분)')])
        + "\n\n다음 순서대로 수행하시오. 순서를 바꾸면 결과가 달라진다.\n\n"
        "- 1) 먼저 screen_time의 결측치를 같은 grade의 screen_time 평균으로 채운다(평균은 원본 460행에서 결측을 뺀 값으로 계산).\n"
        "- 2) 그다음 sleep_hours가 결측인 행을 삭제한다.\n\n"
        "① 남은 데이터에서 screen_time과 sleep_hours의 피어슨 상관계수를 구하시오.\n\n"
        "② 같은 데이터에서 screen_time의 3사분위수(pandas quantile 기본값)를 구하시오.\n\n"
        "【제출 형식】 ① 반올림하여 소수 넷째 자리까지 ② 소수점 이하를 버리고 정수로"
    )
    solution = (
        "import pandas as pd\n"
        "df = pd.read_csv('data/t1_3.csv')\n"
        "df['screen_time'] = df['screen_time'].fillna(df.groupby('grade')['screen_time'].transform('mean'))\n"
        "df = df.dropna(subset=['sleep_hours'])\n"
        "print(round(df['screen_time'].corr(df['sleep_hours']), 4))\n"
        "print(int(df['screen_time'].quantile(0.75)))\n"
    )
    explain = (
        "그룹 평균 대체는 groupby('grade').transform('mean')을 fillna에 넣는다. dropna(subset=['sleep_hours'])는 그 칼럼이 빈 행만 지운다. "
        "이 데이터는 다른 칼럼에 결측이 없어 subset 없이 dropna()를 써도 같지만, 지울 기준 칼럼을 subset으로 밝혀 두는 편이 안전하다.\n\n"
        "행을 먼저 지우고 채우면 학년 평균이 달라져 상관계수 넷째 자리가 바뀐다. 상관계수는 Series.corr(다른 Series)가 기본 피어슨이다."
    )
    return dict(make=make, check=check, title='학년 평균 대체 후 수면과 화면시간 상관',
                statement=statement, solution=solution, explain=explain,
                answers=[('①', '반올림하여 소수 넷째 자리까지', None), ('②', '소수점 이하를 버리고 정수로', None)])


# ---------------------------------------------------------------- main
ORDER = [('m1', 1), ('m1', 2), ('m1', 3), ('m2', 1), ('m2', 2), ('m2', 3), ('m3', 1), ('m3', 2), ('m3', 3),
         ('m4', 1), ('m4', 2), ('m4', 3), ('m5', 1), ('m5', 2), ('m5', 3)]


def main():
    out = []
    report = []
    for (st, k), fn in zip(ORDER, PROBLEMS):
        p = fn()
        for seed in range(1, 400):
            df = p['make'](seed)
            ok, vals, info = p['check'](df)
            if ok:
                break
        else:
            raise SystemExit(f'{st}-{k}: no seed')
        os.makedirs(f'{OUT}/{st}', exist_ok=True)
        path = f'{OUT}/{st}/t1_{k}.csv'
        df.to_csv(path, index=False, encoding='utf-8')
        # 저장본을 다시 읽어 확인(부동소수 자리 문제 방지)
        df2 = pd.read_csv(path)
        ok2, vals2, info2 = p['check'](df2)
        assert ok2 and vals2 == vals, (st, k, vals, vals2)
        assert ',' not in ''.join(df.astype(str).values.ravel()), (st, k)
        answers = [{'label': lab, 'format': f, 'value': v} for (lab, f, _), v in zip(p['answers'], vals)]
        out.append({
            'id': f'{st}-1-{k}', 'set': st, 'type': 1, 'no': f'1-{k}', 'points': 10,
            'title': p['title'], 'statement': p['statement'], 'files': [f'{st}/t1_{k}.csv'],
            'starter': f"import pandas as pd\ndf = pd.read_csv('data/t1_{k}.csv')\n",
            'answers': answers, 'solution': p['solution'], 'explain': p['explain'],
        })
        report.append((f'{st}-1-{k}', seed, len(df), os.path.getsize(path), vals, info))
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    with open(f'{OUT}/parts/t1.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for r in report:
        print(r[0], 'seed', r[1], 'rows', r[2], 'bytes', r[3], 'ans', r[4])
        print('   ', r[5])


if __name__ == '__main__':
    main()
