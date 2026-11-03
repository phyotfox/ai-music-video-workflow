# Launch kit

Build the launch as a Claude Doc ("<Title>: launch plan") so nothing gets lost in chat: positioning, assets table,
per-platform copy, timeline, checklist, sources. Copy in the user's voice (see SKILL.md).

## Order and timing
- **X first** (native video, never a YouTube link). The AI-video scene lives there; SlopHits (slophits.com) charts
  X posts that contain "slopcore" and takes self-submissions of original songs.
- Post for US tech hours. The user is in New Zealand and sleeps at ~11 pm: post **6–8 am NZ** (≈ US midday the
  previous day) and reply to comments over breakfast. US daylight saving ends early November; recheck the offset.
- X's scheduler handles single posts with media. It can't schedule replies or quote-posts, and thread scheduling is
  unreliable — post the thread manually or with a third-party scheduler (Buffer, PostPaddy, OneUp, Fedica).
- **Technique thread** 3–24 h later as a **new post** (not a quote): post 1 with a comparison video, replies 2–N,
  the last post links to the launch post (a link with no media renders as an embedded post card). Optionally a final
  post linking the previous film. Then reply under the launch post linking to the thread.
- **YouTube** (Music category, AI disclosure = Yes, chapters from 0:00 each ≥10 s, lyrics, credits, pinned comment
  linking the making-of thread, end screen, Test & Compare with 3 thumbnails).
- **Instagram**: vertical Reel for reach + "full widescreen version on YouTube, link in bio" + a Story with a link
  sticker the same day. A process carousel a day or two later.

## Copy rules
- X posts ≤280 characters each (emoji and arrows count as 2; links count as 23). Put credits and tool tags in a
  reply, not the main post. Title format the scene uses: `SLOPCORE: TITLE` + `#slopcore`.
- Credit tools accurately: "Images and video made with the @LeonardoAi API (Seedream, Nano Banana, Seedance, Kling)",
  @claudeai, @suno. Check handles with the @-dropdown (verified accounts).
- Costs: quote USD; separate generation cost from Claude usage if the user wants the full figure.

## Platform specs
| Asset | Size | Safe area / notes |
|---|---|---|
| X video / thumbnail | 1920×1080 / 1600×900 | Keep key content central |
| YouTube thumbnail | 1280×720 | Big face + 2–4 words |
| Instagram Reel | 1080×1920 | UI covers ~250 px top, ~340 px bottom |
| Reel cover | 1080×1920 | Grid crops to **3:4** (centre 1080×1440); keep text in the centre **1080×1350** |
| Instagram feed | 1080×1350 | 4:5 |
| Captions | `.srt` | Plain filename, CRLF, ≤2 lines of ~32–40 chars |

## X thread page
`assets/x-thread-page-template.html` — one card per post with Copy text, live character count, the media to attach,
link boxes that fill placeholders ({LINK}, {OLD}), and a Posted tick. Publish it as an artifact with the media files
alongside (`media/…`). The viewer can't download files, so also tell the user where the media sit in their Drive.
