"""
PeerRead dataset data models.

This module defines Pydantic models for representing PeerRead scientific paper
review data structures. These models ensure type safety and validation for
papers, reviews, and evaluation results used in the multi-agent system evaluation.

The models are based on the actual PeerRead dataset structure validated from:
https://raw.githubusercontent.com/allenai/PeerRead/master/data/acl_2017/train/reviews/104.json

This module also includes structured data models for LLM-generated reviews,
ensuring consistency and validation against the PeerRead format.
"""

import re
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

# Coerce numeric score values from raw PeerRead JSON (int) to str.
# Reason: Some PeerRead JSON files store scores as integers (e.g., "SOUNDNESS_CORRECTNESS": 3)
# which fail str validation without coercion.
_ScoreStr = Annotated[str, BeforeValidator(str)]

# Recommendation word → numeric score mapping for weak-structured-output providers (e.g. Cerebras).
_WORD_TO_SCORE: dict[str, int] = {
    "strong accept": 5,
    "strong_accept": 5,
    "accept": 4,
    "borderline accept": 3,
    "borderline reject": 3,
    "borderline": 3,
    "reject": 2,
    "strong reject": 1,
    "strong_reject": 1,
}


def _coerce_score_to_int(v: Any) -> Any:
    """Coerce LLM score values to int for providers that ignore integer schema constraints.

    Reason: Providers like Cerebras with openai_supports_strict_tool_definition=False
    may return natural language descriptions, floats, or word labels instead of integers.
    Extraction priority: word mapping → float rounding → first digit in text → default 3.
    """
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return max(1, min(5, round(v)))
    if isinstance(v, str):
        v_lower = v.lower().strip()
        if v_lower in _WORD_TO_SCORE:
            return _WORD_TO_SCORE[v_lower]
        try:
            return max(1, min(5, round(float(v_lower.split()[0]))))
        except (ValueError, IndexError):
            pass
        if m := re.search(r"\b([1-5])\b", v):
            return int(m.group(1))
        return 3
    return v


def _coerce_presentation_format(v: Any) -> Any:
    """Coerce presentation format to Literal['Poster', 'Oral'].

    Reason: Same provider compliance issue — model may return a sentence describing
    the format instead of the exact literal value.
    """
    if isinstance(v, str) and v not in ("Poster", "Oral"):
        return "Oral" if "oral" in v.lower() else "Poster"
    return v


_ScoreInt = Annotated[int, BeforeValidator(_coerce_score_to_int)]
_PresentationFormatLiteral = Annotated[
    Literal["Poster", "Oral"], BeforeValidator(_coerce_presentation_format)
]


class PeerReadReview(BaseModel):
    """Individual peer review from PeerRead dataset.

    Note: Some PeerRead papers (e.g., 304-308, 330) lack optional fields.
    Defaults to "UNKNOWN" for missing review criteria fields.

    Accepts both PeerRead uppercase keys (IMPACT) and model lowercase keys
    (impact) via populate_by_name with aliases. Numeric score fields are
    coerced to str to handle raw PeerRead JSON integer values.
    """

    model_config = ConfigDict(populate_by_name=True)

    impact: _ScoreStr = Field(
        default="UNKNOWN", validation_alias="IMPACT", description="Impact score (1-5)"
    )
    substance: _ScoreStr = Field(
        default="UNKNOWN", validation_alias="SUBSTANCE", description="Substance score (1-5)"
    )
    appropriateness: _ScoreStr = Field(
        default="UNKNOWN",
        validation_alias="APPROPRIATENESS",
        description="Appropriateness score (1-5)",
    )
    meaningful_comparison: _ScoreStr = Field(
        default="UNKNOWN",
        validation_alias="MEANINGFUL_COMPARISON",
        description="Meaningful comparison score (1-5)",
    )
    presentation_format: str = Field(
        default="Poster",
        validation_alias="PRESENTATION_FORMAT",
        description="Presentation format (Poster/Oral)",
    )
    comments: str = Field(default="", description="Detailed review comments")
    soundness_correctness: _ScoreStr = Field(
        default="UNKNOWN",
        validation_alias="SOUNDNESS_CORRECTNESS",
        description="Soundness/correctness score (1-5)",
    )
    originality: _ScoreStr = Field(
        default="UNKNOWN", validation_alias="ORIGINALITY", description="Originality score (1-5)"
    )
    recommendation: _ScoreStr = Field(
        default="UNKNOWN",
        validation_alias="RECOMMENDATION",
        description="Overall recommendation score (1-5)",
    )
    clarity: _ScoreStr = Field(
        default="UNKNOWN", validation_alias="CLARITY", description="Clarity score (1-5)"
    )
    reviewer_confidence: _ScoreStr = Field(
        default="UNKNOWN",
        validation_alias="REVIEWER_CONFIDENCE",
        description="Reviewer confidence score (1-5)",
    )
    is_meta_review: bool | None = Field(default=None, description="Whether this is a meta review")

    def is_compliant(self) -> bool:
        """Check if all score fields are populated (not UNKNOWN).

        A review is compliant when every field that defaults to UNKNOWN
        has been populated with an actual value from the raw JSON.

        Returns:
            True if all score fields have non-UNKNOWN values.
        """
        # Reason: Derive dynamically from model_fields to stay in sync with field definitions.
        return all(
            getattr(self, name) != "UNKNOWN"
            for name, info in PeerReadReview.model_fields.items()
            if info.default == "UNKNOWN"
        )


class PeerReadPaper(BaseModel):
    """Scientific paper from PeerRead dataset."""

    paper_id: str = Field(description="Unique paper identifier")
    title: str = Field(description="Paper title")
    abstract: str = Field(description="Paper abstract")
    reviews: list[PeerReadReview] = Field(description="Peer reviews for this paper")
    review_histories: list[str] = Field(
        default_factory=list, description="Paper revision histories"
    )


class DownloadResult(BaseModel):
    """Result of dataset download operation."""

    success: bool = Field(description="Whether download was successful")
    cache_path: str = Field(description="Path to cached data")
    papers_downloaded: int = Field(default=0, description="Number of papers downloaded")
    error_message: str | None = Field(default=None, description="Error message if download failed")


class GeneratedReview(BaseModel):
    """
    Structured data model for LLM-generated reviews.

    This model enforces the PeerRead review format and ensures
    all required fields are present with proper validation.
    """

    impact: _ScoreInt = Field(
        ..., ge=1, le=5, description="Impact rating (1=minimal, 5=high impact)"
    )

    substance: _ScoreInt = Field(
        ..., ge=1, le=5, description="Substance/depth rating (1=shallow, 5=substantial)"
    )

    appropriateness: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Venue appropriateness rating (1=inappropriate, 5=appropriate)",
    )

    meaningful_comparison: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Related work comparison rating (1=poor, 5=excellent)",
    )

    presentation_format: _PresentationFormatLiteral = Field(
        ..., description="Recommended presentation format"
    )

    comments: str = Field(
        ...,
        min_length=100,
        description="Detailed review comments covering contributions, strengths, "
        "weaknesses, technical soundness, clarity, and suggestions",
    )

    soundness_correctness: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Technical soundness rating (1=many errors, 5=very sound)",
    )

    originality: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Originality rating (1=not original, 5=highly original)",
    )

    recommendation: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description=(
            "Overall recommendation (1=strong reject, 2=reject, 3=borderline, "
            "4=accept, 5=strong accept)"
        ),
    )

    clarity: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Presentation clarity rating (1=very unclear, 5=very clear)",
    )

    reviewer_confidence: _ScoreInt = Field(
        ...,
        ge=1,
        le=5,
        description="Reviewer confidence rating (1=low confidence, 5=high confidence)",
    )

    @field_validator("comments")
    def validate_comments_structure(cls, v: str) -> str:  # noqa: N805
        """Ensure comments contain key review sections."""
        required_sections = [
            "contributions",
            "strengths",
            "weaknesses",
            "technical",
            "clarity",
        ]

        v_lower = v.lower()
        missing_sections = [section for section in required_sections if section not in v_lower]

        if missing_sections:
            # Just warn but don't fail - LLM might use different wording
            pass

        return v

    def to_peerread_format(self) -> dict[str, str | None]:
        """Convert to PeerRead dataset format for compatibility."""
        return {
            "IMPACT": str(self.impact),
            "SUBSTANCE": str(self.substance),
            "APPROPRIATENESS": str(self.appropriateness),
            "MEANINGFUL_COMPARISON": str(self.meaningful_comparison),
            "PRESENTATION_FORMAT": self.presentation_format,
            "comments": self.comments,
            "SOUNDNESS_CORRECTNESS": str(self.soundness_correctness),
            "ORIGINALITY": str(self.originality),
            "RECOMMENDATION": str(self.recommendation),
            "CLARITY": str(self.clarity),
            "REVIEWER_CONFIDENCE": str(self.reviewer_confidence),
            "is_meta_review": None,
        }


class ReviewGenerationResult(BaseModel):
    """
    Complete result from the review generation process.

    Contains the structured review along with metadata.
    """

    paper_id: str = Field(..., description=("The unique paper identifier provided by PeerRead"))
    review: GeneratedReview = Field(..., description="The structured review povided by LLM")
    timestamp: str = Field(..., description="Generation timestamp in ISO format")
    model_info: str = Field(
        ...,
        description=("Information about the generating model: your model name, version, etc."),
    )
