"""Storyboard as data. Edit SHOTS, then run: python3 storyboard_data.py
Writes STORYBOARD.md + storyboard/storyboard.json and stops with an error if a check fails."""
import json, os, sys

SONG_LENGTH = 90.0   # seconds, from audio/analysis/beatmap.json
BPM = 128.0
BEAT = 60 / BPM
MAX_LIPSYNC = 3

# id, start (s), story beat, action, camera, references (ids from CANON), flags
SHOTS = [
    ("S01", 0.0, "Hook: she floats in red", "Slow drift, hair moving", "Static close-up, slow push", ["face-anchor", "outfit"], {}),
    ("S02", 3.75, "Title card", "Dot-matrix title types on", "Code graphic", [], {"code": True}),
    ("S03", 7.5, "She sings the first line", "Lip-sync on the vocal", "Locked medium close-up", ["face-anchor"], {"lipsync": True}),
    ("S04", 11.25, "End frame", "Fade to black", "Hold", [], {}),
]
ANCHORS = {"S01"}   # shots the film is built around: never replaced or reordered

def build():
    ids = [s[0] for s in SHOTS]
    starts = [s[1] for s in SHOTS]
    errors = []
    if len(set(ids)) != len(ids): errors.append("duplicate shot ids")
    if starts != sorted(starts): errors.append("shots are out of order")
    if starts and starts[0] != 0: errors.append("first shot must start at 0")
    if not ANCHORS <= set(ids): errors.append(f"anchor shots missing: {sorted(ANCHORS - set(ids))}")
    if sum(1 for s in SHOTS if s[6].get("lipsync")) > MAX_LIPSYNC: errors.append(f"more than {MAX_LIPSYNC} lip-sync shots")
    rows = []
    for i, (sid, t, beat, action, camera, refs, flags) in enumerate(SHOTS):
        end = SHOTS[i + 1][1] if i + 1 < len(SHOTS) else SONG_LENGTH
        if end - t < BEAT - 1e-6: errors.append(f"{sid} is shorter than one beat")
        rows.append({"id": sid, "start": t, "end": end, "length": round(end - t, 3), "bar": int(t / (4 * BEAT)) + 1,
                     "beat": beat, "action": action, "camera": camera, "refs": refs, **flags})
    if errors: sys.exit("Storyboard checks failed:\n- " + "\n- ".join(errors))
    os.makedirs("storyboard", exist_ok=True)
    json.dump(rows, open("storyboard/storyboard.json", "w"), indent=1)
    md = ["# STORYBOARD (built from storyboard_data.py; edit the data, not this file)", "",
          "| Shot | Bar | In | Len | Beat | Action | Camera | Refs |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {r['id']}{' ★' if r['id'] in ANCHORS else ''} | {r['bar']} | {r['start']:.2f} | {r['length']:.2f} | {r['beat']} | "
           f"{r['action']} | {r['camera']} | {', '.join(r['refs'])} |" for r in rows]
    open("STORYBOARD.md", "w").write("\n".join(md) + "\n")
    print(f"{len(rows)} shots, {SONG_LENGTH:.1f} s, checks passed")

if __name__ == "__main__":
    build()
