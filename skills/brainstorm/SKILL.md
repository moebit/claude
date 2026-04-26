---
name: brainstorm
description: Run a multi-turn brainstorm between OpenAI and Gemini on a user-supplied topic, then return the transcript for synthesis. Use when the user wants to "brainstorm with other models", get cross-model perspectives, debate an idea, or explore a topic from multiple angles. Supports a research mode where both models use web search.
allowed-tools: Bash(uv run *)
argument-hint: <topic>
---

# Brainstorm with OpenAI and Gemini

This skill runs a back-and-forth dialogue between OpenAI and Gemini on `$ARGUMENTS`, prints the transcript to stdout, and lets you (Claude) synthesize the result for the user.

## How to invoke

Default (3 rounds, no web search):

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/brainstorm.py" --topic "$ARGUMENTS"
```

Research mode — both models use web search:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/brainstorm.py" --topic "$ARGUMENTS" --research
```

Other flags:
- `--turns N` — number of rounds (default `3`; each round is one OpenAI turn + one Gemini turn)
- `--start gemini` — Gemini opens (default: OpenAI opens)
- `--openai-model NAME` — override OpenAI model (default `gpt-5`, or `$BRAINSTORM_OPENAI_MODEL`)
- `--gemini-model NAME` — override Gemini model (default `gemini-2.5-pro`, or `$BRAINSTORM_GEMINI_MODEL`)

If the user passed a topic but also expressed intent like "research it" or "look it up", add `--research`. If they asked for "a quick exchange" or "just one round", set `--turns 1`.

## Required environment variables

- `OPENAI_API_KEY` — OpenAI API key
- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) — Google AI API key

If either is missing, the script exits non-zero with a clear message. Relay it to the user and ask them to export the missing key before re-running.

## After the script runs

Don't just paste the transcript back. Synthesize:
1. Rank the strongest ideas across both models.
2. Note where OpenAI and Gemini disagreed or emphasized different angles.
3. Call out any novel point the user probably hadn't considered.
4. End with a concrete next step or a follow-up question.

The raw transcript is already on the user's screen — your value is judgment on top of it.
