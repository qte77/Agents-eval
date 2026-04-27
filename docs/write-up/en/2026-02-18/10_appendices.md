# Appendices {.unnumbered}

## Appendix A: ADR Summary

The following architectural decisions were documented and justified during system development. Each ADR describes the decision context, alternatives considered, and the choice made.

| ADR | Title | Decision | Status |
|-----|-------|----------|--------|
| ADR-001 | PydanticAI as Agent Framework | PydanticAI for multi-agent orchestration | Active |
| ADR-002 | PeerRead Dataset Integration | PeerRead as primary evaluation benchmark | Active |
| ADR-003 | Three-Tier Evaluation Framework | Traditional Metrics $\rightarrow$ LLM-as-a-Judge $\rightarrow$ Graph Analysis | Active |
| ADR-004 | Post-Execution Graph Analysis | Retrospective trace processing instead of real-time monitoring | Active |
| ADR-005 | Plugin-Based Evaluation Architecture | EvaluatorPlugin interface with PluginRegistry | Active |
| ADR-006 | pydantic-settings Migration | BaseSettings classes instead of JSON configuration files | Active |
| ADR-007 | Optional Container-Based Deployment | Local execution as default, containers optional | Proposed (deferred) |
| ADR-008 | CC Baseline Engine: subprocess vs. SDK | subprocess.run for Sprint 7; evaluate SDK migration for Sprint 8 | Active |

## Appendix B: System Requirements

### Minimum System Requirements

- **Python**: 3.13 or higher (exactly 3.13.x required)
- **RAM**: 4 GB (8 GB recommended)
- **CPU**: 2 cores (4 cores recommended)
- **Storage**: 10 GB available disk space
- **Network**: Internet connection for LLM provider APIs

### Development Environment

- **uv**: Package manager for dependency management and virtual environments
- **Ruff**: Code formatting and linting
- **Pyright**: Static type analysis (mode: strict)
- **Pytest**: Test framework with asyncio support
- **MkDocs**: Documentation generation

### Core Production Dependencies (from pyproject.toml)

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic-ai-slim | >=1.59.0 | Multi-agent orchestration |
| pydantic | >=2.12.5 | Data validation and data models |
| pydantic-settings | >=2.12.0 | Type-safe configuration via environment variables |
| logfire | >=4.24.0 | Structured logging and observability |
| networkx | >=3.6.1 | Graph-based behavioral analysis (Tier 3) |
| arize-phoenix | >=13.0.0 | Local trace viewer for observability |
| scikit-learn | >=1.8.0 | Text similarity metrics (Tier 1) |
| streamlit | >=1.54.0 | Graphical user interface |
| openinference-instrumentation-pydantic-ai | >=0.1.12 | PydanticAI auto-instrumentation |

## Appendix C: Supported LLM Providers

The framework supports a variety of LLM providers through PydanticAI's OpenAI-compatible interfaces. Providers are configured via CLI arguments (`--chat-provider`, `--judge-provider`) or environment variables.

| Provider | Type | Characteristics |
|----------|------|-----------------|
| OpenAI | Cloud | GPT-4o and further models; default reference provider |
| Google Gemini | Cloud | Multimodal capabilities; large context window |
| Anthropic | Cloud | Claude models; balanced evaluation quality |
| Ollama | Local | Privacy-focused implementations without API costs |
| OpenRouter | Cloud gateway | Aggregator for multiple providers |
| Together AI | Cloud | Batch inference and open-source models |
| HuggingFace | Cloud/Local | Access to open-source models |
| Cerebras | Cloud | Hardware-accelerated inference |
| Groq | Cloud | High-speed LPU inference |
| XAI | Cloud | Grok model family |

## Appendix D: Documentation Hierarchy

The project follows a structured documentation hierarchy that prevents scope creep and defines clear authoritative sources. Each document has a specific scope and serves as the single source of truth for its domain.

The complete hierarchy is described in [AGENTS.md](../../../../AGENTS.md). The following figure illustrates the reference structure and authority chain:

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/documentation-hierarchy-light.png}
\caption{Documentation hierarchy}
\end{figure}

**Authority Chain (Reference Flow):**

```text
PRD.md (Requirements) $\rightarrow$ architecture.md (Technical Design)
  $\rightarrow$ Sprint Documents (Implementation) $\rightarrow$ Usage Guides (Operations)
        ↑
Landscape Documents (inform strategic decisions, do not create requirements)
```
