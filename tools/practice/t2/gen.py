"""작업형2 데이터 생성 (m1~m7). 시드 고정.
사용: python gen.py <out_root>   (out_root/m<N>/train.csv, test.csv, t2_truth.csv)
"""
import sys, os
import numpy as np
import pandas as pd

OUT = sys.argv[1]


def save(setid, train, test, truth):
    d = os.path.join(OUT, setid)
    os.makedirs(d, exist_ok=True)
    train.to_csv(os.path.join(d, 'train.csv'), index=False)
    test.to_csv(os.path.join(d, 'test.csv'), index=False)
    pd.DataFrame({'y': truth}).to_csv(os.path.join(d, 't2_truth.csv'), index=False)


# ---------------------------------------------------------------- m1
# 카페 매장 일 매출(만원) 회귀, RMSE. 함정: train의 sales 0 = 집계 누락
def m1():
    rng = np.random.default_rng(1101)
    n = 3200
    region = rng.choice(['역세권', '주택가', '오피스', '대학가'], n, p=[.3, .3, .25, .15])
    weekday = rng.choice(['월', '화', '수', '목', '금', '토', '일'], n)
    month = rng.integers(1, 13, n)
    temp = np.round(12 - 13 * np.cos((month - 1) / 12 * 2 * np.pi) + rng.normal(0, 4, n), 1)
    rain = np.where(rng.random(n) < 0.72, 0.0, np.round(rng.gamma(1.2, 9, n), 1))
    promo = (rng.random(n) < 0.22).astype(int)
    seats = rng.integers(16, 81, n)
    staff = np.clip(np.round(seats / 14 + rng.normal(0.5, 1.0, n)), 2, 9).astype(int)
    delivery = rng.choice(['Y', 'N'], n, p=[.55, .45])

    base = {'역세권': 260, '주택가': 200, '오피스': 240, '대학가': 210}
    weekend = np.isin(weekday, ['토', '일'])
    mult = np.ones(n)
    mult *= np.where(weekend & (region == '오피스'), 0.45, 1)
    mult *= np.where(weekend & (region == '대학가'), 0.7, 1)
    mult *= np.where(weekend & (region == '주택가'), 1.35, 1)
    mult *= np.where(weekend & (region == '역세권'), 1.15, 1)
    mult *= np.where((weekday == '금'), 1.1, 1)
    mult *= np.exp(-0.0009 * (temp - 21) ** 2)     # 21도 근처가 최고
    rain_eff = np.where(delivery == 'Y', 0.002, 0.009)
    mult *= np.exp(-rain_eff * rain)
    mult *= np.where(promo == 1, 1.18, 1)
    mult *= (seats / 40) ** 0.45
    mult *= 1 - 0.35 * np.exp(-(staff - 1) / 1.5)  # 인원 부족하면 손해
    mult *= np.where(delivery == 'Y', 1.08, 1)
    mean = np.array([base[r] for r in region]) * mult
    sales = np.round(mean * np.exp(rng.normal(0, 0.09, n)), 1)
    sales = np.maximum(sales, 15.0)

    df = pd.DataFrame({'region': region, 'weekday': weekday, 'month': month, 'temp': temp,
                       'rain_mm': rain, 'promo': promo, 'seats': seats, 'staff': staff,
                       'delivery': delivery, 'sales': sales})
    ntr = 2400
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    # 함정: train 일부 행의 sales를 0으로(집계 누락) — 특징과 무관하게 무작위
    zero = rng.random(ntr) < 0.08
    tr.loc[zero, 'sales'] = 0.0
    tr.insert(0, 'id', np.arange(1, ntr + 1))
    te.insert(0, 'id', np.arange(ntr + 1, n + 1))
    truth = te.pop('sales').values
    save('m1', tr, te, truth)


# ---------------------------------------------------------------- m2
# 설비 상태 3분류(정상/주의/고장) 심한 불균형, macro F1
def m2():
    rng = np.random.default_rng(1202)
    n = 4000
    line = rng.choice(['A', 'B', 'C', 'D'], n, p=[.3, .3, .25, .15])
    model = rng.choice(['구형', '표준', '신형'], n, p=[.25, .5, .25])
    run_hours = np.round(rng.gamma(3, 2500, n))
    load_pct = np.round(np.clip(rng.normal(68, 14, n), 20, 100), 1)
    temp_c = np.round(45 + 0.25 * load_pct + rng.normal(0, 6, n), 1)
    vibration = np.round(np.abs(rng.gamma(2.2, 1.1, n) + 0.00008 * run_hours), 2)
    pressure = np.round(rng.normal(6.0, 0.8, n), 2)
    noise_db = np.round(62 + 3.2 * vibration + rng.normal(0, 4, n), 1)
    maint_days = rng.integers(1, 365, n)

    risk = (0.9 * np.maximum(vibration - 3.0, 0) ** 1.4
            + 0.08 * np.maximum(temp_c - 68, 0) ** 1.2
            + 0.004 * maint_days
            + np.where(model == '구형', 0.9, np.where(model == '신형', -0.6, 0))
            + 1.1 * np.abs(pressure - 6.0) ** 2
            + np.where((line == 'D') & (load_pct > 80), 1.2, 0)
            + 0.00004 * run_hours
            + rng.normal(0, 0.55, n))
    q1, q2 = np.quantile(risk, [0.84, 0.953])
    status = np.where(risk >= q2, '고장', np.where(risk >= q1, '주의', '정상'))
    df = pd.DataFrame({'line': line, 'model': model, 'run_hours': run_hours.astype(int),
                       'load_pct': load_pct, 'temp_c': temp_c, 'vibration': vibration,
                       'pressure': pressure, 'noise_db': noise_db, 'maint_days': maint_days,
                       'status': status})
    ntr = 3000
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    tr.insert(0, 'id', ['EQ%05d' % i for i in range(1, ntr + 1)])
    te.insert(0, 'id', ['EQ%05d' % i for i in range(ntr + 1, n + 1)])
    truth = te.pop('status').values
    save('m2', tr, te, truth)


# ---------------------------------------------------------------- m3
# 전기차 충전소 시간당 충전 건수(비음수 카운트) 회귀, RMSLE
def m3():
    rng = np.random.default_rng(1303)
    n = 3400
    stype = rng.choice(['아파트', '대형마트', '휴게소', '관공서'], n, p=[.35, .25, .2, .2])
    area = rng.choice(['도심', '외곽'], n, p=[.6, .4])
    day_type = rng.choice(['평일', '주말', '공휴일'], n, p=[.68, .26, .06])
    hour = rng.integers(0, 24, n)
    temp = np.round(np.clip(rng.normal(14, 9, n), -12, 36), 1)   # 기온은 한국 날씨 범위로
    chargers = rng.integers(2, 13, n)
    fast_ratio = np.round(rng.beta(2, 3, n), 2)
    price = np.round(rng.choice([292.9, 324.4, 347.2], n) + rng.normal(0, 8, n), 1)
    event = (rng.random(n) < 0.07).astype(int)

    h = hour.astype(float)
    def bump(c, w):
        d = np.minimum(np.abs(h - c), 24 - np.abs(h - c))
        return np.exp(-(d / w) ** 2)
    prof = np.where(stype == '아파트', 0.4 + 2.2 * bump(21, 3) + 0.6 * bump(7, 2),
           np.where(stype == '대형마트', 0.15 + 2.4 * bump(15, 3.5) * (h >= 9) * (h <= 22),
           np.where(stype == '휴게소', 0.6 + 1.6 * bump(13, 4),
                    0.1 + 1.9 * bump(11, 3) * (h >= 8) * (h <= 19))))
    off = day_type != '평일'
    dmult = np.where(stype == '휴게소', np.where(off, 2.0, 1.0),
            np.where(stype == '대형마트', np.where(off, 1.7, 1.0),
            np.where(stype == '관공서', np.where(off, 0.2, 1.0), np.where(off, 1.15, 1.0))))
    loglam = (np.log(prof * dmult + 1e-3)
              + 0.5 * np.log(chargers)
              + 0.9 * fast_ratio
              + np.where(area == '도심', 0.35, 0)
              - 0.0006 * (temp - 18) ** 2
              - 0.012 * (price - 320)
              + 0.8 * event
              + 0.1)
    lam = np.exp(loglam) * rng.gamma(4, 1 / 4, n)   # 과산포
    cnt = rng.poisson(lam)
    df = pd.DataFrame({'station_type': stype, 'area': area, 'day_type': day_type, 'hour': hour,
                       'temp': temp, 'chargers': chargers, 'fast_ratio': fast_ratio,
                       'price': price, 'event': event, 'sessions': cnt})
    ntr = 2600
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    tr.insert(0, 'id', np.arange(10001, 10001 + ntr))
    te.insert(0, 'id', np.arange(10001 + ntr, 10001 + n))
    truth = te.pop('sessions').values
    save('m3', tr, te, truth)


# ---------------------------------------------------------------- m4
# 헬스장 회원 재등록 여부 이진분류, ROC-AUC. 함정: test에만 있는 지점(송도)
def m4():
    rng = np.random.default_rng(1404)
    ntr, nte = 2600, 900
    n = ntr + nte
    branch_tr = rng.choice(['강남', '잠실', '분당', '일산', '수원'], ntr, p=[.25, .22, .2, .18, .15])
    branch_te = rng.choice(['강남', '잠실', '분당', '일산', '수원', '송도'], nte,
                           p=[.22, .2, .18, .16, .14, .10])
    branch = np.concatenate([branch_tr, branch_te])
    plan = rng.choice(['1개월', '3개월', '6개월', '12개월'], n, p=[.35, .3, .2, .15])
    gender = rng.choice(['M', 'F'], n, p=[.55, .45])
    age = np.clip(np.round(rng.normal(34, 10, n)), 18, 70).astype(int)
    visits = np.round(np.clip(rng.gamma(2.2, 0.9, n), 0, 7), 1)
    pt = rng.poisson(np.where(rng.random(n) < 0.3, 6, 0.3))
    tenure = np.clip(np.round(rng.exponential(10, n)), 1, 72).astype(int)
    locker = (rng.random(n) < 0.35).astype(int)
    dist = np.round(rng.gamma(2, 1.6, n), 1)
    complaint = rng.choice([0, 1, 2, 3], n, p=[.7, .18, .08, .04])

    beff = {'강남': 0.2, '잠실': 0.0, '분당': 0.3, '일산': -0.3, '수원': -0.1, '송도': 0.1}
    peff = {'1개월': -0.6, '3개월': 0.0, '6개월': 0.35, '12개월': 0.6}
    z = (-0.9
         + 1.6 * np.tanh((visits - 1.5) / 1.2)
         + 0.12 * np.minimum(pt, 10)
         + 0.5 * np.log1p(tenure) - 1.0
         - 0.3 * np.maximum(dist - 3, 0)
         - 0.7 * complaint
         + 0.35 * locker
         - 0.0025 * (age - 38) ** 2 + 0.3
         + np.array([beff[b] for b in branch])
         + np.array([peff[p] for p in plan])
         + np.where((gender == 'F') & (pt > 3), 0.4, 0))
    p = 1 / (1 + np.exp(-z))
    y = (rng.random(n) < p).astype(int)
    df = pd.DataFrame({'branch': branch, 'plan': plan, 'gender': gender, 'age': age,
                       'visits_week': visits, 'pt_sessions': pt, 'tenure_m': tenure,
                       'locker': locker, 'distance_km': dist, 'complaints': complaint,
                       're_register': y})
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    tr.insert(0, 'member_id', ['M%06d' % i for i in rng.permutation(np.arange(100000, 100000 + ntr))])
    te.insert(0, 'member_id', ['M%06d' % i for i in rng.permutation(np.arange(200000, 200000 + nte))])
    truth = te.pop('re_register').values
    save('m4', tr, te, truth)


# ---------------------------------------------------------------- m5
# 원룸 월세(만원) 회귀, MAE. 함정: train에만 결측 + train에만 있는 구(강북) → 인코딩 일관성
def m5():
    rng = np.random.default_rng(1505)
    ntr, nte = 3000, 1000
    n = ntr + nte
    gus = ['마포', '관악', '성북', '동작', '광진', '서대문', '강서', '노원']
    gu_tr = rng.choice(['강북'] + gus, ntr, p=[.04, .14, .16, .1, .11, .12, .1, .12, .11])
    gu_te = rng.choice(gus, nte, p=[.15, .17, .1, .11, .13, .1, .12, .12])
    gu = np.concatenate([gu_tr, gu_te])
    room = rng.choice(['원룸', '투룸', '오피스텔'], n, p=[.55, .2, .25])
    area = np.round(np.where(room == '원룸', rng.normal(21, 4, n),
                    np.where(room == '투룸', rng.normal(36, 6, n), rng.normal(27, 5, n))), 1)
    area = np.clip(area, 12, 60)
    floor = rng.choice(np.r_[-1, np.arange(1, 16)], n, p=np.r_[[.06], np.full(15, .94 / 15)])
    built = rng.integers(1992, 2025, n)
    station = np.clip(np.round(rng.gamma(2.5, 4, n)), 1, 40).astype(int)
    parking = rng.choice(['Y', 'N'], n, p=[.4, .6])
    options = rng.choice(['Y', 'N'], n, p=[.6, .4])
    deposit = rng.choice([300, 500, 1000, 2000, 3000, 5000], n, p=[.15, .3, .3, .12, .08, .05])

    geff = {'강북': 0.85, '마포': 1.25, '관악': 0.9, '성북': 0.95, '동작': 1.05,
            '광진': 1.1, '서대문': 1.0, '강서': 0.95, '노원': 0.82}
    reff = {'원룸': 0, '투룸': 8, '오피스텔': 12}
    base = (2.1 * area + np.array([reff[r] for r in room]))
    base *= np.array([geff[g] for g in gu])
    base *= np.where(floor == -1, 0.78, np.where(floor >= 5, 1.05, 1.0))
    base *= 1 + 0.012 * np.clip(built - 2005, -13, 19)
    base *= np.exp(-0.012 * station)
    base *= np.where(options == 'Y', 1.08, 1.0)
    base += np.where(parking == 'Y', 4, 0)
    base -= 5.5 * np.log(deposit / 300) ** 1.3   # 보증금이 많으면 월세가 낮다(전환)
    rent = np.round(np.maximum(base * np.exp(rng.normal(0, 0.07, n)), 15))

    df = pd.DataFrame({'gu': gu, 'room_type': room, 'area_m2': area, 'floor': floor,
                       'built_year': built, 'station_min': station, 'parking': parking,
                       'full_option': options, 'deposit': deposit, 'rent': rent.astype(int)})
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    tr['station_min'] = tr['station_min'].astype('Int64')
    tr['built_year'] = tr['built_year'].astype('Int64')
    tr.loc[rng.random(ntr) < 0.05, 'station_min'] = pd.NA
    tr.loc[rng.random(ntr) < 0.04, 'built_year'] = pd.NA
    tr.insert(0, 'room_id', np.arange(50001, 50001 + ntr))
    te.insert(0, 'room_id', np.arange(50001 + ntr, 50001 + n))
    truth = te.pop('rent').values
    save('m5', tr, te, truth)


# ---------------------------------------------------------------- m6
# 미용실 예약 노쇼 이진분류, ROC-AUC. 함정: 타깃이 문자('노쇼','방문')이고 양성(노쇼)이 정렬상 앞
#   -> classes_ = ['노쇼', '방문'], predict_proba[:, 1]은 방문 확률
def m6():
    rng = np.random.default_rng(1606)
    ntr, nte = 3000, 1000
    n = ntr + nte
    branch = rng.choice(['성수', '합정', '판교', '광교', '송파'], n, p=[.24, .22, .2, .18, .16])
    service = rng.choice(['커트', '펌', '염색', '클리닉'], n, p=[.45, .22, .2, .13])
    channel = rng.choice(['앱', '전화', '포털', '방문'], n, p=[.4, .2, .3, .1])
    lead = np.clip(np.round(rng.gamma(1.4, 4.5, n)), 0, 45).astype(int)
    slot = rng.choice(['오전', '오후', '저녁'], n, p=[.25, .45, .3])
    weekend = rng.choice(['Y', 'N'], n, p=[.35, .65])
    age = np.clip(np.round(rng.normal(31, 9, n)), 16, 68).astype(int)
    first = rng.choice(['Y', 'N'], n, p=[.3, .7])
    past_visits = np.where(first == 'Y', 0, np.clip(rng.poisson(5, n), 1, 40)).astype(int)
    past_noshow = np.where(first == 'Y', 0, rng.binomial(past_visits, rng.beta(1.2, 12, n))).astype(int)
    deposit = rng.choice(['Y', 'N'], n, p=[.35, .65])
    deposit = np.where(np.isin(service, ['펌', '염색']) & (rng.random(n) < 0.35), 'Y', deposit)
    reminder = np.where(rng.random(n) < np.where(channel == '앱', 0.7, 0.45), 'Y', 'N')
    price_base = {'커트': 22, '펌': 95, '염색': 80, '클리닉': 55}
    price = np.round(np.array([price_base[s] for s in service]) * np.exp(rng.normal(0, 0.18, n))).astype(int)
    rain = rng.choice(['Y', 'N'], n, p=[.2, .8])

    ceff = {'앱': 0.0, '전화': -0.35, '포털': 0.45, '방문': -0.6}
    seff = {'오전': 0.35, '오후': 0.0, '저녁': -0.1}
    z = (-2.1
         + 0.55 * np.log1p(lead)
         - 1.2 * (deposit == 'Y')
         - 0.8 * (reminder == 'Y')
         + 0.9 * np.minimum(past_noshow, 4) - 0.06 * np.minimum(past_visits, 15)
         + 0.5 * (first == 'Y') + 0.6 * ((first == 'Y') & (deposit == 'N') & (lead > 7))
         + np.array([ceff[c] for c in channel])
         + np.array([seff[s] for s in slot])
         + 0.25 * (weekend == 'N')
         - 0.022 * (age - 31)
         - 0.006 * (price - 50)
         + 0.45 * (rain == 'Y')
         + rng.normal(0, 0.3, n))
    p = 1 / (1 + np.exp(-z))
    noshow = rng.random(n) < p
    result = np.where(noshow, '노쇼', '방문')
    df = pd.DataFrame({'branch': branch, 'service': service, 'channel': channel, 'lead_days': lead,
                       'slot': slot, 'weekend': weekend, 'age': age, 'first_visit': first,
                       'past_visits': past_visits, 'past_noshow': past_noshow, 'deposit': deposit,
                       'reminder': reminder, 'price': price, 'rain': rain, 'result': result})
    tr, te = df.iloc[:ntr].copy(), df.iloc[ntr:].copy()
    tr.insert(0, 'booking_id', ['R%06d' % i for i in rng.permutation(np.arange(300000, 300000 + ntr))])
    te.insert(0, 'booking_id', ['R%06d' % i for i in rng.permutation(np.arange(400000, 400000 + nte))])
    truth = (te.pop('result').values == '노쇼').astype(int)   # 채점용: 1 = 노쇼
    save('m6', tr, te, truth)


# ---------------------------------------------------------------- m7
# 시립도서관 분관 일 대출 권수 회귀, RMSE. 함정: 날짜(date) 문자열 — test 기간이 train 뒤라
#   그대로 원-핫하면 test 날짜가 train에 없어 요일·월 정보가 사라진다 -> 월·요일을 뽑아야 한다
def m7():
    rng = np.random.default_rng(1707)
    days = pd.date_range('2024-03-01', '2026-02-28', freq='D')
    days = days[days.dayofweek != 0]                      # 월요일 휴관
    branches = ['중앙', '해오름', '별빛', '솔숲', '물빛']
    bbase = {'중앙': 520, '해오름': 260, '별빛': 210, '솔숲': 300, '물빛': 170}
    bseats = {'중앙': 420, '해오름': 180, '별빛': 150, '솔숲': 220, '물빛': 120}
    hol = {'2024-03-01', '2024-04-10', '2024-05-05', '2024-05-06', '2024-05-15', '2024-06-06',
           '2024-08-15', '2024-09-16', '2024-09-17', '2024-09-18', '2024-10-03', '2024-10-09',
           '2024-12-25', '2025-01-01', '2025-01-28', '2025-01-29', '2025-01-30', '2025-03-01',
           '2025-03-03', '2025-05-05', '2025-05-06', '2025-06-03', '2025-06-06', '2025-08-15',
           '2025-10-03', '2025-10-06', '2025-10-07', '2025-10-08', '2025-10-09', '2025-12-25',
           '2026-01-01', '2026-02-16', '2026-02-17', '2026-02-18'}
    D = np.repeat(days.values, len(branches))
    D = pd.DatetimeIndex(D)
    br = np.tile(branches, len(days))
    n = len(D)
    m = D.month.values
    dow = D.dayofweek.values                              # 1=화 ... 6=일
    dstr = D.strftime('%Y-%m-%d')
    holiday = np.where(np.isin(dstr, list(hol)), 'Y', 'N')
    # 날씨는 날짜별로 같게(분관이 같은 도시)
    nd = len(days)
    dm = days.month.values
    temp_d = np.round(12.5 - 14 * np.cos((dm - 1 + days.day.values / 31) / 12 * 2 * np.pi) + rng.normal(0, 3.5, nd), 1)
    rain_d = np.where(rng.random(nd) < 0.7, 0.0, np.round(rng.gamma(1.1, 10, nd), 1))
    temp = np.repeat(temp_d, len(branches))
    rain = np.repeat(rain_d, len(branches))
    event = (rng.random(n) < 0.08).astype(int)
    new_books = rng.poisson(np.array([bbase[b] / 6 for b in br])).astype(int)
    seats = np.array([bseats[b] for b in br])

    dmult = {1: 1.0, 2: 0.9, 3: 0.92, 4: 1.08, 5: 1.75, 6: 1.55}
    mmult = {1: 1.4, 2: 1.3, 3: 0.88, 4: 0.92, 5: 1.0, 6: 0.9, 7: 1.3, 8: 1.45,
             9: 0.86, 10: 0.95, 11: 0.85, 12: 1.12}
    mean = np.array([bbase[b] for b in br], dtype=float)
    mean *= np.array([dmult[d] for d in dow])
    mean *= np.array([mmult[x] for x in m])
    mean *= np.where((holiday == 'Y') & (dow < 5), 1.5, 1.0)
    mean *= np.where(np.isin(br, ['해오름', '물빛']) & (dow >= 5), 1.2, 1.0)   # 주거지 분관은 주말 효과가 더 크다
    mean *= np.exp(-0.012 * rain)
    mean *= 1 + 0.012 * np.maximum(temp - 27, 0) + 0.01 * np.maximum(-2 - temp, 0)
    mean *= np.where(event == 1, 1.15, 1.0)
    mean *= (new_books / (np.array([bbase[b] for b in br]) / 6) + 0.5) ** 0.12
    loans = np.round(mean * np.exp(rng.normal(0, 0.1, n))).astype(int)

    df = pd.DataFrame({'date': dstr, 'branch': br, 'holiday': holiday, 'temp': temp,
                       'rain_mm': rain, 'event': event, 'new_books': new_books, 'seats': seats,
                       'loans': loans})
    cut = D < pd.Timestamp('2025-09-01')
    tr, te = df[cut].reset_index(drop=True), df[~cut].reset_index(drop=True)
    truth = te.pop('loans').values
    save('m7', tr, te, truth)


for f in (m1, m2, m3, m4, m5, m6, m7):
    f()
print('ok')
