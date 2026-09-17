#!/usr/bin/env python3
"""스펙 문서 문체 검사. 위반이 있으면 종료 코드 1."""
import re
import sys

SYMBOLS = {"·": "가운데점", "—": "줄표", "–": "줄표"}
CIRCLED = re.compile("[①-⑳❶-❿]")
BANNED_WORDS = ["미결", "누락", "누수", "선제", "고지", "제고", "도모", "요건", "상기",
                "하였습니다", "되었습니다", "따라서", "그러므로", "아울러"]
ENDING = re.compile(r"습니다\.?\s*$")
LABEL = re.compile(r"맥락\s*:")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
ALLOWED_EMOJI = {"⚠", "\U0001F4D8"}  # ⚠ 📘
URL = re.compile(r"https?://\S+")
INLINE_CODE = re.compile(r"`[^`]*`")


def check(path):
    issues = []
    in_code = False
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            text = INLINE_CODE.sub("", URL.sub("", line))
            for sym, name in SYMBOLS.items():
                if sym in text:
                    issues.append((n, name, sym))
            if CIRCLED.search(text):
                issues.append((n, "원형 숫자", CIRCLED.search(text).group()))
            for w in BANNED_WORDS:
                if w in text:
                    issues.append((n, "금지어", w))
            if ENDING.search(text):
                issues.append((n, "습니다체", text.strip()[-20:]))
            if LABEL.search(text):
                issues.append((n, "라벨", "맥락:"))
            for m in EMOJI.finditer(text):
                if m.group() not in ALLOWED_EMOJI:
                    issues.append((n, "이모지", m.group()))
    return issues


def main():
    if len(sys.argv) < 2:
        print("사용법: lint_spec.py <file.md> [...]")
        return 2
    total = 0
    for path in sys.argv[1:]:
        for n, kind, what in check(path):
            print(f"{path}:{n}: {kind}: {what}")
            total += 1
    if total:
        print(f"위반 {total}건")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
