# AI music video workflow

How I made two AI music videos, **To The Moon** and **Don't Let Go**, with Claude as my producer while I directed. This repo has the whole method: a step-by-step guide anyone can follow, two Claude skills that run it, and blank templates for your own project.

**Start here: [WORKFLOW.md](WORKFLOW.md)**

## What's in here

| Folder | What it is | Who it's for |
|---|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | The 12-step workflow, with costs and what went wrong | Anyone, whatever AI tool you use |
| [`skills/`](skills) | Two Claude skills: `ai-music-video-studio` (the film) and `ai-song-production` (the song), with their scripts | Claude users |
| [`downloads/`](downloads) | The same skills as `.skill` files, ready to install | Claude users |
| [`templates/`](templates) | Blank `CLAUDE.md`, `BRIEF.md`, `CANON.md`, `CAMERA.md`, run log, handoff log and a storyboard builder | Anyone starting a project |

## Install the skills

- **Claude app:** upload the `.skill` files from `downloads/` in your Skills settings.
- **Claude Code:** copy the folders in `skills/` into `~/.claude/skills/` (or your project's `.claude/skills/`).

Then copy `templates/` into a new project folder, fill in `CLAUDE.md` and `BRIEF.md`, and ask Claude to start a music video.

## What you need

- A Leonardo API key for generation. Keep it in an env file (`leo_env.txt`), loaded with `set -a; . ./leo_env.txt; set +a`. Never paste it into a chat or commit it. `.gitignore` already excludes it.
- Suno, which you drive yourself in the browser.
- Python 3 with Pillow, NumPy and OpenCV, plus ffmpeg. `analyze_song.py` installs its own audio dependencies the first time it runs (about 5 minutes).
- Premiere Pro and After Effects for the finish (optional).

## The films

- To The Moon (2026): [case study](https://silly-independence-136547.framer.app/lab/to-the-moon)
- Don't Let Go (2026): [link to come]

Made by [Phyo Thu](https://x.com/phyofox). The code and text are MIT licensed (see [LICENSE](LICENSE)). The films, songs and images from the projects aren't part of this repo and stay mine.
