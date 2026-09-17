#!/usr/bin/env python3
"""Mermaid Chart 앱 매크로 HTML 생성. 사용법: mermaid_macro.py <in.mmd> <in.png>
표준 출력에 Confluence HTML(extension div) 한 줄. 코드와 PNG를 함께 넣어야 보기 화면에 그림이 표시된다."""
import base64
import datetime
import html
import json
import sys


def build(code, png_bytes):
    params = {
        "size": "medium",
        "isEditable": "true",
        "diagramCode": code,
        "caption": "",
        "theme": "default",
        "lastEdited": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "diagramType": "mermaid",
        "__bodyContent": base64.b64encode(png_bytes).decode(),
    }
    payload = {
        "macroParams": {k: {"value": v} for k, v in params.items()},
        "macroMetadata": {
            "schemaVersion": {"value": "1"},
            "placeholder": [{"type": "icon", "data": {"url": "https://confluence.mermaidchart.com/icon_80x80.png"}}],
            "title": "Mermaid chart",
        },
    }
    attr = html.escape(json.dumps(payload, ensure_ascii=False), quote=True)
    return ('<div data-type="extension" data-extension-key="mermaid" '
            'data-extension-type="com.atlassian.confluence.macro.core" data-layout="default" '
            f'data-parameters="{attr}"></div>')


def main():
    if len(sys.argv) != 3:
        print("사용법: mermaid_macro.py <in.mmd> <in.png>", file=sys.stderr)
        return 2
    code = open(sys.argv[1], encoding="utf-8").read().strip()
    png = open(sys.argv[2], "rb").read()
    sys.stdout.write(build(code, png))
    return 0


if __name__ == "__main__":
    sys.exit(main())
