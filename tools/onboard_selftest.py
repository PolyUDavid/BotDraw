#!/usr/bin/env python3
"""Kevin t69u — onboard smoke before any user figure.

Self-detects the BotDraw environment, draws the bundled fixtures/onboard
mini panel, and tunes type scale + clearance until the real OCR and layout
gates pass. Writes qa/onboard_selftest.json. Exit 0 only when pass is true.

  python3 tools/onboard_selftest.py
  python3 tools/onboard_selftest.py --emit-fixture

Does not read a user FIG_ROOT. t68u crude-B ban still applies after this proof.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "fixtures" / "onboard"
SPEC_PATH = FIXTURE / "spec.json"
ORIG_PATH = FIXTURE / "orig.png"
EXPECTED_PATH = FIXTURE / "expected.json"
TAG = "Onboard"
EMU_PER_PX = 9525
FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
GOLD_ARCHETYPES = (
    "brain_layered",
    "gear_layered",
    "axis_arrows_outward",
    "type_title_body_caption",
)
T68U_NOTE = (
    "After onboard, B hardware/vehicle slots still ban blurry screenshots and "
    "grey-block Cycles. Fig08 HIL/FiSens/PV must be Confirmation Cycles "
    "(film_transparent, Freestyle #34363A, dual SUN, SAMPLES>=96). "
    "This proof does not certify B."
)


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text())


def find_font() -> Path | None:
    for p in FONT_CANDIDATES:
        if p.exists():
            return p
    return None


def which(names: list[str]) -> str | None:
    for name in names:
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def detect_env() -> dict:
    blockers: list[str] = []
    warnings: list[str] = []

    def try_import(mod: str) -> bool:
        try:
            __import__(mod)
            return True
        except Exception:
            return False

    pillow = try_import("PIL")
    rapid = try_import("rapidocr_onnxruntime")
    lxml = try_import("lxml")
    if not pillow:
        blockers.append("Python package Pillow is missing (pip install pillow)")
    if not rapid:
        blockers.append("Python package rapidocr_onnxruntime is missing")
    if not lxml:
        warnings.append("Python package lxml is missing (needed by fig_gate_audit.py)")

    ocr_tool = (REPO / "tools" / "ocr_font_overlap_gate.py").exists()
    layout_tool = (REPO / "tools" / "layout_type_shape_gate.py").exists()
    if not ocr_tool:
        blockers.append("tools/ocr_font_overlap_gate.py missing")
    if not layout_tool:
        blockers.append("tools/layout_type_shape_gate.py missing")

    gold = {}
    gold_root = REPO / "gold_bars"
    for name in GOLD_ARCHETYPES:
        d = gold_root / name
        ok = (d / "orig.png").exists() and (d / "checklist.md").exists() and (d / "pass_example.png").exists()
        gold[name] = ok
        if not ok:
            blockers.append(f"gold_bars/{name}/ missing orig.png, pass_example.png, or checklist.md")

    font = find_font()
    if font is None:
        blockers.append("No DejaVu/Liberation sans font found for the onboard fixture")

    if not SPEC_PATH.exists() or not EXPECTED_PATH.exists():
        blockers.append("fixtures/onboard/spec.json or expected.json missing")

    libre = which(["soffice", "libreoffice"])
    blender = which(["blender"])
    if not libre:
        warnings.append("LibreOffice not found; user-figure PNG export still needs it before a real PASS")
    if not blender:
        warnings.append("Blender not found; A onboard can pass, but B still requires Blender and the t68u crude-B ban")

    env = {
        "python": sys.version.split()[0],
        "pillow": pillow,
        "rapidocr_onnxruntime": rapid,
        "lxml": lxml,
        "font": str(font) if font else None,
        "ocr_gate": ocr_tool,
        "layout_gate": layout_tool,
        "gold_bars": gold,
        "libreoffice": libre,
        "blender": blender,
    }
    return {"env": env, "blockers": blockers, "warnings": warnings, "env_pass": not blockers}


def fit_contain(src_w: int, src_h: int, box_w: int, box_h: int) -> tuple[int, int, int, int]:
    scale = min(box_w / src_w, box_h / src_h)
    dw, dh = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    x = (box_w - dw) // 2
    y = (box_h - dh) // 2
    return x, y, dw, dh


def render_panel(path: Path, spec: dict, scale: float, gap_extra: int) -> dict:
    from PIL import Image, ImageDraw, ImageFont

    font_path = find_font()
    if font_path is None:
        raise SystemExit("onboard font missing")
    w, h = spec["canvas"]
    im = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(im)
    px0, py0, pw, ph = spec["panel"]
    draw.rectangle([px0, py0, px0 + pw - 1, py0 + ph - 1], outline="#34363A", width=2)
    sx, sy, sw, sh = spec["slot"]
    draw.rectangle([sx, sy, sx + sw - 1, sy + sh - 1], fill="#F4F1EA", outline="#34363A", width=2)
    gold_path = REPO / spec["gold_inset"]
    gold = Image.open(gold_path).convert("RGBA")
    ox, oy, dw, dh = fit_contain(gold.width, gold.height, sw - 16, sh - 16)
    fitted = gold.resize((dw, dh), Image.Resampling.LANCZOS)
    im.paste(fitted, (sx + 8 + ox, sy + 8 + oy), fitted)
    placed = {
        "source": spec["gold_inset"],
        "source_crop": False,
        "slot": [sx, sy, sw, sh],
        "placed": [sx + 8 + ox, sy + 8 + oy, dw, dh],
        "full_source_contained": True,
    }
    for i, tb in enumerate(spec["texts"]):
        size = max(8, int(round(tb["font_px"] * scale)))
        font = ImageFont.truetype(str(font_path), size)
        x, y = tb["xy"]
        y = y + gap_extra * i
        draw.text((x, y), tb["text"], fill="#161616", font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return placed


def emu(px: float) -> int:
    return int(round(px * EMU_PER_PX))


def text_boxes(spec: dict, tight: bool, gap_extra: int) -> list[dict]:
    sx, sy, sw, sh = spec["slot"]
    boxes = []
    for i, tb in enumerate(spec["texts"]):
        x, y, bw, bh = tb["box"]
        y = y + gap_extra * i
        if not tight:
            # Deliberately ride the media slot so the layout gate fails clearance.
            bw = max(bw, (sx + sw) - x - 8)
            bh = max(bh, 220)
        boxes.append({**tb, "x": x, "y": y, "w": bw, "h": bh})
    return boxes


def write_measure(path: Path, spec: dict) -> None:
    blocks = []
    for tb in spec["texts"]:
        blocks.append(
            {
                "id": tb["id"],
                "role": tb["role"],
                "text": tb["text"],
                "font_px": tb["font_px"],
                "font_px_orig": tb["font_px"],
            }
        )
    doc = {"panels": [{"id": "P1", "text_blocks": blocks}]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2))


def write_pptx(path: Path, spec: dict, boxes: list[dict], slot_png: Path) -> None:
    w, h = spec["canvas"]
    sx, sy, sw, sh = spec["slot"]
    px, py, pw, ph = spec["panel"]
    parts: list[str] = []
    sid = 2
    parts.append(
        f"""<p:sp>
          <p:nvSpPr><p:cNvPr id="{sid}" name="panel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{emu(px)}" y="{emu(py)}"/><a:ext cx="{emu(pw)}" cy="{emu(ph)}"/></a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
            <a:ln w="12700"><a:solidFill><a:srgbClr val="34363A"/></a:solidFill></a:ln>
          </p:spPr>
        </p:sp>"""
    )
    for tb in boxes:
        sid += 1
        sz = int(tb["font_px"] * 100)
        text = (
            tb["text"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        name = tb["id"]
        x, y, bw, bh = tb["x"], tb["y"], tb["w"], tb["h"]
        parts.append(
            f"""<p:sp>
              <p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
              <p:spPr>
                <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(bw)}" cy="{emu(bh)}"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                <a:noFill/>
              </p:spPr>
              <p:txBody>
                <a:bodyPr/><a:lstStyle/>
                <a:p><a:r><a:rPr lang="en-US" sz="{sz}"/><a:t>{text}</a:t></a:r></a:p>
              </p:txBody>
            </p:sp>"""
        )
    sid += 1
    parts.append(
        f"""<p:pic>
          <p:nvPicPr><p:cNvPr id="{sid}" name="media_slot"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
          <p:blipFill>
            <a:blip r:embed="rId1"/>
            <a:stretch><a:fillRect/></a:stretch>
          </p:blipFill>
          <p:spPr>
            <a:xfrm><a:off x="{emu(sx)}" y="{emu(sy)}"/><a:ext cx="{emu(sw)}" cy="{emu(sh)}"/></a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          </p:spPr>
        </p:pic>"""
    )
    slide = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {''.join(parts)}
  </p:spTree></p:cSld>
</p:sld>"""
    pres = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>
  <p:sldSz cx="{emu(w)}" cy="{emu(h)}"/>
</p:presentation>"""
    ctypes = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""
    pres_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>"""
    slide_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/slot.png"/>
</Relationships>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        z.writestr("ppt/slides/slide1.xml", slide)
        z.writestr("ppt/slides/_rels/slide1.xml.rels", slide_rels)
        z.write(slot_png, "ppt/media/slot.png")


def media_complete(spec: dict, placed: dict) -> bool:
    w, h = spec["canvas"]
    sx, sy, sw, sh = placed["slot"]
    px, py, pw, ph = placed["placed"]
    slot_inside = sx >= 2 and sy >= 2 and sx + sw <= w - 2 and sy + sh <= h - 2
    inset_inside = (
        px >= sx and py >= sy and px + pw <= sx + sw and py + ph <= sy + sh and pw > 8 and ph > 8
    )
    return bool(placed["full_source_contained"] and not placed["source_crop"] and slot_inside and inset_inside)


def run_gate(script: Path, scratch: Path) -> dict:
    env = os.environ.copy()
    env["FIG_ROOT"] = str(scratch)
    proc = subprocess.run(
        [sys.executable, str(script), "A", TAG],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
    )
    name = "ocr_font_overlap" if "ocr_font" in script.name else "layout_type_shape"
    report = scratch / "qa" / f"{TAG}_{name}.json"
    if report.exists():
        data = json.loads(report.read_text())
    else:
        data = {"pass": False, "error": (proc.stderr or proc.stdout or "gate wrote no report")[-500:]}
    data["_exit"] = proc.returncode
    return data


def write_sbs(orig: Path, redraw: Path, dest: Path) -> None:
    from PIL import Image

    a = Image.open(orig).convert("RGB")
    b = Image.open(redraw).convert("RGB")
    gap = 12
    canvas = Image.new("RGB", (a.width + gap + b.width, max(a.height, b.height)), "white")
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width + gap, 0))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)


def emit_fixture() -> None:
    spec = load_spec()
    placed = render_panel(ORIG_PATH, spec, scale=1.0, gap_extra=0)
    print(f"wrote {ORIG_PATH} slot={placed['placed']}")


def tune(scratch: Path) -> dict:
    spec = load_spec()
    if not ORIG_PATH.exists():
        raise SystemExit(f"missing {ORIG_PATH}; run with --emit-fixture first")
    orig = scratch / "orig" / f"{TAG}.png"
    prev = scratch / "prev" / "A" / f"{TAG}.png"
    pptx = scratch / "out_A" / f"{TAG}.pptx"
    diag = scratch / "diag" / f"{TAG}_measure_coords.json"
    slot_png = scratch / "slot.png"
    orig.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ORIG_PATH, orig)
    from PIL import Image

    gold = Image.open(REPO / spec["gold_inset"]).convert("RGB")
    gold.save(slot_png)
    write_measure(diag, spec)

    scale = 0.75
    gap_extra = 0
    tight = False
    rounds = []
    last_ocr: dict = {}
    last_layout: dict = {}
    placed: dict = {}
    for n in range(1, 7):
        placed = render_panel(prev, spec, scale=scale, gap_extra=gap_extra)
        boxes = text_boxes(spec, tight=tight, gap_extra=gap_extra)
        write_pptx(pptx, spec, boxes, slot_png)
        last_ocr = run_gate(REPO / "tools" / "ocr_font_overlap_gate.py", scratch)
        last_layout = run_gate(REPO / "tools" / "layout_type_shape_gate.py", scratch)
        row = {
            "round": n,
            "scale": round(scale, 3),
            "gap_extra": gap_extra,
            "tight_boxes": tight,
            "font_pass": bool(last_ocr.get("font_pass")),
            "overlap_pass": bool(last_ocr.get("overlap_pass")),
            "h_med": last_ocr.get("h_med"),
            "n_overlap": last_ocr.get("n_overlap"),
            "type_uniform_pass": bool(last_layout.get("type_uniform_pass")),
            "shape_overlap_pass": bool(last_layout.get("shape_overlap_pass")),
            "text_shape_clear_pass": bool(last_layout.get("text_shape_clear_pass")),
            "media_slot_complete": media_complete(spec, placed),
        }
        rounds.append(row)
        proof = (
            row["font_pass"]
            and row["overlap_pass"]
            and row["type_uniform_pass"]
            and row["shape_overlap_pass"]
            and row["text_shape_clear_pass"]
            and row["media_slot_complete"]
        )
        if proof:
            break
        if not row["font_pass"]:
            h = last_ocr.get("h_med")
            if not h:
                scale = min(1.4, scale * 1.12)
            else:
                scale = min(1.4, max(0.7, scale * (1.0 / float(h))))
        if not row["overlap_pass"]:
            gap_extra += 18
        if not row["text_shape_clear_pass"] or not row["shape_overlap_pass"]:
            tight = True
            gap_extra += 8
    return {
        "rounds": rounds,
        "ocr": last_ocr,
        "layout": last_layout,
        "placed": placed,
        "prev": prev,
        "orig": orig,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BotDraw t69u onboard self-test")
    parser.add_argument("--emit-fixture", action="store_true", help="rewrite fixtures/onboard/orig.png")
    parser.add_argument("--out", type=Path, default=REPO / "qa" / "onboard_selftest.json")
    args = parser.parse_args()
    if args.emit_fixture:
        emit_fixture()
        return

    detected = detect_env()
    out = args.out
    sbs = out.parent / "onboard_sbs.png"
    report = {
        "version": "2026-10-28-t69u",
        "skill": "paper-figure-onboard-selftest",
        "fig": TAG,
        "pass": False,
        "ready_for_user_figures": False,
        "env_pass": detected["env_pass"],
        "proof_pass": False,
        "font_pass": False,
        "overlap_pass": False,
        "h_med": None,
        "n_overlap": None,
        "type_uniform_pass": False,
        "shape_overlap_pass": False,
        "text_shape_clear_pass": False,
        "media_slot_complete": False,
        "sbs_path": str(sbs.relative_to(REPO)) if sbs.is_relative_to(REPO) else str(sbs),
        "fixture": "fixtures/onboard/orig.png",
        "gold_bar_ref": "gold_bars/brain_layered",
        "tuned_rounds": 0,
        "rounds": [],
        "env": detected["env"],
        "warnings": detected["warnings"],
        "blockers": detected["blockers"],
        "t68u_crude_b_ban": T68U_NOTE,
    }
    if detected["env_pass"]:
        scratch = Path(tempfile.mkdtemp(prefix="botdraw-onboard-"))
        try:
            tuned = tune(scratch)
            ocr = tuned["ocr"]
            layout = tuned["layout"]
            placed = tuned["placed"]
            spec = load_spec()
            report["rounds"] = tuned["rounds"]
            report["tuned_rounds"] = len(tuned["rounds"])
            report["font_pass"] = bool(ocr.get("font_pass"))
            report["overlap_pass"] = bool(ocr.get("overlap_pass"))
            report["h_med"] = ocr.get("h_med")
            report["n_overlap"] = ocr.get("n_overlap")
            report["type_uniform_pass"] = bool(layout.get("type_uniform_pass"))
            report["shape_overlap_pass"] = bool(layout.get("shape_overlap_pass"))
            report["text_shape_clear_pass"] = bool(layout.get("text_shape_clear_pass"))
            report["media_slot_complete"] = media_complete(spec, placed)
            report["proof_pass"] = bool(tuned["rounds"] and all(
                tuned["rounds"][-1][k]
                for k in (
                    "font_pass",
                    "overlap_pass",
                    "type_uniform_pass",
                    "shape_overlap_pass",
                    "text_shape_clear_pass",
                    "media_slot_complete",
                )
            ))
            if tuned["prev"].exists():
                write_sbs(tuned["orig"], tuned["prev"], sbs)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    report["pass"] = bool(report["env_pass"] and report["proof_pass"])
    report["ready_for_user_figures"] = report["pass"]
    if not report["pass"] and report["env_pass"]:
        report["blockers"] = list(report["blockers"]) + ["onboard proof did not pass; do not start user figures"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in (
        "pass", "ready_for_user_figures", "env_pass", "proof_pass", "h_med",
        "font_pass", "overlap_pass", "type_uniform_pass", "shape_overlap_pass",
        "text_shape_clear_pass", "media_slot_complete", "tuned_rounds", "sbs_path",
        "blockers", "warnings",
    )}, indent=2, ensure_ascii=False))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
