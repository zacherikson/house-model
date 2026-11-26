import json, numpy as np
from scipy import ndimage as ndi
DX,DY=2,78
m=json.load(open('main.json')); b=json.load(open('bsmt_export.json'))
sh=lambda r:[round(r[0]-DX,2),round(r[1]-DY,2),round(r[2]-DX,2),round(r[3]-DY,2)]
def in_garage(r):
    cx=(r[0]+r[2])/2; cy=(r[1]+r[3])/2
    return (cx>548 and cy>376) or (cx>804 and cy>205) or (cx>532 and cy>522)
patio=[258,-60,530,122]
def in_patio(r):
    cx=(r[0]+r[2])/2; cy=(r[1]+r[3])/2
    return patio[0]<cx<patio[2] and patio[1]<cy<patio[3]
bw=[]
for w in b['walls']:
    r=sh(w['r'])
    if in_garage(r): continue
    bw.append(dict(r=r,ext=w['ext']))
bops=[]
for o in b['ops']:
    r=sh([o['x0'],o['y0'],o['x1'],o['y1']])
    o2={k:o[k] for k in ('t','sfx','w','h','o','kind','ext')}; o2.update(x0=r[0],y0=r[1],x1=r[2],y1=r[3])
    if o['kind']=='door' and o['h']>=68: o2['kind']='door'
    bops.append(o2)
brooms=[]
for r in b['rooms']:
    rr=[sh(q) for q in r['rects']]
    a=r['rects'][0]
    if in_patio(rr[0]) or in_garage(rr[0]): continue
    if r['area_sqft']<10 and rr[0][1]<40: continue  # fireplace alcove
    name=(r['name'] or '').replace('SESSURT','').strip() or None
    brooms.append(dict(name=name,area=r['area_sqft'],rects=rr))
wells=[sh(q) for q in [[126.5,56.5,193.5,104],[548.5,56.5,616,104],[710,56.5,777.5,104],[2,463.5,29,531]]]
# ground: complement of basement footprint (+wells) within a window, 3" cells
X0,Y0,X1,Y1,C=-150,-210,1150,860,3
nx,ny=(X1-X0)//C,(Y1-Y0)//C
hole=np.zeros((ny,nx),bool)
def mark(r,pad=0):
    a=max(0,int((r[0]-pad-X0)//C)); bb=min(nx,int(np.ceil((r[2]+pad-X0)/C))); c=max(0,int((r[1]-pad-Y0)//C)); d=min(ny,int(np.ceil((r[3]+pad-Y0)/C)))
    hole[c:d,a:bb]=True
for r in brooms:
    for q in r['rects']: mark(q)
for w in bw: mark(w['r'])
for q in wells: mark(q)
hole=ndi.binary_closing(hole,iterations=2)|hole
hole=ndi.binary_fill_holes(hole)
def rects(mk):
    mk=mk.copy(); out=[]; H,W=mk.shape
    while True:
        ys,xs=np.nonzero(mk)
        if len(ys)==0: break
        y,x=ys[0],xs[0]; x2=x
        while x2+1<W and mk[y,x2+1]: x2+=1
        y2=y
        while y2+1<H and mk[y2+1,x:x2+1].all(): y2+=1
        mk[y:y2+1,x:x2+1]=False; out.append([int(X0+x*C),int(Y0+y*C),int(X0+(x2+1)*C),int(Y0+(y2+1)*C)])
    return out
ground=rects(~hole)
mrooms=[dict(name=r['name'],area=r['area_sqft'],rects=r['rects']) for r in m['rooms']]
mops=[{k:(round(v,2) if isinstance(v,float) else v) for k,v in o.items() if k in ('t','sfx','w','h','o','x0','y0','x1','y1','kind','ext')} for o in m['ops']]
out=dict(walls=m['walls'],ops=mops,rooms=mrooms,bsmt=dict(walls=bw,ops=bops,rooms=brooms,wells=wells),ground=ground,groundWin=[X0,Y0,X1,Y1])
json.dump(out,open('../site/house.json','w'),separators=(',',':'))
print(len(bw),'bwalls',len(bops),'bops',len(brooms),'brooms',len(ground),'ground rects')
for r in brooms: print(r['name'],r['area'],[round(v) for v in r['rects'][0]])
for o in bops: print(o['t'],o['sfx'],o['kind'],[round(o[k]) for k in ('x0','y0','x1','y1')],[k for k,v in o['ext'].items() if v])
