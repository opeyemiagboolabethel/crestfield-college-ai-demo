"""Expand the compact fictional school profile into reproducible administrative records."""
import copy
def expand(profile):
    s=copy.deepcopy(profile)
    s['students']=[dict(student_ref=f'SB-S{i:03}',class_id=s['classes'][(i-1)//40]['class_id'],enrolment_type='Boarding' if (i-1)%10<3 else 'Day') for i in range(1,721)]
    s['attendance']=[]
    for i,student in enumerate(s['students'],1):
        for day in range(5,10):
            status='Absent' if (i<=30 and day in [6,8]) or (31<=i<=110 and day==7) else 'Unmarked' if (111<=i<=125 and day==9) else 'Late' if (126<=i<=165 and day in [5,6]) else 'Present'
            s['attendance'].append(dict(student_ref=student['student_ref'],class_id=student['class_id'],date=f'2026-10-{day:02}',status=status))
    s['fees']=[]
    for i,student in enumerate(s['students'],1):
        tuition=350000;boarding=250000 if student['enrolment_type']=='Boarding' else 0;discount=70000 if i%30==0 else 0;net=tuition+boarding-discount
        paid=int(net*[1,1,.8,.6,.5][(i-1)%5])
        s['fees'].append(dict(student_ref=student['student_ref'],invoice_id=f'SB-F{i:03}',term=s['term'],tuition_ngn=tuition,boarding_ngn=boarding,approved_discount_ngn=discount,billed_ngn=net,paid_ngn=paid,due_date='2026-10-20' if i%4==0 else '2026-10-05',payment_note='Recorded approved instalment balance due 20 October' if i%4==0 else 'Recorded first-term balance due 5 October'))
    return s
