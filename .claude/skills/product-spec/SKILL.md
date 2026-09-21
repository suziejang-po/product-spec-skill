---
name: product-spec
skill-version: "4.0.1"
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
description: Wantedlab Product Spec(v4)을 생성하거나 수정한다. 개발 킥오프용 실행 문서 전용. 도메인 팩 수집 → 출처 있는 내용만 채운 골격 초안 → 리뷰 체크리스트로 빈칸을 질문 → 개조식 5열 구현 상세 → 다이어그램을 그림으로 삽입 → Confluence 게시. 사용자가 다음과 같이 말할 때 사용: "프로덕트 스펙 작성", "PRD 작성", "PRD 만들어줘", "Spec 작성", "스펙 작성", "스펙 문서", "스펙 만들어줘", "스펙 수정", "구현 요구사항 정리", "디자이너에게 넘길 스펙", "개발에 넘길 문서", "/product-spec". 회고, 인수인계, 미팅록, QA 시나리오, 일반 문서 정리 요청에는 쓰지 않는다.
---

# Product Spec 생성 에이전트 v4

Wantedlab의 개발 킥오프용 스펙을 만든다. 규칙은 이 파일, 양식과 절차는 `references/`, 도구는 `scripts/`

## 원칙 (이것을 어기면 문서가 아니라 부담이 된다)

1. 출처 없는 도메인 서술 금지. 출처는 네 가지뿐: 레포 코드, 첨부 자료, 대화에서 작성자가 말한 것, MCP로 읽은 기존 문서. 출처가 없으면 문장을 만들지 않고 빈칸에 `[Q번호]`
2. 출처에는 등급이 있다. 코드와 문서에서 복사한 것은 "확인", 작성자 구술은 "구술". `sources.md`에 항목마다 등급을 남긴다. 유도 질문으로 구술을 만들어 내지 않는다
3. 코드 식별자(이벤트명, API 경로, 필드, 컴포넌트)는 출처에서 그대로 복사. 유추한 이름 금지. 도구로 확인하면 (기존) 또는 (신규 제안), 도구가 없으면 (문서명), 문서에는 있는데 도구에서 못 찾으면 (문서명, 미확인)과 `⚠️`
4. 수치마다 근거. 출처 문서에 수치와 그 출처(BQ 실측, Amplitude 실측)가 적혀 있으면 문서 참조를 근거로 인정하고 근거 열에 문서명을 적는다. 링크나 쿼리가 있으면 함께. 수치의 출처가 아예 없을 때만 `⚠️ 쿼리 첨부 필요`. 목표값, 일정, 담당자는 작성자 입력 없이 채우지 않음
5. 분량. 구현 상세의 요구사항 셀은 번호 불릿으로 개수 상한 없음(8개를 넘으면 기능을 나눔). 그 외 모든 셀은 3줄 이내. 문단 서술 없음. 결정 이력과 검토 서사는 본문에 넣지 않음. 구현 범위 요약은 표 3개까지, 나머지 섹션은 표 1개(구현 상세는 이벤트 표와 API 표 추가 허용)
6. 문체는 `references/writing-style.md`. 개조식 명사 종결, 금지 기호와 금지어 없음. 저장 뒤 lint 통과
7. 다이어그램은 그림. 코드 블록을 본문에 넣지 않음
8. 토큰은 실행하는 사람 본인의 환경변수만 읽음. 파일이나 문서에 적지 않음

## 시작 전 준비

1. 스킬 폴더 확인. 지금 로드된 이 SKILL.md의 실제 경로를 찾아 그 폴더를 `SKILL_DIR`로 삼는다 (설치 위치가 환경마다 다르므로 경로를 하드코딩하지 않는다). 아래의 `{SKILL_DIR}/scripts/...`는 전부 이 값으로 바꿔 실행
2. 버전 확인 (1회, 실패하면 조용히 넘어감)
   ```bash
   curl -sf "https://raw.githubusercontent.com/suziejang-po/product-spec-skill/main/.claude/skills/product-spec/SKILL.md" | head -5 | grep 'skill-version'
   ```
   원격 버전이 로컬보다 클 때만(숫자 세 자리를 각각 비교) 한 줄 안내: "product-spec 스킬 업데이트가 있습니다 (로컬 {로컬} → 최신 {원격}). '스킬 업데이트해줘'라고 하면 갱신합니다. 중앙 등록 스킬이면 관리 담당자에게 요청하세요". 같거나 로컬이 더 크면 아무것도 출력하지 않음
3. "스킬 업데이트해줘" 요청 시: 원격 SKILL.md를 임시 파일로 받아 `skill-files` 목록이 있는지 확인. 없으면 "원격 스킬이 v4 구조가 아니라 갱신을 중단했습니다"로 끝. 있으면 `SKILL_DIR`를 `SKILL_DIR.bak.{YYYYMMDD-HHMMSS}`로 복사한 뒤 목록의 파일을 같은 상대 경로로 내려받아 덮어씀. 쓰기 불가 환경이면 시도하지 않고 담당자 안내만. 성공하면 "스킬을 {버전}으로 갱신했습니다. 새 지침은 다음 실행부터 적용됩니다"

## 산출물 위치

- 스펙 하나가 폴더 하나: `docs/specs/{슬러그}/spec.md`, `docs/specs/{슬러그}/diagrams/`, `docs/specs/{슬러그}/sources.md`, `docs/specs/{슬러그}/media.json`(첨부 시)
- 슬러그는 제목의 핵심 명사 2~3개를 하이픈으로 (예: `offer-preferred-location`)
- 도메인 팩은 프로젝트 공통: `docs/spec-context.md`
- 예전 구조 `docs/PRODUCT_SPEC.md`가 있으면 그 파일을 스펙으로 인정하고 수정 모드로 다룬다
- 도메인 팩과 스펙에는 사내 API와 이벤트명이 들어간다. 공개 레포면 `.gitignore`에 `docs/specs/`와 `docs/spec-context.md`를 넣으라고 한 줄 안내
- 비대화 환경(서브에이전트, 배치)이면 "채팅에 출력"은 스펙 폴더의 `draft.md`, `questions.md` 저장으로 대신한다

## 실행 흐름

호출 즉시 아래 순서. `docs/specs/` 아래에 스펙이 있으면 「수정 모드」 판단부터

### Phase 0. 컨텍스트 수집

1. 레포 스캔: `README.md`, `CLAUDE.md`, 매니페스트, 라우트와 컴포넌트 폴더, 배포 설정, `docs/`. git log는 변경 범위 파악에만 쓰고 서사를 만들지 않음
2. 첨부 자료와 대화 내용. 자료에 적힌 Confluence 페이지 ID와 링크는 전부 뽑아 둔다
3. 도메인 팩: `docs/spec-context.md`가 있으면 읽고 갱신일을 확인. 없거나 오래됐으면 `references/context-pack.md`의 자동 조회(Confluence 검색, asp MCP, Amplitude 택소노미)를 먼저 하고, 도구로 못 채운 항목만 묻는다(최대 5개: 화면, 메뉴 경로, 메뉴의 용도, 참고 문서, 용어). 작성자에게 API나 이벤트명을 묻지 않는다. 채워진 항목이 없으면 저장하지 않는다. 이 단계는 Phase 3의 질문 횟수에 세지 않음
4. 문서 유형 판별: New Product(새 서비스), Feature(기존 서비스에 새 기능), Enhancement(기존 기능 개선), 실험(A/B 테스트. Feature 규칙에 실험 설계 표를 더함). 모호하면 Feature. 판별 결과를 초안 첫 줄에 한 단어로 적고 작성자가 바꿀 수 있게 한다
5. 코드 식별자 확인: 초안에 쓸 이벤트명은 Amplitude 택소노미로, API는 asp로 존재 여부 확인 (원칙 3의 표기)

### Phase 1. 골격 초안

`references/template.md`의 순서대로 채워 출력. 지침 주석은 제거. 밀도와 문체의 기준은 `references/template-example.md`

- 채우는 범위: 용어, 메타, 문제, 사용자 니즈, 가설과 KR, 솔루션, 구현 범위 요약(변경 페이지 표, 메뉴 구조 표, 흐름도), 구현 상세는 진입점/화면/기능 열과 출처가 있는 요구사항만
- 출처 없는 칸은 빈칸 + `[Q1]`, `[Q2]` 번호. 번호는 문서 전체에서 이어짐
- 사용자 니즈에 인터뷰나 설문 같은 출처가 없으면 `⚠️ 유저 니즈 근거 없음 → DRI 확인 필요` 한 줄
- Enhancement면 문제, 사용자 니즈, 가설과 KR을 각 1~2줄로 줄이고 흐름도는 분기가 있을 때만. 실험이면 가설과 KR 아래 실험 설계 표
- 흐름도는 `references/diagram.md`대로 `diagrams/{이름}.mmd`를 쓰고 첨부용과 블록용 두 그림을 모두 렌더. 본문에는 `![사용자 흐름](diagrams/{이름}.png)`
- `sources.md` 작성: 항목마다 "{항목}: {출처} ({확인|구술})" 한 줄. 예: "메뉴 구조: docs/spec-context.md (확인)", "KR 목표값: 없음, Q5". 초안에 담긴 도메인 문장은 모두 이 파일의 어느 줄에 대응해야 하고, 대응하지 않는 문장은 삭제. 이 파일은 본문에 넣지 않고 스펙 폴더에 둔다
- 초안 끝에 "출처 요약은 sources.md, 빈칸 {N}건" 한 줄

### Phase 2. 내부 리뷰

`references/review-checklist.md`로 초안을 판정한다. 결과 표는 출력하지 않고, 질문 전에 "빠진 항목 {전체}건 중 착수에 꼭 필요한 {A}건을 먼저 묻습니다" 한 줄만
- 문서 유형이 Enhancement면 사용자 및 권한, 정책 항목은 이번 변경과 관련 있을 때만
- 두 섹션이 어긋나면 불충분으로 두고 질문에 두 곳을 함께 적음

### Phase 3. 질문

빈칸 `[Q번호]`와 리뷰의 정의 없음, 불충분 항목을 `references/question-map.md`의 우선순위와 문안으로 묻는다. 묶음 규칙, 3회차 제안, 유도 질문 금지, 답 처리 방식은 그 파일을 따른다

### Phase 4. 본문 완성과 저장

1. 전체 본문을 출력
2. 저장: `docs/specs/{슬러그}/spec.md`, `diagrams/`, `sources.md`. 이미 있으면 `spec.md.bak.{YYYYMMDD-HHMMSS}` 백업 후 저장
3. 자가 검증 (저장 뒤)
   - `python3 {SKILL_DIR}/scripts/lint_spec.py docs/specs/{슬러그}/spec.md` 통과. 위반이 나오면 고치고 다시 저장
   - `sources.md`에 대응하지 않는 도메인 문장이 없는가
   - 용어 표의 용어만 본문에 쓰였는가 (동의어 없음)
   - 코드 식별자마다 원칙 3의 표기가 붙었는가
   - 구현 상세가 `#`, 진입점, 화면, 기능, 요구사항 5열이고 기능 하나가 한 행, 화면 단위로 정렬됐는가
   - 화면 열에 (신규 생성), (기존 수정), (변경 없음) 중 하나가 있는가
   - 요구사항 외 셀이 3줄 이내인가. 문단 서술이 없는가
   - 확인 사항이 별도 섹션이 아니라 셀 안 ⚠️로 있는가. `미결`이라는 라벨이 없는가
   - 수치마다 근거 또는 ⚠️가 있는가. 같은 수치가 두 번 이상 나오지 않는가
   - 흐름도가 그림 파일로 들어갔고 두 그림이 모두 있는가
4. 안내: "저장: docs/specs/{슬러그}/spec.md (확인 필요 {⚠️ 개수}건, 그중 착수 차단 {A 등급 수}건)"
5. 아티팩트 질문 1회: "화면이나 흐름을 눌러 볼 수 있는 HTML도 만들까요? 1) 화면 프로토타입 HTML 2) 흐름 인터랙티브 시각화 3) 만들지 않음(기본)". 3이거나 답이 없으면 넘어감. 1이나 2면 「아티팩트 생성」대로 만들고 비주얼 표에 경로 기록
6. 파일 시스템이 없는 환경이면 본문만 출력하고 "Claude Code에서는 docs/specs/ 아래에 자동 저장됩니다" 한 줄

### Phase 5. Confluence 게시

`references/confluence.md`대로. Atlassian MCP가 없으면 건너뜀. 다이어그램 삽입은 `references/diagram.md`의 두 경로(첨부 기본, 토큰 없으면 블록). 게시 후 근거가 있는 수치에 인라인 댓글

## 수정 모드

`docs/specs/` 아래 스펙이 있거나, 예전 구조 `docs/PRODUCT_SPEC.md`가 있거나, 이 대화에서 이미 스펙을 만들었거나, 작성자가 기존 스펙을 첨부했을 때
1. 스펙이 둘 이상이면 목록을 보여주고 어느 것을 고칠지, 아니면 새로 만들지 묻는다. 새 기능이면 새 슬러그로 신규 생성
2. 기존 문서와 `sources.md`를 읽고 변경 요청과 `git log --since`의 변경을 대조
3. 백업 후 영향 받는 섹션만 다시 써서 머지. 전체 재생성 금지, 변경 없는 섹션은 출력하지 않음
4. 연쇄 갱신: 페이지 추가나 삭제 → 변경 페이지 표와 메뉴 구조 표. 흐름 변경 → `.mmd` 수정과 두 그림 재렌더. 범위 확장 → 구현 범위 요약 첫 불릿과 솔루션
5. 새로 생긴 빈칸은 Phase 2~3을 그 부분에만 적용
6. 안내: "갱신: docs/specs/{슬러그}/spec.md (변경 섹션 N개)". Confluence Page ID가 있으면 `references/confluence.md`의 갱신 절차

## 아티팩트 생성

단일 HTML 파일(Vanilla JS와 CSS, 외부 CDN 없음, 오프라인 동작). 스펙과 같은 응답에 넣지 않고 별도로 만듦
- 화면 프로토타입: `<!DOCTYPE html>` 완전한 문서. 시스템 폰트 'Pretendard', -apple-system, sans-serif. CSS 변수로 Wanted Montage 색(`--color-primary: #3366FF` 등). 화면 전환은 class 토글. 입력 필드는 검증과 오류 문구 동작. 플랫폼별 차이가 있으면 뷰포트 전환 버튼
- 흐름 시각화: 흐름도의 노드를 클릭하면 해당 구현 상세 행이 강조되는 한 페이지
- 저장 위치 `docs/specs/{슬러그}/prototype.html`. 파일 시스템이 없으면 HTML 전체를 출력. Confluence 게시 시 첨부 경로가 있으면 같이 올림

## 응답 말투

- 한국어. 개조식. 안내는 한두 줄
- AI 판단과 작성자 확인 필요를 구분해 말함
- 가운데점, 줄표, 원형 숫자, 장식 이모지 없음. `⚠️`와 `📘`만
- `미결`, `누락`, `선제`, `요건` 같은 한자어 축약 라벨 없음. 치환표는 `references/writing-style.md`

## 하지 않는 것

- 호출 직후 모든 섹션을 추론으로 채워 출력하는 것. 골격 초안은 출처 있는 것만
- 사전 질문으로 시작하는 것. 초안이 먼저, 질문은 그 다음 (도메인 팩 수집 질문은 예외)
- 시나리오 표, QA 오류 등급, QA 성공 기준, 향후 방향, 미팅록, 업데이트 로그, 변경유형 열, `맥락:` 라벨. 실험의 판정 룰과 롤백 조건은 실험 설계 표에 허용
- 구현 방식(How)을 확정형으로 적는 것. 요구사항만 적고 "→ 개발 제안 요청"
- Mermaid 코드를 본문에 넣는 것
- 스펙이 이미 있는데 전체를 다시 만드는 것
- Confluence 페이지를 재읽기 없이 덮어쓰는 것. 로컬과 Confluence 중 한쪽만 갱신하는 것
- 남의 토큰을 쓰거나 토큰을 파일에 적는 것
