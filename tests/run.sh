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
# v5.7 검사: 문제 길이, 근거 위치, 코드 블록 위치, 섹션 순서, 표시 형태, 용어 정의, 근거 블록 제목, 비율 분모
out57=$(python3 $S/scripts/lint_spec.py tests/fixtures/bad-spec-v57.md)
for kind in "문제 길이" "근거 위치" "코드 블록" "섹션 순서" "표시 형태" "용어 정의 표" "근거 블록" "비율 분모" "불릿 끝 마침표"; do
  if grep -q ": $kind:" <<<"$out57"; then echo "검출 OK: $kind"; else echo "실패: '$kind'를 잡지 못함"; fail=1; fi
done
# 메타 표는 첫 열만 머리글, 펼치기는 Confluence 펼치기로
body=$(python3 $S/scripts/md_to_confluence.py $S/references/template-example.md 2>/dev/null)
if grep -q '<tr><th data-colwidth="160"><p>PO</p></th><td' <<<"$body" && ! grep -q '<thead><tr><th[^>]*><p>PO</p>' <<<"$body"; then echo "통과 OK: 메타 표 첫 열 머리글"; else echo "실패: 메타 표 머리글"; fail=1; fi
if grep -q '<details><summary>데이터 근거: ' <<<"$body" && grep -q '<details><summary>[^<]*</summary>.*<pre><code class="language-sql">' <<<"$body"; then echo "통과 OK: 데이터 근거 펼치기와 쿼리"; else echo "실패: 데이터 근거 펼치기"; fail=1; fi
# Jira 에픽 미리보기 (v2 가이드): 배포 단위, 날짜, 레이블, A/B 테스트 Task, 이미 있는 Jira 칸
jp() { python3 $S/scripts/jira_preview.py "$@"; }
chk() { if python3 -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if ($2) else 1)" <<<"$1"; then echo "통과 OK: jira $3"; else echo "실패: jira $3"; fail=1; fi; }
chk "$(jp $S/references/template-example.md --label pod-ax인재)" "d['epic_count']==1 and d['can_create'] and d['label_check']['ok']" "기능 스펙 에픽 1개"
chk "$(jp $S/references/template-example-enhancement.md --url https://x/p/1)" "d['epic_count']==2 and '#2-1.-목록-표기-개선' in d['epics'][0]['description'] and '(2차)' in d['epics'][1]['summary']" "배포 단위 2개면 에픽 2개와 하위 섹션 링크"
chk "$(jp tests/fixtures/jira-has-epic.md)" "not d['can_create']" "Jira 칸에 값이 있으면 만들지 않음"
chk "$(jp $S/references/template-example-new.md)" "d['can_create']" "Jira 칸의 양식 자리 표시는 빈칸으로 봄"
chk "$(jp tests/fixtures/jira-ab.md --label 'POD 지원')" "d['epics'][0]['start_date']=='2026-12-01' and d['epics'][0]['due_date']=='2026-12-19' and d['epics'][0]['labels']==['pod-지원'] and d['ab_test_task'] and d['ab_test_task']['labels'][0]=='exp-공고상세-지원버튼'" "개발 일정 날짜, 레이블 고침, 실험 Task"
chk "$(jp $S/references/template-example.md)" "not d['label_check']['ok'] and d['epics'][0]['labels']==[]" "레이블 없으면 필수 안내"
for bad in "ax인재" "pod-" "" "POD AX"; do
  if jp --check-label "$bad" >/dev/null; then echo "실패: jira 레이블 '$bad'를 통과시킴"; fail=1; else echo "검출 OK: jira 레이블 '$bad'"; fi
done
for good in "pod-ax인재" "chapter-front" "exp-detail-apply-cta" "prj-신규"; do
  if jp --check-label "$good" >/dev/null; then echo "통과 OK: jira 레이블 '$good'"; else echo "실패: jira 레이블 '$good'를 막음"; fail=1; fi
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
