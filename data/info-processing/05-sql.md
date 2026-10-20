# SQL 응용

## SQL 분류

- **SQL (Structured Query Language)** — 데이터를 정의·조작·제어하는 관계형 DBMS의 표준 언어. 비절차적이며 관계 대수와 관계 해석을 바탕으로 한다
- **DDL (Data Definition Language)** — 테이블·뷰·인덱스 같은 객체의 구조를 만들고 바꾸고 없애는 언어
  - CREATE, ALTER, DROP, TRUNCATE
- **DML (Data Manipulation Language)** — 사용자가 테이블에 저장된 실제 데이터를 조회·삽입·수정·삭제하며 다루는 언어
  - SELECT, INSERT, UPDATE, DELETE
- **DCL (Data Control Language)** — 사용자 권한 부여·회수를 통해 데이터의 보안·무결성·회복·병행 수행을 관리하는 언어
  - GRANT, REVOKE (COMMIT·ROLLBACK을 포함하기도 한다)
- **TCL (Transaction Control Language)** — 하나의 논리적 작업 단위가 끝났을 때 그 결과를 확정하거나 이전 상태로 되돌리는 언어
  - COMMIT, ROLLBACK, SAVEPOINT

## DDL 명령

- Q: 테이블 생성 — `CREATE TABLE 학생 (학번 CHAR(8) PRIMARY KEY, 이름 VARCHAR(20) NOT NULL);`
- Q: 인덱스 생성 — `CREATE UNIQUE INDEX idx_이름 ON 학생 (이름 ASC);`
  - UNIQUE는 선택
- Q: 뷰 생성 — `CREATE VIEW 우수학생 AS SELECT 학번, 이름 FROM 학생 WHERE 점수 >= 90;`
- Q: 컬럼 추가 — `ALTER TABLE 학생 ADD 전화번호 VARCHAR(15);`
- Q: 컬럼 변경 — `ALTER TABLE 학생 MODIFY 이름 VARCHAR(30);`
  - DBMS에 따라 `ALTER COLUMN`을 쓴다
- Q: 컬럼 삭제 — `ALTER TABLE 학생 DROP COLUMN 전화번호;`
- Q: 테이블 삭제 — `DROP TABLE 학생 CASCADE;`
  - 참조 중이면 거부하려면 `RESTRICT`
- Q: 인덱스 삭제 — `DROP INDEX idx_이름;`
- Q: 뷰 삭제 — `DROP VIEW 우수학생;`
- Q: 구조는 남기고 테이블의 모든 행 삭제 — `TRUNCATE TABLE 학생;`
- **CASCADE** — 제거하려는 개체를 참조하고 있는 다른 개체까지 연쇄적으로 함께 제거하는 옵션
- **RESTRICT** — 제거하려는 개체를 다른 개체가 참조하고 있으면 제거 자체를 거부하는 옵션

## DML 명령

- Q: SELECT 문의 논리적 실행 순서 — FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
- Q: 중복 제거 조회 — `SELECT DISTINCT 학과 FROM 학생;`
- Q: 범위 조건 (BETWEEN) — `SELECT * FROM 학생 WHERE 점수 BETWEEN 80 AND 90;`
  - 양 끝값 포함(80 이상 90 이하)
- Q: NULL 검사 — `SELECT * FROM 학생 WHERE 전화번호 IS NULL;`
  - 반대는 `IS NOT NULL`, `= NULL`로는 비교할 수 없다
- Q: 패턴 검색 (LIKE) — `SELECT * FROM 학생 WHERE 이름 LIKE '김%';`
  - `%`는 0개 이상의 임의 문자, `_`는 정확히 한 글자
- Q: 목록 중 하나와 일치 (IN) — `SELECT * FROM 학생 WHERE 학과 IN ('컴퓨터', '전자');`
- Q: 하위 질의 결과 존재 여부 (EXISTS) — `SELECT * FROM 학생 S WHERE EXISTS (SELECT * FROM 수강 C WHERE C.학번 = S.학번);`
  - 하위 질의가 한 행이라도 돌려주면 참
- Q: 그룹별 집계 (GROUP BY) — `SELECT 학과, AVG(점수) FROM 학생 GROUP BY 학과;`
- Q: 그룹에 조건 걸기 (HAVING) — `SELECT 학과, COUNT(*) FROM 학생 GROUP BY 학과 HAVING COUNT(*) >= 3;`
  - WHERE는 그룹화 전 행 조건, HAVING은 그룹화 후 그룹 조건
- Q: 정렬 (ORDER BY) — `SELECT * FROM 학생 ORDER BY 점수 DESC, 이름 ASC;`
  - 생략 시 기본값은 ASC(오름차순)
- Q: INSERT 두 형태 — `INSERT INTO 학생 (학번, 이름) VALUES ('1001', '홍길동');`
  - 다른 테이블 결과를 넣을 때: `INSERT INTO 우수학생 SELECT * FROM 학생 WHERE 점수 >= 90;`
- Q: UPDATE — `UPDATE 학생 SET 학년 = 학년 + 1 WHERE 학번 = '1001';`
- Q: DELETE — `DELETE FROM 학생 WHERE 학번 = '1001';`
  - WHERE를 빼면 모든 행이 지워지고 테이블 구조는 남는다

## DCL·TCL 명령

- Q: 학생 테이블의 SELECT·UPDATE 권한을 사용자1에게 부여 — `GRANT SELECT, UPDATE ON 학생 TO 사용자1;`
- Q: 받은 권한을 다른 사용자에게 다시 줄 수 있게 부여 — `GRANT SELECT ON 학생 TO 사용자1 WITH GRANT OPTION;`
- Q: 권한 회수 (연쇄 포함) — `REVOKE UPDATE ON 학생 FROM 사용자1 CASCADE;`
  - CASCADE: 사용자1이 다른 사용자에게 다시 준 권한까지 함께 회수
- Q: 권한은 남기고 다시 부여할 수 있는 권한만 회수 — `REVOKE GRANT OPTION FOR UPDATE ON 학생 FROM 사용자1;`
- Q: 작업 결과를 영구히 확정하는 명령 — `COMMIT;`
- Q: 확정되지 않은 작업을 취소하고 이전 상태로 되돌리는 명령 — `ROLLBACK;`
- Q: 되돌아갈 중간 지점을 지정하고 그 지점까지만 취소 — `SAVEPOINT S1;` 후 `ROLLBACK TO S1;`

## 집합 연산자

- **UNION** — 두 SELECT 결과를 하나로 합치되 중복 행은 한 번만 남기는 연산자
  - 두 질의의 컬럼 수와 데이터 타입이 같아야 한다
- **UNION ALL** — 두 SELECT 결과를 중복 행까지 하나도 빼지 않고 그대로 이어 붙이는 연산자
- **INTERSECT** — 두 SELECT 결과에 공통으로 들어 있는 행만 돌려주는 연산자
- **EXCEPT (MINUS)** — 첫 번째 SELECT 결과에서 두 번째 결과에 있는 행을 뺀 나머지만 돌려주는 연산자. 오라클에서는 다른 키워드를 쓴다

## 조인

- **내부 조인 (Inner Join)** — 두 테이블에서 결합 조건을 만족하는 행끼리만 짝지어 돌려주는 방식. 등호(=)로 비교하는 동등 결합이 대표적이다
- **왼쪽 외부 조인 (Left Outer Join)** — FROM 절에 먼저 쓴 테이블의 모든 행을 남기고, 짝이 없는 상대 테이블 쪽 컬럼은 NULL로 채워 결합하는 방식
- **오른쪽 외부 조인 (Right Outer Join)** — JOIN 뒤에 쓴 테이블의 모든 행을 남기고, 짝이 없는 앞 테이블 쪽 컬럼은 NULL로 채워 결합하는 방식
- **완전 외부 조인 (Full Outer Join)** — 양쪽 테이블의 모든 행을 남기고 어느 쪽이든 짝이 없으면 상대 컬럼을 NULL로 채우는 방식
- **자연 조인 (Natural Join)** — 두 테이블에서 이름이 같은 컬럼을 기준으로 동등 결합하고, 그 공통 컬럼은 결과에 한 번만 보여 주는 방식
- **셀프 조인 (Self Join)** — 하나의 테이블에 별칭을 둘 붙여 자기 자신과 결합하는 방식
  - 예: 같은 사원 테이블에서 사원과 그 상사 찾기
- **교차 조인 (Cross Join)** — 결합 조건 없이 두 테이블의 모든 행을 서로 짝지어 행 수의 곱만큼 결과를 만드는 방식. 카티션 프로덕트와 같다
- Q: 왼쪽 외부 조인 문법 — `SELECT * FROM 학생 S LEFT OUTER JOIN 수강 C ON S.학번 = C.학번;`

## 절차형·프로그래밍 SQL

- **절차형 SQL (Procedural SQL)** — DBMS 안에서 변수·조건문·반복문 같은 프로그래밍 요소를 질의문과 함께 써서 일련의 작업을 처리하는 언어. DECLARE·BEGIN·END 블록으로 구성한다
- **프로시저 (Procedure)** — 자주 쓰는 일련의 작업을 미리 만들어 DB에 두고 CALL이나 EXECUTE로 호출해 실행하는 절차형 객체. 반환값이 필수는 아니다
- **사용자 정의 함수 (User-Defined Function)** — 절차형으로 작성하며 RETURN으로 반드시 단일 값을 돌려주는 객체. SELECT 같은 질의문 안에서 호출해 쓴다
- **트리거 (Trigger)** — 특정 테이블에 데이터 변경 이벤트가 생기면 자동으로 실행되는 절차형 객체. 무결성 유지·로그 기록에 쓰며 안에서 COMMIT·ROLLBACK을 쓸 수 없다
- Q: 트리거를 실행시키는 이벤트 종류 — INSERT, UPDATE, DELETE
  - 실행 시점은 BEFORE 또는 AFTER, 행마다 실행하려면 FOR EACH ROW
- **내장 SQL (Embedded SQL)** — C·Java 같은 호스트 언어 프로그램 안에 질의문을 넣어 실행하는 방식. EXEC SQL로 시작하고 호스트 변수 앞에는 콜론(:)을 붙인다
- **동적 SQL (Dynamic SQL)** — 실행 시점에 질의문을 문자열로 조립해 실행하는 방식. 상황마다 조건이 달라지는 질의에 유연하지만 매번 구문 분석이 필요하다
