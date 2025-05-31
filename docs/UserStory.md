# User Story for Agents-eval

## Introduction

Agents-eval is designed to evaluate the effectiveness of open-source agentic AI systems across various use cases. This user story focuses on the perspective of Gez, an AI researcher who aims to assess and improve these systems using Agents-eval.

## User Profile

- **Name:** Gez
- **Role:** AI Researcher
- **Goals:**
  - Evaluate the performance of agentic AI systems.
  - Identify areas for improvement in these systems.
  - Develop and integrate new metrics for evaluation.

## User Story

**As** an AI researcher,
**I want** to use Agents-eval to evaluate the effectiveness of agentic AI systems,
**so that** I can assess their performance across different use cases and improve their capabilities.

### Acceptance Criteria

1. **Evaluation Pipeline:**
   - The system should provide a comprehensive evaluation pipeline that measures core agentic capabilities such as task decomposition, tool integration, adaptability, and overall performance.
   - The pipeline should support multiple agentic AI frameworks (e.g., Pydantic-AI, LangChain).

2. **Metric Development:**
   - The system should allow for the development and integration of new metrics that are agnostic to specific use cases.
   - These metrics should be modular and easily integratable with existing evaluation logic.

3. **CLI and GUI Interactions:**
   - The system should offer both a CLI and a Streamlit GUI for user interaction.
   - The CLI should support streaming output from Pydantic-AI models.
   - The Streamlit GUI should display streamed output and provide an intuitive interface for setting up and running evaluations.

4. **Documentation and Feedback:**
   - The system should include comprehensive documentation for setup, usage, and testing.
   - There should be a feedback loop for users to report issues or suggest improvements.

## Example Scenario

- **Scenario:** Gez wants to evaluate a research agent system using Agents-eval.
- **Steps:**
  1. She sets up the environment using the CLI or devcontainer.
  2. She configures the agent system with the desired models and tools.
  3. She runs the evaluation using the CLI or Streamlit GUI.
  4. She views the results and metrics displayed by the system.
  5. She provides feedback on the system's performance and suggests improvements.

## Benefits

- **Improved Evaluation Capabilities:** Agents-eval provides a structured approach to evaluating agentic AI systems, allowing researchers to focus on improving these systems.
- **Flexibility and Customization:** The system supports multiple frameworks and allows for the development of new metrics, making it adaptable to various research needs.
- **Enhanced User Experience:** The combination of CLI and GUI interfaces offers flexibility in how users interact with the system, catering to different preferences and workflows.
