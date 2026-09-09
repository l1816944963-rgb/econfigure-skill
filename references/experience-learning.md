# Reusable experience lifecycle

Use this route when figure production reveals a new reusable design, failure mode, or validated correction. It is an agent-guided repository workflow, not model training or an automatic background updater.

## Capture, verify, promote, retrieve

1. **Capture after delivery.** Store a candidate lesson in the user's workspace outside the installed skill, for example `figure-deliverables/experience-candidates/`. Record only a new finding; link to an existing lesson when it already covers the case.
2. **Define its scope.** Decide whether it belongs to one asset, a figure family, or a shared principle. Separate data semantics from display parameters. A preference for one figure is not a general prohibition.
3. **Reproduce.** Use a minimal synthetic fixture to reproduce the issue and the correction. Compare the rendered results at insertion size. Preserve the test configuration and the relevant QA IDs.
4. **Review.** Identify exceptions, privacy implications and effects on existing assets. Present the proposed skill change for maintainer approval under the maintenance boundary. Ordinary figure approval does not authorize publishing user data or modifying shared rules.
5. **Promote.** Update the relevant asset manifest/script, family guidance, or shared reference. New assets follow `asset-engineering.md` and `qa-asset.md`. Add a regression test where a deterministic failure can be checked; retain a visual acceptance case for layout decisions.
6. **Refresh and reuse.** Rebuild the catalog and atlas for asset changes, run the affected evaluations, and confirm QA. Future requests retrieve the validated asset through its semantic tags or load the relevant shared guidance. Unverified candidates never enter the approved catalog.

## Candidate record

```yaml
id: descriptive-kebab-case
status: candidate  # candidate -> verified -> approved; rejected or superseded also allowed
scope: asset      # asset | family | shared
asset_ids: []
trigger: "Data or layout condition that causes the issue"
symptom: "Observable failure"
cause: "Verified explanation, or explicitly unresolved"
correction: "Smallest reproducible change"
invariants: []    # Statistical meanings and source data that must remain unchanged
exceptions: []   # Cases where the correction must not be applied
evidence: []     # Workspace-local fixture, render and configuration references
qa_ids: []
verification: "Checks run and observed results"
promotion_target: "Relative skill file to update"
approval: null
```

Do not copy confidential data, original publication screenshots, local paths, conversation excerpts, or reviewer identities into public references. Publish the generalized rule and a redistributable synthetic example. Candidate histories and before/after working files remain outside the skill.

## Promotion destinations

| Finding | Destination | Verification |
|---|---|---|
| Incorrect interpretation of a box, interval or reference | Asset `data_contract.semantic_contract` and role definitions | Check actual renderer mapping and supplied statistical definitions |
| Reusable figure form | Script, fixture, preview and manifest in `assets/figures/` | Asset QA, execution and visual approval |
| Repeated layout failure | `common-pitfalls.md` and an applicable QA check | Reproduce in affected layouts and check exceptions |
| Reusable composition | `figure-deconstruction.md` with asset links | Confirm compatible data roles and panel semantics |
| Color mapping issue | `color-palettes.md` and relevant asset settings | Render using the actual background, normalization and secondary encoding |

Promote a shared rule only when supported by a general principle or independently reproduced across multiple figure families. Keep narrow cases narrow. The absence of a new lesson is a normal outcome, not an incomplete delivery.
