---
title: Strategy for Maintaining AGENTS.md
description: Guidelines for keeping AGENTS.md synchronized with codebase changes for effective AI agent operation
date: 2025-09-01
category: maintenance
version: 1.0.0
---

This document outlines a strategy to ensure `AGENTS.md` remains synchronized with the state of the codebase, preventing it from becoming outdated. A reliable `AGENTS.md` is critical for the effective and safe operation of AI agents.

The strategy combines process integration, automation, and collaborative habits.

## 1. Process & Workflow Integration

Integrate documentation updates into the core development workflow, making them a required and explicit step.

* **Pull Request (PR) Template Checklist**: Modify the project's PR template to include a mandatory checklist item that forces a review of `AGENTS.md`.

    ```markdown
    - [ ] I have reviewed `AGENTS.md` and confirmed that my changes are reflected (e.g., updated "Requests to Humans," added a "Learned Pattern," or modified a command).
    ```

* **Agent's Responsibility**: The AI agent must treat updating `AGENTS.md` as the final step of any task that resolves an issue listed in the "Requests to Humans" section.

* **Commit Message Convention**: Encourage commit messages to reference `AGENTS.md` if a change addresses something in it. This creates a link between the code change and the documentation update.

    ```bash
    # Example commit message
    git commit -m "fix(agent): resolve import path issue (refs AGENTS.md #request-1)"
    ```

## 2. Automation & Tooling

Build automated checks to catch desynchronization before it gets merged into the main branch.

* **CI/CD Validation Step**: Create a script that runs as part of the `make validate` or CI/CD pipeline to check for potential inconsistencies. This script could:
  * **Check for `FIXME`/`TODO`**: If a new `FIXME` or `TODO` is added to the code, the script could check if a corresponding entry exists in the "Requests to Humans" section of `AGENTS.md`.
  * **Validate Paths**: The script could parse `AGENTS.md` for path variables (e.g., `$DEFAULT_PATHS_MD`) and ensure those files still exist in the project.
  * **Keyword Synchronization**: The script could check if a feature mentioned in a commit (e.g., "streaming") is also noted as a `NotImplementedError` in the code and `AGENTS.md`, flagging it for an update if the feature has been implemented.

## 3. Cultural & Collaborative Habits

Foster a culture where documentation is treated with the same importance as code.

* **Treat `AGENTS.md` as Code**: The most important principle is to treat `AGENTS.md` with the same rigor as application code. It should be reviewed in every PR, and an inaccurate `AGENTS.md` should be considered a bug that can block a merge.

* **Shared Ownership**: The entire team, including any AI agents, is responsible for the file's accuracy. If anyone spots an inconsistency, they should be empowered to fix it immediately.

* **Regular Reviews**: Periodically (e.g., at the start of a sprint or a weekly sync), the team should perform a quick review of the "Requests to Humans" section to ensure it is still relevant and correctly prioritized.
