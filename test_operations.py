import copy,unittest
from operations import SchoolTools,load_state
class SchoolChecks(unittest.TestCase):
    def setUp(self):self.t=SchoolTools(load_state())
    def test_attendance(self):
        b=self.t.get_school_briefing();self.assertEqual(b['attendance_counts'],{'Present':3365,'Late':80,'Absent':140,'Unmarked':15});self.assertEqual((b['marked_denominator'],b['attendance_pct'],b['attendance_reviews']),(3585,96.1,45));self.assertEqual((b['uncovered_lessons'],b['incomplete_applications']),(6,15))
    def test_finance_permission(self):
        d=self.t.get_fee_followup();self.assertEqual((d['outstanding_ngn'],d['past_due_ngn']),(58200000,44760000))
        with self.assertRaises(PermissionError):SchoolTools(load_state(),'office').get_fee_followup()
    def test_propose_and_confirm(self):
        before=copy.deepcopy(self.t.state);p=self.t.propose_lesson_cover('SB-L001','SB-T03');self.assertEqual(before,self.t.state)
        with self.assertRaises(ValueError):self.t.commit_lesson_cover(p)
        a=self.t.commit_lesson_cover(p,True);self.assertEqual(a['action_id'],'SB-ACT-001');self.assertEqual(self.t.get_school_briefing()['uncovered_lessons'],5)
        with self.assertRaises(ValueError):self.t.propose_lesson_cover('SB-L001','SB-T03')
    def test_subject_unavailability_conflict(self):
        with self.assertRaises(ValueError):self.t.propose_lesson_cover('SB-L001','SB-T02')
        with self.assertRaises(ValueError):self.t.propose_lesson_cover('SB-L001','SB-T01')
        with self.assertRaises(ValueError):self.t.propose_lesson_cover('SB-L001','SB-T04')
        self.assertEqual(self.t.propose_lesson_cover('SB-L004','SB-T04')['subject'],'English')
    def test_stale_tamper_role(self):
        p=self.t.propose_lesson_cover('SB-L001','SB-T03')
        with self.assertRaises(PermissionError):SchoolTools(self.t.state,'bursar').commit_lesson_cover(p,True)
        bad=copy.deepcopy(p);bad['subject']='Changed'
        with self.assertRaises(ValueError):self.t.commit_lesson_cover(bad,True)
        self.t.state['revision']+=1
        with self.assertRaises(ValueError):self.t.commit_lesson_cover(p,True)
    def test_parent_draft_unmarked(self):
        d=self.t.draft_parent_update('SB-S111');self.assertFalse(d['sent']);self.assertIn('not treated those entries as absences',d['draft'])
        with self.assertRaises(PermissionError):SchoolTools(load_state(),'bursar').draft_parent_update('SB-S001')
    def test_source_unchanged(self):self.assertEqual(load_state()['revision'],0)
if __name__=='__main__':unittest.main()
