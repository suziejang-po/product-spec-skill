#!/usr/bin/env python3
"""스펙 마크다운에서 Jira 에픽 미리보기를 만든다 (v2 가이드 기준)

- 에픽 하나는 배포 단위 하나. 구현 상세가 하위 섹션으로 나뉘면 하위 섹션마다 에픽
- Start Date, 기한은 메타 '개발 일정'에서
- A/B 테스트 포함이면 실험 추적 Task 후보를 함께 냄
- --check-label 로 레이블 형식만 검사할 수 있음

사용:
  python3 jira_preview.py spec.md --url https://.../pages/123
  python3 jira_preview.py --check-label "POD AX인재"
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
        reasons.append("앞붙이(pod-, chapter-, exp-, tf-, prj-)가 없음. 어느 그룹인지 작성자에게 물을 것")
        return {"ok": False, "label": label, "suggestion": fixed if fixed != label else "",
                "reason": ", ".join(reasons), "need_prefix": True}
    if fixed in PREFIXES:
        return {"ok": False, "label": label, "suggestion": "", "reason": "앞붙이 뒤에 이름이 없음"}
    return {"ok": not reasons, "label": label, "suggestion": "" if not reasons else fixed,
            "reason": ", ".join(reasons)}


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
                unit = {"section": "", "anchor": "", "features": []}
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
                unit = {"section": name, "anchor": anchor(h3), "features": []}
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


def dates(meta, notes):
    raw = meta.get("개발 일정", "")
    m = RANGE.search(raw)
    if m:
        return m.group(1), m.group(2)
    m = ONE.search(raw)
    if m:
        notes.append("개발 일정에 날짜가 하나뿐. 기한은 작성자에게 물을 것")
        return m.group(1), ""
    if raw:
        notes.append(f"개발 일정 '{raw}'을 YYYY-MM-DD~YYYY-MM-DD로 읽지 못함. 작성자에게 물을 것")
    else:
        notes.append("개발 일정이 비어 있음. Start Date, 기한을 작성자에게 물을 것")
    return "", ""


def build(path, url, label=""):
    p = parse(path)
    lab = check_label(label) if label else {"ok": False, "reason": "레이블은 필수. 미리보기에서 받을 것"}
    # 형식만 틀렸으면 고친 값으로 미리보기를 만들고 확인받음. 앞붙이가 없으면 그대로 두고 물음
    if label and not lab["ok"] and lab.get("suggestion") and not lab.get("need_prefix"):
        label = lab["suggestion"]
    notes = p["notes"]
    start, due = dates(p["meta"], notes)
    jira_cell = p["meta"].get("Jira", "")
    if jira_cell:
        notes.append(f"메타 Jira 칸에 이미 값이 있음: '{jira_cell}'. 에픽을 만들지 않음")
    units = p["units"] or [{"section": "", "anchor": "", "features": []}]
    multi = len(units) > 1
    epics = []
    for n, u in enumerate(units, 1):
        summary = p["summary_base"]
        if multi:
            summary += f" ({n}차) {u['section']}"
        link = url or "{Confluence URL}"
        if multi and u["anchor"]:
            link += "#" + u["anchor"]
        bullets = u["features"] or p["solution"]
        desc = "\n".join([f"스펙: {link}"] + [f"- {b}" for b in bullets])
        epics.append({"summary": summary, "description": desc, "labels": [label] if label else [],
                      "start_date": start, "due_date": due, "fix_version": ""})
    task = None
    if p["ab_test"]:
        flag = p["meta"].get("실험 Flag", "")
        exp_label = check_label("exp-" + flag)["suggestion"] or ("exp-" + flag) if flag else ""
        task = {"summary": f"[실험] {p['summary_base']}",
                "description": f"스펙: {url or '{Confluence URL}'}" + (f"#{p['kr_anchor']}" if p["kr_anchor"] else ""),
                "labels": [l for l in (exp_label, label) if l],
                "due_date": "", "link": "relates to"}
        if not flag:
            notes.append("A/B 테스트 포함인데 실험 Flag가 비어 있음. 실험 레이블(exp-)을 작성자에게 물을 것")
        notes.append("실험 Task 기한(실험 종료일)은 실험 설계 표에서 읽거나 작성자에게 물을 것")
    if multi:
        notes.append(f"배포 단위 {len(units)}개. '하나로 합칠까요?'도 같이 물을 것")
    return {"epic_count": len(epics), "epics": epics, "label_check": lab,
            "ab_test_task": task, "can_create": not jira_cell, "notes": notes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--url", default="")
    ap.add_argument("--label", default="")
    ap.add_argument("--check-label", dest="check")
    a = ap.parse_args()
    if a.check is not None:
        r = check_label(a.check)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(0 if r["ok"] else 1)
    if not a.spec:
        ap.error("spec 경로가 필요함")
    print(json.dumps(build(a.spec, a.url, a.label), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
