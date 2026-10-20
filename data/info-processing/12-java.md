# Java

## 자료형·형변환·연산자

- **묵시적 형변환 (Implicit Casting)** — 표현 범위가 좁은 타입의 값이 넓은 타입으로 컴파일러에 의해 자동으로 바뀌는 것. byte → short → int → long → float → double 방향으로 일어난다.
- **명시적 형변환 (Explicit Casting)** — 값 앞에 `(타입)`을 붙여 넓은 타입을 좁은 타입으로 강제로 바꾸는 것. 실수를 정수로 바꾸면 소수부를 버린다.
- Q: Java의 기본 자료형(primitive type) 8가지는? — byte, short, int, long, float, double, char, boolean
  - 크기는 플랫폼과 무관하게 고정이다(int 4바이트, char 2바이트, long 8바이트).
- Q: `7 / 2`, `7 % 2`, `-7 / 2`, `-7 % 2`의 값은? — `3`, `1`, `-3`, `-1`
  - 정수끼리 나누면 몫의 소수부를 0 쪽으로 버리고, 나머지의 부호는 왼쪽 피연산자를 따른다.
- **단락 평가 (Short-circuit Evaluation)** — 논리 AND(`&&`)·논리 OR(`||`) 연산에서 왼쪽 피연산자만으로 결과가 정해지면 오른쪽 식을 아예 계산하지 않는 방식. 비트 연산자 `&`로 쓰면 양쪽을 모두 계산한다.
- Q: `>>`와 `>>>`의 차이는? — `>>`는 빈 왼쪽 비트를 부호 비트로 채우고, `>>>`는 0으로 채운다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int a = 17, b = 5;
          double r1 = a / b;
          double r2 = (double) a / b;
          int r3 = (int) 7.9 + a % b;
          System.out.println(r1 + " " + r2 + " " + r3);
          char ch = 'a';
          ch += 3;
          System.out.println(ch + " " + (int) ch);
      }
  }
  ```
  - 답:
    ```text
    3.0 3.4 9
    d 100
    ```
  - `a / b`는 정수 나눗셈 3이 먼저 나온 뒤 double로 바뀌어 3.0이 되고, `(int) 7.9`는 7이 된다. char에 `+=`를 쓰면 자동으로 char로 되돌아간다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int x = 4;
          int y = x++ * 2;
          int z = ++x + y;
          System.out.println(x + "," + y + "," + z);
      }
  }
  ```
  - 답: `6,8,14`
  - 후위 `x++`는 기존 값 4로 곱한 뒤 x를 5로 올리고, 전위 `++x`는 6으로 올린 뒤 더한다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int p = 12, q = 10;
          System.out.println((p & q) + " " + (p | q) + " " + (p ^ q));
          System.out.println(~p);
          System.out.println((p << 2) + " " + (-16 >> 2) + " " + (-16 >>> 28));
      }
  }
  ```
  - 답:
    ```text
    8 14 6
    -13
    48 -4 15
    ```
  - 12는 1100, 10은 1010이다. `~p`는 `-(p+1)`이고, `-16 >>> 28`은 상위 4비트 1111만 남아 15가 된다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int count = 0;
          int n = 3;
          if (n > 5 && ++count > 0) {
              n += 10;
          }
          if (n < 5 || ++count > 0) {
              n += 1;
          }
          if (n > 0 & ++count > 0) {
              n += 2;
          }
          System.out.println(n + " " + count);
      }
  }
  ```
  - 답: `6 1`
  - 첫 `&&`는 왼쪽이 거짓, 둘째 `||`는 왼쪽이 참이라 `++count`가 실행되지 않는다. 단락 평가가 없는 `&`에서만 count가 오른다.

## 문자열

- **문자열 상수 풀 (String Constant Pool)** — 내용이 같은 리터럴을 객체 하나로 공유하도록 JVM이 따로 관리하는 영역. `new String(...)`은 이곳을 쓰지 않고 새 객체를 만든다.
- Q: 두 문자열의 내용이 같은지 비교하는 메서드는? — `equals()`
  - `==`는 두 변수가 같은 객체를 가리키는지(참조)를 비교한다.
- Q: `String`이 불변(immutable)이라는 뜻은? — 한 번 만든 문자열 객체의 내용은 바뀌지 않는다.
  - `toUpperCase()`·`substring()`·`concat()`은 원본을 고치지 않고 새 객체를 돌려준다.
- Q: 배열의 길이와 문자열의 길이를 구하는 방법은? — 배열은 `arr.length`(필드), 문자열은 `s.length()`(메서드)

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          String a = "java";
          String b = "java";
          String c = new String("java");
          String d = "ja" + "va";
          String part = "ja";
          String e = part + "va";
          System.out.println((a == b) + " " + (a == c) + " " + a.equals(c));
          System.out.println((a == d) + " " + (a == e) + " " + a.equals(e));
      }
  }
  ```
  - 답:
    ```text
    true false true
    true false true
    ```
  - `"ja" + "va"`는 컴파일 시점에 합쳐지는 상수라 풀의 객체를 공유하지만, 변수가 섞인 연결은 실행 중에 새 객체를 만든다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          String s = "Programming";
          System.out.println(s.length());
          System.out.println(s.charAt(3));
          System.out.println(s.substring(3, 7));
          System.out.println(s.indexOf('m'));
          System.out.println(s.toUpperCase().substring(8));
      }
  }
  ```
  - 답:
    ```text
    11
    g
    gram
    6
    ING
    ```
  - 인덱스는 0부터 센다. `substring(3, 7)`은 끝 인덱스 7을 포함하지 않고, `indexOf`는 처음 나온 위치를 돌려준다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int a = 3, b = 4;
          System.out.println(a + b + "X" + a + b);
          System.out.println("X" + a * b);
          System.out.println('A' + 1 + "B");
          System.out.println("" + 'A' + 1);
      }
  }
  ```
  - 답:
    ```text
    7X34
    X12
    66B
    A1
    ```
  - `+`는 왼쪽부터 계산하므로 문자열이 나오기 전까지는 숫자 덧셈이다. char `'A'`는 숫자 65로 더해진다.

## 배열·제어문

- Q: `int[] a = new int[3];`처럼 만든 배열의 원소 초기값은? — `0`
  - boolean 배열은 `false`, 참조형(String 등) 배열은 `null`로 채워진다.
- Q: 배열의 범위를 벗어난 인덱스에 접근하면? — `ArrayIndexOutOfBoundsException`이 발생한다.
- **폴스루 (Fall-through)** — switch에서 `break` 없이 끝난 case 다음의 case 문장들이 조건 검사 없이 이어서 실행되는 현상.
- Q: 라벨 없는 `break`와 `continue`의 차이는? — `break`는 가장 안쪽 반복문(또는 switch)을 빠져나가고, `continue`는 가장 안쪽 반복문의 다음 회차로 넘어간다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int[] arr = {5, 3, 8, 1, 9, 2};
          int sum = 0;
          for (int i = 0; i < arr.length; i += 2) {
              sum += arr[i];
          }
          int[] ref = arr;
          ref[0] = 100;
          System.out.println(sum + " " + arr[0] + " " + arr.length);

          int[][] m = new int[3][4];
          for (int i = 0; i < 3; i++) {
              for (int j = 0; j < 4; j++) {
                  m[i][j] = i * 4 + j;
              }
          }
          int t = 0;
          for (int i = 0; i < m.length; i++) {
              t += m[i][i];
          }
          System.out.println(m.length + " " + m[0].length + " " + t + " " + m[2][3]);
      }
  }
  ```
  - 답:
    ```text
    22 100 6
    3 4 15 11
    ```
  - `ref = arr`는 배열을 복사하지 않고 같은 배열을 가리키게 한다. `m.length`는 행 수, `m[0].length`는 열 수이다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int[] keys = {2, 4, 7};
          for (int i = 0; i < keys.length; i++) {
              int total = 0;
              switch (keys[i]) {
                  case 1:
                      total += 1;
                  case 2:
                      total += 10;
                  case 3:
                      total += 100;
                      break;
                  case 4:
                      total += 1000;
                  default:
                      total += 5;
              }
              System.out.println(total);
          }
      }
  }
  ```
  - 답:
    ```text
    110
    1005
    5
    ```
  - 2는 case 2부터 break가 있는 case 3까지 실행되고, 4는 break가 없어 default까지 내려간다. 7은 맞는 case가 없어 default만 실행된다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int s = 0;
          for (int i = 1; i <= 10; i++) {
              if (i % 3 == 0) {
                  continue;
              }
              if (i > 8) {
                  break;
              }
              s += i;
          }
          int c = 0;
          for (int i = 0; i < 3; i++) {
              for (int j = 0; j < 5; j++) {
                  if (j == 2) {
                      break;
                  }
                  c++;
              }
          }
          System.out.println(s + " " + c);
      }
  }
  ```
  - 답: `27 6`
  - s는 3의 배수를 건너뛴 1, 2, 4, 5, 7, 8의 합이다. 안쪽 `break`는 안쪽 반복만 끝내므로 바깥 3회마다 c가 2씩 오른다.

## 클래스와 객체·static

- **생성자 (Constructor)** — 클래스 이름과 같고 반환 타입이 없으며, `new`로 객체를 만들 때 자동으로 한 번 호출되는 초기화용 블록.
- Q: 생성자를 하나라도 직접 정의하면 매개변수 없는 기본 생성자는? — 자동으로 만들어지지 않는다.
  - 그래서 `A(int n)`만 있는 클래스에 `new A()`를 쓰면 컴파일 오류가 난다.
- Q: `this`와 `this(...)`의 차이는? — `this`는 현재 객체 자신의 참조, `this(...)`는 같은 클래스의 다른 생성자를 호출하는 문장이다.
  - `this(...)`는 생성자의 첫 줄에만 쓸 수 있다.
- **클래스 변수 (static variable)** — 인스턴스마다 따로 생기지 않고 하나만 만들어져 모든 객체가 공유하는 필드. `클래스명.이름`으로 접근한다.
- Q: static 메서드 안에서 인스턴스 필드를 바로 쓸 수 있는가? — 쓸 수 없다.
  - static 메서드는 객체 없이 호출되므로 `this`가 없다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Box {
      int w, h;

      Box() {
          this(1);
          System.out.print("A");
      }

      Box(int w) {
          this(w, w * 2);
          System.out.print("B");
      }

      Box(int w, int h) {
          this.w = w;
          this.h = h;
          System.out.print("C");
      }

      int area() {
          return w * h;
      }
  }

  public class Main {
      public static void main(String[] args) {
          Box b1 = new Box();
          System.out.println();
          Box b2 = new Box(3);
          System.out.println();
          System.out.println(b1.area() + b2.area());
      }
  }
  ```
  - 답:
    ```text
    CBA
    CB
    20
    ```
  - `this(...)`로 넘어간 생성자가 먼저 끝까지 실행된 뒤 호출한 쪽의 나머지 문장이 실행되므로 C가 가장 먼저 찍힌다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Counter {
      static int total = 0;
      int mine = 0;

      Counter() {
          total++;
          mine++;
      }

      static int twice() {
          return total * 2;
      }
  }

  public class Main {
      public static void main(String[] args) {
          Counter a = new Counter();
          Counter b = new Counter();
          Counter c = new Counter();
          a.mine += 5;
          System.out.println(a.mine + " " + b.mine + " " + Counter.total + " " + Counter.twice());
      }
  }
  ```
  - 답: `6 1 3 6`
  - total은 세 객체가 공유해 3이 되고, mine은 객체마다 따로라 a만 6이다.

## 상속

- **상속 (Inheritance)** — 기존 클래스의 필드와 메서드를 물려받아 새 클래스를 정의하는 것. Java 클래스는 `extends`로 부모를 하나만 가질 수 있다.
- Q: 자식 생성자 첫 줄에 `super(...)`나 `this(...)`가 없으면? — 컴파일러가 `super()`를 자동으로 넣는다.
  - 이때 부모에 매개변수 없는 생성자가 없으면 컴파일 오류다.
- Q: 자식 객체를 만들 때 생성자 본문이 실행되는 순서는? — 최상위 부모부터 자식 순서로 실행된다.
- Q: `final` 클래스와 `final` 메서드의 의미는? — `final` 클래스는 상속할 수 없고, `final` 메서드는 오버라이딩할 수 없다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Base {
      Base() {
          System.out.print("1");
      }

      Base(int n) {
          System.out.print("2");
      }
  }

  class Mid extends Base {
      Mid() {
          System.out.print("3");
      }

      Mid(int n) {
          super(n);
          System.out.print("4");
      }
  }

  class Leaf extends Mid {
      Leaf() {
          super(7);
          System.out.print("5");
      }

      Leaf(int n) {
          System.out.print("6");
      }
  }

  public class Main {
      public static void main(String[] args) {
          new Leaf();
          System.out.println();
          new Leaf(1);
          System.out.println();
      }
  }
  ```
  - 답:
    ```text
    245
    136
    ```
  - `Leaf()`는 `super(7)`로 `Mid(int)`를, 그것은 `super(n)`으로 `Base(int)`를 부른다. `Leaf(int)`는 첫 줄이 비어 있어 `super()`가 들어가 `Mid()`와 `Base()`를 거친다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Robot {
      String name() {
          return "robot";
      }

      String hello() {
          return "I am " + name();
      }
  }

  class Cleaner extends Robot {
      String name() {
          return "cleaner";
      }

      String hello() {
          return super.hello() + "!";
      }
  }

  public class Main {
      public static void main(String[] args) {
          Robot r = new Cleaner();
          System.out.println(r.hello());
      }
  }
  ```
  - 답: `I am cleaner!`
  - `super.hello()`는 부모의 hello를 실행하지만, 그 안의 `name()` 호출은 실제 객체인 Cleaner의 메서드로 연결된다.

## 오버로딩·오버라이딩·다형성

- **오버로딩 (Overloading)** — 한 클래스 안에서 이름은 같고 매개변수의 개수·타입·순서가 다른 메서드를 여러 개 정의하는 것. 반환 타입만 다르면 성립하지 않는다.
- **오버라이딩 (Overriding)** — 부모에게 물려받은 메서드를 자식 클래스에서 이름·매개변수·반환 타입을 똑같이 하여 다시 정의하는 것.
- **업캐스팅 (Upcasting)** — 자식 객체를 부모 타입의 변수로 참조하는 것. 형변환 표기 없이 자동으로 된다.
- **동적 바인딩 (Dynamic Binding)** — 호출할 메서드 본체를 선언 타입이 아니라 실행 시점의 실제 객체 타입을 보고 결정하는 것.
- Q: 부모 타입 변수로 부모·자식에 같은 이름으로 있는 필드에 접근하면 어느 값이 나오는가? — 선언 타입(부모)의 필드 값
  - 필드와 static 메서드는 오버라이딩되지 않고, 인스턴스 메서드만 실제 객체 기준으로 호출된다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Parent {
      int v = 10;

      int get() {
          return v;
      }

      static String tag() {
          return "P";
      }
  }

  class Child extends Parent {
      int v = 20;

      int get() {
          return v;
      }

      static String tag() {
          return "C";
      }
  }

  public class Main {
      public static void main(String[] args) {
          Parent p = new Child();
          System.out.println(p.v + " " + p.get() + " " + ((Child) p).v);
          System.out.println(p.tag());
      }
  }
  ```
  - 답:
    ```text
    10 20 20
    P
    ```
  - `p.v`는 선언 타입 Parent의 필드, `p.get()`은 Child의 메서드이다. static 메서드 `tag()`도 선언 타입을 따라 Parent의 것이 호출된다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class Printer {
      void show(int x) {
          System.out.println("int " + x);
      }

      void show(double x) {
          System.out.println("double " + x);
      }

      void show(Object o) {
          System.out.println("Object " + o);
      }
  }

  public class Main {
      public static void main(String[] args) {
          Printer pr = new Printer();
          pr.show(5);
          pr.show(5L);
          pr.show('A');
          pr.show("hi");
      }
  }
  ```
  - 답:
    ```text
    int 5
    double 5.0
    int 65
    Object hi
    ```
  - 정확히 맞는 타입이 없으면 자동 형변환이 가능한 가장 가까운 메서드가 선택된다. long은 double로, char는 int로 넓어진다.

- Q: 다음 코드의 출력 결과는?
  ```java
  class A {
      String f(A a) {
          return "AA";
      }
  }

  class B extends A {
      String f(A a) {
          return "BA";
      }

      String f(B b) {
          return "BB";
      }
  }

  public class Main {
      public static void main(String[] args) {
          A x = new B();
          B y = new B();
          System.out.println(x.f(y) + " " + y.f(y) + " " + y.f(x));
      }
  }
  ```
  - 답: `BA BB BA`
  - 어떤 시그니처를 부를지는 컴파일 시점에 선언 타입으로 정하고, 그 시그니처의 본체는 실행 시점에 실제 객체로 정한다. `x.f(y)`는 A에 있는 `f(A)`로 정해진 뒤 B가 오버라이딩한 것이 실행된다.

## 추상 클래스·인터페이스

- **추상 클래스 (Abstract Class)** — 선언에 `abstract`가 붙어 직접 `new`로 객체를 만들 수 없고, 몸체 없는 메서드를 포함할 수 있는 미완성 설계도. 자식이 빈 메서드를 모두 구현해야 객체를 만들 수 있다.
- **인터페이스 (Interface)** — 구현할 메서드의 이름과 형식만 정해 둔 규격. 한 클래스가 `implements`로 여러 개를 동시에 구현할 수 있다.
- Q: 인터페이스에 선언한 필드는 자동으로 어떤 제어자가 붙는가? — `public static final` (상수)
  - 인터페이스의 몸체 없는 메서드는 `public abstract`가 생략된 것이라, 구현 클래스에서 `public`으로 오버라이딩해야 한다.

- Q: 다음 코드의 출력 결과는?
  ```java
  interface Payable {
      int fee();
  }

  abstract class Ticket implements Payable {
      protected int base;

      Ticket(int base) {
          this.base = base;
      }

      abstract int discount();

      public int fee() {
          return base - discount();
      }
  }

  class Student extends Ticket {
      Student() {
          super(10000);
      }

      int discount() {
          return base / 4;
      }
  }

  class Senior extends Ticket {
      Senior() {
          super(10000);
      }

      int discount() {
          return 6000;
      }

      public int fee() {
          return super.fee() + 500;
      }
  }

  public class Main {
      public static void main(String[] args) {
          Payable[] list = {new Student(), new Senior(), new Student()};
          int sum = 0;
          for (int i = 0; i < list.length; i++) {
              sum += list[i].fee();
          }
          System.out.println(list[0].fee() + " " + list[1].fee() + " " + sum);
      }
  }
  ```
  - 답: `7500 4500 19500`
  - Student는 10000 - 2500, Senior는 부모 fee 4000에 500을 더한다. 인터페이스 타입 배열로 불러도 각 객체의 메서드가 실행된다.

## 예외 처리

- Q: `finally` 블록은 언제 실행되는가? — 예외 발생 여부와 관계없이 항상 실행된다.
  - try나 catch 안에서 `return`을 만나도, 값을 돌려주기 전에 finally가 먼저 실행된다.
- Q: catch 블록을 여러 개 둘 때 순서 규칙은? — 자식 예외를 먼저, 부모 예외를 나중에 둔다.
  - 부모(예: `Exception`)를 앞에 두면 뒤의 catch에 도달할 수 없어 컴파일 오류가 난다.
- Q: checked 예외와 unchecked 예외의 차이는? — checked는 컴파일러가 try-catch나 throws 처리를 강제하고, unchecked(RuntimeException 계열)는 강제하지 않는다.
  - 예: `IOException`은 checked, `ArithmeticException`·`NullPointerException`은 unchecked.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      static int run(int n) {
          try {
              System.out.print("T");
              int r = 10 / n;
              System.out.print("R");
              return r;
          } catch (ArithmeticException e) {
              System.out.print("C");
              return -1;
          } finally {
              System.out.print("F");
          }
      }

      public static void main(String[] args) {
          int a = run(2);
          System.out.println(" " + a);
          int b = run(0);
          System.out.println(" " + b);
      }
  }
  ```
  - 답:
    ```text
    TRF 5
    TCF -1
    ```
  - `10 / 0`에서 예외가 나면 그 아래 R은 건너뛰고 catch로 간다. 두 경우 모두 return 직전에 finally의 F가 찍힌다.

- Q: 다음 코드의 출력 결과는?
  ```java
  public class Main {
      public static void main(String[] args) {
          int[] data = {1, 2, 3};
          String out = "";
          for (int i = 2; i <= 4; i++) {
              try {
                  if (i == 4) {
                      throw new IllegalStateException();
                  }
                  out += data[i];
                  out += "a";
              } catch (ArrayIndexOutOfBoundsException e) {
                  out += "b";
              } catch (RuntimeException e) {
                  out += "c";
              } finally {
                  out += "d";
              }
          }
          System.out.println(out);
      }
  }
  ```
  - 답: `3adbdcd`
  - catch는 위에서부터 처음 맞는 하나만 실행된다. i가 3이면 인덱스 초과로 b, 4이면 직접 던진 IllegalStateException이 RuntimeException에 잡혀 c가 붙는다.
