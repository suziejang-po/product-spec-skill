"""변환기 링크 점검: 맨 URL은 스마트 링크, 마크다운 링크는 글자 그대로"""
import sys
sys.path.insert(0, sys.argv[1])
import md_to_confluence as m  # noqa: E402

a = m.inline("상위 문서: https://a.b/c")
b = m.inline("[문서](https://a.b/c)")
ok = 'data-card-appearance="inline"' in a and b == '<a href="https://a.b/c">문서</a>'
print("통과 OK: URL 링크 변환" if ok else f"실패: URL 링크 변환 {a} / {b}")
sys.exit(0 if ok else 1)
