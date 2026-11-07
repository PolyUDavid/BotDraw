#!/usr/bin/env python3
"""Status axes, stop/continue rules, and evidence validators.

Synthetic records only. A green validator is not a user-figure PASS, a native
PowerPoint review, or a Blender render.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

AXES = (
    "measurement",
    "source_review",
    "visual_review",
    "owner_acceptance",
    "native_application_review",
    "delivery_integrity",
)

_REVIEW = {"PASS", "FAIL", "UNKNOWN", "NOT_PERFORMED"}
_BASEFONT = re.compile(rb"/BaseFont\s*/([A-Za-z0-9+_.-]+)")


def _require_axes(state: dict) -> None:
    missing = [name for name in AXES if name not in state]
    if missing:
        raise ValueError("missing status axes: " + ",".join(missing))
    measurement = state["measurement"]
    if not isinstance(measurement, dict) or "pass" not in measurement or "report_sha256" not in measurement:
        raise ValueError("measurement needs pass and report_sha256")
    if not isinstance(measurement["pass"], bool):
        raise ValueError("measurement.pass must be boolean")
    owner = state["owner_acceptance"]
    if not isinstance(owner, dict) or "accepted" not in owner or "scope" not in owner:
        raise ValueError("owner_acceptance needs accepted and scope")
    for name in ("source_review", "visual_review", "native_application_review", "delivery_integrity"):
        if state[name] not in _REVIEW:
            raise ValueError(f"{name} must be one of {sorted(_REVIEW)}")


def evaluate_status(state: dict) -> dict:
    """Keep measurement, review, acceptance, native replay, and delivery apart.

    owner_acceptance never flips measurement. A historical FAIL is not rewritten
    here. Same-class retries stop when the gate version is unchanged.
    """
    _require_axes(state)
    measurement = state["measurement"]
    measured_pass = measurement["pass"]
    owner = state["owner_acceptance"]
    native = state["native_application_review"]
    checks = {
        "L0_tool_logic": "NOT_USER_FIGURE_PROOF",
        "L1_measurement": measured_pass,
        "L2_source_review": state["source_review"],
        "L3_visual_review": state["visual_review"],
        "L4_owner_acceptance": {"accepted": bool(owner["accepted"]), "scope": owner["scope"]},
        "L5_native_application_review": native,
        "L6_delivery_integrity": state["delivery_integrity"],
    }
    base = {
        "measured_pass": measured_pass,
        "owner_acceptance_flips_measurement": False,
        "historical_report_sha256": measurement["report_sha256"],
        "checks": checks,
        "native_pass": native == "PASS",
    }
    attempts = int(state.get("same_class_attempts") or 0)
    limit = int(state.get("same_class_limit") or 3)
    same_class = state.get("defect_class") == state.get("previous_defect_class")
    same_version = state.get("gate_version") == state.get("previous_gate_version")
    if state.get("rewrite_historical_measurement") or (
        measured_pass is False and state.get("claim_measurement_pass")
    ):
        action = "REJECT_REWRITE"
    elif state.get("tool_logic_only") and state.get("claim_user_figure_pass"):
        action = "REJECT_FALSE_PASS"
    elif state.get("claim_native_pass") and native in {"UNKNOWN", "NOT_PERFORMED"}:
        action = "REJECT_NATIVE_CLAIM"
    elif state["delivery_integrity"] == "FAIL":
        action = "STOP_DELIVERY"
    elif (
        measured_pass is False
        and attempts >= limit
        and same_class
        and same_version
        and state.get("defect_class") not in (None, "", "none")
    ):
        action = "STOP_SAME_CLASS"
    elif owner["accepted"] and measured_pass is False and not state.get("request_new_technical_fix"):
        action = "STOP_ACCEPTED_STYLE_KEEP_FAIL"
    elif state.get("request_new_technical_fix") and state.get("defect_class") != state.get("previous_defect_class"):
        action = "CONTINUE_NEW_CLASS"
    elif (
        measured_pass is False
        and state.get("previous_gate_version")
        and state.get("gate_version") != state.get("previous_gate_version")
    ):
        action = "CONTINUE_RETEST_NEW_VERSION"
    elif measured_pass is False and attempts < limit:
        action = "CONTINUE_REPAIR"
    elif (
        measured_pass is True
        and state["source_review"] == "PASS"
        and state["visual_review"] == "PASS"
        and state["delivery_integrity"] == "PASS"
        and native == "PASS"
    ):
        action = "CONTINUE_DELIVER"
    elif (
        measured_pass is True
        and state["source_review"] == "PASS"
        and state["visual_review"] == "PASS"
        and state["delivery_integrity"] == "PASS"
    ):
        action = "CONTINUE_DELIVER_NATIVE_UNKNOWN"
    else:
        action = "STOP_INCOMPLETE"
    base["action"] = action
    base["same_class_limit"] = limit
    return base


def same_class_stop(records: list[dict], *, limit: int = 3) -> bool:
    """True when the last `limit` failing rounds share class and gate version."""
    if limit < 1 or len(records) < limit:
        return False
    tail = records[-limit:]

    def key(row: dict) -> tuple:
        return (row.get("defect_class"), row.get("gate_version"))

    if any(row.get("defect_class") in (None, "", "none") for row in tail):
        return False
    return len({key(row) for row in tail}) == 1


def commit_immutable_report(directory: Path, stem: str, payload: dict) -> Path:
    """Write a new content-addressed report. Never replace an existing file."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    legacy = directory / f"{stem}.json"
    legacy_bytes = legacy.read_bytes() if legacy.exists() else None
    stamped = dict(payload)
    stamped["does_not_replace_historical"] = True
    stamped["historical_pass_flipped"] = False
    body = json.dumps(stamped, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    dest = directory / f"{stem}.{digest[:16]}.json"
    if dest.exists():
        if dest.read_bytes() != body:
            raise ValueError("content-addressed report collision")
        return dest
    dest.write_bytes(body)
    if legacy_bytes is not None and legacy.read_bytes() != legacy_bytes:
        raise ValueError("historical report bytes changed")
    return dest


def refuse_inplace_flip(path: Path, payload: dict) -> None:
    """Historical FAIL files stay FAIL. A later PASS is a different file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    old = json.loads(path.read_text(encoding="utf-8"))
    if old.get("pass") is False and payload.get("pass") is True:
        raise ValueError("refusing to flip a historical FAIL to PASS in place")
    raise ValueError("refusing in-place rewrite of a historical report")


def scan_pdf_basefonts(pdf: Path) -> dict:
    """Read /BaseFont names from the PDF bytes. This is not glyph-span attribution."""
    pdf = Path(pdf)
    data = pdf.read_bytes()
    names = []
    for raw in _BASEFONT.findall(data):
        text = raw.decode("ascii", "replace")
        if text not in names:
            names.append(text)
    return {
        "pdf_sha256": hashlib.sha256(data).hexdigest(),
        "pdf_bytes": len(data),
        "pdf_basefonts": names,
        "span_attribution": "UNKNOWN",
        "fc_match_is_pdf_proof": False,
    }


def optional_pdffonts(pdf: Path, *, which=shutil.which, runner=None) -> dict:
    """Run pdffonts when it is installed. Missing tool stays an optional UNKNOWN."""
    exe = which("pdffonts")
    if not exe:
        return {
            "tool": "pdffonts",
            "status": "OPTIONAL_DEPENDENCY_MISSING",
            "proves_span": False,
            "note": "Install poppler-utils to list embedded fonts. Absence is UNKNOWN, not a face match.",
        }
    if runner is None:
        proc = subprocess.run([exe, str(pdf)], capture_output=True, text=True, timeout=30, check=False)
        stdout, exit_code = proc.stdout, proc.returncode
    else:
        stdout, exit_code = runner(exe, pdf)
    return {
        "tool": "pdffonts",
        "status": "RAN",
        "exit": exit_code,
        "stdout": stdout,
        "proves_span": False,
        "note": "A page font list is not attribution of one Greek glyph or span.",
    }


def font_evidence(
    pdf: Path,
    *,
    requested_font: str | None = None,
    fc_match_prediction: str | None = None,
    span_face: str | None = None,
    span_evidence: dict | None = None,
    native_application_review: str = "NOT_PERFORMED",
) -> dict:
    """Separate a fontconfig prediction from fonts actually named in this PDF."""
    if native_application_review not in _REVIEW:
        raise ValueError("native_application_review is not a review status")
    if span_evidence and span_evidence.get("source") in {"fc-match", "fc_match"}:
        raise ValueError("fc-match is a prediction, not span proof")
    if span_face and not span_evidence:
        raise ValueError("span face requires evidence from the PDF, not a fontconfig prediction")
    scanned = scan_pdf_basefonts(pdf)
    record = {
        "requested_font": requested_font,
        "fc_match_prediction": fc_match_prediction,
        "installed_font_file": None,
        "renderer_pdf_font": scanned["pdf_basefonts"],
        "glyph_span_actual_style": span_evidence if span_evidence else None,
        "actual_pdf_span_face": span_face if span_evidence else None,
        "pdf_sha256": scanned["pdf_sha256"],
        "pdf_basefonts": scanned["pdf_basefonts"],
        "span_attribution": "RECORDED" if span_evidence else "UNKNOWN",
        "fc_match_is_pdf_proof": False,
        "native_application_review": native_application_review,
        "pdffonts": optional_pdffonts(pdf),
    }
    return record


def review_media_slot(slot: dict) -> dict:
    required = (
        "slot_id",
        "authorized_use",
        "source_rel_id",
        "source_sha256",
        "scene_label",
        "fit",
        "src_rect_checked",
        "layer_order",
    )
    missing = [key for key in required if key not in slot]
    if missing:
        raise ValueError("missing media fields: " + ",".join(missing))
    problems: list[str] = []
    if slot["fit"] != "uniform_contain":
        problems.append("fit must be uniform_contain")
    if slot.get("identity_status") == "MISMATCH" and slot.get("replaced_actual_media") is not True:
        problems.append("mismatch requires actual media replacement")
    if slot.get("whole_slide_raster") is True:
        problems.append("whole-slide raster cannot stand in for editable A")
    if slot.get("alias_evidence") and slot.get("exact_experiment_run_known") is True and not slot.get("run_evidence"):
        problems.append("alias is not an experiment run")
    if slot.get("src_rect_checked") is not True:
        problems.append("srcRect crop must be checked")
    return {
        "slot_id": slot["slot_id"],
        "problems": problems,
        "identity_ok": not problems,
        "exact_experiment_run": "EVIDENCED" if slot.get("run_evidence") else "UNKNOWN",
        "foreground_occlusion_is_crop": False,
        "source_sha256": slot["source_sha256"],
    }


def review_vehicle(record: dict) -> dict:
    required = (
        "projection_class",
        "aspect_wh",
        "shoulder_tail",
        "wheelbase",
        "window_boundary",
        "lamp",
        "same_scale_sbs",
        "axis_frame",
        "blend_reopened",
        "freestyle_actual",
        "samples",
        "order",
    )
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError("missing vehicle fields: " + ",".join(missing))
    problems: list[str] = []
    if record.get("style_proof") == "samples_only":
        problems.append("sample count is not a shape proof")
    if record.get("confirmation_fully_met") is True and record.get("freestyle_actual") is not True:
        problems.append("template name is not an actual Freestyle value")
    if record.get("wheelbase_fix_axis") == "local" and record.get("object_already_rotated") is True:
        problems.append("local axis scale is not a world wheelbase fix")
    if record.get("same_scale_sbs") is not True:
        problems.append("fixed-scale icon-only SBS required")
    if record.get("blend_reopened") is not True:
        problems.append("reopen the saved blend and record actual values")
    if record.get("order") != "geometry-material-light":
        problems.append("measure geometry before material and light")
    return {
        "projection_class": record["projection_class"],
        "problems": problems,
        "geometry_recorded": True,
        "freestyle_actual": record["freestyle_actual"],
        "confirmation_fully_met": record.get("freestyle_actual") is True and not problems,
        "samples_are_style_proof": False,
    }


def review_series(series: dict, *, primary_dirs: tuple[str, ...] = ("out_A", "out_B")) -> dict:
    kind = series.get("kind")
    if kind not in {"raw", "printed", "image_geometry", "synthetic", "verified"}:
        raise ValueError("series kind must be raw, printed, image_geometry, synthetic, or verified")
    if kind == "image_geometry" and series.get("claims_recovered_experiment"):
        raise ValueError("pixel geometry is not a recovered experiment")
    if series.get("mix_verified_into_primary"):
        raise ValueError("do not mix a verified alternative into the primary trace")
    path = str(series.get("path") or "")
    if kind == "verified":
        parts = PurePosixPath(path).parts if path else ()
        if not parts or parts[0] in primary_dirs or ".." in parts:
            raise ValueError("verified alternative must sit outside the primary out_A/out_B delivery")
        if series.get("label") != "VERIFIED_ALTERNATIVE":
            raise ValueError("verified series needs the VERIFIED_ALTERNATIVE label")
    if series.get("conflict") and series.get("primary_label") != "NON_VERIFIED_SOURCE_TRACE":
        raise ValueError("a conflicted primary trace must be labeled NON_VERIFIED_SOURCE_TRACE")
    experimental = "NOT_CLAIMED" if kind == "image_geometry" else series.get("experimental_sequence", "UNKNOWN")
    return {
        "kind": kind,
        "experimental_sequence": experimental,
        "primary_label": series.get("primary_label"),
        "mixed_into_primary": False,
    }
