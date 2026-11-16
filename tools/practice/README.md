# 빅데이터분석기사 실습 문제 생성기

`data/bigdata-analysis-engineer/practice/`의 CSV와 `problems.json`은 전부 이 스크립트가 만든 가짜 데이터다. 외부 데이터를 읽지 않는다. 시드를 고정한 numpy 난수로 만들고, 답이 반올림 경계에 걸리지 않는지와 문제에 심은 함정이 실제로 답을 바꾸는지를 확인한 시드만 쓴다. 다시 돌리면 같은 파일이 나온다.

문제 유형은 기출 복원본에서 뽑은 출제 패턴(연산 사슬, 검정 종류, 평가지표, 답 형식)만 따랐다. 복원본의 문장, 데이터, 코드는 쓰지 않았다.

## 파이썬 두 벌

| 이름 | 버전 | 쓰임 |
|---|---|---|
| `EXAM_PY` | pandas 2.2.2 · numpy 1.26.4 · scipy 1.14.1 · scikit-learn 1.5.2 · statsmodels 0.14.1 | 시험 체험환경(제12회)과 같은 버전. 데이터 생성과 정답 |
| `BROWSER_PY` | pandas 2.2.0 · numpy 1.26.4 · scipy 1.12.0 · scikit-learn 1.4.2 · statsmodels 0.14.2 | 실습 탭의 Pyodide 0.26.4와 같은 버전. 두 버전의 답이 같은지 확인 |

```
uv venv --python 3.12 exam && uv pip install --python exam/bin/python pandas==2.2.2 numpy==1.26.4 scipy==1.14.1 scikit-learn==1.5.2 statsmodels==0.14.1
uv venv --python 3.12 browser && uv pip install --python browser/bin/python pandas==2.2.0 numpy==1.26.4 scipy==1.12.0 scikit-learn==1.4.2 statsmodels==0.14.2
export EXAM_PY=$PWD/exam/bin/python BROWSER_PY=$PWD/browser/bin/python
```

## 순서

생성기는 `practice/m1..m5/`에 CSV를, `practice/parts/t<유형>.json`에 문제 목록을 쓴다. 검증은 `parts/`를 읽으므로 합치기 전에 한다.

```
cd tools/practice
(cd t1 && $EXAM_PY gen_t1.py && $EXAM_PY verify_t1.py)   # 작업형1 15문제
(cd t3 && $EXAM_PY gen_t3.py && $EXAM_PY verify_t3.py)   # 작업형3 10문제
(cd t2 && $EXAM_PY build.py --gen)                       # 작업형2 5문제: 생성, 두 버전 채점, 기준 점수 기록
$EXAM_PY merge_practice.py                               # parts/ → problems.json (parts/는 지운다)
$EXAM_PY verify_practice.py && $BROWSER_PY verify_practice.py   # 합친 목록 전체를 다시 확인
```

`verify_practice.py`는 문제마다 풀이 코드를 임시 폴더(`data/`에 파일 복사)에서 실행해, 작업형1·3은 출력에 정답이 있는지, 작업형2는 `result.csv` 형식과 점수가 기록과 같은지 본다.
