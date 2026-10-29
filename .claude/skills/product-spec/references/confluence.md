# Confluence 게시

Atlassian MCP 도구(`createConfluencePage`, `updateConfluencePage`, `getConfluencePage`, `createConfluenceInlineComment`, `getAccessibleAtlassianResources`, `atlassianUserInfo`)가 있을 때만 실행. 없으면 이 절차 전체를 건너뛰고 한 줄 안내: "Confluence 게시는 Atlassian MCP 연결 후 다시 요청하면 됩니다"

정본은 로컬 스펙 파일이다. Confluence는 로컬을 변환해 올린 사본이며, 갱신은 전체 본문 덮어쓰기가 기본이고, 한두 줄 수정은 아래 「작은 수정」 경로를 쓸 수 있다. 사람이 Confluence에서 직접 고친 내용은 덮어쓰기 전 확인으로 지킨다

## 설정

부모 페이지와 스페이스는 도메인 팩(`docs/spec-context.md`)의 Confluence 설정 표에서 읽는다. 없으면 기본값 spaceKey `WAN`, 작성중 부모 `4808376595`, 출시 확정 부모 `4808212726`. 생성이 권한 오류(403)로 실패하면 "이 스페이스에 페이지를 만들 권한이 없습니다. 개인 스페이스에 만들까요, 아니면 부모 페이지 ID를 알려 주시겠어요?"라고 묻는다

## 본문 만들기

```
python3 {SKILL_DIR}/scripts/md_to_confluence.py spec.md --diagram-mode attach --media-json media.json --out body.html
```

- `contentFormat`는 `html`. 변환기가 금지 기호를 치환하고, 표 첫 열이 `#`이면 번호 열을 40으로, 화면 단위 3열 표는 140, 200, 나머지로 폭을 고정
- 변환기가 표준 오류로 본문 크기와 알림(첨부 정보 없음, 그림 파일 없음)을 낸다. 알림은 게시 안내에 그대로 붙임
- 본문은 `--out body.html`로 파일에도 저장하고, `updateConfluencePage`에 넣기 전에 파일 크기와 인자 길이가 같은지 확인 (잘림 방지). 43KB 본문은 한 번에 올라갔다 (2026-10-12 실측). 한두 줄 수정은 「작은 수정」 경로
- 게시 전 lint 통과 필수. 변환기가 먼저 `lint_spec.py`를 돌리고 위반이 있으면 본문을 만들지 않고 종료 코드 1로 멈춘다. 이때는 위반을 고쳐 다시 변환한다
- `createConfluencePage`, `updateConfluencePage`에 넣는 본문은 변환기가 만든 `body.html`만. 직접 쓴 HTML, 마크다운 원문, 요약본을 넣지 않는다

## 첫 게시 (spec.md 첫 줄에 Page ID 주석 없음)

1. 안내: "Confluence에 새 페이지를 만듭니다 (5분 정도)"
2. `getAccessibleAtlassianResources`로 cloudId
3. 제목 `(작성중) [{올해}] Product Spec: {제목}`으로 `createConfluencePage`. 그림 자리를 비운 본문으로 먼저 만든다 (그림은 페이지가 있어야 첨부 가능)
4. 응답의 pageId를 즉시 로컬 spec.md 첫 줄에 `<!-- Confluence Page ID: {pageId} -->`로 기록하고 저장. 본문 메타 표에는 넣지 않음 (변환기가 주석을 지우므로 Confluence에는 보이지 않음) (이후 단계가 실패해도 페이지를 잃지 않기 위함)
5. 그림 업로드 → media.json → 본문 재변환 → `updateConfluencePage` (`references/diagram.md`)
6. 수치 인라인 댓글 (아래)
7. 안내: "게시: {URL}. 지금은 '제품 출시 미정' 아래 (작성중) 상태입니다. 출시가 확정되면 알려 주세요"

실패 복구: 3번 뒤에 실패하면 페이지는 있고 그림이 없는 상태. 다음 실행에서 첫 줄 주석의 Page ID로 갱신 절차를 타면 복구된다. 안내에 "그림 삽입이 실패했습니다. 다시 '게시해줘'라고 하면 이어서 합니다"를 붙인다

## 갱신 (spec.md 첫 줄에 Page ID 주석 있음)

1. 안내: "Confluence 페이지를 갱신합니다 (5분 정도). 끝날 때까지 페이지 편집을 멈춰 주세요"
2. `getConfluencePage(pageId)`로 `version.number`, `version.by.accountId`, `version.by.displayName`, `version.when` 확인. 이전에 읽은 값을 재사용하지 않음
3. `atlassianUserInfo`의 본인 accountId와 비교. 다른 사람이 마지막 편집자면 멈추고 묻는다
   ```
   ⚠️ 다른 사람의 편집이 있습니다. 마지막 편집: {displayName} / {when}
   로컬 스펙으로 전체를 덮어쓰면 그 편집이 사라집니다. 'yes' 덮어씀 / 'cancel' 중단 (중단 후 Confluence 내용을 로컬에 먼저 반영할 수 있습니다)
   ```
4. 로컬 스펙 전체를 변환해 `updateConfluencePage`. `contentFormat`는 `html`, `versionMessage`에 변경 요약 한 줄
5. 응답 `version.number`가 N+1이 아니면 동시 편집으로 보고 즉시 멈추고 보고
6. 안내: "갱신 완료. 편집 가능"

## 작은 수정 (Chrome 경로)

한두 줄을 고치는데 본문 전체(40KB 안팎)를 MCP 인자로 다시 보내면 느리고 잘릴 위험이 있다. Claude in Chrome이 있고 Confluence에 로그인돼 있으면 페이지에서 REST로 그 부분만 바꾼다 (2026-10-12 실측)

1. 페이지를 열고 `fetch('/wiki/api/v2/pages/{pageId}?body-format=storage')`로 본문과 `version.number`, `version.authorId`를 읽음. 마지막 편집자가 본인이 아니면 갱신 절차 3번처럼 멈추고 묻는다
2. 바꿀 문자열이 본문에 정확히 한 번 나오는지 확인. 0번이거나 2번 이상이면 멈춤
   - 목록 항목을 나누거나 더할 때는 `<li><p>…</p></li>` 꼴을 그대로 지킨다. `<p>` 안에서 `</li><li>`로 자르면 빈 항목이 생긴다 (2026-10-13 실측)
3. 문자열을 바꾼 본문으로 `PUT /wiki/api/v2/pages/{pageId}` (`representation: storage`, `version.number`는 읽은 값 + 1, `version.message`에 변경 한 줄)
4. 같은 내용을 로컬 `spec.md`에도 고친다. 한쪽만 고치지 않음
5. 페이지를 다시 열어 바뀐 곳을 확인

- 여러 사람이 같은 페이지를 열어 둔 라이브 문서면, PUT 직전에 본문을 다시 읽고 그 본문에 고칠 내용을 적용한다. 몇 분 전에 읽은 본문으로 PUT하면 그 사이 다른 사람(작성자 포함)이 고친 내용이 사라진다 (2026-10-15 실측: 작성자가 넣은 상태 매크로가 덮어써짐)
- 페이지를 새로 열면 페이지 JS에 정의한 도우미 함수가 사라진다. 다시 정의하고 시작
- 인라인 댓글이 달린 글자는 `<ac:inline-comment-marker>`로 감싸져 있어 문자열 바꾸기가 안 맞을 수 있다. 바꿀 때 마커를 그대로 옮겨 넣는다 (지우면 댓글이 사라짐)
- 문서 안 링크는 쓰지 않는다. 다른 곳은 "7-2 신청 취소 확인"처럼 번호와 이름으로

## 차수가 나뉜 문서

상위 페이지 하나 아래에 차수 페이지를 하위로 둔다. 상위 페이지에는 하위 페이지 목록이 자동으로 나와 바로 이동할 수 있다

- 상위 페이지
  - 제목 `[{올해}] Product Spec: {제목}`. 로컬은 `docs/specs/{슬러그}/index.md`, Page ID는 그 첫 줄
  - 본문은 `python3 {SKILL_DIR}/scripts/parent_page.py --summary "{1차 문서 1-5 솔루션 첫 줄}"` 출력만. Confluence '하위 페이지' 매크로가 차수 페이지 목록을 그린다. 차수 페이지가 늘어도 상위 본문은 고치지 않는다
  - 첫 차수를 게시할 때 상위 페이지가 없으면 먼저 만든다 ('제품 출시 미정' 아래)
- 차수 페이지
  - 제목 `(작성중) [{올해}] Product Spec: {제목} ({N}차)`. `createConfluencePage`의 parentId는 상위 페이지
  - 차수 폴더(`p1/`, `p2/`)마다 첫 게시와 갱신을 따로 한다. Page ID는 각 폴더 `spec.md` 첫 줄에. 한 페이지에 두 차수를 올리지 않는다
  - 1-7 참고에 `상위 문서: {상위 URL}` 한 줄
- 출시 확정 이동은 상위 페이지만 옮긴다. 하위 페이지는 따라간다. 차수 페이지 제목의 `(작성중) `은 차수마다 따로 뗀다
- 게시 안내에는 상위와 차수별 링크를 한 줄씩 모두 쓴다. 이번에 게시하지 않은 차수도 페이지가 있으면 같이 쓰고, 아직 없으면 `(아직 없음)`
  ```
  상위: {URL}
  1차: {URL} (갱신)
  2차: {URL} (새로 만듦)
  ```
- 상태 매크로로 차수를 표시하지 않는다

## 시트 첨부

값이 많은 목록은 xlsx로 만들어 페이지에 첨부하고 본문에는 링크만. 링크 꼴: `https://{사이트}/wiki/download/attachments/{pageId}/{파일명}`

## Confluence에서 직접 고친 뒤 로컬 맞추기

작업을 Confluence에서 바로 했으면(작은 수정 경로, 작성자 직접 편집) 끝에 로컬을 맞춘다. 한쪽만 최신인 채로 끝내지 않음
1. 로컬 `spec.md`를 `spec.md.bak.{YYYYMMDD-HHMMSS}`로 백업
2. Confluence 본문을 마크다운으로 받아 `spec.md`에 저장. 표 셀 안 목록은 `<br>- `, 딸린 항목은 `<br>  - `로 바꾸고, 그림은 `diagrams/{첨부 파일명}`으로
3. 페이지 첨부의 그림과 시트를 `diagrams/`와 스펙 폴더에 같은 파일명으로 둠
4. lint 통과 확인

## 출시 확정 이동

작성자가 "출시 확정", "작성 완료했어"라고 하면
1. 확인: "'제품 출시 확정' 아래로 옮길까요? 'yes' / 'cancel'"
2. yes면 제목에서 `(작성중) ` 제거, `updateConfluencePage`의 parentId를 출시 확정 부모로
3. 안내: "제목 갱신과 이동 완료"

## 수치 인라인 댓글

근거(Amplitude 차트 링크, BQ 쿼리)가 있는 수치에만 단다. 근거가 출처 문서 참조뿐이면 댓글을 달지 않는다
1. `getConfluencePage(pageId, contentFormat="markdown")`으로 렌더 텍스트를 받는다
2. 수치 문자열(예: `56.26%`)이 본문에 몇 번 나오는지 센다 → `textSelectionMatchCount`
3. `createConfluenceInlineComment(pageId, body, inlineCommentProperties={textSelection: "56.26%", textSelectionMatchCount: N, textSelectionMatchIndex: 0})`. 본문은 링크 한 줄 또는 `<pre><code class="language-sql">쿼리</code></pre>`
4. 같은 수치가 두 곳 이상이면 첫 번째(index 0)에만
5. 400이 나면 문자열이 렌더 텍스트와 다른 것. 표 셀 안의 수치는 앞뒤 공백 없이 정확히 맞춘다

## 결정 이력

본문에 쓰지 않는다. `versionMessage`에 한 줄로 남긴다 (예: "배너 위치를 제안 상세 표 아래로 변경")

## 표 규칙

- 번호 열은 `data-colwidth="40"`, 나머지 열은 남은 폭을 나눔. 변환기가 처리
- 셀 안 줄바꿈은 `<br>`. 마크다운 원문에서 `<br>`로 적어야 변환됨
- 셀 안의 `|`는 인라인 코드로 감싸거나 `\|`로 씀
- 표를 패널 안에 넣지 않음 (Confluence가 거부)
- 문서 안 링크(앵커)는 넣지 않음
