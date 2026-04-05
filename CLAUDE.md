# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.40.md
2. docs/kjtcom-plan-v9.40.md
3. docs/kjtcom-architecture.mmd

## Shell

* Fish shell only. No bash syntax. `set -gx IAO_ITERATION v9.40` before scripts.

## Security

* NEVER write API keys to repo. Env vars ONLY. NEVER capture customer data.

## Token Efficiency - MANDATORY (v9.40+)

* Target: <50K tokens per infrastructure iteration
* Prefer Nemotron Mini (2.7 GB, fast) for simple checks over Qwen (5.1 GB)
* Limit Ollama num_predict: 512 default, 2048 for evaluations only
* Use direct file reads for structured data (JSON, JSONL) - do not LLM-interpret
* Use scripts/utils/ollama_config.py defaults for all Ollama calls
* Log all token usage. Report total spend in Event Log Summary.

## P3 Diligence - Event Logging

* ALL scripts use iao_logger.py. ALL Telegram messages logged.
* data/iao_event_log.jsonl is append-only.
* Report includes Event Log Summary.

## Orchestration

* Minimum 2 LLMs. Ollama: qwen3.5:9b (evaluator, think:false), nemotron-mini:4b (fast), GLM (vision), nomic-embed-text (embedding).
* OpenClaw via Gemini Flash for autonomous tasks.
* 5 MCP servers: Firebase, Context7, Firecrawl, Playwright, Dart.

## Ollama Config

* ALL calls use think:false (G51 fix). ALL calls use ollama_config.py defaults.

## Artifacts

* design, plan, build, report + changelog, README, agent_scores, install.fish, architecture.mmd
* Report: Agent Scorecard + Event Log Summary + token spend

## Context

* kylejeromethompson.com | SOC-Foundry/kjtcom | kjtcom-c78cd
* 6,181 entities, 3 pipelines, 25 Dart files, 6 tabs, 48 gotchas
* Kyle handles all git. Agents NEVER touch git.
