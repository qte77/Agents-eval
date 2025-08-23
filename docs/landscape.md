# AI Agent Evaluation Landscape

This document provides a comprehensive overview of the AI agent evaluation ecosystem, including frameworks, tools, datasets, and benchmarks relevant to the Agents-eval project.

## Agentic System Frameworks

- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [restack](https://www.restack.io/)
- [smolAgents](https://github.com/huggingface/smolagents)
- [AutoGen](https://github.com/microsoft/autogen)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [Langchain](https://github.com/langchain-ai/langchain)
- [Langflow](https://github.com/langflow-ai/langflow)

## Agent-builder

- [Archon](https://github.com/coleam00/Archon)
- [Agentstack](https://github.com/AgentOps-AI/AgentStack)

## Evaluation

### Focusing on agentic systems

- [AgentNeo](https://github.com/raga-ai-hub/agentneo)
- [AutoGenBench](https://github.com/microsoft/autogen/blob/0.2/samples/tools/autogenbench)
- [Langchain AgentEvals](https://github.com/langchain-ai/agentevals), trajectory or LLM-as-a-judge
- [Mosaic AI Agent Evaluation](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
- [RagaAI-Catalyst](https://github.com/raga-ai-hub/RagaAI-Catalyst)
- [AgentBench](https://github.com/THUDM/AgentBench)

### RAG oriented

- [RAGAs](https://github.com/explodinggradients/ragas)

### LLM apps

- [DeepEval](https://github.com/confident-ai/deepeval)
- [Langchain OpenEvals](https://github.com/langchain-ai/openevals)
- [MLFlow LLM Evaluate](https://mlflow.org/docs/latest/llms/llcheckm-evaluate/index.html)
- [DeepEval (DeepSeek)]( github.com/confident-ai/deepeval)

## Observation, Monitoring, Tracing

- [AgentOps - Agency](https://www.agentops.ai/)
- [arize](https://arize.com/)
- [Langtrace](https://www.langtrace.ai/)
- [LangSmith - Langchain](https://www.langchain.com/langsmith)
- [Weave - Weights & Biases](https://wandb.ai/site/weave/)
- [Pydantic- Logfire](https://pydantic.dev/logfire)
- [comet Opik](https://github.com/comet-ml/opik)
- [Langfuse](https://github.com/langfuse/langfuse)
- [helicone](https://github.com/Helicone/helicone)
- [langwatch](https://github.com/langwatch/langwatch)

## Datasets

- [awesome-reasoning - Collection of datasets](https://github.com/neurallambda/awesome-reasoning)

### Scientific

- [SWIF2T](https://arxiv.org/abs/2405.20477), Automated Focused Feedback Generation for Scientific Writing Assistance, 2024, 300 peer reviews citing weaknesses in scientific papers and conduct human evaluation
- [PeerRead](https://github.com/allenai/PeerRead), A Dataset of Peer Reviews (PeerRead): Collection, Insights and NLP Applications, 2018, 14K paper drafts and the corresponding accept/reject decisions, over 10K textual peer reviews written by experts for a subset of the papers, structured JSONL, clear labels, See [A Dataset of Peer Reviews (PeerRead):Collection, Insights and NLP Applications](https://arxiv.org/pdf/1804.09635)
- [BigSurvey](https://www.ijcai.org/proceedings/2022/0591.pdf), Generating a Structured Summary of Numerous Academic Papers: Dataset and Method, 2022, 7K survey papers and 430K referenced papers abstracts
- [SciXGen](https://arxiv.org/abs/2110.10774), A Scientific Paper Dataset for Context-Aware Text Generation, 2021, 205k papers
- [scientific_papers](https://huggingface.co/datasets/armanc/scientific_papers), 2018, two sets of long and structured documents, obtained from ArXiv and PubMed OpenAccess, 300k+ papers, total disk 7GB

### Reasoning, Deduction, Commonsense, Logic

- [LIAR](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip), fake news detection, only 12.8k records, single label
- [X-Fact](https://github.com/utahnlp/x-fact/), Benchmark Dataset for Multilingual Fact Checking, 31.1k records, large, multilingual
- [MultiFC](https://www.copenlu.com/publication/2019_emnlp_augenstein/), A Real-World Multi-Domain Dataset for Evidence-Based Fact Checking of Claims, 34.9k records
- [FEVER](https://fever.ai/dataset/fever.html), Fact Extraction and VERification, 185.4k records
- TODO GSM8K, bAbI, CommonsenseQA, DROP, LogiQA, MNLI

### Planning, Execution

- [Plancraft](https://arxiv.org/abs/2412.21033), an evaluation dataset for planning with LLM agents, both a text-only and multi-modal interface
- [IDAT](https://arxiv.org/abs/2407.08898), A Multi-Modal Dataset and Toolkit for Building and Evaluating Interactive Task-Solving Agents
- [PDEBench](https://github.com/pdebench/PDEBench), set of benchmarks for scientific machine learning
- [MatSci-NLP](https://arxiv.org/abs/2305.08264), evaluating the performance of natural language processing (NLP) models on materials science text
- TODO BigBench Hard, FSM Game

### Tool Use, Function Invocation

- [Trelis Function Calling](https://huggingface.co/datasets/Trelis/function_calling_v3)
- [KnowLM Tool](https://huggingface.co/datasets/zjunlp/KnowLM-Tool)
- [StatLLM](https://arxiv.org/abs/2502.17657), statistical analysis tasks, LLM-generated SAS code, and human evaluation scores
- TODO ToolComp

## Benchmarks

- [SciArena: A New Platform for Evaluating Foundation Models in Scientific Literature Tasks](https://allenai.org/blog/sciarena)
- [AgentEvals CORE-Bench Leaderboard](https://huggingface.co/spaces/agent-evals/core_leaderboard)
- [Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Chatbot Arena LLM Leaderboard](https://lmsys.org/projects/)
- [GAIA Leaderboard](https://gaia-benchmark-leaderboard.hf.space/)
- [GalileoAI Agent Leaderboard](https://huggingface.co/spaces/galileo-ai/agent-leaderboard)
- [WebDev Arena Leaderboard](https://web.lmarena.ai/leaderboard)
- [MiniWoB++: a web interaction benchmark for reinforcement learning](https://miniwob.farama.org/)

## Research Agents

- [Ai2 Scholar QA](https://qa.allen.ai/chat)
