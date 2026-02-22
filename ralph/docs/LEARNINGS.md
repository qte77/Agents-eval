---
title: Ralph Loop Learnings
scope: Patterns discovered during Ralph autonomous development
usage: Read before writing PRDs or running Ralph loop
---

<!-- markdownlint-disable MD024 MD025 -->

## 1. Story Completion Checklist

- [ ] AC tests behavior, not shape ("returns score>20" not "returns dict")
- [ ] Integration story exists after every 3-5 component stories
- [ ] No orphaned modules — all components wired
- [ ] `generate_prd_json.py --dry-run` AC/files counts match expectations

## 2. PRD Parser Constraints

`generate_prd_json.py` silently drops content that doesn't match its regex.

| Constraint | Why | Fix |
| --- | --- | --- |
| One `#####` heading per story | `##### 8.2 + 8.3` breaks regex | Split into separate headings |
| Top-level `- [ ]` only | Indented sub-items invisible to parser | Flatten to individual checkboxes |
| Sub-feature needs own `**Files**:` | `re.search` finds parent's (wrong scope) or nothing | Add per-sub-feature, remove parent's |
| Parser copies parent description | `resolve_stories()` ignores sub-feature text | Fix manually in prd.json + rehash |

```text
BAD:  - [ ] Module with:        ← parser sees 1 item
        - helper_a()
        - helper_b()
GOOD: - [ ] Module created       ← parser sees 3 items
      - [ ] helper_a()
      - [ ] helper_b()
```

## 3. Platform Integration

Study the target platform's reference implementation BEFORE coding.

- [ ] Extract exact interface contract (CLI args, ports, response format)
- [ ] Add explicit integration story to verify against platform tooling
- [ ] Test with platform's orchestration tools, not local equivalents

## 4. Worktree Branch Merge Strategy

Ralph runs on a worktree branch. Merge back with **squash merge**.

```bash
# After Ralph completes (from main repo)
git merge --squash ralph/<branch>
git commit -m "feat(sprintN): implement stories via Ralph"
git worktree remove ../<worktree-dir>
git branch -d ralph/<branch>
```

**Why squash**: RED/GREEN/REFACTOR commits (~3 per story) are implementation noise. Final state per story is what matters. Single commit is easy to revert. Full TDD history preserved on the branch until deletion.

**Conflict prevention**: Don't edit files listed in `prd.json` stories on the source branch while Ralph runs. The `files` arrays are the off-limits list.

**If conflicts occur**: Resolve manually (small conflicts), rebase worktree first (large conflicts), or `git merge --squash -X theirs` (accept Ralph's version wholesale).

**`-X ours` blind spot**: `-X ours`/`-X theirs` only applies to conflicted hunks. Files added exclusively by the other branch are auto-merged as clean additions — no conflict, no strategy override. After resolving conflicts with `-X ours`, diff against the pre-merge state and `git rm` any files the other branch introduced that shouldn't exist.

**Missing GPG signatures**: If push is rejected due to unsigned commits, re-sign from the earliest unsigned commit: `git rebase --exec 'git commit --amend --no-edit --gpg-sign' <commit-id>~1` then `git push --force-with-lease`. Rebase replays commits after the given base — `~1` targets the parent so `<commit-id>` itself is included. `--exec` runs the amend-sign after each replayed commit. `--force-with-lease` safely pushes the rewritten history.

## 5. Story Scope Must Include All Consumers of Changed Interfaces

PRD `files` lists are authored manually and often miss pre-existing tests that assert on renamed symbols, changed output formats, or widget counts.

**Sprint 8 incident**: Three stories (STORY-001, STORY-011, STORY-012) each passed `make validate` but left stale tests in `tests/security/` and `tests/test_gui/` because those files weren't in the PRD `files` list. The OOM-hanging test masked the failures by killing the process before reaching them.

**Mitigations:**

- [x] **Impact grep before implementation**: When a story renames a symbol or changes observable behavior, grep the full test tree for the old value. Add any consuming test file to the story scope, even if not in the PRD `files` list. Implemented as prompt instruction in `prompt.md` (impact scan section).
- [x] **Distinguish killed vs failed validation**: Exit codes 137/143 (SIGTERM/OOM) mean `make validate` was killed -- result is inconclusive, not PASS. Ralph should retry or flag, never record PASS. Implemented as inline check in `baseline.sh:run_quality_checks_baseline()`.
- [ ] **Snapshot drift detection**: After each story, run `uv run pytest --inline-snapshot=review` to surface stale inline snapshots that normal assertions may not catch quickly.
- [ ] **Cross-directory test discovery**: Flag when a source file has tests in multiple directories (e.g., `tests/gui/` and `tests/test_gui/`). Consolidating split test directories prevents this class of oversight entirely.
- [ ] **Post-story targeted regression**: After completing a story, run tests that import or reference the changed modules specifically, in addition to the full suite. Faster, more targeted, and not masked by unrelated hangs.
