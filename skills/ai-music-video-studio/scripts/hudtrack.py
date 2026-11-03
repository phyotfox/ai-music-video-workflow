"""Track the glowing wrist screen per frame and composite the dot-matrix warning.
usage: hudtrack.py in.mp4 out.mp4 MODE song_t0 dur   MODE = white6 | danger"""
import os, cv2, numpy as np, sys
from PIL import Image
G=os.path.join(os.environ.get("HUD_GFX", "graphics/warning-bar"), "")  # folder with warning-bar-06.png and warning-bar-10-danger-{on,off}.png
def order(pts):
    pts=pts.reshape(-1,2).astype(np.float32); s=pts.sum(1); d=pts[:,1]-pts[:,0]
    tl,br,tr,bl=pts[np.argmin(s)],pts[np.argmax(s)],pts[np.argmin(d)],pts[np.argmax(d)]
    q=np.float32([tl,tr,br,bl])
    if np.linalg.norm(q[1]-q[0])<np.linalg.norm(q[3]-q[0]): q=np.float32([bl,tl,tr,br])  # long edge on top
    return q
def detect(fr):
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV)
    m=((hsv[...,2]>215)&(hsv[...,1]>35)&(hsv[...,0]<35)).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not cs: return None
    c=max(cs,key=cv2.contourArea)
    if cv2.contourArea(c)<1500: return None
    a=cv2.approxPolyDP(c,0.04*cv2.arcLength(c,True),True)
    if len(a)!=4: a=cv2.boxPoints(cv2.minAreaRect(c))
    return order(a)
cache={}
def ov(png):
    if png not in cache: cache[png]=np.array(Image.open(png).convert('RGBA')).astype(np.float32)/255
    return cache[png]
def run(src,dst,mode,t0,dur):
    cap=cv2.VideoCapture(src); W,H=1280,720; out=cv2.VideoWriter(dst,cv2.VideoWriter_fourcc(*'mp4v'),24,(W,H)); q_s=None
    for n in range(int(round(dur*24))):
        ok,fr=cap.read()
        if not ok: break
        fr=cv2.resize(fr,(W,H)); t=t0+n/24; q=detect(fr)
        if q is not None:
            if q_s is not None and np.abs(q-q_s).max()>80: q=q_s  # reject jumps
            q_s=q if q_s is None else 0.5*q_s+0.5*q
        # on a miss, hold the last good quad (no dropout)
        f=fr.astype(np.float32)/255
        if q_s is not None:
            c=q_s.mean(0); dstq=np.float32([c+(p-c)*0.97 for p in q_s]); big=np.int32([c+(p-c)*1.6 for p in q_s])
            box=np.zeros((H,W),np.float32); cv2.fillPoly(box,[big],1); box=cv2.GaussianBlur(box,(0,0),12)
            hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV).astype(np.float32)
            gm=cv2.GaussianBlur(((hsv[...,0]>=4)&(hsv[...,0]<=35)&(hsv[...,1]>40)&(hsv[...,2]>90)).astype(np.float32),(0,0),4)*box
            if mode=="white6":
                png=G+"warning-bar-06.png"; hsv[...,1]*=(1-0.88*gm)
            else:
                k=int((t-70.36)/(60/134/2)); on=(t>=74.6) or k%2==0
                png=G+("warning-bar-10-danger-on.png" if on else "warning-bar-10-danger-off.png")
                hsv[...,0]=hsv[...,0]*(1-gm)+1*gm; hsv[...,1]=np.clip(hsv[...,1]*(1-gm)+225*gm,0,255); hsv[...,2]*=(1-gm*(0 if on else 0.55))
            f=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)/255
            o=ov(png); h,w=o.shape[:2]; M=cv2.getPerspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]),dstq)
            rgb=cv2.warpPerspective(o[...,:3][...,::-1].copy(),M,(W,H)); a=cv2.GaussianBlur(cv2.warpPerspective(o[...,3],M,(W,H)),(0,0),0.6)[...,None]
            f = f*(1-a)+(rgb*f*1.25)*a if mode=="white6" else f*(1-a)+rgb*a+0.4*cv2.GaussianBlur(rgb*a,(0,0),14)
        out.write((np.clip(f,0,1)*255).astype(np.uint8))
    out.release()
if __name__=="__main__": run(sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5]))
