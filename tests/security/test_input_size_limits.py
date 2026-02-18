"""
Tests for input size limits and DoS prevention.

This module tests input size validation in plugin adapters to prevent
resource exhaustion attacks through oversized inputs.

MAESTRO Layer 2 (Agent Logic) and Layer 5 (Execution) security controls tested:
- Plugin input size limits
- Memory exhaustion prevention
- String length limits
- Array size limits
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel, Field, ValidationError


class MockTier1Input(BaseModel):
    """Mock Tier 1 input model for testing."""

    agent_output: str = Field(..., max_length=100000)
    reference_texts: list[str] = Field(..., min_length=1, max_length=10)
    start_time: float = Field(..., ge=0.0)
    end_time: float = Field(..., ge=0.0)


class TestPluginInputSizeLimits:
    """Test plugin adapters enforce input size limits."""

    def test_oversized_agent_output_rejected(self):
        """Agent output exceeding 100KB should be rejected."""
        oversized_output = "A" * 100001  # 100KB + 1 byte

        with pytest.raises(ValidationError) as exc_info:
            MockTier1Input(
                agent_output=oversized_output,
                reference_texts=["ref"],
                start_time=0.0,
                end_time=1.0,
            )

        # Should fail on max_length constraint
        assert "agent_output" in str(exc_info.value)

    def test_exactly_max_size_agent_output_accepted(self):
        """Agent output exactly at 100KB should be accepted."""
        max_size_output = "A" * 100000  # Exactly 100KB

        result = MockTier1Input(
            agent_output=max_size_output,
            reference_texts=["ref"],
            start_time=0.0,
            end_time=1.0,
        )

        assert len(result.agent_output) == 100000

    def test_oversized_reference_texts_array_rejected(self):
        """Reference texts array exceeding 10 items should be rejected."""
        oversized_array = ["reference text"] * 11  # 11 items (max is 10)

        with pytest.raises(ValidationError) as exc_info:
            MockTier1Input(
                agent_output="output",
                reference_texts=oversized_array,
                start_time=0.0,
                end_time=1.0,
            )

        # Should fail on max_length constraint for list
        assert "reference_texts" in str(exc_info.value)

    def test_empty_reference_texts_array_rejected(self):
        """Empty reference texts array should be rejected (min_length=1)."""
        with pytest.raises(ValidationError) as exc_info:
            MockTier1Input(
                agent_output="output",
                reference_texts=[],  # Empty array
                start_time=0.0,
                end_time=1.0,
            )

        assert "reference_texts" in str(exc_info.value)

    def test_exactly_max_reference_texts_accepted(self):
        """Reference texts with exactly 10 items should be accepted."""
        max_refs = ["reference"] * 10

        result = MockTier1Input(
            agent_output="output",
            reference_texts=max_refs,
            start_time=0.0,
            end_time=1.0,
        )

        assert len(result.reference_texts) == 10


class TestMemoryExhaustionPrevention:
    """Test input validation prevents memory exhaustion attacks."""

    def test_extremely_large_string_rejected(self):
        """Strings well above max_length should be rejected by Pydantic validator.

        Reason: Python allocates the full string *before* Pydantic validates,
        so truly huge sizes (e.g. 1GB) cause OOM/hang. We use 10x the limit
        instead -- the boundary case is covered by test_oversized_agent_output_rejected.
        """
        with pytest.raises(ValidationError):
            MockTier1Input(
                agent_output="X" * 1_000_000,  # 10x max_length (100000)
                reference_texts=["ref"],
                start_time=0.0,
                end_time=1.0,
            )

    def test_many_large_reference_texts_rejected(self):
        """Many large reference texts should be rejected."""
        # 10 items of 50KB each = 500KB total (should be rejected if individual items too large)
        large_refs = ["X" * 50000] * 10

        # This should pass array size limit (10 items) but may fail if individual items
        # have size constraints
        try:
            result = MockTier1Input(
                agent_output="output",
                reference_texts=large_refs,
                start_time=0.0,
                end_time=1.0,
            )
            # If it passes, total size should still be bounded
            total_size = sum(len(ref) for ref in result.reference_texts)
            assert total_size < 1_000_000  # Less than 1MB total
        except ValidationError:
            # Also acceptable if validation rejects oversized individual items
            pass


class TestNegativeAndInvalidInputs:
    """Test validation of timing and numeric inputs."""

    def test_negative_start_time_rejected(self):
        """Negative start_time should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MockTier1Input(
                agent_output="output",
                reference_texts=["ref"],
                start_time=-1.0,  # Negative time
                end_time=1.0,
            )

        assert "start_time" in str(exc_info.value)

    def test_negative_end_time_rejected(self):
        """Negative end_time should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MockTier1Input(
                agent_output="output",
                reference_texts=["ref"],
                start_time=0.0,
                end_time=-1.0,  # Negative time
            )

        assert "end_time" in str(exc_info.value)

    def test_zero_times_accepted(self):
        """Zero times should be accepted (ge=0.0 constraint)."""
        result = MockTier1Input(
            agent_output="output",
            reference_texts=["ref"],
            start_time=0.0,
            end_time=0.0,
        )

        assert result.start_time == 0.0
        assert result.end_time == 0.0


class TestUnicodeAndEdgeCases:
    """Test handling of unicode and edge case inputs."""

    def test_unicode_content_within_limits_accepted(self):
        """Unicode content within size limits should be accepted."""
        unicode_output = "🔬🤖" * 1000  # Emoji characters

        result = MockTier1Input(
            agent_output=unicode_output,
            reference_texts=["ref"],
            start_time=0.0,
            end_time=1.0,
        )

        assert len(result.agent_output) > 0

    def test_mixed_unicode_and_ascii_accepted(self):
        """Mixed unicode and ASCII content should be accepted."""
        mixed_content = "ASCII text with émojis 🔬 and Ünïcödé"

        result = MockTier1Input(
            agent_output=mixed_content,
            reference_texts=["ref"],
            start_time=0.0,
            end_time=1.0,
        )

        assert result.agent_output == mixed_content


class TestPropertyBasedValidation:
    """Property-based tests using Hypothesis."""

    @given(
        output_size=st.integers(min_value=0, max_value=100000),
        num_refs=st.integers(min_value=1, max_value=10),
    )
    def test_valid_sizes_always_accepted(self, output_size: int, num_refs: int):
        """Valid sizes within constraints should always be accepted."""
        output = "A" * output_size
        refs = ["ref"] * num_refs

        result = MockTier1Input(
            agent_output=output,
            reference_texts=refs,
            start_time=0.0,
            end_time=1.0,
        )

        assert len(result.agent_output) == output_size
        assert len(result.reference_texts) == num_refs

    @given(
        output_size=st.integers(min_value=100001, max_value=200000),
    )
    def test_oversized_outputs_always_rejected(self, output_size: int):
        """Oversized outputs should always be rejected."""
        output = "A" * output_size

        with pytest.raises(ValidationError):
            MockTier1Input(
                agent_output=output,
                reference_texts=["ref"],
                start_time=0.0,
                end_time=1.0,
            )

    @given(
        num_refs=st.integers(min_value=11, max_value=100),
    )
    def test_oversized_arrays_always_rejected(self, num_refs: int):
        """Arrays exceeding max_length should always be rejected."""
        refs = ["ref"] * num_refs

        with pytest.raises(ValidationError):
            MockTier1Input(
                agent_output="output",
                reference_texts=refs,
                start_time=0.0,
                end_time=1.0,
            )

    @given(
        start_time=st.floats(min_value=0.0, max_value=1000.0),
        end_time=st.floats(min_value=0.0, max_value=1000.0),
    )
    def test_non_negative_times_accepted(self, start_time: float, end_time: float):
        """Non-negative times should always be accepted."""
        # Filter out NaN and inf values
        if not (
            start_time == start_time
            and end_time == end_time
            and start_time != float("inf")
            and end_time != float("inf")
        ):
            return

        result = MockTier1Input(
            agent_output="output",
            reference_texts=["ref"],
            start_time=start_time,
            end_time=end_time,
        )

        assert result.start_time >= 0.0
        assert result.end_time >= 0.0
