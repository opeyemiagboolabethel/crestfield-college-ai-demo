from types import SimpleNamespace
from unittest.mock import patch
from operations import SchoolTools,load_state
from agent import ask
def generate(**kwargs):
    functions=kwargs['config'].tools;assert len(functions)==8 and 'commit_lesson_cover' not in [f.__name__ for f in functions]
    assert functions[0]()['attendance_pct']==96.1
    assert functions[-1]('SB-L001','SB-T03')['revision']==0
    return SimpleNamespace(text='Review 45 registers and six uncovered lessons.')
with patch('google.genai.Client',return_value=SimpleNamespace(models=SimpleNamespace(generate_content=generate))):
    t=SchoolTools(load_state());r=ask(t,'School briefing','test-only-placeholder',True);assert len(r['trace'])==2 and t.state['revision']==0
print('PASS: approved tools, evidence trace and no AI commit tool')
