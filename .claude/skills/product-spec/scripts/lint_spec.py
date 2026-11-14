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
# 다른 곳은 "7-2 신청 취소 확인"처럼 섹션 번호와 이름을 함께 씀. 문서 안 링크(앵커)는 깨지기 쉬워 쓰지 않음
# "[신청 취소](#신청-취소)"처럼 '#'으로 시작하는 링크를 잡음
ANCHORLINK = re.compile(r"\]\(#[^)]*\)")
# 표 셀 안에서 문장을 마침표로 잇지 않음. 한 셀에 정보가 여럿이면 '<br>- ' 불릿, 딸린 내용은 '<br>  - ' 한 단계 아래 불릿
CELLDOT = re.compile(r"\.\s+\S")
LABEL = re.compile(r"맥락\s*:")
# 정해지지 않은 UI 문구 표시는 (문구 워싱 필요)로 통일
DRAFT = re.compile(r"\(문구 초안\)")
# 표시 형태는 디자이너가 정함. 화면 표와 구현 상세에는 무엇을 보여주고 알려야 하는지만 씀
# 기존 화면 이름으로 자주 쓰이는 모달, 팝업, 바텀시트는 잡지 않음
UXFORM = re.compile(r"토스트|아코디언|말줄임|호버|툴팁|스켈레톤|애니메이션|플레이스홀더")
# 수치의 기간, 모수, 쿼리는 본문이 아니라 섹션 끝 '데이터 근거' 펼치기에
EVIDENCE_INLINE = re.compile(r"\((?:BQ|빅쿼리|BigQuery|Amplitude|앰플리튜드)\s*실측")
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
    in_details = False
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if line.strip().startswith("<details"):
                in_details = True
            elif line.strip().startswith("</details"):
                in_details = False
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
            if re.match(r"^\s*[-*]\s+\S", text) and "<!--" not in line and re.search(r"[가-힣a-zA-Z0-9)]\.\s*$", text):
                issues.append((n, "불릿 끝 마침표", "불릿 끝에 마침표를 붙이지 않음"))
            if text.lstrip().startswith("|"):
                m = UXFORM.search(text)
                if m:
                    issues.append((n, "표시 형태", f"'{m.group()}' → 표시 형태는 디자인에서 정함. 무엇을 보여주고 알려야 하는지만 씀 (기존 화면 설명이면 lint-skip: 표시 형태)"))
            if not in_details:
                m = EVIDENCE_INLINE.search(text)
                if m:
                    issues.append((n, "근거 위치", "본문에는 값만. 기간, 모수, 쿼리는 섹션 끝 '데이터 근거' 펼치기에"))
            if re.search(r"\*\*[^*<]{0,10}문구[^*<]{0,10}\*\*", line):
                issues.append((n, "문구 소제목", "'문구' 소제목을 따로 두지 않고 그 문구가 보이는 요소 바로 아래에 씀"))
            if DRAFT.search(line):
                issues.append((n, "문구 표시", "(문구 초안) → (문구 워싱 필요)"))
            for m in EMOJI.finditer(text):
                if m.group() not in ALLOWED_EMOJI:
                    issues.append((n, "이모지", m.group()))
            if skip_kinds is not None:
                issues = [i for i in issues if not (i[0] == n and (not skip_kinds or i[1] in skip_kinds))]
    return issues


HEAD = re.compile(r"확인\s*필요[^|\n]{0,20}?\d+\s*건|\d+\s*건[^|\n]{0,10}?확인\s*필요")
WARN = re.compile("\u26a0(?!\ufe0f?\\s*착수 조건)")


def check_counts(path):
    """v5.1: 문서에 건수 줄을 두지 않고, ⚠️는 '⚠️ 착수 조건:'에만 씀. 나머지 확인 사항은 평문 괄호"""
    out = []
    in_code = False
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or "lint-skip" in line:
            continue
        if HEAD.search(line):
            out.append((n, "건수 줄", "문서에 건수를 쓰지 않음. 채팅 안내로만"))
        text = re.sub(r"<!--.*?-->", "", line)
        if WARN.search(text):
            out.append((n, "확인 표시", "⚠️는 '⚠️ 착수 조건: … → {담당} 확인 필요'에만. 나머지는 '(… 확인 필요)' 평문 괄호"))
    return out


# 결정 과정을 남기는 날짜 표시. "10/16 확정", "2026-10-20 기준", "10월 16일 합의"
DECISION_DATE = re.compile(r"(?:\d{4}[-./])?\d{1,2}[/.월-]\s?\d{1,2}일?\s*(?:확정|정본|기준|결정|합의|변경)")
# 넣지 않는 섹션. 확인 사항은 인라인, 뺀 기능은 언급하지 않음, 데이터 모델과 일정은 스펙 밖
BANNED_H2 = re.compile(r"데이터와\s*API|데이터\s*모델|제외\s*범위|배포|롤백|확인\s*필요|논의|미결|담당과\s*일정|업데이트\s*로그|변경\s*이력|시나리오|향후")
BANNED_H3 = re.compile(r"^(?:확인\s*필요|제외\s*범위|배포와\s*롤백|담당과\s*일정|데이터와\s*API|데이터\s*모델)$")
# 한 문서에 차수가 섞인 표시. "1차 면접" 같은 도메인 말은 잡지 않도록 표시 꼴만 봄
PHASE_MIX = re.compile(r"\[\d+차\]|\d+차\s*,\s*나머지는\s*\d+차|^\d+차\s*[:：]")
PHASE_HEAD = re.compile(r"차수|^\d+차\s*[:：]")
HEAD_ANY = re.compile(r"^(#{2,3})\s+(\d+(?:-\d+)?)\.\s+(.*)$")
TABLE_SEP = re.compile(r"^\s*\|[\s|:-]+\|\s*$")
IMPL_HEADER = ["#", "진입점", "화면", "기능", "요구사항"]
SCREEN_HEADER = ["화면", "진입점", "상세 내용"]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def check_shape(path):
    """양식 검사: 넣지 않는 섹션, 결정 날짜, 문단 서술, 메타의 문서 유형, 구현 상세 5열과 화면 표 3열, 차수 섞임"""
    out = []
    lines = open(path, encoding="utf-8").read().split("\n")
    in_code = in_comment = in_details = False
    h2 = ""          # 지금 있는 '## N.' 제목
    region_first_table = True
    has_impl = has_screen = False
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if "<!--" in s and "-->" not in s:
            in_comment = True
            continue
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if "lint-skip" in line:
            continue
        if s.startswith("<details"):
            in_details = True
        if s.startswith("</details"):
            in_details = False
            continue
        if in_details:
            # 데이터 근거 블록: 'M/D~M/D 기준' 같은 집계 기간과 표는 결정 날짜, 양식 검사 대상이 아님
            continue
        m = HEAD_ANY.match(s)
        if m:
            level, num, title = m.groups()
            if level == "##":
                h2 = title
                if BANNED_H2.search(title):
                    out.append((n, "넣지 않는 섹션", f"'{title}' → 확인 사항은 해당 기능 옆 인라인, 뺀 기능은 언급하지 않음, 데이터 모델과 일정은 메타나 스펙 밖"))
                if "구현 상세" in title:
                    has_impl = True
                if "화면" in title:
                    has_screen = True
            elif BANNED_H3.match(title.strip()):
                out.append((n, "넣지 않는 섹션", f"'{title}'"))
            if PHASE_HEAD.search(title.strip()):
                out.append((n, "차수 섞임", f"'{title}' → 차수마다 문서를 따로 만듦. 문서 하나에 한 차수만"))
            region_first_table = True
            continue
        text = strip(line)
        pm = PHASE_MIX.search(text.lstrip("-* "))
        if pm:
            out.append((n, "차수 섞임", f"'{pm.group()}' → 차수마다 문서를 따로 만듦. 다른 차수 기능은 이 문서에서 지움"))
        m = DECISION_DATE.search(text)
        if m:
            out.append((n, "결정 날짜", f"'{m.group()}' → 결정 과정과 날짜를 쓰지 않고 최종 내용만"))
        if s.startswith("|") and not TABLE_SEP.match(s):
            row = cells(s)
            if row and row[0] == "문서 유형":
                out.append((n, "메타", "문서 유형은 채팅 첫 줄에만. 메타 표에 넣지 않음"))
            nxt = lines[n].strip() if n < len(lines) else ""
            if TABLE_SEP.match(nxt) and region_first_table:   # 표 머리줄
                region_first_table = False
                if "구현 상세" in h2 and row != IMPL_HEADER:
                    out.append((n, "구현 상세 표", f"열이 '{' | '.join(row)}' → '# | 진입점 | 화면 | 기능 | 요구사항' 5열"))
                if ("유저향 화면" in h2 or "어드민" in h2) and row != SCREEN_HEADER:
                    out.append((n, "화면 표", f"열이 '{' | '.join(row)}' → '화면 | 진입점 | 상세 내용' 3열"))
            continue
        # 문단 서술: 목록, 표, 제목, 그림, 인용이 아닌 줄이 긴 완결문이면
        if s and not re.match(r"^([-*>#|!<]|\d+[.)]\s|\[)", s):
            body = text.strip()
            if len(body) >= 40 and (re.search(r"다\.$", body) or len(re.findall(r"[가-힣]\.\s+\S", body)) >= 1):
                out.append((n, "문단 서술", f"'{body[:30]}…' → 개조식 불릿으로 나눔"))
    if not (has_impl or has_screen):
        out.append((1, "구조", "'유저향 화면' 또는 '구현 상세' 섹션이 없음. references/template.md의 섹션 순서를 씀"))
    return out


H2 = re.compile(r"^##\s+(\d+)\.\s")
H3 = re.compile(r"^###\s+(\d+)-(\d+)\.\s")


def check_structure(path):
    """번호는 '## 1. 개요'부터 빈 번호 없이 이어짐. '### N-M.'은 바로 위 '## N.' 아래에서 1부터 이어짐.
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
            elif seen and k != last2 + 1:
                out.append((n, "구조", f"섹션 번호 {k}: 앞 번호 {last2} 다음은 {last2 + 1}. 빈 섹션을 지웠으면 번호를 이어 붙임"))
            seen, last2, last3 = True, k, 0
            continue
        m = H3.match(line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a != last2:
                out.append((n, "구조", f"'{a}-{b}'가 '## {last2}.' 아래에 있음"))
            elif b != last3 + 1:
                out.append((n, "구조", f"하위 번호 {a}-{b}: 앞 번호 다음은 {a}-{last3 + 1}"))
            last3 = b
    if not seen:
        out.append((1, "구조", "번호 섹션 없음. references/template.md의 섹션 순서를 씀"))
    return out

PROBLEM_MAX = 9
H2_ANY = re.compile(r"^##\s+\d+\.\s+(.*)$")
H3_ANY = re.compile(r"^###\s+\d+-\d+\.\s+(.*)$")


TERM_HEADER = ["용어", "설명", "화면 상 노출되는 문구"]
SUMMARY = re.compile(r"<summary>(.*?)</summary>")


def check_v57(path):
    """v5.7: 용어 정의와 참고는 맨 아래, 문제는 9줄 이내, 코드 블록은 '데이터 근거' 펼치기 안에만,
    펼치기 제목은 '데이터 근거: {주제}', 펼치기 표의 비율은 분자와 분모, 용어 정의 표는 3열"""
    out = []
    in_code = in_details = in_problem = False
    problem_line, problem_bullets = 0, 0
    h2s = []  # (줄, 제목)
    cur_h2 = ""
    lines = open(path, encoding="utf-8").read().split("\n")
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        s = line.strip()
        if "lint-skip" in line:
            continue
        m = SUMMARY.search(s)
        if m and not m.group(1).strip().startswith("데이터 근거:"):
            out.append((n, "근거 블록", f"펼치기 제목 '{m.group(1).strip()}' → '데이터 근거: {{주제}}'"))
        if s.startswith("<details"):
            in_details = True
            continue
        if s.startswith("</details"):
            in_details = False
            continue
        if s.startswith("```"):
            if not in_code and not in_details:
                out.append((n, "코드 블록", "코드 블록은 '데이터 근거' 펼치기 안에만 씀"))
            in_code = not in_code
            continue
        if in_code:
            continue
        if in_details and s.startswith("|") and not TABLE_SEP.match(s):
            row = cells(s)
            if len(row) >= 2 and row[0] != "항목" and "%" in row[1] and "/" not in row[1]:
                out.append((n, "비율 분모", f"'{row[1]}' → 분자와 분모를 같이: '12.8% (200건 / 1,558건)'"))
        if s.startswith("|") and not TABLE_SEP.match(s) and cur_h2 == "용어 정의":
            nxt = lines[n].strip() if n < len(lines) else ""
            row = cells(s)
            if TABLE_SEP.match(nxt) and row[:3] != TERM_HEADER:
                out.append((n, "용어 정의 표", f"열이 '{' | '.join(row)}' → '용어 | 설명 | 화면 상 노출되는 문구'"))
        m = H2_ANY.match(s)
        if m:
            cur_h2 = re.sub(r"<!--.*?-->", "", m.group(1)).strip()
            h2s.append((n, cur_h2))
            in_problem = False
            continue
        m = H3_ANY.match(s)
        if m:
            title = re.sub(r"<!--.*?-->", "", m.group(1)).strip()
            in_problem = title == "문제"
            if in_problem:
                problem_line = n
            if title == "참고":
                out.append((n, "섹션 순서", "참고는 개요 아래에 두지 않고 문서 맨 아래 섹션으로"))
            continue
        # 묶음 제목(현재 상황, 유저가 겪는 어려움, 데이터)은 세지 않고 하위 불릿만 셈
        if in_problem and not in_details and re.match(r"^\s+[-*]\s+\S", line):
            problem_bullets += 1
    if problem_bullets > PROBLEM_MAX:
        out.append((problem_line, "문제 길이", f"불릿 {problem_bullets}줄 → 현재 상황, 유저가 겪는 어려움, 데이터 세 묶음으로 {PROBLEM_MAX}줄 이내. 나머지 수치는 '데이터 근거' 펼치기에"))
    titles = [t for _, t in h2s]
    body_idx = [i for i, t in enumerate(titles) if "구현 상세" in t or "화면" in t]
    if h2s and "용어 정의" not in titles:
        out.append((1, "용어 정의 표", "'용어 정의' 섹션이 없음. 문서에서 부르는 이름과 화면 문구를 표로 둠 (참고 바로 앞)"))
    for i, (n, t) in enumerate(h2s):
        if t == "용어":
            out.append((n, "용어 정의 표", "섹션 이름은 '용어 정의'"))
        if t not in ("용어", "용어 정의", "참고"):
            continue
        if body_idx and i < max(body_idx):
            out.append((n, "섹션 순서", f"'{t}'는 구현 상세와 화면 뒤, 문서 맨 아래에 둠"))
        elif t == "참고" and i != len(h2s) - 1:
            out.append((n, "섹션 순서", "참고는 문서의 마지막 섹션"))
        elif t in ("용어", "용어 정의") and not (i == len(h2s) - 1 or (i == len(h2s) - 2 and titles[-1] == "참고")):
            out.append((n, "섹션 순서", "용어 정의는 참고 바로 앞, 참고가 없으면 마지막 섹션"))
    return out


def run_all(path):
    return check(path) + check_counts(path) + check_structure(path) + check_shape(path) + check_v57(path)


def main():
    if len(sys.argv) < 2:
        print("사용법: lint_spec.py <file.md> [...]")
        return 2
    total = 0
    for path in sys.argv[1:]:
        for n, kind, what in run_all(path):
            print(f"{path}:{n}: {kind}: {what}")
            total += 1
    if total:
        print(f"위반 {total}건")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
