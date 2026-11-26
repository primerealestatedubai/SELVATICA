import subprocess, json, os, sys, numpy as np, shutil
W=os.environ.get('WALK_DIR','walk')
SITE=os.environ.get('SITE_DIR','site')
SEL=json.load(open(W+'/selected.json'))
UNIQUE=['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10','C12','C14','C15','C17','C19','C20']
TIMELINE=[('C01',None),('C02',None),('C03',None),('C04',None),('C05',None),('C06',None),('C07',None),('C08',None),('C09',None),('C10',None),
          ('C11','C10'),('C12',None),('C13','C12'),('C14',None),('C15',None),('C16','C15'),('C17',None),('C18','C17'),('C19',None),('C20',None)]
FPS=24
def sh(*a): subprocess.run(a,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def gray_frames(path):
    r=subprocess.run(['ffmpeg','-v','error','-i',path,'-vf','scale=160:90,format=gray','-f','rawvideo','-'],capture_output=True)
    a=np.frombuffer(r.stdout,np.uint8); return a.reshape(-1,90,160).astype(float)
def nbf(path):
    r=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','csv=p=0',path],capture_output=True,text=True); return int(r.stdout.strip())
os.makedirs(W+'/web',exist_ok=True)
trims={}
for c in UNIQUE:
    src='%s/att/%s.mp4'%(W,SEL[c]); g=gray_frames(src); n=len(g); s,e=0,n
    if c=='C01':
        d=np.abs(g-g[0]).mean((1,2)); idx=int(np.argmax(d>2.0)); s=max(0,idx-3)
    elif c=='C20':
        d=np.abs(g-g[-1]).mean((1,2)); idx=int(np.where(d>2.0)[0].max()); e=min(n,idx+8)
    if c!='C01': s=max(s,1)            # the first frame repeats the end of the clip before it
    trims[c]=(s,e,n)
    out='%s/web/%s.mp4'%(W,c)
    sh('ffmpeg','-y','-i',src,'-vf','scale=1280:720:flags=lanczos,trim=start_frame=%d:end_frame=%d,setpts=PTS-STARTPTS'%(s,e),'-r',str(FPS),'-an','-c:v','libx264','-preset','slow','-crf','24','-g','6','-keyint_min','6','-sc_threshold','0','-pix_fmt','yuv420p',out)
    print(c,SEL[c],'frames',n,'keep',s,e,'->',nbf(out),'frames',os.path.getsize(out)//1024,'KB')
json.dump(trims,open(W+'/trims.json','w'))
# group into segment files of at most ~12.5 MB, in timeline order of first use
LIM=12.5*1024*1024; groups=[[]]; size=0
for c in UNIQUE:
    sz=os.path.getsize('%s/web/%s.mp4'%(W,c))
    if groups[-1] and size+sz>LIM: groups.append([]); size=0
    groups[-1].append(c); size+=sz
segs=[]; loc={}
for gi,g in enumerate(groups):
    lst=W+'/web/seg%d.txt'%gi; open(lst,'w').write(''.join("file '%s/web/%s.mp4'\n"%(W,c) for c in g))
    fn='walk%d.mp4'%(gi+1); out=SITE+'/'+fn
    sh('ffmpeg','-y','-f','concat','-safe','0','-i',lst,'-c','copy','-movflags','+faststart',out)
    off=0.0
    for c in g:
        k=nbf('%s/web/%s.mp4'%(W,c)); loc[c]=(gi,off,off+k/FPS); off+=k/FPS
    segs.append({'file':fn,'dur':round(off,3)})
    print(fn,[c for c in g],round(off,2),'s',os.path.getsize(out)//1024,'KB')
items=[]
for cid,rev in TIMELINE:
    base=rev or cid
    if base not in loc: items.append({'id':cid,'missing':True}); continue
    gi,a,b=loc[base]
    if rev: items.append({'id':cid,'seg':gi,'a':round(a,4),'b':round(b-1/FPS,4),'rev':True})
    else: items.append({'id':cid,'seg':gi,'a':round(a,4),'b':round(b,4)})
man={'segs':segs,'items':items}
json.dump(man,open(W+'/manifest.json','w'),indent=1)
print('timeline seconds',round(sum(i['b']-i['a'] for i in items),1))
