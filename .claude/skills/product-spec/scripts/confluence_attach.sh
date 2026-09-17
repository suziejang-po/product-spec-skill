#!/usr/bin/env bash
# 사용법: confluence_attach.sh <pageId> <file>
# 실행자 본인의 토큰만 사용. 환경변수 ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, (선택) ATLASSIAN_SITE
# 출력: {"mediaId": "...", "collection": "contentId-<pageId>", "filename": "...", "attachmentId": "..."}
set -u
PAGE="${1:-}"; FILE="${2:-}"
if [ -z "$PAGE" ] || [ -z "$FILE" ]; then echo "사용법: confluence_attach.sh <pageId> <file>" >&2; exit 1; fi
if [ -z "${ATLASSIAN_EMAIL:-}" ] || [ -z "${ATLASSIAN_API_TOKEN:-}" ]; then
  cat >&2 <<'MSG'
첨부 업로드에는 본인 Atlassian API 토큰이 필요합니다. 등록하지 않으면 다이어그램은 Mermaid 블록(폭 300px)으로 들어갑니다.
  1. https://id.atlassian.com/manage-profile/security/api-tokens 에서 토큰 발급
  2. 셸 설정(~/.zshrc)에 추가 후 새 터미널
     export ATLASSIAN_EMAIL="본인 회사 이메일"
     export ATLASSIAN_API_TOKEN="발급한 토큰"
토큰은 본인 것만 쓰고 파일이나 문서에 적지 않습니다.
MSG
  exit 2
fi
SITE="${ATLASSIAN_SITE:-wantedlab.atlassian.net}"
BASE="https://${SITE}/wiki/rest/api/content/${PAGE}/child/attachment"
NAME="$(basename "$FILE")"
AUTH="${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}"
HDR="X-Atlassian-Token: nocheck"

# 같은 이름의 첨부가 있으면 새 버전으로, 없으면 신규 업로드
EXIST=$(curl -sS -u "$AUTH" -H "$HDR" "${BASE}?filename=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$NAME")")
AID=$(printf '%s' "$EXIST" | python3 -c 'import sys,json
try:
    r=json.load(sys.stdin).get("results",[])
    print(r[0]["id"] if r else "")
except Exception:
    print("")')
if [ -n "$AID" ]; then
  RESP=$(curl -sS -u "$AUTH" -H "$HDR" -F "file=@${FILE}" "${BASE}/${AID}/data")
else
  RESP=$(curl -sS -u "$AUTH" -H "$HDR" -F "file=@${FILE}" "${BASE}?allowDuplicated=false")
fi
printf '%s' "$RESP" | python3 -c '
import sys, json
page = sys.argv[1]
try:
    d = json.load(sys.stdin)
except Exception:
    print("업로드 응답을 읽지 못했습니다", file=sys.stderr); sys.exit(1)
if "results" in d:
    d = d["results"][0] if d["results"] else {}
if "id" not in d:
    print("업로드 실패: " + json.dumps(d, ensure_ascii=False)[:300], file=sys.stderr); sys.exit(1)
ext = d.get("extensions", {})
media = ext.get("fileId") or ext.get("mediaId") or ""
print(json.dumps({"mediaId": media, "collection": f"contentId-{page}", "filename": d.get("title", ""), "attachmentId": d["id"]}, ensure_ascii=False))
' "$PAGE"
