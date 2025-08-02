"""
Test serialization of peerread models after removing deprecated json_encoders.
"""

import json

from app.data_models.peerread_models import GeneratedReview, ReviewGenerationResult


def test_generated_review_serialization():
    """Test GeneratedReview serializes correctly to JSON."""
    review = GeneratedReview(
        impact=4,
        substance=4,
        appropriateness=4,
        meaningful_comparison=3,
        presentation_format="Oral",
        comments=(
            "Test review with sufficient length to meet validation requirements. "
            "This covers contributions, strengths, weaknesses, technical soundness, "
            "and clarity assessment."
        ),
        soundness_correctness=4,
        originality=3,
        recommendation=4,
        clarity=4,
        reviewer_confidence=4,
    )

    # Test model_dump works
    data = review.model_dump()
    assert data["impact"] == 4
    assert data["presentation_format"] == "Oral"

    # Test JSON serialization
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    assert parsed["impact"] == 4


def test_review_generation_result_serialization():
    """Test ReviewGenerationResult serializes correctly without json_encoders."""
    review = GeneratedReview(
        impact=5,
        substance=4,
        appropriateness=5,
        meaningful_comparison=4,
        presentation_format="Poster",
        comments=(
            "Comprehensive test review covering all required aspects including "
            "technical contributions, methodology strengths, clarity assessment, "
            "and improvement suggestions."
        ),
        soundness_correctness=5,
        originality=4,
        recommendation=4,
        clarity=5,
        reviewer_confidence=4,
    )

    result = ReviewGenerationResult(
        paper_id="test-123",
        review=review,
        timestamp="2025-07-25T19:00:00Z",
        model_info="Test model",
    )

    # Test nested serialization works
    data = result.model_dump()
    assert data["paper_id"] == "test-123"
    assert data["review"]["impact"] == 5
    assert data["review"]["presentation_format"] == "Poster"

    # Test JSON serialization of nested structure
    json_str = json.dumps(data, indent=2)
    parsed = json.loads(json_str)
    assert parsed["review"]["impact"] == 5
    assert parsed["model_info"] == "Test model"


def test_peerread_format_conversion():
    """Test to_peerread_format method still works."""
    review = GeneratedReview(
        impact=3,
        substance=4,
        appropriateness=3,
        meaningful_comparison=4,
        presentation_format="Oral",
        comments=(
            "Testing format conversion with adequate length for validation. "
            "Includes assessment of technical aspects, clarity, and overall "
            "contribution quality."
        ),
        soundness_correctness=4,
        originality=3,
        recommendation=3,
        clarity=4,
        reviewer_confidence=3,
    )

    peerread_format = review.to_peerread_format()
    assert peerread_format["IMPACT"] == "3"
    assert peerread_format["PRESENTATION_FORMAT"] == "Oral"
    assert peerread_format["is_meta_review"] is None
