const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:640,height:400}});
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERR '+e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:120000});
  const r=await p.evaluate(()=>{
    const out={}; const D=window.__dbg, P=D.P;
    function walk(name,x,y,tx,ty,level,secs){P.x=x;P.y=y;P.level=level;P.floor=level==='B'?-128:0;P.stuck=0;D.look(tx,ty);D.keys.KeyW=1;const tr=[];for(let t=0;t<secs*30;t++){D.step(1/30);if(t%15==0)tr.push([Math.round(P.x),Math.round(P.y),Math.round(P.floor),P.level])}D.keys.KeyW=0;out[name]=tr}
    walk('downstairs',230,301,600,301,'M',8);
    walk('upstairs',460,301,100,301,'B',8);
    walk('kitchen_to_patio',230,92,600,92,'M',6);walk('patio_to_master',300,92,700,92,'M',8);
    walk('house_to_garage',565,330,565,600,'M',5);
    walk('garage_to_house',565,450,565,200,'M',5);
    walk('front_door_out',306,480,306,800,'M',6);
    walk('porch_back_in',306,640,306,300,'M',6);
    return out});
  for(const k in r) console.log(k, JSON.stringify(r[k]));
  console.log(errs.join('\n')); await b.close();
})();
