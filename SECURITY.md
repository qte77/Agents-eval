# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it by creating a private security advisory on GitHub or by emailing the maintainers directly at qte@77.gh.

**Please do not disclose security vulnerabilities publicly until they have been addressed.**

## Vulnerability Reporting Process

1. **Report**: Submit a detailed report including steps to reproduce, impact, and any relevant context
2. **Acknowledgment**: We will acknowledge receipt within 48 hours
3. **Investigation**: We will investigate and confirm the vulnerability
4. **Fix**: We will develop and test a fix
5. **Disclosure**: We will coordinate public disclosure after the fix is released

## Security Advisories

### Known CVE Advisories

This section documents known CVE advisories affecting dependencies and their applicability to this project.

#### CVE-2026-25580: PydanticAI SSRF Vulnerability (CRITICAL)

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
This project implements comprehensive URL validation with domain allowlisting to prevent SSRF attacks:

1. **URL Validation Module** (`src/app/utils/url_validation.py`):
   - HTTPS-only enforcement
   - Domain allowlist for external requests
   - Blocks internal IP addresses (127.0.0.1, 169.254.169.254, etc.)
   - Blocks private network ranges (10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12)

2. **Allowed Domains**:
   - `raw.githubusercontent.com` - PeerRead dataset downloads
   - `arxiv.org` - arXiv paper repository
   - `api.openai.com` - OpenAI API
   - `api.anthropic.com` - Anthropic API
   - `api.cerebras.ai` - Cerebras API

3. **Integration Points**:
   - `src/app/data_utils/datasets_peerread.py` - All HTTP requests validated before execution
   - Agent tools processing URLs validate before making requests

**References**:
- <https://bugzilla.redhat.com/show_bug.cgi?id=2437781>
- <https://www.sentinelone.com/vulnerability-database/cve-2026-25580/>

---

#### CVE-2026-25640: PydanticAI Stored XSS via Path Traversal (HIGH)

**Status**: **NOT APPLICABLE**

**Severity**: HIGH
**Published**: 2026-02-06
**Affected Component**: PydanticAI web UI (`clai web` command and `Agent.to_web()` method)
**CWE**: CWE-79 (Cross-site Scripting), CWE-22 (Path Traversal)

**Description**:
Path Traversal vulnerability in PydanticAI web UI allows attackers to serve arbitrary JavaScript in the application context by crafting malicious CDN URLs. Affects `clai web` CLI command and `Agent.to_web()` method.

**Impact**:
- Stored XSS attacks on web interface users
- Theft of chat history and session data
- Client-side code execution in victim browsers

**Applicability to This Project**:
**This CVE does NOT affect this project** because:

1. This project **does not use** the `clai web` command
2. This project **does not use** the `Agent.to_web()` method
3. The web interface is provided by Streamlit (`src/gui/`), not PydanticAI's built-in web UI
4. Phoenix UI is used for trace visualization, not PydanticAI web features

**Mitigation Status**: No mitigation needed - affected features not used

**Recommendation**: Continue to avoid using PydanticAI web UI features (`clai web`, `Agent.to_web()`) until a patched version is available.

**References**:
- <https://advisories.gitlab.com/pkg/pypi/pydantic-ai/CVE-2026-25640/>
- <https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-wjp5-868j-wqv7>

---

#### CVE-2024-5206: scikit-learn Sensitive Data Leakage (MEDIUM)

**Status**: **MITIGATED**

**Severity**: MEDIUM (CVSS 5.3)
**Published**: 2024-06-06
**Affected Component**: scikit-learn TfidfVectorizer ≤ 1.4.1.post1
**CWE**: CWE-200 (Information Exposure)

**Description**:
TfidfVectorizer in scikit-learn ≤1.4.1.post1 unexpectedly stores all tokens from training data in `stop_words_` attribute, including potentially sensitive tokens like passwords or API keys if present in training text.

**Impact**:
- Sensitive tokens (if present in training text) leaked via model inspection
- Affects any code using TfidfVectorizer for text processing

**Mitigation Implemented**:
This project pins `scikit-learn>=1.8.0` in `pyproject.toml`, which includes the fix for this vulnerability.

**Verification**:
```toml
# pyproject.toml line 24
"scikit-learn>=1.8.0",  # F1, precision, recall, accuracy metrics
```

**Affected Code**:
- `src/app/judge/traditional_metrics.py` - Uses TF-IDF for similarity scoring

**Mitigation Status**: Patched version installed (scikit-learn 1.8.0+)

**References**:
- <https://vulert.com/vuln-db/CVE-2024-5206>
- <https://www.ibm.com/support/pages/node/7233502>

---

## Security Best Practices

This project follows security best practices including:

1. **Input Validation**: All external data validated through Pydantic models with field constraints
2. **URL Validation**: SSRF protection via domain allowlisting for all HTTP requests
3. **HTTPS-Only**: All external requests use HTTPS protocol
4. **Secret Management**: API keys loaded from environment variables, never hardcoded
5. **Dependency Scanning**: Regular CVE checks for all dependencies
6. **Principle of Least Privilege**: Minimal required permissions for all operations
7. **Secure Defaults**: Security controls enabled by default, not opt-in

## Security Testing

Security tests are located in `tests/security/` and cover:

- SSRF prevention (URL validation, domain blocking)
- Prompt injection resistance (future enhancement)
- Sensitive data filtering in logs (future enhancement)
- Input size limits (DoS prevention)
- Tool registration scope validation

Run security tests with:
```bash
make test_all  # Includes security tests
```

## Security Contacts

- **Project Maintainer**: qte77 <qte@77.gh>
- **GitHub Security Advisories**: <https://github.com/qte77/Agents-eval/security/advisories>

## Acknowledgments

Security findings reported in:
- Sprint 5 MAESTRO Security Review (`docs/reviews/sprint5-code-review.md`)
- Sprint 5 Parallel Pipeline Review

Thank you to all security researchers who responsibly disclose vulnerabilities.
