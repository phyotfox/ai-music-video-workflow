"""Vertical (9:16, 1080x1920) rebuilds of the To The Moon HUD graphics: radar on top, readouts below; stacked titles."""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dothud import Grid, F
from PIL import Image
WHITE=(240,240,240,255); RED=(215,25,33,255); DIM=(70,70,70,255); MID=(140,140,140,255); OFF=(32,32,32,255)
GW,GH,P,RAD,GLOW=90,160,12,4.3,2.5
CX,CY,R=45,46,40
def T(x,y): return x-3, y+1          # landscape radar coords -> vertical radar coords
EARTH=T(22,70); MOON=T(76,18); CTRL=T(20,18)
def bez(t):
    x=(1-t)**2*EARTH[0]+2*(1-t)*t*CTRL[0]+t**2*MOON[0]; y=(1-t)**2*EARTH[1]+2*(1-t)*t*CTRL[1]+t**2*MOON[1]
    return x,y
def inside(x,y): return (x-CX)**2+(y-CY)**2<=R*R
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
def radar(progress, warn, ships_n, sweep_deg, t_ship, seed=7, danger=False, obj=None, impact=None):
    g=Grid(GW,GH)
    for i in range(GW):
        for j in range(GH):
            d=math.hypot(i-CX,j-CY)
            if d>R: continue
            if abs(d-R)<0.6 or abs(d-R*2/3)<0.5 or abs(d-R/3)<0.5: g.px[(i,j)]=3
            if (i==CX or j==CY) and (i+j)%2==0: g.px[(i,j)]=3
            a=(math.degrees(math.atan2(j-CY,i-CX))-sweep_deg)%360
            if d<R-1 and d>1:
                if a>360-2.2 or a<0.6: g.px[(i,j)]=4
                elif a>360-18 and (i+j)%2==0: g.px.setdefault((i,j),3)
    for k in range(0,101,2):
        x,y=bez(k/100); xi,yi=round(x),round(y)
        if inside(xi,yi): g.px[(xi,yi)]=3 if k/100>progress else 1
    for i in range(-6,7):
        for j in range(-6,7):
            if i*i+j*j<=30: g.px[(EARTH[0]+i,EARTH[1]+j)]=1 if (i+j)%3 else 4
            if i*i+j*j<=26: g.px[(MOON[0]+i,MOON[1]+j)]=1
    for (i,j) in [(-2,-2),(2,1),(0,3),(-3,1),(1,-3),(3,-1)]: g.px[(MOON[0]+i,MOON[1]+j)]=4
    rnd=random.Random(seed)
    for n in range(min(ships_n,34)):
        tt=min(1,max(0,t_ship+rnd.uniform(-0.3,0.15)))
        x,y=bez(tt); x+=rnd.uniform(-8,8); y+=rnd.uniform(-8,8)
        xi,yi=round(x),round(y)
        if inside(xi,yi): g.px[(xi,yi)]=1
    x,y=bez(progress); xi,yi=round(x),round(y)
    for i in range(-4,5):
        for j in range(-4,5):
            if 12<=i*i+j*j<=17: g.px[(xi+i,yi+j)]=2
            elif i*i+j*j<=6: g.px.pop((xi+i,yi+j),None)
    for (i,j) in [(0,0),(1,0),(0,1),(1,1),(-1,0),(0,-1)]: g.px[(xi+i,yi+j)]=2
    for k in range(1,4):
        tx,ty=bez(max(0,progress-0.025*k)); g.px[(round(tx),round(ty))]=2 if k==1 else 4
    if obj is not None:
        ox,oy,orad,lbl=obj; ox,oy=T(ox,oy)
        for i in range(-orad-1,orad+2):
            for j in range(-orad-1,orad+2):
                d=i*i+j*j
                if d<=orad*orad: g.px[(round(ox)+i,round(oy)+j)]=2
                elif d<=(orad+1.5)**2 and (i+j)%2==0: g.px[(round(ox)+i,round(oy)+j)]=4
        if lbl:
            if impact is not None:
                for k in range(0,40):
                    a=k/40; x=ox+(MOON[0]-ox)*a; y=oy+(MOON[1]-oy)*a
                    if k%2==0: g.px[(round(x),round(y))]=2
            lx=min(max(round(ox)-20,2),GW-6*len(lbl)-1); ly=round(oy)+orad+3
            g.text(lx,ly,lbl,2)
    X=8
    g.text(X,92,'▲',2); g.text(X+9,92,'WARNING',2)
    if impact is None:
        g.text(X,103,'DEST MOON',1); g.text(X,113,f'SHIPS {ships_n:03d}' if ships_n<1000 else 'SHIPS ∞',1)
    else:
        g.text(X,103,'IMPACT',2); g.text(X,113,f'T-{impact:.1f}',2)
    g.text(X,125,'PROGRESS',1)
    for s in range(10):
        on=s<round(progress*10); g.rect(X+s*7,134,6,6,1 if on else 3, fill=on)
    g.text(X,144,'RISK',1)
    for s in range(10):
        on=s<warn; g.rect(X+s*7,153,6,6,(2 if s>=7 else 1) if on else 3, fill=on)
    cols={1:WHITE,2:RED,3:DIM,4:MID}; bg=(8,8,8,255)
    if danger: cols={1:WHITE,2:WHITE,3:(150,30,30,255),4:(240,170,170,255)}; bg=(190,16,24,255)
    return g.render(pitch=P,rad=RAD,cols=cols,off=(40,0,0,255) if danger else OFF,bg=bg,glow=GLOW).convert('RGB')
# the landscape animation specs (same params as the 16:9 GFX clips), as functions of frame k
SPECS={
 'launch':(30,lambda a,k: radar(0.04+0.06*a,round(2+a),int(96+32*a),(k*12+200)%360,0.03+0.05*a)),
 'midway-v2':(30,lambda a,k: radar(0.45+0.07*a,round(5+a),int(220+36*a),(k*12+200)%360,0.45+0.07*a,obj=(24-a,14+a,1,"UNKNOWN"))),
 'descent-v2':(30,lambda a,k: radar(0.86+0.06*a,round(8+a),int(480+32*a),(k*12+60)%360,0.84+0.06*a,obj=(44+2*a,9+a,2,"UNKNOWN"))),
 'impact':(36,lambda a,k: radar(0.97,10,999,(k*20)%360,0.95,danger=(k//3)%2==0,obj=(56+10*a,10+4*a,4+round(a),"UNKNOWN"),impact=max(0,3.0-a*1.5))),
}
def radar_k(name,k):
    n,fn=SPECS[name]; k=max(0,min(n-1,k)); return fn(k/(n-1),k)
def title(t, t1=30.95, words=(("TO",29.46),("THE",30.22),("MOON",30.64))):
    g=Grid(GW,GH); y=44
    for wi,(w,ts) in enumerate(words):
        rv=0 if t<ts else min(1,(t-ts)/0.10)
        text2(g,(GW-width2(w,3))//2,y,w,1,3,rv,seed=wi); y+=27
    cs=f"T-{max(0,t1-t):.1f}"; g.text((GW-6*len(cs))//2,128,cs,2)
    g.text(4,4,'▲',2); g.text(13,4,'DEST MOON',1)
    for s in range(10): g.rect(4+s*7,16,6,6,(2 if s>=7 else 1) if s<8 else 3,fill=s<8)
    return g.render(pitch=P,rad=RAD,cols={1:WHITE,2:RED,3:DIM},off=(30,30,30,255),bg=(6,6,8,255),glow=GLOW).convert('RGB')
def dld(t):
    if t>=74.75: return Image.new('RGB',(GW*P,GH*P),(0,0,0))
    g=Grid(GW,GH)
    for w,a,b,col in [("DON'T",72.72,73.34,1),("LOOK",73.34,73.66,1),("DOWN",73.66,74.75,2)]:
        if a<=t<b: text2(g,(GW-width2(w,3))//2,70,w,col,3,min(1,(t-a)/0.06),seed=1)
    g.text(4,4,'▲',2); g.text(13,4,'STATUS',1); g.text(13,14,'HOLDING',1)
    return g.render(pitch=P,rad=RAD,cols={1:WHITE,2:RED},off=(30,30,30,255),bg=(6,6,8,255),glow=GLOW).convert('RGB')
