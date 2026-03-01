---
name: auditing-website-accessibility
description: Audits website accessibility for WCAG 2.1 AA compliance, generating findings and code fixes. Use when reviewing accessibility, keyboard navigation, screen reader compatibility, or inclusive design.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [url-or-file-path]
  allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# Website Accessibility Audit

**Target**: $ARGUMENTS

Conducts focused accessibility audits against WCAG 2.1 AA and generates
implementable code fixes. No over-analysis.

## Audit Areas

### Keyboard Navigation

- Tab order and focus management
- Skip links and keyboard shortcuts
- Focus indicators and styling

### Screen Reader Compatibility

- ARIA landmarks and roles
- Semantic HTML structure
- Alternative text and descriptions
- Live region announcements

### Visual Accessibility

- Color contrast ratios (4.5:1 minimum)
- Responsive zoom (200% minimum)
- Motion and animation controls

### Forms and Data Tables

- Label associations and error handling
- Fieldset/legend usage and required field indicators
- Table header associations and caption elements

## Workflow

1. **Identify scope** from $ARGUMENTS (URL, file, or directory)
2. **Run automated checks** (axe-core, HTML validation, contrast ratios)
3. **Manual review** (keyboard-only navigation, screen reader, 200% zoom)
4. **Classify findings** by WCAG level and impact
5. **Generate code fixes** for each finding

## Output Format

### Findings

```text
CRITICAL (WCAG Level A)
- [Issue] - Impact: [High/Medium/Low] - Element: [selector]
  Fix: [Code snippet]
  WCAG: [Success Criterion]

COMPLIANCE (WCAG Level AA)
- [Issue] - Impact: [High/Medium/Low] - Element: [selector]
  Fix: [Code snippet]
  WCAG: [Success Criterion]
```

### Implementation Checklist

```text
- [ ] [Fix description] - Impact: [High/Medium/Low]
```

Group fixes by: Keyboard Navigation, Screen Readers, Visual, Forms/Tables.

## Rules

- Prioritize Level A violations before Level AA
- Every finding must include a specific, implementable code fix
- Test keyboard navigation and screen reader paths manually
- Keep output concise: findings + fixes + checklist only
