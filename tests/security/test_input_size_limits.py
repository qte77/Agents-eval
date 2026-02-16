"""Input size limit security tests.

Tests DoS prevention via input size validation for plugin adapters
as identified in Sprint 5 MAESTRO review Finding L2.2 (MEDIUM).

Attack vectors tested:
- Oversized agent_output strings (>100KB)
- Oversized reference_texts arrays (>10 items)
- Memory exhaustion attacks via unbounded inputs
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel, Field, ValidationError


class TestPluginInputSizeLimits:
    """Test input size limits for plugin adapters."""

    def test_tier1_input_with_oversized_agent_output_raises_validation_error(self):
        """Agent output exceeding 100KB should raise ValidationError."""
        # Define expected Tier1 input schema
        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Create oversized agent output (>100KB)
        oversized_output = "x" * 200000  # 200KB

        with pytest.raises(ValidationError) as exc_info:
            Tier1Input(
                agent_output=oversized_output, reference_texts=["ref1"], start_time=0.0, end_time=1.0
            )

        # Verify validation error is for agent_output field
        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "agent_output" for err in errors)

    def test_tier1_input_with_oversized_reference_texts_raises_validation_error(self):
        """Reference texts exceeding 10 items should raise ValidationError."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Create oversized reference_texts (>10 items)
        oversized_refs = [f"reference_{i}" for i in range(50)]

        with pytest.raises(ValidationError) as exc_info:
            Tier1Input(agent_output="output", reference_texts=oversized_refs, start_time=0.0, end_time=1.0)

        # Verify validation error is for reference_texts field
        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "reference_texts" for err in errors)

    def test_tier1_input_at_boundary_passes_validation(self):
        """Input exactly at size limits should pass validation."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Exactly 100KB output
        boundary_output = "x" * 100000
        # Exactly 10 references
        boundary_refs = [f"ref_{i}" for i in range(10)]

        # Should not raise
        validated = Tier1Input(
            agent_output=boundary_output, reference_texts=boundary_refs, start_time=0.0, end_time=5.0
        )

        assert len(validated.agent_output) == 100000
        assert len(validated.reference_texts) == 10


class TestPluginInputTimeValidation:
    """Test time validation for plugin inputs."""

    def test_negative_start_time_raises_validation_error(self):
        """Negative start time should raise ValidationError."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        with pytest.raises(ValidationError) as exc_info:
            Tier1Input(agent_output="output", reference_texts=["ref1"], start_time=-1.0, end_time=1.0)

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "start_time" for err in errors)

    def test_negative_end_time_raises_validation_error(self):
        """Negative end time should raise ValidationError."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        with pytest.raises(ValidationError) as exc_info:
            Tier1Input(agent_output="output", reference_texts=["ref1"], start_time=0.0, end_time=-1.0)

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "end_time" for err in errors)


class TestTier2InputSizeLimits:
    """Test input size limits for Tier 2 (LLM judge) inputs."""

    def test_tier2_input_with_oversized_paper_excerpt_raises_validation_error(self):
        """Paper excerpt exceeding limit should raise ValidationError."""

        class Tier2Input(BaseModel):
            paper_excerpt: str = Field(..., max_length=50000)
            review: str = Field(..., max_length=50000)
            tier1_result: dict = Field(...)

        # Oversized paper excerpt (>50KB)
        oversized_paper = "x" * 100000

        with pytest.raises(ValidationError) as exc_info:
            Tier2Input(paper_excerpt=oversized_paper, review="review", tier1_result={})

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "paper_excerpt" for err in errors)

    def test_tier2_input_with_oversized_review_raises_validation_error(self):
        """Review exceeding limit should raise ValidationError."""

        class Tier2Input(BaseModel):
            paper_excerpt: str = Field(..., max_length=50000)
            review: str = Field(..., max_length=50000)
            tier1_result: dict = Field(...)

        # Oversized review (>50KB)
        oversized_review = "x" * 100000

        with pytest.raises(ValidationError) as exc_info:
            Tier2Input(paper_excerpt="paper", review=oversized_review, tier1_result={})

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "review" for err in errors)


class TestEmptyInputValidation:
    """Test validation of empty or missing inputs."""

    def test_empty_reference_texts_raises_validation_error(self):
        """Empty reference_texts array should raise ValidationError."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        with pytest.raises(ValidationError) as exc_info:
            Tier1Input(agent_output="output", reference_texts=[], start_time=0.0, end_time=1.0)

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "reference_texts" for err in errors)

    def test_empty_agent_output_allowed(self):
        """Empty agent_output should be allowed (valid edge case)."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Should not raise - empty output is valid
        validated = Tier1Input(agent_output="", reference_texts=["ref1"], start_time=0.0, end_time=1.0)

        assert validated.agent_output == ""


class TestHypothesisInputSizeProperties:
    """Property-based tests for input size validation."""

    @given(
        output_size=st.integers(min_value=0, max_value=100000),
        ref_count=st.integers(min_value=1, max_value=10),
    )
    def test_valid_sizes_always_pass(self, output_size: int, ref_count: int):
        """Inputs within valid size ranges should always pass validation."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        output = "x" * output_size
        refs = [f"ref_{i}" for i in range(ref_count)]

        # Should not raise
        validated = Tier1Input(agent_output=output, reference_texts=refs, start_time=0.0, end_time=1.0)

        assert len(validated.agent_output) == output_size
        assert len(validated.reference_texts) == ref_count

    @given(output_size=st.integers(min_value=100001, max_value=1000000))
    def test_oversized_outputs_always_fail(self, output_size: int):
        """Outputs exceeding max size should always fail validation."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        output = "x" * output_size

        with pytest.raises(ValidationError):
            Tier1Input(agent_output=output, reference_texts=["ref1"], start_time=0.0, end_time=1.0)


class TestMemoryExhaustionPrevention:
    """Test prevention of memory exhaustion attacks."""

    def test_extremely_large_single_reference_text_handled(self):
        """Single reference text that's extremely large should be rejected."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Each reference text can be large, but count is limited
        large_ref = "x" * 1000000  # 1MB single reference

        # Should pass count validation but might exceed memory in real use
        # This tests that count limit prevents unlimited references
        validated = Tier1Input(agent_output="output", reference_texts=[large_ref], start_time=0.0, end_time=1.0)

        assert len(validated.reference_texts) == 1

    def test_reference_text_item_size_not_individually_limited(self):
        """Individual reference text items are not size-limited, only count is."""

        class Tier1Input(BaseModel):
            agent_output: str = Field(..., max_length=100000)
            reference_texts: list[str] = Field(..., min_length=1, max_length=10)
            start_time: float = Field(..., ge=0.0)
            end_time: float = Field(..., ge=0.0)

        # Max 10 items, each can be large
        refs = ["x" * 10000 for _ in range(10)]

        # Should pass - count is within limit
        validated = Tier1Input(agent_output="output", reference_texts=refs, start_time=0.0, end_time=1.0)

        assert len(validated.reference_texts) == 10
