# Research Paper Plan Template

Plan template for **academic research papers and technical writeups** following the
standard scientific structure: Introduction, Literature Review, Methods, Results,
Discussion, Conclusion — with appendices and bibliography.

Use this template when planning a document that presents original or exploratory
research, empirical evaluation, or technical system design in a formal writeup format.
Not intended for blog posts, READMEs, or operational documentation.

Fill in `{{PLACEHOLDERS}}` with project-specific content before execution.

---

## Context

{{CONTEXT_SUMMARY}}
<!-- 3-5 sentences: What exists, what changed, why a new/updated writeup is needed.
     Include version, sprint/iteration count, key new data or features. -->

{{PRIOR_WRITEUP}}
<!-- Reference any prior writeup being updated, or "None (new writeup)". -->

{{PRIMARY_TECHNICAL_REFERENCE}}
<!-- The authoritative technical document to draw from (e.g., architecture.md).
     The writeup references this rather than re-deriving architecture details. -->

**Critical framing**: {{FRAMING}}
<!-- How to position the work: exploratory proof-of-concept, production system,
     research contribution, etc. State what the writeup claims and what it does NOT claim. -->

---

## File Structure

```text
docs/write-up/{{TOPIC}}/
├── 00_frontmatter.md           # YAML frontmatter (title, bibliography, CSL)
├── 01_introduction.md          # Problem, motivation, scope, timeline, usage
├── 02_literature_review.md     # Research landscape, frameworks, state-of-art
├── 03_methods.md               # Architecture, software, measures, parameters
├── 04_results.md               # Empirical data, comparisons, validation
├── 05_discussion.md            # Interpretation, difficulties, innovations
├── 06_conclusion.md            # Summary, limitations, future work
├── 07_appendices.md            # Reference tables, abbreviations, history
├── 09a_bibliography.bib        # BibTeX references
└── blog-post.md                # Standalone blog summary
```

---

## Chapter Content Plan

### `00_frontmatter.md` --- Pandoc YAML

- **Title**: {{TITLE}}
- **Subtitle**: {{SUBTITLE}}
- **Version**: {{VERSION}}
- **Abstract** (~200 words): {{ABSTRACT_GUIDANCE}}
  <!-- Summarize: what was built, key results (with caveats), scope boundaries. -->
- **Repository URL**: {{REPO_URL}}

### `01_introduction.md` --- Introduction

**Sections:** Motivation and Problem Statement | Research Questions | Project Scope | Development Timeline | Using the Application

- **Problem**: {{PROBLEM_STATEMENT}}
  <!-- What gap does this work address? What existing approaches fall short? -->
- **Framing**: {{EXPLORATORY_VS_DEFINITIVE}}
  <!-- Explicitly state scope boundaries: what was explored, what was not. -->
- **Research questions**:
  1. {{RQ1}}
  2. {{RQ2}}
  3. {{RQ3}}
- **Timeline**: {{SPRINT_OR_ITERATION_TABLE}}
  <!-- All iterations with status and one-line focus. -->
- **Using the Application**: CLI and GUI entry points with screenshots.
- **Images**: {{INTRO_IMAGES}}

### `02_literature_review.md` --- Literature and Landscape Review

**Sections:** {{LIT_REVIEW_SECTIONS}}
<!-- Typical: Frameworks | Evaluation Platforms | Standards | Vulnerabilities | Related Work | Positioning -->

**Sources**: {{LIT_REVIEW_SOURCES}}
<!-- Research documents, landscape analyses, paper collections. -->

- For each section: key references with specific metrics/findings
- **Positioning**: How this work differs from existing approaches
- **Images**: {{LIT_REVIEW_IMAGES}}

### `03_methods.md` --- Methods

**Sections:** {{METHODS_SECTIONS}}
<!-- Typical: Architecture | System Design | Software Stack | Measures and Metrics |
     Variables and Parameters | Benchmarking | Security | Observability -->

- Reference {{PRIMARY_TECHNICAL_REFERENCE}} as the detailed spec --- don't duplicate.
- **Architecture**: Core design with tier/layer breakdown
- **Software stack** (table): Key dependencies, versions, purposes
- **Measures**: All metrics with formulae and scoring logic
- **Security**: Framework, test counts, specific protections
- **Observability**: Tracing, persistence, dual-channel considerations
- **Images**: {{METHODS_IMAGES}}

### `04_results.md` --- Results

**Sections:** Data Inventory | Latest Runs | Historical Analysis | Comparative Analysis | Pipeline Validation

Present data factually, minimal interpretation (save for Discussion).

- **Results table**: {{RESULTS_TABLE}}
  <!-- All real runs with engine, config, scores, duration. -->
- **Excluded data**: Synthetic fixtures, incomplete runs --- explain why.
- **Historical**: Trace analysis summaries.
- **Correction notes**: Any data invalidated by bug fixes.
- **Images**: {{RESULTS_IMAGES}}

### `05_discussion.md` --- Discussion

**Sections:** Interpretation of Results | Difficulties and Solutions | What Is New and Innovative | Enhancements to Existing | Threats to Validity

- **Interpretation**: Each key finding with caveats (sample size, domain limits).
- **Difficulties and solutions**: {{DIFFICULTY_COUNT}} narratives --- each as
  problem → root cause → solution → lesson learned.
  <!-- Source from AGENT_LEARNINGS.md, CHANGELOG.md, sprint retrospectives. -->
- **Innovations**: What is genuinely new in this version.
- **Enhancements**: Improvements to pre-existing capabilities.
- **Threats to validity**: Sample size, domain scope, corrections, unexplored dimensions.
  Restate framing: {{VALIDITY_FRAMING}}

### `06_conclusion.md` --- Conclusion

**Sections:** Summary | Limitations | What Was Not Explored | Future Work

- **Summary**: Sprint count, version, key demonstration. Frame as {{FRAMING}}.
- **Limitations**: Exact sample sizes, domain constraints, known metric weaknesses.
- **Not explored**: Dimensions identified but not pursued --- each is a future direction.
- **Future work**: Each limitation maps to a concrete next step.

### `07_appendices.md` --- Appendices

- **A**: {{APPENDIX_A}} <!-- e.g., Architecture Decision Records -->
- **B**: {{APPENDIX_B}} <!-- e.g., System Requirements -->
- **C**: {{APPENDIX_C}} <!-- e.g., Provider/Configuration Tables -->
- **D**: {{APPENDIX_D}} <!-- e.g., Sprint/Iteration History -->
- **E**: {{APPENDIX_E}} <!-- e.g., Abbreviations -->
- **F**: {{APPENDIX_F}} <!-- e.g., Documentation Hierarchy -->

### `09a_bibliography.bib`

{{BIBLIOGRAPHY_SOURCE}}
<!-- Starting point (existing .bib to copy) + list of new entries to add. -->

### `blog-post.md`

Standalone blog summary extracted after all chapters are written.
Covers: problem, approach, key results, architecture highlights, links.

---

## Screenshot Assignments

All screenshots from `{{SCREENSHOT_DIR}}`.
Relative path from writeup dir: `{{SCREENSHOT_RELATIVE_PATH}}`

| Screenshot | Chapter | Shows |
|------------|---------|-------|
| {{SCREENSHOT_ROWS}} |

## Architecture Diagram Assignments

All images from `{{IMAGE_DIR}}`.
Relative path from writeup dir: `{{IMAGE_RELATIVE_PATH}}`

| Image | Chapter | Purpose |
|-------|---------|---------|
| {{IMAGE_ROWS}} |

---

## Execution Sequence

1. **Invoke skill**: `/generating-writeup {{TOPIC}} {{CITATION_STYLE}}`
2. **Copy bibliography**: Start from {{BIBLIOGRAPHY_SOURCE}}, add new entries
3. **Write frontmatter** (`00_frontmatter.md`): YAML block with pandoc settings
4. **Write chapters in order**: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07
5. **Write blog-post.md**: Extract key points after all chapters
6. **Validate**: `make lint_md INPUT_FILES="docs/write-up/{{TOPIC}}/*.md"`
7. **Citation check**: Verify all `[@key]` references exist in `.bib`
8. **Build PDF**: `make pandoc_run` with appropriate variables

---

## Key Source Files

| File | Used For |
|------|----------|
| {{PRIMARY_TECHNICAL_REFERENCE}} | **Primary technical reference** --- draw from, don't duplicate |
| {{SOURCE_FILE_ROWS}} |

---

## Tone Guidelines

- **Realistic and understated**: Report exact sample sizes, acknowledge limitations upfront
- **Difficulties as learning**: Frame obstacles as revealing insights
- **Innovations without hype**: State what was built and why, let the reader judge
- **Data-driven**: Every claim backed by specific run data or citation
- **Framing consistency**: {{TONE_FRAMING}}
  <!-- e.g., "proof-of-concept", "production-ready", "research contribution" -->
- Reference {{PRIMARY_TECHNICAL_REFERENCE}} for detailed specifications rather than re-deriving
