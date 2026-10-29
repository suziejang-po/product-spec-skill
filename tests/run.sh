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
for kind in "건수 줄" "메타" "문단 서술" "결정 날짜" "구현 상세 표" "넣지 않는 섹션" "확인 표시" "차수 섞임"; do
  if grep -q ": $kind:" <<<"$out"; then echo "검출 OK: $kind"; else echo "실패: '$kind'를 잡지 못함"; fail=1; fi
done
# 도메인 말 '1차 면접'은 차수 섞임으로 잡지 않아야 함
printf '## 1. 개요\n\n- 서류 통과자는 1차 면접으로 이동\n' > /tmp/_phase_ok.md
if python3 $S/scripts/lint_spec.py /tmp/_phase_ok.md | grep -q '차수 섞임'; then echo "실패: '1차 면접'을 차수 섞임으로 잡음"; fail=1; else echo "통과 OK: 도메인 말 '1차 면접'은 통과"; fi
# 상위 페이지 본문에 하위 페이지 목록 매크로가 들어가야 함
if python3 $S/scripts/parent_page.py --summary '<b>테스트</b>' | grep -q 'data-extension-key="children"' && ! python3 $S/scripts/parent_page.py --summary '<b>x</b>' | grep -q '<b>'; then echo "통과 OK: 상위 페이지 하위 목록 매크로"; else echo "실패: 상위 페이지 본문"; fail=1; fi
# 맨 URL은 스마트 링크로, 마크다운 링크는 그대로
python3 tests/check_links.py $S/scripts || fail=1
# 게시 변환기는 lint 위반이 있으면 본문을 만들지 않아야 함
if python3 $S/scripts/md_to_confluence.py tests/fixtures/bad-spec.md --out /tmp/_bad_body.html >/dev/null 2>&1; then
  echo "실패: 변환기가 lint 위반 문서를 변환함"; fail=1
else echo "검출 OK: 변환기가 게시를 막음"; fi
if python3 $S/scripts/md_to_confluence.py $S/references/template-example.md >/dev/null 2>&1; then echo "통과 OK: 변환기가 정상 문서를 변환함"; else echo "실패: 변환기가 정상 문서를 막음"; fail=1; fi
python3 tests/check_prototype.py $S/references/change-prototype-template.html || fail=1
# skill-files 목록에 있는 파일이 실제로 있는지
while read -r f; do [ -f "$S/$f" ] || { echo "실패: skill-files에 있는데 없음 $f"; fail=1; }; done < <(sed -n '/^## skill-files/,$p' $S/SKILL.md | grep '^- ' | sed 's/^- //')
exit $fail
