# 다이어그램

스펙에는 Mermaid 코드가 아니라 그림이 들어간다. 코드는 `docs/diagrams/{이름}.mmd`에 보관하고 수정 시 재렌더한다

## 언제 어떤 그림을 그리나

| 상황 | 종류 | 위치 |
|---|---|---|
| 유저 흐름에 분기가 2개 이상 | `flowchart TD` | 구현 범위 요약 |
| 신청, 승인, 만료처럼 상태가 바뀌는 기능 | `stateDiagram-v2` | 구현 상세의 해당 행 아래 |
| 클라이언트, 서버, 외부 API 호출 순서가 구현에 중요 | `sequenceDiagram` | 구현 상세의 해당 행 아래 |
| 분기가 없는 직선 흐름 | 그리지 않음. 진입점 열로 충분 | |

- 노드 텍스트는 12자 이내. 넘으면 용어 표의 짧은 이름으로 바꿈
- 확정되지 않은 단계는 노드 텍스트 끝에 `⚠️`
- 노드와 화살표 텍스트는 큰따옴표로 감쌈 (`A["제안 상세 모달"]`). 한글 노드에서 렌더 오류를 막음
- 방향은 TD 기본. 블록 경로는 폭이 300px이라 LR은 읽히지 않음

## 렌더

```
bash scripts/render_diagram.sh docs/diagrams/flow.mmd docs/diagrams/flow.png attach   # 첨부용, 폭 1200 x 2배
bash scripts/render_diagram.sh docs/diagrams/flow.mmd docs/diagrams/flow.png macro    # 블록용, 폭 300 x 2배
```

- npx로 `@mermaid-js/mermaid-cli`를 받아 실행. 첫 실행은 1분 정도 걸림. Node.js 필요
- 실패하면 스크립트가 종료 코드 1과 안내를 냄. 이때는 스펙의 그림 자리에 `⚠️ 다이어그램 렌더 실패 → 코드 확인 필요`를 쓰고 `.mmd` 경로를 적음. 코드 블록을 본문에 넣지 않음
- 로컬 `docs/PRODUCT_SPEC.md`에는 `![사용자 흐름](diagrams/flow.png)`로 넣음. attach 모드로 렌더한 파일을 씀

## Confluence에 넣는 두 경로

먼저 환경변수 `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`이 있는지 본다. 있으면 경로 1, 없으면 안내 한 번 출력 후 경로 2

### 경로 1. 첨부 이미지 (기본)

1. 페이지가 없으면 먼저 그림 자리를 비운 채 페이지를 만들어 pageId를 받음
2. `bash scripts/confluence_attach.sh <pageId> docs/diagrams/flow.png` → `{"mediaId", "collection", "filename", "attachmentId"}`
3. 본문의 그림 자리에 `<figure data-type="media-single" data-layout="center" data-width="80" data-width-type="percentage"><div data-type="media" data-media-type="file" data-id="{mediaId}" data-collection="{collection}" data-alt="{filename}"></div></figure>`
4. `updateConfluencePage`로 본문 갱신 (재읽기와 버전 검증은 confluence.md)
5. mediaId가 비어 있으면(응답에 fileId가 없는 경우) 경로 2로 대신 넣고 안내: "첨부는 올라갔지만 본문 삽입에 필요한 미디어 ID를 받지 못해 블록으로 넣었습니다. 페이지 편집에서 첨부 파일을 끌어다 놓으면 크게 볼 수 있습니다"

같은 이름의 파일이 이미 있으면 스크립트가 새 버전으로 올림. 첨부 파일명은 `{스펙 제목 슬러그}-{이름}.png`

### 경로 2. 다이어그램 블록 (토큰 없을 때)

Mermaid Chart 앱 매크로. 코드와 PNG를 함께 넣어야 보기 화면에 그림이 뜬다 (코드만 넣으면 빈칸)

```
python3 scripts/mermaid_macro.py docs/diagrams/flow.mmd docs/diagrams/flow-macro.png
```

- 출력된 `<div data-type="extension" data-extension-key="mermaid" ...>` 한 줄을 본문의 그림 자리에 넣음
- macro 모드로 렌더한 PNG(폭 약 600px)를 씀. 블록이 폭 300px로 줄여 보여주므로 2배 해상도가 선명함
- `size` 값은 표시 크기에 영향이 없음 (2026-09-17 실측). 편집 화면에서 더블클릭하면 앱 에디터에서 코드 수정 가능
- 게시 안내에 한 줄 추가: "다이어그램은 블록으로 들어가 작게 보입니다. 본인 API 토큰을 등록하면 다음부터 첨부 이미지로 크게 들어갑니다"

## 수정 모드

흐름이나 상태가 바뀌는 수정이면 `.mmd`를 고치고 같은 모드로 재렌더한 뒤, 경로 1이면 같은 파일명으로 다시 첨부(새 버전), 경로 2면 블록을 새 출력으로 교체
