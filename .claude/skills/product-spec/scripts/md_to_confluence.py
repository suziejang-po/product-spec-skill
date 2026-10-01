#!/usr/bin/env python3
"""스펙 마크다운을 Confluence HTML 본문으로 변환.
사용법: md_to_confluence.py <spec.md> [--diagram-mode attach|macro] [--media-json map.json]
- attach: media-json의 {파일명: {"mediaId", "collection"}}로 이미지를 media figure로 넣음
- macro: 이미지 경로의 .mmd와 -macro.png를 찾아 Mermaid 블록으로 넣음
- 표의 첫 열이 #이면 열 폭을 고정하고 첫 열을 40으로 좁힘
- 변환 직전 금지 기호를 치환"""
import argparse
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mermaid_macro import build as build_macro, quantize_png  # noqa: E402

INLINE_CODE = re.compile(r"`[^`]*`")
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
        p = re.sub(r"\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)", r'<a href="\2">\1</a>', p)
        out.append(p)
    return "".join(out)


def split_cells(row):
    """| a | `x|y` | c \\| d | → 인라인 코드 안의 |와 이스케이프된 \\|는 구분자로 보지 않음"""
    protected = []

    def keep(m):
        protected.append(m.group(0))
        return f"\x00{len(protected) - 1}\x00"

    tmp = INLINE_CODE.sub(keep, row).replace("\\|", "\x01")
    cells = tmp.strip().strip("|").split("|")
    out = []
    for c in cells:
        c = c.replace("\x01", "|")
        c = re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], c)
        out.append(c)
    return out


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
            self.notes.append(f"첨부 정보 없음: {name} (media.json에 미디어 ID 없음). 블록 또는 안내 상자로 대체. 첨부는 올라가 있으면 편집 화면에서 끌어다 놓아도 됨")
        stem = os.path.splitext(os.path.join(self.base_dir, path))[0]
        mmd, png = stem + ".mmd", stem + "-macro.png"
        if os.path.exists(mmd) and not os.path.exists(png):
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_diagram.sh")
            try:
                subprocess.run(["bash", script, mmd, png, "macro"], capture_output=True, timeout=120)
            except subprocess.TimeoutExpired:
                self.notes.append(f"렌더 시간 초과: {mmd}")
        if os.path.exists(mmd) and os.path.exists(png):
            data = quantize_png(open(png, "rb").read())
            m_w = int.from_bytes(data[16:20], "big") if len(data) > 24 else 0
            m_h = int.from_bytes(data[20:24], "big") if len(data) > 24 else 0
            b64_len = len(data) * 4 // 3
            kind = open(mmd, encoding="utf-8").readline().strip().split()[0] if os.path.exists(mmd) else "flowchart"
            label = {"flowchart": "흐름도", "graph": "흐름도", "stateDiagram-v2": "상태도", "stateDiagram": "상태도", "sequenceDiagram": "순서도"}.get(kind, "다이어그램")
            # 블록은 폭 300px로 표시된다. 블록용 그림이 납작하거나(높이 120 미만, 가로세로비 2.5 초과) 크면(8KB 초과) 읽히지 않는다
            if b64_len > 8 * 1024 or (m_h and m_h < 120) or (m_w and m_h and m_w / m_h > 2.5):
                self.notes.append(f"블록 대신 안내 상자: {name} (base64 {b64_len // 1024}KB, 블록 {m_w}x{m_h}). 편집 → /mermaid → {os.path.relpath(mmd, self.base_dir)} 붙여넣기")
                return (f'<div data-type="panel-info"><p>{label} 자리. 편집 화면에서 /mermaid 를 넣고 '
                        f'{html.escape(os.path.relpath(mmd, self.base_dir))} 의 코드를 붙여넣어 주세요. 그림 파일 {html.escape(path)}</p></div>')
            return build_macro(open(mmd, encoding="utf-8").read().strip(), data)
        self.notes.append(f"그림 파일 없음: {mmd} 또는 {png}")
        return f'<div data-type="panel-warning"><p>다이어그램 파일 없음: {html.escape(path)}. 스펙 폴더의 diagrams에서 그림을 만들어 끌어다 놓아 주세요</p></div>'

    def table(self, rows):
        header, body = rows[0], rows[2:]
        ncol = len(header)
        numbered = header[0].strip() == "#"
        widths = None
        if numbered:
            names = [h.strip() for h in header]
            if names == ["#", "진입점", "화면", "기능", "요구사항"]:
                widths = [NUM_COL, 140, 140, 120, TABLE_WIDTH - NUM_COL - 400]
            else:
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
            if s.startswith("```"):
                lang = s[3:].strip()
                i += 1
                code = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code.append(lines[i])
                    i += 1
                i += 1
                cls = f' class="language-{html.escape(lang)}"' if lang else ""
                out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
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
                    rows.append(split_cells(lines[i].strip()))
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
    ap = argparse.ArgumentParser(description="스펙 마크다운을 Confluence HTML로 변환")
    ap.add_argument("spec")
    ap.add_argument("--diagram-mode", choices=["attach", "macro"], default="attach")
    ap.add_argument("--media-json", help='{"파일명": {"mediaId": "...", "collection": "..."}}')
    ap.add_argument("--out", help="본문을 이 파일에도 저장")
    a = ap.parse_args()
    media = json.load(open(a.media_json, encoding="utf-8")) if a.media_json else {}
    conv = Converter(os.path.dirname(os.path.abspath(a.spec)), a.diagram_mode, media)
    body = conv.convert(open(a.spec, encoding="utf-8").read())
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(body)
    sys.stdout.write(body)
    print(f"\n본문 크기: {len(body.encode('utf-8')) // 1024}KB", file=sys.stderr)
    for n in conv.notes:
        print(n, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
