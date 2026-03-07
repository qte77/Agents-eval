---
title: CC Cowork, Plugins & Enterprise Analysis
source: https://claude.com/blog/cowork-plugins-across-enterprise, https://claude.com/product/cowork
purpose: Analysis of Claude's Cowork enterprise platform, plugin architecture, and connector ecosystem for potential relevance to Agents-eval MAS evaluation framework.
created: 2026-03-07
---

**Status**: Research preview (Cowork desktop app); Plugin architecture in active rollout

## What Cowork & Plugins Are

**Cowork** is Claude's agentic desktop application for knowledge work — a local app (Windows/macOS) where users give Claude access to local files and tools, set a task, and step away ([source][cowork-product]). Operates with more agency than Claude Chat: users describe outcomes and cadence, Claude takes action and reports progress ([source][cowork-product]). Available on all paid plans (Max, Team, Enterprise); agent safety is still in development ([source][cowork-product]).

**Plugins** are portable file-system bundles that transform into specialized agents, deployable across Cowork and anything built on the Claude Agent SDK ([source][sdk-plugins]).

### Core Components

#### Plugin Architecture

- Plugins are "simple, portable file systems that you own" ([source][cowork-blog])
- Transform into specialized agents for distinct job functions ([source][sdk-plugins])
- Cross-platform: work in Cowork and Claude Agent SDK applications ([source][sdk-plugins])
- Slash commands launch structured forms for workflow execution ([source][cowork-blog])
- Private GitHub repos as plugin sources (beta) ([source][cowork-blog])
- Organization-specific marketplaces for plugin distribution ([source][cowork-blog])

#### Admin Customization Controls

- Unified "Customize" menu: plugins, skills, connectors ([source][cowork-blog])
- Starter templates or custom-built configurations ([source][cowork-blog])
- Claude-guided questionnaires for tailor-made solutions ([source][cowork-blog])
- Per-user provisioning and auto-installation ([source][cowork-blog])
- OpenTelemetry support for usage tracking, cost monitoring, tool activity audits ([source][cowork-blog])

#### Enterprise Connectors

Google Workspace (Calendar, Drive, Gmail), Docusign, Apollo, Clay, Outreach, Similarweb, MSCI, LegalZoom, FactSet, WordPress, Harvey.

#### Pre-Built Plugin Templates

- **Engineering**: Standup summaries, incident response
- **HR**: Offer letters, onboarding, reviews
- **Design**: Critique frameworks, accessibility audits
- **Operations**: Process documentation, vendor evaluation
- **Financial Analysis**: Market research, modeling
- **Investment Banking**: Deal workflows
- **Equity Research**: Transcript parsing
- **Private Equity**: Diligence and scoring
- **Wealth Management**: Portfolio analysis
- **Brand Voice**: By Tribe AI

#### Multi-App Orchestration

Claude coordinates tasks across Excel and PowerPoint — running analyses in one app and converting results into presentations in the other, passing context between applications automatically. ([source][cowork-blog])

### Availability

- UX updates: All Cowork users
- Admin controls (branding, provisioning, connectors): Team and Enterprise
- Excel/PowerPoint cross-app: Research preview, paid plans, Mac and Windows ([source][cowork-blog])

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Aspect | Fit | Rationale |
| ------ | --- | --------- |
| Plugin architecture for evaluation agents | Moderate | Plugins as portable agent bundles could package our evaluation pipeline (Researcher/Analyst/Synthesizer) for distribution |
| OTel support for usage tracking | Strong | Aligns with existing Phoenix/OTel strategy (see [CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md#tracing--observability)) |
| Connector ecosystem | Weak | Project doesn't integrate with Google Workspace, Docusign, etc. |
| Pre-built templates | Weak | Templates target business workflows, not research/evaluation |
| Multi-app orchestration (Excel/PowerPoint) | None | No Excel/PowerPoint in evaluation workflows |
| Organization marketplace | Moderate | Could distribute evaluation skills/plugins to research team |

<!-- markdownlint-enable MD013 -->

### Plugin Architecture vs Project Skills

Current Skills architecture documented in [CC-skills-adoption-analysis.md](CC-skills-adoption-analysis.md). Key differences: Plugins are cross-platform (Cowork + Agent SDK) with org marketplace distribution and admin provisioning; Skills are repo-local with auto-discovery. Plugins add structured form UI and OTel integration that Skills lack.

### Decision Rule

**Cowork/Plugins are enterprise deployment features. This project's CC usage is developer-local (Ralph loop, baselines, interactive dev). No adoption action needed until the project needs to distribute evaluation capabilities to a broader team.**

### Potential Future Integration

If the evaluation framework becomes a team-wide tool:

1. **Package evaluation pipeline as a plugin** — portable bundle with Researcher/Analyst/Synthesizer agents
2. **Use OTel support** for centralized cost/usage tracking across team members running evaluations
3. **Create org marketplace** for evaluation skill distribution

**Recommendation**: Do not integrate. Cowork/Plugins target enterprise deployment and team-wide AI customization. This project is a research evaluation framework used by individual developers. The existing Skills architecture (`.claude/skills/`) already provides the modular capability pattern needed. Revisit if:

1. Evaluation framework needs distribution to non-developer stakeholders
2. Plugin API stabilizes and supports programmatic creation

## References

- [Cowork product page][cowork-product]
- [Cowork & Plugins announcement][cowork-blog]
- [CC Skills docs][cc-skills]
- [Agent SDK Plugins docs][sdk-plugins]
- [Agent SDK Skills docs][sdk-skills]

[cowork-product]: https://claude.com/product/cowork
[cowork-blog]: https://claude.com/blog/cowork-plugins-across-enterprise
[cc-skills]: https://code.claude.com/docs/en/skills
[sdk-plugins]: https://platform.claude.com/docs/en/agent-sdk/plugins
[sdk-skills]: https://platform.claude.com/docs/en/agent-sdk/skills
