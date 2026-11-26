import sys, json, re, pdfplumber, numpy as np
from PIL import Image, ImageDraw
PDF='../source/plans/plans-review-set-2026-06-02.pdf'
pi=int(sys.argv[1]); base=sys.argv[2]
wall=np.load(base+'.npy'); meta=json.load(open(base+'.json')); R=meta['R']
p=pdfplumber.open(PDF).pages[pi]
labels=[]
for w in p.extract_words(extra_attrs=['upright'],keep_blank_chars=False):
    t=w['text'] if w['upright'] else w['text'][::-1]
    m=re.match(r'^T?(\d{4,5})([A-Z]*)$',t)
    if not m: continue
    d=m.group(1)
    if len(d)==5: wd,ht=int(d[:2])*12,int(d[2])*12+int(d[3:])
    else: wd=int(d[0])*12+int(d[1]); ht=int(d[2])*12+int(d[3])
    cx=((w['x0']+w['x1'])/2-meta['x0'])/0.75; cy=((w['top']+w['bottom'])/2-meta['y0'])/0.75
    labels.append(dict(t=d,sfx=m.group(2),w=wd,h=ht,cx=cx,cy=cy,up=w['upright']))
def runs_gaps(row):
    out=[];n=len(row);i=0
    # find gaps between wall runs
    idx=np.flatnonzero(row)
    if len(idx)<2: return out
    br=np.flatnonzero(np.diff(idx)>1)
    for b in br: out.append((idx[b]+1, idx[b+1]))  # [a,b) empty
    return out
def find(L, M, cx, cy):
    best=None
    for y in range(int((cy-36)*R), int((cy+36)*R)):
        if y<0 or y>=M.shape[0]: continue
        for a,b in runs_gaps(M[y]):
            ln=(b-a)/R
            if not (L['w']-3 <= ln <= L['w']+10): continue
            c=(a+b)/2/R
            if abs(c-cx)>30: continue
            # wall must exist at both ends for at least 3 inches outward
            if not (M[y,max(0,a-3*R):a].all() and M[y,b:b+3*R].all()): continue
            sc=abs(c-cx)+abs(y/R-cy)*0.5+abs(ln-L['w'])*0.3
            if best is None or sc<best[0]: best=(sc,y,a,b)
    if best is None: return None
    _,y,a,b=best
    # extent of gap band in y (wall thickness)
    y0=y;y1=y
    while y0-1>=0 and not M[y0-1,a:b].any() and M[y0-1,a-1] and M[y0-1,b]: y0-=1
    while y1+1<M.shape[0] and not M[y1+1,a:b].any() and M[y1+1,a-1] and M[y1+1,b]: y1+=1
    return (a/R,b/R,y0/R,(y1+1)/R)
ops=[]
for L in labels:
    rh=find(L,wall,L['cx'],L['cy']); rv=find(L,wall.T,L['cy'],L['cx'])
    cand=[]
    if rh: cand.append(('h',rh, abs((rh[0]+rh[1])/2-L['cx'])+abs((rh[2]+rh[3])/2-L['cy'])))
    if rv: cand.append(('v',rv, abs((rv[0]+rv[1])/2-L['cy'])+abs((rv[2]+rv[3])/2-L['cx'])))
    if not cand: print('NO MATCH',L['t'],L['sfx'],round(L['cx']),round(L['cy'])); continue
    o,r,_=min(cand,key=lambda c:c[2])
    if o=='h': x0,x1,y0,y1=r
    else: y0,y1,x0,x1=r
    ops.append(dict(L,o=o,x0=x0,x1=x1,y0=y0,y1=y1))
json.dump(ops,open(base+'_ops.json','w'),indent=0)
im=Image.fromarray((wall*120).astype(np.uint8)).convert('RGB'); d=ImageDraw.Draw(im)
for o in ops:
    col=(0,160,255) if o['h']<68 else (0,255,0)
    d.rectangle([o['x0']*R,o['y0']*R,o['x1']*R,o['y1']*R],fill=col)
    d.text((o['x0']*R,o['y0']*R-14),o['t']+o['sfx'],fill=(255,255,0))
im.save(base+'_ops.png'); print(len(ops),'matched of',len(labels))
