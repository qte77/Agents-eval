# Changelog

All notable changes to Ralph Loop will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- **Agent Activity Monitor**: Heartbeat now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors (`common.sh`: `log_cc`, `log_cc_error`)
- **Quality Retry Context**: Failed quality gate name is passed to the agent prompt on retry via `RETRY_CONTEXT_FILE`, so the agent knows what to fix
- **PRD Parser**: Parser for structured PRD.md files with automatic prd.json generation
- **TDD Workflow**: Optional REFACTOR phase with RED/GREEN/REFACTOR commit markers and chronological verification
- **Template System**: Comprehensive templates for progress.txt and prd.json with parser-compatible structure
- **Documentation**: README.md with Ralph Loop overview, extended functionality guide, and usage examples
- **Project Templates**: Interactive setup script with auto-detection of git repo, author, and Python version

### Changed

- **Documentation Structure**: Reorganized ralph/ directory structure and moved TEMPLATE_USAGE.md to ralph root
- **Skill System**: Relocated commands to skills structure (`.claude/skills/`)
- **Default Configuration**: Increased max iterations to 25, set REQUIRE_REFACTOR to false by default
- **State Files**: Consolidated Ralph script utilities and simplified story processing
- **PRD Format**: Updated to v3.0 with A2A protocol and AgentBeats competition details

### Fixed

- **Scoped Reset**: TDD failure cleanup now only removes story-created untracked files instead of `git clean -fd` which nuked all untracked files
- **REFACTOR Marker Fallback**: `check_tdd_commits` detects conventional `refactor(` prefix when `[REFACTOR]` bracket marker is missing
- **Quality Retry TDD Skip**: Retries after quality failure skip TDD verification (prior RED+GREEN already verified), preventing false rejections
- **Prompt Marker Emphasis**: Added explicit `[REFACTOR]` commit example to retry section of `prompt.md`
- **Error Handling**: Improved error handling when staging state files in Ralph script
- **Type Safety**: Fixed type errors and lint issues for strict type checking
- **Parser Flexibility**: Made Story Breakdown section parsing phase-agnostic
- **Code Formatting**: Applied PEP 8 compliance to generate_prd_json.py
