"""차수가 나뉜 스펙의 상위 Confluence 페이지 본문을 만든다
- 하위 페이지(차수별 스펙) 목록은 Confluence '하위 페이지' 매크로가 자동으로 그린다. 차수 페이지가 늘어도 상위 본문을 고칠 필요 없음
- 사용: python3 parent_page.py --summary "한 줄 설명" [--out body.html]
"""
import argparse
import html
import sys

# Atlassian MCP(html 형식)는 storage XML(<ac:structured-macro>)을 글자 그대로 보여주므로 확장 노드 꼴로 씀
CHILDREN = (
    '<div data-type="extension" data-extension-key="children" '
    'data-extension-type="com.atlassian.confluence.macro.core" '
    'data-parameters=\'{"macroParams":{"all":{"value":"false"},"depth":{"value":"1"}},'
    '"macroMetadata":{"schemaVersion":{"value":"2"},"title":"Children Display"}}\'></div>'
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
