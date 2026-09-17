---
name: product-spec
skill-version: "4.0.0"
skill-repo: suziejang-po/product-spec-skill
skill-files:
  - SKILL.md
  - references/template.md
  - references/template-example.md
  - references/review-checklist.md
  - references/question-map.md
  - references/context-pack.md
  - references/diagram.md
  - references/confluence.md
  - references/writing-style.md
  - scripts/lint_spec.py
  - scripts/render_diagram.sh
  - scripts/mermaid_macro.py
  - scripts/confluence_attach.sh
  - scripts/md_to_confluence.py
description: Wantedlab Product Spec(v4)을 생성/수정한다. 도메인 팩 수집 → 출처 있는 내용만 채운 골격 초안 → 리뷰 체크리스트로 빈칸을 질문 → 개조식 5열 구현 상세 → 다이어그램을 그림으로 삽입 → Confluence 게시. 사용자가 다음과 같이 말할 때 사용: "프로덕트 스펙 작성", "PRD 작성", "PRD 만들어줘", "Spec 작성", "스펙 작성", "스펙 문서", "스펙 만들어줘", "스펙 수정", "프로젝트 정리", "협업 문서", "작업 요구사항 정리", "디자이너에게 넘길 문서", "QA 넘기기 전에 정리", "문서로 정리해줘", "문서 정리", "문서 작성", "/product-spec".
---

# Product Spec 생성 에이전트 v4

Wantedlab의 개발 킥오프용 스펙을 만든다. 규칙은 이 파일, 양식과 절차는 `references/`, 도구는 `scripts/`. 경로는 모두 이 파일이 있는 폴더 기준

## 원칙 (이것을 어기면 문서가 아니라 부담이 된다)

1. 출처 없는 도메인 서술 금지. 출처는 네 가지뿐: 레포 코드, 첨부 자료, 대화에서 작성자가 말한 것, MCP로 읽은 기존 문서. 출처가 없으면 문장을 만들지 않고 빈칸에 `[Q번호]`
2. 코드 식별자(이벤트명, API 경로, 필드, 컴포넌트)는 출처에서 그대로 복사. 유추한 이름 금지. 확인하지 못하면 빈칸
3. 수치마다 근거(Amplitude 차트 링크, BQ 쿼리 위치). 없으면 수치 옆에 `⚠️ 쿼리 첨부 필요`. 목표값, 일정, 담당자는 작성자 입력 없이 채우지 않음
4. 분량 상한. 페이지당 표 1개, 셀당 3줄, 문단 서술 없음. 결정 이력과 검토 서사는 본문에 넣지 않음
5. 문체는 `references/writing-style.md`. 개조식 명사 종결, 금지 기호와 금지어 없음. 출력 전 `python3 scripts/lint_spec.py` 통과
6. 다이어그램은 그림. 코드 블록을 본문에 넣지 않음
7. 토큰은 실행하는 사람 본인의 환경변수만 읽음. 파일이나 문서에 적지 않음

## 버전 확인 (본문 작업 전 1회)

1. 프론트매터 `skill-version`(로컬)과 원격을 비교
   ```bash
   curl -sf "https://raw.githubusercontent.com/suziejang-po/product-spec-skill/main/.claude/skills/product-spec/SKILL.md" | head -5 | grep 'skill-version'
   ```
2. 다르면 한 줄 안내 후 그대로 진행: "product-spec 스킬 업데이트가 있습니다 (로컬 {로컬} → 최신 {원격}). '스킬 업데이트해줘'라고 하면 갱신합니다. 중앙 등록 스킬이면 관리 담당자에게 요청하세요"
3. 같거나 curl이 실패하면 아무것도 출력하지 않음

"스킬 업데이트해줘" 요청 시: 지금 로드된 SKILL.md의 실제 경로를 확인하고(하드코딩 금지), 원격 SKILL.md의 `skill-files` 목록을 읽어 각 파일을 같은 상대 경로로 내려받아 덮어씀. 쓰기 불가 환경이면 시도하지 않고 담당자 안내만. 성공하면 "스킬을 {버전}으로 갱신했습니다. 새 지침은 다음 실행부터 적용됩니다"

## 실행 흐름

호출 즉시 아래 순서. `docs/PRODUCT_SPEC.md`가 있으면 「수정 모드」

### Phase 0. 컨텍스트 수집

1. 레포 스캔: `README.md`, `CLAUDE.md`, 매니페스트, 라우트와 컴포넌트 폴더, 배포 설정, `docs/`. git log는 변경 범위 파악에만 쓰고 서사를 만들지 않음
2. 첨부 자료와 대화 내용
3. 도메인 팩: `docs/spec-context.md`가 있으면 읽음. 없으면 `references/context-pack.md`의 자동 조회(Confluence 검색, asp MCP, Amplitude 택소노미)를 하고, 못 채운 항목만 수집 질문 5개로 물어 저장. 이 단계는 질문 횟수에 세지 않음
4. 문서 유형 판별: New Product(새 서비스), Feature(기존 서비스에 새 기능), Enhancement(기존 기능 개선). 모호하면 Feature
5. 코드 식별자 확인: 초안에 쓸 이벤트명은 Amplitude 택소노미로, API는 asp로 존재 여부 확인. 있으면 (기존), 없으면 (신규 제안). 도구가 없으면 출처 문서에 적힌 것만 (문서명) 표기

### Phase 1. 골격 초안

`references/template.md`의 순서대로 채워 채팅에 전문 출력. 지침 주석은 제거. 밀도와 문체의 기준은 `references/template-example.md`

- 채우는 범위: 용어, 메타, 문제, 사용자 니즈, 가설과 KR, 솔루션, 구현 범위 요약(변경 페이지 표, 메뉴 구조 표, 흐름도), 구현 상세는 진입점/화면/기능 열만. 요구사항 열은 출처가 있는 것만
- 출처 없는 칸은 빈칸 + `[Q1]`, `[Q2]` 번호. 번호는 문서 전체에서 이어짐
- Enhancement면 문제, 사용자 니즈, 가설과 KR을 각 1~2줄로 줄이고 흐름도는 분기가 있을 때만
- 흐름도는 `references/diagram.md`대로 `docs/diagrams/{이름}.mmd`를 쓰고 attach 모드로 렌더해 `![사용자 흐름](diagrams/{이름}.png)`. 채팅에는 "그림 생성: docs/diagrams/{이름}.png" 한 줄
- 초안 끝에 출처 요약: 항목마다 "{항목}: {출처}" 한 줄 (예: "메뉴 구조: docs/spec-context.md", "KR 목표값: 없음, Q5")
- 초안에 담긴 도메인 문장은 모두 출처 요약의 어느 줄에 대응해야 함. 대응하지 않는 문장은 삭제

### Phase 2. 내부 리뷰

`references/review-checklist.md`로 초안을 판정한다. 결과 표는 출력하지 않는다
- 문서 유형이 Enhancement면 사용자 및 권한, 정책 항목은 이번 변경과 관련 있을 때만
- 두 섹션이 어긋나면 불충분으로 두고 질문에 두 곳을 함께 적음

### Phase 3. 질문

빈칸 `[Q번호]`와 리뷰의 정의 없음, 불충분 항목을 `references/question-map.md`로 질문으로 바꾼다
- 한 번에 5개 안팎, 대항목 순서, 선택지 있는 것 먼저. AskUserQuestion 도구가 있으면 선택지형으로
- 최대 2회. 답이 오면 매핑된 섹션과 열에 채우고, 초안과 어긋나면 답을 채택
- 2회 뒤에도 비어 있거나 "모름"이면 해당 셀에 `⚠️ {항목} → {결정 주체} 확인 필요`. 지어내지 않음
- 작성자가 "그냥 만들어"라고 하면 질문을 멈추고 빈칸은 전부 ⚠️ 처리

### Phase 4. 본문 완성과 저장

1. 전체 본문을 채팅에 출력
2. 자가 검증
   - 출처 요약에 대응하지 않는 도메인 문장이 없는가
   - 용어 표의 용어만 본문에 쓰였는가 (동의어 없음)
   - 코드 식별자에 (기존), (신규 제안), (문서명) 중 하나가 붙었는가
   - 구현 상세가 `#`, 진입점, 화면, 기능, 요구사항 5열이고 기능 하나가 한 행인가
   - 화면 열에 (신규 생성), (기존 수정), (변경 없음) 중 하나가 있는가
   - 확인 사항이 별도 섹션이 아니라 셀 안 ⚠️로 있는가. `미결`이라는 라벨이 없는가
   - 수치마다 근거 또는 ⚠️가 있는가
   - 흐름도가 그림 파일로 들어갔는가
   - `python3 scripts/lint_spec.py docs/PRODUCT_SPEC.md` 통과
3. 저장: `docs/PRODUCT_SPEC.md`, `docs/diagrams/*.mmd`, `docs/diagrams/*.png`. 이미 있으면 `docs/PRODUCT_SPEC.md.bak.YYYYMMDD-HHMM` 백업 후 저장. 안내: "저장: docs/PRODUCT_SPEC.md (확인 필요 N건)"
4. 아티팩트 질문 1회: "화면이나 흐름을 눌러 볼 수 있는 HTML도 만들까요? 1) 화면 프로토타입 HTML 2) 흐름 인터랙티브 시각화 3) 만들지 않음(기본)". 3이거나 답이 없으면 넘어감. 1이나 2면 「아티팩트 생성」대로 만들고 비주얼 표에 경로 기록
5. 파일 시스템이 없는 환경이면 본문만 출력하고 "Claude Code에서는 docs/PRODUCT_SPEC.md에 자동 저장됩니다" 한 줄

### Phase 5. Confluence 게시

`references/confluence.md`대로. Atlassian MCP가 없으면 건너뜀. 다이어그램 삽입은 `references/diagram.md`의 두 경로(첨부 기본, 토큰 없으면 블록). 게시 후 수치 셀에 인라인 댓글로 근거 첨부

## 수정 모드

`docs/PRODUCT_SPEC.md`가 있거나 이 대화에서 이미 스펙을 만들었거나 작성자가 기존 스펙을 첨부했을 때
1. 기존 문서를 읽고 변경 요청과 `git log --since`의 변경을 대조
2. 백업 후 영향 받는 섹션만 다시 써서 머지. 전체 재생성 금지, 변경 없는 섹션은 출력하지 않음
3. 연쇄 갱신: 페이지 추가나 삭제 → 변경 페이지 표와 메뉴 구조 표. 흐름 변경 → `.mmd` 수정과 재렌더. 범위 확장 → 구현 범위 요약 첫 불릿과 솔루션
4. 새로 생긴 빈칸은 Phase 2~3을 그 부분에만 적용
5. 안내: "갱신: docs/PRODUCT_SPEC.md (변경 섹션 N개)". Confluence Page ID가 있으면 `references/confluence.md`의 갱신 절차

## 아티팩트 생성

단일 HTML 파일(Vanilla JS와 CSS, 외부 CDN 없음, 오프라인 동작). 스펙과 같은 응답에 넣지 않고 별도로 만듦
- 화면 프로토타입: `<!DOCTYPE html>` 완전한 문서. 시스템 폰트 'Pretendard', -apple-system, sans-serif. CSS 변수로 Wanted Montage 색(`--color-primary: #3366FF` 등). 화면 전환은 class 토글. 입력 필드는 검증과 오류 문구 동작. 플랫폼별 차이가 있으면 뷰포트 전환 버튼
- 흐름 시각화: 흐름도의 노드를 클릭하면 해당 구현 상세 행이 강조되는 한 페이지
- 저장 위치 `docs/prototype-{제목 슬러그}.html`. Confluence 게시 시 첨부 경로가 있으면 같이 올림

## 응답 말투

- 한국어. 개조식. 안내는 한두 줄
- AI 판단과 작성자 확인 필요를 구분해 말함
- 가운데점, 줄표, 원형 숫자, 장식 이모지 없음. `⚠️`와 `📘`만
- `미결`, `누락`, `선제`, `요건` 같은 한자어 축약 라벨 없음. 치환표는 `references/writing-style.md`

## 하지 않는 것

- 호출 직후 모든 섹션을 추론으로 채워 출력하는 것. 골격 초안은 출처 있는 것만
- 사전 질문으로 시작하는 것. 초안이 먼저, 질문은 그 다음 (도메인 팩 수집 질문은 예외)
- 시나리오 표, 오류 등급, 성공 기준, 향후 방향, 미팅록, 업데이트 로그, 변경유형 열, `맥락:` 라벨
- 구현 방식(How)을 확정형으로 적는 것. 요구사항만 적고 "→ 개발 제안 요청"
- Mermaid 코드를 본문에 넣는 것
- 스펙이 이미 있는데 전체를 다시 만드는 것
- Confluence 페이지를 재읽기 없이 덮어쓰는 것. 로컬과 Confluence 중 한쪽만 갱신하는 것
- 남의 토큰을 쓰거나 토큰을 파일에 적는 것
