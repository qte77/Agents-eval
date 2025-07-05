# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Guiding Principles

- Changelogs are for humans, not machines.
- There should be an entry for every single version.
- The same types of changes should be grouped.
- Versions and sections should be linkable.
- The latest version comes first.
- The release date of each version is displayed.
- Mention whether you follow Semantic Versioning.

## Types of changes

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [Unreleased]

## [1.1.0] - 2025-07-05

### Added

- Makefile command and devcontainer.json for claude code usage

### Changed

- Moved streamlit_gui and examples to /src
- Moved app to /src/app

## [1.0.0] - 2025-03-18

### 2025-03-18

- refactor(agent,streamlit): Convert main and run_manager functions again to async for streamli output
- fix(prompts): Update system prompts for manager,researcher and synthesiser roles to remove complexity
- chore(workflows): Update action versions in GitHub workflows for consistency
- chore(workflows): Update action versions for deploy docs to pgh-pages
- docs(deps): Add documentation dependencies for MkDocs and related plugins to pyproject.toml

### 2025-03-17

- feat(main,agent): refactor entry point to support async execution and enhance login handling
- feat(cli,login,log): refactor entry point to integrate Typer, enhance logging, added login every run
- feat(streamlit): replace load_config with load_app_config, enhance sidebar rendering, and improve output rendering with type support
- feat(streamlit): enhance render_output function with detailed docstring and improve query handling in run_app
- feat(streamlit): enhance render_output function with additional info parameter and improve output handling in run_app
- feat(streamlit,app): add Typer dependency, update main entry point for async execution, add streamlit provider input
- feat(agent): update configuration and improve agent system setup with enhanced error handling and new environment variables
- feat(config,login,catch): add inference settings with usage limits and result retries, enhance login function to initialize environment and handle exceptions, comment out raise in error handling context to prevent unintended crashes
- feat(login,catch): integrate logfire configuration in login function and improve error handling context

### 2025-03-16

- feta(devconatiner): Refactor devcontainer setup: remove old configurations and add new setup targets for development and Ollama
- feat(devcontainer): Changed from vscode to astral-sh devcontainer
- feat(devcontainer): Changed to vscode container, added postcreatecommand make setup_env
- feat(devcontainer): restructure environment setup with new devcontainer configurations
- feat(devcontainer): update environment names for clarity in devcontainer configurations
- refactor(agent): Added AgentConfig class for better agent configuration management, Refactored main function for streamlined agent initialization.
- feat(config,agents): Update model providers and enhance configuration management, examples: Added new model providers: Gemini and OpenRouter, src: Enabled streaming responses in the agent system
- chore: Remove unused prompt files, update configuration, and enhance logging setup
- refactor(exception,logfire): Enhance error handling and update model configurations in agent system

### 2025-03-14

- feat(scalene): Add profiling support and update dependencies
- refactor(Makefile): Improve target descriptions and organization

### 2025-03-13

- refactor(API,except): .env.example, add OpenRouter configuration, enhance error handling in run_simple_agent_system.py, and update ModelConfig to allow optional API key.
- feat(streamlit): add Streamlit app structure with header, footer, sidebar, and main content components
- feat(streamlit): enhance Streamlit app with detailed docstrings, improved header/footer, and refined main content layout
- feat(makefile,streamlit): update Makefile commands for CLI and GUI execution, and modify README for usage instructions, add streamlit config.toml
- feat(streamlit): restructure Streamlit app by removing unused components, adding new header, footer, sidebar, and output components, and updating configuration settings
- chore: replace app entrypoint with main, remove unused tools and tests, and update makefile for linting and type checking
- chore: Enhance makefile with coverage and help commands, update mkdocs.yaml and pyproject.toml for improved project structure and documentation
- test: Update makefile for coverage reporting, modify pyproject.toml to include pytest-cov, and adjust dependency settings
- test: Add coverage support with pytest-cov and update makefile for coverage reporting
- test: makefile for coverage reporting, update dependencies in pyproject.toml for improved testing and coverage support
- chore: Remove redundant help command from makefile
- refactor(agent,async): Refactor agent tests to use async fixtures and update verification methods for async results
- fix(Dockerfile): Remove unnecessary user creation and pip install commands from Dockerfile
- feat(agent): Update dependencies and add new example structures; remove obsolete files
- chore(structure): simplified agents.py
- fix(pyproject): Replace pydantic-ai with pydantic-ai-slim and update dependencies
- feat(examples): add new examples and data models; update configuration structure
- feat(agent): update dependencies, enhance examples, and introduce new data models for research and analysis agents
- feat(examples): enhance prompts structure and refactor research agent integration
- feat(examples): improve documentation and enhance error handling in agent examples
- feat(agent): Added data models and configuration for research and analysis agents, Added System C4 plantuml
- feat(weave,dependencies): update dependencies and integrate Weave for enhanced functionality in the agent system
- feat(agent): initialize agentops with API key and default tags for enhanced agent functionality
- feat(agent): integrate logfire for logging and configure initial logging settings
- feat(agent): adjust usage limits for ollama provider to enhance performance
- feat(agent): refine system prompts and enhance data model structure for improved agent interactions
- feat(agent): update system prompts for improved clarity and accuracy; add example environment configuration
- feat(agent): enhance agent system with synthesiser functionality and update prompts for improved coordination
- feat(agent): add Grok and Gemini API configurations; initialize logging and agent operations
- feat(agent): improve documentation and refactor model configuration handling for agent system
- feat(agent): update environment configuration, enhance logging, and refine agent management functionality
- feat(agent): refactor login handling, update model retrieval, and enhance agent configuration

## [0.0.2] - 2025-01-20

### Added

- PRD.md
- C4 architecture diagrams: system context, code
- tests: basic agent evals, config.json

### Changed

- make recipes

## [0.0.1] - 2025-01-20

### Added

- Makefile: setup, test, ruff
- devcontainer: python only, w/o Jetbrains clutter from default devcontainer
- ollama: server and model download successful
- agent: tools use full run red
- pytest: e2e runm final result red
- Readme: basic project info
- pyproject.toml
