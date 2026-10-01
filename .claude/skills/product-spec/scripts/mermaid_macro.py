#!/usr/bin/env python3
"""Mermaid Chart 앱 매크로 HTML 생성. 사용법: mermaid_macro.py <in.mmd> <in.png>
표준 출력에 Confluence HTML(extension div) 한 줄. 코드와 PNG를 함께 넣어야 보기 화면에 그림이 표시된다."""
import base64
import datetime
import html
import json
import struct
import sys
import zlib


def quantize_png(data, levels=16):
    """PNG를 채널당 levels 단계로 줄여 다시 압축. 블록 base64를 줄이기 위함. 실패하면 원본 반환"""
    try:
        p = 8
        idat = b""
        ihdr = None
        while p < len(data):
            ln = struct.unpack(">I", data[p:p + 4])[0]
            t = data[p + 4:p + 8]
            d = data[p + 8:p + 8 + ln]
            p += 12 + ln
            if t == b"IHDR":
                ihdr = struct.unpack(">IIBBBBB", d)
            elif t == b"IDAT":
                idat += d
        w, h, depth, ctype = ihdr[0], ihdr[1], ihdr[2], ihdr[3]
        if depth != 8 or ctype not in (2, 6):
            return data
        bpp = 4 if ctype == 6 else 3
        raw = zlib.decompress(idat)
        stride = w * bpp
        prev = bytearray(stride)
        i = 0
        step = 255 // (levels - 1)
        rows = bytearray()
        for _ in range(h):
            f = raw[i]
            i += 1
            line = bytearray(raw[i:i + stride])
            i += stride
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                if f == 1:
                    line[x] = (line[x] + a) & 255
                elif f == 2:
                    line[x] = (line[x] + b) & 255
                elif f == 3:
                    line[x] = (line[x] + ((a + b) >> 1)) & 255
                elif f == 4:
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                    line[x] = (line[x] + pr) & 255
            prev = line
            rows.append(0)
            for x in range(0, stride, bpp):
                r, g, bl = line[x], line[x + 1], line[x + 2]
                if bpp == 4:
                    al = line[x + 3]
                    r = (r * al + 255 * (255 - al)) // 255
                    g = (g * al + 255 * (255 - al)) // 255
                    bl = (bl * al + 255 * (255 - al)) // 255
                rows += bytes(((r // step) * step, (g // step) * step, (bl // step) * step))

        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b""))
    except Exception:
        return data


def build(code, png_bytes):
    png_bytes = quantize_png(png_bytes)
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
