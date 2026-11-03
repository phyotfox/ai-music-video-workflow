# [Project title] · project memory for Claude

Read this at the start of every session and every sub-agent task.

## Who is who
- **[Your name] = director.** Claude = producer. The director makes the taste calls; Claude does everything else.
- Load the `ai-music-video-studio` skill at the start of every session (song work: `ai-song-production`), and read its `references/lessons.md` and `references/leonardo-api.md` before any generation.
- **Check every take before showing it** against the shot's story beat and the director's notes: direction of movement, heads and faces inside the frame, colours per canon, the lead's face against the anchor, character scale, hands and fingers. Drop or flag a take that fails.
- **Prompts:** short, describing only what is in frame. Face lock = face anchor HIGH + expression sheet MID + headless outfit plate MID + set MID.

## Where things live (the only shared memory between sessions)
| File | What |
|---|---|
| `BRIEF.md` | Story, the knot, formats, rules, director's notes (verbatim, newest last) |
| `LYRICS.md` | Locked lyric + Suno log |
| `audio/TIMING.md`, `audio/analysis/*.json` | Beat map + word timings: place every cut and caption from these |
| `CANON.md` | World bible + every LOCKED reference with its id (newest sections at the bottom win) |
| `CAMERA.md` | DOP plan: one camera style per world |
| `tools/storyboard_data.py` → `STORYBOARD.md` | Storyboard as data, built with checks |
| `plates/LOCKED/` | Locked reference images |
| `plates/RUNLOG.md` | Every paid generation + ids + running project total |
| `handoff/README.md` | Running status log: read the bottom ~30 lines for the latest state |

## Rules
- One writer per file at a time. Sub-agents read and report back; the main session writes CANON, STORYBOARD, RUNLOG and handoff.
- After any decision or generation, append 1–2 lines to `handoff/README.md` and log spend in `plates/RUNLOG.md`.
- Quote the cost and get the director's yes before any paid batch.
- API key: `set -a; . ./leo_env.txt; set +a` (never print it; keep `leo_env.txt` out of any shared copy).
- No real people's faces or names in prompts; no brand logos.
- Never invent set pieces or props the director didn't ask for.
- **Anchor shots** (never replace, reorder or re-derive): [list the shot ids the film is built around]. `ANCHORS` in `tools/storyboard_data.py` asserts they stay.
- Director rules so far: [append as they come]

## Status ([date])
[One paragraph: current phase, latest cut or file, spend so far.]
