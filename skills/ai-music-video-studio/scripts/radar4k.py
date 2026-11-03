import os, sys
"""Dot-matrix radar / space-map HUD (same style as dothud). Earth -> Moon route, rival ships, her ship, progress + warning bars."""
import math, random, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dothud import Grid
from PIL import Image
WHITE=(240,240,240,255); RED=(215,25,33,255); DIM=(70,70,70,255); MID=(140,140,140,255); OFF=(32,32,32,255)
CX,CY,R=48,45,40
EARTH=(22,70); MOON=(76,18)
def bez(t):
    c=(20,18)  # control point: arc up and over
    x=(1-t)**2*EARTH[0]+2*(1-t)*t*c[0]+t**2*MOON[0]; y=(1-t)**2*EARTH[1]+2*(1-t)*t*c[1]+t**2*MOON[1]
    return x,y
def inside(x,y): return (x-CX)**2+(y-CY)**2<=R*R
def frame(progress, warn, ships_n, sweep_deg, t_ship, seed=7, danger=False, obj=None, impact=None):
    g=Grid(160,90)
    # rings + crosshair (dim)
    for i in range(160):
        for j in range(90):
            d=math.hypot(i-CX,j-CY)
            if d>R: continue
            if abs(d-R)<0.6 or abs(d-R*2/3)<0.5 or abs(d-R/3)<0.5: g.px[(i,j)]=3
            if (i==CX or j==CY) and (i+j)%2==0: g.px[(i,j)]=3
            # sweep wedge
            a=(math.degrees(math.atan2(j-CY,i-CX))-sweep_deg)%360
            if d<R-1 and d>1:
                if a>360-2.2 or a<0.6: g.px[(i,j)]=4
                elif a>360-18 and (i+j)%2==0: g.px.setdefault((i,j),3)
    # route (dotted)
    for k in range(0,101,2):
        x,y=bez(k/100); xi,yi=round(x),round(y)
        if inside(xi,yi): g.px[(xi,yi)]=3 if k/100>progress else 1
    # earth (filled disc) and moon (ring + craters)
    for i in range(-6,7):
        for j in range(-6,7):
            if i*i+j*j<=30: g.px[(EARTH[0]+i,EARTH[1]+j)]=1 if (i+j)%3 else 4
            if i*i+j*j<=26: g.px[(MOON[0]+i,MOON[1]+j)]=1
    for (i,j) in [(-2,-2),(2,1),(0,3),(-3,1),(1,-3),(3,-1)]: g.px[(MOON[0]+i,MOON[1]+j)]=4
    # rival ships scattered around the route near their own progress
    rnd=random.Random(seed)
    for n in range(min(ships_n,34)):
        tt=min(1,max(0,t_ship+rnd.uniform(-0.3,0.15)))
        x,y=bez(tt); x+=rnd.uniform(-8,8); y+=rnd.uniform(-8,8)
        xi,yi=round(x),round(y)
        if inside(xi,yi): g.px[(xi,yi)]=1
    # her ship: red 2x2 + short trail
    x,y=bez(progress); xi,yi=round(x),round(y)
    for i in range(-4,5):
        for j in range(-4,5):
            if 12<=i*i+j*j<=17: g.px[(xi+i,yi+j)]=2
            elif i*i+j*j<=6: g.px.pop((xi+i,yi+j),None)
    for (i,j) in [(0,0),(1,0),(0,1),(1,1),(-1,0),(0,-1)]: g.px[(xi+i,yi+j)]=2
    for k in range(1,4):
        tx,ty=bez(max(0,progress-0.025*k)); g.px[(round(tx),round(ty))]=2 if k==1 else 4
    if obj is not None:
        ox,oy,orad,lbl=obj
        for i in range(-orad-1,orad+2):
            for j in range(-orad-1,orad+2):
                d=i*i+j*j
                if d<=orad*orad: g.px[(round(ox)+i,round(oy)+j)]=2
                elif d<=(orad+1.5)**2 and (i+j)%2==0: g.px[(round(ox)+i,round(oy)+j)]=4
        if lbl:
            # dotted collision line to moon if impact
            if impact is not None:
                for k in range(0,40):
                    a=k/40; x=ox+(MOON[0]-ox)*a; y=oy+(MOON[1]-oy)*a
                    if k%2==0: g.px[(round(x),round(y))]=2
            lx=min(max(round(ox)-20,9),45); ly=round(oy)+orad+3
            g.text(lx,ly,lbl,2)
    # right panel
    X=100
    g.text(X,6,'▲',2); g.text(X+9,6,'WARNING',2)
    if impact is None:
        g.text(X,20,'DEST MOON',1); g.text(X,32,f'SHIPS {ships_n:03d}' if ships_n<1000 else 'SHIPS ∞',1)
    else:
        g.text(X,20,'IMPACT',2); g.text(X,32,f'T-{impact:.1f}',2)
    g.text(X,48,'PROGRESS',1)
    for s in range(10):
        on=s<round(progress*10)
        g.rect(X+s*5,58,4,6,1 if on else 3, fill=on)
    g.text(X,70,'RISK',1)
    for s in range(10):
        on=s<warn
        g.rect(X+s*5,80,4,6,(2 if s>=7 else 1) if on else 3, fill=on)
    cols={1:WHITE,2:RED,3:DIM,4:MID}
    bg=(8,8,8,255)
    if danger: cols={1:WHITE,2:WHITE,3:(150,30,30,255),4:(240,170,170,255)}; bg=(190,16,24,255)
    return g.render(pitch=24,rad=8.6,cols=cols,off=(40,0,0,255) if danger else OFF,bg=bg,glow=5)
