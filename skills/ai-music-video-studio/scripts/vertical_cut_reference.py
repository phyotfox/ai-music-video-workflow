"""REFERENCE (from To The Moon) - 16:9 master -> 9:16 cut, frame by frame.
Adapt the tables at the top for a new film, then run with PROJECT set.
Per shot it supports: crop (C: centre x 0-1), SPLIT (girl then cat, switch on the nearest beat),
WIDE (wider window anchored to the bottom, black fill above - for scenes with black sky),
ZOOM (explicit pixel box, for a tighter reference framing), FIT (full-width on a solid fill
taken from the frame edge: black / red / white), REPL (swap in a natively regenerated 9:16 clip),
and gfx (HUD graphics rebuilt vertically by vertical_gfx.py, frame-matched to the 16:9 animation).
cuts.json = shot boundaries in seconds (from ffmpeg scene detection on the master)."""
import os, sys
import json,subprocess,sys,numpy as np
from PIL import Image,ImageOps
TTM=os.environ.get("PROJECT",".").rstrip("/")+"/"
sys.path.insert(0,TTM+'tools'); import vertical_gfx as V
M=TTM+'handoff/07_master/ToTheMoon_V01.mp4'; OUT=TTM+'handoff/07_master/ToTheMoon_V03_vertical_9x16.mp4'
cuts=json.load(open('/tmp/vc/cuts.json')); FPS=24
beats=json.load(open(TTM+'audio/analysis/beatmap.json'))['beats']
def dec(path,w,h,gray=True):
    fmt='gray' if gray else 'rgb24'; ch=1 if gray else 3
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt',fmt,'-'],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w) if gray else np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
small=dec(M,192,108).astype(np.float32); N=len(small)
cf=[round(t*FPS) for t in cuts[:-1]]+[N]
def shot_of(f):
    for i in range(len(cf)-1):
        if cf[i]<=f<cf[i+1]: return i
    return len(cf)-2
C={0:.55,1:.45,2:.45,3:.5,4:.5,5:.5,6:.55,8:.5,10:.5,11:.44,12:.5,13:.35,14:.45,16:.5,17:.5,26:.5,27:.5,28:.5,30:.58,31:.5,32:.5,
   33:.42,34:.5,35:.5,36:.5,38:.5,39:.35,41:.35,43:.45,44:.5,47:.42,48:.40,51:.48,52:.48,53:.45,54:.45,55:.5,56:.45,57:.5,59:.45,61:.45,62:.5,63:.45,64:.5}
SPLIT={9:(.6,.3),15:(.55,.75),29:(.58,.3),37:(.5,.2)}
WIDE={42:(.17,.65),45:(.22,.66),46:(.16,.76)}
ZOOM={13:(690,199,1124,971)}
VV=TTM+'video/vertical/'
REPL={42:(VV+'vv_walk.mp4',0.6,42),46:(VV+'vv_hug.mp4',0.3,46),47:(VV+'vv_flag.mp4',0.3,47),48:(VV+'vv_flag.mp4',0.3,47)}
rp={'key':None,'proc':None}
def repl_frame(i):
    file,off,anchor=REPL[i]
    if rp['key']!=(file,anchor):
        if rp['proc']: rp['proc'].kill()
        rp['proc']=subprocess.Popen(['ffmpeg','-v','error','-ss',str(off),'-i',file,'-vf','scale=1080:1920:flags=lanczos,fps=24','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE); rp['key']=(file,anchor); rp['last']=None
    b=rp['proc'].stdout.read(1080*1920*3)
    if len(b)==1080*1920*3: rp['last']=Image.frombytes('RGB',(1080,1920),b)
    return rp['last']
FIT={49,58,60,67,68,69}
RADAR={7:'launch',18:'midway-v2',40:'descent-v2',50:'impact'}
split_f={}
for i,(a,b) in SPLIT.items():
    mid=(cuts[i]+cuts[i+1])/2; bt=min([x for x in beats if cuts[i]+0.3<x<cuts[i+1]-0.3] or [mid],key=lambda x:abs(x-mid))
    split_f[i]=round(bt*FPS)
# radar matching
gfx={}
for i,name in RADAR.items():
    clip=dec(TTM+f'handoff/02_graphics/GFX_radar-{name}_4K.mp4',192,108).astype(np.float32)
    for f in range(cf[i],cf[i+1]):
        m=small[f]; inv=bool(m.mean()>110)
        ref=255-clip if inv else clip
        k=int(np.argmin(((ref-m)**2).mean(axis=(1,2))))
        gfx[f]=('radar',name,k,inv)
    offs=[gfx[f][2]-(f-cf[i]) for f in range(cf[i],cf[i+1])]; k0=int(np.median(offs)); n=len(clip)
    for f in range(cf[i],cf[i+1]): gfx[f]=('radar',name,max(0,min(n-1,k0+f-cf[i])),gfx[f][3])
    if i==18: last=gfx[cf[19]-1][2]
for i in range(19,24):
    for f in range(cf[i],cf[i+1]):
        last=min(last+1,29); gfx[f]=('radar','midway-v2',last,bool(small[f].mean()>110))
for i in (24,25):
    for f in range(cf[i],cf[i+1]): gfx[f]=('title',f/FPS,bool(small[f].mean()>110))
for i in (65,66):
    for f in range(cf[i],cf[i+1]): gfx[f]=('dld',f/FPS,bool(small[f].mean()>110))
print({i:(gfx[cf[i]][2],gfx[cf[i+1]-1][2]) for i in RADAR})
COLS=np.array([(0,0,0),(200,20,30),(245,245,245)])
def fillcol(fr):
    e=np.concatenate([fr[:24].reshape(-1,3),fr[-24:].reshape(-1,3)]).astype(int); med=np.median(e,0)
    snap=COLS[np.argmin(((COLS-med)**2).sum(1))]
    return tuple(int(x) for x in (med if (med[0]>90 and med[1]<60) else snap))
def crop(im,cx):
    x=int(min(max(cx*1920-304,0),1312)); return im.crop((x,0,x+608,1080)).resize((1080,1920),Image.LANCZOS)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-i',M,'-map','0:v','-map','1:a',
    '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
src=subprocess.Popen(['ffmpeg','-v','error','-i',M,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
for f in range(N):
    buf=src.stdout.read(1920*1080*3)
    if len(buf)<1920*1080*3: break
    arr=np.frombuffer(buf,np.uint8).reshape(1080,1920,3); im=Image.fromarray(arr); i=shot_of(f)
    if i in REPL: out=repl_frame(i)
    elif f in gfx:
        g=gfx[f]
        if g[0]=='radar': out=V.radar_k(g[1],g[2]); inv=g[3]
        elif g[0]=='title': out=V.title(g[1]); inv=g[2]
        else: out=V.dld(g[1]); inv=g[2]
        if inv: out=ImageOps.invert(out)
    elif (lambda m:((m[...,0]>110)&(m[...,1]<60)&(m[...,2]<70)).mean()>0.55)(arr[::8,::8].astype(int)):
        out=Image.new('RGB',(1080,1920),fillcol(arr)); out.paste(im.resize((1080,608),Image.LANCZOS),(0,656))
    elif i in ZOOM: out=im.crop(ZOOM[i]).resize((1080,1920),Image.LANCZOS)
    elif i in SPLIT: out=crop(im,SPLIT[i][0] if f<split_f[i] else SPLIT[i][1])
    elif i in WIDE:
        x0,x1=WIDE[i]; x0=int(x0*1920); x1=int(x1*1920); h=round(1080*1080/(x1-x0))
        out=Image.new('RGB',(1080,1920),(0,0,0)); out.paste(im.crop((x0,0,x1,1080)).resize((1080,h),Image.LANCZOS),(0,1920-h))
    elif i in FIT:
        out=Image.new('RGB',(1080,1920),fillcol(arr)); out.paste(im.resize((1080,608),Image.LANCZOS),(0,656))
    else: out=crop(im,C.get(i,.5))
    enc.stdin.write(out.tobytes())
enc.stdin.close(); enc.wait(); print('done',N)
