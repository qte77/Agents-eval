"""Configuration models for MAS composition sweep.

This module defines Pydantic models for sweep configuration including
agent composition definitions and convenience functions for generating
standard composition sets.
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from app.config.config_app import CHAT_DEFAULT_PROVIDER


class AgentComposition(BaseModel):
    """Configuration for a specific agent composition.

    Defines which agents are included in a multi-agent system composition.
    Each toggle determines whether the corresponding agent is instantiated.
    """

    include_researcher: bool = False
    include_analyst: bool = False
    include_synthesiser: bool = False

    def get_name(self) -> str:
        """Generate a readable name for this composition.

        Returns:
            str: A human-readable name describing the active agents.

        Example:
            >>> comp = AgentComposition(include_researcher=True, include_analyst=False)
            >>> comp.get_name()
            'researcher'
        """
        active_agents: list[str] = []
        if self.include_researcher:
            active_agents.append("researcher")
        if self.include_analyst:
            active_agents.append("analyst")
        if self.include_synthesiser:
            active_agents.append("synthesiser")

        if not active_agents:
            return "manager-only"

        return "+".join(active_agents)


class SweepConfig(BaseModel):
    """Configuration for a composition sweep run.

    Defines the sweep parameters including which compositions to test,
    how many repetitions per composition, which papers to evaluate,
    and which execution engine to use (MAS pipeline or Claude Code headless).
    """

    compositions: list[AgentComposition] = Field(
        ..., description="List of agent compositions to test", min_length=1
    )
    repetitions: int = Field(..., description="Number of repetitions per composition", ge=1)
    paper_numbers: list[int] = Field(..., description="List of paper IDs to evaluate", min_length=1)
    output_dir: Path = Field(..., description="Directory for sweep results")

    chat_provider: str = Field(
        default=CHAT_DEFAULT_PROVIDER, description="LLM provider to use for evaluations"
    )

    engine: str = Field(
        default="mas",
        description="Execution engine: 'mas' for MAS pipeline, 'cc' for Claude Code headless",
    )

    cc_artifact_dirs: list[Path] | None = Field(
        default=None,
        description="Pre-collected CC artifact directories (skips re-running CC)",
    )

    @field_validator("compositions")
    @classmethod
    def validate_compositions_not_empty(cls, v: list[AgentComposition]) -> list[AgentComposition]:
        """Validate that compositions list is not empty.

        Args:
            v: The compositions list to validate.

        Returns:
            The validated compositions list.

        Raises:
            ValueError: If compositions list is empty.
        """
        if not v:
            raise ValueError("Compositions list cannot be empty")
        return v

    @field_validator("repetitions")
    @classmethod
    def validate_repetitions_positive(cls, v: int) -> int:
        """Validate that repetitions is positive.

        Args:
            v: The repetitions value to validate.

        Returns:
            The validated repetitions value.

        Raises:
            ValueError: If repetitions is zero or negative.
        """
        if v <= 0:
            raise ValueError("Repetitions must be positive")
        return v

    @field_validator("paper_numbers")
    @classmethod
    def validate_paper_numbers_not_empty(cls, v: list[int]) -> list[int]:
        """Validate that paper_numbers list is not empty.

        Args:
            v: The paper_numbers list to validate.

        Returns:
            The validated paper_numbers list.

        Raises:
            ValueError: If paper_numbers list is empty.
        """
        if not v:
            raise ValueError("Paper numbers list cannot be empty")
        return v


def generate_all_compositions() -> list[AgentComposition]:
    """Generate all 2^3 = 8 possible agent compositions.

    This convenience function generates the full Cartesian product of all
    agent toggle combinations.

    Returns:
        list[AgentComposition]: List of 8 unique agent compositions.

    Example:
        >>> compositions = generate_all_compositions()
        >>> len(compositions)
        8
        >>> any(c.include_researcher and c.include_analyst for c in compositions)
        True
    """
    compositions = []
    for researcher in [False, True]:
        for analyst in [False, True]:
            for synthesiser in [False, True]:
                compositions.append(
                    AgentComposition(
                        include_researcher=researcher,
                        include_analyst=analyst,
                        include_synthesiser=synthesiser,
                    )
                )
    return compositions
