import subprocess, os, sys, tempfile
import numpy as np
from PIL import Image
def sh(a,b,win):
    A=np.fft.fft2((a-a.mean())*win);B=np.fft.fft2((b-b.mean())*win)
    R=A*np.conj(B);R/=np.abs(R)+1e-9;r=np.fft.ifft2(R).real
    y,x=np.unravel_index(np.argmax(r),r.shape)
    def ref(c,n,line):
        l,m,p=line[(c-1)%n],line[c],line[(c+1)%n];den=l-2*m+p
        return 0.0 if abs(den)<1e-12 else 0.5*(l-p)/den
    ry=y+ref(y,r.shape[0],r[:,x]);rx=x+ref(x,r.shape[1],r[y,:])
    if ry>r.shape[0]/2:ry-=r.shape[0]
    if rx>r.shape[1]/2:rx-=r.shape[1]
    return rx,ry
def series(clip):
    d=tempfile.mkdtemp()
    subprocess.run(["ffmpeg","-v","error","-y","-i",clip,"-vf","scale=480:-1,format=gray",os.path.join(d,"f%03d.png")],check=True)
    fr=[np.asarray(Image.open(os.path.join(d,f)),dtype=np.float64) for f in sorted(os.listdir(d))]
    h=fr[0].shape[0]; win=np.outer(np.hanning(h//2),np.hanning(fr[0].shape[1])); T=[];B=[]
    for a,b in zip(fr[:-1],fr[1:]):
        T.append(sh(a[:h//2],b[:h//2],win)); B.append(sh(a[h//2:],b[h//2:],win))
    return np.array(T),np.array(B)
def pulse(v):
    k=12; tr=np.convolve(np.pad(v,(k//2,k//2),mode="edge"),np.ones(k)/k,mode="valid")[:len(v)]
    o=v-tr; sp=np.abs(np.fft.rfft(o*np.hanning(len(o)))); f=np.fft.rfftfreq(len(o),1/24); m=(f>=1.2)&(f<=5)
    return sp[m].max()
for c in sys.argv[1:]:
    T,B=series(c)
    bob,sway,zoom=pulse(T[:,1]),pulse(T[:,0]),pulse(B[:,1]-T[:,1])
    print(f"{os.path.basename(c):14s} bob {bob:5.2f} sway {sway:5.2f} forward-pulse {zoom:5.2f} WORST {max(bob,sway,zoom):5.2f}")
