#!/usr/bin/env python3
"""Audit real m:oMath count, arrow head/tailEnd, and plain-math residue in PPTX."""
import re, sys, zipfile, json
from pathlib import Path

PLAIN_RES = [
    r'γ\s*=', r'γ\s*∈', r'α_risk', r'α\s*=', r'κ\b', r'ε\b',
    r'L_req', r'f_byz', r'P_attack', r'D_γ', r'K\^T', r'd_h\b',
    r'd_model', r'S_info', r'H_spat', r'x\(t\)', r'm\*\(t\)',
    r'ℝ', r'R\^1', r'R¹²', r'∈\s*R', r'O\(1\)', r'→\s*0', r'→\s*Hybrid',
    r'Δα', r'σ_sec', r'T_h_req', r'N_nodes',
]

def texts_outside_omml(xml: str):
    """Collect a:t text that is NOT inside m:oMath."""
    # strip oMath blocks first
    cleaned = re.sub(r'<m:oMath[\s>][\s\S]*?</m:oMath>', '', xml)
    return re.findall(r'<a:t[^>]*>([^<]*)</a:t>', cleaned)

def audit(pptx: Path):
    z = zipfile.ZipFile(pptx)
    slides = [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]
    omml = 0
    head_nz = tail_nz = 0
    head_none = tail_none = 0
    poly_heads = 0
    shaft_named = 0
    plain_hits = []
    for s in slides:
        xml = z.read(s).decode('utf-8', errors='replace')
        omml += len(re.findall(r'<m:oMath[\s>]', xml))
        for m in re.finditer(r'<a:headEnd([^/>]*)/?>', xml):
            a = m.group(1)
            if re.search(r'type\s*=\s*"none"', a) or 'type=' not in a:
                head_none += 1
            else:
                head_nz += 1
        for m in re.finditer(r'<a:tailEnd([^/>]*)/?>', xml):
            a = m.group(1)
            if re.search(r'type\s*=\s*"none"', a) or 'type=' not in a:
                tail_none += 1
            else:
                tail_nz += 1
        names = re.findall(r'<p:cNvPr[^>]*name="([^"]*)"', xml)
        poly_heads += sum(1 for n in names if n.endswith('_head') or n.endswith('arr_head'))
        shaft_named += sum(1 for n in names if n.endswith('_shaft') or n.endswith('arr_shaft'))
        blob_texts = texts_outside_omml(xml)
        for t in blob_texts:
            t = t.strip()
            if not t:
                continue
            for p in PLAIN_RES:
                if re.search(p, t):
                    plain_hits.append(t[:100])
                    break
    # unique plain
    seen = set(); plain_u = []
    for t in plain_hits:
        if t not in seen:
            seen.add(t); plain_u.append(t)
    return {
        'pptx': str(pptx),
        'omml_count': omml,
        'arrowEnds': head_nz + tail_nz,
        'headEnds': head_nz,
        'tailEnds': tail_nz,
        'poly_heads': poly_heads,
        'shaft_named': shaft_named,
        'plain_math_residue': len(plain_u),
        'plain_samples': plain_u[:30],
        'pass_omml_nonzero': omml > 0,
        'pass_arrows': (head_nz + tail_nz) > 0 or poly_heads >= 4,
        'pass_plain_zero': len(plain_u) == 0,
    }

def main():
    paths = sys.argv[1:] or [
        f'/workspace/ConsensusRetNet_figs/out_A/Fig{i:02d}.pptx' for i in range(1, 10)
    ]
    rows = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            print('MISSING', p); continue
        a = audit(p)
        rows.append(a)
        status = 'PASS' if (a['pass_arrows'] and a['pass_plain_zero'] and a['omml_count'] > 0) else 'FAIL'
        # stricter: need native arrowEnds for directed clarity
        if a['arrowEnds'] == 0:
            status = 'FAIL'
        print(f"{p.name}: {status} omml={a['omml_count']} arrowEnds={a['arrowEnds']} "
              f"(H={a['headEnds']} T={a['tailEnds']} polyH={a['poly_heads']}) "
              f"plain={a['plain_math_residue']}")
        if a['plain_samples']:
            print('  plain:', a['plain_samples'][:12])
    out = Path('/workspace/trf_newfigs/consensusretnet_v5/qa/audit_omml_arrows.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(out, 'w'), indent=2, ensure_ascii=False)
    print('wrote', out)

if __name__ == '__main__':
    main()
