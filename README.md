# presencing-break

One-minute presencing breaks while your prompt runs.

When you hand an AI coding agent a big task, you wait. presencing-break turns
some of that waiting into a small natural intelligence practice. Now and then, a card like this
appears at the top of the AI's reply:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│   O N E - M I N U T E   P L A Y                      │
│                                                      │
│   While I work, a little presencing play:            │
│                                                      │
│   > LOOK FAR                                         │
│     Lift your gaze to the farthest point you can     │
│     see and let your eyes rest on the distance.      │
│                                                      │
│   (I'll keep working below. Back in a moment.)       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

Do the practice, or don't. The AI carries on with your request either way.

## What is presencing?

Presencing means being present with your current situation while actively
sensing your surroundings. It rests on a simple idea: inner conditions shape
outer realities. How well we observe, reflect and act depends on the inner
place we work from (Scharmer & Kaufer, 2025).

Our natural human intelligences matter now, more than ever. When waiting for a
prompt response, rather than reach for your phone, it's a great time to attend
to presencing. A short pause clears attention left over from the last task (Leroy, 2009),
and a little movement readies the brain for the next one (Ratey & Hagerman, 2008).

These are micro-practices: breathing, stretching, looking far, naming a
feeling, doodling, noticing the machine at work. Each takes about a minute.
There are 46 of them in `activities.json`. Customize to make your own.

## Which tools it works with

| Tool | How | Status |
|---|---|---|
| Claude Code | Hook, real timing | Works. The tool it was first written for. |
| OpenAI Codex CLI | Hook, real timing | Written to Codex's hook docs. Not yet tested in Codex. |
| Gemini CLI | Hook, real timing | Written to Gemini CLI's hook docs. Not yet tested. Google's docs say Gemini CLI was replaced by Antigravity CLI in June 2026. |
| ChatGPT, claude.ai, Gemini app, Cursor, GitHub Copilot | Paste-in instructions | Works, but the AI chooses when. See below. |
| Any terminal | `--now` command | Works. Prints a card on demand, no AI involved. |

**Why Cursor and Copilot use the paste-in version:** both have hooks, but
their docs say a hook that runs when you send a prompt cannot add text for the
AI to read. They can only add text once, at the start of a session, which
isn't enough to time breaks.

## How it works (hook version)

1. You send a prompt. Your AI tool runs `presencing_break.py` first.
2. The script checks if the prompt is "heavy": long (240+ characters or 40+
   words), or containing words like *refactor, implement, debug, review,
   entire, test suite*. Light prompts are ignored.
3. From the 6th heavy prompt since the last break, each heavy prompt has a
   25% chance of bringing one. On average that's one break per 9 heavy prompts.
4. When a break is due, the script picks a practice at random (never the same
   one twice in a row) and draws the card.
5. A hook can't draw on your screen. It can only add text the AI reads. So
   the script gives the AI the card with a plain request: "show this at the
   top of your reply, then carry on." The request says openly that it comes
   from presencing-break, which you installed.

If anything goes wrong, the script exits quietly. It never blocks your prompt.
It remembers where it is in `~/.presencing-break/state.json`. Delete that file
to start the count over.

## Requirements

- Python 3 (any recent version). No packages to install.
- On Windows, use `py -3` wherever this page says `python3`.

## Install

Download or clone this folder and keep it somewhere it will stay. In the
examples below, replace `/path/to/presencing-break` with that folder's full
path.

Try it first, without any AI tool:

```sh
python3 /path/to/presencing-break/presencing_break.py --now
```

### Claude Code

Add this to `~/.claude/settings.json`. If you already have a `"hooks"`
section, add the `"UserPromptSubmit"` part inside it.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [
        { "type": "command",
          "command": "python3 -I \"/path/to/presencing-break/presencing_break.py\" --tool claude" }
      ] }
    ]
  }
}
```

Start a new session, or open `/hooks` to reload.

### OpenAI Codex CLI

Add this to `~/.codex/hooks.json` (create the file if needed):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [
        { "type": "command",
          "command": "python3 -I \"/path/to/presencing-break/presencing_break.py\" --tool codex" }
      ] }
    ]
  }
}
```

Codex asks you to review and trust each new hook before it runs. Open
`/hooks` in Codex to do that.

### Gemini CLI

Add this to `~/.gemini/settings.json`. If you already have a `"hooks"`
section, add the `"BeforeAgent"` part inside it.

```json
{
  "hooks": {
    "BeforeAgent": [
      { "hooks": [
        { "name": "presencing-break",
          "type": "command",
          "command": "python3 -I \"/path/to/presencing-break/presencing_break.py\" --tool gemini" }
      ] }
    ]
  }
}
```

### ChatGPT, claude.ai, Gemini app, Cursor, Copilot, and others

Open `chat-instructions.md` and paste the text into your tool's custom
instructions, project instructions, or rules file. Honest note: without a
hook, the AI decides when a break is due. The timing will be looser, and it
may forget.

### Check that a hook works

Add `--force` to the end of your hook command, send any prompt, and a card
should appear. Remove `--force` afterwards.

## Settings

Open `presencing_break.py` and change the `SETTINGS` block at the top:

| Setting | Default | What it does |
|---|---|---|
| `MIN_HEAVY_GAP` | 6 | Earliest heavy prompt a break can appear on, counted from the last break |
| `FIRE_PROBABILITY` | 0.25 | Chance each heavy prompt after that brings a break |
| `HEAVY_MIN_CHARS` | 240 | A prompt this long counts as heavy |
| `HEAVY_MIN_WORDS` | 40 | A prompt with this many words counts as heavy |
| `HEAVY_KEYWORDS` | list | Words that make any prompt heavy |
| `BOX_WIDTH` | 54 | Width of the card, in characters |

Command options:

| Option | What it does |
|---|---|
| `--tool claude` / `codex` / `gemini` | Which AI tool is calling it (default `claude`) |
| `--now` | Print a card in the terminal right away |
| `--force` | Always show a card (for testing a hook) |

## Add your own practices

Add a line to `activities.json`:

```json
{ "category": "Breath", "name": "Box Breathing", "desc": "Breathe in for four, hold for four, out for four, hold for four." }
```

Keep each one short enough to do in about a minute.

## Pause or remove

- **Pause:** set `PRESENCING_BREAK_OFF=1` in your environment before starting
  the tool. Unset it to resume.
- **Remove:** delete the hook entry you added, and optionally the
  `~/.presencing-break/` folder.

## Good to know

- The hook also runs in scripted, non-interactive use (for example
  `claude -p`), so a card can show up in that output. Set
  `PRESENCING_BREAK_OFF=1` for those runs.
- The script never sends anything anywhere. It reads your prompt only to
  decide whether it is heavy, and it stores just a counter and the name of
  the last practice.

## Sources

Adapted from *Presencing for Natural Intelligence* by Arthur Grau.

- Leroy, S. (2009). Why is it so hard to do my work? The challenge of
  attention residue when switching between work tasks. *Organizational
  Behavior and Human Decision Processes, 109*(2), 168–181.
- Ratey, J. J., & Hagerman, E. (2008). *Spark: The revolutionary new science
  of exercise and the brain*. Little, Brown.
- Scharmer, C. O., & Kaufer, K. (2025). *Presencing: 7 practices for
  transforming self, society, and business*. Berrett-Koehler.

## License

MIT. Copyright (c) 2026 Arthur Grau (@isarthurgrau). See `LICENSE`.
