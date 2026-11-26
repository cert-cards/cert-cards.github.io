# 작업형2 문제 정의 (statement, solution, baseline). build.py가 읽는다.

STARTER = "import pandas as pd\ntrain = pd.read_csv('data/train.csv')\ntest = pd.read_csv('data/test.csv')\n"

SUBMIT_BLOCK = """【제출 형식】

- 파일명: result.csv
- 칼럼: pred 1개 (index 없이 저장)
- 행 수: {rows}행 (test.csv와 같은 행 순서)
- {pred_desc}"""

P = []

# ------------------------------------------------------------------ m1
P.append(dict(
    id='m1-2', set='m1', title='카페 매장 일 매출액 예측 (RMSE)', metric='rmse', rows=800,
    target='sales', idcol='id',
    statement="""다음은 한 카페 프랜차이즈 매장들의 일 매출 데이터이다. 학습용 데이터(train.csv)를 이용하여 일 매출액(sales)을 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 sales를 예측하여 제출하시오.

- 학습용 데이터: 2,400행, 11개 칼럼 (sales 포함)
- 평가용 데이터: 800행, 10개 칼럼 (sales 없음)

| 칼럼 | 설명 |
|---|---|
| id | 행 식별 번호 |
| region | 매장 상권 (역세권, 주택가, 오피스, 대학가) |
| weekday | 요일 (월~일) |
| month | 월 (1~12) |
| temp | 일 평균기온(℃) |
| rain_mm | 일 강수량(mm) |
| promo | 할인 행사 여부 (1: 행사, 0: 없음) |
| seats | 매장 좌석 수 |
| staff | 근무 인원(명) |
| delivery | 배달 운영 여부 (Y, N) |
| sales | 일 매출액(만원). POS 집계가 되지 않은 날은 0으로 기록되어 있음 |

【유의 사항】

- 성능 평가 지표는 RMSE(Root Mean Squared Error)이며, 값이 낮을수록 좋다.
- 평가용 데이터의 실제 매출(채점 기준값)에는 집계 누락이 없다. 모든 날이 정상 집계된 매출이다.

""" + SUBMIT_BLOCK.format(rows=800, pred_desc='pred에는 예측한 일 매출액(만원)을 넣는다'),
    solution="""import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) sales 0은 매출이 없던 날이 아니라 집계 누락 -> 학습에서 뺀다
print('sales 0 행 수:', (train['sales'] == 0).sum())
train = train[train['sales'] > 0].reset_index(drop=True)

# 2) 범주형 원-핫 인코딩 (train과 test를 합쳐 칼럼을 맞춘다)
y = train['sales']
X_all = pd.concat([train.drop(columns=['id', 'sales']), test.drop(columns=['id'])])
X_all = pd.get_dummies(X_all, columns=['region', 'weekday', 'delivery'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 3) 검증
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
print('검증 RMSE:', np.sqrt(mean_squared_error(y_val, model.predict(X_val))))

# 4) 전체 train으로 다시 학습해 예측
model.fit(X, y)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestRegressor
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['sales']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['id', 'sales']), test.drop(columns=['id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestRegressor(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
""",
    explain="""sales가 0인 행(학습용의 약 8%)은 매출이 없던 날이 아니라 집계가 빠진 날이다. 그대로 학습하면 모형이 0을 따라가 예측이 전반적으로 낮아지고 RMSE가 커진다.
`train[train['sales'] > 0]`으로 걸러 낸 뒤 학습하면 같은 랜덤포레스트로도 RMSE가 약 {base:.0f}에서 {sol:.0f} 수준으로 내려간다. 평가용 정답에는 0이 없다.
원-핫 인코딩은 train과 test를 합쳐 한 번에 해야 칼럼 순서와 개수가 어긋나지 않는다. RMSE는 `np.sqrt(mean_squared_error(...))`로 계산한다.""",
))

# ------------------------------------------------------------------ m2
P.append(dict(
    id='m2-2', set='m2', title='설비 상태 등급 분류 (macro F1)', metric='f1_macro', rows=1000,
    target='status', idcol='id',
    statement="""다음은 한 공장의 설비 점검 기록이다. 학습용 데이터(train.csv)를 이용하여 설비 상태(status)를 분류하는 모형을 만들고, 평가용 데이터(test.csv)의 status를 예측하여 제출하시오.

- 학습용 데이터: 3,000행, 11개 칼럼 (status 포함)
- 평가용 데이터: 1,000행, 10개 칼럼 (status 없음)

| 칼럼 | 설명 |
|---|---|
| id | 설비 점검 번호 |
| line | 생산 라인 (A, B, C, D) |
| model | 설비 모델 (구형, 표준, 신형) |
| run_hours | 누적 가동 시간(시간) |
| load_pct | 평균 부하율(%) |
| temp_c | 설비 표면 온도(℃) |
| vibration | 진동 속도(mm/s) |
| pressure | 유압(bar) |
| noise_db | 소음(dB) |
| maint_days | 마지막 정비 후 경과 일수 |
| status | 설비 상태 (정상, 주의, 고장) |

【유의 사항】

- 성능 평가 지표는 macro F1 score이며, 값이 높을수록 좋다. (클래스별 F1을 단순 평균한 값)

""" + SUBMIT_BLOCK.format(rows=1000, pred_desc='pred에는 예측한 상태를 정상, 주의, 고장 중 하나의 문자 그대로 넣는다'),
    solution="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 클래스 비율 확인 -> 고장이 약 5%로 매우 적다
print(train['status'].value_counts(normalize=True))

# 2) 범주형 원-핫 인코딩 (train과 test를 합쳐서)
y = train['status']
X_all = pd.concat([train.drop(columns=['id', 'status']), test.drop(columns=['id'])])
X_all = pd.get_dummies(X_all, columns=['line', 'model'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 3) 검증: stratify로 클래스 비율 유지, 소수 클래스에 가중치
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
model = RandomForestClassifier(n_estimators=300, class_weight='balanced_subsample',
                               min_samples_leaf=3, random_state=0)
model.fit(X_tr, y_tr)
print('검증 macro F1:', f1_score(y_val, model.predict(X_val), average='macro'))

# 4) 전체 train으로 다시 학습해 예측
model.fit(X, y)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv')['pred'].value_counts())
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['status']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['id', 'status']), test.drop(columns=['id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestClassifier(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
""",
    explain="""status는 정상이 약 84%, 주의 11%, 고장 5%로 크게 치우쳐 있다. macro F1은 세 클래스의 F1을 같은 비중으로 평균하므로 소수 클래스를 놓치면 점수가 크게 깎인다(전부 정상으로 내면 약 0.30).
기본값 랜덤포레스트는 다수결이라 주의와 고장을 정상으로 흡수하는 경향이 있다. `class_weight='balanced_subsample'`로 소수 클래스에 가중치를 주고 `min_samples_leaf=3`으로 잎을 조금 키우면 소수 클래스 재현율이 올라 {base:.3f}에서 {sol:.3f} 정도로 좋아진다.
검증 분할에는 `stratify=y`를 넣어 고장 클래스가 검증 세트에 고르게 들어가게 한다. pred에는 숫자 코드가 아니라 상태 문자를 그대로 넣는다.""",
))

# ------------------------------------------------------------------ m3
P.append(dict(
    id='m3-2', set='m3', title='전기차 충전소 시간당 충전 건수 예측 (RMSLE)', metric='rmsle', rows=800,
    target='sessions', idcol='id',
    statement="""다음은 공영 전기차 충전소의 시간대별 이용 기록이다. 학습용 데이터(train.csv)를 이용하여 해당 시간에 시작된 충전 건수(sessions)를 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 sessions를 예측하여 제출하시오.

- 학습용 데이터: 2,600행, 11개 칼럼 (sessions 포함)
- 평가용 데이터: 800행, 10개 칼럼 (sessions 없음)

| 칼럼 | 설명 |
|---|---|
| id | 행 식별 번호 |
| station_type | 충전소 위치 유형 (아파트, 대형마트, 휴게소, 관공서) |
| area | 지역 구분 (도심, 외곽) |
| day_type | 날짜 구분 (평일, 주말, 공휴일) |
| hour | 시간대 (0~23시) |
| temp | 기온(℃) |
| chargers | 충전기 대수 |
| fast_ratio | 충전기 중 급속 충전기 비율 |
| price | kWh당 충전 요금(원) |
| event | 주변 행사 여부 (1: 있음, 0: 없음) |
| sessions | 해당 시간에 시작된 충전 건수 (0 이상의 정수) |

【유의 사항】

- 성능 평가 지표는 RMSLE(Root Mean Squared Logarithmic Error)이며, 값이 낮을수록 좋다.

""" + SUBMIT_BLOCK.format(rows=800, pred_desc='pred에는 예측한 충전 건수를 넣는다 (정수가 아니어도 된다)'),
    solution="""import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_log_error

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 타깃 분포 확인 -> 0이 많고 오른쪽으로 길게 치우친 카운트
print(train['sessions'].describe())

# 2) 범주형 원-핫 인코딩 (train과 test를 합쳐서)
y = np.log1p(train['sessions'])          # RMSLE에 맞춰 log(1+y)로 학습
X_all = pd.concat([train.drop(columns=['id', 'sessions']), test.drop(columns=['id'])])
X_all = pd.get_dummies(X_all, columns=['station_type', 'area', 'day_type'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 3) 검증 (원래 단위로 되돌려 RMSLE 계산)
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
model = RandomForestRegressor(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
p_val = np.clip(np.expm1(model.predict(X_val)), 0, None)
print('검증 RMSLE:', np.sqrt(mean_squared_log_error(np.expm1(y_val), p_val)))

# 4) 전체 train으로 다시 학습해 예측, 음수는 0으로
model.fit(X, y)
pred = np.clip(np.expm1(model.predict(X_test)), 0, None)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestRegressor
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['sessions']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['id', 'sessions']), test.drop(columns=['id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestRegressor(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
""",
    explain="""sessions는 0 이상의 카운트이고 오른쪽으로 길게 치우쳐 있다(중앙값 2, 최댓값 100 이상). RMSLE는 log(1+y)의 오차를 보므로 타깃을 `np.log1p`로 바꿔 학습하고 `np.expm1`로 되돌리면 작은 값을 덜 틀리게 되어 점수가 {base:.3f}에서 {sol:.3f} 정도로 좋아진다.
선형회귀처럼 음수를 낼 수 있는 모형은 음수 예측이 생겨 RMSLE를 계산할 수 없다(이 데이터에서 LinearRegression은 test 예측 {neg}개가 음수). `np.clip(pred, 0, None)`으로 0 아래를 잘라 둔다.
검증도 `mean_squared_log_error`에 제곱근을 씌워 같은 지표로 본다. RMSE로 검증하면 큰 값 위주로 맞추게 되어 방향이 달라진다.""",
))

# ------------------------------------------------------------------ m4
P.append(dict(
    id='m4-2', set='m4', title='헬스장 회원 재등록 여부 예측 (ROC-AUC)', metric='roc_auc', rows=900,
    target='re_register', idcol='member_id', pos_label=1,
    statement="""다음은 한 피트니스 체인의 회원 이용 기록이다. 학습용 데이터(train.csv)를 이용하여 회원권 만료 후 재등록 여부(re_register)를 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 회원이 재등록할 확률을 예측하여 제출하시오.

- 학습용 데이터: 2,600행, 12개 칼럼 (re_register 포함)
- 평가용 데이터: 900행, 11개 칼럼 (re_register 없음)

| 칼럼 | 설명 |
|---|---|
| member_id | 회원 번호 |
| branch | 등록 지점 |
| plan | 회원권 종류 (1개월, 3개월, 6개월, 12개월) |
| gender | 성별 (M, F) |
| age | 나이 |
| visits_week | 주 평균 방문 횟수 |
| pt_sessions | 이용한 PT 횟수 |
| tenure_m | 누적 등록 기간(개월) |
| locker | 개인 사물함 이용 여부 (1: 이용, 0: 미이용) |
| distance_km | 집에서 지점까지 거리(km) |
| complaints | 접수한 불만 건수 |
| re_register | 재등록 여부 (1: 재등록, 0: 미등록) |

【유의 사항】

- 성능 평가 지표는 ROC-AUC이며, 값이 높을수록 좋다.

""" + SUBMIT_BLOCK.format(rows=900, pred_desc='pred에는 재등록(re_register = 1)할 확률을 넣는다'),
    solution="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 범주 확인 -> test에만 있는 지점이 있다
print(set(test['branch']) - set(train['branch']))

# 2) train과 test를 합쳐 한 번에 원-핫 인코딩 (따로 하면 칼럼이 어긋난다)
y = train['re_register']
X_all = pd.concat([train.drop(columns=['member_id', 're_register']),
                   test.drop(columns=['member_id'])])
X_all = pd.get_dummies(X_all, columns=['branch', 'plan', 'gender'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 3) 검증 (확률로 AUC 계산)
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
model = RandomForestClassifier(n_estimators=300, min_samples_leaf=10, random_state=0)
model.fit(X_tr, y_tr)
print('검증 AUC:', roc_auc_score(y_val, model.predict_proba(X_val)[:, 1]))

# 4) 전체 train으로 다시 학습, 양성(1) 확률을 제출
model.fit(X, y)
print(model.classes_)                     # [0 1] -> 두 번째 열이 1일 확률
pred = model.predict_proba(X_test)[:, 1]
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['re_register']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['member_id', 're_register']), test.drop(columns=['member_id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestClassifier(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict_proba(X_test)[:, 1]}).to_csv('result.csv', index=False)
""",
    explain="""branch의 송도는 test에만 있다. train과 test를 따로 `pd.get_dummies`하면 칼럼 수가 달라 predict에서 오류가 나고, LabelEncoder를 train에만 fit하면 test를 transform할 때 오류가 난다. 두 데이터를 합쳐 한 번에 인코딩한다.
ROC-AUC는 예측의 순위를 보는 지표라 `predict`의 0/1이 아니라 `predict_proba(X_test)[:, 1]`(1일 확률)을 내야 한다. 기본값 랜덤포레스트로 확률을 내면 {base:.3f}인데, 같은 모형으로 0/1을 내면 {hard:.3f}로 떨어진다.
`min_samples_leaf=10`으로 잎을 키우면 확률이 덜 들쭉날쭉해져 AUC가 {sol:.3f}까지 조금 더 오른다.""",
))

# ------------------------------------------------------------------ m5
P.append(dict(
    id='m5-2', set='m5', title='원룸 월세 예측 (MAE)', metric='mae', rows=1000,
    target='rent', idcol='room_id',
    statement="""다음은 서울 일부 자치구의 원룸과 오피스텔 월세 매물 데이터이다. 학습용 데이터(train.csv)를 이용하여 월세(rent)를 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 rent를 예측하여 제출하시오.

- 학습용 데이터: 3,000행, 11개 칼럼 (rent 포함)
- 평가용 데이터: 1,000행, 10개 칼럼 (rent 없음)

| 칼럼 | 설명 |
|---|---|
| room_id | 매물 번호 |
| gu | 자치구 |
| room_type | 방 형태 (원룸, 투룸, 오피스텔) |
| area_m2 | 전용면적(㎡) |
| floor | 층 (-1은 반지하) |
| built_year | 준공 연도 |
| station_min | 가장 가까운 지하철역까지 도보 시간(분) |
| parking | 주차 가능 여부 (Y, N) |
| full_option | 풀옵션 여부 (Y, N) |
| deposit | 보증금(만원) |
| rent | 월세(만원) |

【유의 사항】

- 성능 평가 지표는 MAE(Mean Absolute Error)이며, 값이 낮을수록 좋다.

""" + SUBMIT_BLOCK.format(rows=1000, pred_desc='pred에는 예측한 월세(만원)를 넣는다'),
    solution="""import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 결측치 확인 -> train에만 station_min, built_year 결측
print(train.isna().sum())
print(test.isna().sum().sum())
for col in ['station_min', 'built_year']:
    train[col] = train[col].fillna(train[col].median())

# 2) 범주 확인 -> gu의 강북은 train에만 있다. 합쳐서 한 번에 인코딩
print(set(train['gu']) - set(test['gu']))
y = train['rent']
X_all = pd.concat([train.drop(columns=['room_id', 'rent']), test.drop(columns=['room_id'])])
X_all = pd.get_dummies(X_all, columns=['gu', 'room_type', 'parking', 'full_option'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 3) 검증
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
model = RandomForestRegressor(n_estimators=300, random_state=0)
model.fit(X_tr, y_tr)
print('검증 MAE:', mean_absolute_error(y_val, model.predict(X_val)))

# 4) 전체 train으로 다시 학습해 예측
model.fit(X, y)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestRegressor
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['rent']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['room_id', 'rent']), test.drop(columns=['room_id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestRegressor(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
""",
    explain="""train에만 station_min(약 5%)과 built_year(약 4%) 결측이 있고 test에는 없다. 학습 데이터의 중앙값으로 채운다. scikit-learn 1.4부터 RandomForest가 결측을 받기는 하지만, 채워 두면 버전에 상관없이 돌아간다.
gu의 강북은 train에만 있다. train과 test를 따로 LabelEncoder로 바꾸면 가나다순 번호가 하나씩 밀려 같은 구가 서로 다른 숫자가 되고, 오류 없이 엉뚱한 예측이 나온다(이 데이터에서 MAE {misenc:.2f}). 합쳐서 한 번에 인코딩하면 {sol:.2f}이다.
평가 지표가 MAE이므로 검증도 `mean_absolute_error`로 본다.""",
))

# ------------------------------------------------------------------ m6
P.append(dict(
    id='m6-2', set='m6', title='미용실 예약 노쇼 예측 (ROC-AUC)', metric='roc_auc', rows=1000,
    target='result', idcol='booking_id',
    statement="""다음은 한 미용실 체인의 예약 기록이다. 학습용 데이터(train.csv)를 이용하여 예약 고객이 예약 시간에 오지 않는지(노쇼) 여부(result)를 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 예약이 노쇼일 확률을 예측하여 제출하시오.

- 학습용 데이터: 3,000행, 16개 칼럼 (result 포함)
- 평가용 데이터: 1,000행, 15개 칼럼 (result 없음)

| 칼럼 | 설명 |
|---|---|
| booking_id | 예약 번호 |
| branch | 지점 (성수, 합정, 판교, 광교, 송파) |
| service | 예약 시술 (커트, 펌, 염색, 클리닉) |
| channel | 예약 경로 (앱, 전화, 포털, 방문) |
| lead_days | 예약한 날부터 예약일까지 일수 |
| slot | 예약 시간대 (오전, 오후, 저녁) |
| weekend | 예약일이 주말인지 여부 (Y, N) |
| age | 고객 나이 |
| first_visit | 첫 방문 고객 여부 (Y, N) |
| past_visits | 지난 1년 방문 횟수 |
| past_noshow | 지난 1년 노쇼 횟수 |
| deposit | 예약금 결제 여부 (Y, N) |
| reminder | 전날 알림 확인 여부 (Y, N) |
| price | 시술 예정 금액(천원) |
| rain | 예약일 비 예보 여부 (Y, N) |
| result | 예약 결과 (노쇼, 방문) |

【유의 사항】

- 성능 평가 지표는 ROC-AUC이며, 값이 높을수록 좋다.

""" + SUBMIT_BLOCK.format(rows=1000, pred_desc='pred에는 노쇼(result = 노쇼)일 확률을 넣는다'),
    solution="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 타깃 확인 -> 0/1이 아니라 문자 '노쇼', '방문'
print(train['result'].value_counts())

# 2) 구할 확률이 노쇼이므로 노쇼를 1, 방문을 0으로 바꿔 둔다
y = (train['result'] == '노쇼').astype(int)

# 3) 범주형 원-핫 인코딩 (train과 test를 합쳐서)
X_all = pd.concat([train.drop(columns=['booking_id', 'result']),
                   test.drop(columns=['booking_id'])])
X_all = pd.get_dummies(X_all, columns=['branch', 'service', 'channel', 'slot', 'weekend',
                                       'first_visit', 'deposit', 'reminder', 'rain'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 4) 검증 (확률로 AUC 계산)
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
model = RandomForestClassifier(n_estimators=300, min_samples_leaf=10, random_state=0)
model.fit(X_tr, y_tr)
print('검증 AUC:', roc_auc_score(y_val, model.predict_proba(X_val)[:, 1]))

# 5) 전체 train으로 다시 학습, 노쇼(1) 확률을 제출
model.fit(X, y)
print(model.classes_)                     # [0 1] -> 두 번째 열이 노쇼(1) 확률
pred = model.predict_proba(X_test)[:, 1]
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestClassifier
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['result']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['booking_id', 'result']), test.drop(columns=['booking_id'])]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestClassifier(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict_proba(X_test)[:, 1]}).to_csv('result.csv', index=False)
""",
    explain="""result는 0/1이 아니라 문자 노쇼, 방문이다. 문자 타깃을 그대로 학습하면 `model.classes_`가 가나다순으로 `['노쇼', '방문']`이 되어, 습관대로 `predict_proba(X_test)[:, 1]`을 내면 노쇼가 아니라 방문할 확률을 내게 된다. 순위가 정반대라 ROC-AUC가 0.5보다 낮은 {base:.3f}이 나온다.
같은 모형에서 노쇼 열(`[:, 0]`)을 내면 {right:.3f}이다. 헷갈리지 않으려면 `y = (train['result'] == '노쇼').astype(int)`로 구할 쪽을 1로 바꾸고 `classes_`가 `[0 1]`인지 확인한 뒤 `[:, 1]`을 낸다.
`min_samples_leaf=10`으로 잎을 키우면 확률이 덜 들쭉날쭉해져 {sol:.3f}까지 오른다. AUC는 순위를 보는 지표라 `predict`의 0/1이 아니라 확률을 낸다.""",
))

# ------------------------------------------------------------------ m7
P.append(dict(
    id='m7-2', set='m7', title='도서관 분관 일 대출 권수 예측 (RMSE)', metric='rmse', rows=775,
    target='loans', idcol='date',
    statement="""다음은 한 시립도서관 분관들의 일별 대출 기록이다. 학습용 데이터(train.csv)를 이용하여 하루 대출 권수(loans)를 예측하는 모형을 만들고, 평가용 데이터(test.csv)의 loans를 예측하여 제출하시오.

- 학습용 데이터: 2,355행, 9개 칼럼 (loans 포함)
- 평가용 데이터: 775행, 8개 칼럼 (loans 없음)

| 칼럼 | 설명 |
|---|---|
| date | 날짜 (YYYY-MM-DD). 월요일은 휴관이라 기록이 없음 |
| branch | 분관 (중앙, 해오름, 별빛, 솔숲, 물빛) |
| holiday | 공휴일 여부 (Y, N) |
| temp | 일 평균기온(℃) |
| rain_mm | 일 강수량(mm) |
| event | 문화행사 개최 여부 (1: 개최, 0: 없음) |
| new_books | 최근 1주 신착 도서 수(권) |
| seats | 열람석 수 |
| loans | 하루 대출 권수(권) |

【유의 사항】

- 성능 평가 지표는 RMSE(Root Mean Squared Error)이며, 값이 낮을수록 좋다.

""" + SUBMIT_BLOCK.format(rows=775, pred_desc='pred에는 예측한 하루 대출 권수를 넣는다 (정수가 아니어도 된다)'),
    solution="""import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

# 1) 날짜 범위 확인 -> 평가용 기간이 학습용 기간 뒤에 이어진다
print(train['date'].min(), train['date'].max())
print(test['date'].min(), test['date'].max())

# 2) date는 문자열이라 그대로 쓰면 test 날짜가 train에 없다 -> 월과 요일을 뽑고 date는 뺀다
for df in (train, test):
    d = pd.to_datetime(df['date'])
    df['month'] = d.dt.month
    df['dow'] = d.dt.dayofweek            # 0=월 ... 6=일
print(train.groupby('dow')['loans'].mean())

# 3) 범주형 원-핫 인코딩 (train과 test를 합쳐서)
y = train['loans']
X_all = pd.concat([train.drop(columns=['date', 'loans']), test.drop(columns=['date'])])
X_all = pd.get_dummies(X_all, columns=['branch', 'holiday'])
X = X_all.iloc[:len(train)]
X_test = X_all.iloc[len(train):]

# 4) 검증
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
model = RandomForestRegressor(n_estimators=300, random_state=0)
model.fit(X_tr, y_tr)
print('검증 RMSE:', np.sqrt(mean_squared_error(y_val, model.predict(X_val))))

# 5) 전체 train으로 다시 학습해 예측
model.fit(X, y)
pred = model.predict(X_test)
pd.DataFrame({'pred': pred}).to_csv('result.csv', index=False)
print(pd.read_csv('result.csv').shape)
""",
    baseline="""import pandas as pd
from sklearn.ensemble import RandomForestRegressor
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
y = train['loans']
X_all = pd.get_dummies(pd.concat([train.drop(columns=['loans']), test]))
X, X_test = X_all.iloc[:len(train)], X_all.iloc[len(train):]
m = RandomForestRegressor(random_state=0).fit(X, y)
pd.DataFrame({'pred': m.predict(X_test)}).to_csv('result.csv', index=False)
""",
    explain="""date는 문자열이고 평가용 기간(2025년 9월~2026년 2월)이 학습용 기간(2024년 3월~2025년 8월) 바로 뒤에 이어진다. 그대로 `pd.get_dummies`하면 날짜 하나하나가 칼럼이 되는데 test의 날짜는 train에 한 번도 없으므로 그 칼럼들은 학습에 쓰이지 않는다. 그래서 RMSE가 {base:.1f}이고, date를 아예 빼고 학습한 {nodate:.1f}보다도 나쁘다.
대출 권수는 요일(토·일이 평일보다 1.5배 이상)과 월(방학인 1·2·7·8월이 많다)에 따라 크게 움직인다. `pd.to_datetime`으로 바꾼 뒤 `.dt.month`, `.dt.dayofweek`를 뽑아 넣으면 RMSE가 {sol:.1f}로 크게 내려간다.
연도(`.dt.year`)는 넣지 않는다. test에는 2026년처럼 train에 없거나 적은 연도가 있고, 트리 모형은 본 적 없는 연도의 추세를 이어 그리지 못한다.""",
))
