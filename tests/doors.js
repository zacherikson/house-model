// Walks straight through every door on both floors, both directions; reports any it can't get through.
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:320,height:200}});
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:180000});
  const r=await p.evaluate(async()=>{const D=window.__dbg,P=D.P;const data=await (await fetch('house.json')).json();const fails=[];let n=0;
    for(const [lvl,ops] of [['M',data.ops],['B',data.bsmt.ops]]) for(const o of ops){ if(o.kind!=='door') continue;
      const cx=(o.x0+o.x1)/2, cy=(o.y0+o.y1)/2; const dirs=o.o==='h'?[[0,1],[0,-1]]:[[1,0],[-1,0]];
      for(const [dx,dy] of dirs){ const sx=cx-dx*30, sy=cy-dy*30, tx=cx+dx*30, ty=cy+dy*30; const g=lvl==='B'?D.GB:D.G; const i=D.gIdx(sx,sy);
        if(i<0||g.floor[i]<-500||D.blocked(sx,sy,g.floor[i],10)) continue; n++;
        P.level=lvl;P.x=sx;P.y=sy;P.floor=g.floor[i];P.stuck=0;D.look(tx,ty);D.keys.KeyW=1;for(let t=0;t<90;t++)D.step(1/30);D.keys.KeyW=0;
        const through=(dx?(P.x-cx)*dx:(P.y-cy)*dy)>15; if(!through) fails.push([o.t,lvl,Math.round(cx),Math.round(cy),'stopped at',Math.round(P.x),Math.round(P.y)])}}
    return {tried:n,fails}});
  console.log(JSON.stringify(r)); await b.close();
})();
