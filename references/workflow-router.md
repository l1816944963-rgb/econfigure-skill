# Workflow Router

Resolve the route before opening data, previews, production scripts, or long QA documents.

## Figure delivery

Use when the requested outcome is a new figure, a redesign, or a visual correction. Read `real-use-workflow.md`, then load retrieval and QA documents only when needed.

Do not ask routine setup questions. Use the defaults in `SKILL.md`. Ask only when one of these conditions blocks progress:

- The visual question or requested figure is indeterminate.
- The data location is unavailable.
- Multiple columns can plausibly fill the same required role.
- The requested design conflicts with the data structure.
- A supplied institution, journal, or physical-width requirement changes the design materially.

## Asset engineering

Use when the request changes the reusable library: creating, adding, revising, approving, or retiring an asset. Read `asset-engineering.md`, `figure-deconstruction.md`, and `qa-asset.md`.

## Library governance

Use for schemas, indexing, full-library audits, dependency cleanup, documentation architecture, or public packaging. Keep private development evidence outside runtime documentation.

## Three-line table

Use the table rules in `SKILL.md`. Do not load figure assets or figure QA unless the table request also includes a figure.

## Route changes

A request may change routes. A figure-delivery task becomes asset engineering only when the user asks to promote the result into the reusable library. A one-off bespoke figure does not automatically become an asset.
