---
title: AI Security & Governance Frameworks Analysis
source: OWASP MAESTRO v1.0, MITRE ATLAS, NIST AI 100-1, ISO/IEC 42001:2023, ISO/IEC 23894:2023
purpose: >-
  Comparative analysis of four AI security and governance frameworks and their
  applicability to the Agents-eval multi-agent evaluation system. Covers threat
  modeling (MAESTRO, ATLAS), risk management (NIST AI RMF), and AI governance
  standards (ISO 42001/23894) with unified cross-framework mapping.
created: 2026-03-01
updated: 2026-03-01
---

Analysis of four frameworks applicable to the Agents-eval multi-agent evaluation
system (PydanticAI-based MAS evaluating academic papers via LLM providers).

**Category**: Research / Informational
**Authority**: [security-advisories.md](../security-advisories.md) for CVE status;
[mas-security.md](../best-practices/mas-security.md) for MAESTRO implementation
**Created**: 2026-03-01

## Framework Overview

| Framework | Type | Certifiable | Focus | MAS Relevance |
| --- | --- | --- | --- | --- |
| OWASP MAESTRO | Threat model | No | Multi-agent system threats (7 layers) | Direct — designed for MAS |
| MITRE ATLAS | Attack taxonomy | No | Adversarial tactics/techniques for AI/ML | High — maps attacker TTPs |
| NIST AI RMF 1.0 | Risk framework | No (voluntary) | AI lifecycle risk management | Medium — governance structure |
| ISO 42001 / 23894 | Standards | Yes (42001) | AI management system / AI risk guidance | Medium — certification path |

## 1. OWASP MAESTRO

**Source**: [OWASP MAESTRO v1.0](https://genai.owasp.org/resource/multi-agentic-system-threat-modeling-guide-v1-0/)
**Existing coverage**: Comprehensive — see [mas-security.md](../best-practices/mas-security.md)

### 7-Layer Threat Model

| Layer | Focus | Key Concern |
| --- | --- | --- |
| 1. Model | LLM security | Prompt injection, data leakage |
| 2. Agent Logic | Agent behavior | Input validation, type safety |
| 3. Integration | External services | Service failures, API key exposure |
| 4. Monitoring | Observability | Log injection, sensitive data in traces |
| 5. Execution | Runtime safety | Resource exhaustion, race conditions |
| 6. Environment | Infrastructure | Container isolation, secret management |
| 7. Orchestration | Coordination | Registration hijacking, execution order |

### Implementation Status in Agents-eval

Controls implemented across sprints 5-6:

- **Layer 1**: Structured outputs with Pydantic schema validation; prompt injection
  sanitization (`tests/security/`)
- **Layer 3**: SSRF prevention with domain allowlisting
  (`src/app/utils/url_validation.py`); HTTPS enforcement
- **Layer 4**: Log scrubbing for sensitive data (API keys, tokens); structured
  logging with loguru
- **Layer 5**: Per-component timeouts; bounded iteration
- **Layer 6**: `.env` excluded from VCS; credentials from environment variables

### Unique Value

- Purpose-built for multi-agent architectures — no adaptation needed
- Prescriptive control mappings (what to implement, not just what to watch for)
- Agent lifecycle governance (provisioning, access, deprovisioning)
- Direct regulatory alignment (NIST AI RMF, EU AI Act)

## 2. MITRE ATLAS

**Source**: [MITRE ATLAS](https://atlas.mitre.org/)
**Existing coverage**: Minimal — name and scope referenced in
[security-advisories.md](../security-advisories.md)

### Framework Structure

ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) extends
the ATT&CK methodology to AI/ML systems. Uses the same Tactics → Techniques →
Procedures hierarchy with `AML.Txxxx` technique IDs.

**Tactics** cover the full ML attack lifecycle: Reconnaissance, Resource
Development, Initial Access, Execution, Persistence, Defense Evasion, Discovery,
Collection, ML Attack Staging, Exfiltration, Impact, Credential Access, Privilege
Escalation, and Agentic Behaviors (2024-2025 addition).

### Key Techniques for Multi-Agent Systems

| Technique | Name | MAS Relevance |
| --- | --- | --- |
| AML.T0051 | LLM Prompt Injection | One agent's output becomes another's prompt — injection propagates across the agent graph |
| AML.T0054 | LLM Jailbreak | Bypassing safety guardrails on individual agents corrupts downstream reasoning |
| AML.T0056 | Meta-Prompt Extraction | Recovering agent system prompts reveals orchestration logic and trust assumptions |
| AML.T0040 | ML Supply Chain Compromise | Compromising agent frameworks (PydanticAI), tool registries (MCP), or model weights |
| AML.T0043 | Craft Adversarial Data | Poisoning evaluation datasets to corrupt benchmark integrity |
| AML.T0024 | Exfiltration via ML Inference API | Using agent output channels to exfiltrate sensitive data extracted during inference |
| AML.T0096 | AI Service API Abuse | Credential theft, cost amplification, rate limit bypass on LLM provider APIs |

### Agentic AI Attack Surfaces (2024-2025)

ATLAS expanded to cover AI agents that take autonomous actions:

- **Multi-hop injection**: Poisoned output from one agent cascades to downstream
  agents in the evaluation pipeline
- **Tool parameter injection**: Attacker-controlled content modifies tool call
  arguments
- **Credential abuse**: Agents manipulated to exfiltrate API keys via outputs or
  logs
- **Tool scope creep**: Agent convinced to use tools beyond its operational envelope

### Applicability to Agents-eval (ATLAS)

| Component | ATLAS Threat | Specific Risk |
| --- | --- | --- |
| PydanticAI agents | AML.T0051, AML.T0054 | System prompts overridden via injected inputs in evaluation datasets |
| PeerRead dataset ingestion | AML.T0043 | Poisoned papers skew evaluation metrics |
| Tool registry / function calls | Agentic Behaviors | Evaluation tools (file I/O, HTTP) are attack surfaces if scope is unbounded |
| API credentials | AML.T0096 | Prompt injection could exfiltrate keys via agent outputs or logs |
| Agent graph orchestration | AML.T0056 | Compromised evaluation agent corrupts downstream assessments |
| Trace/artifact collection | AML.T0024 | Execution traces may contain sensitive model outputs |

### How ATLAS Complements MAESTRO

| Dimension | ATLAS | MAESTRO |
| --- | --- | --- |
| Perspective | Attacker (red-team TTPs) | Defender (control mappings) |
| Evidence base | Real-world case studies and incidents | Prescriptive checklists |
| Coverage | Broad ML/AI attack surface (non-LLM included) | Multi-agent topology-specific |
| Detection | Per-technique detection signals | Operational monitoring controls |
| ATT&CK integration | Direct mapping to ATT&CK for unified threat modeling | Standalone |
| Regulatory alignment | Indirect | Direct (NIST, EU AI Act) |

**Combined use**: ATLAS enumerates the threat landscape (what attacks exist);
MAESTRO maps those threats to operational controls (what to implement). Example:
ATLAS AML.T0051 (Prompt Injection) + MAESTRO Layer 1 threat table → together
define both the attack vector taxonomy and the control set.

## 3. NIST AI Risk Management Framework

**Source**: [NIST AI 100-1](https://www.nist.gov/artificial-intelligence/executive-order-safe-secure-and-trustworthy-artificial-intelligence) (January 2023)
**Companion**: [NIST AI 600-1 Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1) (July 2024)
**Existing coverage**: Brief reference in [security-advisories.md](../security-advisories.md)

### Four Core Functions

The framework organizes AI risk management into four iterative, interconnected
functions applied continuously throughout the AI lifecycle.

#### GOVERN — Culture, Policies, Accountability

Establishes organizational structures that enable risk management. Without
governance, Map/Measure/Manage are ad hoc.

| Category | Description |
| --- | --- |
| GOVERN 1 | Policies, processes, procedures for AI risk management |
| GOVERN 2 | Accountability structures and roles defined |
| GOVERN 4 | Teams trained and resourced |
| GOVERN 5 | Stakeholder feedback and organizational learning |
| GOVERN 6 | Responsible disclosure provisions |

**MAS application**: Define risk appetite for evaluation confidence thresholds;
assign risk owner; review LLM provider API terms; establish disclosure process
for evaluation errors.

#### MAP — Context, Risk Identification, Categorization

Establishes the context in which the AI system operates and identifies risks
before measurement begins.

| Category | Description |
| --- | --- |
| MAP 1 | Context established (purpose, deployment, stakeholders) |
| MAP 2 | Scientific knowledge supporting risk decisions documented |
| MAP 3 | Risks to individuals, groups, society identified |
| MAP 5 | Likelihood and magnitude of impacts characterized |

**MAS application**: Document intended use vs foreseeable misuse; catalog AI
supply chain (PydanticAI, LLM APIs, PeerRead); identify stakeholder impact
(paper authors, reviewers, institutions).

#### MEASURE — Assessment, Metrics, Monitoring

Applies quantitative and qualitative methods to analyze and track risks,
converting subjective awareness into evidence-based understanding.

| Category | Description |
| --- | --- |
| MEASURE 1 | Measurement approaches identified and applied |
| MEASURE 2 | Risks analyzed, assessed, ranked, tracked |
| MEASURE 3 | Risks tracked over time |
| MEASURE 4 | Results documented and communicated |

**Trustworthiness characteristics**: Accuracy/reliability, explainability,
fairness/bias, privacy, safety, security/resilience, transparency, accountability.

**MAS application**: Benchmark evaluations against human ground truth; disaggregate
scores for bias testing; implement confabulation detection; red-team for prompt
injection via adversarial paper content.

#### MANAGE — Treatment, Response, Communication

Implements risk treatment decisions and establishes response processes.

| Category | Description |
| --- | --- |
| MANAGE 1 | Risk treatment plan established |
| MANAGE 2 | Strategies planned, implemented, documented |
| MANAGE 3 | Risks tracked and managed over time |
| MANAGE 4 | Treatment impacts documented |

**Treatment options**: Avoid, Mitigate, Transfer, Accept (with documented rationale).

**MAS application**: Pin LLM model versions; implement provider failover; add
verification agents for confabulation; attach confidence intervals to scores.

### Generative AI Profile (AI 600-1)

Extends AI RMF with twelve GenAI-specific risk categories:

| Risk Category | MAS Relevance |
| --- | --- |
| Confabulation | HIGH — LLM agents may fabricate paper details or citations |
| Data Privacy | MEDIUM — papers may contain author PII |
| Human-AI Configuration | HIGH — over-reliance on automated scores |
| Information Security | HIGH — prompt injection, credential exfiltration |
| Toxicity, Bias, Homogenization | HIGH — LLM bias in paper scoring |
| Value Chain / Component Integration | HIGH — three external LLM API dependencies |

**Agentic AI risks** (AI 600-1 extensions): prompt injection in tool outputs,
uncontrolled tool use, goal misalignment, multi-hop trust degradation, reduced
human oversight, context window manipulation.

## 4. ISO/IEC 42001 and ISO/IEC 23894

**Sources**: [ISO 42001:2023](https://www.iso.org/standard/81230.html),
[ISO 23894:2023](https://www.iso.org/standard/77304.html)
**Existing coverage**: Brief reference in [security-advisories.md](../security-advisories.md)

### ISO 42001 — AI Management System (AIMS)

First international certifiable standard for AI governance. Follows ISO
High-Level Structure (Annex SL), enabling integration with ISO 27001, ISO 9001.

**Key clauses** (PDCA structure):

| Clause | Title | Content |
| --- | --- | --- |
| 4 | Context of the Organization | Internal/external issues, stakeholder needs, AIMS scope |
| 5 | Leadership | Top management commitment, AI policy, roles |
| 6 | Planning | Risk/opportunity assessment, AI objectives, AI impact assessment |
| 7 | Support | Resources, competence, awareness, communication |
| 8 | Operation | Lifecycle controls, data management, supplier assessment |
| 9 | Performance Evaluation | Monitoring, internal audit, management review |
| 10 | Improvement | Corrective action, continual improvement |

**Annex A controls** — 38 controls across 8 domains:

| Domain | Key Controls |
| --- | --- |
| A.2 Policies | AI policy, role-specific policies |
| A.5 Impact Assessment | AI system impact assessment process |
| A.6 AI Lifecycle | Specification, data, design, testing, deployment, monitoring, decommissioning |
| A.7 Responsible AI | Transparency, explainability, fairness, accountability, privacy, safety |
| A.8 Third Parties | Supplier assessment, contractual obligations |
| A.9 Documentation | Technical documentation, model cards |

### ISO 23894 — AI Risk Management Guidance

Extends ISO 31000 (generic risk management) with AI-specific considerations.
Guidance document (not certifiable).

**Risk management process** (adapted for AI):

1. **Scope and context**: AI system purpose, stakeholders, risk criteria
2. **Risk identification**: Source-based (data, algorithms, environment) and
   event-based (failure modes, misuse, emergent behaviors)
3. **Risk analysis**: Likelihood estimation (accounting for AI non-determinism),
   consequence assessment (individual, group, societal)
4. **Risk evaluation**: Compare against criteria, prioritize for treatment
5. **Risk treatment**: Avoid, Modify, Share, Retain
6. **Monitoring**: Ongoing performance monitoring, incident tracking, register
   updates

**AI-specific risk categories**:

| Category | Examples |
| --- | --- |
| Data risks | Bias in training data, data poisoning, distribution shift |
| Model risks | Adversarial vulnerability, lack of robustness, unexplainability |
| Integration risks | Automation bias, unsafe human-AI interaction, feedback loops |
| Operational risks | Misuse by operators, out-of-distribution deployment, model drift |
| Lifecycle risks | Inadequate testing, insufficient monitoring, uncontrolled updates |

### ISO 42001 vs ISO 23894

| Dimension | ISO 42001 | ISO 23894 |
| --- | --- | --- |
| Type | Requirements (shall) | Guidance (should) |
| Certifiable | Yes | No |
| Scope | Entire AI management system | Risk management process only |
| Output | AIMS with controls, SoA, audits | Risk register, treatment plan |
| When to use | Certification needed; full AIMS | Building risk assessment process |

**Integration**: ISO 23894 provides the risk methodology that ISO 42001 Clause 6.1
requires. ISO 23894 answers "how do we identify AI risks?"; ISO 42001 answers
"how do we govern the entire AI management process?"

### Applicability to Agents-eval (ISO)

**Highest-priority ISO 42001 controls**:

- **A.5 Impact Assessment**: Evaluation outputs influence research decisions —
  requires documented impact assessment
- **A.6.2 Data for AI Systems**: PeerRead dataset provenance, quality, and bias
  assessment
- **A.6.4 Verification and Validation**: Multi-agent evaluation accuracy
  validated against ground truth
- **A.7.4 Bias and Fairness**: LLM judges inherit training data biases —
  requires bias testing
- **A.8 Third Parties**: LLM API providers require supplier assessment

**Highest-priority ISO 23894 risks**:

| Risk | Likelihood | Consequence | Treatment |
| --- | --- | --- | --- |
| LLM evaluation bias | HIGH | HIGH | Bias testing, multiple judge models, HITL validation |
| Specification gaming (Goodhart's Law) | MEDIUM | HIGH | Multi-dimensional evaluation, periodic metric review |
| Data distribution shift | HIGH | MEDIUM | Scope documentation, out-of-distribution testing |
| Agent coordination failures | MEDIUM | MEDIUM | Pydantic schema enforcement, circuit breakers |
| Over-reliance by downstream users | MEDIUM | HIGH | Limitation documentation, confidence indicators |

## Cross-Framework Mapping

How the four frameworks relate to each other:

```text
MITRE ATLAS (attack taxonomy — what adversaries do)
      |
      | informs threat identification
      v
OWASP MAESTRO (threat model — what to defend against in MAS)
      |
      | maps threats to controls
      v
NIST AI RMF (risk framework — how to govern/map/measure/manage)
      |
      | operationalized by
      v
ISO 42001 + 23894 (certifiable management system + risk methodology)
```

### Unified Mapping Table

| Concern | ATLAS Technique | MAESTRO Layer | NIST Function | ISO Control |
| --- | --- | --- | --- | --- |
| Prompt injection | AML.T0051 | L1 Model | MEASURE 2.6 | A.7.3 |
| API credential theft | AML.T0096 | L3 Integration | GOVERN 1.5 | A.8 |
| Log data leakage | AML.T0024 | L4 Monitoring | MAP 3 | A.7.5 |
| Resource exhaustion | — | L5 Execution | MANAGE 2 | A.6.6 |
| Supply chain compromise | AML.T0040 | L6 Environment | MAP 1.6 | A.8 |
| Agent hijacking | AML.T0056 | L7 Orchestration | MEASURE 2.6 | A.6.4 |
| Evaluation bias | AML.T0043 | L2 Agent Logic | MEASURE 2.5 | A.7.4 |

## Recommendations for Agents-eval

Given the project's open-source research context, full certification (ISO 42001)
is not warranted. A lightweight alignment approach:

1. **Continue using MAESTRO** as the primary threat model — existing implementation
   in [mas-security.md](../best-practices/mas-security.md) is comprehensive
2. **Tag security tests with ATLAS technique IDs** in docstrings (e.g.,
   `# ATLAS: AML.T0051`) to ground existing tests in the adversary taxonomy
3. **Adopt NIST AI RMF MEASURE function** for evaluation quality — benchmark
   against ground truth, disaggregate for bias, track confabulation rates
4. **Implement ISO 23894 risk register** as a lightweight governance artifact —
   track the top 5-7 risks identified above with treatment status
5. **Document an AI impact assessment** (ISO 42001 A.5 / NIST MAP) covering
   evaluation output consequences on research community stakeholders

## References

- [OWASP MAESTRO v1.0](https://genai.owasp.org/resource/multi-agentic-system-threat-modeling-guide-v1-0/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI RMF 1.0 (AI 100-1)](https://www.nist.gov/artificial-intelligence/executive-order-safe-secure-and-trustworthy-artificial-intelligence)
- [NIST AI 600-1 Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)
- [ISO/IEC 23894:2023](https://www.iso.org/standard/77304.html)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
