# Jira 에픽 만들기

스펙을 Confluence에 게시한 뒤 에픽을 만든다. 기준 문서: [원티드 채용 플랫폼 지라 사용 가이드 v2](https://wantedlab.atlassian.net/wiki/spaces/oneproduct/pages/5032247310/v2) (2026-11 기준 작성중. 가이드가 바뀌면 이 파일을 고친다). Atlassian MCP 도구(`getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `atlassianUserInfo`, `createJiraIssue`, `createIssueLink`)가 있을 때만. 없으면 건너뛰고 "Jira 연결이 없어 에픽은 만들지 않았습니다" 한 줄

## 에픽 기준 (v2 가이드)

- 에픽 하나는 배포 단위 하나. 스펙 문서와 에픽은 1:N
  - 구현 상세가 배포 단위로 하위 섹션이 나뉘어 있으면 하위 섹션마다 에픽 하나
  - 나뉘지 않았으면 문서 하나에 에픽 하나
  - 차수 문서가 따로 있으면 차수 문서마다 위 기준을 다시 적용. 상위 페이지에는 에픽을 만들지 않는다
- 보고자는 스펙 작성자 본인 (만들기와 배포 관리 담당). 담당자도 작성자 본인으로 만들고, 개발 시작 뒤 바꾸는 것은 개발 주체가 함
- 상태는 만들 때 `열림`(OPEN) 그대로. 진행중, 검토중은 개발 주체가, 완료는 보고자가 바꿈
- Story는 쓰지 않는다. Task, Sub-task도 만들지 않는다 (A/B 테스트 추적 Task 하나만 예외)
- Team 필드는 채우지 않는다

## 만드는 조건

- 스킬 흐름의 마지막 단계로 자동 진행한다. 만들지 묻지 않고, 미리보기로 확인받지 않고 바로 만든다
- 만든 뒤 링크를 주면서 "고칠 게 있으면 Jira에서 바로 고쳐 주세요"라고 안내한다
- 묻는 것은 레이블이 없을 때 레이블 하나뿐. 도메인 팩 `Jira 레이블`에 값이 있으면 묻지 않는다
- 건너뛰는 경우: Jira 연결이 없음, 메타 Jira 칸에 이미 링크가 있음, 작성자가 에픽을 만들지 말라고 함
- 게시를 건너뛰었거나 실패했으면 Confluence 링크 없이 만들고, 게시 뒤 설명에 링크를 넣는다

## 레이블 규칙

- 에픽은 레이블 필수. 레이블 없이는 만들지 않는다
- 영어는 소문자, 띄어쓰기는 `-`. 한글 가능
- 앞붙이: 팟 `pod-`, 챕터 `chapter-`, 실험 `exp-`, TF `tf-`, 프로젝트 `prj-`
  - 예: `pod-기업위생요인-이용불편`, `chapter-front`, `exp-공고상세-지원버튼-문구`
- 작성자가 넣은 값은 `scripts/jira_preview.py --check-label`로 검사. 형식이 틀리면 고친 값으로 만들고 안내에 적는다 (예: `POD AX인재` → `pod-ax인재`)
- 앞붙이가 없으면 어느 그룹인지 묻는다. 짐작으로 붙이지 않음
- 확정된 팟, 챕터 레이블은 도메인 팩 `Jira 레이블`에 저장해 다음 스펙의 기본값으로. 실험 레이블은 저장하지 않음

## 절차

1. 만들 값 뽑기: `python3 scripts/jira_preview.py docs/specs/{슬러그}/spec.md --url {Confluence URL}`
   - 스펙에서 에픽 후보(배포 단위), 요약, 설명, 날짜, A/B 테스트 포함 여부를 뽑아 JSON으로 낸다
   - 메타 '개발 일정'이 `YYYY-MM-DD~YYYY-MM-DD`이면 Start Date와 기한을 채운다. 하위 섹션마다 일정이 다르면 작성자에게 묻는다
2. 프로젝트 키: `docs/spec-context.md`의 `Jira 프로젝트` 값. 비어 있으면 기본값 `WRP`로 만든다. 다른 프로젝트를 쓰면 작성자가 도메인 팩에 적는다
3. `getJiraProjectIssueTypesMetadata`로 에픽 유형 id를 찾는다 (이름 `에픽` 또는 untranslatedName `Epic`). 없으면 "이 프로젝트에는 에픽 유형이 없습니다" 안내하고 멈춤. A/B 테스트 포함이면 Task 유형 id도 찾는다
4. `getJiraIssueTypeMetaWithFields`(requiredFieldsOnly=false)로 항목 key를 확인한다. 이름으로 찾음: `Start Date`/`시작 날짜`(WRP는 `customfield_10014`), `기한`(duedate), `레이블`(labels), `수정 버전`(fixVersions). 수정 버전 항목의 allowedValues에서 릴리스 목록을 읽는다. 레이블은 Jira에서 필수가 아니어도 이 스킬이 필수로 받는다 아래 표로 못 채우는 필수 항목은 작성자에게 묻는다. 짐작으로 채우지 않음
5. `atlassianUserInfo`로 작성자 계정을 찾는다. 안내에는 계정 ID 대신 이름을 씀
6. 레이블이 없으면 `AskUserQuestion` 한 번으로 레이블만 받는다 (선택지: 도메인 팩에 저장된 값, 없으면 "pod- 레이블 입력(기타)", "chapter- 레이블 입력(기타)"). 형식이 틀리면 고친 값으로 만든다
   - 수정 버전은 묻지 않고 기본값을 쓴다: `released`가 false이고 `releaseDate`가 기한 이후인 가장 가까운 정기배포(`Release_YYYYMMDD`). `overdue`와 `Hotfix_`는 고르지 않음. 기한이 없으면 비워 둔다
   - Start Date, 기한이 없으면 비워 두고 만든다
7. `createJiraIssue`로 에픽을 만든다. 배포 단위마다 하나
8. A/B 테스트 포함 스펙이면 실험 추적 Task를 하나 만든다 (아래 표). 에픽과 `relates to`로 `createIssueLink`
9. SQA 티켓은 묻지 않는다. 작성자가 요청에 SQA 키를 적었으면 `createIssueLink`로 `{SQA} blocks {에픽}` 연결
10. 에픽 링크를 스펙 메타 표 Jira 칸에 넣는다. 에픽이 여럿이면 `<br>`로 한 줄씩 `{요약}: {URL}`. 저장 → lint → `references/confluence.md` 갱신 절차로 페이지 반영
11. 안내 (채팅)
   ```
   Jira 에픽을 만들었어요. 고칠 게 있으면 Jira에서 바로 고쳐 주세요
   - {요약}: {URL}
   - 실험 Task: {URL} (있을 때)
   넣은 값: 레이블 {레이블}, 시작 날짜 {값 또는 비어 있음}, 기한 {값 또는 비어 있음}, 수정 버전 {값 또는 비어 있음}
   SQA 티켓이 있으면 에픽의 '연결된 이슈'에 blocks로 추가해 주세요
   ```

## 에픽 항목

| 항목 | 값 |
|---|---|
| 요약 | 스펙 제목에서 `(작성중) `과 `[{연도}] Product Spec: `를 뗀 것. 배포 단위가 둘 이상이면 끝에 ` ({N}차) {하위 섹션 이름}`. 차수 문서면 끝에 `({N}차)` |
| 설명 | 1줄: `스펙: {Confluence URL}`. 배포 단위가 나뉘면 `{Confluence URL}#{하위 섹션 제목의 공백을 -로 바꾼 것}`<br>그 아래: 그 배포 단위 표의 기능 열을 불릿으로. 나뉘지 않았으면 솔루션 묶음 이름을 불릿으로 |
| 담당자 | 작성자 본인 |
| 보고자 | 작성자 본인 (기본값) |
| 레이블 | 필수. 「레이블 규칙」 |
| Start Date | 개발 시작일. 메타 '개발 일정'의 시작일 |
| 기한 | 개발 완료일. 메타 '개발 일정'의 끝날 |
| 수정버전 | 배포 릴리스. Jira 릴리스 목록에서 고름 |

- 날짜는 `YYYY-MM-DD`
- 기획 일정, 배포 목표는 에픽 날짜에 쓰지 않는다 (v2에서 Start Date는 개발 시작, 기한은 개발 완료)

## A/B 테스트 추적 Task

A/B 테스트 포함 스펙(「실험 요청 구분」 2번)일 때만. 실험은 에픽이 완료된 뒤에도 이어지므로 에픽과 따로 둔다

| 항목 | 값 |
|---|---|
| 유형 | Task |
| 요약 | `[실험] {스펙 요약}` |
| 설명 | `스펙: {Confluence URL}#{KR 제목 앵커}` 한 줄과 실험 설계 표의 배분, 기간, 판정 시점 |
| 레이블 | `exp-{실험명}`. 실험명은 메타 '실험 Flag' 값이나 Amplitude 실험 키를 쓰고, 없으면 묻는다. 에픽 레이블도 함께 붙인다 |
| 기한 | 실험 종료일. 실험 설계 표의 기간 끝날, 없으면 묻는다 |
| 상위항목 | 두지 않음. 에픽과는 `relates to`로만 연결 |
