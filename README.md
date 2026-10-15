# product-spec-skill (v5.0.1)

Claude Code에서 `/product-spec`으로 호출하는 Product Spec 작성 스킬. 원본 레포를 포크해 v4, v5로 재구성

## 출처

아래 두 가지를 기반으로 발전시켰다

- 기존 스펙 문서: [Product Spec Claude Skill](https://wantedlab.atlassian.net/wiki/spaces/~71202040d3ee88a99a4ff7a2114eff1430dbd8/pages/4777082907/Product+Spec+Claude+Skill) (사내 Confluence, 원티드 계정 로그인 필요)
- 원본 레포: [hyeongkeunpark-bit/product-spec-skill](https://github.com/hyeongkeunpark-bit/product-spec-skill)

## 변경사항

- 출처 있는 내용만 쓴다. 코드, 첨부 자료, 대화, 기존 문서에 없는 도메인 서술은 빈칸으로 두고 질문한다
- 골격 초안을 먼저 보여주고, 리뷰 체크리스트(문제 근거, 가설과 KR, 사용자와 권한, 정책, 시나리오, 기능 상세, UI, 데이터 연동)로 빈 곳을 찾아 한 번에 5개 안팎씩 기본 2회 묻는다. 착수를 막는 항목이 남으면 한 번 더 제안
- 문서 뼈대는 문서 유형과 상관없이 1~8 번호 섹션 (v5)
  - 1. 개요 (메타, 문제, 니즈, 가설, 솔루션, KR, 참고)
  - 2. 용어 (2-1 상태, 2-2 버튼/액션, 2-3 도메인 용어)
  - 3. 서비스 구조 (상태 흐름, 메뉴 구조, 차수별 범위)
  - 4. 플로우
  - 5. 유저향 화면 (Feature, Enhancement는 5. 구현 상세 5열 표)
  - 6. 어드민 화면
  - 7. 공통 정책
  - 8. 기타 (8-1 원티드 화면 변경, 8-2 외부 연동)
- 상태와 버튼 표를 먼저 확정하고 화면을 씀. 다른 팀 화면(GNB, 기업대시보드, 프로필)도 8-1에 화면 표로 쓰고 담당팀 확인 표시
- 다른 곳은 "7-2 순위 표 확인"처럼 섹션 번호와 이름으로 가리킴. 문서 안 링크 없음
- 정해지지 않은 UI 문구는 "(문구 워싱 필요)"
- 질문이 끝나면 문서 첫 줄에 "착수 전 확인 필요 N건"이 표시됨. AI가 빈칸을 대신 채우지 않음
- 프로토타입 HTML은 화면마다 스펙 요구사항 설명 패널을 달아 디자이너와 개발자에게 그대로 설명할 수 있게 함
- 다이어그램은 코드가 아니라 담당자별 띠 그림으로 들어간다. 첨부 파일로 올려 크게 보임
- 문체는 개조식. 누가 하는지 쓰고, 들여쓰기로 묶음. 가운데점, 줄표, 원형 숫자, 한자어 축약 라벨 금지. 출력 전 자동 검사 (번호 뼈대 순서도 검사)

## 설치

### Claude 앱 (claude.ai, 데스크톱 앱)

1. [dist/product-spec.zip](dist/product-spec.zip)을 내려받음 (Download raw file)
2. 설정 > 기능(Capabilities)에서 코드 실행을 켬
3. 같은 화면의 스킬에서 zip 업로드
4. 채팅에서 "스펙 작성해줘"로 호출

zip 안은 `product-spec/` 폴더 하나. 압축을 풀거나 다시 묶지 않고 그대로 올림

### Claude Code

Claude Code에 URL을 주고 설치를 요청

> 이 스킬 설치해줘 https://github.com/suziejang-po/product-spec-skill

또는 레포의 `.claude/skills/product-spec` 폴더를 `~/.claude/skills/` 아래에 복사

Node.js가 있어야 다이어그램을 그린다

## 사용

```
/product-spec
```

또는 "스펙 작성해줘", "PRD 만들어줘", "구현 요구사항 정리해줘". 회고, 인수인계, 일반 문서 정리에는 쓰지 않음

흐름: 도메인 팩 수집(첫 실행만) → 골격 초안 → 질문(우선순위 순, 5개씩 기본 2회) → 본문 저장(`docs/specs/{슬러그}/spec.md`) → 아티팩트 여부 질문 → Confluence 게시

- 스펙 하나가 폴더 하나. `docs/specs/{슬러그}/` 아래 `spec.md`, `diagrams/`, `sources.md`(출처 기록)
- 기존 스펙이 있으면 변경 섹션만 수정. 예전 구조 `docs/PRODUCT_SPEC.md`도 인식
- `docs/spec-context.md`(도메인 팩)는 같은 프로젝트에서 재사용. 사내 정보가 들어가므로 공개 레포면 gitignore

## 다이어그램을 Confluence에 넣는 두 경로

| 경로 | 조건 | 결과 |
|---|---|---|
| 첨부 이미지 | 본인 Atlassian API 토큰을 환경변수로 등록 | 본문 폭에 맞게 크게, 선명하게 (⚠️ 토큰 보유자의 첫 실행으로 검증 필요) |
| Mermaid 블록 | 토큰 없음 | 세로형 상태도와 순서도는 블록으로 자동 삽입(폭 300px). 가로형 흐름도는 안내 상자가 들어가며 편집 화면에서 /mermaid 로 코드를 한 번 붙여넣음 |

토큰 등록 (본인 것만. 파일이나 문서에 적지 않음)

```bash
# https://id.atlassian.com/manage-profile/security/api-tokens 에서 발급 후 ~/.zshrc에 추가
export ATLASSIAN_EMAIL="본인 회사 이메일"
export ATLASSIAN_API_TOKEN="발급한 토큰"
# 사이트가 다르면
export ATLASSIAN_SITE="wantedlab.atlassian.net"
```

## 파일 구조

```
.claude/skills/product-spec/
  SKILL.md                      실행 흐름과 규칙
  references/
    template.md                 스펙 양식 v5 (1~8 번호 뼈대)
    template-example.md         가상 서비스 예시 (밀도와 문체 기준)
    review-checklist.md         리뷰 6개 대항목과 판정 기준
    question-map.md             빈칸을 질문으로 바꾸는 표
    context-pack.md             도메인 팩 양식과 수집 절차
    diagram.md                  다이어그램 규칙과 삽입 경로
    confluence.md               게시, 갱신, 충돌 검사, 인라인 댓글
    writing-style.md            문체와 금지어
  scripts/
    lint_spec.py                문체 검사
    render_diagram.sh           Mermaid → PNG
    mermaid_macro.py            Mermaid 블록 HTML 생성
    confluence_attach.sh        첨부 업로드 (본인 토큰)
    md_to_confluence.py         마크다운 → Confluence HTML
```

## 업데이트

실행 시 원격 버전을 확인해 다르면 안내한다. "스킬 업데이트해줘"라고 하면 `SKILL.md`의 `skill-files` 목록 전체를 내려받아 갱신한다
