#!/usr/bin/env python3
"""Versioned spatial OCR pairing. Does not change the t48u historical gate.

Historical `ocr_font_overlap_gate.py` still strips non-alphanumeric characters,
picks a nearest string per source, and can ignore unmatched lines. This report
is a separate artifact. `pairing_coverage_complete` is not a measured visual PASS.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path


def _primitives():
    path = Path(__file__).resolve().parent / "quality_primitives.py"
    spec = importlib.util.spec_from_file_location("quality_primitives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def orientation_from_quad(points) -> str:
    """Reading direction from a quadrilateral. Ambiguous angles stay unknown."""
    if not points or len(points) < 2:
        return "unknown"

    def length(p, q) -> float:
        return math.hypot(float(q[0]) - float(p[0]), float(q[1]) - float(p[1]))

    if len(points) >= 3 and length(points[1], points[2]) > length(points[0], points[1]):
        start, end = points[1], points[2]
    else:
        start, end = points[0], points[1]
    dx = float(end[0]) - float(start[0])
    dy = float(end[1]) - float(start[1])
    if dx == 0 and dy == 0:
        return "unknown"
    angle = abs(math.degrees(math.atan2(dy, dx))) % 180
    if angle <= 20 or angle >= 160:
        return "h"
    if 70 <= angle <= 110:
        return "v"
    return "unknown"


def ink_height_along_normal(box: dict):
    """Glyph size along the normal of the reading direction.

    An axis-aligned box only approximates this. Unknown direction returns no height.
    Vertical text uses the short side (AABB width), not the line length.
    """
    orientation = box.get("orientation")
    if orientation == "h":
        return box.get("h"), "normal_to_horizontal_line"
    if orientation == "v":
        return box.get("w"), "normal_to_vertical_line"
    return None, "aabb_only_approximate"


def gate_box_to_pairing(box: dict, index: int, prefix: str, *, norm_w: float = 1672.0) -> dict:
    """Map one OCR record into the shared width-normalized frame.

    Missing orientation stays unknown. It is not treated as horizontal.
    Zone defaults to unspecified for every box so a missing panel id cannot
    invent a match across panels the caller actually labeled.
    """
    if "x" not in box or "y" not in box:
        raise ValueError("OCR box needs x and y in the shared normalized canvas")
    orientation = box.get("orientation") or "unknown"
    if orientation not in {"h", "v", "unknown"}:
        orientation = "unknown"
    return {
        "id": box.get("id") or f"{prefix}{index}",
        "text": box.get("text") if "text" in box else (box.get("t") or ""),
        "x": float(box["x"]) / norm_w if box.get("normalized") is not True else float(box["x"]),
        "y": float(box["y"]) / norm_w if box.get("normalized") is not True else float(box["y"]),
        "orientation": orientation,
        "zone": box.get("zone") or "unspecified",
    }


def pairing_report(source: list[dict], redraw: list[dict], **kwargs) -> dict:
    primitives = _primitives()
    paired = primitives.pair_boxes(source, redraw, **kwargs)
    unmatched_source = paired["unmatched_source"]
    unmatched_redraw = paired["unmatched_redraw"]
    coverage = not unmatched_source and not unmatched_redraw
    return {
        "version": "spatial-ocr-pairing-v1",
        "historical_gate_version_untouched": "2026-10-28-t48u",
        "changes_historical_pass": False,
        "claims_measured_visual_pass": False,
        "visual_or_source_pass_inferred": False,
        "source_total": paired["source_total"],
        "redraw_total": paired["redraw_total"],
        "pairs": paired["pairs"],
        "unmatched_source": unmatched_source,
        "unmatched_redraw": unmatched_redraw,
        "rejected": paired["rejected"],
        "excluded": [],
        "pairing_coverage_complete": coverage and paired["source_total"] == len(paired["pairs"]),
        "relation_symbols_preserved": True,
    }


def emit_from_gate_boxes(orig: list[dict], redraw: list[dict], *, norm_w: float = 1672.0) -> dict:
    source = [gate_box_to_pairing(box, i, "s", norm_w=norm_w) for i, box in enumerate(orig)]
    candidate = [gate_box_to_pairing(box, i, "r", norm_w=norm_w) for i, box in enumerate(redraw)]
    report = pairing_report(source, candidate)
    report["coordinate_frame"] = "width_normalized_shared_canvas"
    report["local_fit_used"] = False
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Spatial one-to-one OCR pairing (not a t48u PASS).")
    parser.add_argument("--source", type=Path, required=True, help="JSON list of source boxes")
    parser.add_argument("--redraw", type=Path, required=True, help="JSON list of redraw boxes")
    parser.add_argument("--out", type=Path, help="Write the report JSON here")
    args = parser.parse_args(argv)
    source = json.loads(args.source.read_text(encoding="utf-8"))
    redraw = json.loads(args.redraw.read_text(encoding="utf-8"))
    prepared_s = []
    prepared_r = []
    for index, box in enumerate(source):
        item = dict(box)
        item.setdefault("normalized", True)
        prepared_s.append(gate_box_to_pairing(item, index, "s"))
    for index, box in enumerate(redraw):
        item = dict(box)
        item.setdefault("normalized", True)
        prepared_r.append(gate_box_to_pairing(item, index, "r"))
    report = pairing_report(prepared_s, prepared_r)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
