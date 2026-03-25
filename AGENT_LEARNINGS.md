---
title: Agent Learning Documentation
description: Non-obvious patterns that prevent repeated mistakes across sprints
version: 1.0.0
created: 2025-08-19
updated: 2026-03-07
---

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **Example**: Working code
- **References**: Related files

## Learned Patterns

### Error Handling and Performance Monitoring

- **Context**: Evaluation pipeline
- **Problem**: Generic errors lacked context; no bottleneck detection
- **Solution**: Tier-specific error messages + bottleneck warnings when >40% of total time
- **Example**: `if tier_time > total_time * 0.4: logger.warning(f"Bottleneck: {tier}")`
- **References**: `src/app/judge/evaluation_runner.py`

### PlantUML Theming

- **Context**: PlantUML diagrams in `docs/arch_vis`
- **Problem**: Redundant files for light/dark themes
- **Solution**: Single file with theme variable: `!ifndef STYLE !define STYLE "light" !endif` then `!include styles/github-$STYLE.puml`
- **References**: `docs/arch_vis/`

### Module Naming Conflicts

- **Context**: pyright validation with third-party libraries
- **Problem**: `src/app/datasets/` shadowed HuggingFace `datasets` library
- **Solution**: Use specific names: `datasets_peerread.py` not `datasets/`
- **References**: AGENTS.md Code Organization Rules

### External Dependencies Validation

- **Context**: Integrating external APIs (PeerRead dataset)
- **Problem**: Mocking without validation led to incorrect API assumptions
- **Solution**: Validate real APIs first (`requests.head(url)`), then mock. Test with small samples.
- **References**: PeerRead integration — wrong URLs undetected by mocks

### Agent Teams Parallel Orchestration

- **Context**: Claude Code agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)
- **Problem**: Need reusable pattern for parallel agent orchestration
- **Solution**: Independent reviewers with shared task list + dependency-blocked aggregation task. Traces in `~/.claude/teams/` and `~/.claude/tasks/`.
- **Example**:

  ```python
  TaskCreate(subject="Security review", ...)   # Task 1
  TaskCreate(subject="Quality review", ...)    # Task 2
  TaskCreate(subject="Coverage review", ...)   # Task 3
  TaskCreate(subject="Aggregate", blockedBy=["1","2","3"])  # Task 4
  ```

- **Key Finding**: Parallel reduces latency but token cost scales linearly (N teammates = N instances)
- **References**: `docs/reviews/evaluation-pipeline-parallel-review-2026-02-11.md`, `ai-agents-research/docs/cc-native/agents-skills/CC-agent-teams-orchestration.md`

### OpenAI-Compatible Provider Strict Tool Definitions

- **Context**: PydanticAI with OpenAI-compatible providers (Cerebras, Groq)
- **Problem**: PydanticAI's per-tool `strict` inference causes HTTP 422 with mixed values
- **Solution**: Disable via `OpenAIModelProfile(openai_supports_strict_tool_definition=False)`. Don't force `strict=True` — breaks defaults.
- **Example**: `OpenAIChatModel(provider=..., profile=OpenAIModelProfile(openai_supports_strict_tool_definition=False))`
- **References**: `src/app/llms/models.py`, [OpenAI Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)

### Pydantic validation_alias for External Data Mapping

- **Context**: Pydantic models with different external key names (PeerRead `IMPACT` → `impact`)
- **Problem**: `alias` breaks constructor signature; `model_validator(mode="before")` couples to external format
- **Solution**: Use `validation_alias` (only affects `model_validate()`) + `ConfigDict(populate_by_name=True)`
- **Example**: `impact: str = Field(default="UNKNOWN", validation_alias="IMPACT")`
- **Anti-pattern**: Sentinel keys in data dicts (e.g., `_paper_id`). Use Pydantic's `context` parameter.
- **References**: `src/app/data_models/peerread_models.py`, `src/app/data_utils/datasets_peerread.py`

### Measurable Acceptance Criteria for Meta-Tasks

- **Context**: PRD meta-tasks (reviews, audits, assessments)
- **Problem**: "Review completed" not verifiable
- **Solution**: Three gates: (1) Coverage - every scope item has findings or explicit "no issues", (2) Severity - zero critical unfixed; high findings fixed or tracked, (3) Artifact - document exists with required structure. No minimum finding counts to avoid padding.
- **Anti-pattern**: Minimum finding counts incentivize noise
- **References**: Sprint 5 Features 10-11, `docs/reviews/sprint5-code-review.md`

### Streamlit Background Execution Strategy

- **Context**: Long tasks (LLM calls, pipelines) without blocking UI
- **Problem**: Tab navigation aborts execution; `threading.Thread` session state writes not thread-safe
- **Solution**: Prefer `st.fragment` (1.33+) for isolated re-runs. Fall back to `threading.Thread` + synchronized writes when execution must survive full re-renders.
- **Decision rule**: `st.fragment` for single component; `threading.Thread` + callback for page-level survival
- **References**: `src/gui/pages/run_app.py`, Streamlit docs

### PRD Files List Completeness Check

- **Context**: Writing sprint PRD features with acceptance criteria, technical requirements, and files lists
- **Problem**: Files referenced in acceptance criteria or technical requirements but missing from Files list. Implementers working from Files list miss changes.
- **Solution**: After writing each feature, verify every file referenced in AC and tech requirements appears in Files with correct annotation (new/edit/delete).
- **References**: Sprint 6 Features 2, 7 (caught in post-task review)

### Claude Code Headless Invocation for Benchmarking

- **Context**: Running CC from Python for MAS vs CC baseline comparison
- **Problem**: Sprint 3 `cc_otel` used wrong abstraction — CC tracing is infrastructure (env vars), not application code
- **Solution**: `claude -p "prompt" --output-format json` via `subprocess.run()`. Check with `shutil.which("claude")`. Collect artifacts from `~/.claude/teams/` + `~/.claude/tasks/`, parse via `CCTraceAdapter`.
- **References**: `ai-agents-research/docs/cc-native/agents-skills/CC-agent-teams-orchestration.md`, Sprint 6 Feature 7

### Review-to-PRD Traceability

- **Context**: Planning a sprint after a security review or code audit produced findings tagged for future sprints
- **Problem**: Review findings fall through the cracks between sprints. The Sprint 5 MAESTRO review tagged 14 findings as "Sprint 6" or "Sprint 7+" but the initial Sprint 6 PRD had zero of them.
- **Solution**: After any review/audit sprint, the next PRD must account for every finding: feature, Out of Scope with sprint attribution, or explicitly dismissed with rationale. Checklist: for each review finding, grep the PRD for its ID or description.
- **Anti-pattern**: Assuming review findings will be remembered. They won't.
- **References**: Sprint 5 `docs/reviews/sprint5-code-review.md` → Sprint 6 Features 10-13 + Out of Scope

### Coverage Before Audit Ordering

- **Context**: Sprint includes both adding test coverage and deleting low-value tests
- **Problem**: Deleting implementation-detail tests first creates a coverage gap. A module at 27% loses tests before behavioral replacements exist.
- **Solution**: Order coverage improvements before test pruning. Express as `depends:` in story breakdown. Prove behavioral coverage exists, then safely prune.
- **Anti-pattern**: "Clean up first, then build" — creates a coverage valley between deletion and addition.
- **References**: Sprint 6 Features 14-15 (STORY-015 depends on STORY-014)

### CVE Version Check Before PRD Story

- **Context**: Writing a CVE remediation story from a security review finding
- **Problem**: Review says "upgrade scikit-learn to >=1.5.0 for CVE-2024-5206." Author writes the story without checking `pyproject.toml`. Turns out `scikit-learn>=1.8.0` already pinned — CVE already mitigated. Wasted story.
- **Solution**: Before writing any CVE story, check current dependency version. If patched, note in PRD description ("already mitigated by...") and skip.
- **References**: Sprint 6 Feature 10 (scikit-learn CVE dismissed after version check)

### SSRF Allowlist Must Match Actual HTTP Call Sites

- **Context**: SSRF URL validation with domain allowlisting
- **Problem**: Allowlist built from *conceptual* dependencies (which services we use) rather than *actual* `validate_url()` call sites. Result: `api.github.com` missing (used but rejected), 3 LLM provider domains present (listed but never checked — PydanticAI uses its own HTTP clients).
- **Solution**: Grep for `validate_url(` calls, trace each URL back to its domain. Only list domains that actually pass through the validation function.
- **Anti-pattern**: Listing domains based on "what services does the project talk to" instead of "what domains flow through this specific validation gate."
- **References**: `src/app/utils/url_validation.py`, `src/app/data_utils/datasets_peerread.py:300`

### Test Filesystem Isolation (tmp_path)

- **Context**: Tests that mock network calls but call real write paths (e.g., `_save_file_data`, `_download_single_data_type`)
- **Problem**: Mocking `download_file` prevents network access but unmocked methods still write to real project directories (e.g., `datasets/peerread/`). Mock data pollutes the source tree and breaks subsequent app runs.
- **Solution**: Always redirect `cache_dir` or any write-target path to `tmp_path` in tests that trigger file writes, even when the download itself is mocked.
- **Example**: `downloader.cache_dir = tmp_path / "cache"` before calling `download_venue_split()`
- **Anti-pattern**: Only mocking the network layer and assuming no disk side-effects. If the code has `mkdir` + `open()` + `write()`, those still execute against real paths.
- **Also applies to**: Mock data strings containing `/tmp` paths (Bandit B108 flags even non-filesystem string literals). Use `str(tmp_path / "name")` in fixture data to avoid false positives.
- **References**: `tests/data_utils/test_datasets_peerread.py:601`, `src/app/data_utils/datasets_peerread.py:468`

### CC Teams Artifacts Ephemeral in Print Mode

- **Context**: Running `claude -p` (headless/print mode) for CC baseline collection
- **Problem**: `~/.claude/teams/` and `~/.claude/tasks/` are empty after `claude -p` completes. `CCTraceAdapter` teams parser finds no artifacts to parse.
- **Solution**: Teams artifacts are ephemeral in print mode — they exist only during execution. For teams trace data, parse `raw_stream.jsonl` for `TeamCreate`, `Task`, `TodoWrite` events instead of relying on filesystem artifacts.
- **Anti-pattern**: Assuming `~/.claude/teams/` persists after headless invocation. It doesn't — only interactive sessions leave persistent team state.
- **References**: `scripts/collect-cc-traces/run-cc.sh`, ADR-008

### CC OTel Exports Metrics/Logs Only — No Trace Spans

- **Context**: Configuring `OTEL_*` env vars in `.claude/settings.json` for CC observability
- **Problem**: CC OTel integration was described as providing "Tool-level traces" and "LLM-call traces", implying trace spans. In practice, CC OTel exports only metrics and logs — no distributed trace spans. This is an upstream limitation in the CC instrumentation layer.
- **Solution**: For trace-level execution analysis (required for evaluation), use artifact collection (`CCTraceAdapter` parses `raw_stream.jsonl`). OTel is supplementary for cost/token dashboards only.
- **Key distinction**: metrics/logs → OTel → Phoenix dashboards; trace spans → artifact collection → `CCTraceAdapter` → `GraphTraceData`
- **Upstream issues**: [anthropics/claude-code#9584](https://github.com/anthropics/claude-code/issues/9584), [#2090](https://github.com/anthropics/claude-code/issues/2090)
- **References**: `ai-agents-research/docs/cc-native/agents-skills/CC-agent-teams-orchestration.md`, `.claude/settings.json` (OTel vars currently disabled)

### Makefile $(or) Does Not Override ?= Defaults

- **Context**: Makefile variable defaults with `?=` and `$(or $(VAR),fallback)` pattern
- **Problem**: `CC_MODEL ?= sonnet` sets `CC_MODEL` to `"sonnet"` at parse time. `$(or $(CC_MODEL),fallback)` always sees `CC_MODEL` as truthy (non-empty), so the fallback never triggers — even when the user hasn't explicitly set the variable.
- **Solution**: Use separate variables for user-facing defaults and internal fallbacks. Or use `ifdef`/`ifndef` guards instead of `$(or)` when the variable has a `?=` default.
- **Example**: Instead of `TIMEOUT := $(or $(CC_TEAMS_TIMEOUT),600)`, use `CC_TEAMS_TIMEOUT ?= 600` directly — the `?=` already provides the default.
- **References**: `Makefile` (cc_run_solo, cc_run_teams recipes)

### Repeated Dispatch Chains Inflate File Complexity

- **Context**: Multiple methods in a module dispatch on the same enum/string value
- **Problem**: `datasets_peerread.py` has 4 methods each with `if/elif/else` over `data_type` ("reviews"/"parsed_pdfs"/"pdfs"). Each chain adds 3 CC points = 12 total from one repeated pattern.
- **Solution**: Replace with a registry dict (`DATA_TYPE_SPECS`). Dispatch becomes a single lookup. Validates once at entry point.
- **Anti-pattern**: Copy-pasting dispatch logic into each method that needs type-specific behavior.
- **References**: `src/app/data_utils/datasets_peerread.py`, CodeFactor Sprint 7 review

### Shell Keyword Collision in jq Arguments (SC1010)

- **Context**: Bash scripts calling `jq` with `--argjson` or `--arg`
- **Problem**: `jq -r --argjson done "$var" '...$done...'` triggers ShellCheck SC1010 because `done` is a shell keyword. ShellCheck can't distinguish jq argument names from shell syntax.
- **Solution**: Avoid shell keywords (`done`, `then`, `fi`, `do`, `esac`) as jq variable names. Use descriptive names matching the bash variable feeding them.
- **Example**: `--argjson completed "$completed"` instead of `--argjson done "$completed"`
- **References**: `ralph/scripts/ralph.sh` (`get_next_story`, `get_unblocked_stories`)

### Pipe-into-While Loses Variable Assignments (Bash Subshell)

- **Context**: Bash `while read` loops processing multi-line variables in Ralph shell scripts
- **Problem**: `echo "$var" | while read -r line; do found=true; done` — pipe creates a subshell, so `found=true` never propagates to the parent. Duplicate detection loops or post-loop checks are needed as workarounds, adding fragile complexity.
- **Solution**: Use here-string to keep the loop in the current shell: `while read -r line; do ...; done <<< "$var"`
- **Example**: `while IFS= read -r filepath; do found=true; done <<< "$files"` instead of `echo "$files" | while ...`
- **Anti-pattern**: Adding a second subshell loop to detect what the first loop already computed but couldn't propagate.
- **References**: `ralph/scripts/lib/snapshot.sh` (test files section), ShellCheck SC2031

### Stale Test Fixtures Cause Cross-File Pollution

- **Context**: Full `make test` suite with tests that error/fail due to stale fixtures (e.g., patching removed imports)
- **Problem**: Test fixture errors (e.g., `patch("module.removed_name")`) don't clean up properly. Shared singletons or module-level state mutated during failed setup leaks into subsequent test files. Test passes in isolation but fails in full suite.
- **Solution**: Delete stale tests promptly. When a source module changes (renamed/removed imports, restructured widgets), update or delete tests that patch the old interface. Use `pytest --lf` (last failed) + bisection to identify the polluter: `uv run pytest tests/suspect_dir/ tests/failing_test.py`
- **Anti-pattern**: Leaving failing tests in the suite "to fix later." Their fixture side-effects silently corrupt other tests.
- **Detection**: Test passes alone (`uv run pytest tests/file.py`) but fails in full suite (`make test`). Run directory batches to bisect.
- **References**: `tests/gui/test_settings.py` (deleted), `tests/test_gui/test_settings_page.py` (deleted) — fixture patching `gui.pages.settings.text` after import was removed

### Cerebras Structured Output Non-Compliance in MAS Delegation

- **Context**: PydanticAI agents with `openai_supports_strict_tool_definition=False` providers (Cerebras, Groq, etc.)
- **Problem**: Three failure modes observed with Cerebras `gpt-oss-120b`:
  1. **Score fields as text**: Model returns natural language descriptions where `int` is expected (e.g., `"The work documents..."` for `impact: int`). Also returns word labels (`"accept"`) and floats (`0.78`).
  2. **Wrong output type for general queries**: `enable_review_tools: bool = True` default in `main()` forced `ReviewGenerationResult` even for non-paper queries, triggering 422 from Cerebras on schema retry.
  3. **Tool arg/output confusion**: Model calls `delegate_synthesis(insights=[...], recommendations=[...], approval=True)` instead of `delegate_synthesis(query="...")` — dumping the previous agent's output schema as tool input args.
- **Solution**:
  1. `BeforeValidator` coercions (`_ScoreInt`, `_PresentationFormatLiteral`) on `GeneratedReview` to handle text→int, float→int, word→score mapping.
  2. Changed `enable_review_tools` default to `False`; `_prepare_query` activates it when `paper_id` is present.
  3. Improved delegation tool docstrings to explicitly state `query` must be a plain text string, NOT structured data.
- **Anti-pattern**: Assuming OpenAI-compatible providers follow JSON schema constraints. Without `strict=True` support, models may ignore type constraints entirely.
- **References**: `src/app/data_models/peerread_models.py` (coercions), `src/app/app.py:343` (default fix), `src/app/agents/agent_system.py` (tool docstrings)

### BERTScore Class-Level Lazy Loading with Failure Caching

- **Context**: `TraditionalMetricsEngine` initializing BERTScorer (downloads HuggingFace model)
- **Problem**: Per-instance lazy loading retries BERTScorer init on every new engine instance. In environments with read-only HF cache or no network, each attempt costs ~200ms. Hypothesis property tests (many instances) exceed deadline; performance tests fail.
- **Solution**: Class-level `_bertscore_instance` and `_bertscore_init_failed` flags. First successful init is shared across all instances. First failure is cached — no retries.
- **Example**: `TraditionalMetricsEngine._bertscore_instance = BERTScorer(...)` (class attr, not `self._bertscore`)
- **Anti-pattern**: Instance-level lazy loading for expensive singletons. Each `__init__` retries the same failing operation.
- **Also applies to**: Tests must reset class-level cache between test cases (`autouse` fixture setting both attrs to `None`/`False`).
- **References**: `src/app/judge/traditional_metrics.py`, `tests/evals/test_traditional_metrics.py::TestBERTScoreReenablement`

### Auto Provider Model Resolution via PROVIDER_REGISTRY

- **Context**: `LLMJudgeEngine` with `tier2_provider=auto` resolving to non-OpenAI providers (Cerebras, Groq)
- **Problem**: Auto-resolved provider inherits `tier2_model` default (`gpt-4o-mini`), which doesn't exist on the resolved provider's API. Cerebras returns 401; Groq returns 404.
- **Solution**: After auto-resolution, when `chat_model=None`, consult `PROVIDER_REGISTRY[provider].default_model`. If set, use it instead of `tier2_model`.
- **Example**: Cerebras auto-resolved → `PROVIDER_REGISTRY["cerebras"].default_model` = `"gpt-oss-120b"` → used instead of `"gpt-4o-mini"`
- **Anti-pattern**: Assuming a single default model works across all providers. Each provider has its own model namespace.
- **References**: `src/app/judge/llm_evaluation_managers.py:_resolve_model()`, `src/app/data_models/app_models.py:PROVIDER_REGISTRY`

### `-X ours` Does Not Delete Files Added by Theirs

See `ralph/docs/LEARNINGS.md` section 4 (authoritative).

### PR Squash Merge via GitHub API Requires Both Title and Message

- **Context**: Merging a PR via GitHub API (e.g. Ralph branch or any feature branch)
- **Problem**: `commit_title` alone drops all branch commit messages from the squash body. Title must follow repo convention `PR <title> (#NUM)` to match history.
- **Solution**:
  ```bash
  gh api repos/OWNER/REPO/pulls/NUM/merge \
    -X PUT \
    -f merge_method=squash \
    -f commit_title="PR <title> (#NUM)" \
    -f commit_message="$(git log origin/main..HEAD --format='* %s')"
  ```
- **Anti-pattern**: Passing only `commit_title` — squash body will be empty, losing branch commit history
- **References**: `ralph/docs/LEARNINGS.md` (section 4)

### `gh pr edit` Fails with Projects Classic Deprecation

- **Context**: Editing PR title or body via GitHub CLI
- **Problem**: `gh pr edit` exits with GraphQL error about Projects (classic) deprecation — even for unrelated edits
- **Solution**: Use GraphQL mutation directly:
  ```bash
  PR_ID=$(gh pr view NUM --json id --jq '.id')
  gh api graphql -f query="mutation { updatePullRequest(input: {pullRequestId: \"$PR_ID\", title: \"...\", body: \"...\"}) { pullRequest { title } } }"
  ```
- **Anti-pattern**: Retrying `gh pr edit` — always fails until GitHub removes the deprecated Projects field from the PR schema

### Claude Code Sandbox Blocks Git on `.claude/skills/`

- **Context**: Any git operation (reset, stash, pull, checkout) touching `.claude/skills/` paths
- **Problem**: `.claude/skills/` is write-denied in the Bash tool sandbox. Git operations that modify files there fail with "Read-only file system" — including `git reset --hard`, `git stash`, `git pull`
- **Solution**: Use Edit/Write tools for file changes in `.claude/skills/`; run git from a non-sandboxed terminal when those paths are involved
- **Anti-pattern**: `git reset --hard` or `git clean` to resolve conflicts involving skill files — always fails in sandbox

### Cross-Repo Sandbox Write Access

- **Context**: Claude Code sessions needing to write to sibling repos (e.g., `/workspaces/qte77/dotfiles` from an `/workspaces/Agents-eval` session)
- **Problem**: Bash sandbox `write.allowOnly` defaults to CWD. Write/Edit tools work cross-repo, but `git add`, `git commit`, and other Bash commands fail with "Read-only file system" for paths outside CWD.
- **Solution**: Add the parent workspace path to `sandbox.filesystem.write.allowOnly` in `.claude/settings.json`:

```json
"sandbox": {
  "filesystem": {
    "write": {
      "allowOnly": ["/tmp/claude-1000", ".git", "/workspaces/qte77"]
    }
  }
}
```

- **Alternative**: Use `sandbox.filesystem.allowWrite` (additive array, merges across scopes) instead of modifying `allowOnly`. Or set in `~/.claude/settings.json` (user-level) to apply globally.
- **Key insight**: Write/Edit tools bypass the Bash sandbox — they have their own permission model. Only Bash tool commands are sandboxed. So file reads/writes work cross-repo even without sandbox changes, but git operations don't.
- **References**: `CC-sandboxing-analysis.md` (path prefix conventions, array merging), `.claude/settings.json`

### uv `exclude-newer` Silently Blocks Dependency Resolution

- **Context**: Upgrading a dependency with `uv lock --upgrade-package <pkg>` when `pyproject.toml` has `[tool.uv] exclude-newer`
- **Problem**: Package exists on PyPI but uv resolves to an older version. Verbose logs show `Selecting: pkg==old [compatible]` with no error. Root cause: the package was uploaded after the `exclude-newer` cutoff date, so uv treats it as non-existent.
- **Solution**: Check `exclude-newer` date first when upgrades fail silently. Update it before debugging cache, index, or version constraints.
- **Anti-pattern**: Debugging with `--no-cache`, `--refresh-package`, or alternate `UV_CACHE_DIR` when the real blocker is the date cutoff.
- **References**: `pyproject.toml` (`[tool.uv]` section)

### GitHub API Enum Values Use Spaces Not Underscores

- **Context**: Calling GitHub REST API with enum parameters (e.g., `dismissed_reason` for code scanning alerts)
- **Problem**: `-f dismissed_reason=false_positive` returns HTTP 422. The API expects `"false positive"` (space-separated), not `false_positive` (underscore).
- **Solution**: Quote enum values with spaces: `-f "dismissed_reason=false positive"`. Always check the API error message — it lists valid enum members.
- **Anti-pattern**: Assuming snake_case for enum values because the field name is snake_case.
- **References**: [GitHub Code Scanning API](https://docs.github.com/rest/code-scanning/code-scanning#update-a-code-scanning-alert)

### CodeQL `actions` Language for Bash/GHA Repos

- **Context**: CodeQL workflow in a repo with only bash scripts and GitHub Actions YAML (no JS/TS/Python)
- **Problem**: `languages: javascript-typescript` causes `CodeQL detected code written in GitHub Actions, but not any written in JavaScript/TypeScript` error. Build succeeds but analyze fails.
- **Solution**: Use `languages: actions`. Remove the `autobuild` step (not needed for actions analysis).
- **Example**: `github/codeql-action/init@v4` with `languages: actions` → `github/codeql-action/analyze@v4`
- **References**: `gha-github-mirror-action/.github/workflows/codeql.yaml`

### PAT Scrubbing in Shell Scripts (Defense in Depth)

- **Context**: Shell scripts that handle PATs and run `git push` with authenticated URLs
- **Problem**: `::add-mask::` only works inside GitHub Actions. Outside GHA (local, other CI), PATs leak in git error messages, command output, and bash error traces.
- **Solution**: Wrap script body in `_main()` function, pipe all output through `sed "s|$PAT|***|g"`. Use `PIPESTATUS[0]` to preserve exit code.
- **Example**:
  ```bash
  _main() { ... }
  _sed_expr=""
  [ -n "${PAT:-}" ] && _sed_expr="s|${PAT}|***|g;"
  _main 2>&1 | sed "$_sed_expr"
  exit "${PIPESTATUS[0]}"
  ```
- **Anti-pattern**: Relying solely on `::add-mask::` — it's a GHA-specific command, not a universal solution.
- **References**: `gha-github-mirror-action/scripts/mirror.sh`

### BATS Tests Need Git Identity in CI

- **Context**: BATS tests that create temporary git repos and run `git commit`
- **Problem**: CI runners (GitHub Actions `ubuntu-latest`) lack `user.name`/`user.email` git config. `git commit` fails with "Please tell me who you are".
- **Solution**: Add `git config --global user.name "test"` and `git config --global user.email "test@test"` in BATS `setup()`.
- **Also**: Use `$BATS_TEST_NUMBER` (not `$$`) for unique temp dir names — `$$` is the bats process PID, same across all tests in a run.
- **References**: `gha-github-mirror-action/tests/unit/test_mirror.bats`

### Dependabot Rebase Fails with GPG Signing Mismatch

- **Context**: Rebasing dependabot PRs onto updated main when GPG signing is required
- **Problem**: `git rebase origin/main` fails with "gpg failed to sign the data: Author is invalid" because the dependabot commit author doesn't match the GPG signing identity.
- **Solution**: Close the dependabot PR. Create a fresh branch from main, apply the same change manually (usually a single version bump in a workflow file), create new PR.
- **Anti-pattern**: Trying `--no-gpg-sign` or `git -c commit.gpgsign=false rebase` — won't merge if branch protection requires signed commits.
- **References**: `gha-github-mirror-action` PR #3 (closed) → PR #4 (replacement)

### First Release Bootstrap for bump-my-version Repos

- **Context**: New repo with `pyproject.toml` version already set to target (e.g., `0.1.0`), need to create initial release
- **Problem**: `bump-my-version` always increments — running `patch` on `0.1.0` gives `0.1.1`, not `0.1.0`. No "tag current version" mode.
- **Solution**: Create first release manually via GitHub API: tag + release + floating major tag. Then `bump-my-version` handles all subsequent releases.
- **Example**:
  ```bash
  gh api repos/OWNER/REPO/git/refs -f ref=refs/tags/v0.1.0 -f sha=$SHA
  gh release create v0.1.0 --generate-notes
  gh api repos/OWNER/REPO/git/refs -f ref=refs/tags/v0 -f sha=$SHA
  ```
- **References**: `gha-github-mirror-action` v0.1.0 release

### Plugin/Package Version Must Be Synced Across Manifest Files

- **Context**: Multi-manifest package systems (CC plugins with `plugin.json` + `marketplace.json`, npm with `package.json` + `package-lock.json`, etc.)
- **Problem**: Bumping the version in one manifest but not the other causes CI validation failures. The version check compares across files.
- **Solution**: When bumping versions, grep for the old version string across all manifest files and update all occurrences. For CC plugins: `plugin.json` AND `marketplace.json`.
- **Anti-pattern**: Only bumping the "primary" manifest and assuming CI will pass.
- **References**: `.claude-plugin/marketplace.json`, `plugins/*/. claude-plugin/plugin.json`
