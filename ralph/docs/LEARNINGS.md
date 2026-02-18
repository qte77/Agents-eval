<!-- markdownlint-disable MD024 no-duplicate-heading -->
# Ralph Loop Learnings

## Patterns to Apply

1. **Integration stories**: Add explicit wiring story after every 3-5 component stories
2. **Behavioral acceptance**: Test behavior ("detector returns score>20"), not interface ("returns dict")
3. **Dependency fields**: Add `depends_on`, `blocks`, `type` to prd.json schema
4. **Checkpoints**: Pause loop after component groups for smoke test
5. **Integration tests**: Verify wiring ("if detector returns X, evaluator outputs Y")

## Checklist (Before Marking Story Complete)

- [ ] Acceptance criteria test behavior, not just shape
- [ ] Integration story exists if this completes a component group
- [ ] No orphaned modules (all components used)
- [ ] Smoke test passes (E2E flow works)

## Schema Enhancement (TODO)

```json
{
  "id": "STORY-010",
  "type": "integration",
  "depends_on": ["STORY-006", "STORY-007", "STORY-008", "STORY-009"],
  "blocks": ["STORY-015"]
}
```

Adding `depends_on`/`blocks` to prd.json prevents this category of errors at the source.

---

## Learning 2: Platform Integration Gap

**Root Cause**: Implementation works in isolation but doesn't match target platform's integration contract.

**Pattern**: All unit tests pass, local testing works, but deployment/submission fails due to interface mismatch.

### Why This Happens

1. **Assumed equivalence**: "It works locally" ≠ "It works on platform"
2. **Late template analysis**: Reference implementations studied after building, not before
3. **Wrong test target**: Tested against own assumptions, not platform tooling

### Patterns to Apply

1. **Template-first development**: Study platform's reference implementation BEFORE coding
2. **Contract extraction**: Document exact interface requirements (CLI args, ports, endpoints, response format)
3. **Platform integration story**: Add explicit story to verify against platform's actual tooling
4. **Shadow testing**: Run platform's orchestration tools locally before submission

### Checklist (Platform Integration)

- [ ] Reference/template implementation analyzed before design
- [ ] CLI interface matches platform expectations exactly
- [ ] Default configuration (ports, timeouts) matches platform defaults
- [ ] Entry point pattern matches platform's invocation method
- [ ] Health/discovery endpoints match platform's probes
- [ ] Tested with platform's actual orchestration tooling (not just local equivalents)

### PRD Enhancement

For any platform-targeted project, add to PRD:

```markdown
**Platform Compatibility**:
- [ ] CLI interface: [exact args expected by platform]
- [ ] Entry point: [exact invocation pattern]
- [ ] Defaults: [ports, timeouts matching platform]
- [ ] Endpoints: [discovery/health endpoints platform probes]
- [ ] Validated against: [platform's tooling/scripts]
```

### Anti-Pattern

```text
BAD:  "Works on my machine" → Ship
GOOD: "Works with platform tooling" → Ship
```
