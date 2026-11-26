// Walks at every door/window jamb from many angles and reports how close the viewer ever gets to a wall.
// The camera near plane is 0.1 m (~4"), so anything closer than ~5" would let you see through the wall.
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:320,height:200}});
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:180000});
  const r=await p.evaluate(async()=>{
    const D=window.__dbg,P=D.P; const data=await (await fetch('house.json')).json();
    const near=(g)=>{let best=99;for(let dy=-12;dy<=12;dy+=1)for(let dx=-12;dx<=12;dx+=1){const d=Math.hypot(dx,dy);if(d>=best)continue;const i=D.gIdx(P.x+dx,P.y+dy);if(i>=0&&g.block[i])best=d}return best};
    let worst={d:99}; let runs=0;
    for(const [lvl,ops,fl] of [['M',data.ops,0],['B',data.bsmt.ops,-128]]){
      const g=lvl==='B'?D.GB:D.G;
      for(const o of ops){ if(o.kind!=='door'&&o.kind!=='entry') continue;
        const cx=(o.x0+o.x1)/2, cy=(o.y0+o.y1)/2, ends=o.o==='h'?[[o.x0,cy],[o.x1,cy]]:[[cx,o.y0],[cx,o.y1]];
        for(const [ex,ey] of ends) for(let a=0;a<16;a++){
          const ang=a*Math.PI/8, sx=ex+Math.cos(ang)*40, sy=ey+Math.sin(ang)*40;
          P.level=lvl; P.x=sx; P.y=sy; const i=D.gIdx(sx,sy); if(i<0||g.block[i]||g.floor[i]<-500) continue;
          P.floor=g.floor[i]; if(D.blocked(sx,sy,P.floor,10)) continue; P.stuck=0; D.look(ex,ey); D.keys.KeyW=1; runs++;
          for(let t=0;t<60;t++){D.step(1/30); const d=near(P.level==='B'?D.GB:D.G); if(d<worst.d) worst={d,x:Math.round(P.x),y:Math.round(P.y),lvl:P.level,door:o.t}}
          D.keys.KeyW=0;}}}
    return {runs,worst};});
  console.log(JSON.stringify(r)); await b.close();
})();
