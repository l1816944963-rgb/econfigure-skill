# Asset Retrieval and Design Routing

## Retrieval principle

The asset library supplies tested visual evidence. It does not limit the design space. The user's message and data structure outrank visual resemblance.

## Progressive retrieval

Use three levels to limit context and prevent semantic drift.

### Level 1: catalog index

Read `assets/catalog.index.yaml`. Filter compact records by intent, available data-contract information, geometry, interval or reference requirements, panel structure, grayscale and target-publication compatibility, and explicit exclusions. Do not open every preview or script. As semantic contracts are added, use their required data roles as the first hard filter.

### Level 2: semantic cards

Load detailed manifests for the strongest candidates. Compare scenes, mark meanings, geometry controls, non-negotiable behavior, and invalid conditions. Inspect previews only for shortlisted candidates.

### Level 3: implementation

Open production code, fixtures, and asset-specific lessons only after selecting an asset or element for the approved design.

## Design routes

### Direct reuse

Use when the required semantic roles, transformations, marks, and panel structure match. Visual similarity alone is insufficient.

### Element composition

Use when no single asset matches but tested elements can be combined. Cite each inherited element by asset ID and class: geometry, encoding, annotation, axes, legend, or layout. Resolve conflicting invariants before implementation.

### Bespoke design

Use when retrieval produces no semantically sound match or when a new design communicates the user's goal better. Apply the global visual baseline and full QA. Do not label bespoke work as inherently lower quality.

## Ranking order

1. Hard compatibility of required data roles.
2. Semantic compatibility of visual marks.
3. Coverage of required elements.
4. Layout and annotation compatibility.
5. Grayscale and target-publication compatibility.
6. Visual preference.

Never force an asset match to improve a retrieval score.
