# 다이어그램

스펙에는 코드가 아니라 그림이 들어간다. 기본은 담당자별 띠 그림(SVG를 손으로 배치해 PNG로 렌더). 그림 소스는 `{스펙 폴더}/diagrams/`에 보관하고 수정 시 재렌더한다

## 언제 어떤 그림을 그리나

| 상황 | 종류 | 위치 |
|---|---|---|
| 유저 흐름에 분기가 2개 이상 | 담당자 띠 흐름도 (기본) | 4. 플로우의 하위 섹션 |
| 운영자가 만든 일정에 따라 단계가 바뀌는 흐름 | 담당자 띠 + 단계 열 | 4. 플로우의 하위 섹션 |
| 화면이 여러 묶음으로 나뉘는 New Product (공간, 화면이 어떻게 묶이는지) | 묶음 상자 그림 | 3. 서비스 구조 설명 불릿 아래 |
| 신청, 승인, 만료처럼 상태가 바뀌는 기능 | 상태 그림 (상태 상자 + 화살표에 누가 무엇을 하면) | 3-1 상태 흐름, 또는 5. 구현 상세의 해당 행 아래 |
| 클라이언트, 서버, 외부 API 호출 순서가 구현에 중요 | Mermaid `sequenceDiagram` | 구현 상세의 해당 행 아래 |
| 분기가 없는 직선 흐름 | 그리지 않음. 진입점 열로 충분 | |

## 담당자 띠 그림 규칙

- 가로 띠 하나가 담당자 하나: 유저, 시스템, 운영자 (필요한 것만. 팀장, 팀원처럼 나눠도 됨)
- 왼쪽에서 오른쪽으로 시간 순서. 일정 단계가 있으면 위에 단계 열 머리(접수, 제출, 공개 등)와 점선 구분선
- 상자 색은 담당자와 결과로 구분: 유저 `user`(파랑), 시스템 `sys`(회색), 운영자 `ops`(노랑), 완료 `ok`(초록), 막힘 `bad`(빨강)
- 판단은 마름모, 갈림 화살표에 '예', '아니오' 또는 조건 이름
- 상자 글자는 2줄 이내, 한 줄 12자 안팎. 길면 용어 표의 짧은 이름으로
- 확정되지 않은 단계는 상자 글자 끝에 `⚠️`
- 그림 제목은 기능 이름 그대로 ("팀 초대 플로우"). 수사형 제목 금지
- 화살표가 상자를 가로지르지 않게 꺾은선으로 돌림. 화살표 글자는 선 바로 위

## 만드는 법

1. `{SKILL_DIR}/references/swimlane-example.py`를 읽는다. 허브 스펙에서 실제로 쓴 예시 2개(담당자 띠, 담당자 띠 + 단계 열)
2. 같은 꼴로 `{스펙 폴더}/diagrams/charts.py`를 쓴다. `from svgkit import Chart`(경로는 `{SKILL_DIR}/scripts`). 좌표는 손으로 정함
   - `Chart(폭, 높이, 제목)`, `lane(y, 높이, 이름, 배경색)`, `column_header(x, y, 폭, 이름, 부제)`, `vline(x, y1, y2)`, `group(x, y, 폭, 높이, 이름, 배경색, 선색, 부제)`
   - `box(id, cx, cy, 글자, 종류, w=, h=)`, `diamond(id, cx, cy, 글자)`, `note(x, y, 글자)`
   - `arrow([점들], 글자, 글자x, 글자y, dashed=)`. 점은 `c.p(id, 'l'|'r'|'t'|'b')`로 상자 가장자리를 씀
3. 실행해 `{이름}.svg`를 만들고 렌더
   ```
   python3 {SKILL_DIR}/scripts/render_svg.py diagrams/{이름}.svg
   ```
   Python playwright가 있으면 그것으로, 없으면 Chrome headless로 2배 PNG를 만든다
4. 렌더한 PNG를 직접 열어 본다. 글자가 상자 밖으로 나가거나 화살표가 겹치면 좌표를 고쳐 다시 렌더
5. 실패하면 스펙의 그림 자리에 `⚠️ 다이어그램 렌더 실패 → 코드 확인 필요`와 `charts.py` 경로. 코드 블록을 본문에 넣지 않음
6. 로컬 스펙에는 `![팀 초대 플로우](diagrams/{이름}.png)`

Mermaid는 순서도(`sequenceDiagram`)에만 쓴다. 렌더는 `bash {SKILL_DIR}/scripts/render_diagram.sh diagrams/{이름}.mmd diagrams/{이름}.png attach`

## Confluence에 넣는 경로

그림은 페이지 첨부 파일로 올리고 본문에 미디어로 넣는다. 다이어그램 블록(Mermaid 앱 매크로)은 폭 300px로 작게 보여 쓰지 않는다

### 1. 첨부 올리기

환경에 따라 아래 중 되는 것 하나
- 토큰 있음 (`ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`): `bash {SKILL_DIR}/scripts/confluence_attach.sh <pageId> diagrams/{이름}.png`
- 토큰 없음, Claude in Chrome 있음 (2026-10-15 실측):
  1. PNG를 세션 작업 폴더에 둔다. 출력 폴더나 연결된 기기 폴더의 경로는 파일 업로드 도구가 거부함
  2. 페이지에서 JS로 숨은 `<input type=file id=cc-up>`을 붙이고, `find`로 그 요소를 찾아 파일 업로드 도구로 PNG를 넣는다
  3. 페이지에서 `PUT /wiki/rest/api/content/{pageId}/child/attachment` (헤더 `X-Atlassian-Token: no-check`, FormData에는 파일만)
  4. 같은 파일명으로 새 버전을 올리면 400이나 403(XSRF)이 난다. 고칠 때는 `{이름}_v2.png`처럼 새 파일명으로 올림
- 둘 다 없음: 그림 자리에 `⚠️ 그림은 diagrams/{이름}.png를 페이지에 끌어다 놓아 주세요` 안내 상자를 넣고 게시 안내에 적음

### 2. 미디어 ID 받기 (2026-10-12 실측)

- `GET /wiki/api/v2/pages/{pageId}/attachments`의 각 항목 `fileId`가 본문 미디어의 `data-id`
- collection은 `contentId-{pageId}`
- Chrome이면 페이지에서 `fetch('/wiki/api/v2/pages/{pageId}/attachments?limit=50')`로 받음
- 결과를 `media.json`에 모음: `{"{이름}.png": {"mediaId": "{fileId}", "collection": "contentId-{pageId}"}}`

### 3. 본문에 넣기

`python3 {SKILL_DIR}/scripts/md_to_confluence.py spec.md --media-json media.json --out body.html` → 그림 자리에 `<figure data-type="media-single" ...>`. `updateConfluencePage`(html)로 올림

- 폭은 기본 80%. 단계 열이 있는 넓은 그림은 100%
- 페이지 본문 폭 때문에 넓은 그림은 작게 보임. 게시 안내에 "넓은 그림은 클릭하면 크게 보입니다" 한 줄

## 수정 모드

흐름이나 상태가 바뀌면 `charts.py`를 고치고 재렌더한 뒤
1. 새 파일명(`{이름}_v{N}.png`)으로 첨부
2. 본문의 `ri:filename`을 새 이름으로 바꾸고, 같은 태그의 `ri:version-at-save` 속성은 지운다 (남기면 없는 버전을 가리켜 '미리 보기를 사용할 수 없음'이 뜸)
3. PUT 성공 뒤 예전 첨부를 `DELETE /wiki/api/v2/attachments/{id}`로 지움 (휴지통으로 감. 첫 시도 500이면 한 번 더)
4. 페이지를 다시 열어 그림이 실제로 보이는지 확인. 첨부 목록에 있어도 깨져 보일 수 있음
