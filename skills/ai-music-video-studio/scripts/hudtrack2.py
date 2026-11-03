import os, sys
"""Robust wrist-HUD tracker: 2-pass. Detect the screen quad per frame, reject outliers against the
running median, fill misses by interpolation, smooth, then composite. Never drops out.
usage: hudtrack2.py in.mp4 out.mp4 MODE song_t0 dur   (MODE white6|danger)"""
import cv2, numpy as np, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from hudtrack import detect, ov, G
from PIL import Image
def run(src,dst,mode,t0,dur):
    cap=cv2.VideoCapture(src); W,H=1280,720; N=int(round(dur*24)); frames=[]; Q=[]
    for n in range(N):
        ok,fr=cap.read()
        if not ok: break
        fr=cv2.resize(fr,(W,H)); frames.append(fr); Q.append(detect(fr))
    good=[q for q in Q if q is not None]; med=np.median(np.stack(good),0) if good else None
    area=lambda q: cv2.contourArea(q.astype(np.float32))
    ma=area(med)
    for i,q in enumerate(Q):
        if q is None or abs(area(q)-ma)/ma>0.35 or np.abs(q.mean(0)-med.mean(0)).max()>90: Q[i]=None
    idx=[i for i,q in enumerate(Q) if q is not None]
    arr=np.stack([Q[i] for i in idx]); full=np.zeros((len(Q),4,2),np.float32)
    for c in range(4):
        for d in range(2): full[:,c,d]=np.interp(range(len(Q)),idx,arr[:,c,d])
    k=np.ones(5)/5
    for c in range(4):
        for d in range(2): full[:,c,d]=np.convolve(np.pad(full[:,c,d],2,mode='edge'),k,'valid')
    out=cv2.VideoWriter(dst,cv2.VideoWriter_fourcc(*'mp4v'),24,(W,H))
    for n,fr in enumerate(frames):
        t=t0+n/24; q=full[n]; c=q.mean(0); dstq=np.float32([c+(p-c)*0.97 for p in q])
        f=fr.astype(np.float32)/255
        if mode=="white6": png=G+"warning-bar-06.png"; tint=None
        else:
            on=(t>=74.6) or int((t-70.36)/(60/134/2))%2==0
            png=G+("warning-bar-10-danger-on.png" if on else "warning-bar-10-danger-on.png"); tint=1.0 if on else 0.62
        o=ov(png); h,w=o.shape[:2]; M=cv2.getPerspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]),dstq)
        rgb=cv2.warpPerspective(o[...,:3][...,::-1].copy(),M,(W,H)); a=cv2.GaussianBlur(cv2.warpPerspective(np.ones((h,w),np.float32),M,(W,H)),(0,0),0.8)[...,None]
        if mode=="white6":
            oa=cv2.warpPerspective(o[...,3],M,(W,H))[...,None]
            screen=np.array([0.90,0.93,0.95],np.float32)*(1-oa)+rgb*oa
            f=f*(1-a)+screen*a+0.12*cv2.GaussianBlur(a*0.9,(0,0),14)[...,None]
        else:
            rgb=rgb*tint; f=f*(1-a)+rgb*a+0.35*tint*cv2.GaussianBlur(rgb*a,(0,0),16)
        out.write((np.clip(f,0,1)*255).astype(np.uint8))
    out.release()
if __name__=="__main__": run(sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5]))
