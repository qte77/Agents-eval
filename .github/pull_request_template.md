## Summary

<!-- Brief description of what this PR does and why -->

Closes <!-- #issue-number or N/A -->

## Type of Change

<!-- Check all that apply. Commit type must match .gitmessage: feat|fix|build|chore|ci|docs|style|refactor|perf|revert|test -->

- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` — no functional change
- [ ] `test` — test additions or fixes
- [ ] `ci` — CI/CD changes
- [ ] `build` — build system or dependency changes
- [ ] `perf` — performance improvement
- [ ] `style` — formatting, whitespace (no logic change)
- [ ] `revert` — reverts a previous commit
- [ ] `chore` — tooling, config, maintenance
- [ ] **Breaking change** — add `!` after commit type, e.g. `feat!:` or `feat(scope)!:`

## Self-Review

- [ ] I have reviewed my own diff and removed debug/dead code
- [ ] Commit messages follow [`.gitmessage`](../.gitmessage) format: `type[(scope)][!]: description`

## Testing

<!-- Skip make validate if only docs/config/ci files changed -->

- [ ] `make validate` passes — required if `src/` or `tests/` modified (lint + type check + tests)
- [ ] New functionality has corresponding tests
- [ ] Integration tested against real external dependencies (if applicable)

## Documentation

- [ ] [`CHANGELOG.md`](../CHANGELOG.md) updated under `## [Unreleased]` using correct section type:
  `Added` · `Changed` · `Deprecated` · `Removed` · `Fixed` · `Security`
- [ ] `AGENTS.md` updated if new patterns, role boundaries, or rules changed
- [ ] `AGENT_LEARNINGS.md` updated if a new pattern or solution was discovered
- [ ] `AGENT_REQUESTS.md` — resolved requests removed; new blockers added if any
- [ ] `CONTRIBUTING.md` updated if commands, paths, or coding standards changed
- [ ] Docstrings added/updated for all new/modified functions and classes

## Security

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No new SQL/command injection vectors
- [ ] Input validated at system boundaries (user input, external APIs)
- [ ] Sensitive data not logged or traced
