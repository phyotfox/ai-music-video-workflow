"""Generate the After Effects build script (ttm_template.jsx): beat punch-zooms, downbeat flashes, shake ramp,
word-timed lyric layers. Edit LINES (which words go on which caption layer) for each new song.
Needs audio/analysis/words.json + beatmap.json (from the ai-song-production skill)."""
import os, sys
import json
P=os.environ.get("PROJECT",".").rstrip("/")+"/"
W=json.load(open(P+"audio/analysis/words.json"))
bm=json.load(open(P+"audio/analysis/beatmap.json"))
beats=[round(b,3) for b in bm["beats"]]; downs=[round(b,3) for b in bm["downbeats"]]
def words(a,b): return [(x["w"],round(x["s"],3),round(x["e"],3)) for x in W if a<=x["s"]<b]
sold2=words(8.9,12.5); sold1=[(w,round(s-3.58,3),round(e-3.58,3)) for w,s,e in sold2]
LINES=[  # (style, words)
 ("small",words(0.9,2.2)),("small",words(4.2,5.2)),("verse",sold1),("verse",sold2),
 ("verse",words(12.6,14.7)),("verse",words(14.9,16.0)),("verse",words(16.1,17.4)),("verse",words(17.6,19.1)),
 ("verse",words(19.4,20.42)),("verse",words(20.42,22.7)),("verse",words(22.8,24.9)),("verse",words(24.9,27.9)),
 ("chant",words(31.2,32.1)),("chant",words(32.1,33.05)),("chant",words(33.05,33.95)),("chant",words(33.95,35.6)),
 ("chant",words(36.2,37.6)),("chant",words(37.6,39.2)),("chant",words(39.3,40.2)),("chant",words(40.4,42.1)),
 ("chant",words(42.3,43.85)),("chant",words(44.7,45.6)),("chant",words(50.0,52.1)),
 ("verse",words(52.8,56.3)),("verse",words(57.9,60.4)),("small",words(61.0,64.5)),
]
LINES=[(st,ws) for st,ws in LINES if ws]
js_lines=json.dumps([{"style":st,"w":[w for w,_,_ in ws],"t":[s for _,s,_ in ws],"end":ws[-1][2]} for st,ws in LINES])
tmpl=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ttm_template.jsx")).read()
out=tmpl.replace("__LINES__",js_lines).replace("__BEATS__",json.dumps(beats)).replace("__DOWNS__",json.dumps(downs))
open(P+"handoff/08_AE/ToTheMoon_build_AE.jsx","w").write(out)
print(len(LINES),"lines",len(beats),"beats",len(downs),"downbeats")
