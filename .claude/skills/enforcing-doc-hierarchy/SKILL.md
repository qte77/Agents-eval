---
name: enforcing-doc-hierarchy
description: Audits and aligns project documentation against the two authority chains (project docs and Claude Code infrastructure). Detects broken references, duplicates, scope creep, and chain breaks. Use when reviewing documentation health, fixing stale references, or enforcing single-source-of-truth.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [file-directory-or-full]
  allowed-tools: Read, Grep, Glob, Edit
---

# Enforce Documentation Hierarchy

**Scope**: $ARGUMENTS

Audits documentation against the two authority chains defined in
CONTRIBUTING.md "Documentation Hierarchy", then aligns violations with user
approval.

## Two Authority Chains

### 1. Project Documentation

```
UserStory.md (user workflows, acceptance criteria)
  -> docs/sprints/sprintN.prd.md (requirements -- symlinked to docs/PRD.md -> prd.json for Ralph)
    -> docs/architecture.md (technical design)
      -> Sprint implementation docs (current state)
        -> docs/howtos/ (operations)
          ^ docs/landscape/, docs/analysis/ (INFORMATIONAL ONLY)
```

### 2. Claude Code Infrastructure

```
CLAUDE.md (entry point -- inserts @AGENTS.md)
  -> AGENTS.md (behavioral rules, compliance, decision framework)
    -> CONTRIBUTING.md (technical workflows, commands, coding standards)
    -> .claude/rules/*.md (session-loaded rules)
    -> .claude/skills/*/SKILL.md (on-demand capabilities)
```

**Authority source**: See CONTRIBUTING.md "Documentation Hierarchy" for full
rules, reference flow, and anti-redundancy/anti-scope-creep policies.

### Content Authority (from AGENTS.md Information Source Rules)

| Content Type | Authoritative Source | NOT here |
|---|---|---|
| Requirements/scope | Sprint PRDs ONLY | architecture, howtos, landscape |
| User workflows | UserStory.md ONLY | architecture, sprint docs |
| Technical design | architecture.md ONLY | sprint docs, howtos, landscape |
| Current status | Sprint documents ONLY | architecture, UserStory |
| Operations | Usage guides (howtos/) ONLY | architecture, sprint docs |
| Research | landscape/, analysis/ | INFORMATIONAL — never requirements |

## When to Use

- After moving/renaming/deleting documentation files
- Before or after a sprint to verify doc health
- When adding new documents (verify correct tier placement)
- When reviewing PRs that touch docs
- Periodically as a hygiene check (`/enforcing-doc-hierarchy full`)

## Phase 1: Audit

Detect violations across the scope. For each finding, record:

| Source File | Line | Type | Description |
|-------------|------|------|-------------|
| path | Lnn | type | what's wrong |

### Violation Types

- **broken-ref**: Cross-reference points to a moved, renamed, or deleted file
- **stale-path**: File path in docs no longer matches actual location
- **duplicate**: Same content exists in multiple documents (DRY violation)
- **scope-creep**: Requirement-like content in landscape/analysis docs (should be in PRD or architecture)
- **wrong-authority**: Content placed in the wrong authoritative doc per the Content Authority table (e.g., user workflows in architecture.md, design decisions in howtos, requirements in sprint docs)
- **chain-break**: Missing link in an authority chain (e.g., AGENTS.md doesn't reference CONTRIBUTING.md)
- **symlink-invalid**: `docs/PRD.md` symlink target doesn't exist or points to wrong sprint

### Audit Procedure

1. **Determine scope** from `$ARGUMENTS`:
   - Specific file: audit that file's references and content placement
   - Directory: audit all `.md` files in that directory
   - `full` or empty: audit both authority chains end-to-end

2. **Validate cross-references**: Run `make lint_links` first as a fast
   pre-pass (lychee). Then grep for `@file` references and relative paths
   that lychee may miss.

3. **Check symlinks**: Verify `docs/PRD.md` symlink resolves to the current
   sprint PRD.

4. **Detect duplicates**: Look for substantial content (3+ lines) that appears
   in both an authoritative document and a dependent document.

5. **Check content placement** against the Content Authority table:
   - landscape/analysis: flag requirement-like language (`must`, `shall`,
     `required`, `will implement`) — scope-creep
   - architecture.md: flag user workflows or acceptance criteria — wrong-authority
   - sprint docs: flag design decisions that belong in architecture.md — wrong-authority
   - howtos: flag technical design or requirements — wrong-authority
   Distinguish informational references (describing external concepts) from
   project-level mandates (defining what this project must do).

6. **Verify chain integrity**: Confirm each document in both chains references
   the next document in the chain.

7. **Output findings table** sorted by violation type.

## Phase 2: Align

Resolve findings with user confirmation. For each violation, propose the fix
and wait for approval before applying.

### Resolution Procedures

| Violation | Procedure |
|---|---|
| **broken-ref** | Update path to new location. If target deleted, remove the reference. |
| **stale-path** | Grep all docs for old path. Replace with current path. |
| **duplicate** | Identify authoritative source by tier. Update it if needed. Replace duplicate with a reference link to the authority. |
| **scope-creep** | Move requirement-like content into PRD or architecture.md. Leave informational summary in source document. |
| **wrong-authority** | Identify correct authoritative doc per Content Authority table. Move content there; replace with reference link in source. |
| **chain-break** | Add missing reference to restore the chain link. |
| **symlink-invalid** | Update symlink to point to current sprint PRD. |

### Alignment Rules

- Always update the **authoritative** document first, then fix dependents
- Never duplicate -- replace with a reference to the authority
- Confirm each fix with the user before applying (list changes, ask approval)
- Keep edits minimal and targeted (only the reference/duplicate, not surrounding content)

## Workflow

1. **Scope**: Parse `$ARGUMENTS` to determine audit target
2. **Scan**: Grep cross-references across both hierarchies, validate targets
3. **Classify**: Check content placement against authority tier
4. **Report**: Output findings table
5. **Fix**: For each finding, propose fix and apply on user approval

## References

- CONTRIBUTING.md "Documentation Hierarchy" -- authority structure and rules
- AGENTS.md "Decision Framework" -- anti-scope-creep and anti-redundancy rules
- `.claude/rules/core-principles.md` -- DRY, KISS principles
