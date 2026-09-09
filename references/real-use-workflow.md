# Real-Use Figure Workflow

## 1. Resolve the request

Identify the visual question, required variables, units, grouping, and requested output. Apply defaults silently. Ask only for information that blocks a defensible mapping or design.

## 2. Inspect data feasibility

Open source files read-only. Inspect column names, types, units, missingness, duplicate keys, group counts, and time coverage. Do not perform analytical calculations. Start an `AuditLog` for any plot-required transformation.

## 3. Apply the selection gate

Reject forbidden forms and verify chart-specific hard conditions. Choose the chart family from the intended comparison and data morphology, not from filename similarity.

## 4. Retrieve design evidence

Follow `asset-retrieval.md`. Use direct reuse when an asset's semantics and data contract match. Otherwise compose elements or use a bespoke design.

## 5. Present the design

State the question, data-to-mark mapping, layout, axes, legend, labels, intervals, annotations, asset influences, bespoke elements, and material risks. Wait for user approval before rendering. A minor cosmetic edit may use the user's requested change as approval of that design delta.

## 6. Adapt data and code

Keep data adaptation separate from rendering. Map user columns to declared semantic roles. Prefer copying a compatible production script. Modify declared inputs and scalable parameters; preserve semantic invariants. A bespoke implementation must still use shared visual and export rules.

## 7. Preflight and render

Validate the complete plotting frame before rendering. Produce the final figure at its intended physical size and 600 dpi. Do not generate unrequested formats.

## 8. Verify and deliver

Run `qa-real-use.md`, inspect the final rendered PNG at insertion size and enlarged size, fix failures, and rerender. Deliver the latest PNG, QA report, and data-processing note.

## 9. Triage lessons

Record a new lesson at asset or figure-family scope first. Promote it to a global rule only when it is a general visual principle or has recurred across multiple independent asset families. Do not turn a source-specific correction into a universal hard gate.

Follow `experience-learning.md`: capture a scoped candidate outside the skill, reproduce with synthetic data, obtain maintenance approval, promote the verified rule or asset, and refresh retrieval metadata. Do not delay an otherwise complete figure delivery for optional asset promotion.
