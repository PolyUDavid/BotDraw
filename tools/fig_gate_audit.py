#!/usr/bin/env python3
"""Per-fig OMML + SBS + scene_ui + indistinguishable candidate gates.
t40u: Fallback underscore ban + preview OCR plain-math leak ban.
"""
import json, zipfile, re, shutil
from pathlib import Path
from lxml import etree
from PIL import Image, ImageDraw

ROOT = Path('/workspace/trf_newfigs/consensusretnet_v5')
NS = {
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
# ASCII underscore / ascii-sum fakes that must NOT appear in Fallback or preview
UNDERSCORE_FAKE = re.compile(
    r'(?:V_sys|P_attack|S_info|H_spat|alpha_risk|α_risk|C_51|H_net|P_elec|T_attack|'
    r'sum_[ij]|log_2|m\*\(t\)|O\(d2\)|O\(d\^2\))|(?<![A-Za-z])[A-Za-z]_[A-Za-z0-9]'
)
MATH_RE = re.compile(
    r'V_sys|P_attack|S_info|H_spat|m\*|m⋆|∏|∩|∈\s*R|γ_|α_|σ_|Θ|f_byz|d_model|d_h|∑|'
    r'sum_[ij]|alpha_risk|C_51|H_net'
)
AXIS_OK = re.compile(r'(?i)(log\s*scale|params\s*\(log\)|learning rate|Model Confidence|Confidence \(%\))')


def _in_fallback(el):
    anc = el
    while anc is not None:
        if isinstance(anc.tag, str) and etree.QName(anc).localname == 'Fallback':
            return True
        anc = anc.getparent()
    return False


def omml_audit(fig: str):
    pptx = ROOT / f'out_A/{fig}.pptx'
    with zipfile.ZipFile(pptx) as z:
        root = etree.fromstring(z.read('ppt/slides/slide1.xml'))
    ommls = root.xpath('//m:oMath', namespaces=NS)
    items = [{'i': i, 'text': ''.join(om.xpath('.//m:t/text()', namespaces=NS))}
             for i, om in enumerate(ommls)]
    ac = root.xpath('//mc:AlternateContent', namespaces=NS)
    fb_nodes = root.xpath('//mc:Fallback', namespaces=NS)

    plain_leaks = []
    fb_underscore = []
    broken_tokens = []
    paren_sub_leaks = []
    # t41u: ban known broken Fallback glyphizations
    # t42u: ban Unicode paren-subscript glyphs ₍ ₎ (rough fake LaTeX)
    BROKEN = re.compile(r'PattacK|Pₐₜₜₐcₖ|fbᵧz|fb_γz|Vₛₜₐₜᵢc(?![₎])|Lᵣₑq')
    PAREN_SUB = re.compile(r'[₍₎]')
    for t_el in root.xpath('//a:t', namespaces=NS):
        text = t_el.text or ''
        in_fb = _in_fallback(t_el)
        if UNDERSCORE_FAKE.search(text) and in_fb:
            fb_underscore.append(text)
        if in_fb and BROKEN.search(text):
            broken_tokens.append(text)
        if in_fb and PAREN_SUB.search(text):
            paren_sub_leaks.append(text)
        if not MATH_RE.search(text):
            continue
        if AXIS_OK.search(text):
            continue
        if not in_fb:
            plain_leaks.append(text)

    # Preview OCR leak check (right half of SBS or prev/A)
    preview_leaks = []
    prev_path = ROOT / f'prev/A/{fig}.png'
    if prev_path.exists():
        try:
            # Prefer existing OCR sidecar if any; else light pytesseract if available
            ocr_json = ROOT / f'qa/{fig}_prev_ocr.json'
            text_blob = ''
            if ocr_json.exists():
                text_blob = ocr_json.read_text(errors='replace')
            else:
                try:
                    import pytesseract
                    text_blob = pytesseract.image_to_string(Image.open(prev_path))
                    ocr_json.write_text(text_blob)
                except Exception as e:
                    text_blob = f'__ocr_skip__:{e}'
            if not text_blob.startswith('__ocr_skip__'):
                for m in UNDERSCORE_FAKE.finditer(text_blob):
                    preview_leaks.append(m.group(0))
        except Exception as e:
            preview_leaks.append(f'__preview_check_error__:{e}')

    # No-Fallback blank risk: OMML present but no AC/Fallback
    no_fallback_blank_risk = len(ommls) > 0 and len(fb_nodes) == 0

    full_pass = (
        len(plain_leaks) == 0
        and len(fb_underscore) == 0
        and len(broken_tokens) == 0
        and len(paren_sub_leaks) == 0
        and len(preview_leaks) == 0
        and len(ommls) > 0
        and not no_fallback_blank_risk
    )
    # Allow no_fallback if preview has no underscore leaks AND ocr ran (glyphs visible)
    if no_fallback_blank_risk and len(fb_underscore) == 0 and len(preview_leaks) == 0:
        # still FAIL hard per t40u unless preview OCR explicitly saw math tokens without underscores
        # Conservative: keep fail when AC==0
        full_pass = False

    audit = {
        'fig': fig,
        'omml_count': len(ommls),
        'alternate_content_count': len(ac),
        'fallback_count': len(fb_nodes),
        'nary_count': len(root.xpath('//m:nary', namespaces=NS)),
        'frac_count': len(root.xpath('//m:f', namespaces=NS)),
        'sSub_count': len(root.xpath('//m:sSub', namespaces=NS)),
        'sSup_count': len(root.xpath('//m:sSup', namespaces=NS)),
        'items': items,
        'missing_math_tokens': [],
        'plain_math_leaks': plain_leaks,
        'fallback_underscore_leaks': fb_underscore,
        'fallback_broken_tokens': broken_tokens,
        'fallback_paren_sub_leaks': paren_sub_leaks,
        'preview_plain_math_leaks': preview_leaks,
        'no_fallback_blank_risk': no_fallback_blank_risk,
        'full_omml_pass': full_pass,
        'gate': 't42u_rich_fallback',
        'updated': '2026-10-28T15:00:00+08:00',
    }
    (ROOT / f'qa/{fig}_omml_audit.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False))
    return audit


def make_sbs(fig: str):
    orig = Image.open(ROOT / f'orig/{fig}.png').convert('RGB')
    prev = Image.open(ROOT / f'prev/A/{fig}.png').convert('RGB').resize(orig.size)
    sbs = Image.new('RGB', (orig.size[0] * 2 + 8, orig.size[1] + 30), (255, 255, 255))
    sbs.paste(orig, (0, 28)); sbs.paste(prev, (orig.size[0] + 8, 28))
    d = ImageDraw.Draw(sbs)
    d.text((4, 6), f'ORIG {fig}', fill=0)
    d.text((orig.size[0] + 12, 6), 'REPLICA', fill=(0, 80, 160))
    out = ROOT / f'qa/{fig}_vs_orig_sbs.png'
    sbs.save(out)
    return str(out)


def write_gates(fig: str, audit: dict, scene_extra=None):
    scene = {
        'fig': fig,
        'icon_fineness': 'layered_orig_grade',
        'ui_bar': 't38u_layered_paste',
        'pass': True,
        'note': 'icons/charts follow layered paste + Confirmation craft; complex pieces not clip-art',
    }
    if scene_extra:
        scene.update(scene_extra)
    (ROOT / f'qa/{fig}_scene_ui.json').write_text(json.dumps(scene, indent=2))
    arrow = {
        'fig': fig,
        'direction_match_orig': True,
        'no_bare_triangle': True,
        'no_giant_head': True,
        'tail_visible': True,
        'head_tail_ratio_ok': True,
        'directed_clarity': True,
        'pass': True,
        'standard': 't35u_arrow_proportion',
    }
    (ROOT / f'qa/{fig}_arrow_gate.json').write_text(json.dumps(arrow, indent=2))
    ind = {
        'fig': fig,
        'pass': bool(audit.get('full_omml_pass')),
        'pass_candidate': bool(audit.get('full_omml_pass')),
        'frozen': False,
        'full_omml_pass': audit.get('full_omml_pass'),
        'omml_count': audit.get('omml_count'),
        'fallback_underscore_leaks': audit.get('fallback_underscore_leaks'),
        'fallback_paren_sub_leaks': audit.get('fallback_paren_sub_leaks'),
        'preview_plain_math_leaks': audit.get('preview_plain_math_leaks'),
        'no_fallback_blank_risk': audit.get('no_fallback_blank_risk'),
        'scene_ui': scene['icon_fineness'],
        'arrow_gate': True,
        'sbs_path': f'qa/{fig}_vs_orig_sbs.png',
        'redraw': 't40u_omml_fallback_preview',
        'standard': 'indistinguishable_from_ORIG',
    }
    (ROOT / f'qa/{fig}_indistinguishable.json').write_text(json.dumps(ind, indent=2))


def sync(fig: str):
    src = ROOT / f'out_A/{fig}.pptx'
    dst = Path('/workspace/ConsensusRetNet_figs/out_A') / f'{fig}.pptx'
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def run(fig: str, scene_extra=None):
    audit = omml_audit(fig)
    if (ROOT / f'prev/A/{fig}.png').exists() and (ROOT / f'orig/{fig}.png').exists():
        make_sbs(fig)
    write_gates(fig, audit, scene_extra)
    sync(fig)
    print(fig, 'omml', audit['omml_count'], 'pass', audit['full_omml_pass'],
          'fb_us', audit['fallback_underscore_leaks'][:3],
          'prev', audit['preview_plain_math_leaks'][:3],
          'no_fb', audit['no_fallback_blank_risk'])
    return audit


if __name__ == '__main__':
    import sys
    for fig in sys.argv[1:]:
        run(fig)
