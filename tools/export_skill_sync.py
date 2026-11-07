#!/usr/bin/env python3
"""Write skills_sync_export.zip for a parent bot UpdateSkill sync.

The zip contains SKILL.md files that differ from main, plus manifest.json.
It does not hash itself, and it does not include images, decks, or fonts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def changed_skill_files() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "main", "--", "skills"],
        cwd=str(REPO),
        check=True,
        capture_output=True,
        text=True,
    )
    names = []
    for line in proc.stdout.splitlines():
        relative = line.strip()
        if relative.endswith("/SKILL.md") or relative.endswith("SKILL.md"):
            names.append(relative)
    return sorted(set(names))


def frontmatter_name(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    block = text.split("---", 2)[1]
    for line in block.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def build(output: Path) -> dict:
    files = changed_skill_files()
    if not files:
        raise SystemExit("no SKILL.md files differ from main")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_files = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            path = REPO / relative
            data = path.read_bytes()
            if b"\x00" in data[:200]:
                raise SystemExit(f"refusing binary skill file {relative}")
            digest = hashlib.sha256(data).hexdigest()
            name = frontmatter_name(data.decode("utf-8"))
            manifest_files.append(
                {
                    "path": relative,
                    "sha256": digest,
                    "bytes": len(data),
                    "frontmatter_name": name,
                }
            )
            archive.writestr(relative, data)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        manifest = {
            "purpose": "UpdateSkill bundle of BotDraw SKILL.md files changed for quality sync",
            "base": "main",
            "head": head,
            "zip_is_not_self_hashed": True,
            "files": manifest_files,
        }
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export changed SKILL.md files and a hash manifest.")
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    manifest = build(args.output)
    print(json.dumps({"output": str(args.output), "files": len(manifest["files"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
