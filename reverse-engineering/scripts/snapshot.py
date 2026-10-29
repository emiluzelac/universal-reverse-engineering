#!/usr/bin/env python3
"""Create and compare read-only local directory manifests. Python standard library only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    ".next", "dist", "build", ".cache", ".idea",
    ".qwen", ".claude", ".codex", ".agents"
}
IGNORE_FILES = {
    ".ds_store", "thumbs.db", ".env", ".npmrc", ".pypirc", ".netrc",
    "id_rsa", "id_ed25519", "known_hosts"
}
SENSITIVE_ENDINGS = (".pem", ".p12", ".pfx", ".key", ".asc", ".jks", ".keystore")
DEFAULT_MAX_HASH_MIB = 64
DEFAULT_MAX_FILES = 10000
CHUNK = 1024 * 1024


def secret_like(name: str) -> bool:
    lower = name.lower()
    return (lower in IGNORE_FILES or lower.startswith(".env.") or
            lower.endswith(SENSITIVE_ENDINGS) or
            lower in {"credentials.json", "service-account.json", "secrets.json"})


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def capture(root: Path, max_hash_bytes: int, max_files: int) -> dict:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Root must be a normal local directory (not a symlink)")
    root = root.resolve()
    files = {}
    warnings = []
    visited = 0
    truncated = False

    def on_error(err: OSError) -> None:
        warnings.append(f"Directory read error: {err}")

    for current, dirs, names in os.walk(root, topdown=True, followlinks=False, onerror=on_error):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS and
                         not (Path(current) / d).is_symlink() and not secret_like(d))
        for name in sorted(names):
            if secret_like(name):
                continue
            target = Path(current) / name
            if target.is_symlink() or not target.is_file():
                continue
            if visited >= max_files:
                truncated = True
                break
            visited += 1
            relative = target.relative_to(root).as_posix()
            try:
                stat = target.stat()
                size = stat.st_size
                record = {
                    "size_bytes": size,
                    "mtime_ns": stat.st_mtime_ns,
                    "sha256": hash_file(target) if size <= max_hash_bytes else None,
                }
                if size > max_hash_bytes:
                    record["note"] = "hash_skipped_file_too_large"
                files[relative] = record
            except OSError as exc:
                warnings.append(f"Unable to inspect {relative}: {type(exc).__name__}")
        if truncated:
            break
    return {
        "format": "reverse-engineering-snapshot-v1",
        "root": str(root),
        "max_hash_bytes": max_hash_bytes,
        "max_files": max_files,
        "file_count": len(files),
        "truncated": truncated,
        "warnings": warnings,
        "files": dict(sorted(files.items())),
    }


def compare(before: dict, after: dict) -> dict:
    if before.get("format") != "reverse-engineering-snapshot-v1" or after.get("format") != "reverse-engineering-snapshot-v1":
        raise ValueError("Expected two reverse-engineering-snapshot-v1 manifests")
    if before.get("root") != after.get("root"):
        raise ValueError("Manifests have different root paths; compare the same directory")
    left, right = before["files"], after["files"]
    added = sorted(right.keys() - left.keys())
    removed = sorted(left.keys() - right.keys())
    changed_content = []
    changed_metadata = []
    indeterminate = []
    for path in sorted(left.keys() & right.keys()):
        a, b = left[path], right[path]
        if a["size_bytes"] != b["size_bytes"]:
            changed_content.append(path)
        elif a["sha256"] is not None and b["sha256"] is not None:
            if a["sha256"] != b["sha256"]:
                changed_content.append(path)
            elif a["mtime_ns"] != b["mtime_ns"]:
                changed_metadata.append(path)
        elif a["mtime_ns"] != b["mtime_ns"]:
            indeterminate.append(path)
    return {
        "root": before["root"],
        "added": added,
        "removed": removed,
        "changed_content": changed_content,
        "changed_metadata_only": changed_metadata,
        "indeterminate_large_files": indeterminate,
        "limitations": [
            "Changes between captures are correlations, not proof of causation.",
            "A same-size file skipped for hashing may change without an updated mtime.",
            "Both manifests can omit hidden secrets, excluded folders, symlinks, and unreadable files.",
        ],
        "incomplete": bool(before.get("truncated") or after.get("truncated") or
                           before.get("warnings") or after.get("warnings")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cap = commands.add_parser("capture", help="Make a read-only manifest; output path must be outside root")
    cap.add_argument("directory")
    cap.add_argument("--output", required=True, help="Manifest JSON path outside scanned root")
    cap.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    cap.add_argument("--max-hash-mib", type=int, default=DEFAULT_MAX_HASH_MIB)
    dif = commands.add_parser("diff", help="Compare two manifest files")
    dif.add_argument("before")
    dif.add_argument("after")
    dif.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "capture":
            original_root = Path(args.directory).expanduser()
            root = original_root.resolve()
            if original_root.is_symlink():
                raise ValueError("Refusing symlink directory")
            output = Path(args.output).expanduser().resolve()
            if root == output or root in output.parents:
                raise ValueError("--output must be outside the scanned root")
            if args.max_files <= 0 or args.max_hash_mib < 0:
                raise ValueError("--max-files must be positive and --max-hash-mib must be nonnegative")
            result = capture(root, args.max_hash_mib * CHUNK, args.max_files)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"Saved {result['file_count']} file records to {output}")
            if result["truncated"] or result["warnings"]:
                print(f"WARNING: manifest may be incomplete; truncated={result['truncated']}, errors={len(result['warnings'])}")
        else:
            with open(args.before, encoding="utf-8") as fh:
                before = json.load(fh)
            with open(args.after, encoding="utf-8") as fh:
                after = json.load(fh)
            result = compare(before, after)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                for kind in ("added", "removed", "changed_content", "changed_metadata_only", "indeterminate_large_files"):
                    print(f"{kind}: {len(result[kind])}")
                    for path in result[kind][:100]:
                        print(f"  {path}")
                if result["incomplete"]:
                    print("WARNING: One or both manifests are incomplete")
                print("Caution: Changes do not prove what caused them.")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
