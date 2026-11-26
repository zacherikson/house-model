import sys, json, re, pdfplumber, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
PDF='../source/plans/plans-review-set-2026-06-02.pdf'
pi=int(sys.argv[1]); base=sys.argv[2]; out=sys.argv[3]
wall=np.load(base+'.npy'); meta=json.load(open(base+'.json')); R=meta['R']
ops=json.load(open(base+'_ops.json'))
seen=set(); ops2=[]
for o in ops:
    k=(round(o['x0']),round(o['y0']),round(o['x1']),round(o['y1']))
    if k in seen: continue
    seen.add(k)
    if o['t']=='6016': o['kind']='entry'; o['y0']=511.5
    elif o['h']>=68 or o['t'] in ('10090',): o['kind']='door'
    else: o['kind']='window'
    if o['t']=='10090': o['kind']='garage'
    ops2.append(o)
ops=ops2
extra=json.load(open(base+'_fix.json')) if len(sys.argv)>4 else {}
for r in extra.get('fill',[]):
    x0,y0,x1,y1=[int(round(v*R)) for v in r]; wall[y0:y1,x0:x1]=True
def rects(m):
    m=m.copy(); out=[]
    H,W=m.shape
    while True:
        ys,xs=np.nonzero(m)
        if len(ys)==0: break
        y,x=ys[0],xs[0]
        x2=x
        while x2+1<W and m[y,x2+1]: x2+=1
        y2=y
        while y2+1<H and m[y2+1,x:x2+1].all(): y2+=1
        m[y:y2+1,x:x2+1]=False
        out.append([x/R,y/R,(x2+1)/R,(y2+1)/R])
    return out
closed=wall.copy()
for o in ops:
    closed[int(o['y0']*R):int(np.ceil(o['y1']*R)),int(o['x0']*R):int(np.ceil(o['x1']*R))]=True
for r in extra.get('close',[]):
    x0,y0,x1,y1=[int(round(v*R)) for v in r]; closed[y0:y1,x0:x1]=True
lab,n=ndi.label(~closed)
outside=lab[0,0]
foot=(lab!=outside)
outm=(lab==outside)
for r in extra.get('hole',[]):
    x0,y0,x1,y1=[int(round(v*R)) for v in r]; lab[y0:y1,x0:x1]=0
def ext(r):
    x0,y0,x1,y1=[int(round(v*R)) for v in r]; d=4*R; res={}
    H,W=outm.shape
    for k,sl in (('y0',outm[max(0,y0-d):y0,x0:x1]),('y1',outm[y1:y1+d,x0:x1]),('x0',outm[y0:y1,max(0,x0-d):x0]),('x1',outm[y0:y1,x1:x1+d])):
        res[k]=bool(sl.size and sl.mean()>0.5)
    return res
print('outside frac',outm.mean())
# room labels
p=pdfplumber.open(PDF).pages[pi]
names={}
words=p.extract_words()
for w in words:
    t=w['text']
    if re.match(r'^[A-Z][A-Z/0-9]+$',t) and len(t)>2 and t not in ('DN','WIC') or t=='WIC':
        cx=int(((w['x0']+w['x1'])/2-meta['x0'])/0.75*R); cy=int(((w['top']+w['bottom'])/2-meta['y0'])/0.75*R)
        if 0<=cy<lab.shape[0] and 0<=cx<lab.shape[1]:
            l=lab[cy,cx]
            if l and l!=outside: names.setdefault(int(l),[]).append(t)
rooms=[]
for l in range(1,n+1):
    if l==outside: continue
    m=lab==l
    if m.sum()<(24*R)**2: continue
    rooms.append(dict(id=l,name=' '.join(names.get(l,[])) or None,area_sqft=round(m.sum()/R/R/144,1),rects=rects(ndi.binary_dilation(m,structure=np.ones((3,3)),iterations=R)&foot)))
# downsample masks for collision (2in per cell)
def ds(m,f):
    H,W=m.shape; H2,W2=H//f,W//f
    return m[:H2*f,:W2*f].reshape(H2,f,W2,f).any(axis=(1,3))
for o in ops: o['ext']=ext([o['x0'],o['y0'],o['x1'],o['y1']])
labels=[]
for w in words:
    t=w['text']
    if re.match(r'^[A-Z][A-Z/0-9]+$',t) and len(t)>2:
        labels.append(dict(t=t,x=((w['x0']+w['x1'])/2-meta['x0'])/0.75,y=((w['top']+w['bottom'])/2-meta['y0'])/0.75))
W=rects(wall)
json.dump(dict(meta=meta,walls=[dict(r=r,ext=ext(r)) for r in W],labels=labels,ops=ops,rooms=rooms,foot=rects(ds(foot,R*6)) ,footScale=6),open(out,'w'))
im=Image.new('RGB',wall.shape[::-1]); d=ImageDraw.Draw(im)
import random
for r in rooms:
    c=tuple(random.randint(60,255) for _ in range(3))
    for a in r['rects']: d.rectangle([a[0]*R,a[1]*R,a[2]*R-1,a[3]*R-1],fill=c)
    a=r['rects'][0]; d.text((a[0]*R+5,a[1]*R+5),str(r['name']),fill=(0,0,0))
d.bitmap((0,0),Image.fromarray((wall*255).astype(np.uint8)),fill=(255,255,255))
im.save(out+'.png')
for r in rooms: print(r['id'],r['name'],r['area_sqft'],len(r['rects']))
print('walls',len(rects(wall)))
