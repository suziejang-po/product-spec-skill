#!/usr/bin/env python3
"""SVG를 PNG로 렌더 (2배). 사용법: render_svg.py <a.svg> [b.svg ...]
같은 이름의 .png를 옆에 만든다. 1순위 Python playwright, 2순위 Chrome/Chromium headless.
둘 다 없으면 종료 코드 1과 안내"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/opt/pw-browsers/chromium",
]


def size(svg):
    w = int(float(re.search(r'width="([\d.]+)"', svg).group(1)))
    h = int(float(re.search(r'height="([\d.]+)"', svg).group(1)))
    return w, h


def with_playwright(files):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(device_scale_factor=2)
        for f in files:
            svg = open(f, encoding="utf-8").read()
            w, h = size(svg)
            pg.set_viewport_size({"width": w, "height": h})
            pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
            pg.wait_for_timeout(200)
            pg.screenshot(path=f[:-4] + ".png", clip={"x": 0, "y": 0, "width": w, "height": h})
            print(f[:-4] + ".png")
        b.close()


def find_chrome():
    for name in ("google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


def with_chrome(files, chrome):
    for f in files:
        svg = open(f, encoding="utf-8").read()
        w, h = size(svg)
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as t:
            t.write(f'<html><body style="margin:0">{svg}</body></html>')
        out = os.path.abspath(f[:-4] + ".png")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={w},{h}",
                        f"--screenshot={out}", "file://" + t.name],
                       check=True, capture_output=True, timeout=60)
        os.unlink(t.name)
        print(out)


def main():
    files = [f for f in sys.argv[1:] if f.endswith(".svg")]
    if not files:
        print("사용법: render_svg.py <a.svg> [...]")
        return 2
    try:
        with_playwright(files)
        return 0
    except Exception as e:  # playwright 없음 또는 실행 실패
        err = e
    chrome = find_chrome()
    if chrome:
        with_chrome(files, chrome)
        return 0
    print(f"렌더 실패: Python playwright 또는 Chrome이 필요함 ({err})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
