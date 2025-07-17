# User Story

## Introduction

Agents-eval is designed to evaluate the effectiveness of open-source agentic AI systems across various use cases. This user story focuses on the perspective of an AI researcher who aims to assess and improve these systems using Agents-eval.

## As a user of the Agents-eval project, I want to:

### Goals

- Evaluate and compare different open-source agentic AI systems.
- Assess core capabilities such as task decomposition, tool integration, and adaptability.
- Get use-case agnostic metrics for a comprehensive assessment.

### Steps

1. **Set up the environment:**
   - Use `make setup_prod` for production or `make setup_dev` for development.
   - Configure API keys and variables in `.env.example` and rename t `.env`
2. **Run the evaluation pipeline:**
   - Execute the CLI with `make run_cli` or the GUI with `make run_gui`.
3. **Configure evaluation metrics:**
   - Adjust weights in `src/app/config/config_eval.json`.
4. **Analyze the results:**
   - Review output logs and UI to assess agent performance.

### Expected Outcomes

- Clear metrics for task success, coordination quality, tool efficiency, etc.
- Insights into the strengths and weaknesses of different agentic systems.
- Data-driven assessment of agentic systems across various use cases.

### Acceptance Criteria

1. Evaluation Pipeline:
   - The system should provide a comprehensive evaluation pipeline that measures core agentic capabilities such as task decomposition, tool integration, adaptability, and overall performance.
   - The pipeline should support multiple agentic AI frameworks (e.g., Pydantic-AI, LangChain).
2. Metric Development:
   - The system should allow for the development and integration of new metrics that are agnostic to specific use cases.
   - These metrics should be modular and easily integratable with existing evaluation logic.
3. CLI and GUI Interactions:
   - The system should offer both a CLI and a Streamlit GUI for user interaction.
   - The Streamlit GUI should display output and provide an intuitive interface for setting up and running evaluations.
   - Optional: The CLI should support streaming output from Pydantic-AI models.
4. Documentation and Feedback:
   - The system should include comprehensive documentation for setup, usage, and testing.
   - There should be a feedback loop for users to report issues or suggest improvements.

### Benefits

- Improved Evaluation Capabilities: Agents-eval provides a structured approach to evaluating agentic AI systems, allowing researchers to focus on improving these systems.
- Flexibility and Customization: The system supports multiple frameworks and allows for the development of new metrics, making it adaptable to various research needs.
- Enhanced User Experience: The combination of CLI and GUI interfaces offers flexibility in how users interact with the system, catering to different preferences and workflows.

### Example Scenario

- Scenario: The user wants to evaluate a research agent system using Agents-eval.
- Steps:
   - User sets up the environment using the CLI or devcontainer.
   - User configures the agent system with the desired models and tools.
   - User runs the evaluation using the CLI or Streamlit GUI.
   - User views the results and metrics displayed by the system.
   - User provides feedback on the system's performance and suggests improvements.

### Additional Notes:

- The project is under development, and some features are not fully implemented yet (DRAFT/WIP).
- Use the [CHANGELOG](https://github.com/qte77/Agents-eval/blob/main/CHANGELOG.md) for version history.
- Refer to [AGENTS.md](https://github.com/qte77/Agents-eval/blob/main/AGENTS.md) for agent instructions and architecture overview.
