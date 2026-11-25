import sys, subprocess, glob, os, shutil
import numpy as np
from PIL import Image
vid, outdir = sys.argv[1], sys.argv[2]
shutil.rmtree(outdir, ignore_errors=True); os.makedirs(outdir)
subprocess.run(['ffmpeg','-v','error','-y','-i',vid,'-vf','fps=25,scale=1000:-1',f'{outdir}/f%04d.png'],check=True)
fs=sorted(glob.glob(f'{outdir}/f*.png'))
out=[]
for i,f in enumerate(fs):
    a=np.asarray(Image.open(f).convert('L'),float); h,w=a.shape
    rows=slice(int(h*.10),int(h*.30))     # open sky rows
    L0=a[rows,0:4].mean(); L1=a[rows,25:45].mean(); R0=a[rows,w-4:w].mean(); R1=a[rows,w-45:w-25].mean()
    out.append((i,L0/L1,R0/R1,L0,R0))
for i,l,r,L0,R0 in out:
    flag='  <-- dark edge' if (l<0.62 or r<0.62) else ''
    print(f'{i:3d} L {l:4.2f} R {r:4.2f}  ({L0:5.1f} {R0:5.1f}){flag}')
