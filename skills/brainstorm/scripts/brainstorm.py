#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.50.0",
#   "google-genai>=1.0.0",
# ]
# ///
"""Run a multi-turn brainstorm between OpenAI and Gemini on a topic.

Reads OPENAI_API_KEY and GEMINI_API_KEY (or GOOGLE_API_KEY) from the
environment. Prints a markdown transcript to stdout, one turn at a time,
so the parent process sees progress in real time.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

from openai import OpenAI
from google import genai
from google.genai import types as genai_types


SYSTEM_PROMPT = (
    "You are participating in a brainstorming dialogue with another AI model. "
    "The goal is generative collaboration, not consensus. On each turn: build "
    "on what was said, push back where you disagree, and add at least one "
    "angle the other model has not raised. Be concrete and concise — a few "
    "strong points beat a long list. Use markdown for structure when helpful."
)


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def get_openai_client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        die("OPENAI_API_KEY is not set. Export it and re-run.")
    return OpenAI(api_key=key)


def get_gemini_client() -> "genai.Client":
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        die("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. Export it and re-run.")
    return genai.Client(api_key=key)


def render_prompt(topic: str, transcript: list[tuple[str, str]], speaker: str) -> str:
    """Render the conversation as a single user-message prompt for either model."""
    parts: list[str] = []
    parts.append(f"# Brainstorming topic\n\n{topic}\n")
    if transcript:
        parts.append("# Conversation so far\n")
        for s, text in transcript:
            parts.append(f"## {s}\n\n{text}\n")
    else:
        parts.append("# Conversation so far\n\n_(you are opening the discussion)_\n")
    parts.append(
        f"# Your turn — you are {speaker}\n\n"
        "Contribute one focused response. Build on prior points (or open the "
        "discussion if nothing has been said), surface a new angle, and where "
        "you disagree with the other model, say so plainly. Keep it tight."
    )
    return "\n".join(parts)


def call_openai(client: OpenAI, model: str, prompt: str, research: bool) -> str:
    kwargs: dict = {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    if research:
        kwargs["tools"] = [{"type": "web_search"}]
    resp = client.responses.create(**kwargs)
    text = getattr(resp, "output_text", None)
    if not text:
        die(f"OpenAI returned no text (model={model}). Raw response: {resp}")
    return text.strip()


def call_gemini(client: "genai.Client", model: str, prompt: str, research: bool) -> str:
    config_kwargs: dict = {"system_instruction": SYSTEM_PROMPT}
    if research:
        config_kwargs["tools"] = [
            genai_types.Tool(google_search=genai_types.GoogleSearch())
        ]
    config = genai_types.GenerateContentConfig(**config_kwargs)
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )
    text = getattr(resp, "text", None)
    if not text:
        die(f"Gemini returned no text (model={model}).")
    return text.strip()


def speakers_for(start: str) -> Iterable[str]:
    if start == "gemini":
        return ("Gemini", "OpenAI")
    return ("OpenAI", "Gemini")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-turn brainstorm between OpenAI and Gemini.",
    )
    parser.add_argument("--topic", required=True, help="The topic to brainstorm.")
    parser.add_argument(
        "--turns",
        type=int,
        default=3,
        help="Number of rounds (default: 3). Each round = one OpenAI + one Gemini turn.",
    )
    parser.add_argument(
        "--research",
        action="store_true",
        help="Enable web search for both models.",
    )
    parser.add_argument(
        "--start",
        choices=["openai", "gemini"],
        default="openai",
        help="Which model opens the discussion (default: openai).",
    )
    parser.add_argument(
        "--openai-model",
        default=os.environ.get("BRAINSTORM_OPENAI_MODEL", "gpt-5"),
        help="OpenAI model name. Default: gpt-5 (or $BRAINSTORM_OPENAI_MODEL).",
    )
    parser.add_argument(
        "--gemini-model",
        default=os.environ.get("BRAINSTORM_GEMINI_MODEL", "gemini-2.5-pro"),
        help="Gemini model name. Default: gemini-2.5-pro (or $BRAINSTORM_GEMINI_MODEL).",
    )
    args = parser.parse_args()

    if args.turns < 1:
        die("--turns must be at least 1")

    openai_client = get_openai_client()
    gemini_client = get_gemini_client()

    print(f"# Brainstorm: {args.topic}\n")
    print(
        f"_OpenAI: `{args.openai_model}` · Gemini: `{args.gemini_model}` · "
        f"rounds: {args.turns}"
        + (" · research mode_" if args.research else "_")
    )
    print()
    sys.stdout.flush()

    transcript: list[tuple[str, str]] = []
    order = speakers_for(args.start)

    for round_num in range(1, args.turns + 1):
        for speaker in order:
            prompt = render_prompt(args.topic, transcript, speaker)
            if speaker == "OpenAI":
                response = call_openai(
                    openai_client, args.openai_model, prompt, args.research
                )
            else:
                response = call_gemini(
                    gemini_client, args.gemini_model, prompt, args.research
                )
            transcript.append((speaker, response))
            print(f"## Round {round_num} — {speaker}\n")
            print(response)
            print()
            sys.stdout.flush()

    print("---")
    print("Brainstorm complete.")


if __name__ == "__main__":
    main()
