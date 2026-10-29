"""차수가 나뉜 스펙의 상위 Confluence 페이지 본문을 만든다
- 하위 페이지(차수별 스펙) 목록은 Confluence '하위 페이지' 매크로가 자동으로 그린다. 차수 페이지가 늘어도 상위 본문을 고칠 필요 없음
- 사용: python3 parent_page.py --summary "한 줄 설명" [--out body.html]
"""
import argparse
import html
import sys

CHILDREN = (
    '<ac:structured-macro ac:name="children" ac:schema-version="2">'
    '<ac:parameter ac:name="all">false</ac:parameter>'
    '<ac:parameter ac:name="sort">creation</ac:parameter>'
    '<ac:parameter ac:name="excerptType">none</ac:parameter>'
    '</ac:structured-macro>'
)


def build(summary):
    parts = []
    if summary:
        parts.append(f"<p>{html.escape(summary)}</p>")
    parts.append("<h2>차수별 스펙</h2>")
    parts.append("<p>아래 문서를 누르면 해당 차수 스펙으로 이동합니다</p>")
    parts.append(CHILDREN)
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="차수별 스펙의 상위 페이지 본문 생성")
    ap.add_argument("--summary", default="", help="프로젝트 한 줄 설명 (1차 문서 1-5 솔루션 첫 줄)")
    ap.add_argument("--out", help="본문을 이 파일에도 저장")
    a = ap.parse_args()
    body = build(a.summary.strip())
    if a.out:
        open(a.out, "w", encoding="utf-8").write(body)
    sys.stdout.write(body + "\n")


if __name__ == "__main__":
    main()
