"""
Tests for SSRF prevention in external HTTP requests.

This module tests SSRF (Server-Side Request Forgery) attack prevention across
the application, focusing on URL validation at external request boundaries.

MAESTRO Layer 3 (Integration) security controls tested:
- Internal IP blocking (AWS metadata, GCP metadata, localhost)
- Non-HTTPS scheme rejection
- Domain allowlist enforcement
- IDN homograph attack prevention
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.utils.url_validation import validate_url


class TestSSRFInternalIPBlocking:
    """Test SSRF prevention blocks internal IP addresses."""

    @pytest.mark.parametrize(
        "url,description",
        [
            ("https://169.254.169.254/latest/meta-data/", "AWS EC2 metadata endpoint"),
            (
                "https://169.254.169.254/latest/meta-data/iam/security-credentials/",
                "AWS IAM credentials",
            ),
            ("https://metadata.google.internal/", "GCP metadata endpoint"),
            (
                "https://metadata.google.internal/computeMetadata/v1/",
                "GCP compute metadata",
            ),
            ("https://localhost/admin", "localhost"),
            ("https://127.0.0.1/secrets", "loopback IP"),
            ("https://127.0.0.2/internal", "loopback range"),
            ("https://0.0.0.0/data", "any IP (0.0.0.0)"),
            ("https://[::1]/internal", "IPv6 loopback"),
            ("https://[::ffff:127.0.0.1]/data", "IPv4-mapped IPv6 loopback"),
        ],
    )
    def test_internal_ip_addresses_blocked(self, url: str, description: str):
        """Internal IP addresses and metadata endpoints should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFPrivateNetworkBlocking:
    """Test SSRF prevention blocks private network IP ranges."""

    @pytest.mark.parametrize(
        "ip_address,network_range",
        [
            ("192.168.0.1", "192.168.0.0/16 (private class C)"),
            ("192.168.1.100", "192.168.0.0/16"),
            ("192.168.255.254", "192.168.0.0/16"),
            ("10.0.0.1", "10.0.0.0/8 (private class A)"),
            ("10.255.255.254", "10.0.0.0/8"),
            ("172.16.0.1", "172.16.0.0/12 (private class B)"),
            ("172.31.255.254", "172.16.0.0/12"),
        ],
    )
    def test_private_network_ranges_blocked(self, ip_address: str, network_range: str):
        """RFC 1918 private network ranges should be blocked."""
        url = f"https://{ip_address}/data"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFNonHTTPSBlocking:
    """Test SSRF prevention enforces HTTPS-only."""

    @pytest.mark.parametrize(
        "url,scheme",
        [
            ("http://raw.githubusercontent.com/data", "http"),
            ("ftp://api.openai.com/data", "ftp"),
            ("file:///etc/passwd", "file"),
            ("file:///c:/windows/system32/config/sam", "file (Windows)"),
            ("data:text/html,<script>alert(1)</script>", "data URI"),
            ("javascript:alert(1)", "javascript"),
            ("gopher://127.0.0.1:25/xHELO%20localhost", "gopher (SSRF smuggling)"),
        ],
    )
    def test_non_https_schemes_rejected(self, url: str, scheme: str):
        """Non-HTTPS schemes should be rejected to prevent SSRF attacks."""
        with pytest.raises(ValueError, match="Only HTTPS URLs allowed"):
            validate_url(url)


class TestSSRFIDNHomographAttacks:
    """Test SSRF prevention blocks IDN homograph attacks."""

    @pytest.mark.parametrize(
        "url,description",
        [
            (
                "https://аpi.openai.com/v1/completions",
                "Cyrillic 'а' (U+0430) instead of Latin 'a'",
            ),
            (
                "https://api.ореnai.com/v1/completions",
                "Cyrillic 'о' (U+043E) and 'е' (U+0435)",
            ),
            (
                "https://ɑpi.openai.com/v1/completions",
                "Latin small letter alpha (U+0251)",
            ),
            ("https://арі.openai.com/data", "Cyrillic lookalike domain"),
        ],
    )
    def test_unicode_homograph_domains_blocked(self, url: str, description: str):
        """Unicode homograph attacks should be blocked."""
        # These domains are not in the allowlist, so they should be rejected
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    def test_punycode_encoded_lookalike_blocked(self):
        """Punycode-encoded lookalike domains should be blocked."""
        # xn-- prefix indicates punycode encoding
        # Example: xn--pi-openai.com (Cyrillic characters)
        url = "https://xn--pi-openai-abc123.com/data"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFLinkLocalAddresses:
    """Test SSRF prevention blocks link-local addresses."""

    @pytest.mark.parametrize(
        "url,description",
        [
            ("https://169.254.1.1/data", "Link-local IPv4"),
            ("https://[fe80::1]/data", "Link-local IPv6"),
            ("https://[fe80::dead:beef]/internal", "Link-local IPv6 with address"),
        ],
    )
    def test_link_local_addresses_blocked(self, url: str, description: str):
        """Link-local addresses should be blocked."""
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFEdgeCases:
    """Test SSRF prevention handles edge cases."""

    def test_url_with_port_variations(self):
        """URLs with non-standard ports on blocked domains should still be blocked."""
        blocked_urls = [
            "https://127.0.0.1:8080/data",
            "https://localhost:3000/admin",
            "https://169.254.169.254:80/metadata",
        ]
        for url in blocked_urls:
            with pytest.raises(ValueError, match="URL domain not allowed"):
                validate_url(url)

    def test_url_with_credentials_in_blocked_domain(self):
        """URLs with credentials in blocked domains should still be blocked."""
        url = "https://user:pass@127.0.0.1/secrets"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    def test_url_with_path_traversal_in_blocked_domain(self):
        """Path traversal attempts in blocked domains should still be blocked."""
        url = "https://127.0.0.1/../../../etc/passwd"
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)


class TestSSRFPropertyBased:
    """Property-based SSRF prevention tests using Hypothesis."""

    @given(
        ip_octet_1=st.integers(min_value=0, max_value=255),
        ip_octet_2=st.integers(min_value=0, max_value=255),
        ip_octet_3=st.integers(min_value=0, max_value=255),
        ip_octet_4=st.integers(min_value=0, max_value=255),
    )
    def test_arbitrary_ip_addresses_blocked(
        self, ip_octet_1: int, ip_octet_2: int, ip_octet_3: int, ip_octet_4: int
    ):
        """Arbitrary IP addresses should be blocked (not in allowlist)."""
        ip = f"{ip_octet_1}.{ip_octet_2}.{ip_octet_3}.{ip_octet_4}"
        url = f"https://{ip}/data"

        # All IP addresses should be blocked since none are in ALLOWED_DOMAINS
        with pytest.raises(ValueError, match="URL domain not allowed"):
            validate_url(url)

    @given(scheme=st.sampled_from(["http", "ftp", "file", "gopher", "data", "javascript"]))
    def test_all_non_https_schemes_blocked(self, scheme: str):
        """All non-HTTPS schemes should be blocked."""
        url = f"{scheme}://example.com/data"
        with pytest.raises(ValueError, match="Only HTTPS URLs allowed"):
            validate_url(url)
