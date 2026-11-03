# How I make an AI music video with Claude as my producer

I'm Phyo, a creative director. In 2026 I made two music videos this way: **To The Moon** (1:15, 2 days, about $137 in generation) and its sequel **Don't Let Go** (1:30, 3 days, about $156). I directed. Claude did the production: writing, prompting, generating through the Leonardo API, measuring the song, coding the graphics, building review tools and prepping the edit. Specialist models made the song, the stills and the video.

This is the whole workflow, step by step, with what went wrong. You can follow it with any AI assistant. If you use Claude, the two skills in `skills/` make Claude follow it for you, and they include the scripts.

## The setup

**Two seats.** The director makes the taste calls: the idea, the look, casting, every approval, when to stop. The producer does everything that can be written down, generated, measured, assembled or coded.

**The tools I used.** Suno for the song. Leonardo's API for stills (Seedream 5.0 Pro, Nano Banana Pro) and video (Seedance 2.5, Hailuo 03, Wan 3.0, Kling). Python, ffmpeg and Pillow for graphics and analysis. Premiere Pro and After Effects for the edit and finish. Swap any of them. The structure still holds.

**Files are the memory.** AI sessions don't remember each other, so everything lives in plain files in one project folder, and every new session reads them first. The templates are in `templates/`:

| File | What it holds |
|---|---|
| `CLAUDE.md` | The rules, where things live and the current status. Every session reads it first |
| `BRIEF.md` | The story, the knot, formats, rules, and the director's notes word for word, newest last |
| `CANON.md` | The world bible: characters, wardrobe, props, sets, colour rules, and every locked reference with its id |
| `CAMERA.md` | The DOP plan: one camera style per world |
| `storyboard_data.py` → `STORYBOARD.md` | The storyboard as data, built by a script that checks it |
| `RUNLOG.md` | Every paid generation, its id and the running total |
| `handoff/README.md` | A running log. Each session adds a line or two when it finishes something |

## The workflow

### 1. Find the knot
Before anything else, find one phrase that does two or three jobs. "To the moon" meant getting high, number go up, and a literal rocket launch. "Don't let go" meant hold your bags, stay alive and hold your breath. Every shot and graphic then has a test: does it say this?

### 2. Write the brief, with every format decided on day one
One-sentence story, the knot, tone, length, and every delivery format (16:9 master, 9:16 Reel, covers). On the first film the vertical cut was an afterthought and cost two re-renders and four regenerated shots.

### 3. Make the song, then measure it
Write the lyric, generate takes in Suno, pick one. Then measure the locked WAV: stems, a beat grid locked to the kick, and every sung word timestamped. Every cut, caption and flash later comes from these numbers, not from listening.
**What went wrong:** both times Suno skipped lines. Measuring caught it. Instead of fighting Suno, the missing line became on-screen type. And try one audio fix, then stop. Five attempts at a whispered ending were all worse than the original.

### 4. Write the world bible and lock the references
Characters, wardrobe, props, sets, colour rules, what never appears. Then lock the look as images: a face anchor for the lead, a headless outfit plate, an expression sheet, a sheet for every recurring character, prop and set.
**What went wrong:** on the sequel, the recovery pod went through nine designs and ate about $25–30 of a $56 stills budget. The prompts kept passing old pod images as references, so old shapes leaked into every new design. The fix: one locked sheet per design before any scene shot, a written list of retired references, and a check on which references each prompt actually sends.

### 5. Storyboard on the beat map, as data
Every shot gets an id, a bar, a start time, a length, the story beat, the action, the camera and its references. Keep it as a small data file and build the readable storyboard from it with a script that checks the order, the total length, the shortest shot and that every plate exists. Write every prompt before spending anything.

### 6. Approve the story on stills, with the music playing
Generate a still per shot (cents each). Then review them as an animatic: a page where the song plays, each shot's still comes up on a monitor, and the shots sit on a timeline to scale. Tap OK, Change or Cut and leave notes. Make it autosave. I lost a round of notes to a Save button once.
This was the best new thing on the sequel. It felt like working with a creative team.

### 7. Give every world a camera
Before any video, write a DOP plan. Tag each shot by the world it's in and give each world one film reference, lens, height and move. Mine: Interstellar as the house look, Dune for the watched shots, Blade Runner 2049 for the red void, First Man for the crew on Earth. Most camera and acting calls are then already made.

### 8. Test the models, then animate
Test 2 shots on 2–3 video models first (about $11). Then animate the approved stills with the winner. Keep prompts short: the camera and the beat in plain words, no character names, and add detail only to fix a failure.
**What went wrong:** $13.10 on reference-mode clips that looked like motion graphics. The fix: start frames by default.

### 9. Check everything before the director sees it
The producer checks every take against a written list: direction of movement, faces in frame, colours per canon, scale, hands. Fix what's free in post (recolours, crops, paint-outs) before paying for a re-roll. The mascot kept coming out huge, so scale is on the list now. One time I just fixed it in Photoshop myself.

### 10. Anything that must be exact is code
HUDs, titles, countdowns and captions are Python, not AI images: a dot-matrix font defined as data plus small generators. On the sequel, the lyric types itself into a HUD in sync with the vocal, because the singer is wearing an oxygen mask. A change is one line and a re-render.

### 11. Edit on the beat map, review every cut
Assemble in Premiere on the beat grid. Every rough cut gets a review page: the cut plays next to a card per shot with Keep, Fix, Re-roll or Trim, timed notes, and a list of what changed since the last cut. The producer reads the decisions back and makes the next cut. After picture lock, generate an After Effects build script from the beat map for punch-zooms, flashes and lyric layers. Then grade by hand.

### 12. Deliver and launch
16:9 master, 9:16 Reel (crop and re-flow the graphics, no blurred backgrounds), covers with all text inside the centre 1080×1350 so Instagram's grid doesn't cut it, an SRT, thumbnails, and posts written in your own voice. Post them yourself.

## The numbers

| | To The Moon | Don't Let Go |
|---|---|---|
| Length | 1:15 | 1:30 |
| Time | About 2 days | About 3 days |
| Generation cost | About $137 | About $156 |
| Shots in the cut | 38 | 59 |
| Stills | About 280 | 400+ |
| How we worked | One long chat | One main session, helpers, shared files |

Cheapest wins: a Seedream still is about 6 cents, a Hailuo clip about 8 cents, and code graphics and free fixes cost nothing.

## Rules I hold to
- No real person's likeness and no brand logos, in prompts or outputs.
- Quote the cost and get a yes before any paid batch.
- API keys live in an env file and never appear in a chat or a file.
- The producer never posts, messages or signs in on my behalf.
- Never invent set pieces I didn't ask for.
- The shots the film is built around never get replaced.

## What still needs a person
Faces drift without a locked reference on every generation. Scale breaks in new sets. Designs that change mid-shoot get expensive. And taste: the model offers, but it doesn't know when something is right. That call is the director's every time.
