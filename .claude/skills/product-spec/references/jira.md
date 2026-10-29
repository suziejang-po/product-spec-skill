# Jira 에픽 만들기

스펙을 Confluence에 게시한 뒤 에픽을 만든다. 기준 문서: [WRP 지라 사용 가이드](https://wantedlab.atlassian.net/wiki/spaces/oneproduct/pages/4680253552/WRP). Atlassian MCP 도구(`getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `atlassianUserInfo`, `createJiraIssue`)가 있을 때만. 없으면 건너뛰고 "Jira 연결이 없어 에픽은 만들지 않았습니다" 한 줄

## 에픽 기준 (WRP 가이드)

- 에픽은 여러 스토리가 모여 사용자 가치 하나를 바꾸는 단위. 스펙 문서 하나(차수가 나뉘면 차수 문서 하나)가 에픽 하나
- 담당자와 보고자는 PO. 스펙 작성자 본인
- 상태는 만들 때 `To Do` 그대로 둔다. 상태 변경은 작성자가 함
- 스토리, 작업은 만들지 않는다. 쪼개기는 개발 킥오프에서 정함

## 만드는 조건

- Phase 5 게시가 끝난 스펙. 게시하지 않았으면 만들기 전에 "Confluence 링크 없이 에픽을 만들까요?" 묻는다
- 스펙 메타 표 Jira 칸이 비어 있을 때만. 이미 있으면 만들지 않고 그 링크를 안내
- 차수가 나뉜 스펙은 차수 문서마다 에픽 하나. 상위 페이지에는 에픽을 만들지 않는다

## 절차

1. 프로젝트 키: `docs/spec-context.md`의 `Jira 프로젝트` 값. 비어 있으면 기본값 `WRP`로 미리보기에 넣고, 미리보기에서 작성자가 바꿀 수 있게 함. 확정된 값은 도메인 팩에 저장
2. `getJiraProjectIssueTypesMetadata`로 에픽 유형 id를 찾는다 (이름 `에픽` 또는 untranslatedName `Epic`). 없으면 "이 프로젝트에는 에픽 유형이 없습니다" 안내하고 멈춤
3. `getJiraIssueTypeMetaWithFields`(requiredFieldsOnly=false)로 항목 id를 확인. 시작 날짜는 이름이 `시작 날짜` 또는 `Start Date`인 항목의 key를 쓴다 (WRP는 `customfield_10014`). 아래 표로 못 채우는 필수 항목은 작성자에게 묻는다. 짐작으로 채우지 않음
4. `atlassianUserInfo`의 account_id를 담당자로
5. 미리보기를 채팅에 보여주고 한 번 확인받는다: "이대로 에픽을 만들까요? 1) 만듦 2) 고칠 것 있음"
   - 레이블, 시작 날짜, 기한이 비어 있으면 미리보기에서 같이 묻는다 (가이드의 주요 항목)
   - 도메인 팩에 `Jira 에픽 확인 생략: 예`가 있으면 묻지 않고 만든다. 이 값은 작성자가 "확인 없이 만들어"라고 할 때만 바꾼다
6. `createJiraIssue`로 만든다. 이슈 유형 이름은 2번에서 찾은 이름 그대로 (WRP는 `에픽`). 만든 직후 상태는 WRP에서 `열림`(해야 할 일)으로 보인다
7. 응답의 이슈 키로 `https://{사이트}/browse/{KEY}` 링크를 만들어 스펙 메타 표 Jira 칸에 넣고 저장 → lint → `references/confluence.md` 갱신 절차로 페이지 반영
8. 안내: "에픽: {KEY} {URL}". 차수가 나뉘었으면 차수별로 한 줄씩

## 항목 기본값

| 항목 | 값 |
|---|---|
| 요약 | 스펙 제목에서 `(작성중) `과 `[{연도}] Product Spec: `를 뗀 것. 차수가 있으면 끝에 `({N}차)` |
| 설명 (필수) | 1줄: `스펙: {Confluence URL}`<br>그 아래: 1-5 솔루션 불릿 그대로 |
| 담당자 | 작성자 본인 (4번) |
| 보고자 | 작성자 본인 (기본값) |
| 레이블 | 과제 구분 (이니셔티브, 챕터 과제 등). 도메인 팩 `Jira 레이블` 값, 없으면 미리보기에서 묻는다 |
| 시작 날짜 | 기획 시작일. 메타 '기획 일정'의 시작일, 없으면 묻는다 |
| 기한 | 배포일. 메타 '배포 목표', 없으면 묻는다 |

- 날짜는 `YYYY-MM-DD`. 메타에 날짜가 범위로 적혀 있으면 시작일, 끝날을 각각 씀
- 작성자가 "비워 둬"라고 한 항목은 비우고 만든다 (필수 항목 제외)
