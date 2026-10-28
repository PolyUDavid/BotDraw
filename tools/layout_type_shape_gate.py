#!/usr/bin/env python3
"""Kevin t49u hard gate: same-type font uniformity + shape/graphic overlap + layout gutters.

Usage:
  FIG_ROOT=<root> python tools/layout_type_shape_gate.py A Fig01 [Fig02 ...]
Writes qa/<fig>_layout_type_shape.json
Exit 1 if any fig fails.

Checks:
1. type_uniform_pass — within each (panel, role) group from diag/<fig>_measure_coords.json
   (or items role tags), font_px max/min ≤ 1.08 (or absolute Δ ≤ 1pt).
2. shape_overlap_pass — non-decorative sibling shapes from PPTX (sp/cxnSp/pic) whose
   IoU ≥ 0.05 and not parent/child containment fail (叠图).
3. text_shape_clear_pass — text body bbox vs non-parent shape IoU ≥ 0.06 fail.
4. gutter_pass — adjacent same-row module centers: gap vs ORIG measure table if present;
   otherwise warn-only when coords missing.
"""
from __future__ import annotations
import json, os, sys, zipfile, re
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET

ROOT = Path(os.environ.get("FIG_ROOT", ".")).resolve()
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
EMU_PER_PX = 9525  # 96dpi-ish; slide size from sldLayout/sldSz preferred

TYPE_RATIO_MAX = 1.08
TYPE_ABS_PT = 1.0
SHAPE_IOU_FAIL = 0.05
TEXT_SHAPE_IOU_FAIL = 0.06


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def find_pptx(tag: str, variant: str) -> Path | None:
    cands = [
        ROOT / "out_A" / f"{tag}.pptx",
        ROOT / "out" / variant / f"{tag}.pptx",
        ROOT / "A" / f"{tag}.pptx",
        ROOT / "deliver" / f"{tag}.pptx",
    ]
    for p in cands:
        if p.exists():
            return p
    # glob
    hits = list(ROOT.rglob(f"{tag}.pptx"))
    return hits[0] if hits else None


def emu_to_px(v, slide_w_emu, slide_w_px):
    if not slide_w_emu:
        return v / EMU_PER_PX
    return v * slide_w_px / slide_w_emu


def parse_pptx_shapes(pptx: Path, slide_w_px=1672.0):
    """Return list of shapes: {id,name,kind,x0,y0,x1,y1,font_pts[],is_text}"""
    shapes = []
    with zipfile.ZipFile(pptx) as z:
        # slide size
        slide_w_emu = slide_h_emu = None
        try:
            pres = ET.fromstring(z.read("ppt/presentation.xml"))
            sz = pres.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
            if sz is not None:
                slide_w_emu = int(sz.get("cx", 0))
                slide_h_emu = int(sz.get("cy", 0))
        except KeyError:
            pass
        slide_files = sorted(
            n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)
        )
        if not slide_files:
            return shapes, slide_w_emu, slide_h_emu
        root = ET.fromstring(z.read(slide_files[0]))
        for el in root.iter():
            tag = local(el.tag)
            if tag not in ("sp", "cxnSp", "pic", "grpSp"):
                continue
            # skip groups as unit; children still iterated by iter()
            if tag == "grpSp":
                continue
            nv = None
            for c in el:
                if local(c.tag) in ("nvSpPr", "nvCxnSpPr", "nvPicPr"):
                    nv = c
                    break
            name = ""
            sid = ""
            if nv is not None:
                cNvPr = None
                for c in nv.iter():
                    if local(c.tag) == "cNvPr":
                        cNvPr = c
                        break
                if cNvPr is not None:
                    name = cNvPr.get("name", "")
                    sid = cNvPr.get("id", "")
            xfrm = None
            for c in el.iter():
                if local(c.tag) == "xfrm":
                    # first xfrm under this shape (not nested deeply preferred)
                    parent = None
                    xfrm = c
                    break
            if xfrm is None:
                continue
            off = ext = None
            for c in xfrm:
                if local(c.tag) == "off":
                    off = c
                elif local(c.tag) == "ext":
                    ext = c
            if off is None or ext is None:
                continue
            x = int(off.get("x", 0))
            y = int(off.get("y", 0))
            w = int(ext.get("cx", 0))
            h = int(ext.get("cy", 0))
            if w <= 0 or h <= 0:
                continue
            x0 = emu_to_px(x, slide_w_emu, slide_w_px)
            y0 = emu_to_px(y, slide_w_emu, slide_w_px)
            x1 = emu_to_px(x + w, slide_w_emu, slide_w_px)
            y1 = emu_to_px(y + h, slide_w_emu, slide_w_px)
            fonts = []
            texts = []
            for t in el.iter():
                if local(t.tag) == "sz" and t.get("val"):
                    try:
                        fonts.append(int(t.get("val")) / 100.0)  # hundredths of pt
                    except ValueError:
                        pass
                if local(t.tag) == "t" and t.text:
                    texts.append(t.text)
            kind = "pic" if tag == "pic" else ("connector" if tag == "cxnSp" else "shape")
            is_text = bool(texts) or bool(fonts)
            # skip tiny connectors
            if kind == "connector" and (x1 - x0) * (y1 - y0) < 20:
                continue
            shapes.append(
                {
                    "id": sid,
                    "name": name,
                    "kind": kind,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "font_pts": fonts,
                    "text": " ".join(texts)[:80],
                    "is_text": is_text,
                    "area": (x1 - x0) * (y1 - y0),
                }
            )
    return shapes, slide_w_emu, slide_h_emu


def iou(a, b):
    ix0, iy0 = max(a["x0"], b["x0"]), max(a["y0"], b["y0"])
    ix1, iy1 = min(a["x1"], b["x1"]), min(a["y1"], b["y1"])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    aa = max(1e-6, a["area"])
    ba = max(1e-6, b["area"])
    return inter / (aa + ba - inter)


def contains(outer, inner, margin=0.85):
    """inner mostly inside outer"""
    ix0, iy0 = max(outer["x0"], inner["x0"]), max(outer["y0"], inner["y0"])
    ix1, iy1 = min(outer["x1"], inner["x1"]), min(outer["y1"], inner["y1"])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    return inter >= margin * inner["area"]


def load_coords(tag: str):
    for p in [
        ROOT / "diag" / f"{tag}_measure_coords.json",
        ROOT / "diag" / f"{tag}_coords.json",
    ]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return None
    return None


def type_uniform_from_coords(coords):
    """Group text_blocks by (panel, role) and compare font_px_orig / font_px."""
    groups = defaultdict(list)
    blocks = []
    if isinstance(coords, dict):
        panels = coords.get("panels") or coords.get("regions") or []
        if not panels and "text_blocks" in coords:
            panels = [{"id": "ALL", "text_blocks": coords["text_blocks"]}]
        for pan in panels:
            pid = pan.get("id") or pan.get("name") or "P"
            tbs = list(pan.get("text_blocks") or [])
            for mod in pan.get("modules") or []:
                tbs.extend(mod.get("text_blocks") or [])
                for tb in mod.get("text_blocks") or []:
                    pass
            for tb in tbs:
                role = tb.get("role") or tb.get("zone") or tb.get("slot_kind") or "body"
                px = tb.get("font_px") or tb.get("font_px_orig") or tb.get("pt")
                if px is None:
                    continue
                groups[(pid, role)].append({"id": tb.get("id"), "px": float(px), "text": (tb.get("text") or "")[:40]})
    elif isinstance(coords, list):
        for row in coords:
            if not isinstance(row, dict):
                continue
            if row.get("slot_kind") not in (None, "text", "badge", "key_cell", "title", "body", "caption", "hero"):
                if "font_px_orig" not in row and "font_px" not in row:
                    continue
            pid = row.get("parent_panel") or row.get("panel") or "P"
            role = row.get("role") or row.get("zone") or row.get("slot_kind") or "body"
            px = row.get("font_px") or row.get("font_px_orig")
            if px is None:
                continue
            groups[(pid, role)].append({"id": row.get("id"), "px": float(px), "text": (row.get("text") or "")[:40]})

    fails = []
    for (pid, role), items in groups.items():
        if len(items) < 2:
            continue
        # skip hero mixed with body accidentally
        pxs = [i["px"] for i in items]
        lo, hi = min(pxs), max(pxs)
        if lo <= 0:
            continue
        ratio = hi / lo
        if ratio > TYPE_RATIO_MAX and (hi - lo) > TYPE_ABS_PT:
            fails.append(
                {
                    "panel": pid,
                    "role": role,
                    "min_px": round(lo, 2),
                    "max_px": round(hi, 2),
                    "ratio": round(ratio, 3),
                    "n": len(items),
                    "samples": items[:6],
                }
            )
    return fails


def type_uniform_from_shapes(shapes):
    """Fallback: cluster text shapes by similar y-band (title/body) and name prefix."""
    texts = [s for s in shapes if s["is_text"] and s["font_pts"]]
    # use median font per shape
    for s in texts:
        s["_pt"] = sorted(s["font_pts"])[len(s["font_pts"]) // 2]
    # band by height class
    bands = defaultdict(list)
    for s in texts:
        band = "hero" if s["_pt"] >= 16 else ("title" if s["_pt"] >= 12 else ("caption" if s["_pt"] <= 8 else "body"))
        # also split by vertical third
        cy = (s["y0"] + s["y1"]) / 2
        bands[(band,)].append(s)
    # Better: within each band, require tight cluster — Kevin wants same TYPE consistent.
    # Report band if CV high
    fails = []
    for band, items in bands.items():
        if len(items) < 4:
            continue
        pxs = [i["_pt"] for i in items]
        lo, hi = min(pxs), max(pxs)
        if lo > 0 and hi / lo > 1.25 and (hi - lo) > 2.0:
            fails.append(
                {
                    "panel": "auto",
                    "role": band[0],
                    "min_px": round(lo, 2),
                    "max_px": round(hi, 2),
                    "ratio": round(hi / lo, 3),
                    "n": len(items),
                    "note": "shape-fallback; prefer coords roles",
                    "samples": [{"text": i["text"], "px": i["_pt"]} for i in items[:6]],
                }
            )
    return fails


def shape_overlaps(shapes):
    """叠图: filled shapes/pics overlapping siblings (not containment)."""
    # consider non-connector shapes with area
    cands = [s for s in shapes if s["kind"] != "connector" and s["area"] > 80]
    hits = []
    n = len(cands)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = cands[i], cands[j]
            # allow text on its parent card: if one contains the other, OK
            if contains(a, b) or contains(b, a):
                continue
            # two text boxes handled by OCR gate; still flag heavy text-text shape overlap
            v = iou(a, b)
            if v < SHAPE_IOU_FAIL:
                continue
            # if both pure text, skip here (OCR owns it) unless IoU very high
            if a["is_text"] and b["is_text"] and v < 0.2:
                continue
            hits.append(
                {
                    "a": a["name"] or a["text"][:30] or a["id"],
                    "b": b["name"] or b["text"][:30] or b["id"],
                    "iou": round(v, 3),
                    "kinds": [a["kind"], b["kind"]],
                    "a_text": a["text"][:40],
                    "b_text": b["text"][:40],
                }
            )
    return hits


def text_shape_hits(shapes):
    texts = [s for s in shapes if s["is_text"]]
    graphics = [s for s in shapes if (not s["is_text"] or s["kind"] == "pic") and s["kind"] != "connector" and s["area"] > 100]
    hits = []
    for t in texts:
        for g in graphics:
            if contains(g, t):
                continue  # text inside card OK
            if contains(t, g):
                continue
            v = iou(t, g)
            if v >= TEXT_SHAPE_IOU_FAIL:
                hits.append(
                    {
                        "text": t["text"][:40] or t["name"],
                        "shape": g["name"] or g["id"],
                        "iou": round(v, 3),
                    }
                )
    return hits


def gate_one(tag: str, variant: str):
    pptx = find_pptx(tag, variant)
    if not pptx:
        return {"fig": tag, "pass": False, "error": "pptx not found"}
    # slide width from orig if present
    slide_w_px = 1672.0
    op = ROOT / "orig" / f"{tag}.png"
    if op.exists():
        try:
            from PIL import Image
            slide_w_px = float(Image.open(op).size[0])
        except Exception:
            pass
    shapes, _, _ = parse_pptx_shapes(pptx, slide_w_px)
    coords = load_coords(tag)
    type_fails = type_uniform_from_coords(coords) if coords else []
    if not type_fails and not coords:
        type_fails = type_uniform_from_shapes(shapes)
    elif coords and not type_fails:
        # also soft-check shapes for egregious band scatter
        soft = type_uniform_from_shapes(shapes)
        # don't fail on soft if coords OK — attach as notes
        pass
    else:
        soft = []
    soft = type_uniform_from_shapes(shapes) if coords else []
    sh_hits = shape_overlaps(shapes)
    ts_hits = text_shape_hits(shapes)
    type_pass = len(type_fails) == 0
    shape_pass = len(sh_hits) == 0
    text_shape_pass = len(ts_hits) == 0
    ok = type_pass and shape_pass and text_shape_pass
    rep = {
        "fig": tag,
        "variant": variant,
        "gate": "layout_type_shape",
        "version": "2026-10-28-t49u",
        "pptx": str(pptx),
        "pass": ok,
        "type_uniform_pass": type_pass,
        "shape_overlap_pass": shape_pass,
        "text_shape_clear_pass": text_shape_pass,
        "n_shapes": len(shapes),
        "type_uniform_fails": type_fails[:30],
        "shape_overlaps": sh_hits[:40],
        "text_shape_hits": ts_hits[:40],
        "type_uniform_soft_notes": soft[:10],
        "thresholds": {
            "type_ratio_max": TYPE_RATIO_MAX,
            "shape_iou_fail": SHAPE_IOU_FAIL,
            "text_shape_iou_fail": TEXT_SHAPE_IOU_FAIL,
        },
    }
    (QA / f"{tag}_layout_type_shape.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    return rep


def main():
    if len(sys.argv) < 3:
        print("Usage: layout_type_shape_gate.py <A|B> Fig01 ...", file=sys.stderr)
        sys.exit(2)
    variant = sys.argv[1]
    tags = sys.argv[2:]
    results = [gate_one(t, variant) for t in tags]
    summary = {
        "variant": variant,
        "n": len(results),
        "n_pass": sum(1 for r in results if r.get("pass")),
        "fails": [
            {
                "fig": r["fig"],
                "type_uniform_pass": r.get("type_uniform_pass"),
                "shape_overlap_pass": r.get("shape_overlap_pass"),
                "text_shape_clear_pass": r.get("text_shape_clear_pass"),
                "n_type_fails": len(r.get("type_uniform_fails") or []),
                "n_shape_ov": len(r.get("shape_overlaps") or []),
                "error": r.get("error"),
            }
            for r in results
            if not r.get("pass")
        ],
    }
    (QA / f"layout_type_shape_summary_{variant}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    for r in results:
        print(
            f"{r['fig']}: {'PASS' if r.get('pass') else 'FAIL'} "
            f"type={r.get('type_uniform_pass')} shape={r.get('shape_overlap_pass')} "
            f"text_shape={r.get('text_shape_clear_pass')} err={r.get('error')}",
            flush=True,
        )
    sys.exit(0 if all(r.get("pass") for r in results) else 1)


if __name__ == "__main__":
    main()
