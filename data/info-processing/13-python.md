# Python

## 자료형과 연산

- Q: `17 // 5`의 값은? — `3`
- Q: `-17 // 5`의 값은? — `-4`
  - 몫을 음의 무한대 방향으로 내린다(0 방향 버림이 아니다).
- Q: `-17 % 5`의 값은? — `3`
  - 나머지의 부호는 나누는 수의 부호를 따른다.
- Q: `2 ** 3 ** 2`의 값은? — `512`
  - 거듭제곱은 오른쪽부터 묶어 `3 ** 2`를 먼저 계산한다.
- Q: `int(-2.7)`의 값은? — `-2`
  - 실수를 정수로 바꿀 때 소수부를 버린다(0 방향).

- Q: 다음 코드의 출력 결과는?
  ```python
  a = 23
  b = 4
  print(a // b, a % b, a / b)
  print(-a // b, -a % b)
  print(2 ** 5 % 7)
  ```
  - 답:
    ```text
    5 3 5.75
    -6 1
    4
    ```
  - `/`는 항상 실수를 돌려주고, `-23 // 4`는 `-5.75`를 내림한 `-6`이다.

- Q: 다음 코드의 출력 결과는?
  ```python
  x = "12"
  y = 3
  print(x * y)
  print(int(x) * y)
  print(str(y) + x)
  print(int(7.99) + float("0.5"))
  ```
  - 답:
    ```text
    121212
    36
    312
    7.5
    ```
  - 문자열에 정수를 곱하면 반복, `+`는 이어 붙이기다.

## print 출력

- **sep 매개변수 (separator parameter)** — print에 넘긴 여러 값 사이에 끼워 넣는 문자열. 기본값은 공백 한 칸 `" "`
- **end 매개변수 (end parameter)** — print가 모든 값을 출력한 뒤 마지막에 붙이는 문자열. 기본값은 줄바꿈 `"\n"`
- Q: `print("a", "b", 3, sep="")`의 출력은? — `ab3`

- Q: 다음 코드의 출력 결과는?
  ```python
  for n in range(1, 4):
      print(n, end="-")
  print("end")
  print("A", "B", "C", sep="/")
  ```
  - 답:
    ```text
    1-2-3-end
    A/B/C
    ```
  - `end`를 바꾸면 줄바꿈이 빠지므로 다음 print가 같은 줄에 이어진다.

- Q: 다음 코드의 출력 결과는?
  ```python
  names = ["kim", "lee", "park"]
  print(*names, sep=", ", end="!\n")
  print(len(names), "명", sep="")
  ```
  - 답:
    ```text
    kim, lee, park!
    3명
    ```
  - `*names`는 리스트를 풀어 값 세 개를 따로 넘긴다.

## 문자열

- **슬라이싱 (slicing)** — `s[시작:끝:간격]`으로 시퀀스의 일부를 잘라 새 객체를 만드는 연산. 끝 위치의 원소는 포함하지 않는다
- **불변 객체 (immutable object)** — 만든 뒤 내용을 바꿀 수 없는 객체. 문자열에 `s[0] = "x"`처럼 대입하면 `TypeError`가 난다
- Q: `"keyboard"[-3]`의 값은? — `"a"`
- Q: `"keyboard"[3:6]`의 값은? — `"boa"`
- Q: `"drawer"[::-1]`의 값은? — `"reward"`
- Q: `"mississippi".find("ss")`의 값은? — `2`
  - 찾는 문자열이 없으면 `-1`을 돌려준다(`index`는 예외를 낸다).

- Q: 다음 코드의 출력 결과는?
  ```python
  word = "ALGORITHM"
  print(word[2:6])
  print(word[-3:])
  print(word[::2])
  print(word[::-1][:3])
  ```
  - 답:
    ```text
    GORI
    THM
    AGRTM
    MHT
    ```
  - `[::-1]`로 뒤집은 `"MHTIROGLA"`에서 앞 세 글자를 자른다.

- Q: 다음 코드의 출력 결과는?
  ```python
  s = "red,green,blue"
  parts = s.split(",")
  print(len(parts), parts[1].upper())
  print("+".join(parts))
  print(s.find("e"), s.find("x"))
  print(s.replace("e", "E", 2))
  ```
  - 답:
    ```text
    3 GREEN
    red+green+blue
    1 -1
    rEd,grEen,blue
    ```
  - `replace`의 세 번째 인자는 앞에서부터 바꿀 최대 횟수다.

- Q: 다음 코드의 출력 결과는?
  ```python
  item = "pen"
  price = 1250
  qty = 3
  print(f"{item}: {price * qty}원")
  print("{1}-{0}-{1}".format("a", "b"))
  print(f"{3.14159:.2f}")
  ```
  - 답:
    ```text
    pen: 3750원
    b-a-b
    3.14
    ```
  - `format`의 `{1}`은 두 번째 인자를 가리키고, `.2f`는 소수 둘째 자리까지 반올림해 표시한다.

## 리스트

- **리스트 컴프리헨션 (list comprehension)** — `[식 for 변수 in 반복 대상 if 조건]` 형태로 새 리스트를 한 줄에 만드는 문법
- **얕은 복사 (shallow copy)** — 바깥 컨테이너만 새로 만들고 안쪽 원소 객체는 원본과 함께 쓰는 사본. `a[:]`·`a.copy()`·`list(a)`가 이에 해당한다
- Q: `a = [0]`일 때 `a.append([1, 2])`와 `a.extend([1, 2])`의 결과는? — `[0, [1, 2]]`와 `[0, 1, 2]`
  - `append`는 인자를 원소 하나로, `extend`는 인자의 원소를 하나씩 붙인다.
- Q: `a.sort()`의 반환값은? — `None`
  - 제자리에서 정렬한다. 정렬된 새 리스트가 필요하면 `sorted(a)`를 쓴다.

- Q: 다음 코드의 출력 결과는?
  ```python
  nums = [5, 2, 8]
  nums.append(1)
  nums.insert(1, 9)
  nums.extend([4, 4])
  print(nums)
  nums.remove(4)
  x = nums.pop()
  y = nums.pop(0)
  print(nums, x, y)
  ```
  - 답:
    ```text
    [5, 9, 2, 8, 1, 4, 4]
    [9, 2, 8, 1] 4 5
    ```
  - `remove`는 값이 같은 첫 원소 하나만 지우고, `pop()`은 마지막 원소를 꺼내 돌려준다.

- Q: 다음 코드의 출력 결과는?
  ```python
  data = [3, 7, 1, 6, 4]
  evens = [v * 10 for v in data if v % 2 == 0]
  print(evens)
  data.sort(reverse=True)
  print(data)
  data.reverse()
  print(data[:2], sorted(evens, reverse=True)[0])
  ```
  - 답:
    ```text
    [60, 40]
    [7, 6, 4, 3, 1]
    [1, 3] 60
    ```
  - `reverse()`는 정렬이 아니라 현재 순서를 뒤집는다.

- Q: 다음 코드의 출력 결과는?
  ```python
  a = [1, 2, [3, 4]]
  b = a
  c = a[:]
  b[0] = 10
  c[1] = 20
  c[2][0] = 30
  print(a)
  print(c)
  print(a is b, a is c)
  ```
  - 답:
    ```text
    [10, 2, [30, 4]]
    [1, 20, [30, 4]]
    True False
    ```
  - `b`는 같은 리스트를 가리키는 이름이고, `c`는 얕은 복사라 안쪽 리스트 `[3, 4]`만 공유한다.

## 튜플·딕셔너리·세트

- **튜플 (tuple)** — 소괄호로 만드는 순서 있는 불변 시퀀스. 원소가 하나면 `(7,)`처럼 쉼표를 붙여야 한다
- Q: `(7)`과 `(7,)`의 자료형은? — `int`, `tuple`
- Q: 딕셔너리 `d`에 없는 키로 `d.get("k", 0)`을 호출하면? — `0`을 돌려준다
  - `d["k"]`로 읽으면 `KeyError`가 난다.
- Q: `{1, 2, 3} & {2, 3, 4}`에 들어 있는 원소는? — `2`, `3`
  - `&` 교집합, `|` 합집합, `-` 차집합, `^` 대칭차집합. 세트의 출력 순서는 보장되지 않는다.

- Q: 다음 코드의 출력 결과는?
  ```python
  score = {"kor": 80, "eng": 95}
  score["math"] = 70
  score["kor"] += 5
  total = 0
  for k, v in score.items():
      total += v
  print(list(score.keys()))
  print(total, score.get("sci", -1), len(score))
  ```
  - 답:
    ```text
    ['kor', 'eng', 'math']
    250 -1 3
    ```
  - 딕셔너리는 넣은 순서를 유지하고, 기존 키에 대입하면 값만 바뀐다.

- Q: 다음 코드의 출력 결과는?
  ```python
  t = (4, 8, 15)
  a, b, c = t
  print(a + c, t[-2], t.count(8))
  s1 = {1, 2, 3, 4}
  s2 = {3, 4, 5}
  print(sorted(s1 | s2), sorted(s1 - s2), len(s1 & s2))
  print(sorted(s1 ^ s2))
  ```
  - 답:
    ```text
    19 8 1
    [1, 2, 3, 4, 5] [1, 2] 2
    [1, 2, 5]
    ```
  - `^`는 어느 한쪽에만 있는 원소를 모은다.

## 제어문

- Q: `for`문에 붙은 `else` 블록은 언제 실행되나? — 반복이 `break` 없이 끝까지 돌았을 때만
- Q: `list(range(10, 0, -3))`의 값은? — `[10, 7, 4, 1]`
  - 끝 값 `0`은 포함하지 않는다.
- Q: `continue`와 `break`의 차이는? — `continue`는 이번 반복의 나머지를 건너뛰고 다음 반복으로, `break`는 반복문 전체를 빠져나간다

- Q: 다음 코드의 출력 결과는?
  ```python
  total = 0
  for i in range(1, 20, 3):
      if i % 2 == 0:
          continue
      if i > 14:
          break
      total += i
  print(total, i)
  ```
  - 답: `21 19`
  - `i`는 1, 4, 7, 10, 13, 16, 19 순서로 바뀌고 짝수는 건너뛰며 19에서 멈춘다.

- Q: 다음 코드의 출력 결과는?
  ```python
  for n in [9, 15, 21, 23]:
      for d in range(2, n):
          if n % d == 0:
              break
      else:
          print(n, "prime")
          break
      print(n, d)
  ```
  - 답:
    ```text
    9 3
    15 3
    21 3
    23 prime
    ```
  - 안쪽 반복이 `break`로 끝나면 `else`를 건너뛰고, 23에서 처음 끝까지 돌아 `else`가 실행된다.

## 함수

- **가변 인자 (variable-length arguments)** — 매개변수 이름 앞에 `*`를 붙여, 개수가 정해지지 않은 위치 인자를 튜플 하나로 묶어 받는 방식
- **람다 식 (lambda expression)** — `def` 없이 키워드 하나와 `인자: 반환식`만으로 만드는 이름 없는 한 줄 함수
- Q: `list(map(lambda x: x + 1, [4, 5, 6]))`의 값은? — `[5, 6, 7]`
- Q: `list(filter(lambda x: x % 3 == 0, range(1, 10)))`의 값은? — `[3, 6, 9]`
- Q: `def f(a=1, b):`로 정의하면? — `SyntaxError`
  - 기본값 있는 매개변수 뒤에 기본값 없는 매개변수를 둘 수 없다.

- Q: 다음 코드의 출력 결과는?
  ```python
  def calc(a, b=2, *rest):
      result = a * b
      for r in rest:
          result += r
      return result

  print(calc(5))
  print(calc(5, 3))
  print(calc(1, 2, 3, 4))
  ```
  - 답:
    ```text
    10
    15
    9
    ```
  - 세 번째 호출에서 `a=1`, `b=2`이고 남은 `3, 4`가 튜플 `rest`로 묶인다.

- Q: 다음 코드의 출력 결과는?
  ```python
  nums = [1, 2, 3, 4, 5, 6]
  sq = list(map(lambda x: x ** 2, nums))
  big = list(filter(lambda x: x > 10, sq))
  f = lambda a, b=10: a + b
  print(sq[-1], big)
  print(f(1), f(1, 2))
  ```
  - 답:
    ```text
    36 [16, 25, 36]
    11 3
    ```
  - `filter`는 조건이 참인 원소만 남긴다.

- Q: 다음 코드의 출력 결과는?
  ```python
  def add(x, box=[]):
      box.append(x)
      return box

  print(add(1))
  print(add(2))
  print(add(3, []))
  print(add(4))
  ```
  - 답:
    ```text
    [1]
    [1, 2]
    [3]
    [1, 2, 4]
    ```
  - 기본값 리스트는 함수를 정의할 때 한 번만 만들어져 호출 사이에 공유된다.

## 클래스

- **생성자 (constructor)** — 객체가 만들어질 때 자동으로 호출되어 인스턴스 속성을 초기화하는 메서드. Python에서는 `__init__(self, ...)`
- **메서드 오버라이딩 (method overriding)** — 자식 클래스가 부모에 있는 같은 이름의 메서드를 다시 정의해 동작을 바꾸는 것
- Q: 인스턴스를 통해 `obj.cnt = 5`처럼 클래스 변수 이름에 대입하면? — 그 인스턴스에만 같은 이름의 인스턴스 변수가 생기고 클래스 변수는 그대로다
- Q: `super().__init__(...)`은 무엇을 하나? — 부모 클래스의 생성자를 호출해 부모 쪽 속성을 초기화한다

- Q: 다음 코드의 출력 결과는?
  ```python
  class Counter:
      def __init__(self, start=0):
          self.value = start

      def up(self, step=1):
          self.value += step
          return self

  c = Counter(3)
  c.up().up(5)
  print(c.value)
  ```
  - 답: `9`
  - `up`이 `self`를 돌려주므로 호출을 이어 붙일 수 있다.

- Q: 다음 코드의 출력 결과는?
  ```python
  class Animal:
      def __init__(self, name):
          self.name = name

      def sound(self):
          return "..."

      def intro(self):
          return self.name + ":" + self.sound()

  class Dog(Animal):
      def sound(self):
          return "woof"

  class Puppy(Dog):
      def __init__(self, name):
          super().__init__(name + "jr")

      def sound(self):
          return super().sound() * 2

  for a in [Animal("x"), Dog("bo"), Puppy("bo")]:
      print(a.intro())
  ```
  - 답:
    ```text
    x:...
    bo:woof
    bojr:woofwoof
    ```
  - `intro` 안의 `self.sound()`는 실제 객체의 클래스에서 오버라이딩된 메서드를 부른다.

- Q: 다음 코드의 출력 결과는?
  ```python
  class Ticket:
      issued = 0

      def __init__(self):
          Ticket.issued += 1
          self.no = Ticket.issued

  t1 = Ticket()
  t2 = Ticket()
  t2.issued = 100
  t3 = Ticket()
  print(t1.no, t2.no, t3.no)
  print(Ticket.issued, t1.issued, t2.issued)
  ```
  - 답:
    ```text
    1 2 3
    3 3 100
    ```
  - `t2.issued = 100`은 `t2`에만 인스턴스 변수를 만들고 클래스 변수 `Ticket.issued`는 계속 늘어난다.
