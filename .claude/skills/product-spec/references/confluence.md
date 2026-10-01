# Confluence 게시

Atlassian MCP 도구(`createConfluencePage`, `updateConfluencePage`, `getConfluencePage`, `createConfluenceInlineComment`, `getAccessibleAtlassianResources`, `atlassianUserInfo`)가 있을 때만 실행. 없으면 이 절차 전체를 건너뛰고 한 줄 안내: "Confluence 게시는 Atlassian MCP 연결 후 다시 요청하면 됩니다"

정본은 로컬 스펙 파일이다. Confluence는 로컬을 변환해 올린 사본이며, 갱신은 부분 치환이 아니라 전체 본문 덮어쓰기로 한다. 사람이 Confluence에서 직접 고친 내용은 덮어쓰기 전 확인으로 지킨다

## 설정

부모 페이지와 스페이스는 도메인 팩(`docs/spec-context.md`)의 Confluence 설정 표에서 읽는다. 없으면 기본값 spaceKey `WAN`, 작성중 부모 `4808376595`, 출시 확정 부모 `4808212726`. 생성이 권한 오류(403)로 실패하면 "이 스페이스에 페이지를 만들 권한이 없습니다. 개인 스페이스에 만들까요, 아니면 부모 페이지 ID를 알려 주시겠어요?"라고 묻는다

## 본문 만들기

```
python3 {SKILL_DIR}/scripts/md_to_confluence.py spec.md --diagram-mode attach --media-json media.json --out body.html
python3 {SKILL_DIR}/scripts/md_to_confluence.py spec.md --diagram-mode macro --out body.html
```

- `contentFormat`는 `html`. 변환기가 금지 기호를 치환하고, 표 첫 열이 `#`이면 열 폭을 고정해 번호 열을 40으로 좁힘
- 변환기가 표준 오류로 본문 크기와 알림(첨부 정보 없음, 그림 파일 없음)을 낸다. 알림은 게시 안내에 그대로 붙임
- 본문 크기가 40KB를 넘으면 `references/diagram.md`의 크기 규칙을 따름
- 게시 전 lint 통과 필수

## 첫 게시 (메타에 Confluence Page ID 없음)

1. 안내: "Confluence에 새 페이지를 만듭니다 (5분 정도)"
2. `getAccessibleAtlassianResources`로 cloudId
3. 제목 `(작성중) [{올해}] Product Spec: {제목}`으로 `createConfluencePage`. 첨부 경로면 그림 자리를 비운 본문으로 먼저 만들고, 블록 경로면 완성 본문으로 만든다
4. 응답의 pageId를 즉시 로컬 스펙 메타의 Confluence Page ID에 기록하고 저장 (이후 단계가 실패해도 페이지를 잃지 않기 위함)
5. 첨부 경로면 그림 업로드 → media.json → 본문 재변환 → `updateConfluencePage`
6. 수치 인라인 댓글 (아래)
7. 안내: "게시: {URL}. 지금은 '제품 출시 미정' 아래 (작성중) 상태입니다. 출시가 확정되면 알려 주세요"

실패 복구: 3번 뒤에 실패하면 페이지는 있고 그림이 없는 상태. 다음 실행에서 메타의 Page ID로 갱신 절차를 타면 복구된다. 안내에 "그림 삽입이 실패했습니다. 다시 '게시해줘'라고 하면 이어서 합니다"를 붙인다

## 갱신 (메타에 Page ID 있음)

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
