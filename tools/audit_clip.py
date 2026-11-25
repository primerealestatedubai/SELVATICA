import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

clip, start_still, end_still, out_prefix = sys.argv[1:5]
n_sheet = int(sys.argv[5]) if len(sys.argv) > 5 else 12
tmp = tempfile.mkdtemp(prefix="audit_")
subprocess.run(["ffmpeg","-v","error","-y","-i",clip,"-vf","scale=480:-1",os.path.join(tmp,"f%04d.png")],check=True)
files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
frames = [Image.open(os.path.join(tmp,f)).convert("RGB") for f in files]
n, fps, size = len(frames), 24.0, frames[0].size
gray = lambda im: np.asarray(im.convert("L"), dtype=np.float64)
def box(a,k=8):
    c=np.pad(np.cumsum(np.cumsum(a,0),1),((1,0),(1,0)));return (c[k:,k:]-c[:-k,k:]-c[k:,:-k]+c[:-k,:-k])/(k*k)
def ssim(a,b):
    a,b=gray(a),gray(b);ma,mb=box(a),box(b);saa=box(a*a)-ma**2;sbb=box(b*b)-mb**2;sab=box(a*b)-ma*mb
    c1,c2=(0.01*255)**2,(0.03*255)**2
    return float((((2*ma*mb+c1)*(2*sab+c2))/((ma**2+mb**2+c1)*(saa+sbb+c2))).mean())
def lap_var(im):
    g=gray(im);l=-4*g[1:-1,1:-1]+g[:-2,1:-1]+g[2:,1:-1]+g[1:-1,:-2]+g[1:-1,2:];return float(l.var())
s_img=Image.open(start_still).convert("RGB").resize(size); e_img=Image.open(end_still).convert("RGB").resize(size)
diffs=[float(np.abs(gray(frames[i])-gray(frames[i-1])).mean()) for i in range(1,n)]
med=float(np.median(diffs)); jumps=[(i+1,round(d,2)) for i,d in enumerate(diffs) if d>max(5*med,3.0)]
sharp=[lap_var(f) for f in frames]
print(json.dumps({"frames":n,"seconds":round(n/fps,2),"ssim_first_vs_start":round(ssim(frames[0],s_img),3),
  "ssim_last_vs_end":round(ssim(frames[-1],e_img),3),"diff_median":round(med,2),"diff_max":round(max(diffs),2),
  "jumps_(frame,diff)":jumps,"sharp_min_over_end":round(min(sharp)/max(np.mean(sharp[-3:]),1e-9),2)},indent=1))
idx=[round(i*(n-1)/(n_sheet-1)) for i in range(n_sheet)]; cols=4; rows=(n_sheet+cols-1)//cols; tw=480; th=int(tw*size[1]/size[0])
sheet=Image.new("RGB",(cols*tw,rows*th)); d=ImageDraw.Draw(sheet); font=ImageFont.load_default()
for k,i in enumerate(idx):
    x,y=(k%cols)*tw,(k//cols)*th; sheet.paste(frames[i].resize((tw,th)),(x,y)); d.text((x+6,y+4),f"{i/fps:.2f}s f{i}",fill=(255,255,255),font=font)
sheet.save(out_prefix+"_sheet.jpg",quality=88)
