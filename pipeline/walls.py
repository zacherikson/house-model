import sys, json, pdfplumber, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
PDF='../source/plans/plans-review-set-2026-06-02.pdf'
pi=int(sys.argv[1]); out=sys.argv[2]
SC=0.75  # pt per inch
p=pdfplumber.open(PDF).pages[pi]
W=[l for l in p.lines if round(l['linewidth'],2)==0.48 and l['stroking_color']==(0.0,0.0,0.0)]
xs=[x for l in W for x,y in l['pts']]; ys=[y for l in W for x,y in l['pts']]
x0,y0=min(xs)-24*SC,min(ys)-24*SC
R=2  # px per inch
w=int((max(xs)-x0)/SC*R)+48*R; h=int((max(ys)-y0)/SC*R)+48*R
im=Image.new('L',(w,h),0); d=ImageDraw.Draw(im)
for l in W:
    d.line([((x-x0)/SC*R,(y-y0)/SC*R) for x,y in l['pts']],fill=255,width=1)
m=np.array(im)>0
lab,n=ndi.label(~m)
dist=ndi.distance_transform_edt(~m)
mx=ndi.maximum(dist,lab,index=np.arange(1,n+1))
area=ndi.sum(np.ones_like(lab),lab,index=np.arange(1,n+1))
thin=np.zeros(n+1,bool); thin[1:]=(mx<=4.5*R)&(area<200000*R*R)
wall=m|thin[lab]
# remove tiny specks
lab2,n2=ndi.label(wall); s=ndi.sum(wall,lab2,np.arange(1,n2+1))
wall&=np.isin(lab2,np.where(s>=20*R*R)[0]+1)
np.save(out+'.npy',wall)
json.dump({'x0':x0,'y0':y0,'SC':SC,'R':R,'w':w,'h':h},open(out+'.json','w'))
Image.fromarray((wall*255).astype(np.uint8)).save(out+'.png')
print(w,h,wall.sum())
