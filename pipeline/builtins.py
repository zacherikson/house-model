import sys, json, pdfplumber, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
PDF='../source/plans/plans-review-set-2026-06-02.pdf'
pi=int(sys.argv[1]); base=sys.argv[2]
meta=json.load(open(base+'.json')); R=meta['R']; wall=np.load(base+'.npy')
p=pdfplumber.open(PDF).pages[pi]
def tr(x,y): return ((x-meta['x0'])/0.75*R,(y-meta['y0'])/0.75*R)
im=Image.new('L',(meta['w'],meta['h']),0); d=ImageDraw.Draw(im)
segs=[l for l in p.lines if round(l['linewidth'],2)==0.36 and l['stroking_color']==(0.0,0.0,0.0)]
segs+= [c for c in p.curves if round(c['linewidth'],2) in (0.24,0.36) and c.get('stroking_color')==(0.0,0.0,0.0)]
for l in segs: d.line([tr(x,y) for x,y in l['pts']],fill=255,width=1)
m=np.array(im)>0
lab,n=ndi.label(ndi.binary_dilation(m,iterations=2))
out=[]
vis=Image.fromarray((wall*60).astype(np.uint8)).convert('RGB'); dv=ImageDraw.Draw(vis)
dv.bitmap((0,0),im,fill=(255,255,255))
for i,sl in enumerate(ndi.find_objects(lab)):
    ys,xs=sl; bb=[xs.start/R,ys.start/R,xs.stop/R,ys.stop/R]
    if (bb[2]-bb[0])*(bb[3]-bb[1])<30: continue
    out.append(dict(id=len(out),bb=[round(v,1) for v in bb]))
    dv.rectangle([xs.start,ys.start,xs.stop,ys.stop],outline=(255,80,80))
    dv.text((xs.start+2,ys.start+2),str(len(out)-1),fill=(255,255,0))
json.dump(out,open(base+'_builtins.json','w'))
vis.save(base+'_builtins.png'); print(len(out))
for o in out: print(o)
