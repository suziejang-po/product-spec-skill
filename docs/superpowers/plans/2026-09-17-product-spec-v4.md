# product-spec v4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** product-spec 스킬을 출처 기반 골격 초안, 리뷰 질문, 개조식 5열 구현 상세, 그림 다이어그램 자동 삽입 구조(v4)로 재작성한다.

**Architecture:** SKILL.md는 실행 흐름과 규칙만 담고, 템플릿, 체크리스트, 질문 매핑, 다이어그램, Confluence, 문체 규칙은 references/ 파일로 분리한다. 렌더와 업로드, 매크로 생성, 금지어 검사는 scripts/의 표준 라이브러리 파이썬과 셸 스크립트가 맡는다. 버전 체크는 프론트매터의 파일 목록을 읽어 여러 파일을 갱신한다.

**Tech Stack:** Markdown, Python 3 표준 라이브러리, bash, npx @mermaid-js/mermaid-cli, Confluence REST API v1(첨부), Atlassian MCP(페이지, 인라인 댓글)

**Spec:** `docs/superpowers/specs/2026-09-17-product-spec-v4-design.md`

## Global Constraints

- 금지 기호: 가운데점 `·`, 줄표 `—` `–`, 원형 숫자 `①②③`. 산출물, 안내 문구, 스크립트 출력 문자열 전부
- 금지어: 미결, 누락, 누수, 선제, 고지, 제고, 도모, 요건, 상기 (치환표는 writing-style.md)
- 이모지는 ⚠️와 📘만
- 개조식 명사 종결. 본문에 `~습니다`체 없음. 개조식 줄 끝 마침표 없음
- 출처 없는 도메인 서술 금지. 코드 식별자는 출처 복사만
- 토큰은 실행자 환경변수 `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `ATLASSIAN_SITE`만. 파일에 쓰지 않음
- 스킬 프론트매터: `name: product-spec`, `skill-version: "4.0.0"`, `skill-repo: suziejang-po/product-spec-skill`, `skill-files:` 목록
- 회사 데이터가 든 샘플은 `docs/samples/`(gitignore)에만 둠

---

### Task 1: 문체 규칙 파일과 금지어 검사 스크립트

**Files:**
- Create: `.claude/skills/product-spec/references/writing-style.md`
- Create: `.claude/skills/product-spec/scripts/lint_spec.py`
- Test: `docs/samples/2026-09-17-sample-preferred-location.md`(통과), 임시 파일(실패)

**Interfaces:**
- Produces: `python3 scripts/lint_spec.py <file.md>` → 위반이 있으면 종료 코드 1과 `줄번호: 종류: 내용` 출력, 없으면 0과 `OK`

- [ ] **Step 1: writing-style.md 작성.** `~/writing-rules/02-forbidden-words-symbols.md`의 기호 표, 금지어 치환표, 상투 어휘, 공문서체 목록, `04-document-style.md`의 종결 규칙, 문장 구성, 근거 붙이는 법, `05-spec-document.md`의 3절 작성 규칙과 4절(How 확정 금지)을 옮긴다. 수지님 개인 경로와 사고 이력은 빼고 규칙만 남긴다
- [ ] **Step 2: lint_spec.py 작성.** 아래 검사를 한다. 코드 블록(```)과 URL은 제외
  - 기호: `·`, `—`, `–`, `①`~`⑳`
  - 금지어: 미결, 누락, 누수, 선제, 고지, 제고, 도모, 요건, 상기, 하였습니다, 되었습니다, 따라서, 그러므로, 아울러
  - 어미: 줄 끝 `습니다.` 또는 `습니다`
  - 라벨: `맥락:`
  - 이모지: ⚠️ 📘 외의 이모지 (U+1F300~U+1FAFF, U+2600~U+27BF 중 ⚠(U+26A0) 제외)
- [ ] **Step 3: 실패 케이스 확인.** `printf '미결 사항 — 확인·검토\n' > /tmp/bad.md && python3 scripts/lint_spec.py /tmp/bad.md` 실행. 기대: 종료 코드 1, 4건 출력
- [ ] **Step 4: 통과 케이스 확인.** 샘플 파일로 실행. 기대: `OK`. 위반이 나오면 샘플을 고친다
- [ ] **Step 5: Commit.** `git add .claude/skills/product-spec/references/writing-style.md .claude/skills/product-spec/scripts/lint_spec.py && git commit -m "feat: 문체 규칙 파일과 금지어 검사 스크립트"`

### Task 2: 템플릿 v4

**Files:**
- Create: `.claude/skills/product-spec/references/template.md`
- Test: `python3 scripts/lint_spec.py references/template.md` → OK

**Interfaces:**
- Produces: 섹션 제목 문자열(SKILL.md와 question-map.md가 그대로 참조): `## 용어`, `## 메타`, `## 문제`, `## 사용자 니즈`, `## 가설과 KR`, `## 솔루션`, `## 구현 범위 요약`, `## 구현 상세`, `## 제약과 참고`

- [ ] **Step 1: 골격 작성.** 설계 문서 「템플릿 v4 골격」의 9개 섹션. 각 표의 열 이름을 확정한다
  - 용어: 용어, 뜻, 코드 식별자 (출처)
  - 메타: 항목, 내용 (DRI, 구현 담당, Jira, 일정, Confluence Page ID, 실험 Flag는 해당 시)
  - 가설과 KR: 구분, 지표, 현재, 목표, 측정, 근거
  - 구현 범위 요약: 한 줄 불릿, 비주얼 표(항목, 링크), 변경 페이지 표(페이지, 변경), 메뉴 구조 표(depth1, depth2, 노출 조건, 주요 기능), 흐름도 이미지
  - 구현 상세: `#`, 진입점, 화면, 기능, 요구사항
- [ ] **Step 2: 작성 지침을 HTML 주석으로.** 각 섹션 아래 `<!-- 지침: ... -->`로 채우는 법, 문서 유형별 축약, ⚠️ 표기법, 빈칸에 `[Q번호]` 붙이는 법을 적는다. 스킬은 출력 시 주석을 제거한다
- [ ] **Step 3: 가상 예시 1개.** 회사 데이터가 아닌 가상 서비스(예: 도서 대여 앱의 반납 알림)로 모든 섹션을 채운 예시를 `references/template-example.md`에 둔다. 밀도는 docs/samples의 기준 샘플과 같게
- [ ] **Step 4: lint 실행.** 두 파일 모두 OK
- [ ] **Step 5: Commit.** `git add .claude/skills/product-spec/references/template*.md && git commit -m "feat: 템플릿 v4와 가상 예시"`

### Task 3: 리뷰 체크리스트와 질문 매핑

**Files:**
- Create: `.claude/skills/product-spec/references/review-checklist.md` (req-review checklist.md 복제)
- Create: `.claude/skills/product-spec/references/question-map.md`
- Test: lint OK, 매핑표의 섹션명이 template.md 섹션명과 일치하는지 grep

**Interfaces:**
- Consumes: Task 2의 섹션 제목과 표 열 이름
- Produces: question-map.md 표 열: 대항목, 소항목, 판정 조건(정의됨으로 보는 기준), 질문 문안, 선택지(있으면), 답이 들어갈 섹션과 열, 적용 유형(New/Feature/Enhancement)

- [ ] **Step 1: review-checklist.md.** `/private/tmp/.../req-review/references/checklist.md` 6개 대항목 27개 소항목을 그대로 옮기고, 소항목마다 "이 스펙에서 정의됨으로 보는 기준" 한 줄을 붙인다
- [ ] **Step 2: question-map.md.** 27개 소항목 전부에 행을 만든다. 예시 행:
  - 사용자 및 권한 / 권한별 접근 범위 / 메뉴 구조 표 노출 조건 열이 모든 행에 채워짐 / "이 화면은 누구에게 보이나요?" / 전체, 로그인 유저, 기업 회원, 기타 / 구현 범위 요약 > 메뉴 구조 표 > 노출 조건 / Feature, New
  - 기능 상세 명세 / 예외·실패·오류 처리 / 요구사항 셀에 실패 시 동작이 있음 / "{기능}이 실패하면(네트워크, 권한, 빈 데이터) 어떻게 보이나요?" / 없음 / 구현 상세 > 요구사항 / 전체
- [ ] **Step 3: 질문 묶음 규칙.** 파일 끝에 "한 번에 5개 안팎, 대항목 순서, 선택지 있는 것 먼저, 최대 2회, 2회 후 ⚠️ 처리" 규칙과 질문 출력 형식 예시를 적는다
- [ ] **Step 4: 검증.** `grep -o '구현 범위 요약\|구현 상세\|가설과 KR\|용어\|메타\|문제\|사용자 니즈\|솔루션\|제약과 참고' references/question-map.md | sort -u`가 template.md 섹션 집합의 부분집합인지 확인. lint OK
- [ ] **Step 5: Commit.** `git commit -m "feat: 리뷰 체크리스트와 질문 매핑표"`

### Task 4: 도메인 팩 양식

**Files:**
- Create: `.claude/skills/product-spec/references/context-pack.md`
- Test: lint OK

**Interfaces:**
- Produces: `docs/spec-context.md` 양식(섹션: 서비스와 화면, 메뉴 구조, 관련 문서, 용어와 코드 식별자, API, 이벤트)과 수집 질문 5개, 자동 조회 절차(Confluence CQL 검색, asp MCP, Amplitude 택소노미 검색)

- [ ] **Step 1: 양식 작성.** 각 섹션의 표 열을 정한다. 용어 표는 template.md의 용어 표와 열이 같아야 한다(용어, 뜻, 코드 식별자 (출처))
- [ ] **Step 2: 자동 조회 절차.** MCP 도구 이름을 적는다: `searchConfluenceUsingCql`(제목과 본문 키워드, 최근 1년), asp MCP(있으면 API 검색), Amplitude `search_amp_data_taxonomy`(이벤트명 존재 확인). 도구가 없으면 건너뛰고 작성자에게 묻는다
- [ ] **Step 3: 수집 질문 5개**를 선택지형 포함으로 적는다. 답을 받으면 양식에 채워 저장하고, 다음 실행부터 재사용
- [ ] **Step 4: lint 후 Commit.** `git commit -m "feat: 도메인 팩 양식과 수집 절차"`

### Task 5: 다이어그램 파이프라인

**Files:**
- Create: `.claude/skills/product-spec/references/diagram.md`
- Create: `.claude/skills/product-spec/scripts/render_diagram.sh`
- Create: `.claude/skills/product-spec/scripts/mermaid_macro.py`
- Create: `.claude/skills/product-spec/scripts/confluence_attach.sh`
- Test: 샘플 .mmd로 렌더, 매크로 HTML 생성, (토큰 있을 때만) 첨부 업로드

**Interfaces:**
- Produces:
  - `render_diagram.sh <in.mmd> <out.png> [attach|macro]` → attach는 `-w 1200 -s 2`, macro는 `-w 300 -s 2`. 실패 시 종료 코드 1
  - `python3 mermaid_macro.py <in.mmd> <in.png>` → 표준 출력에 Confluence HTML `<div data-type="extension" data-extension-key="mermaid" ...>` 한 줄
  - `confluence_attach.sh <pageId> <file.png>` → 표준 출력에 JSON `{"mediaId": "...", "collection": "contentId-<pageId>", "filename": "..."}`. 환경변수 없으면 종료 코드 2와 안내 문구

- [ ] **Step 1: render_diagram.sh.** `npx -y @mermaid-js/mermaid-cli -i "$1" -o "$2" -b white $OPTS`. 모드별 OPTS. npx 미설치면 안내 후 종료 코드 1
- [ ] **Step 2: mermaid_macro.py.** 설계 문서 「삽입 경로 2」의 macroParams(size medium, isEditable true, diagramCode, caption 빈 값, theme default, lastEdited 현재 UTC ISO, diagramType mermaid, `__bodyContent` PNG base64)와 macroMetadata(schemaVersion 1, placeholder 아이콘 `https://confluence.mermaidchart.com/icon_80x80.png`, title `Mermaid chart`)를 JSON으로 만들고 `html.escape(json.dumps(..., ensure_ascii=False), quote=True)`로 data-parameters에 넣는다
- [ ] **Step 3: confluence_attach.sh.** `curl -sS -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" -H "X-Atlassian-Token: nocheck" -F "file=@$2" "https://${ATLASSIAN_SITE:-wantedlab.atlassian.net}/wiki/rest/api/content/$1/child/attachment?allowDuplicated=false"`. 같은 파일명이 있으면(HTTP 400) `GET .../child/attachment?filename=` 으로 id를 찾아 `POST .../child/attachment/{id}/data`로 새 버전 업로드. 응답 JSON에서 `results[0].extensions.fileId`를 mediaId로 출력 (⚠️ 실측으로 필드명 확정. 없으면 `results[0].id`와 다운로드 링크를 함께 출력하고 diagram.md에 확인 결과를 적음)
- [ ] **Step 4: 렌더 테스트.** `bash scripts/render_diagram.sh docs/samples/diagrams/preferred-location-flow.mmd /tmp/t.png macro && python3 -c "import struct;b=open('/tmp/t.png','rb').read();print(struct.unpack('>II',b[16:24]))"` → 폭이 600 근처(300 x 2)
- [ ] **Step 5: 매크로 테스트.** `python3 scripts/mermaid_macro.py docs/samples/diagrams/preferred-location-flow.mmd /tmp/t.png | head -c 300` → `data-extension-key="mermaid"` 포함, 파이썬 `html.unescape` 후 `json.loads` 성공
- [ ] **Step 6: 첨부 테스트.** 토큰이 없으면 종료 코드 2와 안내 문구 확인만. 있으면 개인 스페이스 테스트 페이지 4973199490에 업로드하고 mediaId를 받아 `updateConfluencePage`로 figure를 넣어 그림 표시 확인
- [ ] **Step 7: diagram.md.** 판정 규칙(flowchart TD, stateDiagram-v2, sequenceDiagram), 노드 텍스트 12자, 파일 위치 `docs/diagrams/`, 세 스크립트 사용법, 경로 1과 2 선택 규칙, 매크로 표시 폭 300px 사실, 실패 시 ⚠️ 처리
- [ ] **Step 8: Commit.** `git commit -m "feat: 다이어그램 렌더, 매크로, 첨부 스크립트와 절차"`

### Task 6: Confluence 절차

**Files:**
- Create: `.claude/skills/product-spec/references/confluence.md`
- Create: `.claude/skills/product-spec/scripts/md_to_confluence.py`
- Test: 샘플 md → HTML 변환 결과에 표 colwidth, 인라인 코드, 이미지 자리표시가 있는지 확인

**Interfaces:**
- Produces: `python3 md_to_confluence.py <spec.md> --diagram-mode attach|macro --media-json <json>` → 표준 출력에 Confluence HTML 본문. 이미지는 media-json의 매핑(파일명 → mediaId, collection)으로 figure를 만들고, macro 모드면 mermaid_macro.py 출력을 삽입
- Produces: confluence.md 절차(첫 게시, 갱신, 충돌 검사, 이동, 인라인 댓글, 치환 필터)

- [ ] **Step 1: md_to_confluence.py.** 표준 라이브러리만. 지원 요소: 제목(h1~h3), 문단, 불릿, 번호 목록, 표(첫 열이 `#`이면 `data-display-mode="fixed"`와 첫 열 `data-colwidth="40"`), 인라인 코드, 굵게, 링크, 이미지(`![alt](diagrams/x.png)`). 셀 안 `<br>` 유지. 변환 직전 치환 필터(`·`→`/`, `—`→`,`, `①`→`1.` 등)
- [ ] **Step 2: 변환 테스트.** 샘플로 실행해 `data-colwidth="40"`, `<figure data-type="media-single"` 또는 `data-extension-key="mermaid"` 포함 확인. 출력에 금지 기호 없음
- [ ] **Step 3: confluence.md.** 기존 SKILL.md의 Phase 3(케이스 A, B, C), 안전 절차(재읽기, 버전 검증), 부모 페이지 ID(작성중 4808376595, 출시 확정 4808212726), 제목 규칙을 옮기고, 수치 인라인 댓글 절차(`createConfluenceInlineComment`, 대상 텍스트는 수치 문자열, 본문은 근거 링크나 쿼리)를 추가
- [ ] **Step 4: Commit.** `git commit -m "feat: Confluence 변환 스크립트와 게시 절차"`

### Task 7: SKILL.md 재작성

**Files:**
- Modify: `.claude/skills/product-spec/SKILL.md` (전면 교체)
- Test: lint OK, 300줄 이내, 프론트매터 파싱

**Interfaces:**
- Consumes: Task 1~6의 파일명과 스크립트 인터페이스
- Produces: 프론트매터 `skill-files` 목록(references 8개, scripts 5개)

- [ ] **Step 1: 프론트매터.** name, skill-version 4.0.0, skill-repo suziejang-po/product-spec-skill, skill-files 목록, description(기존 트리거 문구 유지)
- [ ] **Step 2: 버전 체크와 갱신.** raw URL 기준 경로를 `.claude/skills/product-spec/`로 두고, `skill-files` 목록을 순회해 각 파일을 같은 상대 경로에 내려받는다. 쓰기 불가 환경 안내는 유지
- [ ] **Step 3: 실행 흐름.** 설계 문서 Phase 0~5와 수정 모드를 그대로 옮긴다. 각 Phase에서 읽을 references 파일과 실행할 스크립트를 명시. 질문 출력 형식, 출처 요약 형식, 아티팩트 질문 문안을 적는다
- [ ] **Step 4: 절대 규칙과 자가 검증.** 출처 없는 서술 금지, 식별자 복사만, 수치 근거, 분량 상한(페이지당 표 1개, 셀 3줄), 금지 패턴, lint 실행, 다이어그램 그림 확인, 토큰 취급
- [ ] **Step 5: 응답 말투.** writing-style.md 요약 5줄
- [ ] **Step 6: 검증.** `python3 scripts/lint_spec.py SKILL.md`, `wc -l SKILL.md` ≤ 300, `head -12 SKILL.md`로 프론트매터 확인
- [ ] **Step 7: Commit.** `git commit -m "feat: SKILL.md v4.0.0"`

### Task 8: README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 내용 교체.** 설치(포크 URL), 사용법, 실행 흐름 요약(초안 → 질문 → 본문 → 게시), 다이어그램 삽입 두 경로와 토큰 등록법(본인 토큰만, 환경변수 3개), 파일 구조, 업데이트 안내
- [ ] **Step 2: lint 후 Commit.** `git commit -m "docs: README v4"`

### Task 9: 끝까지 실행 검증

**Files:**
- Create: `docs/samples/e2e/` (gitignore 범위)

- [ ] **Step 1: 실행.** 새 세션에서 `/product-spec`을 안 좋은 예 페이지 내용을 입력 자료로 주고 실행. 도메인 팩 질문 → 골격 초안 → 질문 2회 → 본문 → 아티팩트 질문(안 함) → 저장까지
- [ ] **Step 2: 확인.** 출력 문서에 출처 없는 서술이 없는지 원본과 대조. lint OK. 구현 상세가 5열인지. 그림 파일 생성
- [ ] **Step 3: 게시.** 수지님 개인 스페이스에 게시(테스트 페이지 4973199490 갱신). 다이어그램은 토큰이 없으니 매크로 경로. 그림 표시와 번호 열 폭 확인
- [ ] **Step 4: 결과 기록.** `docs/superpowers/plans/2026-09-17-product-spec-v4.md` 끝에 실행 결과와 고친 점을 적고 Commit

### Task 10: 적대적 리뷰

- [ ] **Step 1: 리뷰어 지시.** 스킬 파일 전체와 설계 문서를 주고, 작성자 입장(도메인 지식 없는 PO), 작업자 입장(개발, 디자인), 운영 입장(전사 배포, 토큰, 갱신)에서 깨지는 지점을 찾게 한다. 결론이 아니라 파일을 준다
- [ ] **Step 2: 반영.** 지적 중 사실인 것을 고치고, 판단이 필요한 것은 수지님에게 목록으로 보고


---

## 실행 기록 (2026-09-17)

Task 1~8 완료 후 Task 9(검증 실행 에이전트)와 Task 10(적대적 리뷰 에이전트)을 동시에 실행

Task 9 결과
- 안 좋은 예 페이지(4914709425)만 자료로 주고 Phase 0~4 실행. lint 통과, 5열 표 6행, 흐름도 렌더 1.5초, ⚠️ 28건
- 도구: getConfluencePage와 CQL 검색 동작, Amplitude 택소노미로 이벤트 8종 확인(기존 5, 신규 3, 미확인 1), asp MCP 없음
- 지침 결함 18건 보고. 주요: 셀 3줄 규칙과 예시 불일치, 도메인 팩 서비스명 정의 없음, 식별자 미확인 처리 규칙 없음, 메타 질문 없음, 실험 설계 자리 없음, 출처 요약의 최종 위치 없음, 비대화 환경의 채팅 출력 대체 없음
- 출처 규칙이 막은 추론 6건 기록(유저 니즈 유추, fail-safe 기본값, 닫기 버튼 확정, 플랫폼, DRI, URL)

Task 10 결과
- 판정 배포 불가. 높음 10건(버전 갱신이 v3.2로 되돌림, 스크립트 경로, 블록 경로 파일명 불일치, base64 본문 크기, lint 순서와 오탐, 질문 예산, 빈 도메인 팩 고착, 스펙 파일명 고정, 분량 규칙 모순, 첨부 경로 미검증), 중간 14건, 낮음 6건

반영
- 스크립트: lint 단어 경계와 따옴표 예외와 lint-skip, 이모지 범위 확대. 변환기 셀 안 `|`와 코드 펜스와 괄호 URL, 블록용 그림 자동 렌더, argparse와 --out. 렌더 버전 고정과 오류 로그. 첨부 토큰을 표준 입력 설정으로 전달, python3 확인
- SKILL.md: SKILL_DIR 확인 절차, 버전 크기 비교와 skill-files 확인과 백업, 산출물 위치 `docs/specs/{슬러그}/`, 출처 등급(확인, 구술)과 sources.md, 식별자 표기 4종, 근거 인정 규칙, 분량 규칙 재정의, 실험 유형, 저장 뒤 lint, 비대화 환경 대체, 트리거 축소
- references: 템플릿에 플랫폼 행과 실험 설계 표와 이벤트 표와 API 표, 행 정렬 규칙. 질문 매핑에 우선순위와 메타 행과 모름 선택지와 유도 질문 금지와 3회차 제안. 도메인 팩에 서비스명과 빈 팩과 만료와 pageId 추출과 Confluence 설정. 다이어그램 파일명 통일과 크기 규칙과 media.json 형식. Confluence 정본 선언과 전체 덮어쓰기와 설정과 복구와 인라인 댓글 절차. 문체 규칙의 문서 구성 충돌 줄 제거

남은 것
- 첨부 경로(경로 1)는 토큰 보유자가 실행해 미디어 ID 필드를 확정해야 함
- 블록 경로의 base64 본문을 MCP 인자로 옮기는 부담은 40KB 규칙으로 줄였을 뿐 없애지 못함
