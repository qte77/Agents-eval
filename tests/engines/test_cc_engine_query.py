"""Tests for build_cc_query() — CC engine empty query fix (STORY-006).

Validates:
- build_cc_query returns non-empty prompt when paper_id provided
- Default prompt template matches app.py:_prepare_query() format
- Teams mode prepends "Use a team of agents." to generated prompt
- Explicit query takes precedence over auto-generated prompt
- ValueError raised when both query and paper_id are empty
- DRY: both build_cc_query and _prepare_query use DEFAULT_REVIEW_PROMPT_TEMPLATE
"""

import pytest


class TestBuildCcQuery:
    """Tests for build_cc_query()."""

    def test_paper_id_generates_default_prompt(self):
        """When query is empty and paper_id provided, returns generated prompt."""
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="", paper_id="1105.1072")
        assert result == "Generate a structured peer review for paper '1105.1072'."

    def test_explicit_query_takes_precedence(self):
        """When both query and paper_id provided, explicit query wins."""
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="My custom query", paper_id="1105.1072")
        assert result == "My custom query"

    def test_teams_mode_prepends_team_instruction(self):
        """When cc_teams=True and no explicit query, prepends team instruction."""
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="", paper_id="1105.1072", cc_teams=True)
        assert result == (
            "Use a team of agents. Generate a structured peer review for paper '1105.1072'."
        )

    def test_teams_mode_with_explicit_query_no_prepend(self):
        """When cc_teams=True but explicit query provided, no team prepend."""
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="My query", paper_id="1105.1072", cc_teams=True)
        assert result == "My query"

    def test_empty_query_and_no_paper_id_raises(self):
        """When both query and paper_id are empty/None, raises ValueError."""
        from app.engines.cc_engine import build_cc_query

        with pytest.raises(ValueError, match="query.*paper_id"):
            build_cc_query(query="", paper_id=None)

    def test_empty_query_none_paper_id_raises(self):
        """When query is empty string and paper_id is None, raises ValueError."""
        from app.engines.cc_engine import build_cc_query

        with pytest.raises(ValueError):
            build_cc_query(query="")

    def test_query_only_no_paper_id(self):
        """When query provided but no paper_id, returns query as-is."""
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="Summarize this paper", paper_id=None)
        assert result == "Summarize this paper"


class TestDefaultReviewPromptTemplate:
    """Tests for DEFAULT_REVIEW_PROMPT_TEMPLATE constant (DRY)."""

    def test_constant_exists_in_config(self):
        """DEFAULT_REVIEW_PROMPT_TEMPLATE is defined in config_app.py."""
        from app.config.config_app import DEFAULT_REVIEW_PROMPT_TEMPLATE

        assert "paper_id" in DEFAULT_REVIEW_PROMPT_TEMPLATE
        assert "{paper_id}" in DEFAULT_REVIEW_PROMPT_TEMPLATE

    def test_build_cc_query_uses_template(self):
        """build_cc_query uses DEFAULT_REVIEW_PROMPT_TEMPLATE for generated prompts."""
        from app.config.config_app import DEFAULT_REVIEW_PROMPT_TEMPLATE
        from app.engines.cc_engine import build_cc_query

        result = build_cc_query(query="", paper_id="test123")
        expected = DEFAULT_REVIEW_PROMPT_TEMPLATE.format(paper_id="test123")
        assert result == expected
