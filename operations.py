"""Fictional secondary-school administrative tools and reviewed lesson-cover simulation."""
import copy,json
from pathlib import Path
ROLES={'head':'School leader','office':'School administrator','bursar':'Bursar'}
def load_state():
    from fixture import expand
    return expand(json.loads((Path(__file__).parent/'data/operations.json').read_text()))
class SchoolTools:
    def __init__(self,state,role='head'):
        if role not in ROLES:raise PermissionError('Unknown demo role.')
        self.state,self.role=state,role
    def _get(self,collection,key,value):
        for r in self.state[collection]:
            if r[key]==value:return copy.deepcopy(r)
        raise ValueError('Record ID not found.')
    def get_attendance_review(self):
        rows=[]
        for student in self.state['students']:
            marks=[r for r in self.state['attendance'] if r['student_ref']==student['student_ref']]
            counts={status:sum(r['status']==status for r in marks) for status in ['Present','Late','Absent','Unmarked']}
            if counts['Absent']>=2 or counts['Unmarked']:
                rows.append(dict(**student,counts=counts,absent_dates=[r['date'] for r in marks if r['status']=='Absent'],unmarked_dates=[r['date'] for r in marks if r['status']=='Unmarked']))
        return dict(records=rows,rule='At least two recorded absences, or any unmarked attendance in the fixed five-day period. Verify records and context; this is not a learner risk score.')
    def get_school_briefing(self):
        counts={status:sum(r['status']==status for r in self.state['attendance']) for status in ['Present','Late','Absent','Unmarked']}
        marked=len(self.state['attendance'])-counts['Unmarked']
        return dict(term=self.state['term'],boarding_students=sum(r['enrolment_type']=='Boarding' for r in self.state['students']),day_students=sum(r['enrolment_type']=='Day' for r in self.state['students']),period=self.state['period'],as_of=self.state['as_of'],students=len(self.state['students']),classes=len(self.state['classes']),expected_marks=len(self.state['attendance']),attendance_counts=counts,
                    attendance_pct=round((counts['Present']+counts['Late'])/marked*100,1),marked_denominator=marked,
                    attendance_reviews=len(self.get_attendance_review()['records']),uncovered_lessons=len(self.get_lesson_cover()['uncovered']),
                    incomplete_applications=len(self.get_admissions_queue()['records']),
                    note='Late counts as attending; unmarked entries are excluded from the rate, not assumed absent. Synthetic administrative baseline.')
    def inspect_student(self,student_ref:str):
        student=self._get('students','student_ref',student_ref)
        return dict(student=student,attendance=[copy.deepcopy(r) for r in self.state['attendance'] if r['student_ref']==student_ref],
                    note='Synthetic reference only; no name, contacts, academic judgement or fee detail in this tool.')
    def get_fee_followup(self):
        if self.role not in {'head','bursar'}:raise PermissionError('Fee balances require school leadership or bursar role.')
        rows=[]
        for source in self.state['fees']:
            r=copy.deepcopy(source);r['balance_ngn']=r['billed_ngn']-r['paid_ngn'];r['past_due']=r['due_date']<self.state['as_of'][:10]
            if r['balance_ngn']>0:rows.append(r)
        return dict(records=rows,outstanding_ngn=sum(r['balance_ngn'] for r in rows),past_due_ngn=sum(r['balance_ngn'] for r in rows if r['past_due']),
                    note='Administrative payment follow-up; never infer learner behaviour, attendance causes or entitlement to instruction from fees.')
    def get_admissions_queue(self):
        return dict(records=[copy.deepcopy(r) for r in self.state['admissions'] if r['missing_documents']],
                    note='Document completeness only. Does not rank, accept or reject applicants.')
    def get_lesson_cover(self):
        return dict(uncovered=[copy.deepcopy(r) for r in self.state['lessons'] if r['cover_status']=='Needs cover'],
                    lessons=copy.deepcopy(self.state['lessons']),staff=copy.deepcopy(self.state['staff']),
                    note='Recorded subject eligibility and availability, not a guarantee of staffing readiness.')
    def draft_parent_update(self,student_ref:str):
        if self.role not in {'head','office'}:raise PermissionError('Attendance parent drafts require school leadership or administration.')
        d=self.inspect_student(student_ref);absent=[r['date'] for r in d['attendance'] if r['status']=='Absent'];missing=[r['date'] for r in d['attendance'] if r['status']=='Unmarked']
        text=f"Regarding school reference {student_ref}, our register records absence on {', '.join(absent) if absent else 'no days in the selected period'}. Please help us confirm these records and share any relevant context with the school office."
        if missing:text+=f" The register also needs completion for {', '.join(missing)}; we have not treated those entries as absences."
        return dict(student_ref=student_ref,draft=text,sent=False,note='Private parent-message draft only. Confirm records and recipient before any production communication.')
    def propose_lesson_cover(self,lesson_id:str,staff_id:str):
        if self.role not in {'head','office'}:raise PermissionError('Lesson cover requires school leadership or administration.')
        lesson=self._get('lessons','lesson_id',lesson_id);staff=self._get('staff','staff_id',staff_id)
        if lesson['cover_status']!='Needs cover':raise ValueError('This lesson already has recorded cover.')
        if lesson['starts_at']<=self.state['as_of']:raise ValueError('Only future lessons can receive proposed cover.')
        if lesson['subject'] not in staff['subjects']:raise ValueError('The staff member is not recorded as eligible for this subject.')
        if lesson['period'] not in staff['available_periods']:raise ValueError('The staff member is unavailable for this period.')
        if any(r['staff_id']==staff_id and r['date']==lesson['date'] and r['period']==lesson['period'] for r in self.state['lessons']):raise ValueError('The staff member is already assigned to another lesson in this period.')
        return dict(lesson_id=lesson_id,staff_id=staff_id,subject=lesson['subject'],class_id=lesson['class_id'],period=lesson['period'],role=self.role,revision=self.state['revision'],action='Record lesson cover in this fictional session only; no staff notification.')
    def commit_lesson_cover(self,proposal,confirmed=False):
        if confirmed is not True:raise ValueError('Explicit confirmation is required.')
        if proposal.get('role')!=self.role:raise PermissionError('The proposal belongs to another role.')
        if proposal.get('revision')!=self.state['revision']:raise ValueError('Records changed. Prepare a fresh proposal.')
        if proposal!=self.propose_lesson_cover(proposal['lesson_id'],proposal['staff_id']):raise ValueError('Proposal changed. Prepare a fresh proposal.')
        row=next(r for r in self.state['lessons'] if r['lesson_id']==proposal['lesson_id']);before=copy.deepcopy(row);row['staff_id']=proposal['staff_id'];row['cover_status']='Covered';self.state['revision']+=1
        audit=dict(action_id=f"SB-ACT-{len(self.state['actions'])+1:03}",actor=self.role,at=self.state['as_of'],before=before,after=copy.deepcopy(row),revision=self.state['revision']);self.state['actions'].append(audit);return copy.deepcopy(audit)
def scenario_answer(t,message):
    q=message.lower()
    if 'fee' in q or 'payment' in q:
        name='get_fee_followup';d=t.get_fee_followup();text=f"Outstanding fee balances total ₦{d['outstanding_ngn']:,}, with ₦{d['past_due_ngn']:,} past the recorded due date. Verify payments with the bursar. Do not infer attendance causes or learner behaviour from fee status."
    elif 'admission' in q:
        name='get_admissions_queue';d=t.get_admissions_queue();text='Document follow-up: '+'; '.join(r['application_id']+' — '+', '.join(r['missing_documents']) for r in d['records'])+'. No applicant ranking or admissions decision is made.'
    elif 'cover' in q or 'lesson' in q:
        name='get_lesson_cover';d=t.get_lesson_cover();text='Lesson cover needed: '+'; '.join(r['lesson_id']+' — '+r['subject']+' / '+r['class_id']+' / '+r['period'] for r in d['uncovered'])+'. Check subject eligibility and staff availability, then prepare and confirm in Action Lab.'
    elif 'attendance' in q:
        name='get_attendance_review';d=t.get_attendance_review();text='Attendance records for follow-up: '+', '.join(r['student_ref'] for r in d['records'])+'. Verify absence dates and incomplete marks before contacting a parent. No behaviour or safeguarding inference is made.'
    else:
        name='get_school_briefing';d=t.get_school_briefing();text=f"{d['students']} learners across {d['classes']} classes; {d['expected_marks']} expected daily marks. Attendance is {d['attendance_pct']}% among {d['marked_denominator']} marked entries, counting Late as attending. {d['attendance_counts']['Unmarked']} entries remain unmarked. Review {d['attendance_reviews']} learner registers, {d['uncovered_lessons']} uncovered lessons and {d['incomplete_applications']} incomplete applications."
    return dict(text=text,mode='scenario',trace=[dict(tool=name,result=d)])
