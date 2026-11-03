# Leonardo API notes (as of November 2026)

Client: `scripts/leo.py`. Load the key first: `set -a; . /path/.leo_env; set +a` (never echo it).

```
python3 leo.py upload --prompt /abs/path/image.png          -> {"uploadedId": ...}
python3 leo.py still  --model seedream-5.0-pro --aspect 9:16 --ref ID:HIGH:UPLOADED --prompt "..." --out DIR --slug NAME
python3 leo.py video  --model kling-3.0 --start-image-id ID --duration 5 --prompt "..." --out DIR --slug NAME
python3 leo.py poll --gen-id GEN --out DIR --slug NAME
python3 leo.py balance
```
`--ref id:STRENGTH:TYPE` — TYPE is GENERATED (a Leonardo generation id) or UPLOADED (an upload id). Order is kept.

## Models used and what each is for

| Model id | Use | Sizes | Approx. cost |
|---|---|---|---|
| `seedream-5.0-pro` | Storyboard plates, character-consistent stills, 2K output for reframing | 16:9 2048×1152, 9:16 1152×2048, 4:5 1632×2048, 2:3 1344×2016 | ~$0.06 (16:9), ~$0.08 (2:3) |
| `gemini-image-2` (Nano Banana Pro) | Surgical edits on an approved frame; recomposing a 16:9 frame to 9:16 | 16:9 1376×768, 9:16 768×1376, 2:3, 3:2, 1:1 | ~$0.21 |
| `openai/gpt-image-2.5-sunburst` | Cheap explorations (drifts on identity) | 16:9 1376×768, 9:16 768×1376 | ~$0.02–0.05 |
| `bytedance/seedance-2.5` | Character motion in reference mode; lip-sync with song audio | 1280×720, 1920×1080, **720×1280 vertical**; duration 4–30 s | ~$1.30–1.64 per 5 s |
| `kling-3.0` | Start-frame animation, camera moves, FX | 1920×1080, 1080×1920, 1440×1440 | ~$1.3 per 5 s |
| `kling-4.0` | Start + end frame transitions, up to 10 refs, edits an existing clip | 1080p | ~$1.68 per 5 s |
| `hailuo-03` | Cheap no-reference shots (wides, inserts, dust, flares, liftoff). Native audio always on: strip it | 768p, 2k, 4k | ~$0.08 per clip (TURBO) |
| `alibaba/wan-3.0` | 1080p alternative with refs; best lip-sync on the sequel (via the web app). Faces can drift across shots | 1920×1080, 1080×1920 | ~$1.42 per 5 s |
| `bfl/flux-3-video` | Tested, not used: dearest, and the subject grew and walked out of frame | 1080p | ~$2.06 per 5 s |

Nano Banana silently falls back to 1:1 unless the width/height pair is exact — `leo.py` uses the exact pairs.

## Gotchas we hit

- **Seedance can't take a start frame and image references together.** It errors with "start_frame must NOT have
  more than 0 items; image_reference must NOT have more than 0 items". Use reference mode: `image_reference` with
  the approved still as order 1 (type GENERATED) and face/outfit/mascot sheets after it (type UPLOADED), and say in
  the prompt "Open on the exact frame and composition of reference image 1".
- Seedance vertical output is 720×1280 — upscale to 1080×1920 for the master; it's slightly softer.
- Reference-mode clips sometimes open on a slightly different composition for the first ~0.5 s. Trim from ~0.3–0.6 s.
- A recomposed (outpainted) frame can come out with stretched proportions (long neck/hands). Compare it with the
  original before animating; if it's off, crop the original instead.
- Prompts: describe only what's in frame, "no text, no letters, no logos" (unless the shot has intended text,
  e.g. a flag — then say "keep the words X exactly", "no other text"). `prompt_enhance` OFF, style None.
- Face lock: face anchor (HIGH) + expression sheet (MID) + headless outfit plate (MID) + set (MID). Outfit photos
  that include a face cause face drift.
- Wide shots drift on character scale — give them the same references as close-ups.
- Video poll: `GET /v1/generations/{id}` → `generations_by_pk.generated_images[0].motionMP4URL`.
- Long polls: keep each shell call under ~3 minutes; poll in short loops rather than one long wait.

## Budget from To The Moon (75 s film)
~280 stills, ~107 clips (38 used), 10 rough cuts: ~US$137 to picture lock, ~$144 with launch extras.

## Added on the sequel (November 2026)
- **Leonardo's API takes no audio upload.** Lip-sync shots were made by the user in Leonardo's web app (Wan 3.0
  looked best for lip motion and expressions). Cut the vocal sections from the word timings for them.
- Seedance 2.5 still refuses start frame + image references together. On the sequel it ran from the start frame
  for most shots and became the default.
- Send `motion_has_audio: false` on every non-lip-sync shot; the song is the audio. Kling returns an empty audio
  track anyway: strip it in the edit.
- Costs are not published; Leonardo returns the cost when a job is submitted. Check the spend cap before each
  submit with the known price.
- Seedream 5.0 Pro (2 takes ≈ $0.11) for every new frame. Krea 3 (4.5× the price) and FLUX.2 gave no realism gain.

## Budget from Don't Let Go (90 s film)
400+ stills, 80+ clips (59 shots used), 12 versions of the edit: ~US$156 in generation, of which ~$25–30 went on
the pod redesigns and $13.10 on unneeded reference-mode clips.
