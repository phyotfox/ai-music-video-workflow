import os, sys
"""Beat-synced energy pass on an assembled picture. usage: energy.py in.mp4 out.mp4"""
import cv2, numpy as np, json, sys
P=os.environ.get("PROJECT",".").rstrip("/")+"/"
bm=json.load(open(P+"audio/analysis/beatmap.json")); BEATS=np.array(bm["beats"]); DOWN=np.array(bm["downbeats"])
ZONES=[(30.95,45.28),(63.19,70.36)]          # drop + build get punches/flashes
STROBE=[(41.70,45.28)]                       # red room + crowd-surf: red strobe silhouettes
def since(t,arr):
    p=arr[arr<=t+1e-6]; return t-p[-1] if len(p) else 9
def inz(t,z): return any(a<=t<b for a,b in z)
cap=cv2.VideoCapture(sys.argv[1]); fps=24; W,H=1280,720
out=cv2.VideoWriter(sys.argv[2],cv2.VideoWriter_fourcc(*'mp4v'),fps,(W,H)); n=0
while True:
    ok,fr=cap.read()
    if not ok: break
    t=n/fps; n+=1; f=fr.astype(np.float32)/255
    if inz(t,STROBE):
        e=np.exp(-since(t,BEATS)/0.10)
        lum=f.mean(2,keepdims=True)
        sil=f*0.18+np.clip(lum-0.55,0,1)*0.9           # crush to silhouettes, keep the bright backlight
        red=np.clip(f*np.array([0.35,0.35,1.25])+np.array([0,0,0.18]),0,1)
        f=sil*(1-e)+red*e
        f=f*np.array([0.85,0.85,1.0])+np.array([0,0,0.04])*(1-e)
    if inz(t,ZONES):
        sb=since(t,BEATS); sd=since(t,DOWN)
        z=1+0.03*np.exp(-sb/0.08)+0.03*np.exp(-sd/0.10)
        if z>1.001:
            cw,ch=int(W/z),int(H/z); x0,y0=(W-cw)//2,(H-ch)//2
            f=cv2.resize(f[y0:y0+ch,x0:x0+cw],(W,H),interpolation=cv2.INTER_LINEAR)
        ca=int(round(7*np.exp(-sd/0.07)))
        if ca>0:
            f[...,2]=np.roll(f[...,2],ca,1); f[...,0]=np.roll(f[...,0],-ca,1)
        fl=0.28*np.exp(-sd/0.05)
        f=f*(1-fl)+fl
    out.write((np.clip(f,0,1)*255).astype(np.uint8))
out.release()
