#!/usr/bin/env bash
# 사용법: render_diagram.sh <in.mmd> <out.png> [attach|macro]
# attach: 첨부 이미지용 (폭 1200, 2배). macro: 다이어그램 블록용 (폭 300, 1배)
set -u
IN="${1:-}"; OUT="${2:-}"; MODE="${3:-attach}"
CLI="@mermaid-js/mermaid-cli@11"
if [ -z "$IN" ] || [ -z "$OUT" ]; then
  echo "사용법: render_diagram.sh <in.mmd> <out.png> [attach|macro]" >&2; exit 1
fi
if ! command -v npx >/dev/null 2>&1; then
  echo "렌더 불가: npx 없음. Node.js 설치 필요 (https://nodejs.org)" >&2; exit 1
fi
case "$MODE" in
  macro) OPTS="-w 300 -s 1" ;;
  *) OPTS="-w 1200 -s 2" ;;
esac
mkdir -p "$(dirname "$OUT")"
LOG="$(mktemp -t mermaid-render).log"
if ! npx -y "$CLI" -i "$IN" -o "$OUT" -b white $OPTS >"$LOG" 2>&1; then
  echo "렌더 실패: $IN" >&2
  echo "원인 (마지막 15줄):" >&2
  tail -n 15 "$LOG" >&2
  echo "확인: 1. Mermaid 문법 2. 네트워크 (npx가 패키지와 Chromium을 받음) 3. 로그 $LOG" >&2
  exit 1
fi
rm -f "$LOG"
echo "$OUT"
