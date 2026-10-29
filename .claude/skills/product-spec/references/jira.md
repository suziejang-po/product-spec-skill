# Jira 에픽 만들기

스펙을 Confluence에 게시한 뒤 개발 킥오프용 에픽을 만든다. Atlassian MCP 도구(`getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `createJiraIssue`)가 있을 때만. 없으면 건너뛰고 "Jira 연결이 없어 에픽은 만들지 않았습니다" 한 줄

## 만드는 조건

- Phase 5 게시가 끝난 스펙. 게시하지 않았으면 만들기 전에 "Confluence 링크 없이 에픽을 만들까요?" 묻는다
- 스펙 메타 표 Jira 칸이 비어 있을 때만. 이미 있으면 만들지 않고 그 링크를 안내
- 차수가 나뉜 스펙은 차수 문서마다 에픽 하나. 상위 페이지에는 에픽을 만들지 않는다

## 절차

1. 프로젝트 키: `docs/spec-context.md`의 `Jira 프로젝트` 줄을 읽는다. 없으면 묻는다: "에픽을 만들 Jira 프로젝트 키를 알려 주세요 (예: WRP)". 답을 그 줄에 저장해 다음부터 묻지 않음
2. `getJiraProjectIssueTypesMetadata`로 그 프로젝트에 Epic 유형이 있는지 확인. 없으면 "이 프로젝트에는 Epic 유형이 없습니다" 안내하고 멈춤
3. `getJiraIssueTypeMetaWithFields`로 필수 항목을 확인. 아래 기본값으로 못 채우는 필수 항목은 작성자에게 묻는다. 짐작으로 채우지 않음
4. 미리보기를 채팅에 보여주고 한 번 확인받는다: "이대로 에픽을 만들까요? 1) 만듦 2) 고칠 것 있음"
   - 작성자가 "확인 없이 만들어"라고 한 적이 있으면 `docs/spec-context.md`의 `Jira 에픽 확인 생략: 예`를 보고 바로 만든다
5. `createJiraIssue`로 만든다
6. 응답의 이슈 키로 링크를 만들어 스펙 메타 표 Jira 칸에 넣고 저장 → lint → `references/confluence.md` 갱신 절차로 페이지 반영
7. 안내: "에픽: {KEY} {URL}". 차수가 나뉘었으면 차수별로 한 줄씩

## 기본값

| 항목 | 값 |
|---|---|
| 요약 | 스펙 제목에서 `(작성중)`과 `[{연도}] Product Spec: ` 를 뗀 것. 차수가 있으면 끝에 `({N}차)` |
| 설명 | 1줄: `스펙: {Confluence URL}`<br>그 아래: 1-5 솔루션 불릿 그대로 |
| 담당자 | 비움. 작성자가 말하면 채움 |
| 라벨, 컴포넌트, 기한 | 비움. 필수 항목이면 3번에서 묻는다 |

- 팀 Jira 작성 규칙 문서가 도메인 팩에 있으면 그 규칙을 따른다 (라벨, 상위 이니셔티브 등)
- 하위 스토리와 태스크는 만들지 않는다. 쪼개기는 개발 킥오프에서 정함
