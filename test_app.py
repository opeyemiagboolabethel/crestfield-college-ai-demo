from pathlib import Path
from streamlit.testing.v1 import AppTest
at=AppTest.from_file(str(Path(__file__).parent/'streamlit_app.py'),default_timeout=20).run()
assert not at.exception and at.metric[0].value=='720'
next(b for b in at.button if b.label=='School briefing').click().run()
assert not at.exception and '96.1%' in at.session_state['sb_messages'][-1]['content']
next(b for b in at.button if b.label=='Prepare lesson-cover proposal').click().run()
assert at.session_state['sb_proposal']['staff_id']=='SB-T03'
next(b for b in at.button if b.label=='Confirm simulated lesson cover').click().run()
assert at.error and not at.session_state['sb_state']['actions']
at.checkbox(key='sb_confirmed').check().run()
next(b for b in at.button if b.label=='Confirm simulated lesson cover').click().run()
assert not at.exception and len(at.session_state['sb_state']['actions'])==1
at.selectbox(key='sb_role').select('office').run()
assert not at.exception and not at.session_state['sb_messages']
assert not any(m.label=='Outstanding fee balances' for m in at.metric)
at.selectbox(key='sb_role').select('bursar').run()
assert not any(b.label=='Prepare lesson-cover proposal' for b in at.button)
next(b for b in at.button if b.label=='Reset school session').click().run()
assert not at.exception and not at.session_state['sb_state']['actions']
print('PASS: readable application, scenario response, confirmation, audit, permissions and reset')
