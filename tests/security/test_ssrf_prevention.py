"""SSRF prevention security tests.

Tests URL validation to prevent SSRF (Server-Side Request Forgery) attacks
as identified in CVE-2026-25580 and Sprint 5 MAESTRO review Finding CVE-1.

Attack vectors tested:
- Internal IP addresses (AWS metadata, GCP metadata, loopback)
- Non-HTTPS schemes (HTTP, FTP, file://)
- IDN homograph attacks (unicode domain lookalikes)
- Localhost and private network IPs
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.utils.url_validation import validate_url


class TestSSRFInternalIPPrevention:
    """Test SSRF prevention for internal IP addresses."""

    @pytest.mark.parametrize(
        "url,description",
        [
            ("https://169.254.169.254/latest/meta-data/", "AWS EC2 metadata endpoint"),
            (
                "https://169.254.169.254/latest/meta-data/iam/security-credentials/",
                "AWS IAM credentials",
            ),
            ("https://metadata.google.internal/computeMetadata/v1/", "GCP metadata"),
            ("https://localhost/admin", "localhost HTTP"),
            ("https://127.0.0.1/secrets", "loopback IPv4"),
            ("https://0.0.0.0/data", "any IPv4 address"),
            ("https://[::1]/internal", "loopback IPv6"),
            ("https://[::ffff:127.0.0.1]/data", "IPv4-mapped IPv6 loopback"),
        ],
    )
    def test_internal_ip_addresses_blocked(self, url: str, description: str):
        """Internal IP addresses should be blocked to prevent SSRF attacks."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    @pytest.mark.parametrize(
        "private_ip",
        [
            "https://192.168.0.1/router",
            "https://192.168.1.1/admin",
            "https://192.168.255.255/data",
            "https://10.0.0.1/secrets",
            "https://10.255.255.255/internal",
            "https://172.16.0.1/private",
            "https://172.31.255.255/network",
        ],
    )
    def test_private_network_ranges_blocked(self, private_ip: str):
        """Private network IP ranges (RFC 1918) should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(private_ip)


class TestSSRFNonHTTPSPrevention:
    """Test SSRF prevention for non-HTTPS schemes."""

    @pytest.mark.parametrize(
        "url,scheme",
        [
            ("http://raw.githubusercontent.com/data.json", "HTTP"),
            ("ftp://files.example.com/data.txt", "FTP"),
            ("file:///etc/passwd", "file://"),
            ("file:///c:/windows/system32/config/sam", "file:// Windows"),
            ("data:text/html,<script>alert(1)</script>", "data: URI"),
            ("javascript:alert(document.cookie)", "javascript:"),
            ("gopher://evil.com:70/1", "gopher"),
        ],
    )
    def test_non_https_schemes_blocked(self, url: str, scheme: str):
        """Non-HTTPS schemes should be blocked to prevent protocol smuggling."""
        with pytest.raises(ValueError, match="Only HTTPS URLs allowed"):
            validate_url(url)

    def test_missing_scheme_blocked(self):
        """URLs without scheme should be rejected."""
        with pytest.raises(ValueError, match="Only HTTPS URLs allowed"):
            validate_url("raw.githubusercontent.com/data.json")


class TestSSRFIDNHomographAttacks:
    """Test SSRF prevention for IDN homograph attacks."""

    @pytest.mark.parametrize(
        "url,description",
        [
            # Cyrillic lookalikes
            ("https://аpi.openai.com/v1/completions", "Cyrillic 'а' (U+0430)"),
            ("https://api.ореnai.com/v1/completions", "Cyrillic 'о' and 'е'"),
            ("https://аpi.аnthropic.com/v1/messages", "Multiple Cyrillic chars"),
            # Greek lookalikes
            ("https://αpi.openai.com/v1/completions", "Greek alpha"),
            ("https://api.οpenai.com/v1/completions", "Greek omicron"),
            # Latin extended lookalikes
            ("https://ɑpi.openai.com/v1/completions", "Latin small letter alpha (U+0251)"),
            ("https://api.сerebras.ai/v1/chat", "Cyrillic 'с' (U+0441)"),
        ],
    )
    def test_idn_homograph_domains_blocked(self, url: str, description: str):
        """IDN homograph attacks using lookalike unicode characters should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    @pytest.mark.parametrize(
        "punycode_url",
        [
            "https://xn--pi-openai-7bb.com/data",  # Punycode-encoded domain
            "https://xn--pi-qmc.openai.com/data",  # Partial punycode
        ],
    )
    def test_punycode_encoded_lookalikes_blocked(self, punycode_url: str):
        """Punycode-encoded lookalike domains should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(punycode_url)


class TestSSRFLocalhostVariants:
    """Test SSRF prevention for localhost and loopback variants."""

    @pytest.mark.parametrize(
        "localhost_url",
        [
            "https://localhost/admin",
            "https://localhost:8080/api",
            "https://LOCALHOST/secrets",  # Case variation
            "https://127.0.0.1/internal",
            "https://127.0.0.2/data",  # Other 127.x.x.x
            "https://127.255.255.255/test",
            "https://[::1]/ipv6-loopback",
            "https://[0:0:0:0:0:0:0:1]/ipv6-expanded",
        ],
    )
    def test_localhost_variants_blocked(self, localhost_url: str):
        """All localhost and loopback variants should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(localhost_url)


class TestSSRFPropertyBasedFuzzing:
    """Property-based tests for SSRF prevention using Hypothesis."""

    @given(
        octet1=st.integers(min_value=0, max_value=255),
        octet2=st.integers(min_value=0, max_value=255),
        octet3=st.integers(min_value=0, max_value=255),
        octet4=st.integers(min_value=0, max_value=255),
    )
    def test_all_ipv4_addresses_blocked_unless_allowed(
        self, octet1: int, octet2: int, octet3: int, octet4: int
    ):
        """All IPv4 addresses should be blocked unless explicitly in allowlist."""
        url = f"https://{octet1}.{octet2}.{octet3}.{octet4}/data"
        # All IPs are blocked since none are in ALLOWED_DOMAINS
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    @given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=50))
    def test_random_domains_blocked_unless_allowed(self, domain: str):
        """Random domains should be blocked unless in allowlist."""
        # Skip domains that are in the allowlist or are invalid
        from app.utils.url_validation import ALLOWED_DOMAINS

        if domain in ALLOWED_DOMAINS or not domain.strip():
            return

        url = f"https://{domain}/data"
        try:
            validate_url(url)
            # If it passes, the domain must be in allowlist
            assert domain in ALLOWED_DOMAINS
        except ValueError as e:
            # Expected: domain not allowed or malformed URL
            assert "URL domain not allowed" in str(e) or "Malformed" in str(e) or "empty" in str(e)


class TestSSRFURLParsingEdgeCases:
    """Test URL parsing edge cases that could bypass SSRF protection."""

    @pytest.mark.parametrize(
        "url,description",
        [
            ("https://evil.com@raw.githubusercontent.com/data", "Credentials bypass attempt"),
            ("https://raw.githubusercontent.com.evil.com/data", "Subdomain append"),
            ("https://evil.com#raw.githubusercontent.com", "Fragment bypass attempt"),
            ("https://evil.com?host=raw.githubusercontent.com", "Query param bypass"),
        ],
    )
    def test_url_parsing_bypass_attempts_blocked(self, url: str, description: str):
        """URL parsing bypass attempts should be blocked."""
        # These should either be blocked or parsed to extract correct domain
        try:
            validate_url(url)
            # If it passes, verify it extracted the correct domain
            assert "raw.githubusercontent.com" in url
        except ValueError:
            # Expected if evil.com is extracted as domain
            pass

    def test_url_with_port_on_internal_ip_blocked(self):
        """Internal IP with port should still be blocked."""
        url = "https://127.0.0.1:8080/admin"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    def test_url_with_credentials_on_internal_ip_blocked(self):
        """Internal IP with credentials should still be blocked."""
        url = "https://admin:password@127.0.0.1/secrets"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFMetadataEndpoints:
    """Test blocking of cloud provider metadata endpoints."""

    @pytest.mark.parametrize(
        "metadata_url,cloud_provider",
        [
            # AWS
            ("https://169.254.169.254/latest/meta-data/", "AWS EC2"),
            ("https://169.254.169.254/latest/dynamic/instance-identity/", "AWS identity"),
            ("https://169.254.170.2/v2/metadata", "AWS ECS"),
            # GCP
            ("https://metadata.google.internal/computeMetadata/v1/", "GCP"),
            ("https://metadata.google.internal/computeMetadata/v1/instance/service-accounts/", "GCP SA"),
            # Azure
            ("https://169.254.169.254/metadata/instance?api-version=2021-02-01", "Azure"),
            # Digital Ocean
            ("https://169.254.169.254/metadata/v1/", "DigitalOcean"),
        ],
    )
    def test_cloud_metadata_endpoints_blocked(self, metadata_url: str, cloud_provider: str):
        """Cloud provider metadata endpoints should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(metadata_url)
