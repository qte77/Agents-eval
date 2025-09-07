# PRD-Driven Subagent Coordination

**Authority**: Follow PRD.md (requirements) → architecture.md (technical) → UserStory.md (acceptance criteria) hierarchy

## Pipeline-Centric Development Strategy

**Foundation**: Extend existing `evaluation_pipeline.py:411-519` which already implements ALL mandatory requirements:

- ✅ Traditional + Advanced metrics (PRD.md:148-153)  
- ✅ Three-tier evaluation system (architecture.md:75-155)
- ✅ Comprehensive monitoring (UserStory.md:64-68)

## Single-Branch Enhancement Approach

### **Branch: feat/pipeline-enhancements**

**Location**: `/workspaces/Agents-eval-pipeline`
**Subagent**: `python-developer` → `code-reviewer`  
**Focus**: Enhance existing pipeline with missing PRD requirements

**Core Tasks (PRD.md Mandatory)**:

1. **Replace Custom Metrics with Third-Party Packages**:
   - **Replace** custom cosine similarity (`traditional_metrics.py:64-111`) with **ROUGE-Score package**
   - **Replace** custom Jaccard implementation (`traditional_metrics.py:113-169`) with **NLTK metrics**
   - **Replace** custom semantic similarity (`traditional_metrics.py:212-231`) with **sentence-transformers** or **BERTScore**
   - **Use** existing `textdistance>=4.6.3` library instead of custom Levenshtein
   - **Delete** custom implementations, **import** third-party functions only
   - Update `pyproject.toml` dependencies: `nltk>=3.8`, `rouge-score>=0.1.13`, `sentence-transformers>=3.0.0`

2. **Streamlit Dashboard Integration** (PRD.md:36-42):
   - Connect existing pipeline to Streamlit GUI
   - Display `evaluation_pipeline.py:504-518` execution stats
   - Show composite scores from `composite_scorer.py:210`
   - Real-time monitoring interface

3. **Metrics Sweep Engine** (PRD requirement via metrics-eval-sweep.plantuml):
   - Create `MetricsSweepEngine` extending `evaluation_pipeline.py:411`
   - Implement batch evaluation with configuration matrix
   - Agent configuration variations (single/multi-agent)
   - Results comparison and analysis

4. **Opik Implementation** (PRD.md:157 + architecture.md monitoring):
   - Complete Opik local deployment setup
   - Enhance existing `opik_instrumentation.py:61-93` agent tracking  
   - ClickHouse analytics integration for performance trends
   - Graph metrics export for Tier 3 analysis

**Files to modify**:

- `src/app/evals/traditional_metrics.py` (**REPLACE custom implementations with third-party imports**)
- `src/app/evals/metrics_sweep_engine.py` (new, extends pipeline)  
- `src/app/agents/opik_instrumentation.py` (complete implementation)
- `src/gui/pages/run_app.py` (connect to pipeline)
- `docker-compose.opik.yml` (new, official Opik deployment)
- `pyproject.toml` (add `nltk>=3.8`, `rouge-score>=0.1.13`, `sentence-transformers>=3.0.0`)

## **Opik Implementation Requirements**

### **1. Local Opik Deployment** (Official Setup)

**Reference**: <https://www.comet.com/docs/opik/self-host/local_deployment/>

```bash
# Create official Opik Docker Compose
./scripts/worktrees/setup-opik.sh
```

**Files to create**:

- `docker-compose.opik.yml` - Official Opik + ClickHouse + Redis stack
- `scripts/worktrees/setup-opik.sh` - Automated deployment script
- `.env.opik` - Environment variables for local deployment

**Services**:

- **Opik Frontend**: <http://localhost:5173>
- **Opik API**: <http://localhost:3003>
- **ClickHouse**: <http://localhost:8123> (analytics database)
- **Redis**: localhost:6379 (caching layer)

### **2. Enhanced Agent Instrumentation**

Extend existing `opik_instrumentation.py:61-93`:

```python
# Enhanced agent tracking with step-level spans
@opik_manager.track_agent_execution("Manager", "orchestration", "paper_review")
async def process_paper_review(self, paper: str) -> str:
    # Automatic span creation for each agent interaction
    pass
```

### **3. ClickHouse Analytics Integration**

**Analytical Queries for Performance Trends**:

- Agent execution time analysis by role (Manager/Researcher/Analyst/Synthesizer)
- Tool usage effectiveness measurements across evaluation runs  
- Multi-agent coordination patterns and delegation success rates
- Graph complexity metrics correlation with composite scores

### **4. Graph Metrics Export**

Integration with `graph_analysis.py:23-82`:

- Export NetworkX metrics to ClickHouse for time-series analysis
- Agent interaction graphs stored as JSON in Opik traces
- Performance correlation between graph complexity and evaluation scores

## **Coordination Commands**

### **Setup Single Pipeline Enhancement**

```bash
# Create single enhancement worktree
cd /workspaces/Agents-eval
git worktree add --track -b feat/pipeline-enhancements ../Agents-eval-pipeline feat-evals

# Start development  
cd /workspaces/Agents-eval-pipeline
claude --print 'Task("Replace ALL custom metric implementations in traditional_metrics.py with third-party packages (ROUGE-Score, NLTK, sentence-transformers), complete Opik implementation, add metrics sweep engine, and connect Streamlit dashboard - following PRD.md mandatory requirements", subagent_type="python-developer")'
```

### **Validation Commands**

```bash
# Validate against existing pipeline
make validate

# Test integration with existing evaluation system  
uv run pytest tests/evals/test_evaluation_pipeline.py -v

# Verify Opik tracing
uv run pytest tests/integration/test_opik_integration.py -v

# Test complete system
./scripts/worktrees/integration-workflow.sh test-specific pipeline-enhancements
```

## **PRD-Driven Development Workflow**

### **Phase 1: Requirements Validation**

- ✅ Verify all PRD.md mandatory features covered by existing pipeline
- ✅ Identify only missing third-party integrations (NLTK, ROUGE, Opik)
- ✅ Confirm UserStory.md acceptance criteria alignment

### **Phase 2: Enhancement Implementation**  

- Extend existing `evaluation_pipeline.py` (not replace)
- Complete `opik_instrumentation.py` implementation
- **REPLACE custom metric implementations with third-party package imports** in `traditional_metrics.py`
- Create `MetricsSweepEngine` extending pipeline
- Connect Streamlit GUI to pipeline results

**Critical**: Do NOT implement metrics manually - use established packages:

- `from rouge_score import rouge_scorer` (replace custom cosine)
- `from nltk.translate.bleu_score import sentence_bleu` (replace custom similarity)  
- `from sentence_transformers import SentenceTransformer` (replace custom semantic)
- `import textdistance` (already available, replace custom Levenshtein)

### **Phase 3: Integration Testing**

- Validate enhanced pipeline maintains existing functionality
- Test Opik tracing with real evaluation runs
- Verify Streamlit dashboard displays pipeline results
- Confirm metrics sweep produces comparative analysis

### **Phase 4: Production Deployment**

- Deploy local Opik stack with ClickHouse analytics
- Update documentation for new capabilities
- Merge enhancements to feat-evals branch
  