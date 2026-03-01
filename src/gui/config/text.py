# S8-F8.1: correct onboarding order — Settings before App
HOME_INFO = "Start with 'Settings' to configure your provider, then select 'App' to run queries"
HOME_HEADER = "Welcome to the Multi-Agent Research System"
HOME_DESCRIPTION = """
This system allows you to:

- Run research queries using multiple specialized agents
- Configure agent settings and prompts
- View detailed results from your research

Use the sidebar to navigate between different sections of the application.
"""
PAGE_TITLE = "MAS Eval"
PROMPTS_WARNING = "No prompts found. Using default prompts."
PROMPTS_HEADER = "Agent Prompts"
RUN_APP_HEADER = "Run Research App"
# S8-F8.1: domain-specific example placeholder for better UX
RUN_APP_QUERY_PLACEHOLDER = "e.g., Evaluate this paper's methodology and novelty"
RUN_APP_PROVIDER_PLACEHOLDER = "Provider?"
RUN_APP_BUTTON = "Run Query"
RUN_APP_OUTPUT_PLACEHOLDER = "Run the agent to see results here"
RUN_APP_QUERY_WARNING = "Please enter a query"
RUN_APP_QUERY_RUN_INFO = "Running query: "
SETTINGS_HEADER = "Settings"
SETTINGS_PROVIDER_LABEL = "Select Provider"
SETTINGS_PROVIDER_PLACEHOLDER = "Select Provider"
SETTINGS_ADD_PROVIDER = "Add New Provider"
SETTINGS_API_KEY_LABEL = "API Key"
OUTPUT_SUBHEADER = "Output"
# STORY-009: Evaluation page constants
EVALUATION_HEADER = "Evaluation Results"
EVALUATION_OVERALL_RESULTS_SUBHEADER = "Overall Results"
EVALUATION_TIER_SCORES_SUBHEADER = "Tier Scores"
EVALUATION_METRICS_COMPARISON_SUBHEADER = "Graph Metrics vs Text Metrics Comparison"
# STORY-009: Agent graph page constants
AGENT_GRAPH_HEADER = "\U0001f578\ufe0f Agent Interaction Graph"
AGENT_GRAPH_NETWORK_SUBHEADER = "Interactive Agent Network Visualization"
# STORY-009: Run app label constants
DEBUG_LOG_LABEL = "Debug Log"
GENERATE_REPORT_LABEL = "Generate Report"
DOWNLOAD_REPORT_LABEL = "Download Report"

ONBOARDING_STEPS = [
    {
        "title": "1. Configure Provider",
        "description": "Go to **Settings** to set up your LLM provider and API key.",
    },
    {
        "title": "2. Download Dataset",
        "description": "Run `make setup_dataset_sample` to fetch the PeerRead dataset.",
    },
    {
        "title": "3. Run a Query",
        "description": "Navigate to **App** to evaluate a paper or run a custom query.",
    },
]
