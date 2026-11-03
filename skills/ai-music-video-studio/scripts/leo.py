#!/usr/bin/env python3
"""
Leonardo.ai v2 generation helper for the cinematic-ai-visuals skill.

Submits on /api/rest/v2/generations, polls on /api/rest/v1/generations/{id}
(the v2 GET does not exist), downloads outputs, prints image/video ids for I2V chaining.

Usage:
  export LEONARDO_API_KEY=...
  # still
  python3 leonardo_gen.py still --model seedream-5.0-pro --prompt "..." --w 2048 --h 1152 --n 2 --out /mnt/user-data/outputs/shot --slug chef
  # image-to-video from a GENERATED image id
  python3 leonardo_gen.py video --model kling-3.0 --prompt "..." --start-image-id <id> --duration 5 --w 1920 --h 1080 --audio false --out ... --slug chef
  # balance
  python3 leonardo_gen.py balance
  # poll an existing generation id
  python3 leonardo_gen.py poll --gen-id <id> --out ... --slug x

Prints one JSON line per output: {"file":..., "id":..., "type":...}. Cost is printed on submit.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

BASE = "https://cloud.leonardo.ai/api/rest"
KEY = os.environ.get("LEONARDO_API_KEY")

# Exact aspect pairs per model family. Nano Banana silently falls back to 1:1 if the pair is not exact.
ASPECT = {
    "nano-banana-2": {"16:9": (1376, 768), "9:16": (768, 1376), "21:9": (1584, 672), "1:1": (1024, 1024), "4:5": (928, 1152), "3:2": (1264, 848)},
    "nano-banana-pro": {"16:9": (1376, 768), "9:16": (768, 1376), "21:9": (1584, 672), "1:1": (1024, 1024)},
    "gpt-image-2": {"16:9": (1376, 768), "9:16": (768, 1376), "1:1": (1024, 1024), "3:2": (1264, 848), "2:3": (848, 1264)},
    "gemini-image-2": {"16:9": (1376, 768), "9:16": (768, 1376), "1:1": (1024, 1024), "2:3": (848, 1264), "3:2": (1264, 848)},
    "seedream-5.0-pro": {"4:5": (1632, 2048), "16:9": (2048, 1152), "9:16": (1152, 2048), "1:1": (2048, 2048), "21:9": (2048, 880), "2:3": (1344, 2016), "3:2": (2016, 1344)},
    "openai/gpt-image-2.5-sunburst": {"16:9": (1376, 768), "9:16": (768, 1376), "1:1": (1024, 1024), "3:2": (1264, 848), "2:3": (848, 1264)},
    "flux-dev": {"16:9": (1600, 896), "9:16": (896, 1600), "1:1": (1024, 1024), "21:9": (1680, 720)},
    "bytedance/seedance-2.5": {"16:9": (1280, 720), "16:9hd": (1920, 1080)},
    "kling-3.0": {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1440, 1440)},
    "kling-3.0-turbo": {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1440, 1440)},
}
STYLE_NONE = "556c1ee5-ec38-42e8-955a-1e82dad0ffa1"

def req(method, path, body=None):
    if not KEY:
        sys.exit("LEONARDO_API_KEY not set")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers={
        "authorization": f"Bearer {KEY}", "accept": "application/json", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:800]}")

def balance():
    d = req("GET", "/v1/me")
    u = d.get("user_details", [{}])[0]
    print(json.dumps({"apiPaidTokens": u.get("apiPaidTokens"), "concurrency": u.get("apiConcurrencySlots")}))

def submit(body):
    d = req("POST", "/v2/generations", body)
    if isinstance(d, list):
        sys.exit(f"submit error: {json.dumps(d)[:1200]}")
    g = d.get("generate") or {}
    if not g:
        sys.exit(f"submit failed: {json.dumps(d)[:800]}")
    print(json.dumps({"generationId": g["generationId"], "cost": g.get("cost")}), flush=True)
    return g["generationId"]

def poll(gen_id, out, slug, timeout=900):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = req("GET", f"/v1/generations/{gen_id}").get("generations_by_pk") or {}
        st = d.get("status")
        if st == "COMPLETE":
            results = []
            imgs = d.get("generated_images") or []
            for i, im in enumerate(imgs):
                url = im.get("motionMP4URL") or im.get("url")
                ext = "mp4" if url.lower().endswith(".mp4") else ("png" if url.lower().endswith(".png") else "jpg")
                path = f"{out}/{slug}-v{i+1}.{ext}"
                rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # CDN 403s the default urllib agent
                with urllib.request.urlopen(rq, timeout=120) as resp, open(path, "wb") as fh:
                    fh.write(resp.read())
                results.append({"file": path, "id": im["id"], "type": "video" if ext == "mp4" else "image", "url": url})
                print(json.dumps(results[-1]), flush=True)
            return results
        if st == "FAILED":
            sys.exit(f"generation FAILED: {json.dumps(d)[:800]}")
        time.sleep(5)
    sys.exit("timed out polling")

def upload(path):
    ext = path.rsplit(".",1)[-1].lower()
    d = req("POST", "/v1/init-image", {"extension": ext})["uploadInitImage"]
    import requests
    fields = json.loads(d["fields"]) if isinstance(d["fields"], str) else d["fields"]
    with open(path, "rb") as fh:
        r = requests.post(d["url"], data=fields, files={"file": fh}, timeout=120)
    print(json.dumps({"uploadedId": d["id"], "status": r.status_code}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["still", "video", "poll", "balance", "upload"])
    ap.add_argument("--model"); ap.add_argument("--prompt")
    ap.add_argument("--aspect", default=None, help="16:9 | 9:16 | 1:1 | 21:9 ... (uses exact model pair)")
    ap.add_argument("--w", type=int); ap.add_argument("--h", type=int)
    ap.add_argument("--n", type=int, default=1); ap.add_argument("--seed", type=int)
    ap.add_argument("--style", default=STYLE_NONE, help="style_id for flux/nano; 'omit' to skip")
    ap.add_argument("--quality", default="MEDIUM", help="gpt-image-2: LOW|MEDIUM|HIGH")
    ap.add_argument("--start-image-id"); ap.add_argument("--start-image-type", default="GENERATED")
    ap.add_argument("--end-image-id")
    ap.add_argument("--ref", action="append", default=[], help="image reference id[:STRENGTH], GENERATED type; repeatable, order kept")
    ap.add_argument("--ref-type", default="UPLOADED")
    ap.add_argument("--duration", type=int, default=5); ap.add_argument("--audio", default="false")
    ap.add_argument("--mode-res", default="RESOLUTION_1080")
    ap.add_argument("--gen-id"); ap.add_argument("--out", default="/mnt/user-data/outputs"); ap.add_argument("--slug", default="shot")
    ap.add_argument("--no-wait", action="store_true")
    a = ap.parse_args()

    if a.mode == "balance":
        return balance()
    if a.mode == "upload":
        return upload(a.prompt)
    if a.mode == "poll":
        return poll(a.gen_id, a.out, a.slug)

    w, h = a.w, a.h
    if a.aspect and a.model in ASPECT:
        w, h = ASPECT[a.model][a.aspect]
    p = {"prompt": a.prompt}
    if w and h: p.update({"width": w, "height": h})
    if a.seed is not None: p["seed"] = a.seed

    if a.mode == "still":
        p["quantity"] = a.n
        p["prompt_enhance"] = "OFF"
        if a.model in ("flux-dev", "flux-schnell", "nano-banana-2", "nano-banana-pro", "gemini-image-2") and a.style != "omit":
            p["style_ids"] = [a.style]
        if a.ref:
            refs = []
            for i, r in enumerate(a.ref):
                parts = r.split(":")
                rid, st = parts[0], (parts[1] if len(parts) > 1 else "")
                typ = parts[2] if len(parts) > 2 else "GENERATED"
                item = {"image": {"id": rid, "type": typ}}
                if a.model.startswith("openai/"): item["order"] = i + 1      # Sunburst: no strength
                else: item["strength"] = st or "MID"
                refs.append(item)
            p["guidances"] = {"image_reference": refs}
        if a.model.startswith("openai/gpt-image-2.5"):
            p["style_ids"] = [STYLE_NONE]   # default would be "Dynamic", which fights the brief
        if a.model.startswith("gpt-image") or a.model.startswith("openai/gpt-image"):
            p["quality"] = a.quality
    else:
        p["duration"] = a.duration
        p["motion_has_audio"] = a.audio.lower() == "true"
        if a.model.startswith("kling"):
            p["mode"] = a.mode_res
        if a.model.startswith("bytedance/seedance"):
            p.pop("mode", None); p["quantity"] = 1
            if not (w and h): p.update({"width": 1280, "height": 720})
        if (not a.start_image_id) and a.ref and a.model.startswith("bytedance/seedance"):
            rt = a.ref_type
            p["guidances"] = {"image_reference": [{"image": {"id": r.split(":")[0], "type": rt}, "order": i + 1} for i, r in enumerate(a.ref)]}
        if a.start_image_id:
            g = {"start_frame": [{"image": {"id": a.start_image_id, "type": a.start_image_type}}]}
            if a.ref and a.model.startswith("bytedance/seedance"):
                g["image_reference"] = [{"image": {"id": r.split(":")[0], "type": "GENERATED"}} for r in a.ref]
            if a.end_image_id:
                g["end_frame"] = [{"image": {"id": a.end_image_id, "type": a.start_image_type}}]
            p["guidances"] = g

    gid = submit({"model": a.model, "public": False, "parameters": p})
    if not a.no_wait:
        poll(gid, a.out, a.slug)

if __name__ == "__main__":
    main()
