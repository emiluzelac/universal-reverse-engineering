# Local analysis helpers

These Python 3.9+ utilities use only Python's standard library and run locally. They are passive; none executes a target executable or contacts the network.

They live in the skill's own `scripts/` folder, not in the project being inspected. The commands below use a shell variable `SKILL_DIR` that **you set yourself** to the absolute path of the folder holding `SKILL.md`; no host sets it for you. To find that path: Claude Code prints it as "Base directory for this skill" when the skill loads, Qwen Code exports it as `$QWEN_SKILL_ROOT`, and any other host should use the directory the skill was read from. `OUT` is a scratch folder outside the target, set the same way.

## `scripts/file_probe.py`

```bash
python3 "$SKILL_DIR/scripts/file_probe.py" /path/to/file
python3 "$SKILL_DIR/scripts/file_probe.py" /path/to/file --json
```

Reports file size, SHA-256, approximate entropy from a bounded sample, printable-byte ratio, and common file signatures, including a `#!` script line and an all-printable text heuristic. It does not output file contents or embedded strings. Entropy is **not** evidence of encryption by itself.

## `scripts/snapshot.py`

```bash
python3 "$SKILL_DIR/scripts/snapshot.py" capture /path/to/project --output "$OUT/re-before.json"
# Run a separate, user-approved experiment.
python3 "$SKILL_DIR/scripts/snapshot.py" capture /path/to/project --output "$OUT/re-after.json"
python3 "$SKILL_DIR/scripts/snapshot.py" diff "$OUT/re-before.json" "$OUT/re-after.json"
python3 "$SKILL_DIR/scripts/snapshot.py" diff "$OUT/re-before.json" "$OUT/re-after.json" --json
```

Creates a file manifest and compares two manifests by relative path, byte length, SHA-256, and modification time. Skips symlinks, common hidden/sensitive files, development folders, and agent configuration folders (`.claude`, `.codex`, `.agents`, `.qwen`). The skip applies to folders *inside* the scanned root; a root that itself lives under one of those names, such as this skill's own `examples/` folder, is scanned normally. Files over 64 MiB are represented with metadata without SHA-256. Read failures and truncation are recorded; their changes cannot be fully verified. Snapshots should be stored **outside** the folder being inspected. Diff results may include file and directory names: review before sharing.

## Limits

- No code execution, packet capture, binary disassembly, or network access is provided by the scripts.
- A manifest difference supports 'file changed,' not necessarily *why* it changed.
- Metadata and signature heuristics can be misleading; validate conclusions independently.
