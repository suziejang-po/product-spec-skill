#!/usr/bin/env bash
# 사용법: render_diagram.sh <in.mmd> <out.png> [attach|macro]
# attach: 첨부 이미지용(폭 1200, 2배). macro: 다이어그램 블록용(폭 300, 2배)
set -u
IN="${1:-}"; OUT="${2:-}"; MODE="${3:-attach}"
if [ -z "$IN" ] || [ -z "$OUT" ]; then
  echo "사용법: render_diagram.sh <in.mmd> <out.png> [attach|macro]" >&2; exit 1
fi
if ! command -v npx >/dev/null 2>&1; then
  echo "npx가 없어 다이어그램을 그릴 수 없습니다. Node.js를 설치한 뒤 다시 실행하세요" >&2; exit 1
fi
case "$MODE" in
  macro) OPTS="-w 300 -s 2" ;;
  *) OPTS="-w 1200 -s 2" ;;
esac
mkdir -p "$(dirname "$OUT")"
if ! npx -y @mermaid-js/mermaid-cli -i "$IN" -o "$OUT" -b white $OPTS >/dev/null 2>&1; then
  echo "렌더 실패: $IN. Mermaid 문법을 확인하세요" >&2; exit 1
fi
echo "$OUT"
