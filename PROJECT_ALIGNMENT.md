# Alignment with the Final iQuality Business Case

Reference date: **29 August 2026**

## Buyer and users

- Buyer: owner's representatives and QS/consultant teams on Saudi giga-projects.
- Field user: site engineer using a helmet- or body-mounted 360° camera.
- Excluded initial segment: small/general contractors without standardized
  BOQ/WBS activity coding.

## Prototype workflow

| Business workflow | MVP implementation |
| --- | --- |
| Capture | `frames.py` extracts timestamped evidence frames. |
| Recognize | `verification.py` accepts the activity output from a demo/model. |
| Match | The recognized activity is matched to codes seeded from BOQ/WBS data. |
| Verify | Quality, code agreement and visible ArUco IDs are stored as evidence. |
| Approve | Every observation creates a pending QS approval record. |

## Evidence rules

- `supported`: usable visual evidence and recognized code matches the claim.
- `contradicted`: usable evidence identifies a different activity code.
- `not_observed`: image/model evidence is insufficient; this is not treated as
  proof that the work was not completed.

## Target metrics represented by the design

- At least 95% capture completion on scheduled walks.
- At least 90% recognition-to-code match accuracy.
- Less than 48 hours from recognition to QS approval.

The MVP records the fields required to calculate these metrics, but real target
performance requires pilot footage and a trained construction-activity model.

## Governance boundary

iQuality recognizes construction activity, not individual performance. Safety,
disciplinary and productivity monitoring are explicitly out of scope. A real
pilot requires consent, retention controls, in-Kingdom data localization,
PDPL/SDAIA review and role-based access.
