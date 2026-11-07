"""New generic candidate primitives. Standard library only; no OCR/render/asset access.
Nothing here proves visual equivalence, source correctness, or native Office success.
"""
from __future__ import annotations
import copy
import difflib
import hashlib
import math
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def math_signature(xml: str):
    """Conservative complete-tree signature for math roots supplied by the caller.

    Includes all descendants, attributes, order and text (not just m:t). Formatting
    changes may intentionally change this signature. No semantic-equivalence claim.
    Reject DTD/entities rather than resolving untrusted external input.
    """
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", xml, re.I):
        raise ValueError("DTD/entities are not allowed")
    root = ET.fromstring(xml)
    if not root.tag.startswith("{" + MATH_NS + "}"):
        raise ValueError("Supply a selected math root, not a full slide")

    def node(el):
        text = el.text or ""
        if el.tag != "{" + MATH_NS + "}t" and not text.strip():
            text = ""
        return (el.tag, tuple(sorted(el.attrib.items())), text,
                tuple(node(child) for child in el))
    return node(root)


def audit_coverage(original_ids, reviewed, extras=()):
    """reviewed maps stable source IDs to reviewed/unknown/defect/correct results.

    Count of records looked at is separate from correctness. An erratum changes a
    result, not the fixed denominator. Extras never inflate original coverage.
    """
    ids = list(original_ids)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate original source ID")
    if set(reviewed) - set(ids):
        raise ValueError("Unregistered source IDs must be separate extras")
    valid = {"reviewed", "unknown", "defect", "correct"}
    if any(v not in valid for v in reviewed.values()):
        raise ValueError("Unknown review status")
    return {"original_total": len(ids), "original_looked_at": len(reviewed),
            "original_not_looked_at": sorted(set(ids) - set(reviewed)),
            "unknown": sorted(k for k, v in reviewed.items() if v == "unknown"),
            "known_defects": sorted(k for k, v in reviewed.items() if v == "defect"),
            "explicitly_correct": sum(v == "correct" for v in reviewed.values()),
            "extra_count": len(list(extras)), "coverage_is_correctness_proof": False}


def _norm(text):
    # Do not case-fold scientific symbols, discard operators, or collapse Greek.
    return "".join(unicodedata.normalize("NFC", text).split())


def _protected(text):
    return (tuple(re.findall(r"[<≤>≥=≠≈]", text)),
            tuple(re.findall(r"[+−-]?\d+(?:\.\d+)?", text)))


def _assignment(cost):
    """Minimum-cost rectangular assignment, rows <= columns, potentials method."""
    n = len(cost)
    if not n:
        return []
    m = len(cost[0])
    if n > m or any(len(row) != m for row in cost):
        raise ValueError("Rectangular rows <= columns required")
    u, v, p, way = [0.] * (n+1), [0.] * (m+1), [0] * (m+1), [0] * (m+1)
    for i in range(1, n+1):
        p[0] = i
        j0 = 0
        best, used = [float("inf")] * (m+1), [False] * (m+1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float("inf"), 0
            for j in range(1, m+1):
                if not used[j]:
                    cur = cost[i0-1][j-1] - u[i0] - v[j]
                    if cur < best[j]:
                        best[j], way[j] = cur, j0
                    if best[j] < delta:
                        delta, j1 = best[j], j
            for j in range(m+1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    best[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    result = [-1] * n
    for j in range(1, m+1):
        if p[j]:
            result[p[j]-1] = j-1
    return result


def pair_boxes(source, redraw, *, max_distance=0.16, similarity=0.80):
    """Input centres x/y in the SAME normalized source coordinate system.

    Fields: id, text, x, y, orientation (h/v), zone. No hidden confidence filtering.
    Direction is caller-supplied; unknown does not silently become horizontal.
    Returns raw matches/rejections/unmatched, never a visual or scientific PASS.
    """
    for side in (source, redraw):
        if len({b["id"] for b in side}) != len(side):
            raise ValueError("Duplicate OCR box IDs")
        for box in side:
            if not all(math.isfinite(float(box[k])) for k in ("x", "y")):
                raise ValueError("Non-finite OCR coordinates")
    n, m = len(source), len(redraw)
    cost = [[1.0] * (m+n) for _ in source]
    valid, rejected = {}, []
    for i, a in enumerate(source):
        for j, b in enumerate(redraw):
            ta, tb = _norm(a["text"]), _norm(b["text"])
            reason = None
            if a.get("orientation") not in ("h", "v") or a.get("orientation") != b.get("orientation"):
                reason = "direction"
            elif a.get("zone") != b.get("zone"):
                reason = "zone"
            elif _protected(ta) != _protected(tb):
                reason = "relations_or_numeric_bounds"
            elif not ta or not tb or min(len(ta), len(tb))/max(len(ta), len(tb)) < .80:
                reason = "partial_entity"
            elif ta != tb and (ta in tb or tb in ta):
                # Conservative: a missing base or condition is not a complete label,
                # even when the suffix is long enough to clear similarity thresholds.
                reason = "proper_substring_entity"
            dist = math.hypot(a["x"]-b["x"], a["y"]-b["y"])
            sim = difflib.SequenceMatcher(None, ta, tb).ratio()
            if reason is None and (dist > max_distance or sim < similarity):
                reason = "distance_or_text"
            if reason:
                rejected.append({"source": a["id"], "redraw": b["id"], "reason": reason})
            else:
                score = 2*dist + .6*(1-sim)
                if score >= 1.0:
                    rejected.append({"source": a["id"], "redraw": b["id"], "reason": "unmatched_cost"})
                    continue
                cost[i][j] = score
                valid[i, j] = (sim, dist)
    # Invalid real pairs cost more than dedicated unmatched columns.
    for i in range(n):
        for j in range(m):
            if (i, j) not in valid:
                cost[i][j] = 1000.
    pairs, used_s, used_r = [], set(), set()
    for i, j in enumerate(_assignment(cost)):
        if (i, j) in valid:
            sim, dist = valid[i, j]
            pairs.append({"source": source[i]["id"], "redraw": redraw[j]["id"],
                          "similarity": sim, "distance": dist})
            used_s.add(i)
            used_r.add(j)
    return {"pairs": pairs, "source_total": n, "redraw_total": m,
            "unmatched_source": [a["id"] for i, a in enumerate(source) if i not in used_s],
            "unmatched_redraw": [b["id"] for j, b in enumerate(redraw) if j not in used_r],
            "rejected": rejected, "visual_or_source_pass_inferred": False}


def _safe_rel(value):
    p = PurePosixPath(value)
    if not value or "\\" in value or p.is_absolute() or ".." in p.parts or str(p) == ".":
        raise ValueError("Expected a safe relative POSIX path")
    return p


def resolve_variant(root, tag, variant, *, supplementary=False):
    if variant not in ("A", "B") or not tag or any(c in tag for c in ("/", "\\")) or tag in (".", ".."):
        raise ValueError("Explicit figure tag and A/B required")
    p = Path(root) / ("out_"+variant)
    if supplementary:
        p /= "SI"
    p /= tag+".pptx"
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def review_semantic(raw_report, exceptions):
    """Separate exception ledger; no rewrite of measured pass or findings."""
    raw = copy.deepcopy(raw_report)
    known = {f["id"] for f in raw.get("findings", [])}
    approved = set()
    for e in exceptions:
        if (e.get("finding_id") not in known or not e.get("source_evidence")
                or not e.get("object_ids") or e.get("geometry_unchanged") is not True):
            raise ValueError("Evidence, source geometry and specific known objects required")
        if e.get("review_status") == "reviewed_semantic_exception":
            approved.add(e["finding_id"])
    return {"measurement": raw, "exceptions": copy.deepcopy(exceptions),
            "unexcepted_finding_ids": sorted(known-approved),
            "measured_pass": raw.get("pass"), "overrides_gate_pass": False}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _source(root, rel):
    rel = _safe_rel(rel)
    p = Path(root)
    if p.is_symlink():
        raise ValueError("Symlink root refused")
    for part in rel.parts:
        p /= part
        if p.is_symlink():
            raise ValueError("Symlink member refused")
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def freeze_snapshot(source_root, destination, relative_files):
    """Explicit whitelist; destination must be new or empty. No recursive copying.

    Leaves a partial NEW destination on error for diagnosis; returns no completed
    manifest until all source/snapshot hashes and container CRC checks succeed.
    """
    paths = [str(_safe_rel(r)) for r in relative_files]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate delivery paths")
    dst = Path(destination)
    if dst.is_symlink() or (dst.exists() and any(dst.iterdir())):
        raise ValueError("Use a clean destination; never overwrite an old snapshot")
    dst.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for rel in paths:
        src = _source(source_root, rel)
        if src.suffix.lower() != ".pptx":
            raise ValueError("Only selected primary PPTX files belong in this snapshot")
        with zipfile.ZipFile(src) as z:
            if z.testzip() is not None:
                raise ValueError("Source ZIP CRC failed")
        manifest[rel] = {"sha256": sha256(src), "bytes": src.stat().st_size}
    for rel in paths:
        src, dest = _source(source_root, rel), dst / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as f:
            tmp = Path(f.name)
            with src.open("rb") as stream:
                for block in iter(lambda: stream.read(1 << 20), b""):
                    f.write(block)
        if sha256(tmp) != manifest[rel]["sha256"]:
            tmp.unlink()
            raise ValueError("Source changed during snapshot")
        os.replace(tmp, dest)
    for rel, entry in manifest.items():
        if sha256(_source(source_root, rel)) != entry["sha256"] or sha256(dst/rel) != entry["sha256"]:
            raise ValueError("Snapshot not frozen")
    return manifest


def make_zip(snapshot, manifest, output, *, root_name="ALL_FIGURES", limit_bytes=25_000_000):
    """One ordinary ZIP of caller-selected group; no network or auto splitting."""
    root = _safe_rel(root_name)
    if len(root.parts) != 1:
        raise ValueError("One common root directory name required")
    out = Path(output)
    if out.exists():
        raise FileExistsError(out)
    for rel, entry in manifest.items():
        if sha256(_source(snapshot, rel)) != entry["sha256"]:
            raise ValueError("Snapshot differs from the manifest")
    with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(manifest):
            z.write(_source(snapshot, rel), str(root / rel))
    if out.stat().st_size >= limit_bytes:
        raise ValueError("Archive exceeds the strict byte limit; not a completed pack")
    verify_zip(out, manifest, root_name=root_name)
    return {"bytes": out.stat().st_size, "sha256": sha256(out), "crc_ok": True}


def verify_zip(archive, manifest, *, root_name="ALL_FIGURES"):
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        expected = {str(PurePosixPath(root_name) / _safe_rel(rel)) for rel in manifest}
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Missing, duplicate, or unexpected ZIP members")
        if z.testzip() is not None:
            raise ValueError("ZIP CRC failure")
        for rel, entry in manifest.items():
            data = z.read(str(PurePosixPath(root_name) / rel))
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Archive bytes differ from frozen source")
    return True
