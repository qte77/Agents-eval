---
title: GUI Comprehensive Audit — Actionable Fixes
description: 28 actionable UX, accessibility, and design fixes for the Streamlit GUI, mapped to Sprint 8 PRD features.
scope: src/gui/ + src/run_gui.py
sprint: 8
prd_features: F3 polish, F4 polish, F7 polish, F8 standalone
created: 2026-02-18
updated: 2026-02-18
---

# GUI Audit — Actionable Fixes

Items are assigned to PRD features based on file ownership. Items touching files already owned by Features 3, 4, or 7 are folded into those features as GUI polish sub-sections. The rest are Feature 8 standalone.

---

## Critical (blocks basic usability)

| # | What to do | Where | PRD Owner |
|---|-----------|-------|-----------|
| 1 | Change `HOME_INFO` to: "Configure your provider in Settings, then run evaluations from the App page." | `text.py:1` | **F8.1** |
| 2 | Add `st.warning("Prompt edits are preview-only and are not applied to agent runs.")` at top of page, set `disabled=True` on text areas | `prompts.py:27,46` | **F8.1** |
| 3 | Replace "Use the Downloads page" with `"No papers found. Download with: make setup_dataset_sample"` | `run_app.py:381` | **F3 polish** |
| 4 | Delete the CSS block (lines 12-20). Keep only `set_page_config()` | `styling.py:12-20` | **F8.1** |
| 5 | Change `sidebar.radio(" ", PAGES)` to `sidebar.radio("Navigation", PAGES, label_visibility="collapsed")` | `sidebar.py:16` | **F8.1** |
| 6 | Move `subheader(OUTPUT_SUBHEADER)` after the `button()` call | `run_app.py:519-521` | **F8.2** |
| 7 | After completed state, add `st.info("View structured results on the Evaluation Results and Agent Graph pages.")`. Note: app uses sidebar radio routing (not `st.navigation`), so `st.page_link()` won't work — use text guidance or `st.button` + session state + `st.rerun()` | `run_app.py:352` | **F3 polish** |
| 8 | Change defaults to `"include_researcher": True, "include_analyst": True` | `run_gui.py:63-64` | **F8.1** |

## High (significantly improves experience)

| # | What to do | Where | PRD Owner |
|---|-----------|-------|-----------|
| 9 | Create `.streamlit/config.toml` with `primaryColor="#4A90E2"` | `.streamlit/config.toml` (new) | **F8.1** |
| 10 | Set `expanded=False` on judge/tier/scoring expanders. Add "Advanced Settings" divider | `settings.py:90,131,171,215` | **F7 polish** |
| 11 | Show `sidebar.caption("Evaluation running...")` when execution in progress | `sidebar.py:17` | **F3 polish** |
| 12 | Map metric keys to human-readable labels (`cosine_score` → `"Text Similarity (Cosine)"` etc.) | `evaluation.py:136-142` | **F3 polish** |
| 13 | Add `st.caption("Blue = Agent · Green = Tool · Scroll to zoom · Drag to pan · Hover for details")` | `agent_graph.py:139` | **F4 polish** |
| 14 | Add `help="MAS: multi-agent PydanticAI pipeline. Claude Code: delegates to Claude CLI."` to engine radio | `run_app.py:481` | **F3 polish** |
| 15 | Change `RUN_APP_QUERY_PLACEHOLDER` to `"e.g., Evaluate this paper's methodology and novelty"` | `text.py:16` | **F8.1** |
| 16 | When `engine == "cc"`, hide MAS controls entirely (not just disabled + info banner) | `run_app.py:496-504` | **F8.2** |
| 17 | Wrap baseline comparison in `st.expander("Baseline Comparison (Advanced)", expanded=False)` | `evaluation.py:249-259` | **F3 polish** |
| 18 | Color-code recommendation. `st.metric(delta_color=)` only colors the delta, not the value — replace the recommendation `st.metric` with `st.markdown(f'... style="color: green/red" ...', unsafe_allow_html=True)`, or keep `st.metric` and add a colored `st.caption()` below it | `evaluation.py:61` | **F3 polish** |

## Medium (polish and delight)

| # | What to do | Where | PRD Owner |
|---|-----------|-------|-----------|
| 19 | Rewrite Home page: config status, dataset status, last run summary, action buttons | `home.py`, `text.py` | **F8.1** |
| 20 | Execution state a11y: use `st.status(label=..., state="running"/"complete"/"error")` (Streamlit-native, has built-in a11y) instead of raw ARIA divs. Can't wrap Streamlit widgets in custom `<div role="status">` — Streamlit renders components independently. Fallback: hidden `st.markdown('<p role="status" aria-live="polite">...</p>', unsafe_allow_html=True)` | `run_app.py:343-361` | **F3 polish** |
| 21 | Pyvis a11y: inject wrapper into HTML string before `components.html()`: `html_content = f'<div role="region" aria-label="Agent Interaction Graph">{html_content}</div>'`. Add edge list text summary in Graph Statistics expander (standard `st.text`) | `agent_graph.py:139-154` | **F4 polish** |
| 22 | Populate `delta` on `st.metric()` for tier scores when baseline exists | `evaluation.py:80-104` | **F3 polish** |
| 23 | `render_output()`: render CompositeResult as summary card, not raw dump. Also rename `type` parameter to `output_type` — shadows Python built-in (`output.py:6`) | `output.py:6,21-23` | **F8.2** |
| 24 | Replace hardcoded `bgcolor="#ffffff"` with `"transparent"` | `agent_graph.py:57` | **F4 polish** |
| 25 | Change log module text color `#999999` → `#696969` (WCAG contrast fix) | `log_capture.py:131` | **F8.1** |
| 26 | Add "(opens in new tab)" to Phoenix Traces link | `sidebar.py:22` | **F8.1** |
| 27 | Add `help=` to paper selectbox | `run_app.py:384` | **F3 polish** |
| 28 | Add `st.dataframe()` below bar chart as text alternative | `evaluation.py:130` | **F3 polish** |

## Deferred (future sprint)

| # | What | Why deferred |
|---|------|-------------|
| 29 | Guided workflow step indicator across pages | New component, design needed |
| 30 | Demo/sample data for empty states | Requires synthetic CompositeResult |
| 31 | Run history (past evaluations list) | New state management |
| 32 | Export evaluation as JSON/Markdown | Feature scope beyond audit |
| 33 | Pre-flight validation (API key check before run) | Needs env var detection per provider |
| 34 | Settings persistence to disk | Requires file I/O + migration logic |

---

## PRD Feature Index

| Feature | Audit items | Shared files |
|---------|-------------|-------------|
| **F3 polish** (CC engine — `run_app.py`, `evaluation.py`, `sidebar.py`) | #3, #7, #11, #12, #14, #17, #18, #20, #22, #27, #28 | `run_app.py`, `evaluation.py`, `sidebar.py` |
| **F4 polish** (graph alignment — `agent_graph.py`) | #13, #21, #24 | `agent_graph.py` |
| **F7 polish** (judge dropdowns — `settings.py`) | #10 | `settings.py` |
| **F8 standalone** (dedicated GUI files) | #1, #2, #4, #5, #6, #8, #9, #15, #16, #19, #23, #25, #26 | `styling.py`, `sidebar.py`, `text.py`, `prompts.py`, `home.py`, `run_gui.py`, `output.py`, `log_capture.py`, `.streamlit/config.toml` |

## Files touched (summary)

| File | Items |
|------|-------|
| `text.py` | #1, #15, #19 |
| `prompts.py` | #2 |
| `run_app.py` | #3, #6, #7, #14, #16, #20, #27 |
| `styling.py` | #4 |
| `sidebar.py` | #5, #11, #26 |
| `run_gui.py` | #8 |
| `.streamlit/config.toml` | #9 (new) |
| `settings.py` | #10 |
| `evaluation.py` | #12, #17, #18, #22, #28 |
| `agent_graph.py` | #13, #21, #24 |
| `output.py` | #23 |
| `log_capture.py` | #25 |
| `home.py` | #19 |

## See also (PRD-originated, not from this audit)

PRD Feature 8 includes additional items that were added directly to the PRD, not sourced from this audit:

- **F8.3** — Run ID threading (`execution_id` stored in session state, displayed on Evaluation page) + baseline path validation with `Path.is_dir()` check
- **F8.4** — Environment-aware service URL resolution (`resolve_service_url()` for Codespaces/Gitpod/localhost)
- **F8.5** — TDD tests for the above
