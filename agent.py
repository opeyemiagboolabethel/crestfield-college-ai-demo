import os
from operations import scenario_answer
def ask(tools,message,api_key='',live=False,history=None):
    if not live:return scenario_answer(tools,message)
    if not api_key:raise ValueError('Live AI is not configured.')
    from google import genai
    from google.genai import types
    trace=[]
    def run(name,**args):
        try:result=getattr(tools,name)(**args)
        except (ValueError,PermissionError,KeyError) as e:result={'error':str(e)}
        trace.append(dict(tool=name,result=result));return result
    def get_school_briefing()->dict:
        """Read reconciled attendance, uncovered lessons and admissions completeness."""
        return run('get_school_briefing')
    def get_attendance_review()->dict:
        """Read repeat recorded absences and incomplete registers; not a learner risk score."""
        return run('get_attendance_review')
    def inspect_student(student_ref:str)->dict:
        """Read fictional student reference and attendance only."""
        return run('inspect_student',student_ref=student_ref)
    def get_fee_followup()->dict:
        """Read balances; school leader and bursar only."""
        return run('get_fee_followup')
    def get_admissions_queue()->dict:
        """Read document completeness only, with no ranking or acceptance decision."""
        return run('get_admissions_queue')
    def get_lesson_cover()->dict:
        """Read lesson cover and recorded staff availability."""
        return run('get_lesson_cover')
    def draft_parent_update(student_ref:str)->dict:
        """Prepare a neutral attendance update draft; never sends."""
        return run('draft_parent_update',student_ref=student_ref)
    def propose_lesson_cover(lesson_id:str,staff_id:str)->dict:
        """Validate eligibility and availability without writing. Confirm separately in Action Lab."""
        return run('propose_lesson_cover',lesson_id=lesson_id,staff_id=staff_id)
    prompt=f"""You are Crestfield College AI for a fictional secondary school. Role: {tools.role}. Fixed clock: {tools.state['as_of']}; period: {tools.state['period']}. Always call tools before claiming counts, learner records, fees, admissions or cover availability. Quote IDs and evidence. Late counts as attending; exclude unmarked entries from the attendance denominator and show their number. An unmarked record is not an absence. Repeat absences require record verification and context, not behavioural judgement, diagnosis, safeguarding inference or a risk label. Never connect fee status to an absence cause or entitlement to teaching. Financial figures require head/bursar; respect tool permission errors. Admissions tools only check documents, not accept/reject or rank children. Parent updates are private neutral drafts, never sent. Cover proposals require eligibility, availability and no period conflict. The model has no commit tool: human staff review and confirm in Action Lab. Do not claim staff contact, a real timetable update or external work. All learners have synthetic references with no personal contacts. Keep administrative priorities concise."""
    context='\n'.join(f"{m['role']}: {m['content']}" for m in (history or [])[-6:])
    client=genai.Client(api_key=api_key,http_options=types.HttpOptions(timeout=45000))
    response=client.models.generate_content(model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite'),contents=context+'\nUser: '+message,config=types.GenerateContentConfig(system_instruction=prompt,temperature=.1,tools=[get_school_briefing,get_attendance_review,inspect_student,get_fee_followup,get_admissions_queue,get_lesson_cover,draft_parent_update,propose_lesson_cover],automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=8)))
    return dict(text=response.text or 'Try a focused school operations question.',mode='live-ai',trace=trace)
