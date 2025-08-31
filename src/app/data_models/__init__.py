"""
Data models and schemas for the multi-agent evaluation system.

This module defines Pydantic data models that serve as contracts throughout
the evaluation system. It provides structured data validation, serialization,
and type safety for all data flowing between components.

Key model categories:
- App models: Core application configuration and environment settings
- Evaluation models: Structured evaluation results and metrics
- Agent models: Data structures for agent inputs, outputs, and coordination

All models follow Pydantic best practices for validation and serialization,
ensuring data integrity across the entire evaluation pipeline.
"""
