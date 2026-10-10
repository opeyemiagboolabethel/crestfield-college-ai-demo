# Crestfield College AI

ONE Light Analytics secondary-school administrative operations demonstration. The fictional school has 720 synthetic learner references across 18 class arms (JSS1–SS3), five daily attendance registers, 72 upcoming lessons, 40 staff references, 720 term-fee invoices and 60 admissions applications. The first-term 2026/2027 profile includes 504 day learners and 216 boarders. No real names, contact details or personal records are used.

## Run and deploy

```sh
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Python 3.11 or later. Deploy independently from repository `crestfield-college-ai-demo`, branch `main`, main file `streamlit_app.py`. Suggested subdomain: `crestfield-college-ai-demo`, subject to availability. Configure `GEMINI_API_KEY` or `GOOGLE_API_KEY` privately in this app's settings or environment. Never commit keys. Scenario mode requires no key. Default model: `gemini-3.5-flash-lite`; override with `GEMINI_MODEL` if needed.

## Explore

Read School overview. Ask the agent for attendance review, lesson cover or admissions paperwork. Inspect readable reference records. In Action Lab, propose `SB-L001` with `SB-T03`. Review and explicitly confirm the session-only cover assignment. Inspect Audit trail. Parent messages are private drafts and are not sent.

The compact `data/operations.json` profile is expanded reproducibly by `fixture.py` into the full learner, attendance and invoice records. CSV exports contain the expanded records.

## Definitions and baseline

The fixed clock is 9 October 2026, 10:00 WAT. The attendance period is 5–9 October morning registers. 3,600 expected marks = 3,365 Present + 80 Late + 140 Absent + 15 Unmarked. Attendance is (Present + Late) / marked entries: 3,445 / 3,585 = 96.1%. Missing marks are not assumed absent. 45 learner registers need verification because they contain at least two recorded absences or an unmarked entry. This is not a behaviour, safeguarding or risk score.

Six lessons need cover; 15 applications lack documents. The document queue does not rank, accept or reject applicants. Outstanding fee balances total ₦58,200,000, including ₦44,760,000 past the recorded due date. Balances equal billed minus paid. Illustrative invoices itemise tuition, boarding and approved discounts; payment due dates retain recorded instalment arrangements. Amounts are synthetic and do not represent any real school’s fees. Fees do not determine learner behaviour, absence causes or entitlement to teaching.

## Permissions and actions

Only school leadership and bursars access fees. Leadership and school administration can prepare lesson cover and attendance parent drafts. All roles can inspect the fictional operational references. Role switching illustrates tool permissions; it is not production authentication.

Lesson proposals validate a future uncovered lesson, recorded subject eligibility, period availability and existing timetable conflicts. Confirmation revalidates role, revision and proposal fields, then records a session-only assignment with before/after evidence. Stale or tampered proposals are rejected. The model has no commit tool. No teacher or parent is contacted. Reset discards simulated changes.

The demo focuses on secondary schools. Primary-school or wider education deployments would adapt calendars, class structures, permissions and workflows rather than assume these records apply unchanged. Production needs approved school-system integrations, appropriate data governance, verified recipients and durable identity/auditing.

## Verify

```sh
python -m unittest test_operations.py
python test_agent.py
python test_app.py
```

Checks cover attendance denominators, fee permissions, subject eligibility, timetable conflicts, non-mutating proposals, explicit confirmation, stale/tampered proposals, neutral unsent parent drafts, audit records, role isolation and reset. The external provider is mocked in automated tests; verify Live AI on the deployed app separately.
