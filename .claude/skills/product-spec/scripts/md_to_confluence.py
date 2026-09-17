#!/usr/bin/env python3
"""스펙 마크다운을 Confluence HTML 본문으로 변환.
사용법: md_to_confluence.py <spec.md> [--diagram-mode attach|macro] [--media-json map.json]
- attach: media-json의 {파일명: {"mediaId", "collection"}}로 이미지를 media figure로 넣음
- macro: 이미지 경로의 .mmd와 -macro.png를 찾아 Mermaid 블록으로 넣음
- 표의 첫 열이 #이면 열 폭을 고정하고 첫 열을 40으로 좁힘
- 변환 직전 금지 기호를 치환"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mermaid_macro import build as build_macro  # noqa: E402

REPLACE = {"·": "/", "—": ", ", "–": ", "}
CIRCLED = {chr(0x2460 + i): f"{i + 1}." for i in range(20)}
TABLE_WIDTH = 760
NUM_COL = 40


def clean(text):
    for k, v in REPLACE.items():
        text = text.replace(k, v)
    for k, v in CIRCLED.items():
        text = text.replace(k, v)
    return text


def inline(text):
    text = clean(text)
    parts = re.split(r"(<br\s*/?>)", text)
    out = []
    for p in parts:
        if re.fullmatch(r"<br\s*/?>", p):
            out.append("<br>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"`([^`]+)`", r"<code>\1</code>", p)
        p = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
        out.append(p)
    return "".join(out)


class Converter:
    def __init__(self, base_dir, mode, media):
        self.base_dir = base_dir
        self.mode = mode
        self.media = media
        self.notes = []

    def image(self, alt, path):
        name = os.path.basename(path)
        if self.mode == "attach":
            m = self.media.get(name) or self.media.get(path)
            if m and m.get("mediaId"):
                return (f'<figure data-type="media-single" data-layout="center" data-width="80" '
                        f'data-width-type="percentage"><div data-type="media" data-media-type="file" '
                        f'data-id="{html.escape(m["mediaId"])}" data-collection="{html.escape(m["collection"])}" '
                        f'data-alt="{html.escape(name)}"></div></figure>')
            self.notes.append(f"첨부 정보 없음: {name}. 블록으로 대체")
        stem = os.path.splitext(os.path.join(self.base_dir, path))[0]
        mmd, png = stem + ".mmd", stem + "-macro.png"
        if os.path.exists(mmd) and os.path.exists(png):
            return build_macro(open(mmd, encoding="utf-8").read().strip(), open(png, "rb").read())
        self.notes.append(f"그림 파일 없음: {mmd} 또는 {png}")
        return f'<div data-type="panel-warning"><p>⚠️ 다이어그램 파일 없음: {html.escape(path)}</p></div>'

    def table(self, rows):
        header, body = rows[0], rows[2:]
        ncol = len(header)
        numbered = header[0].strip() == "#"
        widths = None
        if numbered:
            rest = (TABLE_WIDTH - NUM_COL) // max(ncol - 1, 1)
            widths = [NUM_COL] + [rest] * (ncol - 1)
        attrs = ' data-display-mode="fixed"' if numbered else ""
        out = [f"<table{attrs}><thead><tr>"]
        for i, c in enumerate(header):
            w = f' data-colwidth="{widths[i]}"' if widths else ""
            out.append(f"<th{w}><p>{inline(c.strip())}</p></th>")
        out.append("</tr></thead><tbody>")
        for r in body:
            r = (r + [""] * ncol)[:ncol]
            out.append("<tr>")
            for i, c in enumerate(r):
                w = f' data-colwidth="{widths[i]}"' if widths else ""
                out.append(f"<td{w}><p>{inline(c.strip())}</p></td>")
            out.append("</tr>")
        out.append("</tbody></table>")
        return "".join(out)

    def convert(self, text):
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        lines = text.split("\n")
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s:
                i += 1
                continue
            m = re.match(r"^(#{1,6})\s+(.*)", s)
            if m:
                out.append(f"<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>")
                i += 1
                continue
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", s)
            if m:
                out.append(self.image(m.group(1), m.group(2)))
                i += 1
                continue
            if s.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                    i += 1
                if len(rows) >= 2:
                    out.append(self.table(rows))
                continue
            if re.match(r"^[-*]\s", s) or re.match(r"^\d+\.\s", s):
                ordered = bool(re.match(r"^\d+\.\s", s))
                tag = "ol" if ordered else "ul"
                items = []
                while i < len(lines) and (re.match(r"^\s*[-*]\s", lines[i]) or re.match(r"^\s*\d+\.\s", lines[i])):
                    items.append(re.sub(r"^\s*([-*]|\d+\.)\s", "", lines[i]))
                    i += 1
                out.append(f"<{tag}>" + "".join(f"<li><p>{inline(x)}</p></li>" for x in items) + f"</{tag}>")
                continue
            para = [s]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||[-*]\s|\d+\.\s|!\[)", lines[i].strip()):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
        return "".join(out)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    mode = "attach"
    media = {}
    if "--diagram-mode" in args:
        mode = args[args.index("--diagram-mode") + 1]
    if "--media-json" in args:
        media = json.load(open(args[args.index("--media-json") + 1], encoding="utf-8"))
    conv = Converter(os.path.dirname(os.path.abspath(path)), mode, media)
    body = conv.convert(open(path, encoding="utf-8").read())
    sys.stdout.write(body)
    for n in conv.notes:
        print(n, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
