# Institution templates

Institution templates are optional configuration packages. Econfigure Skill loads one only when the user names the institution, supplies a matching document, or explicitly selects the template.

Each institution directory must contain:

- `template.yaml`: machine-readable figure and table requirements;
- `README.md`: scope, source, verification date, and usage notes;
- the original template file when redistribution is permitted;
- optional style files or examples that are specific to that institution.

Use a lowercase English slug for the directory name. Copy `_template/template.yaml` when adding a school, replace every placeholder, add the institution README, and run `python scripts/eval_runner.py`. Never promote an institution package to the global visual baseline.
