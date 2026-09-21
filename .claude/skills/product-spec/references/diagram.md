# 다이어그램

스펙에는 Mermaid 코드가 아니라 그림이 들어간다. 코드는 `docs/diagrams/{이름}.mmd`에 보관하고 수정 시 재렌더한다

## 언제 어떤 그림을 그리나

| 상황 | 종류 | 위치 |
|---|---|---|
| 유저 흐름에 분기가 2개 이상 | `flowchart LR` (가로형) | 구현 범위 요약 |
| 신청, 승인, 만료처럼 상태가 바뀌는 기능 | `stateDiagram-v2` | 구현 상세의 해당 행 아래 |
| 클라이언트, 서버, 외부 API 호출 순서가 구현에 중요 | `sequenceDiagram` | 구현 상세의 해당 행 아래 |
| 분기가 없는 직선 흐름 | 그리지 않음. 진입점 열로 충분 | |

- 노드 텍스트는 12자 이내. 넘으면 용어 표의 짧은 이름으로 바꿈
- 확정되지 않은 단계는 노드 텍스트 끝에 `⚠️`
- 노드와 화살표 텍스트는 큰따옴표로 감쌈 (`A["제안 상세 모달"]`). 한글 노드에서 렌더 오류를 막음
- 방향은 LR(가로) 기본. 작업자가 한눈에 훑는 순서와 같기 때문. 한 줄에 노드 6개까지, 넘으면 subgraph로 묶어 두 줄로. 첨부 경로의 figure 폭은 100%. 블록 경로(폭 300px)에서는 가로형이 읽히지 않으므로 변환기가 블록 대신 안내 상자를 넣는다

## 렌더

파일 이름 규칙 (세 파일이 한 세트)
- 코드 `{스펙 폴더}/diagrams/{이름}.mmd`
- 첨부용 그림 `{스펙 폴더}/diagrams/{이름}.png` (폭 1200, 2배)
- 블록용 그림 `{스펙 폴더}/diagrams/{이름}-macro.png` (폭 300, 1배)

```
bash {SKILL_DIR}/scripts/render_diagram.sh diagrams/flow.mmd diagrams/flow.png attach
bash {SKILL_DIR}/scripts/render_diagram.sh diagrams/flow.mmd diagrams/flow-macro.png macro
```

초안 단계에서 두 파일을 모두 만든다. 블록용이 없으면 변환기가 렌더를 다시 시도하지만 시간이 걸린다

- npx로 `@mermaid-js/mermaid-cli@11`을 받아 실행. 첫 실행은 1분 정도 걸림. Node.js 필요
- 실패하면 스크립트가 종료 코드 1과 원인(로그 마지막 15줄)을 냄. 이때는 스펙의 그림 자리에 `⚠️ 다이어그램 렌더 실패 → 코드 확인 필요`를 쓰고 `.mmd` 경로를 적음. 코드 블록을 본문에 넣지 않음
- 로컬 스펙에는 `![사용자 흐름](diagrams/{이름}.png)`로 넣음

## Confluence에 넣는 두 경로

먼저 환경변수 `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`이 있는지 본다. 있으면 경로 1, 없으면 안내 한 번 출력 후 경로 2

### 경로 1. 첨부 이미지 (기본)

⚠️ 2026-09-17 기준 이 경로는 토큰이 있는 사람이 실제로 한 번 실행해 검증해야 한다. 응답에서 미디어 ID를 읽는 항목(`extensions.fileId`)은 추정값이며, 실측 결과를 이 절에 기록할 것

1. 페이지가 없으면 먼저 그림 자리를 비운 채 페이지를 만들어 pageId를 받고 메타에 기록
2. 그림마다 `bash {SKILL_DIR}/scripts/confluence_attach.sh <pageId> diagrams/{이름}.png` → `{"mediaId", "collection", "filename", "attachmentId"}`. 파일명은 basename 그대로 올라감
3. 결과를 `media.json`에 모음. 형식: `{"{이름}.png": {"mediaId": "...", "collection": "contentId-<pageId>"}}`
4. `python3 {SKILL_DIR}/scripts/md_to_confluence.py spec.md --diagram-mode attach --media-json media.json --out body.html`. 변환기가 그림 자리에 `<figure data-type="media-single" ...>`를 넣음
5. `updateConfluencePage`로 본문 갱신 (재읽기와 버전 검증은 confluence.md)
6. mediaId가 비어 있으면 변환기가 그 그림만 블록으로 대체하고 표준 오류에 알림. 안내: "첨부는 올라갔지만 본문 삽입에 필요한 미디어 ID를 받지 못해 블록으로 넣었습니다. 페이지 편집에서 첨부 파일을 끌어다 놓으면 크게 볼 수 있습니다"

같은 이름의 파일이 이미 있으면 스크립트가 새 버전으로 올림

### 경로 2. 다이어그램 블록 (토큰 없을 때)

Mermaid Chart 앱 매크로. 코드와 PNG를 함께 넣어야 보기 화면에 그림이 뜬다 (코드만 넣으면 빈칸)

변환기가 `--diagram-mode macro`일 때 `{이름}.mmd`와 `{이름}-macro.png`로 블록을 만들어 그림 자리에 넣는다. 단 변환기는 PNG의 base64가 8KB를 넘거나 논리 폭(픽셀 폭 ÷ 2)이 600px을 넘으면 블록 대신 안내 상자(편집 → /mermaid → 코드 붙여넣기)를 넣고 표준 오류에 알린다. 가로형 흐름도는 대부분 이 조건에 걸리므로 블록 경로의 기본 결과는 안내 상자다

- 본문 크기 규칙: 변환기가 표준 오류로 알려 주는 본문 크기가 40KB를 넘으면, 첫 번째 그림만 블록으로 넣고 나머지 그림 자리에는 `⚠️ 그림은 {스펙 폴더}/diagrams/{이름}.png를 페이지에 끌어다 놓아 주세요`를 쓴다. 본문을 MCP 도구 인자로 옮길 때 잘림을 막기 위한 규칙
- 2026-09-18 실측: MCP 도구 인자에 base64를 넣으면 약 12KB 지점에서 잘려 HTML이 깨졌다(본문 크기와 무관). 블록 경로는 PNG base64가 8KB 이하일 때만 시도하고, 넘으면 그림 자리에 `<div data-type="panel-info">` 안내(편집 → /mermaid → 코드 붙여넣기, 코드 경로 명시)를 넣고 게시 안내에 그 사실을 적는다. 편집기 자동 조작으로 블록을 넣는 방법은 문서를 망칠 위험이 있어 쓰지 않는다
- PNG 크기를 줄이는 법: 렌더 뒤 4비트 양자화(채널당 16단계)로 다시 저장하면 26KB가 10KB로 줄었다. 그래도 8KB를 넘으면 위 안내 경로
- 본문은 `--out body.html`로 파일에도 저장하고, `updateConfluencePage`에 넣기 전에 파일 크기와 인자 길이가 같은지 확인한다
- `size` 값은 표시 크기에 영향이 없음 (2026-09-17 실측). 편집 화면에서 더블클릭하면 앱 에디터에서 코드 수정 가능
- 게시 안내에 한 줄 추가: "다이어그램은 블록으로 들어가 작게 보입니다. 본인 API 토큰을 등록하면 다음부터 첨부 이미지로 크게 들어갑니다"

## 수정 모드

흐름이나 상태가 바뀌는 수정이면 `.mmd`를 고치고 두 그림을 재렌더한 뒤, 경로 1이면 같은 파일명으로 다시 첨부(새 버전), 경로 2면 변환기를 다시 돌려 전체 본문을 교체
