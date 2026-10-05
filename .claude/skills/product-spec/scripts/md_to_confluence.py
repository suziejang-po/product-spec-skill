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
TABLE_WIDTH = 1800
MIN_COL = 100
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


def cell_html(text):
    """셀 안 위계를 살린다. `1.`은 단락, `- `는 불릿, `  - `는 안쪽 불릿"""
    parts = [p for p in re.split(r"<br\s*/?>", text or "") if p.strip()]
    if not parts:
        return "<p></p>"
    out, stack = [], 0

    def close_to(target):
        nonlocal stack
        while stack > target:
            out.append("</ul>")
            stack -= 1
            if stack > 0:
                out.append("</li>")

    for raw in parts:
        m = re.match(r"^(\s*)-\s+(.*)$", raw)
        depth = (2 if len(m.group(1)) >= 2 else 1) if m else 0
        body = m.group(2) if m else raw.strip()
        if depth > stack:
            while depth > stack:
                if stack > 0 and out and out[-1] == "</li>":
                    out.pop()          # 부모 항목 안에 중첩한다
                out.append("<ul>")
                stack += 1
        elif depth < stack:
            close_to(depth)
        if depth == 0:
            out.append(f"<p>{inline(body)}</p>")
        else:
            out.append(f"<li><p>{inline(body)}</p>")
            out.append("</li>")
    close_to(0)
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
            # storage 형식으로 올릴 때는 figure media-single이 저장되지 않고 그림이 사라짐.
            # media.json에 filename(첨부 파일명)이 있으면 storage용 ac:image로 내보냄
            if m and m.get("filename"):
                return (f'<p><ac:image ac:align="center" ac:layout="center" ac:custom-width="true" '
                        f'ac:width="760" ac:alt="{html.escape(alt or name)}">'
                        f'<ri:attachment ri:filename="{html.escape(m["filename"])}" /></ac:image></p>')
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
        names = [h.strip() for h in header]
        numbered = names[0] == "#"

        def plain(x):
            x = re.sub(r"<br\s*/?>", " ", x or "")
            return re.sub(r"[*`\[\]()]", "", x).strip()

        def weight(x):
            # 한글은 영문보다 넓게 차지하므로 1.8배로 센다
            t = plain(x)
            wide = sum(1 for ch in t if ord(ch) > 0x1100)
            return wide * 1.8 + (len(t) - wide)

        # 구현 상세 표는 요구사항 셀이 압도적으로 길어 비례 배분이 무너지므로 고정값을 쓴다
        if numbered and names == ["#", "진입점", "화면", "기능", "요구사항"]:
            fixed = [NUM_COL, 210, 200, 170]
            widths = fixed + [TABLE_WIDTH - sum(fixed)]
        else:
            reps, caps = [], []
            for i in range(ncol):
                cells = [(r + [""] * ncol)[i] for r in body]
                filled = [weight(c) for c in cells if plain(c)]
                avg = sum(filled) / len(filled) if filled else 0
                reps.append(max(avg, weight(header[i]) * 1.2, 1))
                # 그 열에서 가장 긴 글자보다 넓어지지 않게 상한을 둔다
                longest = max([weight(c) for c in cells] + [weight(header[i])])
                caps.append(max(MIN_COL, round(longest * 9 + 40)))
            # 표가 실제로 필요한 폭. 이보다 넓히면 오른쪽이 비어 보인다
            need = sum(caps) + (NUM_COL if numbered else 0)
            target = min(TABLE_WIDTH, max(need, 320))
            pool = target - (NUM_COL if numbered else 0)
            idx = [i for i in range(ncol) if not (numbered and i == 0)]
            widths = [NUM_COL if (numbered and i == 0) else 0 for i in range(ncol)]
            # 상한과 하한에 걸린 열을 고정하고, 남은 폭을 나머지 열에 길이 비례로 다시 나눈다
            free, remain = list(idx), pool
            for _ in range(6):
                total = sum(reps[i] for i in free) or 1
                done = []
                for i in free:
                    w = round(remain * reps[i] / total)
                    if w > caps[i]:
                        widths[i] = caps[i]; done.append(i)
                    elif w < MIN_COL:
                        widths[i] = MIN_COL; done.append(i)
                if not done:
                    for i in free:
                        widths[i] = round(remain * reps[i] / total)
                    break
                remain -= sum(widths[i] for i in done)
                free = [i for i in free if i not in done]
                if not free:
                    break
            # Confluence는 열 폭을 비율로 쓴다. 합을 억지로 맞추지 않고 상한을 지킨다

        # 본문이 왼쪽 정렬이므로 표도 왼쪽에서 시작해야 한다.
        # default와 wide는 가운데 배치라 좁은 표가 중앙에 떠 보인다
        layout = "full-width" if sum(widths) > 1100 else "align-start"
        attrs = f' data-layout="{layout}" data-display-mode="fixed"'
        # storage 형식은 data-colwidth를 무시한다. 실제 폭은 colgroup으로 넣어야 적용된다
        cols = "".join(f'<col style="width: {w}.0px;" />' for w in widths)
        out = [f"<table{attrs}><colgroup>{cols}</colgroup><thead><tr>"]
        for i, c in enumerate(header):
            out.append(f'<th data-colwidth="{widths[i]}"><p>{inline(c.strip())}</p></th>')
        out.append("</tr></thead><tbody>")
        for r in body:
            r = (r + [""] * ncol)[:ncol]
            out.append("<tr>")
            for i, c in enumerate(r):
                out.append(f'<td data-colwidth="{widths[i]}">{cell_html(c.strip())}</td>')
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
