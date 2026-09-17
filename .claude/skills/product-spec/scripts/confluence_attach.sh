#!/usr/bin/env bash
# 사용법: confluence_attach.sh <pageId> <file>
# 실행자 본인의 토큰만 사용. 환경변수 ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, (선택) ATLASSIAN_SITE
# 출력: {"mediaId": "...", "collection": "contentId-<pageId>", "filename": "...", "attachmentId": "..."}
# 종료 코드: 0 성공, 1 실패, 2 토큰 없음
set -u
PAGE="${1:-}"; FILE="${2:-}"
if [ -z "$PAGE" ] || [ -z "$FILE" ]; then echo "사용법: confluence_attach.sh <pageId> <file>" >&2; exit 1; fi
if [ -z "${ATLASSIAN_EMAIL:-}" ] || [ -z "${ATLASSIAN_API_TOKEN:-}" ]; then
  cat >&2 <<'MSG'
첨부 업로드에는 본인 Atlassian API 토큰 필요. 없으면 다이어그램은 Mermaid 블록(폭 300px)으로 삽입
  1. https://id.atlassian.com/manage-profile/security/api-tokens 에서 발급
  2. ~/.zshrc에 추가 후 새 터미널
     export ATLASSIAN_EMAIL="본인 회사 이메일"
     export ATLASSIAN_API_TOKEN="발급한 토큰"
토큰은 본인 것만. 파일이나 문서에 기록 금지
MSG
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then echo "python3 없음. Xcode Command Line Tools 또는 python.org에서 설치 필요" >&2; exit 1; fi
if [ ! -f "$FILE" ]; then echo "파일 없음: $FILE" >&2; exit 1; fi
SITE="${ATLASSIAN_SITE:-wantedlab.atlassian.net}"
BASE="https://${SITE}/wiki/rest/api/content/${PAGE}/child/attachment"
NAME="$(basename "$FILE")"
HDR="X-Atlassian-Token: nocheck"
# 토큰을 인자로 넘기지 않고 curl 설정을 표준 입력으로 전달
CFG=$(printf 'user = "%s:%s"\n' "$ATLASSIAN_EMAIL" "$ATLASSIAN_API_TOKEN")
ENC_NAME=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$NAME")
EXIST=$(printf '%s' "$CFG" | curl -sS -K - -H "$HDR" "${BASE}?filename=${ENC_NAME}")
AID=$(printf '%s' "$EXIST" | python3 -c 'import sys,json
try:
    r=json.load(sys.stdin).get("results",[]); print(r[0]["id"] if r else "")
except Exception:
    print("")')
if [ -n "$AID" ]; then
  RESP=$(printf '%s' "$CFG" | curl -sS -K - -H "$HDR" -F "file=@${FILE}" "${BASE}/${AID}/data")
else
  RESP=$(printf '%s' "$CFG" | curl -sS -K - -H "$HDR" -F "file=@${FILE}" "${BASE}?allowDuplicated=false")
fi
printf '%s' "$RESP" | python3 -c '
import sys, json
page = sys.argv[1]
try:
    d = json.load(sys.stdin)
except Exception:
    print("업로드 응답 해석 불가", file=sys.stderr); sys.exit(1)
if "results" in d:
    d = d["results"][0] if d["results"] else {}
if "id" not in d:
    print("업로드 실패: " + json.dumps(d, ensure_ascii=False)[:300], file=sys.stderr); sys.exit(1)
ext = d.get("extensions", {})
media = ext.get("fileId") or ext.get("mediaId") or ""
print(json.dumps({"mediaId": media, "collection": f"contentId-{page}", "filename": d.get("title", ""), "attachmentId": d["id"]}, ensure_ascii=False))
' "$PAGE"
