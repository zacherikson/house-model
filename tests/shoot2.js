const {chromium}=require('playwright');
(async()=>{
  const out=process.argv[2]; const views=JSON.parse(process.argv[3]);
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERR '+e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('http://localhost:8765/index.html'); await p.waitForFunction(()=>window.__dbg,null,{timeout:120000});
  await p.evaluate(()=>{document.getElementById('hint').style.display='none'});
  for(const v of views){ const [name,kind]=v;
    await p.evaluate((v)=>{const D=window.__dbg,P=D.P;const [name,kind,a,b2,c,d,e,f]=v;
      if(kind==='spot') window.__view('walk',a,13);
      else if(kind==='over'||kind==='overb') window.__view(kind,0,13);
      else {window.__view('walk',0,13);P.x=a;P.y=b2;P.level=e;P.floor=c;P.eye=c+64;D.look(d[0],d[1]);P.pitch=f||-.05}},v);
    await p.waitForTimeout(2500); await p.screenshot({path:`${out}/${name}.png`}); }
  console.log(errs.join('\n')); await b.close();
})();
