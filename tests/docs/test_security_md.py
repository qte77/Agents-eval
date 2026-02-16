"""
Tests for SECURITY.md CVE documentation.

This module tests that the SECURITY.md file exists and contains required CVE advisories.
"""

from pathlib import Path

import pytest


@pytest.fixture
def security_md_path() -> Path:
    """Get path to SECURITY.md file."""
    return Path(__file__).parent.parent.parent / "SECURITY.md"


class TestSecurityMDExists:
    """Test that SECURITY.md file exists."""

    def test_security_md_file_exists(self, security_md_path: Path):
        """SECURITY.md file should exist in project root."""
        assert security_md_path.exists(), f"SECURITY.md not found at {security_md_path}"

    def test_security_md_is_not_empty(self, security_md_path: Path):
        """SECURITY.md should not be empty."""
        content = security_md_path.read_text()
        assert len(content.strip()) > 0, "SECURITY.md is empty"


class TestCVEDocumentation:
    """Test that required CVE advisories are documented."""

    def test_cve_2026_25580_documented(self, security_md_path: Path):
        """CVE-2026-25580 (PydanticAI SSRF) should be documented."""
        content = security_md_path.read_text()
        assert "CVE-2026-25580" in content, "CVE-2026-25580 not documented"

    def test_cve_2026_25580_mitigation_documented(self, security_md_path: Path):
        """CVE-2026-25580 mitigation strategy should be documented."""
        content = security_md_path.read_text()
        # Should mention URL validation or allowlist as mitigation
        assert any(
            term in content.lower()
            for term in ["url validation", "domain allowlist", "validate_url"]
        ), "CVE-2026-25580 mitigation not documented"

    def test_cve_2026_25640_documented(self, security_md_path: Path):
        """CVE-2026-25640 (PydanticAI XSS) should be documented."""
        content = security_md_path.read_text()
        assert "CVE-2026-25640" in content, "CVE-2026-25640 not documented"

    def test_cve_2026_25640_not_applicable_status(self, security_md_path: Path):
        """CVE-2026-25640 should be marked as not applicable."""
        content = security_md_path.read_text()
        # Should mention that we don't use the affected features
        assert any(
            phrase in content.lower()
            for phrase in [
                "does not affect",
                "not applicable",
                "do not use",
                "not affected",
            ]
        ), "CVE-2026-25640 applicability status not documented"

    def test_cve_2026_25640_affected_features_documented(self, security_md_path: Path):
        """CVE-2026-25640 should document affected features."""
        content = security_md_path.read_text()
        # Should mention the specific affected features
        assert any(feature in content for feature in ["clai web", "Agent.to_web()"]), (
            "CVE-2026-25640 affected features not documented"
        )

    def test_cve_2024_5206_documented(self, security_md_path: Path):
        """CVE-2024-5206 (scikit-learn) should be documented."""
        content = security_md_path.read_text()
        assert "CVE-2024-5206" in content, "CVE-2024-5206 not documented"

    def test_cve_2024_5206_mitigation_documented(self, security_md_path: Path):
        """CVE-2024-5206 mitigation (version upgrade) should be documented."""
        content = security_md_path.read_text()
        # Should mention scikit-learn version requirement
        assert any(term in content for term in ["scikit-learn>=1.8.0", "scikit-learn 1.8"]), (
            "CVE-2024-5206 mitigation (version) not documented"
        )


class TestSecurityMDStructure:
    """Test SECURITY.md has proper structure."""

    def test_has_security_advisories_section(self, security_md_path: Path):
        """SECURITY.md should have a Security Advisories section."""
        content = security_md_path.read_text()
        assert any(
            heading in content for heading in ["# Security Advisories", "## Security Advisories"]
        ), "Security Advisories section not found"

    def test_has_vulnerability_reporting_section(self, security_md_path: Path):
        """SECURITY.md should have a Vulnerability Reporting section."""
        content = security_md_path.read_text()
        assert any(
            heading in content
            for heading in [
                "# Reporting",
                "## Reporting",
                "# Vulnerability Reporting",
                "## Vulnerability Reporting",
            ]
        ), "Vulnerability Reporting section not found"

    def test_cve_links_present(self, security_md_path: Path):
        """CVE entries should include reference links."""
        content = security_md_path.read_text()
        # Should have at least one URL for CVE references
        assert "http" in content or "https" in content, "No reference links found"
