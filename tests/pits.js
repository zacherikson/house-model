const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:320,height:200}});
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:120000});
  const r=await p.evaluate(()=>{const D=window.__dbg,out={};
    for(const [name,g,lv] of [['main',D.G,'M'],['bsmt',D.GB,'B']]){D.P.level=lv;const pits=[];
      for(let y=-60;y<700;y+=4)for(let x=0;x<1010;x+=4){const i=D.gIdx(x,y);const f=g.floor[i];if(f<-500||g.block[i])continue;
        if(D.blocked(x,y,f,10))continue; // can't stand here anyway
        let ok=false;for(let k=0;k<8&&!ok;k++){const a=k*Math.PI/4;if(!D.blocked(x+Math.cos(a)*6,y+Math.sin(a)*6,f,10))ok=true}
        if(!ok)pits.push([x,y,f])}
      out[name]=pits.length+' '+JSON.stringify(pits.slice(0,25))}
    return out});
  console.log(JSON.stringify(r,null,1)); await b.close();
})();
