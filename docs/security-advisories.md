# Security Advisories

Known CVE advisories affecting dependencies and their applicability to this project.

## CVE-2026-25580: PydanticAI SSRF Vulnerability (CRITICAL)

**Status**: **MITIGATED**

**Severity**: CRITICAL
**Published**: 2026-02-09
**Affected Component**: PydanticAI message history processing
**CWE**: CWE-918 (Server-Side Request Forgery)

**Description**:
Information disclosure via Server-Side Request Forgery (SSRF) through malicious URLs in PydanticAI message history. Attackers can craft URLs that cause the agent to make unauthorized HTTP requests to internal or external systems.

**Impact**:

- Agents could be tricked into accessing internal AWS metadata (http://169.254.169.254/latest/meta-data/)
- External service enumeration and port scanning
- Bypass of network access controls
- Information disclosure from internal services

**Mitigation Implemented**:
URL validation with domain allowlisting in `src/app/utils/url_validation.py`:

- HTTPS-only enforcement
- Domain allowlist for application-level `httpx.Client` requests (`raw.githubusercontent.com`, `api.github.com`, `arxiv.org`)
- Blocks internal IPs, private network ranges, link-local addresses

Note: LLM provider APIs (OpenAI, Anthropic, Cerebras, etc.) are called through PydanticAI's internal HTTP clients and do not pass through `validate_url()`.

**References**:

- <https://bugzilla.redhat.com/show_bug.cgi?id=2437781>
- <https://www.sentinelone.com/vulnerability-database/cve-2026-25580/>

---

## CVE-2026-25640: PydanticAI Stored XSS via Path Traversal (HIGH)

**Status**: **NOT APPLICABLE**

**Severity**: HIGH
**Published**: 2026-02-06
**Affected Component**: PydanticAI web UI (`clai web` command and `Agent.to_web()` method)
**CWE**: CWE-79 (Cross-site Scripting), CWE-22 (Path Traversal)

**Description**:
Path Traversal vulnerability in PydanticAI web UI allows attackers to serve arbitrary JavaScript in the application context by crafting malicious CDN URLs. Affects `clai web` CLI command and `Agent.to_web()` method.

**Applicability to This Project**:
**This CVE does NOT affect this project** because:

1. This project **does not use** the `clai web` command
2. This project **does not use** the `Agent.to_web()` method
3. The web interface is provided by Streamlit (`src/gui/`), not PydanticAI's built-in web UI

**Recommendation**: Continue to avoid using PydanticAI web UI features until a patched version is available.

**References**:

- <https://advisories.gitlab.com/pkg/pypi/pydantic-ai/CVE-2026-25640/>
- <https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-wjp5-868j-wqv7>

---

## CVE-2024-5206: scikit-learn Sensitive Data Leakage (MEDIUM)

**Status**: **MITIGATED**

**Severity**: MEDIUM (CVSS 5.3)
**Published**: 2024-06-06
**Affected Component**: scikit-learn TfidfVectorizer ≤ 1.4.1.post1
**CWE**: CWE-200 (Information Exposure)

**Description**:
TfidfVectorizer in scikit-learn ≤1.4.1.post1 unexpectedly stores all tokens from training data in `stop_words_` attribute, including potentially sensitive tokens.

**Mitigation Implemented**:
This project pins `scikit-learn>=1.8.0` in `pyproject.toml`, which includes the fix.

**References**:

- <https://vulert.com/vuln-db/CVE-2024-5206>
- <https://www.ibm.com/support/pages/node/7233502>

---

## Related Frameworks

- [MITRE ATLAS](https://atlas.mitre.org/) — Adversarial threat landscape for AI/ML systems
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — LLM-specific vulnerability categories
- [OWASP MAESTRO](https://owasp.org/www-project-multi-agent-security-testing-and-review-operations/) — Multi-agent security testing (used in Sprint 5 review)
