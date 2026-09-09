# Asset Engineering QA

Apply this protocol to reusable assets. Each check returns `PASS`, `FAIL`, `WARN`, or `N/A`. A `FAIL` blocks promotion. Keep private evidence outside the public release bundle.

## Source and semantics

| ID | Level | Check |
|---|---|---|
| AS-01 | FAIL | The complete source is preserved privately and its hash is recorded. |
| AS-02 | FAIL | The asset ID and family follow visible geometry and intended use rather than a legacy filename. |
| AS-03 | FAIL | Unrelated page furniture is excluded from the visual target. |
| AS-04 | FAIL | Data geometry, display geometry, semantic markers, and reading aids are distinguished. |
| AS-05 | FAIL | Every ambiguous or special mark has a verified semantic contract. |
| AS-06 | FAIL | Unverified mark meanings keep the asset out of retrieval. |

## Data and implementation

| ID | Level | Check |
|---|---|---|
| AI-01 | FAIL | Plotting values live in an external fixture and visually estimated values are identified privately. |
| AI-02 | FAIL | The renderer performs no analytical calculation and validates its data contract. |
| AI-03 | FAIL | The runtime entry point is deterministic. |
| AI-04 | FAIL | The asset depends only on documented stable runtime modules. |
| AI-05 | FAIL | The asset depends only on stable runtime modules and declared packages. |
| AI-06 | FAIL | Paths are portable and no source file is modified. |
| AI-07 | FAIL | Repeated warning-free renders produce the same output hash. |
| AI-08 | FAIL | The renderer creates a 600 dpi PNG and no undeclared format. |

## Structural fidelity

| ID | Level | Check |
|---|---|---|
| AF-01 | FAIL | Source-sized review covers marks, axes, ticks, labels, legends, panels, and annotations. |
| AF-02 | FAIL | Interval centers and every boundary come from separately supplied values. |
| AF-03 | FAIL | Interval review compares turning points, asymmetry, and enclosed area separately. |
| AF-04 | FAIL | Normalized stacks close at the declared total for every complete key. |
| AF-05 | FAIL | Annotation statistics are separate from mark geometry when they encode different values. |
| AF-06 | FAIL | Tick presence, absence, and position match the declared grammar in every facet. |
| AF-07 | FAIL | Legends are evaluated as complete visual objects, including footprint and clearance. |
| AF-08 | FAIL | Compound connectors preserve every segment and endpoint. |
| AF-09 | FAIL | Color-dominant fills retain subordinate gridlines. |
| AF-10 | FAIL | Fitted geometry is separate from observation noise. |
| AF-11 | FAIL | Histogram bins remain distinguishable at insertion size. |
| AF-12 | FAIL | Repeated interval panels align common reference values physically. |
| AF-13 | FAIL | Horizontal boxplots declare quartile, median, whisker, and display-height semantics. |
| AF-14 | FAIL | Text, legends, titles, and notes have positive clearance from unrelated elements. |
| AF-15 | FAIL | Grayscale and actual-size reviews reveal no clipping or unresolved collision. |

## Evidence and promotion

| ID | Level | Check |
|---|---|---|
| AP-01 | FAIL | Automated PASS results have executed evidence. |
| AP-02 | FAIL | The final review uses the current production PNG rather than a cached preview. |
| AP-03 | FAIL | The asset remains outside retrieval until visual acceptance is explicit. |
| AP-04 | FAIL | The runtime manifest passes the catalog schema. |
| AP-05 | FAIL | The public preview, code, fixture, and manifest contain no private provenance. |
| AP-06 | FAIL | Public filenames contain no batch, revision, candidate, or temporary naming. |
| AP-07 | FAIL | Asset-specific lessons are reviewed before any rule is promoted globally. |

Image comparison may support visual review but never proves semantic or visual acceptance. Do not use image-similarity metrics as real-data quality scores.
