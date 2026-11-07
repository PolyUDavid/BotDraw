#!/usr/bin/env python3
"""Runnable quality-sync commands. Standard library plus the sibling modules.

`selftest` runs the synthetic primitive suite only. A passing selftest does not
make any user figure, native PowerPoint file, or Blender scene PASS.

Optional, not required for selftest:
  pdffonts (poppler-utils), Pillow, rapidocr_onnxruntime, LibreOffice, Blender.
Missing optional tools stay UNKNOWN. They are not font or render proof.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _print(payload) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_selftest(_args: argparse.Namespace) -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_quality_primitives", "-v"],
        cwd=str(REPO),
        check=False,
    )
    return proc.returncode


def cmd_resolve(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    try:
        path = primitives.resolve_variant(
            args.root, args.tag, args.variant, supplementary=args.supplementary
        )
    except (FileNotFoundError, ValueError) as exc:
        _print({"ok": False, "error": str(exc), "fallback_used": False})
        return 1
    if Path(path).is_symlink():
        _print({"ok": False, "error": "symlink variant path refused", "fallback_used": False})
        return 1
    _print(
        {
            "ok": True,
            "path": str(path),
            "sha256": primitives.sha256(path),
            "variant": args.variant,
            "fallback_used": False,
        }
    )
    return 0


def cmd_pair(args: argparse.Namespace) -> int:
    spatial = _load("spatial_ocr_pairing")
    report = spatial.pairing_report(_read_json(args.source), _read_json(args.redraw))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _print(report)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    ledger = _read_json(args.ledger)
    report = primitives.audit_coverage(
        ledger["source_index"], ledger.get("reviewed") or {}, ledger.get("extra_math") or ()
    )
    _print(report)
    return 0


def cmd_math(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    left = primitives.math_signature(args.xml.read_text(encoding="utf-8"))
    payload = {"signature": repr(left)}
    if args.compare:
        right = primitives.math_signature(args.compare.read_text(encoding="utf-8"))
        payload["equal"] = left == right
        payload["note"] = "Equal signatures are not a correctness or completeness proof."
    _print(payload)
    return 0


def cmd_semantic(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    report = primitives.review_semantic(_read_json(args.report), _read_json(args.exceptions))
    _print(report)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    policy = _load("quality_policy")
    _print(policy.evaluate_status(_read_json(args.state)))
    return 0


def cmd_font(args: argparse.Namespace) -> int:
    policy = _load("quality_policy")
    evidence = None
    if args.span_evidence:
        evidence = _read_json(args.span_evidence)
    try:
        report = policy.font_evidence(
            args.pdf,
            requested_font=args.requested_font,
            fc_match_prediction=args.fc_match_prediction,
            span_face=args.span_face,
            span_evidence=evidence,
            native_application_review=args.native,
        )
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(report)
    return 0


def cmd_media(args: argparse.Namespace) -> int:
    policy = _load("quality_policy")
    try:
        report = policy.review_media_slot(_read_json(args.slot))
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(report)
    return 0 if report["identity_ok"] else 1


def cmd_vehicle(args: argparse.Namespace) -> int:
    policy = _load("quality_policy")
    try:
        report = policy.review_vehicle(_read_json(args.record))
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(report)
    return 0 if not report["problems"] else 1


def cmd_series(args: argparse.Namespace) -> int:
    policy = _load("quality_policy")
    try:
        report = policy.review_series(_read_json(args.series))
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(report)
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    files = [line.strip() for line in args.files.read_text(encoding="utf-8").splitlines() if line.strip()]
    try:
        manifest = primitives.freeze_snapshot(args.source, args.dest, files)
    except (ValueError, FileNotFoundError) as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _print({"ok": True, "manifest": str(args.manifest), "files": sorted(manifest)})
    return 0


def cmd_zip(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    manifest = _read_json(args.manifest)
    try:
        report = primitives.make_zip(
            args.snapshot,
            manifest,
            args.output,
            root_name=args.root_name,
            limit_bytes=args.limit_bytes,
        )
    except (ValueError, FileExistsError) as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(report)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    primitives = _load("quality_primitives")
    try:
        ok = primitives.verify_zip(args.archive, _read_json(args.manifest), root_name=args.root_name)
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print({"ok": bool(ok), "archive_sha256": primitives.sha256(args.archive), "remote_hash_verified": "UNKNOWN"})
    return 0


def cmd_wiring(_args: argparse.Namespace) -> int:
    wiring = _load("skill_wiring")
    errors = wiring.wiring_errors(REPO)
    _print({"ok": not errors, "errors": errors, "new_skills": list(wiring.NEW_SKILLS)})
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BotDraw quality-sync commands (synthetic proof is not a user-figure PASS).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    selftest = sub.add_parser("selftest", help="Run tests/test_quality_primitives.py. Not a figure PASS.")
    selftest.set_defaults(func=cmd_selftest)

    resolve = sub.add_parser("resolve-variant", help="Resolve out_A or out_B. Missing B does not fall back to A.")
    resolve.add_argument("--root", type=Path, required=True)
    resolve.add_argument("--tag", required=True)
    resolve.add_argument("--variant", required=True, choices=("A", "B"))
    resolve.add_argument("--supplementary", action="store_true")
    resolve.set_defaults(func=cmd_resolve)

    pair = sub.add_parser("pair-boxes", help="Global one-to-one pairing. Does not change t48u.")
    pair.add_argument("--source", type=Path, required=True)
    pair.add_argument("--redraw", type=Path, required=True)
    pair.add_argument("--out", type=Path)
    pair.set_defaults(func=cmd_pair)

    audit = sub.add_parser("audit-coverage", help="Coverage is not correctness.")
    audit.add_argument("--ledger", type=Path, required=True)
    audit.set_defaults(func=cmd_audit)

    math = sub.add_parser("math-signature", help="Compare a caller-selected math root, not a whole slide.")
    math.add_argument("--xml", type=Path, required=True)
    math.add_argument("--compare", type=Path)
    math.set_defaults(func=cmd_math)

    semantic = sub.add_parser("review-semantic", help="Keep the measured FAIL and record an object-level exception.")
    semantic.add_argument("--report", type=Path, required=True)
    semantic.add_argument("--exceptions", type=Path, required=True)
    semantic.set_defaults(func=cmd_semantic)

    status = sub.add_parser("status-policy", help="Six status axes and the stop/continue action.")
    status.add_argument("--state", type=Path, required=True)
    status.set_defaults(func=cmd_status)

    font = sub.add_parser("font-evidence", help="Read /BaseFont from a PDF. fc-match is not proof. pdffonts is optional.")
    font.add_argument("--pdf", type=Path, required=True)
    font.add_argument("--requested-font")
    font.add_argument("--fc-match-prediction")
    font.add_argument("--span-face")
    font.add_argument("--span-evidence", type=Path)
    font.add_argument("--native", default="NOT_PERFORMED")
    font.set_defaults(func=cmd_font)

    media = sub.add_parser("review-media", help="Check a media-slot identity record.")
    media.add_argument("--slot", type=Path, required=True)
    media.set_defaults(func=cmd_media)

    vehicle = sub.add_parser("review-vehicle", help="Check a vehicle geometry record. Does not launch Blender.")
    vehicle.add_argument("--record", type=Path, required=True)
    vehicle.set_defaults(func=cmd_vehicle)

    series = sub.add_parser("review-series", help="Check one data-provenance series.")
    series.add_argument("--series", type=Path, required=True)
    series.set_defaults(func=cmd_series)

    freeze = sub.add_parser("freeze", help="Whitelist snapshot into a clean directory.")
    freeze.add_argument("--source", type=Path, required=True)
    freeze.add_argument("--dest", type=Path, required=True)
    freeze.add_argument("--files", type=Path, required=True, help="Newline-separated relative PPTX paths")
    freeze.add_argument("--manifest", type=Path, required=True)
    freeze.set_defaults(func=cmd_freeze)

    zipper = sub.add_parser("make-zip", help="One ordinary ZIP from a frozen manifest.")
    zipper.add_argument("--snapshot", type=Path, required=True)
    zipper.add_argument("--manifest", type=Path, required=True)
    zipper.add_argument("--output", type=Path, required=True)
    zipper.add_argument("--root-name", default="ALL_FIGURES")
    zipper.add_argument("--limit-bytes", type=int, default=25_000_000)
    zipper.set_defaults(func=cmd_zip)

    verify = sub.add_parser("verify-zip", help="Check ZIP members, CRC, and bytes. Remote hash stays UNKNOWN.")
    verify.add_argument("--archive", type=Path, required=True)
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--root-name", default="ALL_FIGURES")
    verify.set_defaults(func=cmd_verify)

    wiring = sub.add_parser("wiring", help="Fail if a new skill is missing from the load path.")
    wiring.set_defaults(func=cmd_wiring)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
