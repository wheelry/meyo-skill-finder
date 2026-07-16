<div align="center">

# Deep Skill Finder

![deep-skill-finder](assets/background.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.x-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-ClaudeCode%20%7C%20Hermes%20%7C%20OpenClaw%20%7C%20CatClaw%20%7C%20MeyoAgent-8A2BE2.svg)](https://www.meyo.life)

English | [中文](README.zh.md)

</div>

---


## What is this?
> Deep-skill-finder search powered by real execution and validation, not just follow creator claims

deep-skill-finder crawls Skills across the web, builds an evaluable candidate pool, and uses multi-channel recall to precisely match the best-fit Skill for your current task. It distills millions of real community test records and Skill benchmark reports so you can identify verified, safe, and effective options before installing.

## Quick Start


### Prerequisites
- A running Agent 

### Install deep-skill-finder in your Agent
- Send the following prompt directly to your Agent to complete installation:

```text
Please install the deep-skill-finder skill: download the skill package from https://www.meyo.life/api/v1/skill-finder, extract it to the local skills directory, and enable it.
```

### Use

Talk to your Agent in natural language — no special syntax needed. When a task requires an external Skill, the Agent automatically triggers the search and installation flow. Examples:

```
"Find me a skill that builds interactive dashboards from a CSV"
"Is there a skill for pulling stock market data?"
"Recommend a skill for translating technical docs into plain English"
"I need to set up a CI/CD pipeline for my repo, find me a skill that writes GitHub Actions configs that actually run"
"I'm building an AI product and need a business plan, find me a skill that helps structure the logic and polish the deck"
"I want to batch-transcribe audio interviews into clean text, find me a skill that does this end to end"
```

The Agent returns a ranked list of up to 5 recommendations with reasons. Confirm a number and the installation completes automatically.


## Why not just search the marketplace?

Standard marketplace search has two fundamental problems:

1. **Discovery** — creators write broad, abstract descriptions to rank in more searches. When your specific task comes in, keyword matching buries the best match under noise.

2. **Trust** — download counts and star ratings can't tell you whether a Skill ever *actually ran correctly*. Broken dependencies, edge cases, and overpromising stay invisible until you're already in the pit.

deep-skill-finder addresses both: it recalls by actual task behavior, and ranks by real community run results — not by what a creator claims their Skill does.


## Highlights

**Web-wide Skill indexing** — crawls Skill content across the web and builds an evaluable candidate pool, independent of any single platform's popularity ranking.

**Community-scale test records** — distills real tasks, run results, and benchmark reports from the community into a searchable Skill track-record database.

**Multi-channel recall** — pulls simultaneously from Skill capability descriptions, community test posts, and real outputs, preventing any single signal from missing the best candidate.

**Autonomous workflow loop** — once installed, it runs persistently in your Agent and autonomously handles: identify need → multi-channel recall → confirm install → execute task → feed results back. Each match gets more accurate over time.

**Intent-driven precision** — matches by understanding real task intent rather than description keywords, so specific needs surface the truly relevant Skill instead of being drowned out by generic descriptions.

**Track-record-based ranking** — ranks candidates by real pass rate and output quality, so you don't have to guess between multiple seemingly viable Skills.

**Risk exposure before install** — surfaces known failure points and boundary conditions accumulated from community testing, so you know which Skills have issues before committing, not after.


## How it works

```
You describe a task in natural language
            │
            ▼
     Intent understanding
  (rewrite into semantic query)
            │
            ▼
      Multi-channel recall
  ┌─────────┬──────────────┐
  │ Skill   │  Community   │
  │ profile │  test posts  │
  └────┬────┴──────┬───────┘
       └─────┬─────┘
             ▼
  Rank by verified track record
  → return TOP 5 with reasons
             │
             ▼
  Confirm a number → auto-install
```


## Project structure

```
├── SKILL.md                        # Skill definition (read by the Agent)
└── scripts/
    ├── deep_skill_search.py        # Semantic search via Meyo retrieval service
    └── deep_skill_install.py       # Download and install a Skill locally
```

## Scripts reference

You normally don't call these directly — the Agent handles invocation. But you can run them standalone:

**Search**
```bash
python3 scripts/deep_skill_search.py "your task description" [--agent-type openclaw]
```

**Install / Uninstall / List**
```bash
# Install
python3 scripts/deep_skill_install.py <skill-name> --dir ~/.catpaw/skills

# Uninstall
python3 scripts/deep_skill_install.py <skill-name> --dir ~/.catpaw/skills --uninstall

# List installed
python3 scripts/deep_skill_install.py --dir ~/.catpaw/skills --list
```

## Contributing

Issues and pull requests are welcome.

If you find that a specific Skill is ranked too high or too low, the underlying signal lives in the [Meyo community](https://www.meyo.life/community/home) — leaving a real test report there is the most direct way to improve future recommendations.

## License

Released under the [MIT License](LICENSE). Free to use, modify, and distribute — attribution appreciated.
