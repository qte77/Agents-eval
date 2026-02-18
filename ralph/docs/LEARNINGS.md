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
