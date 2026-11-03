"""REFERENCE (from To The Moon) - Reel covers that survive Instagram's 3:4 profile grid.
All text sits inside the centre 1080x1350 of a 1080x1920 cover (SAFE). Writes a grid-check sheet.
Point CON at your own source frames and tag lines."""
import sys,numpy as np; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dothud import Grid; import vertical_gfx as V
from PIL import Image,ImageFilter,ImageEnhance,ImageDraw
P=os.environ.get("PROJECT",".").rstrip("/")+"/"; OUT=P+"thumbnails/"
WHITE=(245,245,245,255); RED=(226,32,40,255); W,H=1080,1920
SAFE=(285,1635)   # centre 1080x1350: visible in the 3:4 grid, 4:5 feed and 9:16 Reels tab
def title(lines,scale=3,pitch=10,gap=6):
    Wg=max(V.width2(t,scale) for t,_ in lines)+4; Hg=len(lines)*(7*scale+gap)+2; g=Grid(Wg,Hg); y=1
    for t,c in lines: V.text2(g,(Wg-V.width2(t,scale))//2,y,t,c,scale,1.0); y+=7*scale+gap
    return g.render(pitch=pitch,rad=pitch*0.40,cols={1:WHITE,2:RED},off=None,bg=(0,0,0,0),glow=pitch*0.25)
def chip(txt,pitch=7):
    g=Grid(len(txt)*6+12,9); g.text(1,1,'▲',2); g.text(10,1,txt,1)
    return g.render(pitch=pitch,rad=pitch*0.4,cols={1:WHITE,2:RED},off=None,bg=(0,0,0,0),glow=pitch*0.3)
def shadowed(base,ov,xy,blur=18,s=0.75):
    a=ov.split()[3]; sh=Image.new("RGBA",ov.size,(0,0,0,0)); sh.putalpha(a.point(lambda v:int(v*s)))
    pad=blur*3; big=Image.new("RGBA",(ov.width+2*pad,ov.height+2*pad),(0,0,0,0)); big.paste(sh,(pad,pad)); big=big.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(big,(xy[0]-pad,xy[1]-pad)); base.alpha_composite(ov,xy)
def cover(src,cx,cy,zoom=1.0):
    im=Image.open(src).convert("RGB"); r=max(W/im.width,H/im.height)*zoom
    im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
    x=int((im.width-W)*cx); y=int((im.height-H)*cy); return im.crop((x,y,x+W,y+H)).convert("RGBA")
def grad(im,y0,y1,top=False,amt=0.8):
    yy=np.arange(H)[:,None]*np.ones((1,W)); v=np.clip((y0-yy)/(y0-y1) if top else (yy-y0)/(y1-y0),0,1)*amt
    m=Image.fromarray((v*255).astype('uint8')); im.alpha_composite(Image.composite(Image.new("RGBA",(W,H),(0,0,0,255)),Image.new("RGBA",(W,H),(0,0,0,0)),m))
CON={"C_cat-hug":dict(src="/tmp/th/f_38.6.png",cx=0.5,cy=0.5,zoom=1.0,chipt="ALL IN",moon=1),
     "A_helmet-amber":dict(src="/tmp/th/f_69.6.png",cx=0.5,cy=0.5,zoom=1.0,chipt="DON'T LOOK DOWN",moon=2),
     "B_light-streaks":dict(src=P+"plates/storyboard-v6/FX5v_9x16-v1.jpg",cx=0.5,cy=0.5,zoom=1.0,chipt="IMPACT T-0.0",moon=2),
     "D_asteroid":dict(src="/tmp/th/f_66.9.png",cx=0.42,cy=0.5,zoom=1.0,chipt="IMPACT T-0.3",moon=1)}
for name,c in CON.items():
    im=cover(c["src"],c["cx"],c["cy"],c["zoom"])
    im=ImageEnhance.Contrast(im.convert("RGB")).enhance(1.06).convert("RGBA")
    grad(im,1150,1650,amt=0.75); grad(im,560,240,top=True,amt=0.55)
    ch=chip(c["chipt"]); shadowed(im,ch,((W-ch.width)//2,SAFE[0]+40))
    t=title([("TO THE",1),("MOON",c["moon"])]); s=0.80*W/t.width; t=t.resize((round(t.width*s),round(t.height*s)),Image.LANCZOS)
    shadowed(im,t,((W-t.width)//2,SAFE[1]-40-t.height))
    im.convert("RGB").save(OUT+f"{name}_reel-cover_1080x1920.jpg",quality=92)
# preview: full cover + 3:4 grid crop with safe-zone guide
names=list(CON); pv=Image.new("RGB",(len(names)*(270+250)+20,520),"#f3f3f3"); d=ImageDraw.Draw(pv)
for i,n in enumerate(names):
    a=Image.open(OUT+f"{n}_reel-cover_1080x1920.jpg"); x=10+i*520
    full=a.resize((270,480)); dd=ImageDraw.Draw(full); dd.rectangle([0,60,269,420],outline=(0,200,255),width=2); pv.paste(full,(x,20))
    pv.paste(a.crop((0,240,1080,1680)).resize((240,320)),(x+275,20)); d.text((x+275,350),"3:4 grid crop",fill="black"); d.text((x,505),n,fill="black")
pv.save(OUT+"_reel-cover_grid-check.jpg",quality=88)
