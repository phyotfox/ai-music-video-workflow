#!/usr/bin/env python3
"""
analyze_song.py — turn a finished song file into edit-ready timing data.

What it produces (in --out):
  stems/vocals.wav, drums.wav, bass.wav, other.wav   (htdemucs separation)
  analysis/beatmap.json   beats, bar downbeats, per-bar energy, sections, words
  analysis/words.json     every sung word with start/end and bar.beat
  analysis/embedded-lyrics.srt   (only if the file carries Suno's timed lyrics, e.g. .m4a)
  TIMING.md               human-readable summary: tempo, bar table, sections, lyrics as sung

Usage:
  python3 analyze_song.py SONG.wav --out PROJECT/audio [--lyrics LYRICS.txt] [--no-stems] [--whisper small]

Method (why it works this way):
  * Suno tempos drift and often run 3–6% faster than requested, so we never assume a fixed BPM.
  * The grid is anchored on the KICK (drums stem), not the full mix: full-mix beat trackers lock
    onto hi-hats and land early. Runs of evenly spaced kicks give the most reliable beats.
  * Sections without kicks get their tempo from bass/synth onsets, constrained near the kick tempo,
    and gaps between kick runs are filled with a whole number of beats so the grid re-locks.
  * The first beat of each kick run is assumed to be a bar downbeat (true for most dance songs).
    Check the drop downbeat by ear once; everything else follows.
  * Word timing uses Whisper on the vocal stem in overlapping windows, because a single pass
    tends to skip shouted chant sections.

Dependencies (installed on demand): librosa soundfile torch demucs==4.0.1 openai-whisper, plus ffmpeg.
"""
import argparse, json, os, subprocess, sys, shutil

def pip(*pkgs, index=None):
    cmd = [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages"]
    if index: cmd += ["--index-url", index]
    subprocess.run(cmd + list(pkgs), check=False)

def ensure_deps(need_stems, need_words):
    try:
        import librosa, soundfile  # noqa
    except ImportError:
        pip("librosa", "soundfile")
    if need_stems or need_words:
        try:
            import torch  # noqa
        except ImportError:
            pip("torch", "torchaudio", index="https://download.pytorch.org/whl/cpu")
    if need_stems:
        try:
            import demucs  # noqa
        except ImportError:
            # demucs>=4.1 pulls a dependency that often fails to build; 4.0.1 + its deps works.
            pip("demucs==4.0.1", "--no-deps")
            pip("dora-search", "einops", "julius", "lameenc", "openunmix", "pyyaml", "tqdm")
    if need_words:
        try:
            import whisper  # noqa
        except ImportError:
            pip("openai-whisper")

def to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ar", "44100", "-ac", "2", dst], check=True)

def extract_embedded_lyrics(src, dst):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-map", "0:s:0", dst],
                       capture_output=True)
    return r.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 0

def separate(wav, stems_dir):
    import torch, soundfile as sf
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    y, sr = sf.read(wav, always_2d=True)
    m = get_model("htdemucs"); m.eval()
    x = torch.tensor(y.T, dtype=torch.float32)
    ref = x.mean(0); x = (x - ref.mean()) / ref.std()
    with torch.no_grad():
        out = apply_model(m, x[None], device="cpu", split=True, overlap=0.25, progress=False)[0]
    out = out * ref.std() + ref.mean()
    os.makedirs(stems_dir, exist_ok=True)
    for name, s in zip(m.sources, out):
        sf.write(os.path.join(stems_dir, f"{name}.wav"), s.numpy().T, sr)  # soundfile: avoids torchaudio/torchcodec save issues

def kick_times(drums_wav):
    import numpy as np, librosa
    y, sr = librosa.load(drums_wav, sr=22050)
    hop = 64
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop)); f = librosa.fft_frequencies(sr=sr, n_fft=1024)
    env = S[(f > 30) & (f < 110)].sum(0)
    flux = np.maximum(0, np.diff(env, prepend=env[0])); t = np.arange(len(flux)) * hop / sr
    if flux.max() <= 0: return np.array([])
    pk = librosa.util.peak_pick(flux, pre_max=40, post_max=40, pre_avg=80, post_avg=80,
                                delta=np.percentile(flux, 98.5) * 0.35, wait=60)
    return t[pk]

def regular_runs(k, min_intervals=6, tol=0.03):
    import numpy as np
    if len(k) < min_intervals + 1: return []
    d = np.diff(k); med = np.median(d)
    runs, s = [], 0
    for i, ok in enumerate(np.abs(d - med) < tol):
        if not ok:
            if i - s >= min_intervals: runs.append((s, i))
            s = i + 1
    if len(d) - s >= min_intervals: runs.append((s, len(d)))
    return [(float(k[a]), float(k[b]), b - a) for a, b in runs]   # start, end, number of beat intervals

def fit_period(onsets, p_ref, spread=0.04):
    """Best beat period near p_ref from onset times (16th-note grid phase coherence)."""
    import numpy as np
    if len(onsets) < 8: return p_ref
    best = (-1, p_ref)
    for p in np.linspace(p_ref * (1 - spread), p_ref * (1 + spread), 400):
        st = p / 4
        ph = np.angle(np.mean(np.exp(2j * np.pi * onsets / st))); off = (-ph / (2 * np.pi)) * st % st
        r = ((onsets - off + st / 2) % st) - st / 2
        sc = np.mean(np.abs(r) < 0.012)
        if sc > best[0]: best = (sc, p)
    return best[1]

def build_grid(stems_dir, mix_wav, dur):
    import numpy as np, librosa
    k = kick_times(os.path.join(stems_dir, "drums.wav"))
    runs = regular_runs(k)
    ons = []
    for s in ("drums", "bass", "other"):
        p = os.path.join(stems_dir, f"{s}.wav")
        if os.path.exists(p):
            y, sr = librosa.load(p, sr=22050)
            ons.append(librosa.onset.onset_detect(y=y, sr=sr, hop_length=128, units="time"))
    ons = np.sort(np.concatenate(ons)) if ons else np.array([])
    notes = []
    if not runs:
        y, sr = librosa.load(mix_wav, sr=22050)
        _, b = librosa.beat.beat_track(y=y, sr=sr, units="time", tightness=300)
        notes.append("No steady kick found: grid from a full-mix beat tracker (less reliable). Check downbeats by ear.")
        beats = list(b); downs = beats[::4]
        return beats, downs, runs, notes
    beats = []
    # each run: evenly spaced from its own kicks
    run_periods = [(e - s) / n for s, e, n in runs]
    p0 = run_periods[0]
    # before first run: extend backwards with tempo fitted on onsets before it
    s0 = runs[0][0]
    pre = fit_period(ons[ons < s0 - 0.05], p0)
    n_pre = int(s0 // pre)
    beats += [s0 - i * pre for i in range(n_pre, 0, -1)]
    for idx, ((s, e, n), p) in enumerate(zip(runs, run_periods)):
        beats += [s + i * p for i in range(n)]
        nxt = runs[idx + 1][0] if idx + 1 < len(runs) else None
        if nxt is not None:
            gap = nxt - e
            nb = max(1, round(gap / p))
            gp = gap / nb
            beats += [e + i * gp for i in range(nb)]
        else:
            post = fit_period(ons[ons > e + 0.05], p)
            t = e
            while t < dur: beats.append(t); t += post
    beats = sorted(b for b in beats if b >= 0)
    # downbeats: every 4th beat counted from the first run's first kick
    import bisect
    a = min(range(len(beats)), key=lambda i: abs(beats[i] - s0))
    downs = [beats[i] for i in range(a % 4, len(beats), 4)]
    notes.append(f"Kick runs (steady four-on-the-floor): " + ", ".join(f"{s:.2f}–{e+p:.2f}s" for (s, e, n), p in zip(runs, run_periods)))
    notes.append("Downbeats assume each kick run starts on beat 1. Check the drop downbeat by ear once.")
    return beats, downs, runs, notes

def bar_energy(stems_dir, downs, dur):
    import numpy as np, librosa
    out = []
    E = {}
    for s in ("drums", "vocals", "bass", "other"):
        y, sr = librosa.load(os.path.join(stems_dir, f"{s}.wav"), sr=22050)
        r = librosa.feature.rms(y=y, hop_length=512)[0]; t = librosa.times_like(r, sr=sr, hop_length=512)
        E[s] = (r, t)
    edges = list(downs) + [dur]
    for i in range(len(downs)):
        a, b = edges[i], edges[i + 1]
        row = {"bar": i + 1, "t": round(a, 3)}
        for s, (r, t) in E.items():
            m = (t >= a) & (t < b); row[s] = round(float(r[m].mean()) if m.any() else 0.0, 4)
        out.append(row)
    # normalise and label
    import numpy as np
    for s in ("drums", "vocals"):
        mx = max(x[s] for x in out) or 1
        for x in out: x[s + "_n"] = x[s] / mx
    for x in out:
        x["label"] = ("kick" if x["drums_n"] > 0.45 else "light drums" if x["drums_n"] > 0.12 else "no drums") + \
                     (" + vocal" if x["vocals_n"] > 0.15 else "")
    return out

def sections_from_bars(bars):
    """Group bars by drum state (kick / light / none); 1-bar blips are absorbed into the previous section."""
    def drum(x): return x["label"].split(" + ")[0]
    secs = []
    for x in bars:
        if secs and secs[-1]["drums"] == drum(x):
            secs[-1]["end_bar"] = x["bar"]; secs[-1]["vocal_bars"] += "vocal" in x["label"]
        else:
            secs.append({"drums": drum(x), "start_bar": x["bar"], "end_bar": x["bar"], "start": x["t"],
                         "vocal_bars": int("vocal" in x["label"])})
    merged = []
    for i, s in enumerate(secs):
        prev = secs[i - 1]["drums"] if i else None
        nxt = secs[i + 1]["drums"] if i + 1 < len(secs) else None
        if merged and s["end_bar"] == s["start_bar"] and prev is not None and prev == nxt:
            merged[-1]["end_bar"] = s["end_bar"]; merged[-1]["vocal_bars"] += s["vocal_bars"]; continue
        if merged and merged[-1]["drums"] == s["drums"]:
            merged[-1]["end_bar"] = s["end_bar"]; merged[-1]["vocal_bars"] += s["vocal_bars"]; continue
        merged.append(dict(s))
    for s in merged:
        n = s["end_bar"] - s["start_bar"] + 1
        s["label"] = f"{s['drums']}, vocals in {s['vocal_bars']}/{n} bars"
    return merged

def transcribe(vocals_wav, dur, model_name, lyrics_text):
    """Split the vocal stem into voiced chunks (<=20 s, cut at pauses), transcribe each chunk on its own,
    then offset the times. Short clips stop Whisper from skipping shouted chants or hallucinating over
    instrumental bleed. Non-word junk and very low-confidence words are dropped."""
    import re, numpy as np, librosa, whisper
    m = whisper.load_model(model_name)
    prompt = lyrics_text[:800] if lyrics_text else None
    ok = re.compile(r"^[A-Za-z0-9'’,.!?()\-]+$")
    y, sr = librosa.load(vocals_wav, sr=16000)
    hop = 320  # 20 ms
    r = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
    voiced = r > 0.08 * np.percentile(r, 95)  # low threshold: filtered/whispered lines are quiet next to chants
    # voiced regions, bridging pauses shorter than 0.5 s
    regs, on = [], None
    for i, v in enumerate(voiced):
        t = i * hop / sr
        if v and on is None: on = t
        if not v and on is not None:
            regs.append([on, t]); on = None
    if on is not None: regs.append([on, len(y) / sr])
    bridged = []
    for a_, b_ in regs:
        if bridged and a_ - bridged[-1][1] < 0.5: bridged[-1][1] = b_
        elif b_ - a_ > 0.15: bridged.append([a_, b_])
    # split long regions at the quietest moment between 8 and 18 s in, so no chunk exceeds ~18 s
    def quietest(a_, b_):
        i0, i1 = int(a_ * sr / hop), int(b_ * sr / hop)
        return (i0 + int(np.argmin(r[i0:i1]))) * hop / sr
    split = []
    for a_, b_ in bridged:
        while b_ - a_ > 18:
            c = quietest(a_ + 8, a_ + 18); split.append([a_, c]); a_ = c
        split.append([a_, b_])
    chunks = []
    for a_, b_ in split:
        if chunks and b_ - chunks[-1][0] <= 18 and a_ - chunks[-1][1] < 1.5: chunks[-1][1] = b_
        else: chunks.append([a_, b_])
    words = []
    for a_, b_ in chunks:
        s0, s1 = max(0, a_ - 0.3), min(len(y) / sr, b_ + 0.3)
        clip = y[int(s0 * sr):int(s1 * sr)].astype(np.float32)
        # No initial_prompt here: on short sung clips a lyrics prompt makes Whisper hallucinate junk tokens.
        res = m.transcribe(clip, word_timestamps=True, language="en", fp16=False, temperature=0.0,
                           condition_on_previous_text=False)
        for seg in res["segments"]:
            for w in seg.get("words", []):
                txt = w["word"].strip()
                if ok.match(txt) and w.get("probability", 0) >= 0.15:
                    words.append({"w": txt, "s": round(s0 + w["start"], 3), "e": round(s0 + w["end"], 3),
                                  "p": round(w.get("probability", 0), 2)})
    words.sort(key=lambda x: x["s"])
    return words

def barpos(t, downs):
    import bisect
    i = max(0, bisect.bisect_right(downs, t) - 1)
    nxt = downs[i + 1] if i + 1 < len(downs) else downs[i] + (downs[i] - downs[i - 1] if i else 1.8)
    return f"{i + 1}.{1 + (t - downs[i]) / ((nxt - downs[i]) / 4):.1f}"

def lyric_check(lyrics_text, words):
    """Flag intended lyric lines that the transcript barely contains — catches skipped sections
    (e.g. a break Suno decided not to sing) before anyone storyboards around them."""
    import re
    if not lyrics_text or not words: return []
    norm = lambda x: re.sub(r"[^a-z']", "", x.lower())
    heard = [norm(w["w"]) for w in words]
    out, seen = [], set()
    for line in lyrics_text.splitlines():
        line = re.sub(r"\(.*?\)", "", line).strip()
        if not line or line.startswith("["): continue
        toks = [norm(t) for t in line.split() if norm(t)]
        if not toks or line in seen: continue
        seen.add(line)
        hit = sum(1 for t in toks if t in heard) / len(toks)
        if hit < 0.5: out.append((line, hit))
    return out

def write_timing_md(path, src, dur, beats, downs, bars, secs, words, notes, missing=()):
    import numpy as np
    bpm = 60 / np.median(np.diff(beats)) if len(beats) > 2 else 0
    L = [f"# TIMING — {os.path.basename(src)}", "",
         f"Duration {dur:.2f} s · median tempo ≈ {bpm:.1f} BPM · {len(downs)} bars. Cut on the beat map, not a fixed BPM.", ""]
    L += [f"- {n}" for n in notes] + ["", "## Bar downbeats (s)", "", "| Bar | Time | Energy |", "|---|---|---|"]
    for b in bars: L.append(f"| {b['bar']} | {b['t']:.2f} | {b['label']} |")
    L += ["", "## Sections (auto, by drum/vocal energy — rename them by ear)", "", "| Bars | Start | What's there |", "|---|---|---|"]
    for s in secs: L.append(f"| {s['start_bar']}–{s['end_bar']} | {s['start']:.2f} | {s['label']} |")
    if missing:
        L += ["", "## ⚠ Lyric lines that may NOT have been sung", "",
              "Check these by ear. If a section was skipped, fix it in the song (e.g. Suno Replace Section) before planning shots around it.", ""]
        L += [f"- \"{l}\" ({int(h*100)}% of its words heard)" for l, h in missing]
    if words:
        L += ["", "## Lyrics as sung (Whisper on the vocal stem, ±0.1 s; check spellings against LYRICS.md)", ""]
        line, last = [], None
        for w in words:
            if last is not None and w["s"] - last > 0.9 and line:
                L.append(f"- {line[0][1]:.2f}s (bar {barpos(line[0][1], downs)}): " + " ".join(x[0] for x in line)); line = []
            line.append((w["w"], w["s"])); last = w["e"]
        if line: L.append(f"- {line[0][1]:.2f}s (bar {barpos(line[0][1], downs)}): " + " ".join(x[0] for x in line))
    open(path, "w").write("\n".join(L) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--out", required=True)
    ap.add_argument("--lyrics", help="text file with the intended lyrics (improves word recognition)")
    ap.add_argument("--no-stems", action="store_true", help="reuse existing OUT/stems")
    ap.add_argument("--no-words", action="store_true")
    ap.add_argument("--whisper", default="small")
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "analysis"), exist_ok=True)
    ensure_deps(not a.no_stems, not a.no_words)
    import numpy as np, librosa
    work = os.path.join("/tmp", "analyze_song_work"); os.makedirs(work, exist_ok=True)
    wav = os.path.join(work, "song.wav"); to_wav(a.song, wav)
    dur = float(librosa.get_duration(path=wav))
    srt = os.path.join(out, "analysis", "embedded-lyrics.srt")
    has_srt = extract_embedded_lyrics(a.song, srt)
    stems = os.path.join(out, "stems")
    if not a.no_stems: print("separating stems…", flush=True); separate(wav, stems)
    print("building beat grid…", flush=True)
    beats, downs, runs, notes = build_grid(stems, wav, dur)
    bars = bar_energy(stems, downs, dur); secs = sections_from_bars(bars)
    words = []
    lyr = open(a.lyrics).read() if a.lyrics and os.path.exists(a.lyrics) else None
    if not a.no_words:
        print("timing words…", flush=True)
        words = transcribe(os.path.join(stems, "vocals.wav"), dur, a.whisper, lyr)
        for w in words: w["bar"] = barpos(w["s"], downs)
    if has_srt: notes.append("Suno's own timed lyrics were embedded in the file: analysis/embedded-lyrics.srt (shows what was actually sung, incl. skipped/repeated lines).")
    bm = {"source": os.path.basename(a.song), "duration": round(dur, 3),
          "beats": [round(b, 3) for b in beats], "downbeats": [round(d, 3) for d in downs],
          "bars": bars, "sections": secs, "words": words, "notes": notes,
          "kick_runs": [{"start": round(s, 3), "end": round(e, 3), "intervals": n} for s, e, n in runs]}
    json.dump(bm, open(os.path.join(out, "analysis", "beatmap.json"), "w"), indent=1)
    json.dump(words, open(os.path.join(out, "analysis", "words.json"), "w"), indent=1)
    missing = lyric_check(lyr, words)
    if missing: bm["possibly_unsung_lines"] = [l for l, _ in missing]
    json.dump(bm, open(os.path.join(out, "analysis", "beatmap.json"), "w"), indent=1)
    write_timing_md(os.path.join(out, "TIMING.md"), a.song, dur, beats, downs, bars, secs, words, notes, missing)
    print(f"done: {len(beats)} beats, {len(downs)} bars, {len(words)} words → {out}")

if __name__ == "__main__":
    main()
