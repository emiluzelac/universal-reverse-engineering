#!/usr/bin/env python3
"""Passive fingerprint of one local file. Does not execute or upload content."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

SAMPLE_LIMIT = 1024 * 1024
CHUNK = 1024 * 1024


def file_signature(header: bytes) -> str:
    magic = [
        (b"\x89PNG\r\n\x1a\n", "PNG image"),
        (b"%PDF-", "PDF document"),
        (b"PK\x03\x04", "ZIP-based archive/container"),
        (b"PK\x05\x06", "empty ZIP archive"),
        (b"\x7fELF", "ELF executable/container"),
        (b"MZ", "DOS/PE-family executable (unverified)"),
        (b"\x1f\x8b", "gzip stream"),
        (b"\xff\xd8\xff", "JPEG image"),
        (b"GIF87a", "GIF image"),
        (b"GIF89a", "GIF image"),
        (b"SQLite format 3\x00", "SQLite database"),
        (b"\xca\xfe\xba\xbe", "Mach-O universal or Java class (ambiguous)"),
        (b"\xfe\xed\xfa\xce", "Mach-O 32-bit executable"),
        (b"\xfe\xed\xfa\xcf", "Mach-O 64-bit executable"),
        (b"\xcf\xfa\xed\xfe", "Mach-O 64-bit little-endian executable"),
        (b"\xce\xfa\xed\xfe", "Mach-O 32-bit little-endian executable"),
    ]
    for prefix, label in magic:
        if header.startswith(prefix):
            return label
    if len(header) >= 262 and header[257:262] == b"ustar":
        return "tar archive"
    if header.startswith(b"#!"):
        return "text script with a #! interpreter line"
    if header.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
        return "text with a Unicode byte-order mark"
    return "unknown (no recognized signature)"


def entropy(sample: bytes) -> float:
    if not sample:
        return 0.0
    counts = Counter(sample)
    n = len(sample)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def _guess(sample: bytes, printable_count: int) -> str:
    guess = file_signature(sample[:512])
    if guess.startswith("unknown") and sample and printable_count / len(sample) >= 0.95:
        return "plain text (all printable bytes, heuristic)"
    return guess


def probe(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError("Refusing symlink; provide a direct file path")
    if not path.is_file():
        raise ValueError("Not a regular file")
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        sample = fh.read(SAMPLE_LIMIT)
        sha.update(sample)
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            sha.update(block)
    size = path.stat().st_size
    printable_count = sum(b in (9, 10, 13) or 32 <= b <= 126 for b in sample)
    return {
        "file_name": path.name,
        "size_bytes": size,
        "sha256": sha.hexdigest(),
        "signature_guess": _guess(sample, printable_count),
        "sampled_bytes": len(sample),
        "sample_entropy_bits_per_byte": round(entropy(sample), 3),
        "sample_printable_byte_fraction": round(printable_count / len(sample), 3) if sample else None,
        "caution": "Signatures are heuristic; entropy is not proof of encryption or compression; no content executed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Local file to inspect without executing")
    parser.add_argument("--json", action="store_true", help="Output one JSON object")
    args = parser.parse_args()
    try:
        result = probe(Path(args.file))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
