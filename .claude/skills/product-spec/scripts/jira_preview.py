#!/usr/bin/env python3
"""스펙 마크다운에서 Jira 에픽을 만들 값을 뽑는다 (지라 사용 가이드 v2 기준)

작성자에게 묻는 것은 레이블과, 하위 섹션이 2개 이상일 때 에픽을 나눌지뿐이다.
나머지 빈 값은 비워 두고 만든 뒤 안내에 적는다 (notes는 안내에 쓸 문장)

- 에픽 하나는 배포 단위 하나. 구현 상세가 하위 섹션으로 나뉘면 하위 섹션마다 에픽 (--single이면 하나로)
- 날짜: 에픽이 하나면 메타 '개발 일정', 여럿이면 하위 섹션의 '개발 일정:' 줄. 없으면 비움
- 요약: 차수 문서(제목 끝 '(N차)')를 하위 섹션으로 나누면 '(N-1차)', '(N-2차)'
- A/B 테스트 포함이면 실험 추적 Task 값도 함께 냄
- --check-label 로 레이블 형식만 검사 (쉼표로 여러 개 가능)

사용:
  python3 jira_preview.py spec.md --url https://.../pages/123 --label pod-ax인재
  python3 jira_preview.py spec.md --single --label pod-ax인재
  python3 jira_preview.py --check-label "POD AX인재,chapter-front"
"""
import argparse
import json
import re
import sys

PREFIXES = ("pod-", "chapter-", "exp-", "tf-", "prj-")
DATE = r"(\d{4}-\d{2}-\d{2})"
RANGE = re.compile(DATE + r"\s*~\s*" + DATE)
ONE = re.compile(DATE)


def check_label(raw):
    """레이블 형식 검사. ok면 그대로, 아니면 고친 값을 suggestion으로"""
    label = (raw or "").strip()
    if not label:
        return {"ok": False, "label": label, "suggestion": "", "reason": "레이블은 필수"}
    if label.lower() in PREFIXES:
        return {"ok": False, "label": label, "suggestion": "", "reason": "앞붙이 뒤에 이름이 없음"}
    fixed = re.sub(r"\s+", "-", label)
    fixed = re.sub(r"[A-Z]+", lambda m: m.group().lower(), fixed)
    fixed = re.sub(r"-{2,}", "-", fixed).strip("-")
    reasons = []
    if fixed != label:
        reasons.append("영어는 소문자, 띄어쓰기는 '-'")
    if not fixed.startswith(PREFIXES):
        reasons.append("앞붙이(pod-, chapter-, exp-, tf-, prj-)가 없음. 레이블 질문에서 어느 그룹인지 다시 받을 것")
        return {"ok": False, "label": label, "suggestion": fixed if fixed != label else "",
                "reason": ", ".join(reasons), "need_prefix": True}
    if fixed in PREFIXES:
        return {"ok": False, "label": label, "suggestion": "", "reason": "앞붙이 뒤에 이름이 없음"}
    return {"ok": not reasons, "label": label, "suggestion": "" if not reasons else fixed,
            "reason": ", ".join(reasons)}


def check_labels(raw):
    """쉼표로 나눈 레이블을 하나씩 검사. 결과: ok, labels(고친 값), items(하나씩 결과)"""
    parts = [x.strip() for x in (raw or "").split(",") if x.strip()]
    items = [check_label(x) for x in parts] or [check_label("")]
    fixed = []
    for r in items:
        if r["ok"]:
            fixed.append(r["label"])
        elif r.get("suggestion") and not r.get("need_prefix"):
            fixed.append(r["suggestion"])
    ok = all(r["ok"] for r in items)
    usable = len(fixed) == len(items) and bool(fixed)
    return {"ok": ok, "usable": usable, "labels": fixed if usable else [], "items": items}


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def strip_md(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"\*\*|`", "", s)
    return re.sub(r"\s+", " ", s).strip()


def anchor(title):
    """Confluence 제목 앵커: 공백을 -로"""
    return re.sub(r"\s+", "-", title.strip())


def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out = {"title": "", "summary_base": "", "meta": {}, "units": [], "solution": [], "kr_anchor": "",
           "ab_test": False, "notes": []}
    in_code = False
    h2 = h3 = ""
    unit = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or s.startswith("<!--"):
            continue
        if s.startswith("# ") and not out["title"]:
            out["title"] = s[2:].strip()
            continue
        m = re.match(r"^##\s+\d+\.\s+(.*)$", s)
        if m:
            h2 = m.group(1).strip()
            h3 = ""
            unit = None
            if h2 == "구현 상세":
                unit = {"section": "", "anchor": "", "features": [], "schedule": ""}
                out["units"].append(unit)
            continue
        m = re.match(r"^###\s+(\d+-\d+\.\s+.*)$", s)
        if m:
            h3 = m.group(1).strip()
            if h3.endswith("KR"):
                out["kr_anchor"] = anchor(h3)
            if "실험 설계" in h3:
                out["ab_test"] = True
            if h2 == "구현 상세":
                name = re.sub(r"^\d+-\d+\.\s+", "", h3)
                if out["units"] and not out["units"][-1]["section"] and not out["units"][-1]["features"]:
                    out["units"].pop()
                unit = {"section": name, "anchor": anchor(h3), "features": [], "schedule": ""}
                out["units"].append(unit)
            continue
        if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s):
            row = cells(s)
            if h3.endswith("메타") and len(row) >= 2:
                key = strip_md(row[0])
                val = strip_md(row[1])
                # {티켓 링크} 같은 양식 자리 표시는 빈칸으로 봄
                out["meta"][key] = "" if re.fullmatch(r"\{[^}]*\}", val) else val
            elif unit is not None and len(row) >= 5 and row[0] not in ("#",) and re.match(r"^\d+$", row[0]):
                feat = strip_md(row[3])
                if feat and feat not in unit["features"]:
                    unit["features"].append(feat)
            if row and strip_md(row[0]) == "실험 Flag":
                out["ab_test"] = True
            continue
        m = re.match(r"^[-*]?\s*개발 일정\s*:\s*(.+)$", s)
        if m and unit is not None and h2 == "구현 상세":
            unit["schedule"] = m.group(1).strip()
            continue
        if h3.endswith("솔루션") and re.match(r"^[-*]\s+\S", line):
            out["solution"].append(strip_md(re.sub(r"^[-*]\s+", "", line)))
        if "실험 설계" in s and s.startswith("|") is False and h3.endswith("KR"):
            out["ab_test"] = True
    t = out["title"]
    t = re.sub(r"^\(작성중\)\s*", "", t)
    t = re.sub(r"^\[\d{4}\]\s*Product Spec:\s*", "", t)
    out["summary_base"] = t.strip()
    out["units"] = [u for u in out["units"] if u["section"] or u["features"]]
    return out


def read_range(raw):
    m = RANGE.search(raw or "")
    if m:
        return m.group(1), m.group(2)
    m = ONE.search(raw or "")
    if m:
        return m.group(1), ""
    return "", ""


def build(path, url, label="", single=False):
    p = parse(path)
    notes = p["notes"]
    lab = check_labels(label)
    labels = lab["labels"]
    if not labels:
        notes.append("레이블이 없거나 앞붙이가 없음. 레이블을 받은 뒤 만들 것 (레이블은 필수)")
    elif not lab["ok"]:
        notes.append("레이블 형식을 고쳐서 넣음: " + ", ".join(labels))
    jira_cell = p["meta"].get("Jira", "")
    if jira_cell:
        notes.append(f"메타 Jira 칸에 이미 값이 있음: '{jira_cell}'. 에픽을 만들지 않음")
    units = p["units"] or [{"section": "", "anchor": "", "features": [], "schedule": ""}]
    if single:
        units = [{"section": "", "anchor": "", "features": [], "schedule": ""}]
    multi = len(units) > 1
    base = p["summary_base"]
    m = re.search(r"\s*\((\d+)차\)\s*$", base)
    chasu = m.group(1) if m else ""
    base_no_chasu = base[:m.start()] if m else base
    link0 = url or "{Confluence URL}"
    epics = []
    empty_dates = []
    for n, u in enumerate(units, 1):
        if multi:
            tag = f"({chasu}-{n}차)" if chasu else f"({n}차)"
            summary = f"{base_no_chasu} {tag} {u['section']}".strip()
            start, due = read_range(u["schedule"])
        else:
            summary = base
            start, due = read_range(p["meta"].get("개발 일정", ""))
        if not (start and due):
            empty_dates.append(summary)
        link = link0 + ("#" + u["anchor"] if multi and u["anchor"] else "")
        # 에픽이 하나면 솔루션 묶음, 여럿이면 그 배포 단위 표의 기능 열
        bullets = (u["features"] or p["solution"]) if multi else (p["solution"] or u["features"])
        desc = "\n".join([f"스펙: {link}"] + [f"- {b}" for b in bullets])
        epics.append({"summary": summary, "description": desc, "labels": labels,
                      "start_date": start, "due_date": due, "fix_version": ""})
    if empty_dates:
        how = "하위 섹션 제목 아래 '개발 일정: YYYY-MM-DD~YYYY-MM-DD' 줄이 없음" if multi else "메타 '개발 일정'을 YYYY-MM-DD~YYYY-MM-DD로 읽지 못함"
        notes.append(f"{how}. 날짜를 비워 두고 만들고, 안내에 '에픽별 시작 날짜와 기한을 채워 주세요'를 적을 것")
    task = None
    if p["ab_test"]:
        flag = p["meta"].get("실험 Flag", "").strip()
        exp_label = ""
        if flag:
            raw = flag if flag.lower().startswith("exp-") else "exp-" + flag
            r = check_label(raw)
            exp_label = r["label"] if r["ok"] else r.get("suggestion", "")
        task = {"summary": f"[실험] {base}",
                "description": f"스펙: {link0}" + (f"#{p['kr_anchor']}" if p["kr_anchor"] else ""),
                "labels": [l for l in [exp_label] + labels if l],
                "due_date": "", "link": "relates to"}
        if not exp_label:
            notes.append("실험 Flag가 비어 있어 exp- 레이블 없이 만듦. 안내에 'exp- 레이블을 붙여 주세요'를 적을 것")
        notes.append("실험 Task 기한(실험 종료일)은 실험 설계 표의 기간 끝날을 쓰고, 없으면 비워 두고 안내에 적을 것")
    return {"epic_count": len(epics), "epics": epics, "label_check": lab, "split_question": multi,
            "ab_test_task": task, "can_create": not jira_cell and bool(labels), "notes": notes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--url", default="")
    ap.add_argument("--label", default="")
    ap.add_argument("--check-label", dest="check")
    ap.add_argument("--single", action="store_true", help="하위 섹션이 여럿이어도 에픽 하나로")
    a = ap.parse_args()
    if a.check is not None:
        r = check_labels(a.check)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(0 if r["ok"] else 1)
    if not a.spec:
        ap.error("spec 경로가 필요함")
    print(json.dumps(build(a.spec, a.url, a.label, a.single), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
