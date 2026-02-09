"""
Common data models for the Agents-eval application.

This module provides shared Pydantic base models and common data structures
used across the application.
"""

from pydantic import BaseModel, ConfigDict


class CommonBaseModel(BaseModel):
    """
    Common base model with shared configuration for all Pydantic models.

    Provides consistent configuration across all data models in the application
    including validation behavior and serialization settings.
    """

    model_config = ConfigDict(
        # Enable validation on assignment
        validate_assignment=True,
        # Allow arbitrary types for complex fields
        arbitrary_types_allowed=False,
        # Use enum values instead of enum instances in JSON
        use_enum_values=True,
    )
