---
title: Inference Provider Analysis
purpose: Free-tier model recommendations for each provider in PROVIDER_REGISTRY
created: 2026-02-21
---

## Provider Free-Tier Summary

Recommendations for `config_chat.json` default models. Criteria: free tier, tool/function calling support, highest context window.

| Provider | Free Tier | Recommended Model (API ID) | Context | Output | Tools | Key Limit |
| --- | --- | --- | --- | --- | --- | --- |
| **gemini** | Truly free | `gemini-2.0-flash` | 1M | 8K | Yes | 15 RPM, ~1.5K RPD |
| **github** | Truly free | `gpt-4.1-mini` | 1M | 32K | Yes | 15 RPM, ~150 RPD |
| **cerebras** | Truly free | `gpt-oss-120b` | 128K | 8K | Yes | 30 RPM, 1M TPD |
| **groq** | Truly free | `llama-3.3-70b-versatile` | 131K | 32K | Yes | 30 RPM, 1K RPD |
| **mistral** | Truly free | `open-mistral-nemo` | 128K | 4K | Yes | 1 RPS, 1B tokens/mo |
| **openrouter** | Truly free | `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | 8K | Yes | 20 RPM, 50 RPD |
| **cohere** | Truly free | `command-a-03-2025` | 256K | 8K | Yes | 20 RPM, 1K calls/mo |
| **deepseek** | 5M free tokens | `deepseek-chat` | 128K | 8K | Yes | Spend-limited |
| **grok** | $25 trial credit | `grok-3-mini` | 131K | 32K | Yes | Spend-limited |
| **sambanova** | $5 trial + limited free | `Meta-Llama-3.3-70B-Instruct` | 128K | 8K | Yes | Free: 40 RPD |
| **nebius** | $1 trial credit | `meta-llama/Meta-Llama-3.1-70B-Instruct` | 128K | 8K | Yes | $1 credit |
| **fireworks** | $1 trial credit | `accounts/fireworks/models/llama-v3p3-70b-instruct` | 131K | 8K | Yes | $1 credit |
| **openai** | No free tier | `gpt-4.1-mini` | 1M | 32K | Yes | $5 min purchase |
| **anthropic** | No free tier | `claude-sonnet-4-20250514` | 200K | 8K | Yes | Pay-as-you-go |
| **together** | No free tier | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 128K | 8K | Yes | $5 min purchase |
| **perplexity** | No free API tier | `sonar` | 127K | 4K | Limited | Credits required |
| **huggingface** | $0.10/mo (minimal) | `meta-llama/Meta-Llama-3.3-70B-Instruct` | 128K | 8K | Yes | ~10 calls on free |
| **restack** | N/A | N/A | N/A | N/A | N/A | Not an inference provider |
| **ollama** | Always free (local) | `llama3.3:70b` | 128K | 8K | Yes | Hardware-bound |

## PydanticAI Compatibility Notes

Providers requiring `OpenAIModelProfile(openai_supports_strict_tool_definition=False)`:

- `groq`, `cerebras` (already handled), `fireworks`, `together`, `sambanova`

Provider requiring native PydanticAI model (not OpenAI-compatible fallback):

- `anthropic` — use `AnthropicModel` from `pydantic_ai.models.anthropic`

## Actionable Changes for `config_chat.json`

Update existing entries with stale models:

| Provider | Current Model | Recommended Model | Reason |
| --- | --- | --- | --- |
| gemini | `gemini-1.5-pro` | `gemini-2.0-flash` | 1.5-pro not on free tier; 2.0-flash is |
| github | `gpt-4.1` | `gpt-4.1-mini` | 4.1 has tighter free limits (50 RPD vs 150 RPD) |
| grok | `grok-2-1212` | `grok-3-mini` | grok-2 deprecated; grok-3-mini is cheapest current |
| openrouter | `google/gemini-2.0-flash-exp:free` | `qwen/qwen3-next-80b-a3b-instruct:free` | Larger context (262K vs 32K), better tool calling |
| together | `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | Free model removed Jul 2025; no free tier |
| openai | `gpt-4-turbo` | `gpt-4.1-mini` | gpt-4-turbo deprecated; 4.1-mini is current |
| anthropic | `claude-3-5-sonnet-20241022` | `claude-sonnet-4-20250514` | Sonnet 4 is current generation |
| huggingface | `facebook/bart-large-mnli` | `meta-llama/Meta-Llama-3.3-70B-Instruct` | bart-large-mnli is classification, not chat |
| ollama | `granite3-dense` | `llama3.3:latest` | granite3-dense has limited tool calling |

New entries to add:

| Provider | Model | Base URL | Context |
| --- | --- | --- | --- |
| groq | `llama-3.3-70b-versatile` | `https://api.groq.com/openai/v1` | 131K |
| fireworks | `accounts/fireworks/models/llama-v3p3-70b-instruct` | `https://api.fireworks.ai/inference/v1` | 131K |
| deepseek | `deepseek-chat` | `https://api.deepseek.com/v1` | 128K |
| mistral | `open-mistral-nemo` | `https://api.mistral.ai/v1` | 128K |
| sambanova | `Meta-Llama-3.3-70B-Instruct` | `https://api.sambanova.ai/v1` | 128K |
| nebius | `meta-llama/Meta-Llama-3.1-70B-Instruct` | `https://api.studio.nebius.ai/v1` | 128K |
| cohere | `command-a-03-2025` | `https://api.cohere.com/v2` | 256K |

## Restack Note

`restack` is an agent workflow orchestration platform, not an LLM inference provider. It proxies to other providers. Consider removing from `PROVIDER_REGISTRY` or documenting as a proxy.
