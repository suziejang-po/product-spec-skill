#!/usr/bin/env python3
"""스펙 문서 문체 검사. 위반이 있으면 종료 코드 1.
검사 제외: 코드 블록, 인라인 코드, URL, 따옴표로 감싼 UI 카피와 안내 문구, `<!-- lint-skip -->`가 있는 줄"""
import re
import sys

SYMBOLS = {"·": "가운데점", "—": "줄표", "–": "줄표"}
CIRCLED = re.compile("[①-⑳❶-❿]")
BANNED_WORDS = ["미결", "누락", "누수", "선제", "고지", "제고", "도모", "요건", "상기",
                "하였습니다", "되었습니다", "따라서", "그러므로", "아울러"]
# 앞은 시작, 공백, 여는 괄호, 구두점. 뒤는 끝, 공백, 조사, 구두점. "고지서", "최고지점", "정상기능"은 걸리지 않음
BEFORE = r"(?:^|(?<=[\s(\[\|>,.:;/'\"]))"
AFTER = r"(?=$|[\s)\]\|,.:;/'\"]|은|는|이|가|을|를|의|로|에|와|과|도|만|사항)"
BANNED = {w: re.compile(BEFORE + re.escape(w) + AFTER) for w in BANNED_WORDS}
ENDING = re.compile(r"[가-힣]습니다")
LABEL = re.compile(r"맥락\s*:")
EMOJI = re.compile("[\U0001F300-\U0001FAFF⌀-⏿☀-➿⬀-⯿]")
ALLOWED_EMOJI = {"⚠", "\U0001F4D8"}  # ⚠ 📘
URL = re.compile(r"https?://\S+")
INLINE_CODE = re.compile(r"`[^`]*`")
QUOTED = re.compile(r"'[^']{1,80}'|\"[^\"]{1,160}\"")


def strip(line):
    text = URL.sub("", line)
    text = INLINE_CODE.sub("", text)
    text = QUOTED.sub("''", text)
    return text


def check(path):
    issues = []
    in_code = False
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code or "lint-skip" in line:
                continue
            text = strip(line)
            for sym, name in SYMBOLS.items():
                if sym in text:
                    issues.append((n, name, sym))
            m = CIRCLED.search(text)
            if m:
                issues.append((n, "원형 숫자", m.group()))
            for w, rx in BANNED.items():
                if rx.search(text):
                    issues.append((n, "금지어", w))
            if ENDING.search(text):
                issues.append((n, "습니다체", ENDING.search(text).group()))
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
