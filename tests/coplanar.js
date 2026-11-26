// Finds surfaces that sit exactly on top of each other (same plane, same facing, overlapping),
// which flicker ("z-fighting") as the camera moves. Run against a served test copy on :8765.
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:320,height:200}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:180000});
  const res=await p.evaluate(()=>{
    const faces=[];
    for(const k in window.__dbg.B){const bk=window.__dbg.B[k],P=bk.p,N=bk.n;
      for(let v=0;v+18<=P.length;){
        const nx=N[v],ny=N[v+1],nz=N[v+2];let same=true;
        for(let j=1;j<6;j++){if(N[v+3*j]!==nx||N[v+3*j+1]!==ny||N[v+3*j+2]!==nz){same=false;break}}
        const ax=Math.abs(nx)>.999?0:Math.abs(ny)>.999?1:Math.abs(nz)>.999?2:-1;
        if(!same||ax<0){v+=9;continue}
        let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];
        for(let j=0;j<6;j++)for(let c=0;c<3;c++){const q=P[v+3*j+c];mn[c]=Math.min(mn[c],q);mx[c]=Math.max(mx[c],q)}
        if(Math.abs(mx[ax]-mn[ax])<1e-6) faces.push({m:bk.m,ax,dir:Math.sign([nx,ny,nz][ax]),pl:mn[ax],mn,mx});
        v+=18;}}
    const groups={};for(const f of faces){const key=f.ax+'|'+f.dir+'|'+Math.round(f.pl*400);(groups[key]=groups[key]||[]).push(f)}
    const hits=[];const IN=0.0254;
    for(const g of Object.values(groups)){if(g.length<2)continue;
      for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++){const a=g[i],c=g[j];if(a.m===c.m)continue;
        let area=1;for(let d=0;d<3;d++){if(d===a.ax)continue;const o=Math.min(a.mx[d],c.mx[d])-Math.max(a.mn[d],c.mn[d]);if(o<=0.001){area=0;break}area*=o}
        if(area>0) hits.push({mats:a.m+'/'+c.m,axis:'xyz'[a.ax],at_in:[a.mn[0],a.mn[1],a.mn[2]].map(v=>Math.round(v/IN)),areaSqIn:Math.round(area/IN/IN)})}}
    return {faces:faces.length,hits};
  });
  console.log('faces checked',res.faces,'overlaps',res.hits.length);
  const byPair={};for(const h of res.hits){(byPair[h.mats]=byPair[h.mats]||[]).push(h)}
  for(const k in byPair) console.log(k,byPair[k].length,JSON.stringify(byPair[k].slice(0,6)));
  await b.close();
})();
