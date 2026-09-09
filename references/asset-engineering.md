# Asset Engineering Workflow

Use this workflow for a new or revised reusable asset.

1. Register the source privately and preserve its hash.
2. Deconstruct data geometry, display geometry, semantic markers, and reading aids using `figure-deconstruction.md`.
3. Assign a stable English kebab-case asset ID from the rendered geometry and intended use.
4. Build an external, clearly labeled rendering fixture. Do not embed research values in drawing calls.
5. Implement a deterministic renderer with an explicit data contract.
6. Render a source-sized comparison candidate and a final 600 dpi PNG.
7. Run `qa-asset.md` and resolve every failure.
8. Present the current production output for user visual approval.
9. Promote only the approved implementation, runtime manifest, neutral fixture, and preview into the public catalog.
10. Store private source material and development evidence outside the distributable skill.

## Promotion gates

An asset is publishable only when its entry point is deterministic, it depends only on stable runtime modules, its fixture is external, its manifest passes the catalog schema, special marks have a semantic contract, it passes rendered QA, and public files contain no private provenance or batch-module dependency.

User approval determines visual acceptance. Successful execution alone does not.
