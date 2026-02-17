"""
Tests for paper selection mode in the GUI App page.

This module tests:
- Dropdown population with available PeerRead papers
- paper_id passthrough from dropdown to _execute_query_background
- Abstract display on paper selection
- PeerReadReview int→str coercion for numeric score fields

Mock strategy:
- PeerReadLoader.load_papers mocked to avoid filesystem access
- Streamlit session state and widgets mocked via patch
- No real LLM or filesystem calls
"""

from unittest.mock import MagicMock, patch

import pytest

from app.data_models.peerread_models import PeerReadPaper, PeerReadReview


class TestPeerReadReviewIntToStrCoercion:
    """Tests for int→str coercion on numeric PeerReadReview score fields.

    Arrange: dict with integer values for score fields
    Act: PeerReadReview.model_validate(data)
    Expected: Fields stored as strings, not ints
    """

    def test_soundness_correctness_int_coerced_to_str(self) -> None:
        """Integer SOUNDNESS_CORRECTNESS is coerced to str."""
        data = {"SOUNDNESS_CORRECTNESS": 3}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.soundness_correctness, str)
        assert review.soundness_correctness == "3"

    def test_originality_int_coerced_to_str(self) -> None:
        """Integer ORIGINALITY is coerced to str."""
        data = {"ORIGINALITY": 4}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.originality, str)
        assert review.originality == "4"

    def test_recommendation_int_coerced_to_str(self) -> None:
        """Integer RECOMMENDATION is coerced to str."""
        data = {"RECOMMENDATION": 5}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.recommendation, str)
        assert review.recommendation == "5"

    def test_clarity_int_coerced_to_str(self) -> None:
        """Integer CLARITY is coerced to str."""
        data = {"CLARITY": 2}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.clarity, str)
        assert review.clarity == "2"

    def test_reviewer_confidence_int_coerced_to_str(self) -> None:
        """Integer REVIEWER_CONFIDENCE is coerced to str."""
        data = {"REVIEWER_CONFIDENCE": 1}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.reviewer_confidence, str)
        assert review.reviewer_confidence == "1"

    def test_impact_int_coerced_to_str(self) -> None:
        """Integer IMPACT is coerced to str."""
        data = {"IMPACT": 3}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.impact, str)
        assert review.impact == "3"

    def test_substance_int_coerced_to_str(self) -> None:
        """Integer SUBSTANCE is coerced to str."""
        data = {"SUBSTANCE": 4}
        review = PeerReadReview.model_validate(data)
        assert isinstance(review.substance, str)
        assert review.substance == "4"

    def test_str_score_unchanged(self) -> None:
        """String score values are accepted without modification."""
        data = {"SOUNDNESS_CORRECTNESS": "3"}
        review = PeerReadReview.model_validate(data)
        assert review.soundness_correctness == "3"

    def test_all_missing_fields_default_to_unknown(self) -> None:
        """All optional fields default to UNKNOWN when missing."""
        review = PeerReadReview.model_validate({})
        assert review.soundness_correctness == "UNKNOWN"
        assert review.originality == "UNKNOWN"
        assert review.recommendation == "UNKNOWN"
        assert review.clarity == "UNKNOWN"
        assert review.reviewer_confidence == "UNKNOWN"
        assert review.impact == "UNKNOWN"
        assert review.substance == "UNKNOWN"


class TestLoadAvailablePapers:
    """Tests for loading available papers for the dropdown.

    Arrange: Mock PeerReadLoader.load_papers to return test papers
    Act: Call the GUI helper that collects available papers
    Expected: Returns list of (paper_id, title, abstract) tuples
    """

    def test_load_available_papers_returns_paper_list(self) -> None:
        """Available papers loaded from PeerReadLoader for configured venues/splits."""
        from gui.pages.run_app import _load_available_papers

        papers = [
            PeerReadPaper(
                paper_id="42",
                title="Attention Is All You Need",
                abstract="Transformers are great.",
                reviews=[],
            ),
        ]

        with patch("gui.pages.run_app.PeerReadLoader") as mock_loader_cls:
            mock_loader = mock_loader_cls.return_value
            mock_loader.load_papers.return_value = papers
            mock_loader.config.venues = ["acl_2017"]
            mock_loader.config.splits = ["train"]

            result = _load_available_papers()

        assert len(result) == 1
        assert result[0].paper_id == "42"
        assert result[0].title == "Attention Is All You Need"

    def test_load_available_papers_returns_empty_on_file_not_found(self) -> None:
        """Returns empty list when dataset not downloaded (FileNotFoundError)."""
        from gui.pages.run_app import _load_available_papers

        with patch("gui.pages.run_app.PeerReadLoader") as mock_loader_cls:
            mock_loader = mock_loader_cls.return_value
            mock_loader.load_papers.side_effect = FileNotFoundError("not found")
            mock_loader.config.venues = ["acl_2017"]
            mock_loader.config.splits = ["train"]

            result = _load_available_papers()

        assert result == []

    def test_load_available_papers_deduplicates_across_venues(self) -> None:
        """Papers loaded from multiple venue/split combos are deduplicated by paper_id."""
        from gui.pages.run_app import _load_available_papers

        paper_a = PeerReadPaper(
            paper_id="1", title="Paper A", abstract="Abstract A.", reviews=[]
        )
        paper_b = PeerReadPaper(
            paper_id="2", title="Paper B", abstract="Abstract B.", reviews=[]
        )

        with patch("gui.pages.run_app.PeerReadLoader") as mock_loader_cls:
            mock_loader = mock_loader_cls.return_value
            # Return paper_a from all venues/splits to test deduplication
            mock_loader.load_papers.side_effect = [[paper_a], [paper_a, paper_b]]
            mock_loader.config.venues = ["acl_2017", "conll_2016"]
            mock_loader.config.splits = ["train"]

            result = _load_available_papers()

        paper_ids = [p.paper_id for p in result]
        assert paper_ids.count("1") == 1, "Paper 1 should appear only once"
        assert "2" in paper_ids


class TestExecuteQueryBackgroundWithPaperId:
    """Tests for paper_id parameter passthrough to main().

    Arrange: Mock main() and session state
    Act: Call _execute_query_background with paper_id set
    Expected: main() called with paper_number=paper_id
    """

    @pytest.mark.asyncio
    async def test_paper_id_passed_to_main(self) -> None:
        """paper_id passed to _execute_query_background is forwarded to main()."""
        from gui.pages.run_app import _execute_query_background

        mock_session = MagicMock()
        mock_session.__setattr__ = MagicMock()

        with (
            patch("gui.pages.run_app.main") as mock_main,
            patch("gui.pages.run_app.st") as mock_st,
            patch("gui.pages.run_app.LogCapture") as mock_capture_cls,
        ):
            mock_st.session_state = {}
            mock_main.return_value = None

            mock_capture = mock_capture_cls.return_value
            mock_capture.attach_to_logger.return_value = 1
            mock_capture.get_logs.return_value = []

            await _execute_query_background(
                query="Review this paper",
                provider="openai",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                paper_id="42",
            )

        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args.kwargs
        assert call_kwargs.get("paper_number") == "42"

    @pytest.mark.asyncio
    async def test_no_paper_id_passes_none_to_main(self) -> None:
        """When paper_id is None, main() is called with paper_number=None."""
        from gui.pages.run_app import _execute_query_background

        with (
            patch("gui.pages.run_app.main") as mock_main,
            patch("gui.pages.run_app.st") as mock_st,
            patch("gui.pages.run_app.LogCapture") as mock_capture_cls,
        ):
            mock_st.session_state = {}
            mock_main.return_value = None

            mock_capture = mock_capture_cls.return_value
            mock_capture.attach_to_logger.return_value = 1
            mock_capture.get_logs.return_value = []

            await _execute_query_background(
                query="What is attention?",
                provider="openai",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                paper_id=None,
            )

        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args.kwargs
        assert call_kwargs.get("paper_number") is None


class TestFormatPaperDropdownOption:
    """Tests for paper dropdown option formatting.

    Arrange: PeerReadPaper with id and title
    Act: Call _format_paper_option(paper)
    Expected: Returns "42 — Attention Is All You Need"
    """

    def test_format_paper_option_includes_id_and_title(self) -> None:
        """Dropdown option displays paper_id and title separated by em dash."""
        from gui.pages.run_app import _format_paper_option

        paper = PeerReadPaper(
            paper_id="42",
            title="Attention Is All You Need",
            abstract="Transformers are great.",
            reviews=[],
        )

        result = _format_paper_option(paper)

        assert result == "42 \u2014 Attention Is All You Need"

    def test_format_paper_option_with_numeric_id(self) -> None:
        """Works with numeric string paper IDs."""
        from gui.pages.run_app import _format_paper_option

        paper = PeerReadPaper(
            paper_id="1105",
            title="Neural Machine Translation",
            abstract="NMT stuff.",
            reviews=[],
        )

        result = _format_paper_option(paper)

        assert "1105" in result
        assert "Neural Machine Translation" in result
