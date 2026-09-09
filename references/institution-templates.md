# Institution template selection

Read an institution package only when the user names the institution, supplies a matching document, or explicitly selects the package.

1. Search `assets/institution-templates/` by the normalized institution name and aliases in `template.yaml`.
2. Prefer the user's supplied document over a bundled package when they conflict.
3. Apply only the fields relevant to the requested output. Do not let an institution package change the data contract.
4. Record the selected template id and any override in the QA report.
5. If the institution is absent, use the generic workflow and ask for a template only when an unresolved format requirement materially affects delivery.

To add another institution, copy `assets/institution-templates/_template/`, rename the directory with a lowercase English slug, complete the machine-readable fields from an authoritative source, add the original template only when redistribution is permitted, and run the full audit.
