---
name: econfigure
description: Design and produce reproducible figures and three-line Word tables for applied-economics master's theses from user-provided data. Use for thesis figure design, chart redesign, figure replication, asset-guided composition, and figure QA. Prefer validated assets, allow bespoke designs when they serve the thesis argument better, keep source data read-only, and deliver 600 dpi PNG figures.
---

# Econfigure Skill

Create thesis-ready figures and three-line tables for applied-economics master's dissertations. Treat journal submission as a user-specified target rather than the default. Do not assume an institution or typography system.

## Baseline and requirement resolution

Apply the fixed delivery and integrity rules below. Resolve visual conventions from the user's request, target document, or supplied template:

- Deliver figures as 600 dpi PNG files.
- Check grayscale discrimination when the target medium requires it.
- Inherit typography from the target document or an explicit user requirement. When neither is available, use an installed font with complete glyph coverage and report the rendered choice; do not claim institutional compliance.
- Keep source data read-only and record plot-required transformations.
- Keep titles, figure numbers, captions, and notes outside the PNG for Word layout.
- Prefer rerunnable code and approved production assets.

Do not present a first-use questionnaire. Ask a concise question only when missing information blocks a defensible design or data mapping. Read `references/workflow-router.md` first.

## Workflow routing

Route each request before loading detailed instructions:

| Route | Use when | Read |
|---|---|---|
| Figure delivery | Create, redesign, or adapt an academic figure | `references/real-use-workflow.md` |
| Asset engineering | Create, add, or revise a reusable figure asset | `references/asset-engineering.md` |
| Library governance | Audit, index, or restructure the reusable library | `references/asset-engineering.md` and the relevant QA document |
| Institution template | Apply or add a school-specific thesis format | `references/institution-templates.md` and the selected package |
| Three-line table | Create or append an academic table | The `Three-line tables` section below |

Cosmetic edits may enter the figure-delivery route after design resolution. They still require rendered QA.

## Data boundary

- Treat every source data file as read-only.
- Permit only plot-required selection, missing-value handling, duplicate removal, pivoting, renaming, sorting, and time parsing.
- Do not run regressions, significance tests, construct research indicators, change analytical definitions, or write results back to source files.
- Record every transformation with `chartlib.data_io.AuditLog` under `figure-deliverables/data-processing-notes/`.

## Figure design

Use the user's communication goal and data structure as the primary design constraints. Apply the following routes in order:

1. **Direct reuse:** copy an approved asset when its semantics and data contract match.
2. **Element composition:** combine compatible geometry, encoding, layout, axis, annotation, or legend elements from multiple assets.
3. **Bespoke design:** create a new design when existing assets would distort or weaken the requested message.

Asset retrieval is the preferred starting point, not a constraint on the final design. Never force a weak asset match. Follow `references/asset-retrieval.md`, `references/parameter-system.md`, and the asset's `required_data_roles`, `semantic_contract`, and `retrieval_contract`.

Present a concrete design plan before rendering. Include the chart form, encodings, layout, annotations, intended asset reuse or composition, bespoke elements, and material warnings. Proceed after the user approves the plan.

## Figure selection guardrails

- Use line charts for continuous change, bars for category comparison, stacked forms for composition, histograms or density plots for distributions, scatter plots for relationships, coefficient plots for estimates with intervals, and event-study plots for policy dynamics.
- Reject 3-D effects, rainbow palettes, truncated bar axes, single-value snapshots, and figures with fewer than six information cells.
- Require confidence intervals for coefficient plots and supplied estimate/lower/upper values on identical keys for interval figures.
- Split line charts with more than six series unless the design justifies another readable encoding.
- Require explicit justification for dual axes.

## Visual baseline

- Read `references/color-palettes.md`, `references/typography-layout.md`, and `references/common-pitfalls.md` when the design or QA decision involves those topics.
- Resolve absolute font sizes from the target document and insertion size; axis labels must be at least as large as tick labels.
- Default to white plotting areas, no decorative borders, no shadows, and restrained guides.
- Use redundant encoding where grayscale could collapse categories.
- Do not place two series together when their grayscale luminance difference is below 15% unless another strong encoding distinguishes them.
- Never smooth or infer supplied statistical paths unless the approved analysis explicitly requires it.
- Treat ticks, legend footprint, connector geometry, whitespace, and collision clearance as structural design elements.

## Quality and output

For figure delivery, run `references/qa-real-use.md`. For asset work, run `references/qa-asset.md`. A failed hard check blocks delivery or asset promotion. Every warning requires a written disposition.

- Write figures to `<workspace>/figure-deliverables/` using stable descriptive filenames unless the user supplies another destination.
- Deliver no PDF, SVG, EPS, TIFF, or undeclared companion image unless the user explicitly changes the output rule.
- Deliver the PNG, QA report, and one transformation note per output.

## Three-line tables

- Inherit font family and size from the target document or supplied template.
- Keep the table number and title on one line without terminal punctuation.
- Use three horizontal rules and no vertical rules; take exact rule weights from the target template when supplied.
- Ask only for information that cannot be inferred, such as an unavailable chapter number or table title.
- Append tables to `figure-deliverables/three-line-tables.docx` unless another destination is supplied, and continue numbering from the existing document.
- Preserve the user's language and document labels in generated Word output.

## Maintenance boundary

After figure delivery, follow `references/experience-learning.md` when there is a new reusable finding. Capture candidates outside the skill; verify and obtain maintenance approval before updating shared assets or references. Load approved lessons through the relevant asset manifest or topic reference in subsequent tasks.

Before changing this skill's code, styles, schemas, or rules, present a concrete change plan and obtain user approval. Rendering with approved assets is not a maintenance change.

Keep repository prose, code comments, diagnostics, metadata, and tests in English. Keep private source material, development evidence, and project history outside the skill directory.

## Runtime structure

```text
assets/figures/             Approved runtime assets
assets/catalog.index.yaml  Compact machine-readable retrieval index
assets/figure-atlas.md      Human-readable generated catalog
assets/standard_samples/    End-to-end acceptance scenarios
chartlib/                   Shared runtime components
references/                 Conditionally loaded workflow and design knowledge
scripts/                    Deterministic validation and packaging tools
styles/                     Shared Matplotlib baselines
tests/                      Runtime and asset checks
```

The figure library was collected for study from publicly accessible academic literature and independently implemented as executable assets. Read `references/asset-provenance.md` when adding, publishing, or redistributing assets.
