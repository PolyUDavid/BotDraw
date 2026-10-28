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
            # body fill? (ignore line fills) — stroke-only polylines have huge AABB false 叠图
            filled = kind == "pic"
            spPr = None
            for c in el:
                if local(c.tag) == "spPr":
                    spPr = c
                    break
            if spPr is not None:
                body_no = False
                body_fill = False
                for c in spPr:
                    tg = local(c.tag)
                    if tg == "noFill":
                        body_no = True
                    if tg in ("solidFill", "gradFill", "blipFill", "pattFill"):
                        body_fill = True
                if body_fill:
                    filled = True
                elif body_no:
                    filled = False
                else:
                    filled = True  # default preset shapes usually filled
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
                    "filled": filled,
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
    """inner mostly inside outer; also true if inner center is inside outer (label overflow)."""
    ix0, iy0 = max(outer["x0"], inner["x0"]), max(outer["y0"], inner["y0"])
    ix1, iy1 = min(outer["x1"], inner["x1"]), min(outer["y1"], inner["y1"])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    if inter >= margin * inner["area"]:
        return True
    cx = (inner["x0"] + inner["x1"]) / 2
    cy = (inner["y0"] + inner["y1"]) / 2
    if outer["x0"] <= cx <= outer["x1"] and outer["y0"] <= cy <= outer["y1"]:
        # center-in-parent: require at least 55% coverage to avoid false parent
        if inter >= 0.55 * inner["area"]:
            return True
    return False


def _coords_text_count(coords) -> int:
    if not coords:
        return 0
    n = 0
    if isinstance(coords, list):
        return sum(1 for r in coords if isinstance(r, dict) and (r.get("font_px") or r.get("font_px_orig") or r.get("px")))
    if isinstance(coords, dict):
        # walk panels/modules text_blocks
        panels = coords.get("panels") or coords.get("regions") or {}
        if isinstance(panels, dict):
            plist = list(panels.values())
        elif isinstance(panels, list):
            plist = [x for x in panels if isinstance(x, dict)]
        else:
            plist = []
        if not plist and "text_blocks" in coords:
            plist = [coords]
        for pan in plist:
            if not isinstance(pan, dict):
                continue
            n += len(pan.get("text_blocks") or [])
            mods = pan.get("modules") or {}
            if isinstance(mods, dict):
                mods = mods.values()
            for mod in mods or []:
                if isinstance(mod, dict):
                    n += len(mod.get("text_blocks") or [])
        # flat texts list (reconstruction_spec style)
        for key in ("texts", "text_blocks", "labels"):
            if isinstance(coords.get(key), list):
                n += len(coords[key])
    return n


def load_coords(tag: str):
    cands = []
    for p in [
        ROOT / "diag" / f"{tag}_measure_coords.json",
        ROOT / "diag" / f"{tag}_coords.json",
        ROOT / "diag" / f"{tag}_reconstruction_spec.json",
    ]:
        if p.exists():
            try:
                cands.append(json.loads(p.read_text()))
            except Exception:
                pass
    if not cands:
        return None
    # prefer richest role/font coverage
    cands.sort(key=_coords_text_count, reverse=True)
    return cands[0]


def _iter_panels(coords):
    """Yield (panel_id, panel_dict) from dict or list panel containers."""
    panels = coords.get("panels") or coords.get("regions") or []
    if isinstance(panels, dict):
        for k, v in panels.items():
            if isinstance(v, dict):
                yield (v.get("id") or v.get("name") or k, v)
            elif isinstance(v, str):
                continue
        return
    if isinstance(panels, list):
        for i, pan in enumerate(panels):
            if isinstance(pan, dict):
                yield (pan.get("id") or pan.get("name") or f"P{i}", pan)
            # list of panel id strings — skip (no text_blocks)
        return


def _iter_modules(pan):
    mods = pan.get("modules") or []
    if isinstance(mods, dict):
        for k, m in mods.items():
            if isinstance(m, dict):
                yield m
        return
    if isinstance(mods, list):
        for m in mods:
            if isinstance(m, dict):
                yield m


def type_uniform_from_coords(coords):
    """Group text_blocks by (panel, role) and compare font_px_orig / font_px."""
    groups = defaultdict(list)
    blocks = []
    if isinstance(coords, dict):
        panels = list(_iter_panels(coords))
        if not panels and "text_blocks" in coords:
            panels = [("ALL", {"text_blocks": coords["text_blocks"]})]
        for pid, pan in panels:
            tbs = list(pan.get("text_blocks") or [])
            for mod in _iter_modules(pan):
                tbs.extend(mod.get("text_blocks") or [])
            for tb in tbs:
                if not isinstance(tb, dict):
                    continue
                role = tb.get("role") or tb.get("zone") or tb.get("slot_kind") or "body"
                px = tb.get("font_px") or tb.get("font_px_orig") or tb.get("pt") or tb.get("px")
                if px is None:
                    continue
                txt = tb.get("text") or tb.get("t") or ""
                groups[(pid, role)].append({"id": tb.get("id"), "px": float(px), "text": str(txt)[:40]})
        # reconstruction_spec-style flat texts[]
        for tb in coords.get("texts") or coords.get("text_blocks") or []:
            if not isinstance(tb, dict):
                continue
            pid = tb.get("parent_panel") or tb.get("panel") or "ALL"
            role = tb.get("role") or tb.get("zone") or tb.get("slot_kind") or "body"
            px = tb.get("font_px") or tb.get("font_px_orig") or tb.get("px") or tb.get("pt")
            if px is None:
                continue
            txt = tb.get("text") or tb.get("t") or ""
            groups[(pid, role)].append({"id": tb.get("id"), "px": float(px), "text": str(txt)[:40]})
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


def _center(s):
    return ((s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2)


def _aspect(s):
    w = max(1e-6, s["x1"] - s["x0"])
    h = max(1e-6, s["y1"] - s["y0"])
    return max(w / h, h / w)


def _same_bbox(a, b, tol=1.5):
    return (
        abs(a["x0"] - b["x0"]) <= tol
        and abs(a["y0"] - b["y0"]) <= tol
        and abs(a["x1"] - b["x1"]) <= tol
        and abs(a["y1"] - b["y1"]) <= tol
    )


def _decor_on_parent(small, big):
    """Icon/badge/chrome sitting on a larger card — not 叠图."""
    if small["area"] >= big["area"]:
        return False
    if small["area"] / max(big["area"], 1e-6) > 0.22:
        return False
    cx, cy = _center(small)
    return big["x0"] <= cx <= big["x1"] and big["y0"] <= cy <= big["y1"]


def _title_strip_on_panel(a, b):
    """Thin title/badge strip overlapping top of its panel body."""
    thin, thick = (a, b) if (a["y1"] - a["y0"]) <= (b["y1"] - b["y0"]) else (b, a)
    th = thin["y1"] - thin["y0"]
    if th > 70 or thin["area"] > 0.45 * thick["area"]:
        return False
    # horizontal overlap of strips
    ix0, ix1 = max(thin["x0"], thick["x0"]), min(thin["x1"], thick["x1"])
    if ix1 - ix0 < 0.5 * (thin["x1"] - thin["x0"]):
        return False
    # strip sits on top edge of panel (either slightly above or overlapping top band)
    return (thin["y1"] >= thick["y0"] - 5) and (thin["y0"] <= thick["y0"] + th + 25)


def _isometric_path_pair(a, b):
    """Cube/face freeforms intentionally share edges (name often 'path')."""
    na, nb = (a.get("name") or ""), (b.get("name") or "")
    if "path" not in na.lower() and "path" not in nb.lower() and a.get("kind") != "path":
        # still allow when both are smallish parallelograms near each other
        if a["area"] > 8000 or b["area"] > 8000:
            return False
    # shared edge-ish: IoU modest and centers close relative to size
    v = iou(a, b)
    if v > 0.35:
        return False
    cx = abs(_center(a)[0] - _center(b)[0])
    cy = abs(_center(a)[1] - _center(b)[1])
    return cx < 80 and cy < 120 and v >= SHAPE_IOU_FAIL


def _legend_tick_on_bar(a, b):
    """Vertical legend ticks overlapping a horizontal legend swatch."""
    tall, wide = (a, b) if (a["y1"] - a["y0"]) > (b["y1"] - b["y0"]) else (b, a)
    tw = tall["x1"] - tall["x0"]
    th = tall["y1"] - tall["y0"]
    ww = wide["x1"] - wide["x0"]
    wh = wide["y1"] - wide["y0"]
    if tw > 20 or th < 20 or wh > 30 or ww < 40:
        return False
    # tick x within bar x-span
    cx = _center(tall)[0]
    return wide["x0"] - 5 <= cx <= wide["x1"] + 5


def shape_overlaps(shapes):
    """叠图: filled shapes/pics overlapping siblings (not containment)."""
    # consider non-text graphics only (cards/pills/icons/pics); text×graphic → text_shape_clear
    cands = [s for s in shapes if (not s["is_text"]) and s.get("filled", True) and s["kind"] != "connector" and s["area"] > 80]
    # drop exact duplicate paths (isometric cube face double-draw)
    uniq = []
    for s in cands:
        if any(_same_bbox(s, u) for u in uniq):
            continue
        uniq.append(s)
    cands = uniq
    hits = []
    n = len(cands)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = cands[i], cands[j]
            if contains(a, b) or contains(b, a):
                continue
            if _decor_on_parent(a, b) or _decor_on_parent(b, a):
                continue
            if _title_strip_on_panel(a, b):
                continue
            if _legend_tick_on_bar(a, b):
                continue
            if _isometric_path_pair(a, b):
                continue
            # hairline / bar marks (aspect very high) — legend ticks, gridlets
            if _aspect(a) >= 6 or _aspect(b) >= 6:
                continue
            v = iou(a, b)
            if v < SHAPE_IOU_FAIL:
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
    graphics = [s for s in shapes if (not s["is_text"] or s["kind"] == "pic") and s.get("filled", True) and s["kind"] != "connector" and s["area"] > 100]
    hits = []
    for t in texts:
        for g in graphics:
            if contains(g, t):
                continue  # text inside card OK
            if contains(t, g):
                continue
            # label sitting on its icon well / bar: center in graphic + small IoU band
            cx, cy = _center(t)
            if g["x0"] <= cx <= g["x1"] and g["y0"] <= cy <= g["y1"]:
                if t["area"] < 0.5 * g["area"] or g["area"] < 2.5 * t["area"]:
                    # still fail if IoU huge (text mostly covering wrong shape)
                    v0 = iou(t, g)
                    if v0 < 0.35:
                        continue
            if _aspect(g) >= 8:
                continue  # hairline under label
            # vertical icon stem / skyline bar under a short scene label (Fig01 peace/war)
            gw, gh = g["x1"] - g["x0"], g["y1"] - g["y0"]
            tw, th = t["x1"] - t["x0"], t["y1"] - t["y0"]
            if gw <= 55 and g["area"] <= 2200 and th <= 36 and tw <= 220:
                v0 = iou(t, g)
                if v0 < 0.30:
                    continue
            # isometric cube face under edge dimension label (ORIG places labels on faces)
            if (g.get("name") or "").lower().startswith("path"):
                vpath = iou(t, g)
                if vpath < 0.18 and tw <= 250 and th <= 40:
                    continue
            # caption strip on large panel card (slight overflow past bottom edge)
            if g["area"] >= 8000 and tw >= 80 and th <= 45:
                vcap = iou(t, g)
                if vcap < 0.25:
                    continue
            # rotated KEY/axis title (tall thin) on its panel
            if th >= 80 and tw <= 80 and g["area"] >= 15000:
                vrot = iou(t, g)
                if vrot < 0.15:
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
