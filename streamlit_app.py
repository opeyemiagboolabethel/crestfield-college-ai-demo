"""Crestfield College's secondary-school administrative workspace."""
import copy,json,os
import pandas as pd
import streamlit as st
from operations import SchoolTools,ROLES,load_state
from agent import ask
st.set_page_config(page_title='Crestfield College AI | ONE Light Analytics',page_icon='🏫',layout='wide')
st.markdown('''<style>.stApp{background:#f7f5ef;color:#102536}.block-container{padding-top:2rem;padding-bottom:3rem}.sb-hero{padding:32px;background:linear-gradient(115deg,#071522,#294f48);border-radius:16px;color:white;margin-bottom:24px}.sb-hero h1{color:white;font-size:3rem;margin:12px 0}.sb-hero p{color:#d5dfe3;max-width:780px}.sb-kicker{color:#e5bf7c;letter-spacing:.14em;font-size:12px;text-transform:uppercase}[data-testid="stMetric"]{background:white;border:1px solid #d6dadd;border-radius:12px;padding:18px}[data-testid="stMetricValue"]{color:#102536}.stButton button{min-height:44px;border-color:#b18a4c}.stButton button p{color:#102536}</style>''',unsafe_allow_html=True)
if 'sb_state' not in st.session_state:st.session_state.sb_state=load_state()
if 'sb_messages' not in st.session_state:st.session_state.sb_messages=[]
with st.sidebar:
    st.subheader('Crestfield College AI');st.caption('Secondary-school administrative operations')
    st.link_button('ONE Light Analytics','https://onelightanalytics.com/')
    role=st.selectbox('Demo role',list(ROLES),format_func=ROLES.get,key='sb_role')
    key=os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or ''
    if not key:
        try:key=st.secrets.get('GEMINI_API_KEY','') or st.secrets.get('GOOGLE_API_KEY','')
        except Exception:key=''
    modes=['Scenario mode']+(['Live AI'] if key else [])
    mode=st.radio('Agent mode',modes,index=len(modes)-1,key='sb_mode')
    if st.button('Reset school session'):
        for k in ['sb_state','sb_messages','sb_proposal','sb_pending','sb_confirmed']:st.session_state.pop(k,None)
        st.rerun()
    st.caption('Fictional references only. Fixed clock: 9 October 2026, 10:00 WAT. Attendance: 5–9 October morning registers. Role switching illustrates permissions, not production authentication.')
if st.session_state.get('sb_context')!=(role,mode):
    st.session_state.sb_context=(role,mode);st.session_state.sb_messages=[]
    for k in ['sb_proposal','sb_pending']:st.session_state.pop(k,None)
t=SchoolTools(st.session_state.sb_state,role);b=t.get_school_briefing()
labels={'student_ref':'Learner reference','class_id':'Class','enrolment_type':'Day / boarding','term':'Term','tuition_ngn':'Tuition · ₦','boarding_ngn':'Boarding · ₦','approved_discount_ngn':'Approved discount · ₦','payment_note':'Payment arrangement','date':'Date','status':'Status','invoice_id':'Invoice','billed_ngn':'Billed · ₦','paid_ngn':'Paid · ₦','balance_ngn':'Outstanding · ₦','due_date':'Due date','past_due':'Past due date','application_id':'Application','requested_class':'Requested class','missing_documents':'Documents to follow up','lesson_id':'Lesson','period':'Period','starts_at':'Starts at','subject':'Subject','staff_id':'Staff reference','cover_status':'Lesson cover','subjects':'Recorded subject eligibility','available_periods':'Available periods'}
def table(rows):st.dataframe(pd.DataFrame(rows).rename(columns=labels),hide_index=True,width='stretch')
st.markdown('''<div class="sb-hero"><div class="sb-kicker">ONE Light Analytics · Sector AI 05 / Education</div><h1>Crestfield College AI</h1><p>Keep the school day connected, from the register to the next lesson.</p><p>Coordinate attendance records, lesson cover, fee follow-up and admissions paperwork with clear evidence and staff approval.</p></div>''',unsafe_allow_html=True)
if st.session_state.get('sb_flash'):st.success(st.session_state.pop('sb_flash'))
with st.expander('Start here · a three-minute school walkthrough'):
    st.markdown('**1. Read the school overview.** Separate missing register marks from recorded absence.\n\n**2. Ask the agent.** Inspect attendance, lesson cover or admissions records.\n\n**3. Open Action Lab.** Prepare SB-L001 with SB-T03. Review and confirm the lesson-cover simulation, then inspect Audit trail. No staff member or parent is contacted.')
overview,chat,desk,lab,audit=st.tabs(['School overview','AI Agent','Evidence desk','Action Lab','Audit trail'])
with overview:
    st.subheader('A clear administrative picture of the school week.')
    for cols,vals in [(st.columns(3),[('Learners',b['students']),('Attendance · marked entries',f"{b['attendance_pct']}%"),('Unmarked register entries',b['attendance_counts']['Unmarked'])]),(st.columns(3),[('Registers for follow-up',b['attendance_reviews']),('Lessons needing cover',b['uncovered_lessons']),('Incomplete applications',b['incomplete_applications'])])]:
        for col,(label,value) in zip(cols,vals):col.metric(label,value)
    st.caption('2026/2027 first term · JSS1–SS3 · 18 class arms · 504 day learners and 216 boarders. Fees are illustrative net invoices, after recorded discounts; approved instalment due dates are retained.')
    st.caption('3,600 expected marks = 3,365 Present + 80 Late + 140 Absent + 15 Unmarked. Attendance = (3,365 + 80) / 3,585 marked entries = 96.1%. Missing marks are not assumed absent.')
    a,c=st.columns(2)
    with a:st.markdown('#### Attendance review');table([dict(student_ref=r['student_ref'],class_id=r['class_id'],recorded_absences=r['counts']['Absent'],missing_marks=r['counts']['Unmarked']) for r in t.get_attendance_review()['records']])
    with c:st.markdown('#### Lesson cover');table(t.get_lesson_cover()['uncovered'])
    if role in {'head','bursar'}:
        fees=t.get_fee_followup();x,y=st.columns(2);x.metric('Outstanding fee balances',f"₦{fees['outstanding_ngn']:,}");y.metric('Past recorded due date',f"₦{fees['past_due_ngn']:,}");st.caption(fees['note'])
with chat:
    left,right=st.columns([1.7,1])
    with left:
        st.subheader('Ask Crestfield College AI')
        for m in st.session_state.sb_messages[-12:]:
            with st.chat_message(m['role']):
                st.markdown(m['content'])
                if m.get('trace'):
                    with st.expander('Inspect tool evidence'):st.json(m['trace'])
        message=st.chat_input('Ask about attendance, lesson cover or school administration',key='sb_chat')
        if st.session_state.get('sb_pending'):message=st.session_state.pop('sb_pending')
        if message:
            history=copy.deepcopy(st.session_state.sb_messages);st.session_state.sb_messages.append(dict(role='user',content=message))
            with st.chat_message('user'):st.markdown(message)
            with st.chat_message('assistant'):
                try:
                    with st.spinner('Checking the school records…'):r=ask(t,message,key,mode=='Live AI',history)
                    st.markdown(r['text']);st.caption(f"Mode: {r['mode']} · {ROLES[role]}")
                    with st.expander('Inspect tool evidence'):st.json(r['trace'])
                    st.session_state.sb_messages.append(dict(role='assistant',content=r['text'],trace=r['trace']))
                except Exception:st.error('This request could not complete. Try Scenario mode or a focused school question. No timetable change or message was executed.')
    with right:
        st.subheader('Operating questions')
        prompts={'School briefing':'Give me the school operations briefing.','Attendance review':'Which attendance records need follow-up?','Lesson cover':'Show lessons needing cover.','Admissions paperwork':'Which admissions documents need follow-up?'}
        if role in {'head','bursar'}:prompts['Fee follow-up']='Show fee follow-up balances.'
        for label,prompt in prompts.items():
            if st.button(label,width='stretch',key='sb_'+label):st.session_state.sb_pending=prompt;st.rerun()
        st.info('Verify records and context before parent contact. This tool does not label learners, infer absence causes or make admissions decisions.')
with desk:
    st.subheader('Readable evidence, with each record kept in context.')
    options=['Attendance registers','Lesson timetable','Staff availability','Admissions paperwork']+(['Outstanding fees'] if role in {'head','bursar'} else [])
    choice=st.selectbox('Record collection',options)
    if choice=='Attendance registers':rows=t.state['attendance']
    elif choice=='Lesson timetable':rows=t.get_lesson_cover()['lessons']
    elif choice=='Staff availability':rows=t.get_lesson_cover()['staff']
    elif choice=='Admissions paperwork':rows=t.get_admissions_queue()['records']
    else:rows=t.get_fee_followup()['records']
    table(rows);st.download_button('Download displayed records',pd.DataFrame(rows).rename(columns=labels).to_csv(index=False),'schoolbridge-records.csv','text/csv')
    student=st.selectbox('Inspect a learner reference',[r['student_ref'] for r in t.state['students']])
    detail=t.inspect_student(student)
    with st.container(border=True):
        st.subheader('Learner reference '+student);st.caption('Class: '+detail['student']['class_id'])
        table(detail['attendance']);st.caption('Recorded absence needs verification and context. An incomplete mark is not an absence.')
        with st.expander('View underlying record data'):st.json(detail)
with lab:
    st.subheader('Check lesson cover before recording an assignment.')
    st.caption('Only recorded subject eligibility, period availability and timetable overlap are checked. A real assignment requires staff confirmation and the school’s approval process.')
    if role in {'head','office'}:
        uncovered=t.get_lesson_cover()['uncovered']
        if uncovered:
            with st.form('sb_prepare'):
                lesson=st.selectbox('Lesson needing cover',[r['lesson_id'] for r in uncovered]);staff=st.selectbox('Proposed staff reference',[r['staff_id'] for r in t.state['staff']],index=2)
                prepare=st.form_submit_button('Prepare lesson-cover proposal')
            if prepare:
                st.session_state.pop('sb_proposal',None)
                try:st.session_state.sb_proposal=t.propose_lesson_cover(lesson,staff);st.session_state.sb_confirmed=False
                except (ValueError,PermissionError) as e:st.error(str(e))
        else:st.success('All demonstration lessons have recorded cover.')
        p=st.session_state.get('sb_proposal')
        if p:
            st.info(f"{p['lesson_id']} · {p['subject']} · {p['class_id']} · {p['period']}\n\nProposed staff: {p['staff_id']}")
            with st.form('sb_commit'):
                confirmed=st.checkbox('I reviewed the subject, availability and timetable; confirm this simulated cover assignment.',key='sb_confirmed');commit=st.form_submit_button('Confirm simulated lesson cover')
            if commit:
                try:a=t.commit_lesson_cover(p,confirmed);st.session_state.sb_flash=f"{a['action_id']}: {p['lesson_id']} covered by {p['staff_id']} in this session only. No staff notification occurred.";st.session_state.pop('sb_proposal',None);st.rerun()
                except (ValueError,PermissionError) as e:st.error(str(e))
    else:st.info('Bursars can inspect fees. Lesson-cover changes require school leadership or administration.')
    if role in {'head','office'}:
        target=st.selectbox('Learner reference for parent draft',[r['student_ref'] for r in t.state['students']])
        if st.button('Prepare parent-update draft'):
            d=t.draft_parent_update(target);st.text_area('Private draft only — not sent',d['draft'],height=130)
with audit:
    st.subheader('Confirmed lesson-cover simulations')
    for a in t.state['actions']:
        with st.container(border=True):
            st.write(f"**{a['action_id']} · {a['after']['lesson_id']}**");st.caption('Actor: '+ROLES[a['actor']]);st.write('Assigned staff: '+a['after']['staff_id'])
            with st.expander('View full audit record'):st.json(a)
    if not t.state['actions']:st.info('No lesson cover has been confirmed in this session.')
    st.download_button('Download session audit',json.dumps(t.state['actions'],indent=2),'schoolbridge-audit.json','application/json')
st.caption('Crestfield College is fictional. No real learner names, contacts or personal records are used. This is a synthetic administrative demonstration; reset discards simulated changes.')
