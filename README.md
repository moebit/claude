# multi-llm

A Claude Code plugin for cross-model collaboration. Lets Claude reach out to OpenAI and Gemini from inside a session.

## Skills

| Skill | What it does |
| :---- | :----------- |
| `brainstorm` | Multi-turn dialogue between OpenAI and Gemini on a topic; optional `--research` mode where both models use web search. |

## Install

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — `brew install uv` or `conda install -c conda-forge uv`. The brainstorm script declares its dependencies inline and `uv run` resolves them on first call.
- `OPENAI_API_KEY` and `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) exported in the shell that runs Claude Code.

### Local install

From this repo's directory:

```bash
claude --add-dir .
```

Then in Claude Code:

```
/plugin install ./
```

Or use the plugin marketplace flow once published. The plugin manifest lives at `.claude-plugin/plugin.json`; skills auto-discover from `skills/`.

## Usage

Ask Claude naturally — the skill description triggers it:

> "Brainstorm with the other models on how to design a distributed task queue."

Or invoke directly:

```
/multi-llm:brainstorm how to design a distributed task queue
```

Add "research it" / "use web search" to engage the `--research` flag, which turns on web search for both models.

## How it works

1. Claude invokes `skills/brainstorm/SKILL.md`.
2. The skill runs `scripts/brainstorm.py` via `uv run` (inline dependency metadata).
3. The script alternates calls to OpenAI (Responses API) and Gemini (`google-genai` SDK), feeding each model the running transcript.
4. The transcript streams to stdout; Claude reads it back and synthesizes for the user.

## Configuration

| Variable | Purpose | Default |
| :------- | :------ | :------ |
| `OPENAI_API_KEY` | OpenAI auth | _(required)_ |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google AI auth | _(required)_ |
| `BRAINSTORM_OPENAI_MODEL` | OpenAI model name | `gpt-5` |
| `BRAINSTORM_GEMINI_MODEL` | Gemini model name | `gemini-2.5-pro` |

## Layout

```
.
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── brainstorm/
│       ├── SKILL.md
│       └── scripts/
│           └── brainstorm.py
└── README.md
```
