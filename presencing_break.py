#!/usr/bin/env python3
"""
presencing-break: one-minute presencing plays while an AI agent works.

Copyright (c) 2026 Arthur Grau (@isarthurgrau). MIT License, see LICENSE.

Every so often, when you send an AI coding agent a long or heavy request,
this script asks the agent to show you a small card with a one-minute
practice (breathe, stretch, look far, name a feeling) before it gets to work.

How it reaches you: a hook cannot draw on your screen. It can only add text
that the AI reads. So the script hands the AI a ready-made card and openly
asks it to show the card at the top of its reply. Nothing is hidden from you
or from the AI.

Ways to run it:
  python3 presencing_break.py --tool claude   hook for Claude Code (default)
  python3 presencing_break.py --tool codex    hook for OpenAI Codex CLI
  python3 presencing_break.py --tool gemini   hook for Gemini CLI
  python3 presencing_break.py --now           print a card in your terminal now
  python3 presencing_break.py --tool X --force   always fire (to test a hook)

It never blocks your prompt: on any error it exits quietly with no output.
Standard library only. Set PRESENCING_BREAK_OFF=1 to pause it.
"""

import json
import os
import random
import sys
import textwrap

# ---------------------------------------------------------------------------
# SETTINGS: change these to taste.
# ---------------------------------------------------------------------------
MIN_HEAVY_GAP = 6            # a break can first appear on the 6th heavy prompt since the last one
FIRE_PROBABILITY = 0.25      # after that, the chance each heavy prompt brings a break
HEAVY_MIN_CHARS = 240        # a prompt this long counts as heavy
HEAVY_MIN_WORDS = 40         # ...or this many words
HEAVY_KEYWORDS = [           # ...or one of these words (not case-sensitive)
    "refactor", "implement", "rewrite", "redesign", "migrate", "build",
    "generate", "analyze", "analyse", "audit", "debug", "investigate",
    "review", "all files", "every file", "entire", "whole codebase",
    "across the", "step by step", "end to end", "test suite", "write tests",
]
BOX_WIDTH = 54               # inner width of the card, in characters

HERE = os.path.dirname(os.path.abspath(__file__))
ACTIVITIES_PATH = os.path.join(HERE, "activities.json")
STATE_DIR = os.path.join(os.path.expanduser("~"), ".presencing-break")
STATE_PATH = os.path.join(STATE_DIR, "state.json")
OFF_ENV_VAR = "PRESENCING_BREAK_OFF"   # set to 1 / true / yes to pause

# The hook event name each tool expects in its reply.
EVENT_NAMES = {
    "claude": "UserPromptSubmit",
    "codex": "UserPromptSubmit",
    "gemini": "BeforeAgent",
}


# ---------------------------------------------------------------------------
def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"heavy_since_break": 0, "last_activity": ""}


def save_state(state):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
    except Exception:
        pass  # never let a write failure disrupt the prompt


def is_heavy(prompt):
    if not prompt:
        return False
    if len(prompt) >= HEAVY_MIN_CHARS:
        return True
    if len(prompt.split()) >= HEAVY_MIN_WORDS:
        return True
    low = prompt.lower()
    return any(kw in low for kw in HEAVY_KEYWORDS)


def pick_activity(last_name):
    with open(ACTIVITIES_PATH, "r", encoding="utf-8") as fh:
        activities = json.load(fh)
    choices = [a for a in activities if a.get("name") != last_name] or activities
    return random.choice(choices)


def render_card(activity):
    """Build an aligned box. Padding is computed, so borders always line up."""
    w = BOX_WIDTH

    def line(s=""):
        return "│" + s.ljust(w)[:w] + "│"

    name = activity.get("name", "").upper()
    desc = activity.get("desc", "")

    lines = ["┌" + "─" * w + "┐", line()]
    lines.append(line("   O N E - M I N U T E   P L A Y"))
    lines.append(line())
    lines.append(line("   While I work, a little presencing play:"))
    lines.append(line())
    for nl in textwrap.wrap(name, w - 8) or [""]:
        lines.append(line("   > " + nl))
    for dl in textwrap.wrap(desc, w - 8):
        lines.append(line("     " + dl))
    lines.append(line())
    lines.append(line("   (I'll keep working below. Back in a moment.)"))
    lines.append(line())
    lines.append("└" + "─" * w + "┘")
    return "\n".join(lines)


def emit(card, tool):
    instruction = (
        "The user installed presencing-break, an open-source hook that now and "
        "then offers them a one-minute presencing play while you work. One "
        "is due now. Near the top of your reply, show the card below as-is "
        "inside a fenced code block (```), then continue with the user's "
        "request as normal. No need to comment on the card beyond showing it."
        "\n\n" + card
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": EVENT_NAMES[tool],
            "additionalContext": instruction,
        }
    }
    sys.stdout.write(json.dumps(out))


def parse_args(argv):
    tool, now, force = "claude", False, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--now":
            now = True
        elif a == "--force":
            force = True
        elif a == "--tool" and i + 1 < len(argv):
            i += 1
            tool = argv[i].lower()
        i += 1
    if tool not in EVENT_NAMES:
        tool = "claude"
    return tool, now, force


def main():
    tool, now, force = parse_args(sys.argv[1:])

    if now:
        # Standalone: print a card straight to the terminal. No AI involved.
        state = load_state()
        activity = pick_activity(state.get("last_activity", ""))
        print(render_card(activity))
        state["last_activity"] = activity.get("name", "")
        save_state(state)
        return

    if os.environ.get(OFF_ENV_VAR, "").strip().lower() in ("1", "true", "yes"):
        return

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # Claude Code, Codex CLI and Gemini CLI all send the prompt as "prompt".
    prompt = payload.get("prompt", "") if isinstance(payload, dict) else ""

    state = load_state()

    if not force:
        if not is_heavy(prompt):
            return  # light prompt: nothing changes, no break
        state["heavy_since_break"] = state.get("heavy_since_break", 0) + 1
        eligible = state["heavy_since_break"] >= MIN_HEAVY_GAP
        if not (eligible and random.random() < FIRE_PROBABILITY):
            save_state(state)
            return

    activity = pick_activity(state.get("last_activity", ""))
    emit(render_card(activity), tool)
    state["heavy_since_break"] = 0
    state["last_activity"] = activity.get("name", "")
    save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A presencing break must never break the user's prompt.
        sys.exit(0)
