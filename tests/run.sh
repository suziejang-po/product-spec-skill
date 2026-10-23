#!/usr/bin/env bash
# 스킬 자체 점검: 예시 문서는 lint를 통과하고, 일부러 틀린 문서는 각 검사에 걸려야 함
set -u
cd "$(dirname "$0")/.."
S=.claude/skills/product-spec
fail=0
for f in $S/references/template-example*.md; do
  if python3 $S/scripts/lint_spec.py "$f" >/dev/null; then echo "통과 OK: $f"; else echo "실패: 예시 문서가 lint에 걸림 $f"; fail=1; fi
done
out=$(python3 $S/scripts/lint_spec.py tests/fixtures/bad-spec.md)
for kind in "건수 줄" "메타" "문단 서술" "결정 날짜" "구현 상세 표" "넣지 않는 섹션" "확인 표시"; do
  if grep -q ": $kind:" <<<"$out"; then echo "검출 OK: $kind"; else echo "실패: '$kind'를 잡지 못함"; fail=1; fi
done
# 게시 변환기는 lint 위반이 있으면 본문을 만들지 않아야 함
if python3 $S/scripts/md_to_confluence.py tests/fixtures/bad-spec.md --out /tmp/_bad_body.html >/dev/null 2>&1; then
  echo "실패: 변환기가 lint 위반 문서를 변환함"; fail=1
else echo "검출 OK: 변환기가 게시를 막음"; fi
if python3 $S/scripts/md_to_confluence.py $S/references/template-example.md >/dev/null 2>&1; then echo "통과 OK: 변환기가 정상 문서를 변환함"; else echo "실패: 변환기가 정상 문서를 막음"; fail=1; fi
exit $fail
