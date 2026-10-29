#!/usr/bin/env bash
# Offline checks for the skill: Agent Skills validator (when installed), name/directory
# match, Python syntax, the two helpers against the bundled example, the example itself,
# and that every relative link in SKILL.md resolves.
# Usage: tests/smoke.sh [skill-dir]   default: ./reverse-engineering or ./skills/reverse-engineering
set -euo pipefail
cd "$(dirname "$0")/.."
SKILL="${1:-}"
if [ -z "$SKILL" ]; then
  for c in reverse-engineering skills/reverse-engineering; do
    if [ -f "$c/SKILL.md" ]; then SKILL=$c; break; fi
  done
fi
[ -n "$SKILL" ] && [ -f "$SKILL/SKILL.md" ] || { echo "smoke.sh: no SKILL.md found; pass the skill directory" >&2; exit 1; }
SKILL=${SKILL%/}
echo "skill: $SKILL"

# 1. Agent Skills validator (https://agentskills.io): pip install skills-ref
if command -v agentskills >/dev/null 2>&1; then agentskills validate "$SKILL"
elif command -v uvx >/dev/null 2>&1; then uvx --from skills-ref agentskills validate "$SKILL"
else echo "skip: validator not installed (pip install skills-ref)"; fi

# 2. frontmatter name must equal the directory name
name=$(sed -n 's/^name: *//p' "$SKILL/SKILL.md" | head -1)
[ "$name" = "$(basename "$SKILL")" ] || { echo "name '$name' does not match directory '$(basename "$SKILL")'" >&2; exit 1; }
echo "name ok: $name"

# 3. Python syntax, without writing bytecode into the skill folder
python3 -I - "$SKILL" <<'PY'
import ast, pathlib, sys
root = pathlib.Path(sys.argv[1])
files = sorted(root.glob("scripts/*.py")) + sorted(root.glob("examples/*.py"))
for f in files:
    ast.parse(f.read_text(encoding="utf-8"), str(f))
print("syntax ok:", ", ".join(str(f.relative_to(root)) for f in files))
PY

# 4. the helpers, run against the bundled example
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
python3 -I "$SKILL/scripts/file_probe.py" "$SKILL/examples/number_machine.py" --json > "$TMP/probe.json"
python3 -I - "$TMP/probe.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert "#!" in d["signature_guess"], d
assert len(d["sha256"]) == 64, d
print("file_probe ok:", d["signature_guess"])
PY
python3 -I "$SKILL/scripts/snapshot.py" capture "$SKILL/examples" --output "$TMP/before.json" >/dev/null
python3 -I "$SKILL/scripts/snapshot.py" capture "$SKILL/examples" --output "$TMP/after.json" >/dev/null
out=$(python3 -I "$SKILL/scripts/snapshot.py" diff "$TMP/before.json" "$TMP/after.json")
grep -q '^changed_content: 0$' <<<"$out" || { echo "snapshot diff unexpected:"; echo "$out"; exit 1; } >&2
echo "snapshot ok: capture twice, diff reports no content change"

# 5. the example runs and prints JSON; its rule is deliberately not asserted here
python3 -I "$SKILL/examples/number_machine.py" 5 | python3 -I -c 'import json,sys; d=json.load(sys.stdin); assert {"input","status"} <= set(d), d; print("example ok: keys", sorted(d))'
if python3 -I "$SKILL/examples/number_machine.py" abc >/dev/null 2>&1; then echo "example should reject a non-integer" >&2; exit 1; fi
echo "example ok: rejects non-integer input"

# 6. every relative link in SKILL.md points at a file that exists
python3 -I - "$SKILL" <<'PY'
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
text = (root / "SKILL.md").read_text(encoding="utf-8")
missing = [p for p in re.findall(r"\]\(([^)]+)\)", text)
           if not p.startswith(("http://", "https://", "#")) and not (root / p).exists()]
if missing:
    sys.exit(f"SKILL.md links to missing files: {missing}")
print("links ok")
PY
echo "smoke: all checks passed"
