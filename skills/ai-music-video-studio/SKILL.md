---
name: "ai-music-video-studio"
description: An end-to-end workflow (by Phyo Thu) for making an AI music video with Claude as producer and the user as director — brief, world bible, song, stills, Leonardo API generation (Seedream, Nano Banana Pro, Seedance, Kling), edit in Premiere, After Effects finish, code-built motion graphics, review page, 16:9 + 9:16 masters, thumbnails, and the launch kit (X thread, Instagram Reel, YouTube). Use this whenever the user wants to start, plan, continue or finish an AI music video, short film, MV, "slopcore" video or similar music-driven piece, even if they only say "let's make another video like To The Moon", "new MV idea", "help me storyboard this song", "make the vertical cut", "build the launch posts" or "how do we do this faster this time". Pair it with the ai-song-production skill for the song itself.
---

# AI Music Video Studio

The user directs. You produce. The user's time goes on taste calls (idea, look, which take, which frame,
when to stop); yours goes on everything that can be written down, generated, measured, assembled or coded.
This skill is the workflow from two films, "To The Moon" and its sequel "Don't Let Go" (2026), rewritten after each.

## What changed after the first film (read this first)

The first film cost ~US$144 in Leonardo generation and ~US$230 in Claude usage over one 4-day session.
Almost all of the Claude cost was the session re-reading its own history. So:

1. **Run one session per phase** (below). End each phase by writing/refreshing the handoff files, then tell the
   user to open a fresh session that starts from them. Don't let one session run for days.
2. **Delegate heavy reading to sub-agents** (contact sheets, frame checks, research, reading big files). Only
   their short conclusions come back into the main context.
3. **Decide every delivery format on day one** (16:9 master + 9:16 Reel at minimum). Vertical was an afterthought
   last time and cost two re-renders, a graphics rebuild and four regenerated shots.
4. **Lock inputs before spending**: song fully sung (all sections), face anchor + reference sheets attached to every
   generation from shot one, review page from the first rough cut.
5. **Reuse the toolkit in `scripts/`** instead of re-inventing it.

## What changed after the second film

The sequel was 20% longer with 55% more shots, made in about 3 days for ~US$156 in generation. Most of the
waste was one design (a recovery pod) that went through nine versions. So, on top of the list above:

1. **Sheets before shots.** Every recurring character, prop and set gets a locked sheet before any scene shot.
   One reference per design. Write retired designs into `CANON.md` and never pass them again.
2. **Audit the references each prompt actually sends.** Old shapes leak in through reference images, not
   prompts. A plate passed as a reference carries its face, its scale and its set with it.
3. **One main session plus sub-agents, with a `CLAUDE.md` at the project root** (rules, where things live,
   current status) and an append-only `handoff/README.md`. Parallel chats on one project drift. One writer per file.
4. **Review the story before anything moves:** a storyboard board with the song playing, each shot's still on a
   monitor, a to-scale shot strip and OK / Change / Cut + note per shot, autosaved to a database.
5. **A DOP plan (`CAMERA.md`):** tag every shot by the world it's in and give each world one camera style
   (one film reference, lens, height, one move). Camera and acting calls get fast.
6. **Check every take before showing it** against a written checklist (direction of movement, faces in frame,
   colours per canon, scale, hands). Free fixes in post before paid re-rolls. The director's time is for taste.
7. **Test video models on 2 shots before the batch** (~$11), then pick a default.
8. **Protect the shots the director loves.** Mark them as anchors in the storyboard data and assert they stay.

## Ground rules

- **Money:** state the estimated cost and get a clear yes before any paid generation batch. Log every spend in
  `plates/RUNLOG.md` with a running project total.
- **Keys:** the Leonardo key lives only in an env file (e.g. `.leo_env`) loaded with `set -a; . .leo_env; set +a`.
  Never print, echo or write it anywhere.
- **Accounts:** the user logs in to Suno, X, Instagram and YouTube themselves. Never post, schedule, reply or
  message on their behalf. Ask before downloads and before deleting files.
- **Likeness and brands:** references are style only. No real person's face or likeness, no logos or brand
  names in lyrics or prompts. Describe, don't name.
- **Taste stays with the user.** Offer options with a recommendation; don't decide the look for them.
- **Never invent set pieces or props the user didn't ask for.** If a shot needs one, ask.

## The phases

Each phase ends with its handoff files updated. A new session reads `BRIEF.md`, `CANON.md`, the newest
storyboard, `handoff/README.md` and `plates/RUNLOG.md` first — that is the whole memory it needs.

### 1. Brief and song
- Write `BRIEF.md`: one-sentence story, **the knot** (one phrase doing 2–3 jobs; for To The Moon: high /
  number-go-up / literal launch), tone, length, **delivery formats** (16:9 + 9:16 + covers), rules/leave-out list,
  and the director's notes verbatim at the bottom (append, newest last).
- Song: use the **ai-song-production** skill (lyrics, Suno fields, takes, stems, beat map, word timings).
  Before locking, listen-check that every section is actually sung — Suno skipped the sincere break last time.
- Output: locked WAV, `audio/analysis/beatmap.json`, `words.json`, `audio/TIMING.md`. Everything later is placed
  from these numbers, not by ear.
- If a line wasn't sung, move it to on-screen type or the HUD instead of fighting Suno. Try one audio fix, then stop.

### 2. World bible and look
- `CANON.md`: face, hair, wardrobe, props, mascot, sets, colour rules, what never appears.
- Lock reference images: **face anchor**, hero outfit (headless "ghost mannequin" plate works best for outfits),
  expression sheet, mascot turnaround, key sets. Upload them once and keep the ids in a JSON
  (`video/refs-720/uploaded-ids.json`).
- **Character and asset sheets** for every recurring thing (characters in costume, mascot, props, vehicles, sets),
  one locked reference per design. Any frame where the lead's face shows, including edits of an existing plate,
  passes the face anchor as ref 1 at HIGH.
- Spend extra time here: the user's lesson from both films is that everything later references the look.

### 3. Storyboard and stills
- Storyboard on the beat map, **as data** (a Python list built into `STORYBOARD.md` + JSON by a script with checks:
  order, total length, no shot shorter than a beat, plates exist, anchors kept): shot id, bar, record-in, length,
  story beat, action, reaction, camera, and which references go in. Write **all** prompts in one sitting before spending (anabology's "prompt book" rule).
- **Compose for both aspects:** keep the action inside the centre third of the 16:9 frame where possible, and mark
  shots that need a native 9:16 version (two characters far apart, wide establishing shots).
- Generate stills in batches (Seedream 5 Pro for plates, Nano Banana Pro / gemini-image-2 for surgical edits).
  Show one contact sheet per batch; the user approves stills (cheap) before anything is animated (expensive).
- Review it on the **storyboard board** (see "What changed after the second film") before any motion.
- **Fix, don't re-roll:** extra fingers, hair outside a helmet, face drift → edit that frame with Nano Banana Pro
  using the face anchor as a second reference, then animate the fixed frame.

### 4. Motion
- Write `CAMERA.md` (the DOP plan) first. Prompts stay short: the camera and the beat in 1–3 plain sentences,
  no character names (the model doesn't know them), detail added only to fix a returned failure.
- Test 2 shots on 2–3 models before the batch. On the second film **Seedance 2.5 from the start frame** became the
  default, **Hailuo 03** did the cheap no-reference shots (~$0.08 a clip), and **Wan 3.0** did the lip-sync in
  Leonardo's web app (the API takes no audio upload; cut the vocal sections for the user). Reference mode on shots
  that didn't need it looked like "After Effects motion graphics" and was wasted. See `references/leonardo-api.md`.
- "Every light moves": screens and glows get code-built motion comped in the edit, pulsing on the beat.
- Submit in parallel, poll, and review on one contact sheet. Native 9:16 clips for the shots marked in phase 3.

### 5. Edit, review, finish
- Assemble on the beat map. If the Premiere MCP is connected, place clips with it (import → overwrite on the
  right track at the record-in time; set scale explicitly — "scale to frame size" did not stick).
- **Review page from the first rough cut:** the cut playing, a strip of shot blocks, a card per shot with
  Keep / Fix / Re-roll / Trim + reason, "note at current time", a "what changed in this cut" list, decisions
  autosaved on the page so you can read them back.
  Build it as a published artifact with a runtime database capability.
- After picture lock: export a ProRes master, verify sync against the WAV, then generate the After Effects build
  script with `scripts/genjsx.py` + `ttm_template.jsx` (beat punch-zooms, downbeat flashes, shake ramp,
  word-timed lyric layers, a BEAT_CONTROL null with sliders).
- Motion graphics are **code, not AI images** (`dothud.py` dot-matrix font, `radar4k.py`, `gfx_titles.py`,
  `vertical_gfx.py`). Type, numbers and UI must be pixel-exact and changeable in one line.
- Grade: the user may use another assistant for a first-pass grade; they finish it by hand.

### 6. Delivery and launch
- **9:16 cut:** adapt `scripts/vertical_cut_reference.py` (crop / split-on-beat / wide-with-black-sky / zoom box /
  fit-on-solid-colour / native regenerated clip / rebuilt vertical HUD). No blurred backgrounds — the user prefers
  solid black, red or white taken from the frame. Check proportions of any regenerated shot against the original
  (a recomposed frame once came out stretched; the fix was to go back to cropping the original).
- **Covers and thumbnails:** `scripts/covers_reference.py`. Instagram's grid crops covers to 3:4; keep all text in the
  centre 1080×1350 of a 1080×1920 cover and produce a grid-check sheet.
- **Captions file:** SRT from `words.json`, plain `name.srt` (no extra dots), CRLF line endings, long lines split in two.
- **Launch kit:** see `references/launch-kit.md` (platform order, timing for the user's timezone, captions in the
  user's own voice, the X thread page template in `assets/`).
- **Making-of / case study:** a framework anyone can apply, written in the user's voice, with real images from the
  project; compare with their previous film if they have one.

## Writing in the user's voice
Write posts, captions and the making-of the way the user talks. Read a few of their own posts first.
The author's own voice, as an example: casual and direct, first person, plain words, enthusiastic but not salesy
("this part blew my mind", "super tidy", "a lot has changed"). Avoid slogan lines and aphorisms ("The finish stayed
human", "who carries the boxes", "That part's yours"); they read as AI. Draft, then offer to adjust.

## Files in this skill
- `scripts/leo.py` — Leonardo API client (still / video / upload / poll / balance; exact aspect pairs per model).
- `scripts/dothud.py`, `radar4k.py`, `gfx_titles.py`, `vertical_gfx.py` — dot-matrix HUD, radar, titles; landscape + vertical.
- `scripts/hudtrack.py` + `hudtrack2.py` — track a HUD onto a glowing screen in footage (set `HUD_GFX` to your overlay PNGs). `scripts/energy.py` — beat-synced punch/flash pass for rough cuts.
- `scripts/genjsx.py` + `scripts/ttm_template.jsx` — After Effects build script generator.
- `scripts/*_reference.py` — project scripts from To The Moon to adapt (vertical cut, covers, transcript export).
- `assets/x-thread-page-template.html` — copy-paste page for an X thread (copy buttons, character counts, media per post).
- `references/leonardo-api.md` — models, sizes, costs, gotchas. Read before any generation.
- `references/launch-kit.md` — platform specs and launch playbook. Read in phase 6.
- `references/lessons.md` — what went wrong on both films and the fix. Skim at the start of each phase.

Set `PROJECT` to the project folder before running scripts (they read and write relative to it).
