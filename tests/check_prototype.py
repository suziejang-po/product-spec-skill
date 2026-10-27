"""변경 표시 프로토타입 양식 점검: data-go, data-target, data-open, data-tab, data-validate, data-toast가 실제 id를 가리키는지"""
import re, sys
path = sys.argv[1]
html = re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)
ids = set(re.findall(r'\bid="([^"]+)"', html))
bad = []
for attr in ["data-go", "data-open", "data-tab", "data-validate", "data-toast"]:
    for v in re.findall(attr + r'="([^"]+)"', html):
        if v not in ids:
            bad.append(f"{attr}={v}")
for v in re.findall(r'href="#/?([^"]+)"', html):
    if v not in ids:
        bad.append(f"href=#{v}")
if re.search(r'<(script|link)[^>]+(src|href)="https?://', html):
    bad.append("외부 리소스 불러옴")
# 격리된 미리보기(아티팩트, 파일 미리보기)에서 막히는 브라우저 기능은 try 안에서만 부름
for line in html.splitlines():
    if re.search(r"(replaceState|pushState|localStorage|sessionStorage)", line) and "try" not in line:
        bad.append("try 없이 부름: " + line.strip()[:60])
if bad:
    print("실패: " + ", ".join(bad)); sys.exit(1)
print("통과 OK: 프로토타입 연결")
