#!/usr/bin/env python3
"""카드 데이터 검사. 저장소 루트에서 실행한다.

    python3 tools/check.py            # 세 가지 전부
    python3 tools/check.py --no-code  # 코드 실행은 건너뛰기 (빠름)

1. 형식      — Markdown이 assets/app.js 파서가 읽는 규칙을 지키나
2. 덱 일치   — decks.json · deck.json · 페이지 · 파일 목록이 서로 맞나
3. 코드 답   — 코드 읽기 문제를 실제로 실행한 출력이 「답」과 같나

문제가 있으면 종료 코드 1. GitHub Actions에서는 파일·줄 위치가 주석으로 붙는다.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"
errors = 0


def fail(msg, path=None, line=None):
    global errors
    errors += 1
    where = ""
    if path is not None:
        rel = Path(path).resolve().relative_to(ROOT)
        where = f"{rel}:{line}: " if line else f"{rel}: "
        if IN_CI:
            loc = f"file={rel}" + (f",line={line}" if line else "")
            print(f"::error {loc}::{msg}")
            return
    print(f"  ✗ {where}{msg}")


# ── 1. 형식 ────────────────────────────────────────────────────────────
# 규칙은 assets/app.js의 parseDeck과 같다.
T_LINE = re.compile(r"^- \*\*(.+?)\*\* — (.*)$")
Q_LINE = re.compile(r"^- Q: (.+?) — (.*)$")
Q_CODE = re.compile(r"^- Q: (.+)$")
FENCE = re.compile(r"^( {2,})```(\w*)$")
ANSWER = re.compile(r"^ {2,}- 답:\s*(.*)$")
EXTRA = re.compile(r"^ {2,}- (.*)$")
LANGS = {"c", "java", "python", "text"}


def parse(path):
    """카드 목록을 돌려준다. 형식 오류는 바로 보고한다."""
    cards, cur, fence = [], None, None
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or not lines[0].startswith("# "):
        fail("첫 줄은 `# 과목 이름`이어야 한다", path, 1)
    for no, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if fence:
            if line.strip() == "```":
                fence = None
            else:
                if "\t" in raw:
                    fail("코드에 탭이 있다 (공백 4칸으로)", path, no)
                ind = min(fence["indent"], len(line) - len(line.lstrip()))
                cur[fence["key"]].append(line[ind:])
            continue
        if raw != line:
            fail("줄 끝 공백", path, no)
        if not line.strip() or line.startswith("# ") or line.startswith("## ") or line.startswith(">"):
            if line.startswith("## ") or line.startswith("# "):
                cur = None
            continue
        if m := T_LINE.match(line):
            cur = {"kind": "T", "line": no, "a": m[1], "b": m[2], "ans": True}
        elif m := Q_LINE.match(line):
            cur = {"kind": "Q", "line": no, "a": m[1], "b": m[2], "ans": True}
        elif m := Q_CODE.match(line):
            cur = {"kind": "Q", "line": no, "a": m[1], "b": "", "ans": False,
                   "lang": None, "code": [], "ansblock": [], "answer": None}
        elif cur and (m := FENCE.match(line)):
            lang = m[2]
            if lang not in LANGS:
                fail(f"코드 블록 언어 `{lang or '(없음)'}` — {', '.join(sorted(LANGS))} 중 하나", path, no)
            if not cur["ans"] and "code" in cur and not cur["code"]:
                cur["lang"] = lang
                fence = {"indent": len(m[1]), "key": "code"}
            elif cur.get("answer") == "" and "ansblock" in cur:
                fence = {"indent": len(m[1]), "key": "ansblock"}
            else:
                fail("코드 블록 위치가 이상하다 (문제 코드 하나, 「- 답:」 아래 블록 하나만)", path, no)
                fence = {"indent": len(m[1]), "key": "_skip"}
                cur.setdefault("_skip", [])
            continue
        elif cur and cur["kind"] == "Q" and not cur["ans"] and (m := ANSWER.match(line)):
            cur["ans"] = True
            cur["answer"] = m[1].strip()
            continue
        elif cur and EXTRA.match(line):
            continue
        else:
            fail("읽을 수 없는 줄 — `- **용어** — 정의` · `- Q: 질문 — 답` · `- Q: 질문`(코드 문제) 중 하나여야 한다", path, no)
            continue
        cards.append(cur)
    if fence:
        fail("닫히지 않은 코드 블록", path, len(lines))
    for c in cards:
        if not c["ans"]:
            fail(f"답이 없는 문제: {c['a'][:40]}", path, c["line"])
        elif "code" in c:
            if not c["code"]:
                fail("코드 문제인데 코드 블록이 없다", path, c["line"])
            if not c["answer"] and not c["ansblock"]:
                fail("「- 답:」이 비어 있고 아래 블록도 없다", path, c["line"])
        if c["kind"] == "T":
            core = re.split(r"\s*[(（]", c["a"])[0].strip()
            if len(core) >= 2 and core in c["b"]:
                fail(f"정의에 용어가 그대로 들어 있다 ({core}) — 정답이 보인다", path, c["line"])
    return cards


# ── 2. 덱 일치 ─────────────────────────────────────────────────────────
def check_decks():
    decks = []
    try:
        ids = json.loads((DATA / "decks.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        fail(f"data/decks.json을 읽지 못했다: {e}")
        return decks
    if len(ids) != len(set(ids)):
        fail("decks.json에 같은 이름이 두 번 있다", DATA / "decks.json")
    for did in ids:
        folder, page = DATA / did, ROOT / did / "index.html"
        dj = folder / "deck.json"
        if not dj.exists():
            fail(f"`{did}`: deck.json이 없다", DATA / "decks.json")
            continue
        try:
            info = json.loads(dj.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            fail(f"JSON 형식 오류: {e}", dj)
            continue
        for key in ("title", "files"):
            if not info.get(key):
                fail(f"`{key}`가 없다", dj)
        files = info.get("files", [])
        if len(files) != len(set(files)):
            fail("files에 같은 파일이 두 번 있다", dj)
        for f in files:
            if not (folder / f).exists():
                fail(f"files에 있는 `{f}`가 폴더에 없다", dj)
        for md in sorted(folder.glob("*.md")):
            if md.name not in files:
                fail(f"`{md.name}`이 deck.json files에 없다 — 사이트에 안 보인다", dj)
        if not page.exists():
            fail(f"`{did}/index.html` 페이지가 없다", DATA / "decks.json")
        elif not re.search(r"deck:\s*['\"]" + re.escape(did) + r"['\"]", page.read_text(encoding="utf-8")):
            fail(f"페이지의 window.CERT.deck이 `{did}`가 아니다", page)
        decks.append((did, [folder / f for f in files if (folder / f).exists()]))
    for folder in sorted(p for p in DATA.iterdir() if p.is_dir()):
        if folder.name not in ids:
            fail(f"`{folder.name}` 폴더가 decks.json에 없다 — 첫 화면에 안 보인다", DATA / "decks.json")
    return decks


# ── 3. 코드 답 ─────────────────────────────────────────────────────────
def tool(names, env_dirs=()):
    for d in env_dirs:
        for n in names:
            p = Path(d) / n
            if p.exists():
                return str(p)
    for n in names:
        if shutil.which(n):
            return shutil.which(n)
    return None


CC = tool(["clang", "gcc", "cc"])
JAVA_DIRS = [d for d in (os.environ.get("JAVA_HOME", "") and os.environ["JAVA_HOME"] + "/bin",
                         "/opt/homebrew/opt/openjdk/bin") if d]
JAVAC, JAVA = tool(["javac"], JAVA_DIRS), tool(["java"], JAVA_DIRS)


def run(lang, code, d):
    d = Path(d)
    if lang == "c":
        if not CC:
            return None, "C 컴파일러가 없다"
        (d / "m.c").write_text(code)
        c = subprocess.run([CC, "-std=c11", "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined",
                            "-fno-sanitize-recover=all", "-o", str(d / "m"), str(d / "m.c")],
                           capture_output=True, text=True)
        if c.returncode:
            return None, "컴파일 실패: " + (c.stderr.strip().splitlines() or ["?"])[0]
        cmd, cwd = [str(d / "m")], d
    elif lang == "java":
        if not (JAVAC and JAVA):
            return None, "javac/java가 없다"
        (d / "Main.java").write_text(code)
        c = subprocess.run([JAVAC, "Main.java"], cwd=d, capture_output=True, text=True)
        if c.returncode:
            return None, "컴파일 실패: " + (c.stderr.strip().splitlines() or ["?"])[0]
        cmd, cwd = [JAVA, "Main"], d
    elif lang == "python":
        (d / "m.py").write_text(code)
        cmd, cwd = [sys.executable, "-I", str(d / "m.py")], d
    else:
        return None, f"실행할 수 없는 언어 `{lang}`"
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        return None, "20초 안에 끝나지 않았다"
    if r.returncode or r.stderr.strip():
        return None, f"실행 오류(종료 {r.returncode}): " + (r.stderr.strip().splitlines() or [""])[0]
    return r.stdout, None


def check_code(path, cards):
    n = 0
    for c in cards:
        if "code" not in c or not c["code"] or not c["ans"]:
            continue
        n += 1
        if c["ansblock"]:
            expect = "\n".join(c["ansblock"])
        else:
            a = c["answer"] or ""
            expect = a[1:-1] if a.startswith("`") and a.endswith("`") and a.count("`") == 2 else a
        with tempfile.TemporaryDirectory() as d:
            out, err = run(c["lang"], "\n".join(c["code"]) + "\n", d)
        if err:
            fail(err, path, c["line"])
        elif out.rstrip("\n") != expect.rstrip("\n"):
            fail(f"답이 실행 결과와 다르다 — 적힌 답 {expect!r} / 실행 결과 {out.rstrip()!r}", path, c["line"])
    return n


def main():
    run_code = "--no-code" not in sys.argv
    print("1·2. 덱 일치와 형식")
    decks = check_decks()
    parsed = []
    for did, files in decks:
        total = 0
        for f in files:
            cards = parse(f)
            parsed.append((f, cards))
            total += len(cards)
        print(f"  {did}: 파일 {len(files)}개 · 카드 {total}장")
    if run_code:
        print("3. 코드 답")
        print(f"  C: {CC or '없음'} · Java: {JAVAC or '없음'} · Python: {sys.executable}")
        n = sum(check_code(f, cards) for f, cards in parsed)
        print(f"  코드 문제 {n}개 실행")
    print("통과" if not errors else f"문제 {errors}개")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
