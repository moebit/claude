# moebit-tools

A personal Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) hosting `multi-llm` (cross-model collaboration) and `project-status` (interactive HTML progress tracker for any project).

## Plugins & skills

| Plugin | Skill | What it does |
| :----- | :---- | :----------- |
| `multi-llm` | `brainstorm` | Multi-turn dialogue between OpenAI and Gemini on a topic; optional `--research` mode where both models use web search. |
| `project-status` | `project-status` | Generate or update `project_status.html` — an interactive page showing the main parts of a project, what's shipped, and what's pending. Styled with the ivory/clay/olive palette from [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/). |

## Install

### Prerequisites

- For `multi-llm`: [`uv`](https://docs.astral.sh/uv/) — `brew install uv` or `conda install -c conda-forge uv`. The brainstorm script declares its dependencies inline and `uv run` resolves them on first call. Also `OPENAI_API_KEY` and `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the shell that runs Claude Code.
- For `project-status`: nothing beyond Claude Code itself — pure HTML output, no runtime deps.

### Install from this repo

`moebit-tools` is a Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) hosting the two plugins listed above. From inside Claude Code:

```
/plugin marketplace add moebit/claude
/plugin install multi-llm@moebit-tools
/plugin install project-status@moebit-tools
```

Then run `/reload-plugins` to activate. The skills become available as `/multi-llm:brainstorm` and `/project-status:project-status` (both also auto-invoke from natural-language triggers).

> Because the repo is private, `gh auth status` (or another git credential helper) must be authenticated for the host running Claude Code so the marketplace clone can fetch.

You can also install via the CLI before launching Claude Code:

```bash
claude plugin marketplace add moebit/claude
claude plugin install multi-llm@moebit-tools
claude plugin install project-status@moebit-tools
```

### Local development (skip marketplace)

To iterate without committing/pushing:

```bash
claude --plugin-dir /path/to/claude
```

Run `/reload-plugins` after edits to pick up changes.

## `multi-llm`

### Usage

Ask Claude naturally — the skill description triggers it:

> "Brainstorm with the other models on how to design a distributed task queue."

Or invoke directly:

```
/multi-llm:brainstorm how to design a distributed task queue
```

Add "research it" / "use web search" to engage the `--research` flag, which turns on web search for both models.

### How it works

1. Claude invokes `skills/brainstorm/SKILL.md`.
2. The skill runs `scripts/brainstorm.py` via `uv run` (inline dependency metadata).
3. The script alternates calls to OpenAI (Responses API) and Gemini (`google-genai` SDK), feeding each model the running transcript.
4. The transcript streams to stdout; Claude reads it back and synthesizes for the user.

### Configuration

| Variable | Purpose | Default |
| :------- | :------ | :------ |
| `OPENAI_API_KEY` | OpenAI auth | _(required)_ |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google AI auth | _(required)_ |
| `BRAINSTORM_OPENAI_MODEL` | OpenAI model name | `gpt-5.5` (`gpt-5.5-pro` with `--pro`) |
| `BRAINSTORM_GEMINI_MODEL` | Gemini model name | `gemini-3.1-flash-lite-preview` (`gemini-3.1-pro-preview` with `--pro`) |

Defaults pick the cheap-but-current tier. Pass `--pro` (or ask Claude for "the Pro models") to swap both sides to the top tier for the run.

## `project-status`

### Usage

Run the skill from any project directory:

```
/project-status:project-status
```

…or in natural language: "build a status page for this project", "make a progress tracker", "generate a project board".

First invocation in a project: Claude analyzes the codebase, identifies 4–10 main parts, writes `project_status.html` to the project root, and appends a tracking section to `CLAUDE.md`. Open the HTML file in a browser to see clickable stage cards with shipped/pending columns.

Subsequent invocations: the skill detects the existing file and runs in **update mode** — surgical edits to the inline `STAGES` array based on recent git history, without regenerating the file or touching user-curated entries.

### How it works

1. Claude detects mode by checking for `project_status.html` in the target directory.
2. **Create mode**: reads README, manifest, top-level dirs, recent commits, and any TODO/ROADMAP docs; substitutes them into `templates/project_status.html`; appends `assets/claude_md_tracking.md` to the project's CLAUDE.md so future sessions know to keep the page current.
3. **Update mode**: reads the existing file, runs `git log --since=<header-date>`, edits the STAGES array surgically, bumps the snapshot date.

The tracking note in `CLAUDE.md` is the auto-update mechanic — once dropped, any Claude session opened in that project will see it and update the page after finishing meaningful work on a tracked part.

### Visual identity

Palette borrowed from [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/) — ivory background, terracotta clay accents, sage olive for shipped bullets, warm oat for card hover. Serif headings with italic emphasis, monospace eyebrows.

## Layout

```
.
├── .claude-plugin/
│   ├── marketplace.json     # marketplace manifest (lists both plugins)
│   └── plugin.json          # multi-llm plugin manifest (source: "./")
├── skills/
│   └── brainstorm/          # multi-llm's skill
│       ├── SKILL.md
│       └── scripts/
│           └── brainstorm.py
├── plugins/
│   └── project-status/      # project-status plugin (source: "./plugins/project-status/")
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── project-status/
│               ├── SKILL.md
│               ├── templates/
│               │   └── project_status.html
│               └── assets/
│                   └── claude_md_tracking.md
└── README.md
```
