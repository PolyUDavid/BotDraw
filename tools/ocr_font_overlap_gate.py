#!/usr/bin/env python3
"""Hard OCR gate: font-size vs ORIG (h_med) + text–text bbox overlap on A preview.

Kevin t48u: PASS forbidden without this report.
Usage:
  FIG_ROOT=/path/to/figroot python tools/ocr_font_overlap_gate.py A Fig01 Fig02 ...
Writes qa/<fig>_ocr_font_overlap.json and merges summary into stdout.
Exit 1 if any fig fails hard gates.
"""
from __future__ import annotations
import difflib, hashlib, json, os, statistics as st, sys
from pathlib import Path

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(os.environ.get("FIG_ROOT", ".")).resolve()
CACHE = ROOT / ".ocr_cache"
CACHE.mkdir(exist_ok=True)
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)
eng = RapidOCR()

# Normalized canvas width for comparable heights (same as qa_ocr2)
NORM_W = 1672.0
# Overlap: IoU threshold for text–text collide
IOU_FAIL = 0.08
# Soft gap: centers closer than this fraction of smaller height with any IoU>0
GAP_FRAC = 0.25
# Font: paired height ratio band
H_MED_LO, H_MED_HI = 0.92, 1.22  # hard reject outside; preferred 1.00–1.16
H_OUTLIER_LO, H_OUTLIER_HI = 0.75, 1.40  # per-pair extremes
MIN_CONF = 0.70
MIN_LEN = 2


def ocr(path: Path):
    key = hashlib.md5(path.read_bytes()).hexdigest()
    cf = CACHE / f"{key}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    im = Image.open(path).convert("RGB")
    s = NORM_W / im.size[0]
    r, _ = eng(str(path))
    out = []
    for b, t, c in r or []:
        xs = [p[0] * s for p in b]
        ys = [p[1] * s for p in b]
        out.append(
            {
                "t": t,
                "c": float(c),
                "x0": min(xs),
                "y0": min(ys),
                "x1": max(xs),
                "y1": max(ys),
                "x": (min(xs) + max(xs)) / 2,
                "y": (min(ys) + max(ys)) / 2,
                "h": max(ys) - min(ys),
                "w": max(xs) - min(xs),
            }
        )
    cf.write_text(json.dumps(out, ensure_ascii=False))
    return out


def iou(a, b):
    ix0, iy0 = max(a["x0"], b["x0"]), max(a["y0"], b["y0"])
    ix1, iy1 = min(a["x1"], b["x1"]), min(a["y1"], b["y1"])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    aa = max(1e-6, (a["x1"] - a["x0"]) * (a["y1"] - a["y0"]))
    ba = max(1e-6, (b["x1"] - b["x0"]) * (b["y1"] - b["y0"]))
    return inter / (aa + ba - inter)


def norm(t: str) -> str:
    return "".join(ch for ch in t.lower() if ch.isalnum())


def filter_boxes(boxes):
    return [b for b in boxes if b["c"] >= MIN_CONF and len(norm(b["t"])) >= MIN_LEN and b["h"] >= 4]


def find_overlaps(boxes):
    hits = []
    n = len(boxes)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = boxes[i], boxes[j]
            # skip near-identical duplicate OCR of same glyph cluster
            if difflib.SequenceMatcher(None, norm(a["t"]), norm(b["t"])).ratio() >= 0.95:
                # same string twice — still fail if distinct positions with overlap
                if abs(a["x"] - b["x"]) < 3 and abs(a["y"] - b["y"]) < 3:
                    continue
            v = iou(a, b)
            gap = ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
            min_h = min(a["h"], b["h"])
            collide = v >= IOU_FAIL or (v > 0 and gap < GAP_FRAC * min_h)
            if collide:
                hits.append(
                    {
                        "a": a["t"][:60],
                        "b": b["t"][:60],
                        "iou": round(v, 3),
                        "gap": round(gap, 1),
                        "a_box": [round(a["x0"]), round(a["y0"]), round(a["x1"]), round(a["y1"])],
                        "b_box": [round(b["x0"]), round(b["y0"]), round(b["x1"]), round(b["y1"])],
                    }
                )
    return hits


def pair_heights(orig, redraw):
    hr, items, miss = [], [], []
    for a in orig:
        na = norm(a["t"])
        if len(na) < 3 or a["c"] < 0.75:
            continue
        best, bs = None, 0.0
        for b in redraw:
            nb = norm(b["t"])
            if len(nb) < 3:
                continue
            r = difflib.SequenceMatcher(None, na, nb).ratio()
            if r > bs:
                bs, best = r, b
        if best and bs >= 0.85 and abs(len(norm(best["t"])) - len(na)) <= max(2, 0.15 * len(na)):
            q = best["h"] / max(a["h"], 1e-6)
            hr.append(q)
            items.append(
                {
                    "orig": a["t"][:50],
                    "redraw": best["t"][:50],
                    "h_ratio": round(q, 3),
                    "orig_h": round(a["h"], 1),
                    "redraw_h": round(best["h"], 1),
                }
            )
        else:
            miss.append(a["t"][:50])
    return hr, items, miss


def gate_one(tag: str, variant: str):
    op = ROOT / "orig" / f"{tag}.png"
    if not op.exists():
        op = ROOT / "orig" / f"{tag}_full.png"
    pp = ROOT / "prev" / variant / f"{tag}.png"
    if not pp.exists():
        pp = ROOT / "prev" / variant / f"{tag}_full.png"
    if not op.exists() or not pp.exists():
        return {
            "fig": tag,
            "pass": False,
            "error": f"missing orig={op.exists()} prev={pp.exists()}",
        }
    o = filter_boxes(ocr(op))
    p = filter_boxes(ocr(pp))
    overlaps = find_overlaps(p)
    hr, items, miss = pair_heights(o, p)
    h_med = round(st.median(hr), 3) if hr else None
    outliers = [it for it in items if it["h_ratio"] < H_OUTLIER_LO or it["h_ratio"] > H_OUTLIER_HI]
    # also flag mild outliers outside preferred band for report
    mild = [it for it in items if it["h_ratio"] < 0.90 or it["h_ratio"] > 1.25]
    font_pass = (
        h_med is not None
        and H_MED_LO <= h_med <= H_MED_HI
        and len(outliers) == 0
    )
    overlap_pass = len(overlaps) == 0
    ok = font_pass and overlap_pass
    rep = {
        "fig": tag,
        "variant": variant,
        "gate": "ocr_font_overlap",
        "version": "2026-10-28-t48u",
        "pass": ok,
        "font_pass": font_pass,
        "overlap_pass": overlap_pass,
        "h_med": h_med,
        "h_min": round(min(hr), 3) if hr else None,
        "h_max": round(max(hr), 3) if hr else None,
        "n_paired": len(hr),
        "n_orig_ocr": len(o),
        "n_redraw_ocr": len(p),
        "n_overlap": len(overlaps),
        "overlaps": overlaps[:40],
        "outliers": outliers[:30],
        "mild_size_flags": mild[:30],
        "miss_sample": miss[:20],
        "thresholds": {
            "iou_fail": IOU_FAIL,
            "h_med_band": [H_MED_LO, H_MED_HI],
            "outlier_band": [H_OUTLIER_LO, H_OUTLIER_HI],
        },
    }
    outp = QA / f"{tag}_ocr_font_overlap.json"
    outp.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    return rep


def main():
    if len(sys.argv) < 3:
        print("Usage: ocr_font_overlap_gate.py <A|B> Fig01 [Fig02 ...]", file=sys.stderr)
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
                "h_med": r.get("h_med"),
                "n_overlap": r.get("n_overlap"),
                "font_pass": r.get("font_pass"),
                "overlap_pass": r.get("overlap_pass"),
                "error": r.get("error"),
            }
            for r in results
            if not r.get("pass")
        ],
    }
    (QA / f"ocr_font_overlap_summary_{variant}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    for r in results:
        status = "PASS" if r.get("pass") else "FAIL"
        print(
            f"{r['fig']}: {status} h_med={r.get('h_med')} overlaps={r.get('n_overlap')} "
            f"font={r.get('font_pass')} ov={r.get('overlap_pass')} err={r.get('error')}",
            flush=True,
        )
    sys.exit(0 if all(r.get("pass") for r in results) else 1)


if __name__ == "__main__":
    main()
