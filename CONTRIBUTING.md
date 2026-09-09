# Contributing to Econfigure Skill

Contributions should improve applied-economics master's thesis figure production without changing analytical definitions.

## Asset contributions

1. Add one English kebab-case asset id under the appropriate `assets/figures/<family>/` directory.
2. Include a production script, synthetic or redistributable fixture, generated PNG preview, and `.asset.yaml` manifest.
3. Complete `required_data_roles`, `semantic_contract`, and `retrieval_contract`.
4. Keep source images and development evidence outside the distributable repository.
5. Run:

```bash
python scripts/build_catalog.py
python scripts/generate_atlas.py
python scripts/eval_runner.py --execute
python scripts/release_check.py
```

## Institution templates

Copy `assets/institution-templates/_template/`, use an English directory slug, cite an authoritative source, and bundle the original file only when redistribution is permitted. Institution templates must remain explicit opt-ins.

## Pull requests

Describe the user-facing problem, the resulting behavior, changed assets or rules, and validation performed. Do not include private source material, copied publication figures, caches, or local environments.

## Repository maintenance checks

Run `python scripts/release_check.py` before preparing a release. It checks required repository files, bilingual sections, local README links, generated catalog/atlas freshness, and development-artifact exclusions. This is a maintainer check, separate from real-use figure QA. Platform session validation and third-party redistribution review remain separate release responsibilities.
