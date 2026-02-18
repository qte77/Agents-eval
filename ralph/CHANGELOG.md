# Changelog

All notable changes to Ralph Loop will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- **Worktree Launcher**: `ralph-in-worktree.sh` + `make ralph_worktree` — create branch, setup git worktree, run Ralph (same env var contract as `ralph_run`)
- **PRD Parser Constraints**: Documented 4 parser gotchas in `LEARNINGS.md` (table) and `prd.md.template` (inline comments)
- **Merge Strategy**: Squash merge pattern and conflict prevention rule in `LEARNINGS.md`
- **Wave Terminology**: Defined "wave" (dependency graph frontier) in `ralph.sh` and `README.md`
- **Sprint 8 prd.json**: 14 stories with file-conflict peer deps for teams mode (Wave 4a/4b/4c)
- **CC Agent Teams as alternative orchestrator**: PRD dual-mode support (Ralph loop + CC Teams), file-conflict dependencies, orchestration waves, teammate prompt template
- **Known Failure Mode #5**: File-conflict dependencies not tracked in `get_unblocked_stories`
- **Agent Activity Monitor**: Heartbeat now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors (`common.sh`: `log_cc`, `log_cc_error`)
- **Quality Retry Context**: Failed quality gate name is passed to the agent prompt on retry via `RETRY_CONTEXT_FILE`, so the agent knows what to fix
- **PRD Parser**: Parser for structured PRD.md files with automatic prd.json generation
- **TDD Workflow**: Optional REFACTOR phase with RED/GREEN/REFACTOR commit markers and chronological verification
- **Template System**: Comprehensive templates for progress.txt and prd.json with parser-compatible structure
- **Documentation**: README.md with Ralph Loop overview, extended functionality guide, and usage examples
- **Project Templates**: Interactive setup script with auto-detection of git repo, author, and Python version

### Changed

- **LEARNINGS.md**: Condensed from 114 to ~55 lines, added frontmatter, replaced verbose prose with actionable table and checklists
- **PRD-Sprint8**: Flattened AC sub-items, added sub-feature Files sections, merged compound sub-features, added file-conflict peer deps
- **Documentation Structure**: Reorganized ralph/ directory structure and moved TEMPLATE_USAGE.md to ralph root
- **Skill System**: Relocated commands to skills structure (`.claude/skills/`)
- **Default Configuration**: Increased max iterations to 25, set REQUIRE_REFACTOR to false by default
- **State Files**: Consolidated Ralph script utilities and simplified story processing
- **PRD Format**: Updated to v3.0 with A2A protocol and AgentBeats competition details

### Fixed

- **CC Monitor Log Nesting**: Replace `tail -5` with byte offset tracking (`wc -c`) so monitor reads only new log content per 30s cycle, preventing `[CC] [INFO] [CC] [INFO] ...` chains
- **Worktree VIRTUAL_ENV Mismatch**: Launch `ralph.sh` via `env -u VIRTUAL_ENV` so uv discovers `.venv` via symlink without devcontainer mismatch warnings; capture `SOURCE_VENV=$PWD` before `cd` (replaces `git rev-parse`)
- **Worktree Phantom chmod**: Replace `make_executable()` with `check_executable()` in `init.sh` — warn instead of writing, preventing phantom permission changes on read-only worktree filesystems
- **CC Monitor Log Dedup**: Strip inner log-level prefix from CC agent output before wrapping with `log_cc*`
- **Scoped Reset**: TDD failure cleanup now only removes story-created untracked files instead of `git clean -fd` which nuked all untracked files
- **REFACTOR Marker Fallback**: `check_tdd_commits` detects conventional `refactor(` prefix when `[REFACTOR]` bracket marker is missing
- **Quality Retry TDD Skip**: Retries after quality failure skip TDD verification (prior RED+GREEN already verified), preventing false rejections
- **Prompt Marker Emphasis**: Added explicit `[REFACTOR]` commit example to retry section of `prompt.md`
- **Error Handling**: Improved error handling when staging state files in Ralph script
- **Type Safety**: Fixed type errors and lint issues for strict type checking
- **Parser Flexibility**: Made Story Breakdown section parsing phase-agnostic
- **Code Formatting**: Applied PEP 8 compliance to generate_prd_json.py
