# Lessons from To The Moon

| What happened | Cost | Do this instead |
|---|---|---|
| One session ran 4 days; every step re-read the history (~600 M cached tokens, ~US$230) | Biggest single cost | One session per phase, handoff files, sub-agents for heavy reading |
| Vertical cut planned after picture lock | 2 re-renders, HUD rebuild, 4 regenerated shots | Formats in the brief; centre-safe composition; mark native-9:16 shots in the storyboard |
| Suno skipped the sincere break | Song Editor round + re-timing | Listen-check every section before locking |
| Face drift, hair outside helmet, extra fingers | Several fix rounds | Face anchor + sheets on every generation; fix the frame, don't re-roll |
| Wider asteroid shot came out with wrong character scale | A wasted generation | Same references for wides; keep the original framing when the user likes it |
| "Set scale to frame size" in Premiere MCP didn't stick | Debug time | Set scale explicitly (150 for 720p in 1080p; 50 for 4K graphics) |
| After Effects MCP bridge had no heartbeat | Switched approach | Generate a .jsx build script and have the user run it |
| Blurred-background fills in the vertical cut | User rejected | Solid black / red / white from the frame edge; rebuild graphics vertically |
| Recomposed 9:16 frame looked stretched | One clip discarded | Compare proportions to the original before animating |
| Thumbnail text cut off in Instagram's 3:4 grid | Redo | Text inside the centre 1080×1350 of the cover |
| Captions in a polished "AI" voice | Rewrite | Write like the user talks; no slogans |
| SRT named `name.en.srt` didn't upload | Redo | Plain `name.srt`, CRLF |

What worked and should stay: the knot, a written canon, stills-first approval, the beat map as the spine, motion
graphics in code, the review page, the AE build script, a launch plan doc, and an X thread page with copy buttons.

# Lessons from Don't Let Go (the sequel)

| What happened | Cost | Do this instead |
|---|---|---|
| The recovery pod went through nine designs; prompts kept passing the old pod interior and a retired sheet as references, so old shapes leaked into every new design | ~$25–30 of a ~$56 stills budget | One locked sheet per design before scene shots; audit the refs each prompt sends; list retired assets in CANON |
| Claude invented a tunnel tent to match its first interior, and every later shot inherited it | Several rounds | Never add set pieces the director didn't ask for; ask first |
| Storyboard chat, pod chat and QC session ran side by side | Drift, two cost totals to reconcile | One main session, sub-agents report back, `CLAUDE.md` + handoff log, one writer per file |
| The kitten-sized mascot came out huge in almost every new set | Many edit rounds, then a manual Photoshop fix | Check scale on a contact sheet before showing; macro framing; let the director fix it by hand when edits stall |
| Face drift in close-ups: a drifted plate was passed as a reference, and edits of edits compounded it | ~$2.5 of failed fixes | Face anchor ref 1 at HIGH on every frame with the face; never pass a drifted plate; when stuck, go back to the original plate |
| Nano Banana used for new frames because its runner was handy | Pixel-identical takes, wasted spend | Seedream for new frames; Nano only for one surgical change, never an edit of an edit |
| Review page notes only saved on a button press | The director's notes from v2 on were lost | Autosave ~1.5 s after each edit |
| A rewrite pass replaced the two shots the film was built around | Restore round | Mark anchor shots in the storyboard data and assert they stay |
| Takes shown with wrong direction of movement, wrong screen colour, extra fingers | Director's time on QC | Written checklist; check every take before showing it |
| Reference-mode clips on shots that didn't need references | $13.10 wasted ("looks like AE motion graphics") | Start-frame mode by default; model test on 2 shots first |
| Five attempts to fix the whispered ending in Suno | Time, none better | Try one fix, then stop |
| A model test went over its quote because the cap was checked before the last price came back | $0.75 over | Check the cap before each submit using the known price |

What worked and should stay (new on the sequel): the storyboard board with the song, the DOP plan per world,
sheets first, the storyboard as data with checks, QC before the director sees anything, free fixes in post,
short camera-and-beat prompts, and `CLAUDE.md` as the shared memory between sessions.
