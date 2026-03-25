---
name: enforcing-doc-hierarchy
description: Audits and aligns project documentation against authority chains (project docs and Claude Code infrastructure). Detects broken references, duplicates, scope creep, and chain breaks. Use when reviewing documentation health, fixing stale references, or enforcing single-source-of-truth.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [file-directory-or-full]
  allowed-tools: Read, Grep, Glob, Edit
---

# Enforce Documentation Hierarchy

**Scope**: $ARGUMENTS

Audits documentation against authority chains, then aligns violations with user
approval.

## Authority Chains

### 1. Project Documentation

Discover from the project's `CONTRIBUTING.md` "Documentation Hierarchy" section
(or equivalent). Typical chain:

```
UserStory / PRD (requirements, scope — PRIMARY AUTHORITY)
  → architecture.md (technical design)
    → Sprint / implementation docs (current state)
      → Usage guides / howtos (operations)
        ^ Research / landscape docs (INFORMATIONAL ONLY — never requirements)
```

### 2. Claude Code Infrastructure

```
CLAUDE.md (entry point)
  → AGENTS.md (behavioral rules, compliance, decision framework)
    → CONTRIBUTING.md (technical workflows, commands, coding standards)
    → .claude/rules/*.md (session-loaded rules)
    → .claude/skills/*/SKILL.md (on-demand capabilities)
```

### Content Authority

| Content Type | Authoritative Source | NOT here |
|---|---|---|
| Requirements/scope | PRDs ONLY | architecture, howtos, research |
| User workflows | User stories ONLY | architecture, sprint docs |
| Technical design | architecture.md ONLY | sprint docs, howtos, research |
| Current status | Sprint/impl docs ONLY | architecture, user stories |
| Operations | Usage guides ONLY | architecture, sprint docs |
| Research | Research/landscape docs | INFORMATIONAL — never requirements |

## When to Use

- After moving/renaming/deleting documentation files
- Before or after a sprint to verify doc health
- When adding new documents (verify correct tier placement)
- When reviewing PRs that touch docs
- Periodically as hygiene (`/enforcing-doc-hierarchy full`)

## Phase 1: Audit

Detect violations across the scope. For each finding, record:

| Source File | Line | Type | Description |
|-------------|------|------|-------------|
| path | Lnn | type | what's wrong |

### Violation Types

- **broken-ref**: Reference points to moved, renamed, or deleted file
- **stale-path**: File path in docs doesn't match actual location
- **duplicate**: Same content in multiple documents (DRY violation)
- **scope-creep**: Requirement-like content in research/landscape docs
- **wrong-authority**: Content in wrong doc per Content Authority table
- **chain-break**: Missing link in an authority chain

### Audit Procedure

1. **Determine scope** from `$ARGUMENTS`:
   - Specific file: audit that file's references and content placement
   - Directory: audit all `.md` files in that directory
   - `full` or empty: audit both authority chains end-to-end

2. **Validate cross-references**: Run `make lint_links` if available (lychee).
   Then grep for `@file` references and relative paths that lychee may miss.

3. **Detect duplicates**: Look for substantial content (3+ lines) in both an
   authoritative document and a dependent document.

4. **Check content placement** against Content Authority table:
   - Research/landscape: flag requirement-like language (`must`, `shall`,
     `required`, `will implement`) — scope-creep
   - architecture.md: flag user workflows or acceptance criteria — wrong-authority
   - Sprint docs: flag design decisions belonging in architecture.md
   - Distinguish informational references from project-level mandates.

5. **Verify chain integrity**: Confirm each document in both chains references
   the next document in the chain.

6. **Output findings table** sorted by violation type.

## Phase 2: Align

Resolve findings with user confirmation. Propose each fix and wait for approval.

| Violation | Procedure |
|---|---|
| **broken-ref** | Update path. If target deleted, remove reference. |
| **stale-path** | Grep all docs for old path, replace with current. |
| **duplicate** | Identify authority by tier. Replace duplicate with reference link. |
| **scope-creep** | Move requirement-like content to PRD/architecture. Leave summary. |
| **wrong-authority** | Move to correct doc per table. Replace with reference link. |
| **chain-break** | Add missing reference to restore chain link. |

### Alignment Rules

- Update the **authoritative** document first, then fix dependents
- Never duplicate — replace with a reference to the authority
- Confirm each fix with user before applying
- Keep edits minimal and targeted

## References

- CONTRIBUTING.md "Documentation Hierarchy" — authority structure and rules
- AGENTS.md "Decision Framework" — anti-scope-creep and anti-redundancy rules
- `.claude/rules/core-principles.md` — DRY, KISS principles
