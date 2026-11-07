import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate", ROOT/"tools/quality_primitives.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def equation(body):
    return f'<m:oMath xmlns:m="{q.MATH_NS}">{body}</m:oMath>'


def box(uid, text="Label", x=.30, y=.30, direction="h", zone="panel"):
    return dict(id=uid, text=text, x=x, y=y, orientation=direction, zone=zone)


class MathTests(unittest.TestCase):
    def test_operator_attribute_not_just_text(self):
        a = equation('<m:nary><m:naryPr><m:chr m:val="∑"/></m:naryPr><m:e><m:r><m:t>x</m:t></m:r></m:e></m:nary>')
        self.assertNotEqual(q.math_signature(a), q.math_signature(a.replace('∑', '∏')))

    def test_relation_symbol_error(self):
        a = equation('<m:r><m:t>x&lt;z</m:t></m:r>')
        self.assertNotEqual(q.math_signature(a), q.math_signature(a.replace('&lt;', '≤')))

    def test_subscript_hierarchy(self):
        a = equation('<m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>')
        self.assertNotEqual(q.math_signature(a), q.math_signature(a.replace('sSub', 'sSup').replace('m:sub', 'm:sup')))

    def test_lower_upper_limits(self):
        a = equation('<m:limLow><m:e><m:r><m:t>f</m:t></m:r></m:e><m:lim><m:r><m:t>j</m:t></m:r></m:lim></m:limLow>')
        self.assertNotEqual(q.math_signature(a), q.math_signature(a.replace('limLow', 'limUpp')))

    def test_indentation_only_ignored(self):
        a = equation('<m:r><m:t>x</m:t></m:r>')
        b = equation('\n  <m:r>\n    <m:t>x</m:t>\n  </m:r>\n')
        self.assertEqual(q.math_signature(a), q.math_signature(b))

    def test_duplicate_choice_term_not_hidden_by_fallback(self):
        a = equation('<m:r><m:t>x</m:t></m:r>')
        b = equation('<m:r><m:t>x</m:t></m:r><m:r><m:t>x</m:t></m:r>')
        self.assertNotEqual(q.math_signature(a), q.math_signature(b))

    def test_reject_dtd(self):
        with self.assertRaises(ValueError):
            q.math_signature('<!DOCTYPE x [<!ENTITY xx "x">]>'+equation('<m:r/>'))

    def test_reject_slide_scope(self):
        with self.assertRaises(ValueError):
            q.math_signature('<slide/>')


class AuditTests(unittest.TestCase):
    def test_full_coverage_is_not_correctness(self):
        j = json.loads((ROOT/'fixtures/synthetic_contract.json').read_text())
        r = q.audit_coverage(j['source_index'], j['reviewed'], j['extra_math'])
        self.assertEqual(r['original_looked_at'], 3)
        self.assertEqual(r['explicitly_correct'], 1)
        self.assertEqual(len(r['unknown']), 1)
        self.assertEqual(len(r['known_defects']), 1)
        self.assertEqual(r['extra_count'], 1)
        self.assertFalse(r['coverage_is_correctness_proof'])

    def test_later_erratum_does_not_inflate_coverage(self):
        before = q.audit_coverage(['one'], {'one':'correct'})
        after = q.audit_coverage(['one'], {'one':'defect'})
        self.assertEqual(before['original_looked_at'], after['original_looked_at'])
        self.assertEqual(after['known_defects'], ['one'])

    def test_extra_cannot_silently_enter_original_index(self):
        with self.assertRaises(ValueError):
            q.audit_coverage(['one'], {'outside':'correct'})

    def test_duplicate_original_index_rejected(self):
        with self.assertRaises(ValueError):
            q.audit_coverage(['one', 'one'], {'one':'reviewed'})


class PairingTests(unittest.TestCase):
    def test_duplicate_source_does_not_reuse_candidate(self):
        r = q.pair_boxes([box('s1'),box('s2',x=.31)], [box('r1')])
        self.assertEqual(len(r['pairs']), 1)
        self.assertEqual(len(r['unmatched_source']), 1)

    def test_horizontal_vertical_same_label(self):
        r = q.pair_boxes([box('sH'),box('sV',direction='v')],
                         [box('rV',direction='v'),box('rH')])
        self.assertEqual({(p['source'],p['redraw'])for p in r['pairs']}, {('sH','rH'),('sV','rV')})

    def test_relation_mismatch_preserved(self):
        r = q.pair_boxes([box('s','x<z')], [box('r','x≤z')])
        self.assertEqual(r['unmatched_source'], ['s'])
        self.assertEqual(r['rejected'][0]['reason'], 'relations_or_numeric_bounds')

    def test_different_numeric_bound_not_paired(self):
        r = q.pair_boxes([box('s','x≥9')], [box('r','x≥8')])
        self.assertEqual(len(r['pairs']), 0)

    def test_subscript_fragment_not_full_entity(self):
        r = q.pair_boxes([box('s','Qindex')], [box('r','index')])
        self.assertEqual(r['unmatched_source'], ['s'])

    def test_same_label_far_panel_not_paired(self):
        r = q.pair_boxes([box('s')], [box('r',x=.9)])
        self.assertEqual(r['unmatched_redraw'], ['r'])

    def test_zone_not_ignored(self):
        r = q.pair_boxes([box('s')], [box('r',zone='other')])
        self.assertEqual(r['pairs'], [])

    def test_one_character_is_not_silently_removed(self):
        r = q.pair_boxes([box('s','x')], [box('r','x')])
        self.assertEqual(len(r['pairs']), 1)
        self.assertEqual(r['source_total'], 1)

    def test_unknown_orientation_is_not_horizontal(self):
        r = q.pair_boxes([box('s',direction='unknown')], [box('r')])
        self.assertEqual(r['pairs'], [])

    def test_fragments_not_silently_merged(self):
        r = q.pair_boxes([box('s','Xindex')], [box('r1','X'),box('r2','index',x=.32)])
        self.assertEqual(r['unmatched_source'], ['s'])
        self.assertEqual(len(r['unmatched_redraw']), 2)

    def test_global_assignment_resolves_competition(self):
        # s1 can match r1/r2, s2 only r1. Independent nearest greed fails.
        r = q.pair_boxes([box('s1',x=.40),box('s2',x=.25)],
                         [box('r1',x=.39),box('r2',x=.55)])
        self.assertEqual({(p['source'],p['redraw'])for p in r['pairs']}, {('s1','r2'),('s2','r1')})

    def test_empty_inputs(self):
        self.assertEqual(q.pair_boxes([],[])['pairs'], [])
        self.assertEqual(q.pair_boxes([box('s')],[])['unmatched_source'], ['s'])


class SemanticTests(unittest.TestCase):
    def test_exception_does_not_override_measured_fail(self):
        raw = {'pass':False,'findings':[{'id':'window-overlap'},{'id':'new-text-clipping'}]}
        e = {'finding_id':'window-overlap','source_evidence':'synthetic-source-roi',
             'object_ids':['event-A','event-B'],'geometry_unchanged':True,
             'review_status':'reviewed_semantic_exception'}
        r = q.review_semantic(raw,[e])
        self.assertFalse(r['measurement']['pass'])
        self.assertFalse(r['measured_pass'])
        self.assertEqual(r['unexcepted_finding_ids'], ['new-text-clipping'])
        self.assertFalse(r['overrides_gate_pass'])
        self.assertEqual(len(raw['findings']), 2)

    def test_no_evidence_no_exception(self):
        with self.assertRaises(ValueError):
            q.review_semantic({'pass':False,'findings':[{'id':'x'}]}, [{'finding_id':'x'}])


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src, self.dst = self.root/'source', self.root/'snapshot'
        self.paths = ['out_A/Example.pptx','out_B/Example.pptx']
        for rel in self.paths + ['out_A/Example_verified_ALTERNATIVE.pptx']:
            p = self.src/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            with zipfile.ZipFile(p,'w')as z:
                z.writestr('SYNTHETIC_CONTAINER_ONLY.txt',rel)

    def test_explicit_variant_resolver(self):
        self.assertEqual(q.resolve_variant(self.src,'Example','B'),self.src/self.paths[1])

    def test_missing_B_never_falls_back_to_A_or_backup(self):
        (self.src/self.paths[1]).unlink()
        backup = self.src/'backup/Example.pptx'
        backup.parent.mkdir()
        backup.write_bytes((self.src/self.paths[0]).read_bytes())
        with self.assertRaises(FileNotFoundError):
            q.resolve_variant(self.src,'Example','B')

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            q.freeze_snapshot(self.src,self.dst,['../secret.pptx'])

    def test_symlink_member_refused(self):
        link = self.src/'out_A/link.pptx'
        link.symlink_to(self.src/self.paths[0])
        with self.assertRaises(ValueError):
            q.freeze_snapshot(self.src,self.dst,['out_A/link.pptx'])

    def test_sha_crc_and_excluded_alternative(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        self.assertEqual(len(m),2)
        self.assertFalse((self.dst/'out_A/Example_verified_ALTERNATIVE.pptx').exists())
        a = self.root/'part.zip'
        r = q.make_zip(self.dst,m,a)
        self.assertTrue(r['crc_ok'])
        self.assertTrue(q.verify_zip(a,m))
        for rel in self.paths:
            self.assertEqual(q.sha256(self.src/rel),q.sha256(self.dst/rel))

    def test_existing_snapshot_not_overwritten(self):
        q.freeze_snapshot(self.src,self.dst,self.paths)
        with self.assertRaises(ValueError):
            q.freeze_snapshot(self.src,self.dst,self.paths)

    def test_same_size_content_tamper_detected(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        a = self.root/'bad.zip'
        with zipfile.ZipFile(a,'w')as z:
            for rel,e in m.items():
                data = (self.dst/rel).read_bytes()
                z.writestr('ALL_FIGURES/'+rel,bytes([data[0]^1])+data[1:])
        with self.assertRaises(ValueError):
            q.verify_zip(a,m)

    def test_missing_member_detected(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        a = self.root/'missing.zip'
        q.make_zip(self.dst,{self.paths[0]:m[self.paths[0]]},a)
        with self.assertRaises(ValueError):
            q.verify_zip(a,m)

    def test_extra_old_version_detected(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        a = self.root/'extra.zip'
        q.make_zip(self.dst,m,a)
        with zipfile.ZipFile(a,'a')as z:
            z.writestr('ALL_FIGURES/old.pptx','synthetic')
        with self.assertRaises(ValueError):
            q.verify_zip(a,m)

    def test_duplicate_member_detected(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        a = self.root/'dup.zip'
        q.make_zip(self.dst,m,a)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with zipfile.ZipFile(a,'a')as z:
                z.writestr('ALL_FIGURES/'+self.paths[0],(self.dst/self.paths[0]).read_bytes())
        with self.assertRaises(ValueError):
            q.verify_zip(a,m)

    def test_byte_limit_is_real(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        with self.assertRaises(ValueError):
            q.make_zip(self.dst,m,self.root/'oversize.zip',limit_bytes=8)

    def test_two_parts_same_root_independent(self):
        m = q.freeze_snapshot(self.src,self.dst,self.paths)
        for i,rel in enumerate(self.paths):
            group = {rel:m[rel]}
            p = self.root/f'part{i}.zip'
            q.make_zip(self.dst,group,p)
            self.assertTrue(q.verify_zip(p,group))
            with zipfile.ZipFile(p)as z:
                self.assertEqual(z.namelist(),['ALL_FIGURES/'+rel])


if __name__ == '__main__':
    unittest.main()
