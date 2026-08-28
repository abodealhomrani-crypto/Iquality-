# iQuality MVP — Construction Evidence Platform

iQuality is a proof-of-concept pipeline for owner representatives and Quantity
Surveyor (QS) teams on activity-coded construction projects. A helmet- or
body-mounted 360° camera turns the site engineer's normal walk into a located,
auditable evidence record.

The MVP follows the final project workflow:

1. **Capture** — convert site-walk video into timestamped frames.
2. **Recognize** — receive the activity predicted by the demo/model.
3. **Match** — compare it automatically with a BOQ/WBS activity code.
4. **Verify** — check image quality, activity match and surveyed marker.
5. **Approve** — create a pending QS approval record.

Verification uses three explicit evidence states:

- `supported`
- `contradicted`
- `not_observed`

The MVP is intentionally limited: it demonstrates the workflow and audit trail.
It is not a trained production AI model and must not automatically approve a
payment application.

## Project files

- `seed.sql` — creates the SQLite database and sample activity codes.
- `frames.py` — extracts timestamped frames from a video.
- `verification.py` — recognizes/matches demo activities, checks evidence and
  opens pending QS approvals.
- `test_integration.py` — tests the complete demo workflow.
- `.github/workflows/ci.yml` — runs the tests automatically on GitHub.
- `PROJECT_ALIGNMENT.md` — maps the prototype to the latest Business Case/BMC.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sqlite3 iquality.db < seed.sql
python frames.py site_walk.mp4 --output frames
python verification.py frames --database iquality.db \
  --claimed-activity-code REBAR-L3 \
  --recognized-activity-code REBAR-L3
```

The verification command creates `verification_results.json` and stores the
same observations in `iquality.db`.

## Run the test

```bash
pytest -q
```

## MVP logic

For each frame, the demo checks brightness, sharpness, visual detail and any
visible ArUco marker. If the evidence quality is insufficient, the result is
`not_observed`. If the recognized activity matches the claimed BOQ/WBS code, it
is `supported`; if it confidently identifies a different code, it is
`contradicted`. A future trained activity-recognition model can replace the
demo input without changing the workflow or audit tables.

## Privacy

Do not upload real worker footage without authorization. Production deployment
requires consent, retention rules, in-Kingdom data localization, Saudi PDPL/
SDAIA review, access controls and an explicit ban on safety, disciplinary or
individual productivity monitoring. The system recognizes construction
activities, not worker performance.
