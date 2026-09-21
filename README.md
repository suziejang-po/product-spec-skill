# product-spec-skill (v4.1)

Claude Code에서 `/product-spec`으로 호출하는 Product Spec 작성 스킬. 원본 `hyeongkeunpark-bit/product-spec-skill`을 포크해 v4로 재구성

## 무엇이 달라졌나

- 출처 있는 내용만 쓴다. 코드, 첨부 자료, 대화, 기존 문서에 없는 도메인 서술은 빈칸으로 두고 질문한다
- 골격 초안을 먼저 보여주고, 리뷰 체크리스트(사용자와 권한, 정책, 시나리오, 기능 상세, UI, 데이터 연동)로 빈 곳을 찾아 한 번에 5개 안팎씩 최대 2회 묻는다
- 구현 상세는 번호, 진입점, 화면, 기능, 요구사항 5열 표. 기능 하나가 한 행
- 문제와 솔루션은 한 줄 불릿, 사용자 니즈는 이해관계자별 한 줄. 기존 제품을 바꾸면 현재 vs 변경 비교표
- 질문이 끝나면 문서 첫 줄에 "착수 전 확인 필요 N건"이 표시됨. AI가 빈칸을 대신 채우지 않음
- 프로토타입 HTML은 화면마다 스펙 요구사항 설명 패널을 달아 디자이너와 개발자에게 그대로 설명할 수 있게 함
- 다이어그램은 코드가 아니라 그림으로 들어간다
- 문체는 개조식 명사 종결. 가운데점, 줄표, 원형 숫자, 한자어 축약 라벨 금지. 출력 전 자동 검사

## 설치

Claude Code에 URL을 주고 설치를 요청

> 이 스킬 설치해줘 https://github.com/suziejang-po/product-spec-skill

Node.js가 있어야 다이어그램을 그린다 (`npx @mermaid-js/mermaid-cli`를 자동으로 받음)

## 사용

```
/product-spec
```

또는 "스펙 작성해줘", "PRD 만들어줘", "구현 요구사항 정리해줘". 회고, 인수인계, 일반 문서 정리에는 쓰지 않음

흐름: 도메인 팩 수집(첫 실행만) → 골격 초안 → 질문(우선순위 순, 5개씩 최대 2회) → 본문 저장(`docs/specs/{슬러그}/spec.md`) → 아티팩트 여부 질문 → Confluence 게시

- 스펙 하나가 폴더 하나. `docs/specs/{슬러그}/` 아래 `spec.md`, `diagrams/`, `sources.md`(출처 기록)
- 기존 스펙이 있으면 변경 섹션만 수정. 예전 구조 `docs/PRODUCT_SPEC.md`도 인식
- `docs/spec-context.md`(도메인 팩)는 같은 프로젝트에서 재사용. 사내 정보가 들어가므로 공개 레포면 gitignore

## 다이어그램을 Confluence에 넣는 두 경로

| 경로 | 조건 | 결과 |
|---|---|---|
| 첨부 이미지 | 본인 Atlassian API 토큰을 환경변수로 등록 | 폭 80%로 크게, 선명하게 (⚠️ 토큰 보유자의 첫 실행으로 검증 필요) |
| Mermaid 블록 | 토큰 없음 | 자동으로 들어가지만 폭 300px로 작게. 본문이 40KB를 넘으면 첫 그림만 |

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
    template.md                 스펙 양식 v4
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
