"""Tiny SVG flowchart helper with manual layout."""
from html import escape

FONT = "'Noto Sans CJK KR', 'Noto Sans KR', sans-serif"
STY = {
    'user': ('#DEEBFF', '#4C9AFF', '#172B4D'),
    'sys':  ('#F4F5F7', '#8993A4', '#172B4D'),
    'ops':  ('#FFF7D6', '#E2B203', '#172B4D'),
    'ok':   ('#E3FCEF', '#36B37E', '#172B4D'),
    'bad':  ('#FFEBE6', '#FF8F73', '#172B4D'),
    'plain':('#FFFFFF', '#8993A4', '#172B4D'),
}


class Chart:
    def __init__(self, w, h, title=None):
        self.w, self.h = w, h
        self.back, self.front = [], []
        self.nodes = {}
        if title:
            self.front.append(f'<text x="32" y="44" font-size="22" font-weight="700" fill="#172B4D">{escape(title)}</text>')

    # ---------- layout helpers ----------
    def lane(self, y, h, label, fill, x=24, w=None, labelw=96):
        w = w or self.w - 48
        self.back.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#DFE1E6"/>')
        self.back.append(f'<rect x="{x}" y="{y}" width="{labelw}" height="{h}" rx="10" fill="#FFFFFF" stroke="#DFE1E6"/>')
        self.back.append(f'<text x="{x+labelw/2}" y="{y+h/2+6}" text-anchor="middle" font-size="16" font-weight="700" fill="#42526E">{escape(label)}</text>')

    def column_header(self, x, y, w, label, sub=None):
        self.back.append(f'<rect x="{x}" y="{y}" width="{w}" height="{46 if sub else 34}" rx="6" fill="#253858"/>')
        self.back.append(f'<text x="{x+w/2}" y="{y+22}" text-anchor="middle" font-size="14" font-weight="700" fill="#FFFFFF">{escape(label)}</text>')
        if sub:
            self.back.append(f'<text x="{x+w/2}" y="{y+39}" text-anchor="middle" font-size="11" fill="#B3BAC5">{escape(sub)}</text>')

    def vline(self, x, y1, y2):
        self.back.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#C1C7D0" stroke-dasharray="4 4"/>')

    def group(self, x, y, w, h, label, fill, stroke, sub=None):
        self.back.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        self.back.append(f'<text x="{x+18}" y="{y+28}" font-size="16" font-weight="700" fill="{stroke}">{escape(label)}</text>')
        if sub:
            self.back.append(f'<text x="{x+18}" y="{y+48}" font-size="12" fill="#5E6C84">{escape(sub)}</text>')

    # ---------- nodes ----------
    def box(self, nid, cx, cy, text, kind='plain', w=170, h=None, bold=False, fs=14):
        lines = text.split('\n')
        h = h or (22 * len(lines) + 22)
        fill, stroke, color = STY[kind]
        x, y = cx - w / 2, cy - h / 2
        self.front.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        self._text(cx, cy, lines, fs, color, bold)
        self.nodes[nid] = (cx, cy, w, h)

    def diamond(self, nid, cx, cy, text, w=170, h=84, fs=13):
        lines = text.split('\n')
        pts = f'{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}'
        self.front.append(f'<polygon points="{pts}" fill="#FFFFFF" stroke="#505F79" stroke-width="1.6"/>')
        self._text(cx, cy, lines, fs, '#172B4D', False)
        self.nodes[nid] = (cx, cy, w, h)

    def pill(self, nid, cx, cy, text, w=120, h=36, kind='sys'):
        fill, stroke, color = STY[kind]
        self.front.append(f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        self._text(cx, cy, [text], 13, color, True)
        self.nodes[nid] = (cx, cy, w, h)

    def note(self, x, y, text, fs=12, color='#5E6C84', anchor='start'):
        for i, ln in enumerate(text.split('\n')):
            self.front.append(f'<text x="{x}" y="{y+i*(fs+5)}" font-size="{fs}" fill="{color}" text-anchor="{anchor}">{escape(ln)}</text>')

    def _text(self, cx, cy, lines, fs, color, bold):
        lh = fs + 6
        y0 = cy - (len(lines) - 1) * lh / 2 + fs * 0.36
        wt = ' font-weight="700"' if bold else ''
        for i, ln in enumerate(lines):
            self.front.append(f'<text x="{cx}" y="{y0+i*lh}" text-anchor="middle" font-size="{fs}" fill="{color}"{wt}>{escape(ln)}</text>')

    # ---------- anchors ----------
    def p(self, nid, side):
        cx, cy, w, h = self.nodes[nid]
        return {'l': (cx - w / 2, cy), 'r': (cx + w / 2, cy), 't': (cx, cy - h / 2), 'b': (cx, cy + h / 2), 'c': (cx, cy)}[side]

    # ---------- edges ----------
    def arrow(self, pts, label=None, lx=None, ly=None, dashed=False, color='#505F79', la='middle'):
        d = 'M ' + ' L '.join(f'{x},{y}' for x, y in pts)
        dash = ' stroke-dasharray="6 5"' if dashed else ''
        self.back.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash} marker-end="url(#ah)"/>')
        if label:
            if lx is None:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 8
            self.front.append(f'<text x="{lx}" y="{ly}" font-size="12" fill="#253858" font-weight="700" text-anchor="{la}" paint-order="stroke" stroke="#FFFFFF" stroke-width="5">{escape(label)}</text>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">'
                '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path d="M0,0 L10,5 L0,10 z" fill="#505F79"/></marker></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>'
                + ''.join(self.back) + ''.join(self.front) + '</svg>')
