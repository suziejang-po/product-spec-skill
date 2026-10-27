#!/usr/bin/env bash
# product-spec 스킬을 wanteddev/claude-skills 마켓플레이스에 등록하는 PR을 만든다
# 필요: git, gh(로그인된 상태), python3. wanteddev/claude-skills 쓰기 권한
# 실행: bash register-product-spec.sh
set -euo pipefail

MARKET_REPO="${MARKET_REPO:-wanteddev/claude-skills}"
SKILL_REPO="${SKILL_REPO:-suziejang-po/product-spec-skill}"
PLUGIN=product-spec
BRANCH="update-${PLUGIN}-$(date +%Y%m%d-%H%M%S)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "1/5 레포 내려받기"
gh repo clone "$MARKET_REPO" "$WORK/market" -- --depth 1 -q
gh repo clone "$SKILL_REPO" "$WORK/skill" -- --depth 1 -q
VERSION="$(grep -o 'skill-version: [0-9.]*' "$WORK/skill/.claude/skills/$PLUGIN/SKILL.md" | awk '{print $2}')"

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

echo "5/5 브랜치 올리고 PR 만들기"
cd "$WORK/market"
git checkout -q -b "$BRANCH"
git add -A
git commit -q -m "feat: product-spec 플러그인 추가 (v$VERSION)"
git push -q -u origin "$BRANCH"
MARKET_NAME="$(python3 -c "import json;print(json.load(open('.claude-plugin/marketplace.json'))['name'])")"
gh pr create --repo "$MARKET_REPO" --head "$BRANCH" \
  --title "feat: product-spec 플러그인 추가 (v$VERSION)" \
  --body "## 추가
- \`plugins/$PLUGIN\`: Product Spec 작성, 수정, Confluence 게시 스킬 (v$VERSION)
- 원본: https://github.com/$SKILL_REPO (공개 레포는 마켓플레이스 source로 못 써서 이 레포에 복사함)

## 설치
\`\`\`
/plugin marketplace add $MARKET_REPO
/plugin install $PLUGIN@$MARKET_NAME
\`\`\`"
