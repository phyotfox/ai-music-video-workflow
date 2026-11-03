# Suno guide

Contents: 1 Fields · 2 Style recipes · 3 Section cues · 4 Exclude bank · 5 Settings · 6 Rounds · 7 Fixing takes · 8 Export · 9 Browser automation · 10 Known behaviours

## 1. Fields

**Lyrics** (≤5,000 chars; ~1,800–2,200 for a 3-min song, ~900–1,200 for 60–75 s)
- Section cues in `[Square Brackets]`, one per line, written as performance notes:
  `[Verse - spoken, cool and deadpan, every word crisp, rhymes land on the bar ends]`
  `[Break - no drums, a glassy pad and her voice alone, tender]`
- Suno does not sing brackets. It **does** sing `(parentheses)`: use them on purpose for crowd echoes and ad-libs: `TO THE MOON! (to the moon)`, `(ha-ha)`.
- CAPS = shouted/chanted lines.
- Respell words Suno mispronounces; avoid brand names and hard proper nouns in sung lines.

**Style** (≤1,000 chars). No artist, label or brand names (Suno strips them or blocks the generation). Translate a reference into a description:
"deadmau5" → "ethereal progressive house, long evolving pads, a rolling plucked arpeggio that builds and blooms".

**Exclude**: a comma list of what would ruin the track (bank below).

**Title**: include a version tag so takes stay traceable: `Song (D1 S2)` = lyric draft 1, style 2; `(D2 cover, intercom)` = what changed.

## 2. Style recipes

Formula: `[genre blend], [BPM], [key/mode]. [drums + bass + signature synth]. [Vocal: verse delivery; hook delivery; pre-drop]. [Break description]. [Arrangement shape + ending]. [3–4 mood words], never harsh.`

- Name **two voices** (verse vs hook) so Suno separates sections.
- Ask for the **key** when you'll layer sound effects that have a key (system sounds, chimes). It's a request, not a guarantee: measure the take.
- Ask for a **hard stop into silence** if the video needs a black beat.
- "never harsh" / "glossy" keeps mixes listenable; "bouncy" alone noticeably lifts verse energy.

Examples:
- Melodic techno × K-pop: "Hard-hitting K-pop dance track built on melodic techno, 128 BPM, minor key. Punchy four-on-the-floor kick, rolling arpeggiated bassline, bright supersaw lift into each drop with a big snare build. Female vocals: confident, cool half-spoken verses with swagger; a shouted group chant hook with a crowd answering every line; a soaring sung pre-drop with long held notes. The break drops to a glassy pad and her soft, tender voice alone. Tight arrangement: intro, verse, drop, break, final drop, hard stop into silence. Glossy, bouncy, euphoric, a little bittersweet, never harsh."
- Y2K garage → trance: "Bouncy UK garage into euphoric trance, 130 BPM, C minor verses lifting to E-flat major choruses. Verses ride a shuffled 2-step beat… choruses switch to a four-on-the-floor kick with soft supersaw pads… glassy bell chimes. Verses: playful, close, warm female spoken voice… Sunny, nostalgic, light on its feet, never harsh."
- Electroclash: "Electroclash techno… deadpan, clipped female spoken verses with intimate whispered asides rise into euphoric sung choruses answered by stacked crowd shouts; dry analog kick, rolling acid bassline… a rising siren synth on the builds… 128 BPM hypnotic 4/4 pulse."

## 3. Section cue vocabulary

`[Intro - filtered pad, soft whisper close to the mic]` · `[Verse - spoken/rapped/sung, …]` · `[Intercom - voice through a crackly cockpit intercom loudspeaker, telephone-filtered, cheeky, laughs under her breath]` · `[Pre-Drop - sung, rising, long held notes, the beat drops out]` · `[Drop - shouted chant hook, a crowd answers each line, euphoric supersaw lift]` · `[Break - no drums, glassy pad, her voice alone, tender]` · `[Build - riser, the kick returns]` · `[Final Drop - bigger, the crowd doubles]` · `[Stop - one bar of total silence]` · `[End - whispered, no music]`

Suno follows cue *character* well (filtered, whispered, shouted) and cue *length* loosely ("half a bar" → a bar), and it may skip a short section entirely. Always check the result (the analysis script flags unsung lines).

## 4. Exclude bank

Pick what fits: `rap, male lead vocal, mumbled vocals, rock guitar, acoustic guitar, orchestral strings, dubstep wobble, big room EDM, hardstyle, distorted kick, airhorn, laser zaps, trap hi-hats, heavy autotune, pitched-up chipmunk vocals, pitched vocal chops, lo-fi, vinyl crackle, glitch effects, long intro`.

## 5. Settings (Advanced mode)

- Model: latest (v6 at time of writing).
- **Vocal gender**: set it.
- **Duration**: Custom, type e.g. `1:05` in its text box. Takes land within a few seconds.
- Weirdness / Style influence: 50% default is fine. Raise style influence (~65–75%) if takes ignore the style.
- **Audio influence** (Cover / audio uploads): ~60–70% stays close to the source; 25% is loose.
- Max Mode, Personalize: off unless the director wants them.
- A saved **Voice** (Pro) keeps the same singer across a series of videos.

## 6. Rounds

- Round 1: 2 styles × 2 takes (each Create = 2 takes).
- Later rounds: change one thing at a time (a cue word, one style clause, audio influence).
- Log every take: title · style · length · director's note. The director often generates their own variant and picks it; that's normal, so log it too.

## 7. Fixing takes (smallest fix first)

- **Cover** (⋯ → Remix → Cover): re-performs the liked take with your updated lyrics/cues. Use for delivery changes in one section. Choose "Keep Current" styles when asked to overwrite.
- **Song Editor → Replace Section** (Pro): regenerate only a time range with new lyrics + a section-only style.
  1. ⋯ → Edit → Open in Editor (wait until "Clips analyzing" disappears).
  2. Hide the Learn tips. Drag-select **on the song lane** itself. "Replace from mm:ss–mm:ss" shows the range; Smart snaps to the beat.
  3. Click **Replace Lyrics** → type the new lines with a cue → edit Styles for that section.
  4. Click **Replace** (≈4 credits) → *Alternates* box shows 2 versions → director auditions → **Insert/Commit** → **Save as New Song** (keeps the original).
  - The new section may run longer than the selection, so the song gets longer.
  - Saving re-renders the whole track: no timing from the old file carries over.
- **Extend**: add more song after a point. **Crop / Remove Section / Fade**: in the same Edit menu.
- **Get Stems** (Pro) gives official stems; the analysis script's htdemucs stems are usually good enough.

## 8. Export

- ⋯ → Download → choose WAV (Pro) for the master; M4A/MP3 otherwise. "Unlock & Download" uses one of the plan's monthly downloads; afterwards that song re-downloads free in any format.
- An M4A from Suno can embed the lyrics **as Suno aligned them** (subtitle track + `lyrics` tag). The analysis script extracts it. It reveals skipped and repeated lines.
- After re-singing a word in the editor, export with **BPM lock OFF**, or the timing drifts (up to 0.7 s seen).

## 9. Browser automation (driving the user's logged-in Suno)

- The user logs in themselves. Never type credentials. Cloudflare checkboxes are theirs to tick; after a hand-off, don't reload the page.
- Go to `suno.com/create` → click **Advanced**.
- **Lyrics editor** is a contenteditable DIV: form-filling fails. Click into it and type (newlines work). To replace existing lyrics: click, Cmd/Ctrl+A, Delete, type.
- **Styles** textarea and **Song Title** input accept direct value setting.
- **More Options**: Exclude styles (input: click + type), Vocal Gender buttons, Duration ("Custom" then the duration text box: triple-click, type `1:05`, Enter), sliders (drag; form input doesn't work on them).
- **Create** spends credits: only press it for the round the director agreed to.
- Track list: the newest takes appear at the top. ⋯ opens Remix / Edit / Download. Hover menus close easily: open ⋯, click "Edit", then find the item by name rather than clicking coordinates.
- Clicking a track thumbnail plays it (the director may hear it): pause it if you started it by accident.
- Downloads go to the user's Downloads folder. Ask them to move the file into the project, then verify its name and duration.

## 10. Known behaviours

- Tempo runs 3–6% fast vs the request (ask 128, get ~134) and can drift within a song.
- Short or quiet sections (a 2-line break) are the ones most often skipped.
- Lines may be repeated (a verse line sung twice).
- Requested key changes often don't happen.
- Free plan: Remix/Cover, Extend, Crop and Remove Section are available; Replace Section, Get Stems, WAV, Remaster and the Editor need Pro.
