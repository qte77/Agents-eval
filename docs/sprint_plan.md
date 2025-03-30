# Project Plan Outline

## Week 1 starting 2025-03-31: Metric Development and CLI Enhancements

### Milestones

- Metric Development: Implement at least three new metrics for evaluating agentic AI systems.
- CLI Streaming: Enhance the CLI to stream Pydantic-AI output.

### Tasks and Sequence

- [ ] Research and Design New Metrics
  - Task Definition: Conduct literature review and design three new metrics that are agnostic to specific use cases but measure core agentic capabilities.
  - Sequence: Before implementing any code changes.
  - Definition of Done: A detailed document outlining the metrics, their mathematical formulations, and how they will be integrated into the evaluation pipeline.
- [ ] Implement New Metrics
  - Task Definition: Write Python code to implement the new metrics, ensuring they are modular and easily integratable with existing evaluation logic.
  - Sequence: After completing the design document.
  - Definition of Done: Unit tests for each metric pass, and they are successfully integrated into the evaluation pipeline.
- [ ] Enhance CLI for Streaming
  - Task Definition: Modify the CLI to stream Pydantic-AI output using asynchronous functions.
  - Sequence: Concurrently with metric implementation.
  - Definition of Done: The CLI can stream output from Pydantic-AI models without blocking, and tests demonstrate successful streaming.
- [ ] Update Documentation
  - Task Definition: Update PRD.md and README.md to reflect new metrics and CLI enhancements.
  - Sequence: After completing metric implementation and CLI enhancements.
  - Definition of Done: PRD.md includes detailed descriptions of new metrics, and README.md provides instructions on how to use the enhanced CLI.

## Week 2 starting 2025-03-07: Streamlit GUI Enhancements and Testing

### Milestones

- Streamlit GUI Output: Enhance the Streamlit GUI to display streamed output from Pydantic-AI.
- Comprehensive Testing: Perform thorough testing of the entire system with new metrics and GUI enhancements.

### Tasks and Sequence

- [ ] Enhance Streamlit GUI
  - Task Definition: Modify the Streamlit GUI to display the streamed output from Pydantic-AI models.
  - Sequence: Start of Week 2.
  - Definition of Done: The GUI can display streamed output without errors, and user interactions (e.g., selecting models, inputting queries) work as expected.
- [ ] Integrate New Metrics into GUI
  - Task Definition: Ensure the Streamlit GUI can display results from the new metrics.
  - Sequence: After enhancing the GUI for streamed output.
  - Definition of Done: The GUI displays metric results clearly, and users can easily interpret the output.
- [ ] Comprehensive System Testing
  - Task Definition: Perform end-to-end testing of the system, including new metrics and GUI enhancements.
  - Sequence: After integrating new metrics into the GUI.
  - Definition of Done: All tests pass without errors, and the system functions as expected in various scenarios.
- [ ] Finalize Documentation and Deployment
  - Task Definition: Update MkDocs documentation to reflect all changes and deploy it to GitHub Pages.
  - Sequence: After completing system testing.
  - Definition of Done: Documentation is updated, and the latest version is live on GitHub Pages.

## Additional Considerations

- Code Reviews: Schedule regular code reviews to ensure quality and adherence to project standards.
- Feedback Loop: Establish a feedback loop with stakeholders to gather input on the new metrics and GUI enhancements.
