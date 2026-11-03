import sys, numpy as np, random, subprocess, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dothud import Grid, F
from PIL import Image
import soundfile as sf
P=os.environ.get("PROJECT",".").rstrip("/")+"/"
def text2(g,x,y,t,col,scale=2,reveal=1.0,seed=0):
    rnd=random.Random(seed)
    for ch in t:
        rows=F[ch].split(); w=len(rows[0])
        for j,row in enumerate(rows):
            for i,b in enumerate(row):
                if b=='1' and rnd.random()<reveal:
                    for a in range(scale):
                        for c in range(scale): g.px[(x+i*scale+a,y+j*scale+c)]=col
        x+=(w+1)*scale
    return x
def width2(t,scale=2): return sum((len(F[c].split()[0])+1)*scale for c in t)-scale
WHITE=(240,240,240,255); RED=(215,25,33,255); DIM=(70,70,70,255)
def ttm(out, t0=29.40, t1=30.95, words=(("TO",29.46),("THE",30.22),("MOON",30.64))):
    os.makedirs("/tmp/ttm",exist_ok=True); n=int(round((t1-t0)*24))
    C,R=142,80; GAP=8; x0=(C-(sum(width2(w) for w,_ in words)+GAP*(len(words)-1)))//2; y=33
    for k in range(n):
        t=t0+k/24; g=Grid(C,R); x=x0
        for wi,(w,ts) in enumerate(words):
            rv=0 if t<ts else min(1,(t-ts)/0.10)
            x=text2(g,x,y,w,1,2,rv,seed=wi)-2+GAP
            x+=0
        # countdown + small markers
        rem=max(0,t1-t); cs=f"T-{rem:.1f}"
        g.text((C-6*len(cs))//2,58,cs,2)
        g.text(4,4,'▲',2); g.text(13,4,'DEST MOON',1)
        for s_ in range(10): g.rect(C-4-50+s_*5,4,4,6,(2 if s_>=7 else 1) if s_<8 else 3,fill=s_<8)
        im=g.render(pitch=9,rad=3.4,cols={1:WHITE,2:RED,3:DIM},off=(30,30,30,255),bg=(6,6,8,255),glow=2.2)
        Image.new('RGB',(1280,720),(6,6,8)).paste(im.convert('RGB'),(1,0)) if False else None
        canvas=Image.new('RGB',(1280,720),(6,6,8)); canvas.paste(im.convert('RGB'),((1280-im.width)//2,(720-im.height)//2)); canvas.save(f"/tmp/ttm/{k:03d}.png")
    subprocess.run(["ffmpeg","-v","error","-y","-framerate","24","-i","/tmp/ttm/%03d.png","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",out],check=True)
def eq(out, t0=68.20, t1=70.36):
    os.makedirs("/tmp/eq",exist_ok=True)
    y,sr=sf.read(P+"audio/To The Moon (D2 cover, intercom) (Edit).wav"); y=y.mean(1) if y.ndim>1 else y
    n=int(round((t1-t0)*24)); C,R=142,80; nb=16; bands=np.geomspace(40,12000,nb+1)
    hist=np.zeros(nb)
    for k in range(n):
        t=t0+k/24; i=int(t*sr); seg=y[max(0,i-2048):i+2048]*np.hanning(4096)[:len(y[max(0,i-2048):i+2048])]
        sp=np.abs(np.fft.rfft(seg,4096)); fr=np.fft.rfftfreq(4096,1/sr)
        lv=np.array([sp[(fr>=bands[b])&(fr<bands[b+1])].mean() if ((fr>=bands[b])&(fr<bands[b+1])).any() else 0 for b in range(nb)])
        lv=np.log10(lv+1e-6); lv=np.clip((lv+1.0)/3.2,0,1); hist=np.maximum(lv,hist*0.75)
        blink=(int((t-t0)/(60/134/2))%2==0)
        g=Grid(C,R)
        g.text(4,4,'▲',1); text2(g,14,3,"WARNING",1,2)
        bw=4; gap=1.3; x0=6; base=74; H=44
        for b in range(nb):
            h=int(hist[b]*H); xb=int(x0+b*(bw+gap))
            for yy in range(h): 
                for xx in range(bw): g.px[(xb+xx,base-yy)]=1 if yy<H*0.7 else 4
        # right panel: risk bar full, blinking
        g.text(96,26,'RISK',1); 
        for s_ in range(10): g.rect(96+s_*4,36,3,8,1,fill=True)
        g.text(96,50,'STATUS',1); g.text(96,60,'HOLD' if blink else 'HOLD',1)
        bg=(205,18,28,255) if blink else (120,8,14,255)
        im=g.render(pitch=9,rad=3.4,cols={1:(255,255,255,255),4:(255,200,200,255)},off=(150,20,28,255) if blink else (80,6,10,255),bg=bg,glow=2.2)
        canvas=Image.new('RGB',(1280,720),bg[:3]); canvas.paste(im.convert('RGB'),((1280-im.width)//2,(720-im.height)//2)); canvas.save(f"/tmp/eq/{k:03d}.png")
    subprocess.run(["ffmpeg","-v","error","-y","-framerate","24","-i","/tmp/eq/%03d.png","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",out],check=True)
if __name__=="__main__":
    ttm(P+"graphics/title-to-the-moon.mp4"); eq(P+"graphics/warning-eq.mp4")
    for f,ts in (("title-to-the-moon",1.4),("warning-eq",1.0)):
        subprocess.run(["ffmpeg","-v","error","-y","-ss",str(ts),"-i",P+f"graphics/{f}.mp4","-frames:v","1",f"/tmp/{f}.jpg"],check=True)
