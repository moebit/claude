# moebit-tools

A personal Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) hosting `multi-llm` (cross-model collaboration), `project-status` (interactive HTML progress tracker), and `research-dev-loop` (autonomous research → plan → implement → test loop with Codex critique and Obsidian wiki memory).

## Plugins & skills

| Plugin | Skill | What it does |
| :----- | :---- | :----------- |
| `multi-llm` | `brainstorm` | Multi-turn dialogue between OpenAI and Gemini on a topic; optional `--research` mode where both models use web search. |
| `project-status` | `project-status` | Generate or update `project_status.html` — an interactive page showing the main parts of a project, what's shipped, and what's pending. Styled with the ivory/clay/olive palette from [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/). |
| `research-dev-loop` | `research-dev-loop` | Autonomous research → plan → implement → test loop. Codex critiques the plan and reviews the implementation; every stage is mirrored into an Obsidian wiki for cross-cycle memory; commits after each successful stage. Configurable via `references/program.md`. |

## Install

### Prerequisites

- For `multi-llm`: [`uv`](https://docs.astral.sh/uv/) — `brew install uv` or `conda install -c conda-forge uv`. The brainstorm script declares its dependencies inline and `uv run` resolves them on first call. Also `OPENAI_API_KEY` and `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the shell that runs Claude Code.
- For `project-status`: nothing beyond Claude Code itself — pure HTML output, no runtime deps.
- For `research-dev-loop`: the [Codex plugin](https://github.com/openai/codex-plugin-cc) for plan/implementation reviews and the [claude-obsidian plugin](https://github.com/AgriciDaniel/claude-obsidian) for wiki mirroring. The skill degrades if either is missing, but the full critique + audit-trail loop needs both.

### Install from this repo

`moebit-tools` is a Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) hosting the two plugins listed above. From inside Claude Code:

```
/plugin marketplace add moebit/claude
/plugin install multi-llm@moebit-tools
/plugin install project-status@moebit-tools
/plugin install research-dev-loop@moebit-tools
```

Then run `/reload-plugins` to activate. The skills become available as `/multi-llm:brainstorm`, `/project-status:project-status`, and `/research-dev-loop:research-dev-loop` (all also auto-invoke from natural-language triggers).

> Because the repo is private, `gh auth status` (or another git credential helper) must be authenticated for the host running Claude Code so the marketplace clone can fetch.

You can also install via the CLI before launching Claude Code:

```bash
claude plugin marketplace add moebit/claude
claude plugin install multi-llm@moebit-tools
claude plugin install project-status@moebit-tools
claude plugin install research-dev-loop@moebit-tools
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

Palette borrowed from [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/) — ivory background, terracotta clay accents, sage olive for shipped bullets, warm oat for card hover. All-sans semibold typography, monospace eyebrows.

## `research-dev-loop`

### Usage

From a project directory, with a goal in mind:

```
/research-dev-loop:research-dev-loop add JSON output mode to the report CLI
```

…or in natural language: "run a research-dev loop on X", "autonomous dev loop", "auto research loop".

The skill drives a self-contained research → plan → implement → test cycle. Codex critiques the plan and reviews the implementation; each stage's artifact is mirrored into an Obsidian wiki for cross-cycle memory; commits after each successful stage. Loops until tests pass and no open doubts remain (hard cap configurable in `program.md`).

### How it works

1. Reads `references/program.md` at the start of every run — that file is the policy (cycle cap, model picks, commit style, wiki paths). If `SKILL.md` and `program.md` disagree, the program file wins.
2. Per cycle: (a) research and file findings to the wiki, (b) draft a plan + have Codex critique it, (c) implement with a post-implement Codex review and commit, (d) write and run tests, (e) if tests fail or doubts remain, loop back.
3. Pauses only for: ambiguous goal (one tight clarifier), scope drift mid-cycle, same blocker hit 3+ cycles, or genuinely destructive actions outside the loop's scope.

### Configuration

Tune behavior by editing the program file at `skills/research-dev-loop/references/program.md` inside the installed plugin — cycle cap, web-op cap per cycle, Codex model picks, commit style, wiki path conventions, domain-specific overrides.

## Layout

```
.
├── .claude-plugin/
│   ├── marketplace.json     # marketplace manifest (lists all three plugins)
│   └── plugin.json          # multi-llm plugin manifest (source: "./")
├── skills/
│   └── brainstorm/          # multi-llm's skill
│       ├── SKILL.md
│       └── scripts/
│           └── brainstorm.py
├── plugins/
│   ├── project-status/      # project-status plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── project-status/
│   │           ├── SKILL.md
│   │           ├── templates/
│   │           │   └── project_status.html
│   │           └── assets/
│   │               └── claude_md_tracking.md
│   └── research-dev-loop/   # research-dev-loop plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── research-dev-loop/
│               ├── SKILL.md
│               └── references/
│                   └── program.md
└── README.md
```
