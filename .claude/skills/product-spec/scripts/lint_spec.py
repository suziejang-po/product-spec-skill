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
# 은어: 사람이 쓰는 스펙에 나오지 않는 말. 값은 대체 표현
JARGON = {
    "전이": "상태가 바뀌는 때",
    "액션": "동작",
    "인터페이스": "넘기는 방법",
    "카운터": "세기",
    "플래그": "표시",
    "스냅샷": "그 시점 값을 따로 저장",
    "마이그레이션": "데이터 이관",
    "엣지 케이스": "드문 경우",
    "밸리데이션": "검사",
    "큐": "대기 목록",
}
JARGON_EXCEPT = ["액션 시트", "버튼/액션"]  # 실제 컴포넌트 이름, 용어 하위 표 이름
JARGON_AFTER = r"(?=$|[\s)\]\(\|,.:;/'\"]|은|는|이|가|을|를|의|로|에|와|과|도|만|별|적|화)"
JARGON_RX = {w: re.compile(BEFORE + re.escape(w) + JARGON_AFTER) for w in JARGON}
# 문서 안에서 행 번호로 다른 곳을 가리키면 행이 늘 때 전부 어긋남. 화면 이름으로 가리킴
# "구현 상세 14행", "15행 10번", "11행의", "9행 참고"처럼 가리킬 때만. "최대 2행", "2행 3열"은 통과
ROWREF = re.compile(r"(?:구현 상세|표의)\s*\d+\s*행|\d+\s*행\s*(?:\d+\s*번|참고|의\b|에서|처럼)|\d+\s*번\s*행")
# 다른 곳은 "7-2 순위 표 확인"처럼 섹션 번호와 이름을 함께 씀. 문서 안 링크(앵커)는 깨지기 쉬워 쓰지 않음
# "[순위 표](#순위)"처럼 '#'으로 시작하는 링크를 잡음
ANCHORLINK = re.compile(r"\]\(#[^)]*\)")
# 표 셀 안에서 문장을 마침표로 잇지 않음. 한 셀에 정보가 여럿이면 '<br>- ' 불릿, 딸린 내용은 '<br>  - ' 한 단계 아래 불릿
CELLDOT = re.compile(r"\.\s+\S")
LABEL = re.compile(r"맥락\s*:")
# 정해지지 않은 UI 문구 표시는 (문구 워싱 필요)로 통일
DRAFT = re.compile(r"\(문구 초안\)")
EMOJI = re.compile("[\U0001F300-\U0001FAFF⌀-⏿☀-➿⬀-⯿]")
ALLOWED_EMOJI = {"⚠", "\U0001F4D8", "✓", "✔"}  # ⚠ 📘 ✓ ✔
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
            if in_code:
                continue
            skip_kinds = None
            sk = re.search(r"lint-skip(?::\s*([^>]*))?", line)
            if sk:
                kinds = [k.strip() for k in re.split(r"[,\s]+", sk.group(1) or "") if k.strip()]
                skip_kinds = set(kinds) if kinds else set()  # 빈 집합 = 전부 건너뜀
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
            jtext = text
            for ex in JARGON_EXCEPT:
                jtext = jtext.replace(ex, "")
            for w, rx in JARGON_RX.items():
                if rx.search(jtext):
                    issues.append((n, "은어", f"{w} → {JARGON[w]}"))
            m = ROWREF.search(text)
            if m:
                issues.append((n, "행 번호 참조", f"{m.group()} → 화면 이름으로 가리킴"))
            m = ANCHORLINK.search(line)
            if m:
                issues.append((n, "문서 안 링크", f"{m.group()} → '{{무엇}}: {{섹션 번호}} {{섹션 이름}} 확인'"))
            if text.lstrip().startswith("|") and not re.match(r"^\s*\|[\s|:-]+\|\s*$", text):
                for cell in text.strip().strip("|").split("|"):
                    for seg in re.split(r"<br\s*/?>", cell):
                        body = re.sub(r"^\s*(-|\d+\.)\s+", "", seg).strip()
                        m = CELLDOT.search(body)
                        if m:
                            issues.append((n, "셀 안 문장 잇기", f"'{body[:30]}' → 마침표로 잇지 말고 '<br>- ' 불릿으로 나눔"))
                            break
            if LABEL.search(text):
                issues.append((n, "라벨", "맥락:"))
            if DRAFT.search(line):
                issues.append((n, "문구 표시", "(문구 초안) → (문구 워싱 필요)"))
            for m in EMOJI.finditer(text):
                if m.group() not in ALLOWED_EMOJI:
                    issues.append((n, "이모지", m.group()))
            if skip_kinds is not None:
                issues = [i for i in issues if not (i[0] == n and (not skip_kinds or i[1] in skip_kinds))]
    return issues


HEAD = re.compile(r"착수 전 확인 필요\s*(\d+)건,\s*확인 필요 전체\s*(\d+)건")


def check_counts(path):
    """첫 줄 건수와 본문의 ⚠️ 수 대조. 첫 줄 표기가 없으면 검사하지 않음"""
    text = open(path, encoding="utf-8").read()
    m = HEAD.search(text)
    if not m:
        return []
    body = text[m.end():]
    a = body.count("⚠️ 착수 조건")
    total = body.count("⚠️")
    out = []
    if int(m.group(1)) != a:
        out.append((1, "건수 불일치", f"첫 줄 착수 전 {m.group(1)}건, 본문 '⚠️ 착수 조건' {a}건"))
    if int(m.group(2)) != total:
        out.append((1, "건수 불일치", f"첫 줄 전체 {m.group(2)}건, 본문 ⚠️ {total}건"))
    return out


H2 = re.compile(r"^##\s+(\d+)\.\s")
H3 = re.compile(r"^###\s+(\d+)-(\d+)\.\s")


def check_structure(path):
    """v5 번호 뼈대: '## 1. 개요'부터 번호가 커지는 순서, '### N-M.'은 바로 위 '## N.' 아래에서 커지는 순서.
    번호 섹션이 하나도 없으면 v5 양식이 아님"""
    out = []
    last2, last3 = 0, 0
    seen = False
    in_code = False
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = H2.match(line)
        if m:
            k = int(m.group(1))
            if not seen and (k != 1 or "개요" not in line):
                out.append((n, "구조", "첫 번호 섹션은 '## 1. 개요'"))
            if k <= last2:
                out.append((n, "구조", f"섹션 번호 {k}가 앞 번호 {last2}보다 크지 않음"))
            if k > 8:
                out.append((n, "구조", f"최상위 섹션은 8까지 (지금 {k})"))
            seen, last2, last3 = True, k, 0
            continue
        m = H3.match(line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a != last2:
                out.append((n, "구조", f"'{a}-{b}'가 '## {last2}.' 아래에 있음"))
            elif b <= last3:
                out.append((n, "구조", f"하위 번호 {a}-{b}가 앞 번호보다 크지 않음"))
            last3 = b
    if not seen:
        out.append((1, "구조", "번호 섹션 없음. references/template.md의 1~8 뼈대를 씀"))
    return out


def main():
    if len(sys.argv) < 2:
        print("사용법: lint_spec.py <file.md> [...]")
        return 2
    total = 0
    for path in sys.argv[1:]:
        for n, kind, what in check(path) + check_counts(path) + check_structure(path):
            print(f"{path}:{n}: {kind}: {what}")
            total += 1
    if total:
        print(f"위반 {total}건")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
