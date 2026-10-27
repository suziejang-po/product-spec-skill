# product-spec-skill (v5.4.1)

Claude Code에서 `/product-spec`으로 호출하는 Product Spec 작성 스킬. 원본 레포를 포크해 v4, v5로 재구성

## 출처

아래 두 가지를 기반으로 발전시켰다

- 기존 스펙 문서: [Product Spec Claude Skill](https://wantedlab.atlassian.net/wiki/spaces/~71202040d3ee88a99a4ff7a2114eff1430dbd8/pages/4777082907/Product+Spec+Claude+Skill) (사내 Confluence, 원티드 계정 로그인 필요)
- 원본 레포: [hyeongkeunpark-bit/product-spec-skill](https://github.com/hyeongkeunpark-bit/product-spec-skill)

## 변경사항

- 출처 있는 내용만 쓴다. 코드, 첨부 자료, 대화, 기존 문서에 없는 도메인 서술은 빈칸으로 두고 질문한다
- 골격 초안을 먼저 보여주고, 리뷰 체크리스트(문제 근거, 가설과 KR, 사용자와 권한, 정책, 시나리오, 기능 상세, UI, 데이터 연동)로 빈 곳을 찾아 한 번에 5개 안팎씩 기본 2회 묻는다. 착수를 막는 항목이 남으면 한 번 더 제안
- 섹션 순서: 개요, 용어, 서비스 구조, 플로우, 유저향 화면(또는 구현 상세), 어드민 화면, 공통 정책, 기타 (원티드 화면 변경, 외부 연동)
  - 쓰지 않는 섹션은 지우고 번호를 1부터 이어 붙임 (v5.1)
  - 용어는 새 개념이 2개 이상일 때만, 플로우는 작성자가 고른 경우에만
- 기존 화면 개선은 '화면 > 영역' 경로, AS-IS → TO-BE, 유지와 삭제, 판단 근거 수치로 씀 (v5.1)
- 기준값, 조건, 대상 범위는 출처 문장을 인용해 두고 저장 전에 방향을 대조함 (v5.1)
- 상태와 버튼 표를 먼저 확정하고 화면을 씀. 다른 팀 화면(GNB, 기업대시보드, 프로필)도 원티드 화면 변경에 화면 표로 쓰고 담당팀 확인 표시
- 다른 곳은 "7-2 신청 취소 확인"처럼 섹션 번호와 이름으로 가리킴. 문서 안 링크 없음
- 화면 문구는 그 문구가 보이는 요소 바로 아래에 씀. '문구' 소제목을 따로 두지 않음 (v5.1.1). 정해지지 않은 문구는 "(문구 워싱 필요)"
- ⚠️는 착수를 막는 것에만. 나머지 확인 사항은 "(PO 확인 필요)" 같은 평문 괄호. 건수는 채팅으로만 알림. AI가 빈칸을 대신 채우지 않음
- 프로토타입 HTML은 화면마다 스펙 요구사항 설명 패널을 달아 디자이너와 개발자에게 그대로 설명할 수 있게 함
- 그림은 초안 전에 고름: 담당자 띠 흐름도, 현재 화면 캡처 자리, 넣지 않음(기본)
- 메뉴 구조를 바꿀 때 같은 기능이 두 메뉴에 생기지 않는지, 칩과 탭의 처음 값이 무엇인지 점검. 운영 설정이 유저 화면에 미치는 영향 표 (v5.2)
- 비슷한 버튼과 링크는 용어 표에서 동작으로 구분하고, 내부 용어는 화면에 쓰지 않음 (v5.2)
- 프로토타입이 있으면 유저 관점 리뷰(과업별로 처음 누를 곳과 찾는지)를 따로 돌림. 상태별 화면은 시연 패널로 전환 (v5.2)
- 게시 전 검사를 코드로 강제: lint를 통과하지 않으면 Confluence 본문 변환기가 본문을 만들지 않음. lint에 넣지 않는 섹션, 결정 날짜, 문단 서술, 메타의 문서 유형, 구현 상세 5열과 화면 표 3열 검사 추가 (v5.3)
- 시작 전에 읽을 파일을 SKILL.md 맨 위에 명시. 로컬 스킬이 최신이 아니면 업데이트할지 먼저 물음 (v5.3)
- 변경 표시 프로토타입: 실제 원티드 화면을 WDS로 재현하고 이번에 바뀌는 곳을 점선 상자로 표시함. 색은 확정, 외부 요청, 확인 필요. 범례에서 표시를 끄면 완성 화면처럼 보이고, 화면은 버튼으로 이어짐. 아티팩트 질문에서 3번을 고르거나 "변경 표시 프로토타입 만들어줘" (v5.4)
- 플러그인 마켓플레이스에서 설치할 수 있게 `.claude-plugin/plugin.json` 추가 (v5.4)
- 슬랙 공유 요약 양식: `변경사항`, `디자인 확인 필요`로 나누고 짧게, 경로로 씀 (v5.2)
- 질문할 때 화면 ID와 함께 화면 이름과 상황을 씀. 이미 정한 것은 다시 묻지 않음 (v5.2)
- 문체는 개조식. 누가 하는지 쓰고, 들여쓰기로 묶음. 가운데점, 줄표, 원형 숫자, 한자어 축약 라벨 금지. 출력 전 자동 검사 (번호가 이어지는지, ⚠️가 착수 조건에만 있는지도 검사)

## 설치

배포 정본은 사내 마켓플레이스 `wanteddev/claude-skills`의 `plugins/product-spec`. 이 레포는 개발용 (비공개)

### Claude Code

```
/plugin marketplace add wanteddev/claude-skills
/plugin install product-spec@claude-skills
```

### Claude 앱 (claude.ai, 데스크톱 앱)

1. 스킬 관리자에게 `dist/product-spec.zip`을 받음
2. 설정 > 기능(Capabilities)에서 코드 실행을 켬
3. 같은 화면의 스킬에서 zip 업로드
4. 채팅에서 "스펙 작성해줘"로 호출

zip 안은 `product-spec/` 폴더 하나. 압축을 풀거나 다시 묶지 않고 그대로 올림

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
    template.md                 스펙 양식 v5.2
    template-example.md         Feature 예시 (가상, 밀도와 문체 기준)
    template-example-enhancement.md  기존 화면 개선 예시 (가상)
    template-example-new.md     New Product 예시 (가상 예시)
    review-checklist.md         리뷰 6개 대항목과 판정 기준
    question-map.md             빈칸을 질문으로 바꾸는 표
    context-pack.md             도메인 팩 양식과 수집 절차
    diagram.md                  다이어그램 규칙과 삽입 경로
    confluence.md               게시, 갱신, 충돌 검사, 인라인 댓글
    writing-style.md            문체와 금지어
    change-prototype.md         변경 표시 프로토타입 규칙
    change-prototype-template.html  변경 표시 프로토타입 양식 (WDS 토큰, 동작 속성)
  scripts/
    lint_spec.py                문체 검사
    render_diagram.sh           Mermaid → PNG
    mermaid_macro.py            Mermaid 블록 HTML 생성
    confluence_attach.sh        첨부 업로드 (본인 토큰)
    md_to_confluence.py         마크다운 → Confluence HTML
```

## 업데이트

- 플러그인: `/plugin update product-spec`
- 이 레포를 고친 뒤 마켓플레이스 반영: `register-product-spec.sh` 다시 실행 → wanteddev/claude-skills에 PR
- 스킬이 스스로 원격 파일을 받아 덮어쓰지 않음 (v5.4.1에서 뺌)

## 스킬 점검 (관리자용)

```
bash tests/run.sh
```

- 예시 문서 3개가 lint를 통과하는지
- 일부러 틀린 가상 문서(`tests/fixtures/bad-spec.md`)가 검사 항목마다 걸리는지
- 변환기가 lint 위반 문서를 막고 정상 문서는 변환하는지
- 변경 표시 프로토타입 양식의 화면 이동, 모달, 입력 검사 연결이 실제 id를 가리키는지
- skill-files 목록의 파일이 모두 있는지
- 스킬 파일을 고친 뒤 커밋 전에 돌림
