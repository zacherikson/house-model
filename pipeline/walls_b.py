import sys, json, pdfplumber, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
PDF='../source/plans/plans-review-set-2026-06-02.pdf'
out=sys.argv[1]
p=pdfplumber.open(PDF).pages[2]; SC=0.75; R=2
W=[l for l in p.lines if round(l['linewidth'],2)==0.48 and l['stroking_color']==(0.0,0.0,0.0)]
Hh=[l for l in p.lines if round(l['linewidth'],2)==0.24 and l['stroking_color']==(0.588235318,0.588235318,0.588235318)]
xs=[x for l in Hh+W for x,y in l['pts']]; ys=[y for l in Hh+W for x,y in l['pts']]
x0,y0=min(xs)-24*SC,min(ys)-24*SC
w=int((max(xs)-x0)/SC*R)+48*R; h=int((max(ys)-y0)/SC*R)+48*R
def ras(L):
    im=Image.new('L',(w,h),0); d=ImageDraw.Draw(im)
    for l in L: d.line([((x-x0)/SC*R,(y-y0)/SC*R) for x,y in l['pts']],fill=255,width=1)
    return np.array(im)>0
m=ras(W)
lab,n=ndi.label(~m); dist=ndi.distance_transform_edt(~m)
mx=ndi.maximum(dist,lab,index=np.arange(1,n+1)); area=ndi.sum(np.ones_like(lab),lab,index=np.arange(1,n+1))
thin=np.zeros(n+1,bool); thin[1:]=(mx<=4.5*R)&(area<200000*R*R)
wall=m|thin[lab]
hat=ras(Hh)
hat=ndi.binary_closing(hat,structure=np.ones((3,3)),iterations=3*R)
hat=ndi.binary_opening(hat,structure=np.ones((3,3)),iterations=1)
wall|=hat
lab2,n2=ndi.label(wall); s=ndi.sum(wall,lab2,np.arange(1,n2+1)); wall&=np.isin(lab2,np.where(s>=20*R*R)[0]+1)
np.save(out+'.npy',wall); json.dump({'x0':x0,'y0':y0,'SC':SC,'R':R,'w':w,'h':h},open(out+'.json','w'))
Image.fromarray((wall*255).astype(np.uint8)).resize((w//2,h//2)).save(out+'_small.png'); print(w,h)
