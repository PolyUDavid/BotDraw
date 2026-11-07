#!/usr/bin/env python3
"""Checks that quality-sync skills are on the real BotDraw load path."""
from __future__ import annotations

from pathlib import Path

NEW_SKILLS = (
    "paper-figure-source-symbol-audit",
    "paper-figure-font-renderer-proof",
    "paper-figure-spatial-ocr-pairing",
    "paper-figure-semantic-overlap-exceptions",
    "paper-figure-data-provenance",
    "paper-figure-unified-delivery",
)

# Presence, not order. README's folder table is alphabetical.
PRESENCE_FILES = (
    "skills/botdraw/SKILL.md",
    "skills/paper-figure-quality-merge/SKILL.md",
    "skills/paper-figure-onboard-selftest/SKILL.md",
    "README.md",
    "INSTALL.md",
    "docs/MASTER_PROMPT_zh.md",
    "docs/OVERVIEW.md",
)

# These documents are the load path a new environment actually follows.
ORDER_FILES = (
    "skills/botdraw/SKILL.md",
    "skills/paper-figure-quality-merge/SKILL.md",
    "docs/MASTER_PROMPT_zh.md",
    "docs/OVERVIEW.md",
)

LOAD_ORDER = (
    "paper-figure-onboard-selftest",
    "botdraw",
    "paper-figure-quality-merge",
    "paper-figure-data-provenance",
    "paper-figure-gold-bar-calibration",
    "paper-figure-media-slot-harmony",
    "paper-figure-fig01-gold-bar",
    "paper-figure-full-omml",
    "paper-figure-source-symbol-audit",
    "paper-figure-arrow-proportion",
    "paper-figure-scene-ui",
    "paper-figure-illustrator-layer-trace",
    "paper-figure-type-calibration",
    "paper-figure-text-layout-clearance",
    "paper-figure-font-renderer-proof",
    "paper-figure-layout-distribution",
    "paper-figure-semantic-overlap-exceptions",
    "paper-figure-spatial-ocr-pairing",
    "paper-figure-layout-gates",
    "paper-figure-layout-gates-2",
    "paper-figure-hierarchical-measure",
    "paper-figure-dense-region-pipeline",
    "paper-figure-indistinguishable-gate",
    "paper-figure-a-ppt",
    "paper-figure-b-blender",
    "paper-figure-unified-delivery",
)

HARD_STANDARDS = (
    "真 OMML",
    "小尾巴",
    "gold_bars",
    "paper-figure-illustrator-layer-trace",
)


def _read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    return path.read_text(encoding="utf-8")


def wiring_errors(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    for slug in NEW_SKILLS:
        skill = root / "skills" / slug / "SKILL.md"
        if not skill.is_file():
            errors.append(f"missing skills/{slug}/SKILL.md")
            continue
        text = skill.read_text(encoding="utf-8")
        if f"name: {slug}" not in text.split("---", 2)[1]:
            errors.append(f"frontmatter name mismatch for {slug}")
    for relative in PRESENCE_FILES:
        try:
            text = _read(root, relative)
        except FileNotFoundError:
            errors.append(f"missing {relative}")
            continue
        for slug in NEW_SKILLS:
            if slug not in text:
                errors.append(f"{relative} does not reference {slug}")
    for relative in ORDER_FILES:
        try:
            text = _read(root, relative)
        except FileNotFoundError:
            continue
        marker = "<!-- botdraw-load-order -->"
        start = text.find(marker)
        if start < 0:
            errors.append(f"{relative} missing {marker}")
            continue
        haystack = text[start:]
        cursor = -1
        for slug in LOAD_ORDER:
            found = haystack.find(slug, cursor + 1)
            if found < 0:
                errors.append(f"{relative} lost load-order slug {slug}")
                break
            cursor = found
    try:
        botdraw = _read(root, "skills/botdraw/SKILL.md")
    except FileNotFoundError:
        botdraw = ""
    for needle in HARD_STANDARDS:
        if needle not in botdraw:
            errors.append(f"botdraw lost hard standard {needle}")
    gates2 = root / "skills" / "paper-figure-layout-gates-2" / "SKILL.md"
    if gates2.is_file():
        front = gates2.read_text(encoding="utf-8").split("---", 2)[1]
        if "name: paper-figure-layout-gates\n" not in front and "name: paper-figure-layout-gates\r\n" not in front:
            errors.append("layout-gates-2 YAML name changed; keep loading it by folder path")
    else:
        errors.append("missing skills/paper-figure-layout-gates-2/SKILL.md")
    return errors
