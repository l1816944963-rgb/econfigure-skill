# Agent installation adapters

Econfigure Skill uses `SKILL.md` as the canonical instruction source. Keep the full repository together because the skill resolves `references/`, `scripts/`, `assets/`, `styles/`, and `chartlib/` by relative path.

- Claude Code and Codex can load the repository as a native skill directory.
- Cursor uses the project rule in `cursor/econfigure.mdc` to route relevant requests to a stable repository clone.
- GitHub Copilot uses `copilot/copilot-instructions.md` as repository-wide instructions.

The adapters contain routing instructions only. Do not copy the full `SKILL.md` into each adapter, because duplicated instructions drift.
