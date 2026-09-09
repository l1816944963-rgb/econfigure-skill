# Real-Use Figure QA

Apply this protocol after design approval and before delivery. Each check returns `PASS`, `FAIL`, `WARN`, or `N/A`. A `FAIL` blocks delivery. Every `WARN` needs a written disposition.

## Pass 0: design

| ID | Level | Check |
|---|---|---|
| RD-01 | FAIL | The figure has one explicit visual question or analytical claim. |
| RD-02 | FAIL | The chart form matches the data structure and intended comparison. |
| RD-03 | FAIL | The user approved the chart form, encodings, annotations, and layout. |
| RD-04 | FAIL | The implementation route is declared as direct reuse, element composition, or bespoke design. |
| RD-05 | FAIL | Asset-derived elements name their source asset; bespoke elements name the governing visual rule. |
| RD-06 | FAIL | The plan contains no forbidden 3-D effect, rainbow palette, or truncated bar axis. |
| RD-07 | WARN | A dual axis, dense multipanel layout, or more than four color categories has a written justification. |

## Pass 1: data boundary and feasibility

| ID | Level | Check |
|---|---|---|
| RF-01 | FAIL | Source files were opened read-only and remain unchanged. |
| RF-02 | FAIL | Required columns, types, units, group counts, and time fields satisfy the design contract. |
| RF-03 | FAIL | Plot preparation performs no regression, significance test, indicator construction, or research-definition change. |
| RF-04 | FAIL | Missing-value handling, duplicate removal, reshaping, sorting, and renaming are recorded in `AuditLog`. |
| RF-05 | FAIL | The figure contains at least six information cells. |
| RF-06 | FAIL | Annual time-series periods are continuous or missing periods are explicitly represented. |
| RF-07 | FAIL | Bar charts use a zero baseline. |
| RF-08 | FAIL | Coefficient, event-study, and marginal-effect figures contain supplied intervals and a declared reference. |
| RF-09 | FAIL | Unsplit line charts contain no more than six series. |
| RF-10 | WARN | A supplied fitted curve, smoothing method, binning rule, or density normalization is disclosed. |
| RF-11 | FAIL | Interval estimates and bounds share identical observation, group, panel, and horizon keys. |
| RF-12 | FAIL | Interval boundaries come from supplied output and are not inferred from center-line geometry. |
| RF-13 | FAIL | Every normalized stack has non-negative components that sum to its declared total. |
| RF-14 | FAIL | Labels encoding a statistic other than mark geometry are supplied as separate annotation data. |

## Pass 2: implementation

| ID | Level | Check |
|---|---|---|
| RI-01 | FAIL | Direct reuse starts from the selected production asset. |
| RI-02 | FAIL | Element composition records every inherited element and resolves invariant conflicts. |
| RI-03 | FAIL | Bespoke design follows the shared visual baseline and does not imitate an incompatible asset. |
| RI-04 | FAIL | User-data adaptation is separate from rendering logic. |
| RI-05 | FAIL | The script reads external data and does not hard-code research values in drawing calls. |
| RI-06 | FAIL | Paths are relative, supplied as arguments, or resolved inside the user workspace. |
| RI-07 | FAIL | Identical inputs and configuration produce the same output. |
| RI-08 | FAIL | The implementation writes no source file and creates no undeclared output format. |
| RI-09 | FAIL | Rendering completes without unhandled plotting, data, font, or export warnings. |

## Pass 3: rendered output

| ID | Level | Check |
|---|---|---|
| RV-01 | FAIL | The output is a valid non-empty PNG with approximately 600 dpi metadata. |
| RV-02 | FAIL | Pixel dimensions match the intended physical size. |
| RV-03 | FAIL | No text, mark, interval, annotation, or legend item is clipped. |
| RV-04 | FAIL | Required Chinese and Latin glyphs render correctly. |
| RV-05 | FAIL | Labels identify variables and applicable units. |
| RV-06 | FAIL | Tick precision, scale, and placement follow the declared axis grammar. |
| RV-07 | FAIL | Baselines, event lines, zero lines, and reference periods match the approved design. |
| RV-08 | WARN | Gridlines remain subordinate and appear only where they aid comparison. |
| RV-09 | FAIL | Legends and direct labels match visible encodings and cover no unrelated element. |
| RV-10 | FAIL | Critical categories remain distinguishable in grayscale. |
| RV-11 | FAIL | Numeric labels are accurate, necessary, and collision-free. |
| RV-12 | FAIL | Comparable panels align and use consistent scales where required. |
| RV-13 | WARN | Whitespace, aspect ratio, and legend footprint remain balanced at insertion size. |
| RV-14 | FAIL | The render matches the approved design, including bespoke decisions. |
| RV-15 | FAIL | Supplied interval paths preserve local turning points and asymmetry. |
| RV-16 | FAIL | Text bounds do not intersect unrelated marks, text, axes, or legends. |
| RV-17 | FAIL | Every required panel-specific label or legend is present. |
| RV-18 | FAIL | Error bars remain visible across every fill they cross. |
| RV-19 | FAIL | Intentionally tickless axes remain tickless; boundary and centered ticks occupy their declared positions. |
| RV-20 | FAIL | Legend font, handles, spacing, padding, and inset form a deliberate visual footprint. |
| RV-21 | FAIL | Compound annotations preserve connector endpoints and text-to-line placement. |
| RV-22 | FAIL | Figure-level notes occupy reserved space without collision. |

## Pass 4: delivery

| ID | Level | Check |
|---|---|---|
| DL-01 | FAIL | A brief scan reveals the intended comparison. |
| DL-02 | FAIL | The figure implies no claim stronger than the supplied data support. |
| DL-03 | FAIL | Word-side title, number, caption, and notes are omitted from the PNG. |
| DL-04 | WARN | The figure is consistent with adjacent document figures or the difference is intentional. |
| DL-05 | FAIL | The latest PNG uses a stable descriptive filename in `figure-deliverables/`. |
| DL-06 | FAIL | The QA report and transformation note accompany the figure. |

## QA report

Record the design ID, implementation route, matched assets and inherited elements, bespoke elements, source filename, permitted transformations, check results, warning dispositions, PNG path, pixel dimensions, DPI metadata, and grayscale result.
