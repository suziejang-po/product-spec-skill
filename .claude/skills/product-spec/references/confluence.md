# Confluence 게시

Atlassian MCP 도구(`createConfluencePage`, `updateConfluencePage`, `getConfluencePage`, `createConfluenceInlineComment`, `getAccessibleAtlassianResources`, `atlassianUserInfo`)가 있을 때만 실행. 없으면 이 절차 전체를 건너뛰고 한 줄 안내: "Confluence 게시는 Atlassian MCP 연결 후 다시 요청하면 됩니다"

## 본문 만들기

```
python3 scripts/md_to_confluence.py docs/PRODUCT_SPEC.md --diagram-mode attach --media-json /tmp/media.json
python3 scripts/md_to_confluence.py docs/PRODUCT_SPEC.md --diagram-mode macro
```

- `contentFormat`는 `html`. 변환기가 금지 기호를 치환하고 표 첫 열이 `#`이면 열 폭을 고정해 번호 열을 40으로 좁힘
- 변환기의 표준 오류 출력(첨부 정보 없음, 그림 파일 없음)이 있으면 게시 안내에 그대로 붙임
- 게시 전 `python3 scripts/lint_spec.py docs/PRODUCT_SPEC.md` 통과 필수

## 첫 게시 (메타에 Confluence Page ID 없음)

1. 안내: "⏳ Confluence에 새 페이지를 만듭니다. 5분 정도 걸릴 수 있습니다"
2. 부모 페이지 고정: spaceKey `WAN`, parentId `4808376595` (작성중 문서 보관). 부모를 묻지 않음
3. `getAccessibleAtlassianResources`로 cloudId
4. 다이어그램 경로가 첨부이면 그림 자리를 비운 본문으로 먼저 `createConfluencePage` → pageId → 첨부 업로드 → media.json 작성 → 본문 재변환 → `updateConfluencePage`. 블록 경로이면 한 번에 생성
5. 제목: `(작성중) [{올해}] Product Spec: {제목}`
6. pageId를 `docs/PRODUCT_SPEC.md` 메타의 Confluence Page ID에 기록
7. 수치 인라인 댓글 (아래)
8. 안내: "게시: {URL}. 지금은 '제품 출시 미정' 아래 (작성중) 상태입니다. 출시가 확정되면 알려 주세요"

## 갱신 (메타에 Page ID 있음)

1. 안내: "⏳ Confluence 페이지를 갱신합니다. 5분 정도 걸릴 수 있습니다. 끝날 때까지 페이지 편집을 멈춰 주세요"
2. `getConfluencePage(pageId)`로 `version.number`, `version.by.accountId`, `version.by.displayName`, `version.when` 확인. 이전에 읽은 값을 재사용하지 않음
3. `atlassianUserInfo`의 본인 accountId와 비교. 다른 사람이 마지막 편집자면 멈추고 묻는다
   ```
   ⚠️ 다른 사람의 편집이 있습니다. 마지막 편집: {displayName} / {when}
   덮어쓰면 그 편집이 사라질 수 있습니다. 'yes' 덮어씀 / 'cancel' 중단
   ```
4. 변경된 섹션만 치환. 전체 재작성 금지. `contentFormat`는 읽을 때와 같은 값
5. 응답 `version.number`가 N+1이 아니면 동시 편집으로 보고 즉시 멈추고 보고
6. 안내: "갱신 완료. 편집 가능"

## 출시 확정 이동

작성자가 "출시 확정", "작성 완료했어"라고 하면
1. 확인: "'제품 출시 확정' 아래로 옮길까요? 'yes' / 'cancel'"
2. yes면 제목에서 `(작성중) ` 제거, `updateConfluencePage`의 parentId를 `4808212726`으로
3. 안내: "제목 갱신과 이동 완료"

## 수치 인라인 댓글

본문의 수치(현재 값, 모수, 비율)마다 근거를 인라인 댓글로 단다. `createConfluenceInlineComment`에 대상 텍스트로 수치 문자열(예: `56.26%`)을, 본문으로 근거를 넣는다
- Amplitude 차트가 있으면 링크 한 줄
- BigQuery 쿼리가 있으면 쿼리 전문을 코드로
- 근거가 없으면 댓글을 달지 않고 본문의 `⚠️ 쿼리 첨부 필요`만 남김
- 같은 수치가 두 곳 이상이면 첫 번째에만

## 결정 이력

본문에 쓰지 않는다. `updateConfluencePage`의 `versionMessage`에 한 줄로 남긴다 (예: "배너 위치를 제안 상세 표 아래로 변경")

## 표 규칙

- 번호 열은 `data-colwidth="40"`, 나머지 열은 남은 폭을 나눔. 변환기가 처리
- 셀 안 줄바꿈은 `<br>`. 마크다운 원문에서 `<br>`로 적어야 변환됨
- 표를 패널 안에 넣지 않음 (Confluence가 거부)
