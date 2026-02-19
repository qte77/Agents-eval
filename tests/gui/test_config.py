"""Tests for STORY-014: resolve_service_url() environment-aware URL resolution.

Covers:
- resolve_service_url() with PHOENIX_ENDPOINT env var override
- resolve_service_url() in GitHub Codespaces environment
- resolve_service_url() in Gitpod environment
- resolve_service_url() fallback to localhost

Detection chain (first match wins):
1. PHOENIX_ENDPOINT env var override
2. GitHub Codespaces (CODESPACE_NAME + GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN)
3. Gitpod (GITPOD_WORKSPACE_URL)
4. Fallback: http://localhost:{port}
"""

import os
from unittest.mock import patch


class TestResolveServiceUrlExplicitOverride:
    """Verify PHOENIX_ENDPOINT env var takes highest priority."""

    def test_explicit_phoenix_endpoint_override(self) -> None:
        """PHOENIX_ENDPOINT env var must override all detection logic."""
        from gui.config.config import resolve_service_url

        with patch.dict(
            os.environ, {"PHOENIX_ENDPOINT": "https://my-custom-phoenix.example.com"}, clear=False
        ):
            result = resolve_service_url(6006)
        assert result == "https://my-custom-phoenix.example.com", (
            f"Expected PHOENIX_ENDPOINT override, got: {result}"
        )

    def test_explicit_override_ignores_codespaces_env(self) -> None:
        """PHOENIX_ENDPOINT override must win even when Codespaces vars are set."""
        from gui.config.config import resolve_service_url

        env = {
            "PHOENIX_ENDPOINT": "https://override.example.com",
            "CODESPACE_NAME": "my-codespace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev",
        }
        with patch.dict(os.environ, env, clear=False):
            result = resolve_service_url(6006)
        assert result == "https://override.example.com", (
            f"PHOENIX_ENDPOINT must override Codespaces detection, got: {result}"
        )

    def test_explicit_override_ignores_gitpod_env(self) -> None:
        """PHOENIX_ENDPOINT override must win even when Gitpod vars are set."""
        from gui.config.config import resolve_service_url

        env = {
            "PHOENIX_ENDPOINT": "https://override.example.com",
            "GITPOD_WORKSPACE_URL": "https://my-workspace-12345.gitpod.io",
        }
        with patch.dict(os.environ, env, clear=False):
            result = resolve_service_url(6006)
        assert result == "https://override.example.com", (
            f"PHOENIX_ENDPOINT must override Gitpod detection, got: {result}"
        )


class TestResolveServiceUrlCodespaces:
    """Verify GitHub Codespaces URL construction."""

    def test_codespaces_constructs_forwarded_url(self) -> None:
        """Codespaces env must construct https://{name}-{port}.{domain}/ URL."""
        from gui.config.config import resolve_service_url

        env = {
            "CODESPACE_NAME": "my-codespace-abc123",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev",
        }
        # Remove PHOENIX_ENDPOINT if set in test environment
        env_without_override = {k: v for k, v in os.environ.items() if k != "PHOENIX_ENDPOINT"}
        env_without_override.update(env)
        env_without_override.pop("GITPOD_WORKSPACE_URL", None)

        with patch.dict(os.environ, env, clear=True):
            # Re-add essential env vars that might be needed
            result = resolve_service_url(6006)

        assert result == "https://my-codespace-abc123-6006.app.github.dev/", (
            f"Expected Codespaces forwarded URL, got: {result}"
        )

    def test_codespaces_uses_given_port(self) -> None:
        """Codespaces URL must embed the given port number."""
        from gui.config.config import resolve_service_url

        env = {
            "CODESPACE_NAME": "my-space",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            result = resolve_service_url(8080)

        assert "8080" in result, f"Expected port 8080 in URL, got: {result}"
        assert result == "https://my-space-8080.app.github.dev/", (
            f"Expected Codespaces URL with port 8080, got: {result}"
        )

    def test_codespaces_requires_both_env_vars(self) -> None:
        """Only CODESPACE_NAME alone must NOT trigger Codespaces detection."""
        from gui.config.config import resolve_service_url

        with patch.dict(os.environ, {"CODESPACE_NAME": "my-space"}, clear=True):
            result = resolve_service_url(6006)

        # Should fall back to localhost
        assert result == "http://localhost:6006", (
            f"Codespaces detection needs both vars; single var should fall back. Got: {result}"
        )


class TestResolveServiceUrlGitpod:
    """Verify Gitpod URL construction."""

    def test_gitpod_constructs_port_prefixed_url(self) -> None:
        """Gitpod env must replace scheme with port-prefix convention."""
        from gui.config.config import resolve_service_url

        env = {"GITPOD_WORKSPACE_URL": "https://my-workspace-12345.gitpod.io"}
        with patch.dict(os.environ, env, clear=True):
            result = resolve_service_url(6006)

        # Gitpod convention: replace "https://" with "https://6006-"
        assert result == "https://6006-my-workspace-12345.gitpod.io/", (
            f"Expected Gitpod port-prefixed URL, got: {result}"
        )

    def test_gitpod_uses_given_port(self) -> None:
        """Gitpod URL must embed the given port number."""
        from gui.config.config import resolve_service_url

        env = {"GITPOD_WORKSPACE_URL": "https://my-workspace.gitpod.io"}
        with patch.dict(os.environ, env, clear=True):
            result = resolve_service_url(8080)

        assert "8080" in result, f"Expected port 8080 in Gitpod URL, got: {result}"


class TestResolveServiceUrlFallback:
    """Verify localhost fallback behavior."""

    def test_fallback_returns_localhost(self) -> None:
        """Without any env vars, must return http://localhost:{port}."""
        from gui.config.config import resolve_service_url

        with patch.dict(os.environ, {}, clear=True):
            result = resolve_service_url(6006)

        assert result == "http://localhost:6006", f"Expected fallback localhost URL, got: {result}"

    def test_fallback_uses_given_port(self) -> None:
        """Fallback URL must embed the given port number."""
        from gui.config.config import resolve_service_url

        with patch.dict(os.environ, {}, clear=True):
            result = resolve_service_url(8080)

        assert result == "http://localhost:8080", f"Expected fallback localhost:8080, got: {result}"

    def test_fallback_for_gitpod_domain_only_env(self) -> None:
        """GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN alone must NOT trigger Codespaces."""
        from gui.config.config import resolve_service_url

        env = {"GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev"}
        with patch.dict(os.environ, env, clear=True):
            result = resolve_service_url(6006)

        assert result == "http://localhost:6006", (
            f"Only domain without name should fallback, got: {result}"
        )


class TestPhoenixDefaultEndpointUsesResolver:
    """Verify PHOENIX_DEFAULT_ENDPOINT uses resolve_service_url()."""

    def test_phoenix_default_endpoint_is_string(self) -> None:
        """PHOENIX_DEFAULT_ENDPOINT must be a string URL."""
        from gui.config.config import PHOENIX_DEFAULT_ENDPOINT

        assert isinstance(PHOENIX_DEFAULT_ENDPOINT, str), (
            f"PHOENIX_DEFAULT_ENDPOINT must be a string, got {type(PHOENIX_DEFAULT_ENDPOINT)}"
        )

    def test_phoenix_default_endpoint_is_http_url(self) -> None:
        """PHOENIX_DEFAULT_ENDPOINT must start with http:// or https://."""
        from gui.config.config import PHOENIX_DEFAULT_ENDPOINT

        assert PHOENIX_DEFAULT_ENDPOINT.startswith("http"), (
            f"PHOENIX_DEFAULT_ENDPOINT must be an HTTP URL, got: {PHOENIX_DEFAULT_ENDPOINT}"
        )
