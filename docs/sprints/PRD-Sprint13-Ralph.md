---
title: Product Requirements Document
version: 1.1
sprint: 13
authority: requirements
---

# Product Requirements Document: Sprint 13 — GUI Audit Remediation & Theming

## Project Overview

Sprint 13 remediates findings from a comprehensive GUI audit of `src/gui/` (Streamlit
app) across three dimensions: design patterns, usability, and WCAG 2.1 AA accessibility.
Additionally, it introduces a theme selection system with three curated themes (two dark,
one light) to improve visual identity, reduce eye strain, and support diverse user
preferences.

Audit sources: parallel agent team review (design-reviewer, usability-reviewer,
accessibility-reviewer) conducted 2026-02-28.

### Pre-Sprint Fixes (already implemented)

The following audit findings were resolved before sprint start as trivial changes:

- Sidebar `label_visibility="collapsed"` → `"hidden"` (a11y fix, `sidebar.py`)
- Prompts page text areas set to `disabled=True` with read-only notice (`prompts.py`, `components/prompts.py`)
- Engine radio label renamed from "MAS (PydanticAI)" to "Multi-Agent System (MAS)" (`run_app.py`)
- `help=` tooltips added to CC Teams checkbox, sub-agent checkboxes, prompt editor (`run_app.py`, `settings.py`, `components/prompts.py`)
- "Advanced Settings" changed from `st.header` to `st.subheader` (`settings.py`)
- Emoji removed from `PAGE_TITLE`, `st.warning()`, `st.subheader()`, sidebar info (`text.py`, `evaluation.py`, `sidebar.py`)
- `st.caption()` added before evaluation bar chart (`evaluation.py`)
- Dead commented-out `match/case` block removed from `output.py`

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features (e.g., "##### 2.1 + 2.2") — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: Fix Broken ARIA Live Regions in Execution Page

**Description**: The ARIA live region tags in `run_app.py` are split across separate
`st.markdown()` calls, creating malformed DOM. Screen readers never announce status
changes during pipeline execution. Consolidate opening/closing ARIA tags into single
`st.markdown()` calls or use `st.empty()` containers.

**Acceptance Criteria**:
- [ ] All `<div role="status" aria-live="polite">` regions are emitted as single `st.markdown()` calls
- [ ] Screen reader announcement works for idle, running, completed, and error states
- [ ] No orphaned opening/closing ARIA tags across separate `st.markdown()` calls

**Technical Requirements**:
- Refactor `_display_execution_result` to build complete ARIA-wrapped HTML strings before emitting
- Use `st.empty()` containers for in-place status updates where appropriate
- Verify DOM structure with browser dev tools after changes

**Files**:
- `src/gui/pages/run_app.py` (edit)

---

#### Feature 2: Add Accessible Alternative for Agent Graph Visualization

**Description**: The Pyvis network graph is injected as raw HTML via `components.html()`
with no title, no ARIA role, no alt text, and no text equivalent. Add an accessible
text summary and fix the keyboard trap risk from `scrolling=False`.

**Acceptance Criteria**:
- [ ] Text summary of graph (node count, edge count, agent names) rendered below the graph
- [ ] `st.caption()` with descriptive text added before `components.html()` call
- [ ] `<title>` element added to generated Pyvis HTML before injection
- [ ] `scrolling=True` set on `components.html()` to prevent keyboard trap
- [ ] Pyvis `bgcolor` reads from theme instead of hard-coded `#ffffff`

**Technical Requirements**:
- Insert `<title>Agent Interaction Graph</title>` into the Pyvis HTML string
- Add `st.caption("Agent interaction graph showing agent and tool relationships. See statistics below for details.")` before the component
- Change `scrolling=False` to `scrolling=True`
- Replace `bgcolor="#ffffff"` with theme-aware value from `styling.py`

**Files**:
- `src/gui/pages/agent_graph.py` (edit)
- `src/gui/config/styling.py` (edit)

---

#### Feature 3: Add Debug Log Panel ARIA Landmark

**Description**: The debug log panel renders raw HTML via `unsafe_allow_html=True`
with no ARIA landmark. Add `role="log"` and `aria-label` to the outermost container.
Fix message span color for theme compatibility.

**Acceptance Criteria**:
- [ ] Debug log container has `role="log"` and `aria-label="Debug logs"`
- [ ] Message span uses `color: inherit` for theme compatibility
- [ ] Inline `font-family: monospace; font-size: 12px` removed (duplicates global theme font)

**Technical Requirements**:
- Modify `LogCapture.format_logs_as_html()` to wrap output in `<section role="log" aria-label="Debug logs">`
- Add `color: inherit` to message `<span>` elements
- Remove redundant inline font declarations

**Files**:
- `src/gui/utils/log_capture.py` (edit)
- `src/gui/pages/run_app.py` (edit)

---

#### Feature 4: Fix Validation Warning Placement on Run Page

**Description**: The validation warning for empty query/paper fires inside the async
handler and disappears on Streamlit rerender. Render the warning adjacent to the Run
button so users see it.

**Acceptance Criteria**:
- [ ] Validation warning renders directly above or adjacent to the Run button
- [ ] Warning persists on screen until user corrects the input
- [ ] Warning is not buried in an async handler that fires after rerender

**Technical Requirements**:
- Move validation check from `_handle_query_submission` to the `render_app()` scope
- Use `st.session_state` to persist the warning state across rerenders
- Render warning with `st.warning()` in the same container as the Run button

**Files**:
- `src/gui/pages/run_app.py` (edit)

---

#### Feature 5: Fix Report Generation Double-Render and Download Persistence

**Description**: Clicking "Generate Report" twice duplicates the rendered markdown.
The Download button recreates on each render with no stable confirmation. Cache the
report in session state.

**Acceptance Criteria**:
- [ ] Generated report cached in `st.session_state` — no duplicate renders on re-click
- [ ] Download button persists after first generation
- [ ] "Clear Results" button resets execution state to idle

**Technical Requirements**:
- Store generated markdown in `st.session_state["generated_report"]`
- Render from cache if report already exists
- Add "Clear Results" button that resets `execution_state` to idle and clears result keys

**Files**:
- `src/gui/pages/run_app.py` (edit)

---

#### Feature 6: Selectable Streamlit Themes (3 themes)

**Description**: Add three curated, selectable Streamlit themes: "Expanse Dark" (current),
"Nord Light" (light, readability-first), and "Tokyo Night" (warm dark, recommended
upgrade). Theme definitions stored in `styling.py`, selectable via sidebar or settings.

**Acceptance Criteria**:
- [ ] Three theme dicts defined in `config/styling.py` with full color specs
- [ ] Theme selector widget in sidebar or settings page
- [ ] Selected theme persists in session state across page navigations
- [ ] Pyvis graph colors update to match selected theme accent colors
- [ ] `.streamlit/config.toml` documents the default theme choice

**Technical Requirements**:
- Define `THEMES` dict in `styling.py` with keys: `expanse_dark`, `nord_light`, `tokyo_night`
- Each theme: `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `accentColor`
- Expanse Dark: `#4A90E2`, `#0b0c10`, `#1f2833`, `#66fcf1`, `#50C878`
- Nord Light: `#5E81AC`, `#ECEFF4`, `#E5E9F0`, `#2E3440`, `#88C0D0`
- Tokyo Night: `#7AA2F7`, `#1A1B26`, `#24283B`, `#C0CAF5`, `#9ECE6A`
- Theme selector writes to `st.session_state["selected_theme"]`
- Agent graph reads node/edge colors from active theme
- Note: Streamlit theme switching at runtime requires `st.set_page_config` workaround or custom CSS injection

**Files**:
- `src/gui/config/styling.py` (edit)
- `src/gui/components/sidebar.py` (edit)
- `src/gui/pages/agent_graph.py` (edit)
- `src/gui/pages/settings.py` (edit)
- `.streamlit/config.toml` (edit)

---

#### Feature 7: Improve Home Page Onboarding

**Description**: Home page has minimal onboarding with no actionable first step.
Add a checklist or step-by-step card guiding new users through setup.

**Acceptance Criteria**:
- [ ] Home page shows a step-by-step onboarding guide (configure provider, download dataset, run query)
- [ ] Each step links or navigates to the relevant page
- [ ] Onboarding content defined in `text.py` (not inline strings)

**Technical Requirements**:
- Add onboarding constants to `text.py` (step titles, descriptions)
- Render as `st.info()` or card-like layout with numbered steps
- Link steps to Settings and Run pages

**Files**:
- `src/gui/pages/home.py` (edit)
- `src/gui/config/text.py` (edit)

---

#### Feature 8: Consolidate UI String Constants in text.py

**Description**: Several pages use inline string literals for headers and labels instead
of importing from `text.py`. Consolidate for single-source-of-truth copy management.

**Acceptance Criteria**:
- [ ] All header/subheader strings in `evaluation.py` moved to `text.py`
- [ ] All header/subheader strings in `agent_graph.py` moved to `text.py`
- [ ] All inline label strings in `run_app.py` ("Debug Log", "Generate Report") moved to `text.py`

**Technical Requirements**:
- Add constants to `text.py`: `EVALUATION_HEADER`, `AGENT_GRAPH_HEADER`, `DEBUG_LOG_LABEL`, `GENERATE_REPORT_LABEL`, etc.
- Import and use in respective pages

**Files**:
- `src/gui/config/text.py` (edit)
- `src/gui/pages/evaluation.py` (edit)
- `src/gui/pages/agent_graph.py` (edit)
- `src/gui/pages/run_app.py` (edit)

---

#### Feature 9: Fix Navigation Consistency and Baseline Expander

**Description**: Sidebar labels don't match page headers. Evaluation baseline expander
hidden by default on first visit. Phoenix Trace Viewer always visible even when not
configured.

**Acceptance Criteria**:
- [ ] Sidebar navigation labels align with page headers
- [ ] Baseline comparison expander expanded by default on first visit (no result available)
- [ ] Phoenix Trace Viewer moved to collapsed sidebar expander

**Technical Requirements**:
- Update `PAGES` list in `config.py` to match page header text
- Set `expanded=True` on baseline comparison expander when no result exists
- Wrap Phoenix link in `st.sidebar.expander("Tracing (optional)")`

**Files**:
- `src/gui/config/config.py` (edit)
- `src/gui/pages/evaluation.py` (edit)
- `src/gui/components/sidebar.py` (edit)

---

#### Feature 10: Fix Pyvis Graph Contrast and Color Theming

**Description**: Agent graph node colors have insufficient contrast for text labels.
Graph background is hard-coded white, conflicting with dark theme. Make graph colors
theme-aware.

**Acceptance Criteria**:
- [ ] Node label `font_color` explicitly set (not Pyvis default)
- [ ] Node colors provide >= 4.5:1 contrast ratio for labels
- [ ] Graph `bgcolor` reads from active theme (not hard-coded `#ffffff`)
- [ ] Agent and tool node colors update when theme changes

**Technical Requirements**:
- Set `font_color="#000000"` for light themes, `font_color="#ECEFF4"` for dark themes
- Read `bgcolor` from theme dict in `styling.py`
- Map agent node color to theme `primaryColor`, tool node color to theme `accentColor`

**Files**:
- `src/gui/pages/agent_graph.py` (edit)
- `src/gui/config/styling.py` (edit)

---

#### Feature 11: Type-Aware Output Rendering

**Description**: `render_output` uses generic `st.write()` for all result types.
Implement type-aware rendering so Pydantic models and dicts render with navigable
structure instead of raw object dumps.

**Acceptance Criteria**:
- [ ] `render_output()` type-checks result and uses structured rendering (e.g., `st.json()` for dicts)
- [ ] `CompositeResult` and other Pydantic models render with navigable structure

**Technical Requirements**:
- Add type dispatch: `st.json()` for dicts, `st.markdown()` for strings, structured rendering for Pydantic models
- Import relevant result types from `src/app/data_models/`

**Files**:
- `src/gui/components/output.py` (edit)

---

## Non-Functional Requirements

- All color combinations must pass WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Theme switching must not require app restart — session-state-driven
- No new Python dependencies — use only Streamlit built-in capabilities
- All user-visible strings must live in `src/gui/config/text.py` (single source of truth)
- Debug log panel must function correctly in all three themes

## Out of Scope

- **Custom CSS injection beyond Streamlit theming** — Streamlit's theme system is sufficient for Sprint 13
- **Automated accessibility testing in CI** (axe-core, pa11y) — deferred to Sprint 14+
- **Responsive/mobile layout optimization** — Streamlit's responsive behavior is acceptable for desktop-first tool
- **Internationalization (i18n)** — text.py consolidation enables future i18n but translation is out of scope
- **Phoenix availability detection** — checking if Phoenix is running on startup is a nice-to-have deferred to Sprint 14
- **Prompt editing with save** — Sprint 13 makes prompts read-only; full CRUD editing deferred to Sprint 14+
- **Sub-agent default enablement** — changing checkbox defaults requires UX research on user expectations

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (11 stories total):

- **Feature 1** → STORY-001: Fix broken ARIA live regions in run_app.py
  Consolidate split `st.markdown()` ARIA tags into single calls. Refactor `_display_execution_result` to build complete ARIA-wrapped HTML. Files: `src/gui/pages/run_app.py`.

- **Feature 2** → STORY-002: Add accessible alternative for agent graph
  Add `<title>` to Pyvis HTML, `st.caption()` before graph, text summary below, `scrolling=True`. Files: `src/gui/pages/agent_graph.py`.

- **Feature 3** → STORY-003: Add debug log panel ARIA landmark
  Add `role="log"` and `aria-label` to log container HTML. Fix message span color. Remove redundant inline font. Files: `src/gui/utils/log_capture.py`, `src/gui/pages/run_app.py`.

- **Feature 4** → STORY-004: Fix validation warning placement on Run page
  Move validation from async handler to `render_app()` scope. Persist warning in session state. Files: `src/gui/pages/run_app.py`.

- **Feature 5** → STORY-005: Fix report generation and add clear results (depends: STORY-004)
  Cache generated report in session state. Add "Clear Results" button. Files: `src/gui/pages/run_app.py`.

- **Feature 6** → STORY-006: Define theme dicts in styling.py
  Create `THEMES` dict with three themes (Expanse Dark, Nord Light, Tokyo Night). Full hex color specs. Files: `src/gui/config/styling.py`.

- **Feature 6** → STORY-007: Add theme selector widget (depends: STORY-006)
  Add theme selector to sidebar or settings. Persist in session state. Files: `src/gui/components/sidebar.py`, `src/gui/pages/settings.py`, `.streamlit/config.toml`.

- **Feature 7** → STORY-008: Improve home page onboarding
  Add step-by-step onboarding guide with setup checklist. Define content in text.py. Files: `src/gui/pages/home.py`, `src/gui/config/text.py`.

- **Feature 8** → STORY-009: Consolidate UI string constants in text.py
  Move inline header/label strings from evaluation.py, agent_graph.py, run_app.py to text.py. Files: `src/gui/config/text.py`, `src/gui/pages/evaluation.py`, `src/gui/pages/agent_graph.py`, `src/gui/pages/run_app.py`.

- **Feature 9** → STORY-010: Fix navigation consistency and baseline expander (depends: STORY-009)
  Align sidebar labels with page headers. Expand baseline expander on first visit. Move Phoenix link to collapsed expander. Files: `src/gui/config/config.py`, `src/gui/pages/evaluation.py`, `src/gui/components/sidebar.py`.

- **Feature 10** → STORY-011: Fix Pyvis graph contrast and color theming (depends: STORY-006)
  Set explicit font_color. Read bgcolor from theme. Map node colors to theme palette. Files: `src/gui/pages/agent_graph.py`, `src/gui/config/styling.py`.

- **Feature 11** → STORY-012: Type-aware output rendering
  Add type dispatch for structured rendering of dicts, strings, and Pydantic models. Files: `src/gui/components/output.py`.

### Notes for CC Agent Teams

#### File-Conflict Dependencies

| Story | Logical Dep | + File-Conflict Dep | Shared File |
|---|---|---|---|
| STORY-005 | STORY-004 | — | `src/gui/pages/run_app.py` |
| STORY-007 | STORY-006 | — | `src/gui/components/sidebar.py` |
| STORY-010 | STORY-009 | — | `src/gui/pages/evaluation.py` |
| STORY-011 | STORY-006 | + STORY-002 | `src/gui/pages/agent_graph.py` |

#### Orchestration Waves

```text
Wave 1 (independent):  STORY-001, STORY-002, STORY-003, STORY-004, STORY-006, STORY-008, STORY-012
Wave 2 (after Wave 1): STORY-005, STORY-007, STORY-009
Wave 3 (after Wave 2): STORY-010, STORY-011
```
