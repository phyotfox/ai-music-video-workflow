---
name: "ai-song-production"
description: Write, generate and lock an original AI song (Suno) for a music video or short-form piece, from first idea to an edit-ready, beat-mapped master. Covers concept and lyric writing with scansion rules, Suno style/exclude/lyrics fields, driving Suno in the user's browser, fixing takes (Cover, Song Editor Replace Section), WAV export, and measuring the final take (stems, kick-locked beat grid, word timings, skipped-lyric check) with a bundled script. Use this whenever the user wants to make a song, track, jingle or soundtrack with AI, write lyrics for Suno, improve or fix a Suno take, prepare a song for a music video edit, or get BPM/beat/word timing from a song file — even if they only say "let's make another track like the last one" or "help me write a Suno prompt".
---

# AI song production

You are the production team; the user is the director. They hold taste and make every pick (concept, lyric lock, the take). You do the heavy lifting: research, drafting, prompt writing, running Suno, fixing takes, and turning the locked song into timing data the video edit can run on.

Why this split matters: the best results in AI music videos come from one person spending all their attention on judging, never on typing prompts. So keep the director's decisions small and clear (pick A/B/C, lock, approve), and do everything else.

The method comes from studying high-performing AI music videos (anabology's ESCAPE VELOCITY / CLODYSSEY / BLISS) plus a real run-through ("To The Moon", see `references/worked-example.md`).

## The pipeline at a glance

| # | Phase | You produce | Director decides |
|---|---|---|---|
| 0 | Project folder | `PROJECT/` with `BRIEF.md`, `LYRICS.md`, `audio/`, `refs/` | — |
| 1 | Brief | `BRIEF.md` song section | Genre refs, length, language, tone, purpose |
| 2 | Concept | 3–4 directions, each with a knot + one-sentence story | Picks one (or a mix) |
| 3 | Lyrics | Draft with section cues + line table | Locks the lyric |
| 4 | Suno round 1 | 2 styles × 2 takes, logged | Picks the closest take |
| 5 | Fix rounds | Cover / Replace Section / cue tweaks | Approves each fix |
| 6 | Lock + export | WAV in `audio/`, takes log closed | "Locked" |
| 7 | Measure | stems, `beatmap.json`, `words.json`, `TIMING.md` | Checks the drop downbeat by ear |
| 8 | Hand-off | Shot table in `BRIEF.md` re-timed to real bars | Moves on to visuals |

Write everything to files as you go. Long chats lose decisions; files don't. Every later step (and every sub-agent) should read `BRIEF.md` and `LYRICS.md` first.

## 0. Project folder

Create (or ask where to create) a project folder:

```
PROJECT/
  BRIEF.md        story, rules, structure (template: assets/BRIEF-template.md)
  LYRICS.md       lyric, Suno fields, takes log (template: assets/LYRICS-template.md)
  audio/          locked master + stems + analysis (versions go in audio/archive-*/)
  refs/           reference images/tracks (style only)
```

Put the director's words into `BRIEF.md` verbatim under "Director notes". Paraphrasing loses the taste signal.

## 1. Brief — ask, don't assume

Use the question tool for the few things that change what you build: length (and whether it's for a competition with rules), language, tone, lead vocalist type, release platform/deadline. Research the user's reference tracks (search the web) to learn their BPM range, genre and energy shape — then describe that sound in words; never put artist names in Suno.

Also check early: competition rules, likeness/rights of any real person, deadline with time zone (state today's date in the brief — Claude is weak at "today").

## 2. Concept — find the knot

Offer 3–4 distinct directions. Each one gets:
- **The knot**: one title/phrase/image doing 2–3 jobs (e.g. "To the moon" = getting high + hype chant for a stock or AI valuation + the literal launch).
- **One-sentence story** (who, what changes, how it ends).
- **The drop moment**: the image or line the chorus lands on.
- **A motion-graphics idea** the edit can carry (HUD, UI, editorial type…).
- One line on why it suits AI generation, and one risk.

Recommend one, say why in two lines, and let the director mix. Expect them to reject literal symbols ("don't show the bubble") — move the metaphor into story, props and set clues instead. Read `references/lyric-craft.md` for the concept toolkit.

## 3. Lyrics

Read `references/lyric-craft.md` before drafting. The core rules:
- Every reference lands in one listen; insider jokes go to the graphics, not the lyric.
- The hook is a phrase people already say, 2–7 plain syllables, ideally a double meaning; its literal instruction can be the message ("Don't look down").
- One sincere line where the music thins (the break). It is the emotional turn — protect it.
- Spoken/rapped lines: one line per 2-bar slot, 10–13 syllables, rhyme on the bar end. Count syllables in a table.
- Subtract rather than add. No device the user's last song already used.
- For a ~60 s song: intro (whisper) · verse (4 lines) · pre-drop (held line) · drop (chant ×2) · break (sincere line) · build · final drop · stop · whispered tag. ~100–130 words.

Deliver the lyric paste-ready (cues in `[square brackets]`, sung echoes in `(parentheses)`), plus a line table with syllables and the job of each line, plus 2–3 alternates for the weakest lines. Mark it LOCKED in `LYRICS.md` when approved and don't change locked lines without asking.

## 4. Suno round 1

Read `references/suno-guide.md` for field formats, style recipes, exclude banks and settings. In short:
- **Style** (<1,000 chars): genre blend + BPM + key + two voices (verse delivery / hook delivery) + arrangement shape + "hard stop" + a mood guard ("never harsh"). No artist names.
- **Exclude**: things that would ruin it (rap, male lead, airhorn, trap hats, autotune, chipmunk vocals, lo-fi…).
- **Settings**: Advanced mode, vocal gender, custom duration (it obeys roughly), title with a version tag like `(D1 S1)` = draft 1, style 1.
- Run **2 styles × 2 takes**: one close to the brief, one pushing the other reference. Change one variable per round after that.

**Driving Suno in the user's browser** (they must be logged in themselves — never enter passwords): see the "Browser automation" section of `references/suno-guide.md` for the exact gotchas (the lyrics box is a contenteditable div — click it and type; styles/title accept direct input; duration has its own text box; Create costs credits).

You can't hear audio. Never pick a take yourself. Log every take (title, style, length) in the takes table in `LYRICS.md`, and give the director a short "what to listen for" list: does the chant land on the drop, is the break quiet, does it hard-stop, are key words clear.

## 5. Fix rounds — smallest fix first

| Problem | Fix | Notes |
|---|---|---|
| Delivery of one part (e.g. "make it sound like an intercom, cheekier") | **Remix → Cover** of the liked take, with an updated cue for that section and small ad-libs `(ha-ha)` | Audio influence ~60–70% keeps the rest close. Free plan OK |
| A section is missing, repeated or wrong | **Song Editor → Replace Section** (Pro) | See below |
| Pure sound treatment (filter, radio, reverb) | Do it in post on the vocal stem | Exact and free; can't add new performance |
| Pronunciation | Respell the word, or re-sing in the editor | Keep the BPM lock OFF when re-exporting |

**Replace Section, step by step** (learned the hard way):
1. ⋯ → Edit → *Open in Editor* on the take. Wait for "Clips analyzing" to finish.
2. Select the range **on the song's own lane** (dragging in empty space creates a useless empty lane). Check the "Replace from" times; Smart mode snaps to the beat.
3. Click **Replace Lyrics**, enter the new section with its cue, and set a section-only style (e.g. "drums drop out, glassy pad, soft voice alone, same key and tempo, riser back in").
4. Replace (≈4 credits) → two alternates. The director auditions → **Commit** → **Save as New Song**.
5. Warn the director: the replacement can be **longer than the selection** (a 7 s gap became 18 s), and saving **re-renders the whole song**, so all previous timings are void — always re-measure.

Log each round (what changed, why, settings, results) in `LYRICS.md`.

## 6. Lock and export

When the director says "locked": write the locked take's exact title and length into `LYRICS.md`. Downloading is a file download — ask first, naming the file, source and rough size. Prefer **WAV** (Pro) as the master; M4A is fine for analysis and often carries Suno's own timed lyrics. Chrome saves to the user's Downloads folder, which you may not see: ask them to move it into `PROJECT/audio/`, then verify the filename and duration with `ffprobe` (people often move the wrong version — check before analysing). Move superseded audio into `audio/archive-v1-…/`.

## 7. Measure the locked take

Run the bundled script (it installs its own Python deps on first run, ~5 min; afterwards ~2–4 min):

```bash
python3 scripts/analyze_song.py "PROJECT/audio/SONG.wav" --out "PROJECT/audio" --lyrics lyrics.txt
```

(`lyrics.txt` = the locked lyric lines without cues; it powers the skipped-line check.) It writes `stems/`, `analysis/beatmap.json`, `analysis/words.json`, an embedded-lyrics `.srt` if present, and `TIMING.md`.

Then read `TIMING.md` and check, in this order:
1. **⚠ Possibly unsung lines.** Suno silently skips sections (it dropped the whole break in "To The Moon"). If the sincere line or hook is missing, go back to step 5 before anything else.
2. **Tempo.** Suno usually runs 3–6% fast and drifts; the script anchors on the kick drum, never a fixed BPM.
3. **Drop downbeat.** The script assumes each steady kick run starts on beat 1. Ask the director to confirm the drop lands where the table says.
4. **Sections.** Auto-labelled by drum/vocal energy; rename them (intro, verse, drop, break, build, tag) in a short table.

Whisper word timings are ±0.1 s and can mishear ("Hold your glass" for "breath") — flag odd words for the director to check by ear, and treat them as a pronunciation warning too.

## 8. Hand-off to the video

Rewrite the structure table in `BRIEF.md` on the measured bars: bars · time · what's sung · picture · hidden clues/graphics. Point out natural cut points (a sincere line split across a drums-out bar, a final hit followed by near-silence for a black frame). `beatmap.json` is what an After Effects/Cavalry script or expression reads to key cuts, camera hits and lyric type to the music.

**Lessons from the sequel:** if the measurement shows a line or a hum wasn't sung, move it to on-screen type or the HUD graphics instead of fighting Suno. When a take needs a fix (an ending whisper, say), try one fix, then stop: on Don't Let Go five attempts (Extend, a Speech whisper, three code-built endings) all came out worse than the original take.

## Communicating with the director

- Keep messages short: what you did, what they need to judge, one question.
- Name files and times concretely ("bar 34, 0:59.6"), not "the quiet part".
- When something went wrong (wrong file moved, skipped section, longer song), say it plainly with the fix.
- Offer, don't impose, extra polish; the director's "sounds good" ends a phase.

## Bundled files

- `scripts/analyze_song.py` — stems, kick-locked beat map, word timing, skipped-lyric check, TIMING.md.
- `references/suno-guide.md` — fields, style recipes, cue vocabulary, exclude bank, settings, editor and browser automation details.
- `references/lyric-craft.md` — knots, concept frames, lyric rules, scansion by BPM, hook and break craft.
- `references/worked-example.md` — the full "To The Moon" run: brief → concept → lyric → 3 Suno rounds → measured structure.
- `assets/BRIEF-template.md`, `assets/LYRICS-template.md` — starting files for a new project.
