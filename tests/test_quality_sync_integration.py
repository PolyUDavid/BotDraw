"""Positive and negative checks for the quality-sync integration.

These tests use synthetic files only. A pass here is not a user-figure PASS.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
PY = sys.executable


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


POLICY = load("quality_policy")
SPATIAL = load("spatial_ocr_pairing")
WIRING = load("skill_wiring")
PRIMITIVES = load("quality_primitives")


def status(**overrides):
    base = {
        "measurement": {"pass": False, "report_sha256": "a" * 64},
        "source_review": "FAIL",
        "visual_review": "UNKNOWN",
        "owner_acceptance": {"accepted": False, "scope": ""},
        "native_application_review": "NOT_PERFORMED",
        "delivery_integrity": "UNKNOWN",
        "same_class_attempts": 1,
        "same_class_limit": 3,
        "defect_class": "relation",
        "previous_defect_class": "relation",
        "gate_version": "t48u",
        "previous_gate_version": "t48u",
        "tool_logic_only": False,
        "claim_user_figure_pass": False,
        "claim_native_pass": False,
        "claim_measurement_pass": False,
        "request_new_technical_fix": False,
        "rewrite_historical_measurement": False,
    }
    base.update(overrides)
    return base


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def run(args, *, env=None, cwd=None):
    return subprocess.run(
        [PY, *args],
        cwd=str(cwd or REPO),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def tiny_pptx(path: Path, payload: bytes = b"synthetic-container") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "ppt/presentation.xml",
            "<p:presentation xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'>"
            "<p:sldSz cx='12192000' cy='6858000'/></p:presentation>",
        )
        archive.writestr(
            "ppt/slides/slide1.xml",
            "<p:sld xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'></p:sld>",
        )
        archive.writestr("SYNTHETIC.txt", payload)


class WiringTests(unittest.TestCase):
    def test_real_repo_load_path_is_complete(self):
        self.assertEqual(WIRING.wiring_errors(REPO), [])

    def test_missing_skill_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = WIRING.wiring_errors(root)
        self.assertTrue(any("paper-figure-source-symbol-audit" in item for item in errors))

    def test_new_skills_do_not_carry_private_markers(self):
        banned = ("/home/box", "ConsensusRetNet", "drive.google", "kevin_figure_skills_pack", "@gmail")
        for slug in WIRING.NEW_SKILLS:
            text = (REPO / "skills" / slug / "SKILL.md").read_text(encoding="utf-8")
            for marker in banned:
                self.assertNotIn(marker, text, slug)


class HistoricalOcrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        os.environ["FIG_ROOT"] = cls.tmp.name
        spec = importlib.util.spec_from_file_location("ocr_gate_under_test", TOOLS / "ocr_font_overlap_gate.py")
        cls.ocr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ocr)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_thresholds_and_alnum_strip_remain(self):
        self.assertEqual(self.ocr.IOU_FAIL, 0.08)
        self.assertEqual(self.ocr.H_MED_LO, 0.92)
        self.assertEqual(self.ocr.H_MED_HI, 1.22)
        self.assertIn("isalnum", inspect.getsource(self.ocr.norm))
        self.assertEqual(self.ocr.norm("value<limit"), self.ocr.norm("value≤limit"))

    def test_historical_pairing_can_reuse_one_candidate(self):
        source = [
            {"t": "value<limit", "c": 0.99, "h": 12, "x": 10, "y": 10},
            {"t": "value<limit", "c": 0.99, "h": 12, "x": 30, "y": 10},
        ]
        redraw = [{"t": "value≤limit", "c": 0.99, "h": 12, "x": 11, "y": 10}]
        _ratios, items, missed = self.ocr.pair_heights(source, redraw)
        self.assertEqual(len(items), 2)
        self.assertEqual(missed, [])


class SpatialTests(unittest.TestCase):
    def test_relation_and_duplicate_are_not_silently_resolved(self):
        report = SPATIAL.pairing_report(
            [
                {"id": "s1", "text": "value<limit", "x": 0.10, "y": 0.10, "orientation": "h", "zone": "p"},
                {"id": "s2", "text": "value<limit", "x": 0.12, "y": 0.10, "orientation": "h", "zone": "p"},
            ],
            [{"id": "r1", "text": "value≤limit", "x": 0.10, "y": 0.10, "orientation": "h", "zone": "p"}],
        )
        self.assertEqual(report["pairs"], [])
        self.assertEqual(report["unmatched_source"], ["s1", "s2"])
        self.assertFalse(report["pairing_coverage_complete"])
        self.assertFalse(report["claims_measured_visual_pass"])
        self.assertFalse(report["changes_historical_pass"])

    def test_matching_horizontal_pair_is_kept(self):
        report = SPATIAL.pairing_report(
            [{"id": "s", "text": "value<limit", "x": 0.2, "y": 0.2, "orientation": "h", "zone": "p"}],
            [{"id": "r", "text": "value<limit", "x": 0.21, "y": 0.2, "orientation": "h", "zone": "p"}],
        )
        self.assertEqual(report["pairs"][0]["source"], "s")
        self.assertTrue(report["pairing_coverage_complete"])
        self.assertFalse(report["claims_measured_visual_pass"])

    def test_unknown_orientation_and_vertical_height(self):
        self.assertEqual(SPATIAL.orientation_from_quad([[0, 0], [10, 0], [10, 2], [0, 2]]), "h")
        self.assertEqual(SPATIAL.orientation_from_quad([[0, 0], [0, 10], [2, 10], [2, 0]]), "v")
        self.assertEqual(SPATIAL.orientation_from_quad([[0, 0], [4, 4]]), "unknown")
        height, kind = SPATIAL.ink_height_along_normal({"orientation": "v", "h": 40, "w": 8})
        self.assertEqual((height, kind), (8, "normal_to_vertical_line"))
        self.assertEqual(SPATIAL.ink_height_along_normal({"orientation": "unknown", "h": 40, "w": 8})[0], None)

    def test_cli_writes_report_without_claiming_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src.json"
            redraw = root / "redraw.json"
            out = root / "out.json"
            write_json(source, [{"id": "s", "text": "x<z", "x": 0.2, "y": 0.2, "orientation": "h", "zone": "a"}])
            write_json(redraw, [{"id": "r", "text": "x≤z", "x": 0.2, "y": 0.2, "orientation": "h", "zone": "a"}])
            proc = run([str(TOOLS / "spatial_ocr_pairing.py"), "--source", str(source), "--redraw", str(redraw), "--out", str(out)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertFalse(report["pairing_coverage_complete"])
            self.assertFalse(report["claims_measured_visual_pass"])


class LayoutResolverTests(unittest.TestCase):
    def test_b_resolves_to_b_and_records_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "out_B" / "Example.pptx"
            tiny_pptx(target, b"variant-b")
            env = os.environ.copy()
            env["FIG_ROOT"] = str(root)
            proc = run([str(TOOLS / "layout_type_shape_gate.py"), "B", "Example"], env=env)
            report = json.loads((root / "qa" / "Example_layout_type_shape.json").read_text(encoding="utf-8"))
            self.assertEqual(report["pptx_rel"], "out_B/Example.pptx")
            self.assertEqual(report["pptx_sha256"], PRIMITIVES.sha256(target))
            self.assertFalse(report["resolver_fallback_used"])
            self.assertFalse(report["thresholds_changed"])
            self.assertEqual(report["version"], "2026-10-28-t49u")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_missing_b_does_not_use_a_or_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tiny_pptx(root / "out_A" / "Example.pptx", b"variant-a")
            tiny_pptx(root / "backup" / "old" / "Example.pptx", b"old")
            env = os.environ.copy()
            env["FIG_ROOT"] = str(root)
            proc = run([str(TOOLS / "layout_type_shape_gate.py"), "B", "Example"], env=env)
            self.assertEqual(proc.returncode, 1)
            report = json.loads((root / "qa" / "Example_layout_type_shape.json").read_text(encoding="utf-8"))
            self.assertFalse(report["pass"])
            self.assertIn("refused fallback", report["error"])
            self.assertIn("out_B/Example.pptx", report["error"])
            self.assertNotIn("pptx_rel", report)

    def test_symlink_b_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "out_A" / "Example.pptx"
            tiny_pptx(real, b"variant-a")
            link = root / "out_B" / "Example.pptx"
            link.parent.mkdir(parents=True)
            link.symlink_to(real)
            env = os.environ.copy()
            env["FIG_ROOT"] = str(root)
            proc = run([str(TOOLS / "layout_type_shape_gate.py"), "B", "Example"], env=env)
            report = json.loads((root / "qa" / "Example_layout_type_shape.json").read_text(encoding="utf-8"))
            self.assertEqual(proc.returncode, 1)
            self.assertIn("symlink", report["error"])
            self.assertNotEqual(report.get("pptx_sha256"), PRIMITIVES.sha256(real))


class PolicyTests(unittest.TestCase):
    def test_repair_continue_and_same_class_stop(self):
        self.assertEqual(POLICY.evaluate_status(status())["action"], "CONTINUE_REPAIR")
        stopped = POLICY.evaluate_status(status(same_class_attempts=3))
        self.assertEqual(stopped["action"], "STOP_SAME_CLASS")
        self.assertFalse(stopped["measured_pass"])
        self.assertFalse(stopped["owner_acceptance_flips_measurement"])
        self.assertTrue(POLICY.same_class_stop([
            {"defect_class": "relation", "gate_version": "t48u"},
            {"defect_class": "relation", "gate_version": "t48u"},
            {"defect_class": "relation", "gate_version": "t48u"},
        ]))
        self.assertFalse(POLICY.same_class_stop([
            {"defect_class": "relation", "gate_version": "t48u"},
            {"defect_class": "relation", "gate_version": "t48u-r2"},
            {"defect_class": "relation", "gate_version": "t48u"},
        ]))

    def test_acceptance_does_not_flip_fail_and_new_class_can_continue(self):
        accepted = POLICY.evaluate_status(status(owner_acceptance={"accepted": True, "scope": "current-look"}))
        self.assertEqual(accepted["action"], "STOP_ACCEPTED_STYLE_KEEP_FAIL")
        self.assertFalse(accepted["measured_pass"])
        continued = POLICY.evaluate_status(status(
            owner_acceptance={"accepted": True, "scope": "current-look"},
            request_new_technical_fix=True,
            defect_class="axis-label",
            previous_defect_class="relation",
        ))
        self.assertEqual(continued["action"], "CONTINUE_NEW_CLASS")
        self.assertFalse(continued["measured_pass"])

    def test_false_claims_are_rejected(self):
        self.assertEqual(
            POLICY.evaluate_status(status(rewrite_historical_measurement=True))["action"],
            "REJECT_REWRITE",
        )
        self.assertEqual(
            POLICY.evaluate_status(status(claim_measurement_pass=True))["action"],
            "REJECT_REWRITE",
        )
        self.assertEqual(
            POLICY.evaluate_status(status(tool_logic_only=True, claim_user_figure_pass=True))["action"],
            "REJECT_FALSE_PASS",
        )
        self.assertEqual(
            POLICY.evaluate_status(status(claim_native_pass=True))["action"],
            "REJECT_NATIVE_CLAIM",
        )

    def test_deliver_requires_each_technical_axis(self):
        ready = status(
            measurement={"pass": True, "report_sha256": "b" * 64},
            source_review="PASS",
            visual_review="PASS",
            delivery_integrity="PASS",
            native_application_review="PASS",
        )
        self.assertEqual(POLICY.evaluate_status(ready)["action"], "CONTINUE_DELIVER")
        ready["native_application_review"] = "NOT_PERFORMED"
        unknown = POLICY.evaluate_status(ready)
        self.assertEqual(unknown["action"], "CONTINUE_DELIVER_NATIVE_UNKNOWN")
        self.assertFalse(unknown["native_pass"])
        ready["source_review"] = "UNKNOWN"
        self.assertEqual(POLICY.evaluate_status(ready)["action"], "STOP_INCOMPLETE")

    def test_historical_fail_file_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "gate.json"
            legacy.write_text(json.dumps({"pass": False, "fig": "synthetic"}), encoding="utf-8")
            before = legacy.read_bytes()
            written = POLICY.commit_immutable_report(root, "gate", {"pass": True, "fig": "synthetic"})
            self.assertEqual(legacy.read_bytes(), before)
            self.assertTrue(json.loads(written.read_text(encoding="utf-8"))["pass"])
            self.assertTrue(json.loads(written.read_text(encoding="utf-8"))["does_not_replace_historical"])
            with self.assertRaises(ValueError):
                POLICY.refuse_inplace_flip(legacy, {"pass": True})


class EvidenceTests(unittest.TestCase):
    def test_pdf_bytes_are_not_fc_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "synthetic.pdf"
            pdf.write_bytes(b"%PDF-1.4\n1 0 obj << /BaseFont /AAAAAA+SyntheticSerif >> endobj\n%%EOF\n")
            report = POLICY.font_evidence(
                pdf,
                requested_font="Requested Serif",
                fc_match_prediction="Predicted Sans",
            )
            self.assertEqual(report["pdf_basefonts"], ["AAAAAA+SyntheticSerif"])
            self.assertFalse(report["fc_match_is_pdf_proof"])
            self.assertEqual(report["span_attribution"], "UNKNOWN")
            self.assertNotEqual(report["fc_match_prediction"], report["pdf_basefonts"][0])
            self.assertFalse(report["pdffonts"]["proves_span"])
            with self.assertRaises(ValueError):
                POLICY.font_evidence(pdf, span_face="Predicted Sans", span_evidence={"source": "fc-match"})
        missing = POLICY.optional_pdffonts(Path("unused.pdf"), which=lambda _name: None)
        self.assertEqual(missing["status"], "OPTIONAL_DEPENDENCY_MISSING")

    def test_media_contain_and_mismatch(self):
        ok = POLICY.review_media_slot({
            "slot_id": "slot",
            "authorized_use": "this-slot",
            "source_rel_id": "media/example.png",
            "source_sha256": "abc",
            "scene_label": "ExampleScene",
            "fit": "uniform_contain",
            "src_rect_checked": True,
            "layer_order": "photo-under-labels",
            "alias_evidence": "supplied-name",
        })
        self.assertTrue(ok["identity_ok"])
        self.assertEqual(ok["exact_experiment_run"], "UNKNOWN")
        bad = POLICY.review_media_slot({
            "slot_id": "slot",
            "authorized_use": "this-slot",
            "source_rel_id": "media/example.png",
            "source_sha256": "abc",
            "scene_label": "ExampleScene",
            "fit": "stretch",
            "src_rect_checked": False,
            "layer_order": "photo-under-labels",
            "identity_status": "MISMATCH",
            "replaced_actual_media": False,
            "alias_evidence": "note",
            "exact_experiment_run_known": True,
        })
        self.assertFalse(bad["identity_ok"])
        self.assertTrue(any("replacement" in item for item in bad["problems"]))
        self.assertTrue(any("experiment run" in item for item in bad["problems"]))

    def test_vehicle_geometry_before_samples(self):
        ok = POLICY.review_vehicle({
            "projection_class": "synthetic-long-roof",
            "aspect_wh": 2.0,
            "shoulder_tail": "recorded",
            "wheelbase": 1.2,
            "window_boundary": "recorded",
            "lamp": "recorded",
            "same_scale_sbs": True,
            "axis_frame": "world",
            "blend_reopened": True,
            "freestyle_actual": False,
            "samples": 128,
            "order": "geometry-material-light",
            "style_proof": "geometry",
            "confirmation_fully_met": False,
        })
        self.assertEqual(ok["problems"], [])
        self.assertFalse(ok["confirmation_fully_met"])
        self.assertFalse(ok["samples_are_style_proof"])
        bad = POLICY.review_vehicle({
            "projection_class": "synthetic-long-roof",
            "aspect_wh": 2.0,
            "shoulder_tail": "recorded",
            "wheelbase": 1.2,
            "window_boundary": "recorded",
            "lamp": "recorded",
            "same_scale_sbs": False,
            "axis_frame": "local",
            "blend_reopened": False,
            "freestyle_actual": False,
            "samples": 256,
            "order": "samples-first",
            "style_proof": "samples_only",
            "confirmation_fully_met": True,
            "wheelbase_fix_axis": "local",
            "object_already_rotated": True,
        })
        self.assertGreaterEqual(len(bad["problems"]), 4)
        self.assertFalse(bad["confirmation_fully_met"])

    def test_series_conflict_stays_out_of_primary_delivery(self):
        traced = POLICY.review_series({
            "kind": "image_geometry",
            "conflict": True,
            "primary_label": "NON_VERIFIED_SOURCE_TRACE",
        })
        self.assertEqual(traced["experimental_sequence"], "NOT_CLAIMED")
        with self.assertRaises(ValueError):
            POLICY.review_series({"kind": "image_geometry", "claims_recovered_experiment": True})
        with self.assertRaises(ValueError):
            POLICY.review_series({
                "kind": "verified",
                "path": "out_A/Example.pptx",
                "label": "VERIFIED_ALTERNATIVE",
            })
        side = POLICY.review_series({
            "kind": "verified",
            "path": "alternatives/example.json",
            "label": "VERIFIED_ALTERNATIVE",
        })
        self.assertFalse(side["mixed_into_primary"])


class CommandTests(unittest.TestCase):
    def test_selftest_command_is_runnable(self):
        proc = run([str(TOOLS / "quality_sync.py"), "selftest"])
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])

    def test_documented_freeze_zip_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            snap = root / "snap"
            tiny_pptx(source / "out_A" / "Example.pptx", b"aaa")
            tiny_pptx(source / "out_B" / "Example.pptx", b"bbb")
            files = root / "files.txt"
            files.write_text("out_A/Example.pptx\nout_B/Example.pptx\n", encoding="utf-8")
            manifest = snap / "manifest.json"
            archive = root / "part.zip"
            freeze = run([
                str(TOOLS / "quality_sync.py"), "freeze",
                "--source", str(source), "--dest", str(snap),
                "--files", str(files), "--manifest", str(manifest),
            ])
            self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
            packed = run([
                str(TOOLS / "quality_sync.py"), "make-zip",
                "--snapshot", str(snap), "--manifest", str(manifest),
                "--output", str(archive),
            ])
            self.assertEqual(packed.returncode, 0, packed.stdout + packed.stderr)
            verified = run([
                str(TOOLS / "quality_sync.py"), "verify-zip",
                "--archive", str(archive), "--manifest", str(manifest),
            ])
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
            payload = json.loads(verified.stdout)
            self.assertEqual(payload["remote_hash_verified"], "UNKNOWN")
            missing = run([
                str(TOOLS / "quality_sync.py"), "resolve-variant",
                "--root", str(source), "--tag", "Missing", "--variant", "B",
            ])
            self.assertEqual(missing.returncode, 1)
            self.assertIn("fallback", missing.stdout + missing.stderr)

    def test_skill_export_manifest_matches_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "skills_sync_export.zip"
            proc = run([str(TOOLS / "export_skill_sync.py"), str(output)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
                self.assertNotIn("skills_sync_export.zip", names)
                self.assertTrue(all(not name.endswith((".png", ".pptx", ".ttf")) for name in names))
                manifest = json.loads(archive.read("manifest.json"))
                self.assertGreaterEqual(len(manifest["files"]), 6)
                for item in manifest["files"]:
                    data = archive.read(item["path"])
                    self.assertEqual(PRIMITIVES.sha256_bytes(data) if hasattr(PRIMITIVES, "sha256_bytes") else __import__("hashlib").sha256(data).hexdigest(), item["sha256"])
                    text = data.decode("utf-8")
                    self.assertTrue(text.startswith("---"))
                    self.assertIn(f"name: {item['frontmatter_name']}", text)


if __name__ == "__main__":
    unittest.main()
