#!/usr/bin/env bash
# product-spec 스킬을 wanteddev/claude-skills 마켓플레이스에 등록하거나 갱신하는 PR을 만든다
# 필요: git, gh(로그인된 상태), python3. wanteddev/claude-skills 쓰기 권한
# 실행: bash register-product-spec.sh
#       특정 브랜치를 올릴 때: SKILL_REF=spec-skill-v5.7 bash register-product-spec.sh
#       열려 있는 PR에 이어 올릴 때: PR_BRANCH=update-product-spec-20261119-003224 bash register-product-spec.sh
set -euo pipefail

MARKET_REPO="${MARKET_REPO:-wanteddev/claude-skills}"
SKILL_REPO="${SKILL_REPO:-suziejang-po/product-spec-skill}"
SKILL_REF="${SKILL_REF:-}"   # 올릴 브랜치. 비우면 main
PR_BRANCH="${PR_BRANCH:-}"   # 이미 열린 PR의 브랜치. 있으면 새 PR 대신 그 브랜치에 커밋을 더함
PLUGIN=product-spec
BRANCH="update-${PLUGIN}-$(date +%Y%m%d-%H%M%S)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "1/5 레포 내려받기"
gh repo clone "$MARKET_REPO" "$WORK/market" -- --depth 1 -q
# 개발 레포는 전체 기록을 받음 (아래 덮어쓰기 검사에 씀)
gh repo clone "$SKILL_REPO" "$WORK/skill" -- -q ${SKILL_REF:+--branch "$SKILL_REF"}
VERSION="$(grep -o 'skill-version: [0-9.]*' "$WORK/skill/.claude/skills/$PLUGIN/SKILL.md" | awk '{print $2}')"

# 덮어쓰기 검사: claude-skills에 있는 파일 내용이 개발 레포 기록에 한 번도 없으면,
# 누군가 claude-skills에서 직접 고친 것. 그대로 진행하면 그 수정이 사라지므로 멈춘다
check_foreign() {
  local CUR="$1/plugins/$PLUGIN/skills/$PLUGIN" where="$2" FOREIGN=""
  [ -d "$CUR" ] || return 0
  while IFS= read -r -d '' f; do
    git -C "$WORK/skill" cat-file -e "$(git hash-object "$f")" 2>/dev/null || FOREIGN="$FOREIGN\n   - ${f#$CUR/}"
  done < <(find "$CUR" -type f ! -name '*.bak*' ! -path '*__pycache__*' -print0)
  if [ -n "$FOREIGN" ]; then
    echo "멈춤: claude-skills ${where}에서 다른 사람이 고친 파일이 있어요. 덮어쓰면 그 수정이 사라져요"
    printf "$FOREIGN\n"
    echo "   최근 수정 기록:"
    gh api "repos/$MARKET_REPO/commits?path=plugins/$PLUGIN&sha=$where&per_page=5" --jq '.[] | "   - \(.commit.message | split("\n")[0]) (\(.commit.author.name), \(.commit.author.date[:10]))"' || true
    echo "   그 수정을 개발 레포에 먼저 합친 뒤 다시 실행하세요. 정말 덮어쓰려면 FORCE=1"
    [ "${FORCE:-}" = "1" ] || exit 1
  fi
}
check_foreign "$WORK/market" main
if [ -n "$PR_BRANCH" ]; then
  git -C "$WORK/market" fetch -q --depth 1 origin "$PR_BRANCH"
  git -C "$WORK/market" checkout -q -B "$PR_BRANCH" FETCH_HEAD
  check_foreign "$WORK/market" "$PR_BRANCH"
fi

echo "2/5 플러그인 폴더 만들기 (v$VERSION)"
DEST="$WORK/market/plugins/$PLUGIN"
rm -rf "$DEST"
mkdir -p "$DEST/.claude-plugin" "$DEST/skills"
cp -R "$WORK/skill/.claude/skills/$PLUGIN" "$DEST/skills/$PLUGIN"
find "$DEST" -name '*.bak*' -prune -exec rm -rf {} + 2>/dev/null || true
cat > "$DEST/.claude-plugin/plugin.json" <<EOF
{
  "name": "$PLUGIN",
  "description": "Wantedlab Product Spec(v5) 작성, 수정, Confluence 게시. 바뀌는 곳을 표시한 WDS 화면 프로토타입 생성",
  "version": "$VERSION",
  "author": { "name": "장수지" }
}
EOF

echo "3/5 marketplace.json에 항목 추가"
python3 - "$WORK/market/.claude-plugin/marketplace.json" "$PLUGIN" "$VERSION" <<'PY'
import json, sys, re
path, name, version = sys.argv[1:4]
data = json.load(open(path, encoding="utf-8"))
plugins = data.setdefault("plugins", [])
# 이미 있는 항목의 source 모양을 따라 씀 (./plugins/x 또는 pluginRoot 기준 x)
source = f"./plugins/{name}"
for p in plugins:
    s = p.get("source")
    if isinstance(s, str) and p.get("name") and p["name"] in s:
        source = s.replace(p["name"], name)
        break
entry = {
    "name": name,
    "description": "Wantedlab Product Spec(v5) 작성, 수정, Confluence 게시. 바뀌는 곳을 표시한 WDS 화면 프로토타입 생성",
    "version": version,
    "source": source,
}
for i, p in enumerate(plugins):
    if p.get("name") == name:
        plugins[i] = {**p, **entry}
        break
else:
    plugins.append(entry)
json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(path, "a", encoding="utf-8").write("\n")
print(f"   source: {source}")
PY

echo "4/5 검사"
if claude plugin validate "$WORK/market" >/dev/null 2>&1; then echo "   claude plugin validate 통과"
elif command -v claude >/dev/null; then claude plugin validate "$WORK/market"; exit 1
else echo "   claude CLI가 없어 validate는 건너뜀"; fi

cd "$WORK/market"
if [ -n "$PR_BRANCH" ]; then
  echo "5/5 열린 PR 브랜치($PR_BRANCH)에 커밋 더하기"
  git add -A
  if git diff --cached --quiet; then echo "   바뀐 내용이 없음"; exit 0; fi
  git commit -q -m "fix: product-spec v$VERSION 리뷰 반영"
  git push -q origin "HEAD:$PR_BRANCH"
  gh pr view "$PR_BRANCH" --repo "$MARKET_REPO" --json url --jq .url
  exit 0
fi
echo "5/5 브랜치 올리고 PR 만들기"
git checkout -q -b "$BRANCH"
git add -A
if git diff --cached --quiet; then echo "   바뀐 내용이 없어 PR을 만들지 않음"; exit 0; fi
git commit -q -m "feat: product-spec v$VERSION"
git push -q -u origin "$BRANCH"
MARKET_NAME="$(python3 -c "import json;print(json.load(open('.claude-plugin/marketplace.json'))['name'])")"
gh pr create --repo "$MARKET_REPO" --head "$BRANCH" \
  --title "feat: product-spec v$VERSION" \
  --body "## 변경
- \`plugins/$PLUGIN\`을 v${VERSION}으로 갱신
- 개발 레포: $SKILL_REPO

## 설치
\`\`\`
/plugin marketplace add $MARKET_REPO
/plugin install $PLUGIN@$MARKET_NAME
\`\`\`"
